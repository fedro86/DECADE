"""Hourly ODYSSEY rain on the Belgian ERA5-Land cells, before and after the first-version cleaning (H3, #20).

The same sums as notebook 07, section 4 (`era5grid_odyssey_<YYYY-MM>.npz`), on the ODYSSEY crops cleaned as in H2
(`docs/method.md`, *Static mask: rules in the literature* and *Rule of the first version*), with
`opera_ds.clean.clean_composite`:

- values above 70 dBZ removed, then the Gabella filter, on the whole crop;
- the static mask of the period (4/2013-11/2015, 12/2015-7/2018, 8/2018-6/2024), read from
  `results/h2_artefacts/static_mask_proposal_P<k>.npy` (the H2 rule on the monthly catalogue), each masked pixel
  attached to its radar within 20 km and switched on with the radars listed that day (`nodes_odyssey.csv`: listed
  in at least half of the day's time steps, as in notebook 05), filled as in EURADCLIM.

Rain rate as in notebook 07: Marshall-Palmer from 7 dBZ, capped at 55 dBZ; each 15 min frame closes the hour that
ends at or after its label. Per cell and hour, the mean rain (mm) of its covered Belgian pixels, both raw and
cleaned, so the raw sums can be checked against the notebook's files.

  uv run python scripts/odyssey_clean_era5grid.py --first 2013-04 --last 2024-06 --processes 16

Use --last 2024-07 to add the overlap days, 1-5/7/2024, with the mask of the last period.

Writes results/h3_level/era5grid_odyssey_clean_<YYYY-MM>.npz and prints one line per month when it is done.
Months already written are skipped.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import glob
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from opera_ds.paths import DATA_DIR, RESULTS_DIR

H2 = RESULTS_DIR / "h2_artefacts"
OUT = RESULTS_DIR / "h3_level"
LAT_N, LON_W, STEP, NLAT, NLON = 55.0, -3.9, 0.1, 95, 158
STEP_H = 0.25
# periods of the static mask; the mask of 8/2018-6/2024 also serves the last ODYSSEY days, 1-5/7/2024 (overlap)
PERIODS = (("2013-04", "2015-11"), ("2015-12", "2018-07"), ("2018-08", "2024-07"))


def belgian_window():
    """Window of the ODYSSEY crop (rows, cols at 2 km) and its Belgian cells, as notebook 07, cell 3."""
    mask = np.load(DATA_DIR / "mask_BEL_1km.npy")
    r, c = np.where(mask.any(1))[0], np.where(mask.any(0))[0]
    r0, r1 = r[0] // 2 * 2, (r[-1] + 2) // 2 * 2
    c0, c1 = c[0] // 2 * 2, (c[-1] + 2) // 2 * 2
    m1 = mask[r0:r1, c0:c1]
    m2 = m1.reshape(m1.shape[0] // 2, 2, m1.shape[1] // 2, 2).sum((1, 3)) >= 2
    return (r0 // 2, r1 // 2, c0 // 2, c1 // 2), m2


def cell_index(where, win, m):
    """ERA5-Land cell (flat index) of each pixel centre of the window, nearest cell centre; -1 if not Belgian."""
    from pyproj import Proj

    from opera_ds.bridge import cell_index as bridge_cell_index

    p = Proj(where["projdef"])
    sx, sy = float(where["xscale"]), float(where["yscale"])
    xu, yu = p(float(where["UL_lon"]), float(where["UL_lat"]))
    a, b = int(where.get("crop_row0", 0)), int(where.get("crop_col0", 0))
    rr, cc = np.mgrid[win[0] - a:win[1] - a, win[2] - b:win[3] - b]
    lon, lat = p(xu + (cc + 0.5) * sx, yu - (rr + 0.5) * sy, inverse=True)
    elat = np.round(LAT_N - STEP * np.arange(NLAT), 4)
    elon = np.round(LON_W + STEP * np.arange(NLON), 4)
    return np.where(m, bridge_cell_index(elat, elon, lat, lon), -1)


def rain(dbz: np.ndarray) -> np.ndarray:
    """Marshall-Palmer from 7 dBZ capped at 55 dBZ; NaN (outside coverage) stays NaN."""
    z = np.nan_to_num(dbz, nan=0.0)
    r = np.where((z >= 7) & (z <= 70), (10 ** (np.minimum(z, 55.0) / 10) / 200.0) ** (1 / 1.6), 0.0)
    return np.where(np.isfinite(dbz), r, np.nan)


def period_of(ym: str) -> int:
    for k, (a, b) in enumerate(PERIODS, 1):
        if a <= ym <= b:
            return k
    raise ValueError(f"{ym} is outside the periods of the static mask")


def listed_by_day() -> dict[int, set[str]]:
    import pandas as pd

    nd = pd.read_csv(H2 / "nodes_odyssey.csv")
    nd = nd[nd.steps_listed >= 0.5 * nd.steps_day]
    return nd.groupby("day").node.apply(set).to_dict()


def month(ym: str) -> str:
    from opera_ds.clean import StaticMask, clean_composite
    from opera_ds.odim_io import read_odim_composite

    path = OUT / f"era5grid_odyssey_clean_{ym}.npz"
    if path.exists():
        return f"{ym}: already written"
    win, m2 = belgian_window()
    radars = {k: (v["row"], v["col"]) for k, v in json.loads((H2 / "db_rowcol_odyssey_crop.json").read_text()).items()}
    static = StaticMask(np.load(H2 / f"static_mask_proposal_P{period_of(ym)}.npy").astype(bool), radars=radars,
                        pixel_km=2.0)
    listed = listed_by_day()
    y, m = map(int, ym.split("-"))
    files = sorted(glob.glob(str(DATA_DIR / "odyssey_bel" / f"{y}" / f"{m:02d}" / "*.h5")))
    nh = calendar.monthrange(y, m)[1] * 24
    start = dt.datetime(y, m, 1, 1)
    idx = None
    frames = np.zeros(nh, np.int32)
    bad = 0
    for p in files:
        try:
            f = read_odim_composite(p, "DBZH")
        except Exception:  # noqa: BLE001
            bad += 1
            continue
        if idx is None:
            idx = cell_index(f.where, win, m2)
            sel = idx >= 0
            cells, inv = np.unique(idx[sel], return_inverse=True)
            npix = np.bincount(inv, minlength=len(cells))
            sums = {k: np.zeros((nh, len(cells))) for k in ("raw", "clean")}
            cover = np.zeros((nh, len(cells)), np.int64)
        k = int(np.ceil((f.time - start).total_seconds() / 3600.0))
        if not 0 <= k < nh:
            continue
        dbz = f.to_field(0.0)
        day = int(f.time.strftime("%Y%m%d"))
        clean = clean_composite(dbz, static, listed.get(day, set()), gabella=True)
        a, b = int(f.where.get("crop_row0", 0)), int(f.where.get("crop_col0", 0))
        s = (slice(win[0] - a, win[1] - a), slice(win[2] - b, win[3] - b))
        for key, field in (("raw", dbz), ("clean", clean)):
            r = rain(field[s])[sel]
            ok = np.isfinite(r)
            sums[key][k] += np.bincount(inv[ok], weights=r[ok] * STEP_H, minlength=len(cells))
            if key == "raw":
                cover[k] += np.bincount(inv[ok], minlength=len(cells))
        frames[k] += 1
    if idx is None:
        return f"{ym}: no readable file"
    out = {f"rain_{key}": (v * frames[:, None] / np.maximum(cover, 1)).astype(np.float32) for key, v in sums.items()}
    hours = [(start + dt.timedelta(hours=h)).isoformat() for h in range(nh)]
    np.savez_compressed(path, frames=frames, cover=cover, npix=npix, cells=np.stack([cells // NLON, cells % NLON], 1),
                        hour_end=np.array(hours), period=period_of(ym), n_bad=bad, **out)
    return f"{ym}: {len(files)} file, period P{period_of(ym)}, {bad} unreadable"


def months(first: str, last: str) -> list[str]:
    y, m = map(int, first.split("-"))
    out = []
    while f"{y}-{m:02d}" <= last:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--first", default="2013-04")
    ap.add_argument("--last", default="2024-06")
    ap.add_argument("--processes", type=int, default=16)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    todo = months(args.first, args.last)
    if args.processes == 1:
        for ym in todo:
            print(month(ym), flush=True)
        return
    with ProcessPoolExecutor(args.processes) as ex:
        for fut in as_completed([ex.submit(month, ym) for ym in todo]):
            print(fut.result(), flush=True)
    print("FINITO", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
