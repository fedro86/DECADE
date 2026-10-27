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
"""
from __future__ import annotations

import argparse
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
from opera_ds.odim_io import bbox_extent, extent_window, read_odim_composite  # noqa: E402
from opera_ds.pipeline import run_downscaling_parallel  # noqa: E402


def load_cfg(path: str | None) -> DownscaleConfig:
    cfg = DownscaleConfig()
    if path:
        with open(path) as f:
            d = json.load(f)
        lk = d.pop("lk", {})
        cfg = dataclasses.replace(cfg, **d, lk=dataclasses.replace(LKParams(), **lk))
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--odyssey-glob", required=True)
        p.add_argument("--time-regex", default=None,
                       help="regex con un gruppo che cattura il timestamp nel nome file")
        p.add_argument("--time-format", default="%Y%m%d%H%M")
        p.add_argument("--quantity", default="DBZH")
        p.add_argument("--start", required=True, type=dt.datetime.fromisoformat)
        p.add_argument("--end", required=True, type=dt.datetime.fromisoformat)
        p.add_argument("--config", default=None, help="JSON con i campi di DownscaleConfig (e 'lk')")
        p.add_argument("--out", required=True)
        p.add_argument("--bbox", type=float, nargs=4, default=None,
                       metavar=("LON_MIN", "LAT_MIN", "LON_MAX", "LAT_MAX"),
                       help="ritaglia in lettura al bbox (piu' --buffer-km), allineato a 2 km")
        p.add_argument("--buffer-km", type=float, default=0.0)
        p.add_argument("-v", "--verbose", action="store_true")

    p = sub.add_parser("downscale")
    common(p)
    p.add_argument("--method", default="lk", choices=["lk", "linear", "nearest"])
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--workers", type=int, default=1, help="processi paralleli (blocchi di 1 giorno)")

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
                                           reader=reader)
        else:
            out = run_downscaling(ody, a.start, a.end, a.out, cfg, a.quantity, method=a.method,
                                  overwrite=a.overwrite, reader=reader)
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
