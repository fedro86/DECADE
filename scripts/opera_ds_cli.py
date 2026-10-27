#!/usr/bin/env python
"""CLI per downscaling e validazione.

Esempi
------
# validazione nel periodo di sovrapposizione (una coppia ODYSSEY ogni ora, 8 processi)
python scripts/opera_ds_cli.py validate \
    --odyssey-glob "/data/opera/odyssey/**/*DBZH*.h5" \
    --cirrus-glob  "/data/opera/cirrus/**/*DBZH*.h5" \
    --time-regex "(\\d{12})" --time-format "%Y%m%d%H%M" \
    --start 2024-07-01 --end 2024-10-30 --shifts 0 -2.5 -5 2.5 \
    --pair-stride 4 --workers 8 --out validation_2024

# produzione dell'archivio 1 km / 5 min
python scripts/opera_ds_cli.py downscale \
    --odyssey-glob "/data/opera/odyssey/2019/**/*DBZH*.h5" \
    --time-regex "(\\d{12})" --start 2019-01-01 --end 2020-01-01 --out /data/opera_1km_5min/2019

# scelta delle finestre su ODYSSEY a 2 km (filtro dei buchi + campionamento per importanza)
python scripts/opera_ds_cli.py sample \
    --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" --time-regex "@(\\d{8}T\\d{4})@" \
    --time-format "%Y%m%dT%H%M" --start 2024-07-01 --end 2024-07-06 --out finestre.csv --workers 8

# finestre per il ML (store Zarr in formato IRENE) da un CSV con t_start,row0,col0
python scripts/opera_ds_cli.py windows \
    --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" --time-regex "@(\\d{8}T\\d{4})@" \
    --time-format "%Y%m%dT%H%M" --windows-csv finestre.csv --out windows.zarr --workers 8
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import functools
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import numpy as np  # noqa: E402

from opera_ds import DownscaleConfig, LKParams, index_files, run_downscaling, run_validation  # noqa: E402
from opera_ds.odim_io import bbox_extent, extent_window, read_odim_composite, refine_where  # noqa: E402
from opera_ds.pipeline import run_downscaling_parallel  # noqa: E402
from opera_ds.sampling import SamplerConfig, block_times, sample_block  # noqa: E402
from opera_ds.windows import Window, WindowStore, make_window, store_attrs  # noqa: E402


def load_cfg(path: str | None) -> DownscaleConfig:
    cfg = DownscaleConfig()
    if path:
        with open(path) as f:
            d = json.load(f)
        lk = d.pop("lk", {})
        cfg = dataclasses.replace(cfg, **d, lk=dataclasses.replace(LKParams(), **lk))
    return cfg


_FILES: dict = {}   # indice dei file ODYSSEY, passato una volta sola a ogni processo


def _init_files(files):
    global _FILES
    _FILES = files


def _map(fn, jobs, files, workers):
    """map in parallelo (o in serie) con l'indice dei file condiviso tramite initializer."""
    if workers <= 1:
        _init_files(files)
        yield from map(fn, jobs)
        return
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(workers, initializer=_init_files, initargs=(files,)) as ex:
        yield from ex.map(fn, jobs)


def _window_job(args):
    win, cfg, method, quantity, context_km, shift, clip, domain = args
    return win, make_window(_FILES, win, cfg, method, quantity, context_km=context_km,
                            time_shift_min=shift, clip_dbz=clip, domain_fine=domain)


def run_windows(a, ody, cfg):
    """Produce le finestre del CSV in parallelo e le accoda allo store (un solo scrittore)."""
    with open(a.windows_csv) as f:
        wins = [Window(dt.datetime.fromisoformat(r["t_start"]), int(r["row0"]), int(r["col0"]), a.T, a.H, a.W)
                for r in csv.DictReader(f)]
    w1 = refine_where(read_odim_composite(next(iter(ody.values())), a.quantity).where, cfg.factor)
    domain = (int(w1["ysize"]), int(w1["xsize"]))
    store = WindowStore(a.out, a.T, a.H, a.W,
                        store_attrs(w1, cfg, a.method, a.time_shift, a.clip_dbz, a.context_km))
    jobs = [(w, cfg, a.method, a.quantity, a.context_km, a.time_shift, a.clip_dbz, domain) for w in wins]
    ok = skipped = 0
    for win, res in _map(_window_job, jobs, ody, a.workers):
        ok, skipped = _store_result(store, win, res, ok, skipped)
    logging.info("finestre scritte: %d, scartate (buchi temporali): %d, totale nello store: %d",
                 ok, skipped, len(store))


def _sample_job(args):
    times, n_starts, scfg, seed, reader, origin = args
    return sample_block(_FILES, times, n_starts, scfg, seed, reader, origin)


