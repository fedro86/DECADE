"""How much does the CIRRUS time window change ODYSSEY? (H3, #20; test 2 of the review of #96, 17/11/2026)

ODYSSEY crops cleaned as in H3 (clean_composite, static mask of the period), interpolated by LK to 1 km and 1 min
on the Belgian window plus a margin. Every 5 min frame NT is built in two ways:
  (a) the interpolated field at NT, as the archive does now;
  (b) the maximum over the 1 min fields in (NT-10, NT], i.e. NT-9 ... NT, as CIRRUS would.
Each frame gives Marshall-Palmer rain (from 7 dBZ, capped at 55 dBZ) and closes the hour that ends at or after NT;
per ERA5-Land cell and hour, the mean over its Belgian pixels (the 1 km pixel takes the cell of its 2 km pixel).

The twelve sample months of period C (one per calendar month, 2018-2024), about 25 min with 16 processes:

  uv run python scripts/cirrus_window_odyssey.py --processes 16 --out results/h3_level/window_test2 \
      --days 2018-08 2019-01 2019-09 2020-02 2020-10 2021-03 2021-07 2022-04 2022-11 2023-05 2023-12 2024-06

Writes OUT/w_<YYYYMMDD>.npz per day: sum_a, sum_b (mm per hour and cell), frames_a, frames_b (frames per hour),
cover_a, cover_b, cells, hour_end. Days already written are skipped.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import importlib.util
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from opera_ds.paths import DATA_DIR, RESULTS_DIR  # noqa: E402

_spec = importlib.util.spec_from_file_location("oce", REPO / "scripts" / "odyssey_clean_era5grid.py")
oce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oce)

MARGIN = 50  # 2 km pixels (100 km) of context around the Belgian window
H2 = RESULTS_DIR / "h2_artefacts"


def day_job(args):
    day, out_dir, step_min = args
    from opera_ds.clean import StaticMask, clean_composite
    from opera_ds.interp import DownscaleConfig
    from opera_ds.odim_io import read_odim_composite
    from opera_ds.pipeline import FrameSource

    out = Path(out_dir) / f"w_{day:%Y%m%d}.npz"
    if out.exists():
        return f"{day:%Y-%m-%d}: already written"
    t_start = time.time()
    ym = f"{day:%Y-%m}"
    win, m2 = oce.belgian_window()
    radars = {k: (v["row"], v["col"]) for k, v in json.loads((H2 / "db_rowcol_odyssey_crop.json").read_text()).items()}
    static = StaticMask(np.load(H2 / f"static_mask_proposal_P{oce.period_of(ym)}.npy").astype(bool), radars=radars,
                        pixel_km=2.0)
    listed = oce.listed_by_day()
    files = {}
    for d in (day - dt.timedelta(days=1), day, day + dt.timedelta(days=1)):
        for p in glob.glob(str(DATA_DIR / "odyssey_bel" / f"{d:%Y}" / f"{d:%m}" / f"*{d:%Y%m%d}T*.h5")):
            t = dt.datetime.strptime(Path(p).name.split("@")[1], "%Y%m%dT%H%M")
            files[t] = p
    first = read_odim_composite(files[min(files)], "DBZH")
    a0, b0 = int(first.where.get("crop_row0", 0)), int(first.where.get("crop_col0", 0))
    r0, r1 = max(win[0] - a0 - MARGIN, 0), win[1] - a0 + MARGIN
    c0, c1 = max(win[2] - b0 - MARGIN, 0), win[3] - b0 + MARGIN
    br0, bc0 = win[0] - a0 - r0, win[2] - b0 - c0  # Belgian window inside the sub-crop (2 km)
    hb, wb = win[1] - win[0], win[3] - win[2]
    idx2 = oce.cell_index(first.where, win, m2)
    idx1 = np.repeat(np.repeat(idx2, 2, 0), 2, 1)
    sel = idx1 >= 0
    cells, inv = np.unique(idx1[sel], return_inverse=True)

    cfg = DownscaleConfig(dt_out_min=step_min)

    class CleanSource(FrameSource):
        def field(self, t):
            fr = self.frame(t)
            if fr is None:
                return None
            dbz = fr.to_field(0.0)
            c = clean_composite(dbz, static, listed.get(int(t.strftime("%Y%m%d")), set()), gabella=True)
            return np.where(np.isfinite(c), np.maximum(c, 0.0), np.nan)[r0:r1, c0:c1].astype(np.float32)

    src = CleanSource(files, cfg)
    n_sub = cfg.n_sub
    nh = 24
    h_start = day + dt.timedelta(hours=1)  # hour k ends at day 01:00 + k h
    sums = {k: np.zeros((nh, len(cells))) for k in ("a", "b")}
    cover = {k: np.zeros((nh, len(cells))) for k in ("a", "b")}
    nfr = {k: np.zeros(nh, np.int32) for k in ("a", "b")}
    buf: dict[dt.datetime, np.ndarray] = {}
    w = int(10 / step_min)  # fine fields in (NT-10, NT]
    t0 = day - dt.timedelta(minutes=15)
    end = day + dt.timedelta(days=1)
    while t0 <= end:
        pi = src.pair(t0)
        if pi is None:
            buf.clear()
            t0 += dt.timedelta(minutes=15)
            continue
        for j in range(n_sub):
            t = t0 + dt.timedelta(minutes=j * step_min)
            val, cov, _ = pi.get(j / n_sub, "lk")
            v = np.where(cov, val, np.nan)[2 * br0:2 * (br0 + hb), 2 * bc0:2 * (bc0 + wb)]
            buf[t] = v
            for old in [k for k in buf if k <= t - dt.timedelta(minutes=10)]:
                del buf[old]
            if t.minute % 5 or t <= day or t > end:
                continue
            k = int(np.ceil((t - day).total_seconds() / 3600.0)) - 1
            if not 0 <= k < nh:
                continue
            fields = {"a": v}
            if len(buf) == w:
                stack = np.stack(list(buf.values()))
                cov_all = np.isfinite(stack).all(0)
                fields["b"] = np.where(cov_all, np.nanmax(np.where(np.isfinite(stack), stack, -np.inf), 0), np.nan)
                fields["a"] = np.where(cov_all, v, np.nan)  # same pixels for both
            else:
                continue
            for key, f in fields.items():
                r = oce.rain(f)[sel]
                ok = np.isfinite(r)
                sums[key][k] += np.bincount(inv[ok], weights=r[ok] * (5 / 60),
                                            minlength=len(cells))
                cover[key][k] += np.bincount(inv[ok], minlength=len(cells))
                nfr[key][k] += 1
        t0 += dt.timedelta(minutes=15)
    npix = np.bincount(inv, minlength=len(cells))
    res = {}
    for key in ("a", "b"):
        # mean over covered pixels, scaled to the 12 frames of the hour
        res[f"sum_{key}"] = (sums[key] * 12 / np.maximum(cover[key], 1)).astype(np.float32)
        res[f"frames_{key}"] = nfr[key]
        res[f"cover_{key}"] = (cover[key] / np.maximum(nfr[key][:, None], 1) / npix).astype(np.float32)
    np.savez_compressed(out, cells=np.stack([cells // oce.NLON, cells % oce.NLON], 1),
                        hour_end=np.array([(h_start + dt.timedelta(hours=h)).isoformat() for h in range(nh)]),
                        step_min=step_min, **res)
    return f"{day:%Y-%m-%d}: {time.time() - t_start:.0f} s, frames/h {nfr['a'].mean():.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", nargs="+", required=True, help="YYYY-MM-DD, or YYYY-MM for a whole month")
    ap.add_argument("--processes", type=int, default=8)
    ap.add_argument("--step-min", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    days = []
    for s in a.days:
        if len(s) == 7:
            y, m = map(int, s.split("-"))
            d = dt.datetime(y, m, 1)
            while d.month == m:
                days.append(d)
                d += dt.timedelta(days=1)
        else:
            days.append(dt.datetime.strptime(s, "%Y-%m-%d"))
    with ProcessPoolExecutor(a.processes) as ex:
        for msg in ex.map(day_job, [(d, a.out, a.step_min) for d in days]):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