def run_sample(a, ody):
    """Sceglie le finestre su ODYSSEY a 2 km e scrive il CSV per `windows` + metadati."""
    if os.path.exists(a.out) and not a.overwrite:
        raise SystemExit(f"{a.out} esiste gia': usa --overwrite per sostituirlo")
    scfg = SamplerConfig(T=a.T, H=a.H, W=a.W, step_t=a.step_t, step_px=a.step_px,
                         max_nan_frac=a.max_nan_frac, q_min=a.q_min, m=a.m, s=a.s, n_rand=a.n_rand,
                         clip_dbz=a.clip_dbz)
    w2 = read_odim_composite(next(iter(ody.values())), a.quantity).where
    reader, origin = read_odim_composite, (0, 0)
    if a.bbox:
        extent = bbox_extent(w2, a.bbox, a.buffer_km, align_m=float(w2["xscale"]))
        reader = functools.partial(read_odim_composite, extent=extent)
        origin = (int(round(extent[1] / float(w2["yscale"]))), int(round(extent[0] / float(w2["xscale"]))))
        logging.info("area di campionamento: %.0f x %.0f km, origine (%d, %d) a 2 km",
                     extent[2] / 1e3, extent[3] / 1e3, *origin)
    blocks = block_times(a.start, a.end, scfg, a.block_days)
    seeds = np.random.SeedSequence(a.seed).spawn(len(blocks))
    jobs = [(times, k, scfg, int(s.generate_state(1)[0]), reader, origin) for (times, k), s in zip(blocks, seeds)]
    rows, stats = [], {}
    for out, st in _map(_sample_job, jobs, ody, a.workers):
        rows += out
        for k, v in st.items():
            stats[k] = stats.get(k, 0) + v
    rows.sort(key=lambda r: (r["t_start"], r["row0"], r["col0"]))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["t_start", "row0", "col0", "q", "rain_score", "nan_frac"])
        w.writeheader(); w.writerows(rows)
    meta = {"csv": a.out, "odyssey_glob": a.odyssey_glob, "start": a.start.isoformat(), "end": a.end.isoformat(),
            "bbox": a.bbox, "buffer_km": a.buffer_km, "seed": a.seed, "block_days": a.block_days,
            "sampler": dataclasses.asdict(scfg), "frames_needed": scfg.frames_needed, "stats": stats,
            "created": dt.datetime.now().isoformat(timespec="seconds")}
    with open(os.path.splitext(a.out)[0] + "_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    logging.info("finestre accettate: %d | statistiche: %s", len(rows), stats)


def _store_result(store, win, res, ok, skipped):
    if res is None:
        logging.warning("finestra scartata (mancano frame ODYSSEY): %s", win)
        return ok, skipped + 1
    rr, alpha, times = res
    store.append(rr, alpha, times, win.row0, win.col0)
    return ok + 1, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def base(p):
        p.add_argument("--odyssey-glob", required=True)
        p.add_argument("--time-regex", default=None,
                       help="regex con un gruppo che cattura il timestamp nel nome file")
        p.add_argument("--time-format", default="%Y%m%d%H%M")
        p.add_argument("--quantity", default="DBZH")
        p.add_argument("--config", default=None, help="JSON con i campi di DownscaleConfig (e 'lk')")
        p.add_argument("--out", required=True)
        p.add_argument("-v", "--verbose", action="store_true")

    def common(p):
        base(p)
        p.add_argument("--start", required=True, type=dt.datetime.fromisoformat)
        p.add_argument("--end", required=True, type=dt.datetime.fromisoformat)
        p.add_argument("--bbox", type=float, nargs=4, default=None,
                       metavar=("LON_MIN", "LAT_MIN", "LON_MAX", "LAT_MAX"),
                       help="ritaglia in lettura al bbox (piu' --buffer-km), allineato a 2 km")
        p.add_argument("--buffer-km", type=float, default=0.0)

    p = sub.add_parser("downscale")
    common(p)
    p.add_argument("--method", default="lk", choices=["lk", "linear", "nearest"])
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--workers", type=int, default=1, help="processi paralleli (blocchi di 1 giorno)")
    p.add_argument("--time-shift", type=float, default=0.0,
                   help="minuti; 0 = etichette ODYSSEY, -2.5 = convenzione CIRRUS")

    p = sub.add_parser("sample", help="sceglie le finestre su ODYSSEY a 2 km -> CSV per `windows`")
    common(p)
    p.add_argument("--T", type=int, default=24)
    p.add_argument("--H", type=int, default=256)
    p.add_argument("--W", type=int, default=256)
    p.add_argument("--step-t", type=int, default=1, help="passo in frame ODYSSEY (15 min)")
    p.add_argument("--step-px", type=int, default=8, help="passo in pixel a 2 km")
    p.add_argument("--max-nan-frac", type=float, default=SamplerConfig.max_nan_frac)
    p.add_argument("--q-min", type=float, default=1e-4)
    p.add_argument("--m", type=float, default=0.1)
    p.add_argument("--s", type=float, default=1.0)
    p.add_argument("--n-rand", type=int, default=1)
    p.add_argument("--clip-dbz", type=float, default=60.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--block-days", type=float, default=7.0)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--overwrite", action="store_true")

    p = sub.add_parser("windows")
    base(p)
    p.add_argument("--windows-csv", required=True, help="colonne t_start (ISO), row0, col0 (griglia 1 km)")
    p.add_argument("--T", type=int, default=24)
    p.add_argument("--H", type=int, default=256)
    p.add_argument("--W", type=int, default=256)
    p.add_argument("--context-km", type=float, default=150.0, help="margine per lato per stimare il moto")
    p.add_argument("--time-shift", type=float, default=0.0)
    p.add_argument("--method", default="lk")
    p.add_argument("--clip-dbz", type=float, default=60.0)
    p.add_argument("--workers", type=int, default=1)

    p = sub.add_parser("validate")
    common(p)
    p.add_argument("--cirrus-glob", required=True)
    p.add_argument("--cirrus-time-regex", default=None, help="default: come --time-regex")
    p.add_argument("--cirrus-time-format", default=None)
    p.add_argument("--shifts", type=float, nargs="+", default=[0.0, -2.5])
    p.add_argument("--methods", nargs="+", default=["nearest", "linear", "lk"])
    p.add_argument("--pair-stride", type=int, default=4)
    p.add_argument("--fss-every", type=int, default=1)
    p.add_argument("--region-mask", default=None, help=".npy bool sulla griglia a 1 km")
    p.add_argument("--workers", type=int, default=1)

    a = ap.parse_args()
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_cfg(a.config)

    ody = index_files(a.odyssey_glob, a.time_regex, a.time_format, a.quantity)
    logging.info("ODYSSEY: %d file", len(ody))

    if a.cmd == "windows":
        run_windows(a, ody, cfg)
        return
    if a.cmd == "sample":
        run_sample(a, ody)
        return

    reader = read_odim_composite
    if a.bbox:
        w2 = read_odim_composite(next(iter(ody.values())), a.quantity).where
        extent = bbox_extent(w2, a.bbox, a.buffer_km, align_m=float(w2["xscale"]))
        reader = functools.partial(read_odim_composite, extent=extent)
        logging.info("ritaglio: offset %.0f, %.0f km, %.0f x %.0f km",
                     extent[0] / 1e3, extent[1] / 1e3, extent[2] / 1e3, extent[3] / 1e3)

    if a.cmd == "downscale":
        if a.workers > 1:
            out = run_downscaling_parallel(ody, a.start, a.end, a.out, cfg, a.quantity,
                                           method=a.method, overwrite=a.overwrite, workers=a.workers,
                                           reader=reader, time_shift_min=a.time_shift)
        else:
            out = run_downscaling(ody, a.start, a.end, a.out, cfg, a.quantity, method=a.method,
                                  overwrite=a.overwrite, reader=reader, time_shift_min=a.time_shift)
        logging.info("scritti %d file in %s", len(out), a.out)
    else:
        cir = index_files(a.cirrus_glob, a.cirrus_time_regex or a.time_regex,
                          a.cirrus_time_format or a.time_format, a.quantity)
        logging.info("CIRRUS: %d file", len(cir))
        ov = sorted(set(ody) & {t.replace(minute=t.minute - t.minute % 15) for t in cir})
        if ov:
            logging.info("sovrapposizione effettiva: %s -> %s", ov[0], ov[-1])
        region_mask = a.region_mask
        if region_mask and a.bbox:
            # maschera sulla griglia 1 km intera -> stessa finestra del ritaglio
            m = np.load(region_mask)
            w1 = read_odim_composite(next(iter(cir.values())), a.quantity).where
            if m.shape == (int(w1["ysize"]), int(w1["xsize"])):
                r0, r1, c0, c1 = extent_window(w1, extent)
                os.makedirs(a.out, exist_ok=True)
                region_mask = os.path.join(a.out, "region_mask_crop.npy")
                np.save(region_mask, m[r0:r1, c0:c1])
                logging.info("maschera ritagliata: %d pixel", int(m[r0:r1, c0:c1].sum()))
        summ = run_validation(ody, cir, a.start, a.end, a.out, cfg, shifts=a.shifts,
                              methods=a.methods, quantity=a.quantity, pair_stride=a.pair_stride,
                              fss_every=a.fss_every, region_mask_path=region_mask,
                              workers=a.workers, reader=reader)
        for r in summ:
            logging.info("%-8s shift=%+.1f alpha=%.3f  RMSE=%.2f  bias=%+.2f  CSI20=%.3f",
                         r["method"], r["shift_min"], r["alpha"], r["rmse"], r["bias"],
                         r.get("csi_20", float("nan")))


if __name__ == "__main__":
    main()
