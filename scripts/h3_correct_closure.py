"""Closure test of the level correction (H3, #20): does the shift in dBZ on the pixels give back the intensity
offset on the ERA5-Land cell-hours?

The offsets of `opera_ds.correct` were estimated on hourly sums over the Belgian ERA5-Land cells (docs/method.md,
*Volume or intensity* and *Level on the intensity*). They are applied as one shift in dBZ on the 2 km / 15 min
pixels, where the rain threshold (7 dBZ) and the cap (55 dBZ) make the effect not exactly a factor k. This
script sums each month twice, uncorrected and corrected, the same way, and compares the two:

- intensity: log10 of the ratio of the mean rain of the wet cell-hours (at least 0.1 mm), corrected / uncorrected,
  each over its own wet cell-hours, as in the trial; it should equal log10 k of the period;
- frequency: log10 of the ratio of the wet cell-hours, corrected / uncorrected; the shift changes it only near
  the threshold;
- volume: log10 of the ratio of the totals.

ERA5-Land is the same on both sides, so it cancels: the residual of the intensity offset against CIRRUS D after
the correction is log10 k minus the measured intensity change.

Cleaning: as in `scripts/odyssey_clean_era5grid.py` (#96), where the offsets were estimated: values above 70 dBZ,
the Gabella filter and the static mask of the period (`opera_ds.clean.clean_composite`), read from
`results/h2_artefacts/` (`static_mask_proposal_P<k>.npy`, `db_rowcol_odyssey_crop.json`, `nodes_odyssey.csv`), each
masked pixel switched on with its radar listed that day. With --no-static the mask is left out (first run, on a PC
without those files); the closure then is not on the pixels of the estimation. Rain rate: `opera_ds.clean.rain_rate`
(Marshall-Palmer from 7 dBZ, capped at 55 dBZ). The cells and hours are built as in
`scripts/odyssey_clean_era5grid.py` (#96): each 15 min frame closes the hour that ends at or after its label;
per cell and hour, the mean rain of its covered Belgian pixels times the number of frames of the hour.

  uv run python scripts/h3_correct_closure.py --months 2014-01:2014-12 2017-01:2017-12 2021-01:2021-12
  uv run python scripts/h3_correct_closure.py --summary

Writes results/h3_level/closure_<YYYY-MM>.npz (closure-nostatic_<YYYY-MM>.npz with --no-static), skips the months
already written, and prints the table.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import glob
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

from opera_ds.paths import DATA_DIR, RESULTS_DIR

OUT = RESULTS_DIR / "h3_level"
H2 = RESULTS_DIR / "h2_artefacts"
LAT_N, LON_W, STEP, NLAT, NLON = 55.0, -3.9, 0.1, 95, 158     # ERA5-Land grid of data/era5land_bel.zarr
STEP_H = 0.25
WET_MM = 0.1


def belgian_window():
    """Window of the ODYSSEY crop (rows, cols at 2 km) and its Belgian pixels, from the 1 km Belgium mask."""
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


def prefix(static: bool) -> str:
    return "closure" if static else "closure-nostatic"


def listed_by_day() -> dict[int, set[str]]:
    """Radars listed in at least half of the day's time steps, per day (YYYYMMDD), as scripts/odyssey_clean_era5grid.py."""
    import pandas as pd

    nd = pd.read_csv(H2 / "nodes_odyssey.csv")
    nd = nd[nd.steps_listed >= 0.5 * nd.steps_day]
    return nd.groupby("day").node.apply(set).to_dict()


def static_mask(period: int):
    """Static mask of H2 for period index `period` (0 = A), on the 2 km crop, with the radars of the crop."""
    from opera_ds.clean import StaticMask

    radars = {k: (v["row"], v["col"]) for k, v in json.loads((H2 / "db_rowcol_odyssey_crop.json").read_text()).items()}
    mask = np.load(H2 / f"static_mask_proposal_P{period + 1}.npy").astype(bool)
    return StaticMask(mask, radars=radars, pixel_km=2.0)


def month(ym: str, static: bool = True) -> str:
    from opera_ds.clean import clean_composite, rain_rate
    from opera_ds.correct import V1, correct_composite, period_index
    from opera_ds.odim_io import read_odim_composite

    path = OUT / f"{prefix(static)}_{ym}.npz"
    if path.exists():
        return f"{ym}: already written"
    y, m = map(int, ym.split("-"))
    start = dt.datetime(y, m, 1, 1)
    p = period_index(dt.datetime(y, m, 1))
    mask, listed = (static_mask(p), listed_by_day()) if static else (None, {})
    files = sorted(glob.glob(str(DATA_DIR / "odyssey_bel" / f"{y}" / f"{m:02d}" / "*.h5")))
    nh = calendar.monthrange(y, m)[1] * 24
    win, m2 = belgian_window()
    idx = None
    frames = np.zeros(nh, np.int32)
    bad = 0
    for fp in files:
        try:
            f = read_odim_composite(fp, "DBZH")
        except Exception:  # noqa: BLE001
            bad += 1
            continue
        if idx is None:
            idx = cell_index(f.where, win, m2)
            sel = idx >= 0
            cells, inv = np.unique(idx[sel], return_inverse=True)
            sums = {k: np.zeros((nh, len(cells))) for k in ("raw", "corr")}
            cover = np.zeros((nh, len(cells)), np.int64)
        k = int(np.ceil((f.time - start).total_seconds() / 3600.0))
        if not 0 <= k < nh:
            continue
        day = int(f.time.strftime("%Y%m%d"))
        clean = clean_composite(f.to_field(0.0), mask, listed.get(day, set()), gabella=True)
        corr = correct_composite(clean, f.time, V1)
        a, b = int(f.where.get("crop_row0", 0)), int(f.where.get("crop_col0", 0))
        s = (slice(win[0] - a, win[1] - a), slice(win[2] - b, win[3] - b))
        for key, field in (("raw", clean), ("corr", corr)):
            z = field[s][sel]
            ok = np.isfinite(z)
            sums[key][k] += np.bincount(inv[ok], weights=rain_rate(z[ok]) * STEP_H, minlength=len(cells))
            if key == "raw":
                cover[k] += np.bincount(inv[ok], minlength=len(cells))
        frames[k] += 1
    if idx is None:
        return f"{ym}: no readable file"
    out = {f"rain_{key}": (v * frames[:, None] / np.maximum(cover, 1)).astype(np.float32) for key, v in sums.items()}
    np.savez_compressed(path, frames=frames, cover=cover, period=p, n_bad=bad,
                        cells=np.stack([cells // NLON, cells % NLON], 1), **out)
    return f"{ym}: {len(files)} files, period {'ABC'[p]}, {bad} unreadable, static mask {'on' if static else 'off'}"


def split(raw: np.ndarray, corr: np.ndarray) -> dict:
    """log10 ratios corrected / uncorrected of the wet cell-hours, their mean rain and the total."""
    wr, wc = raw >= WET_MM, corr >= WET_MM
    return {
        "frequency": np.log10(wc.sum() / wr.sum()),
        "intensity": np.log10(corr[wc].mean() / raw[wr].mean()),
        "volume": np.log10(corr.sum() / raw.sum()),
        "wet_raw": int(wr.sum()),
    }


def summary(static: bool = True) -> None:
    from opera_ds.correct import V1

    print(f"static mask {'on' if static else 'off'}")
    by_period: dict[int, list] = {}
    for fp in sorted(OUT.glob(f"{prefix(static)}_*.npz")):
        z = np.load(fp)
        ok = z["frames"] > 0
        raw, corr = z["rain_raw"][ok].ravel(), z["rain_corr"][ok].ravel()
        good = np.isfinite(raw) & np.isfinite(corr)
        by_period.setdefault(int(z["period"]), []).append((fp.stem[-7:], raw[good], corr[good]))
    print("period | months | log10 k applied | intensity | residual (k - intensity) | frequency | volume | "
          "monthly intensity, min to max")
    for p in sorted(by_period):
        rows = by_period[p]
        raw = np.concatenate([r for _, r, _ in rows])
        corr = np.concatenate([c for _, _, c in rows])
        s = split(raw, corr)
        mon = [split(r, c)["intensity"] for _, r, c in rows if (r >= WET_MM).any()]
        k = V1.log10_k[p]
        print(f"{'ABC'[p]} | {rows[0][0]} to {rows[-1][0]} ({len(rows)}) | {k:+.4f} | {s['intensity']:+.4f} | "
              f"{k - s['intensity']:+.4f} | {s['frequency']:+.4f} | {s['volume']:+.4f} | "
              f"{min(mon):+.4f} to {max(mon):+.4f}")


def months(spec: str) -> list[str]:
    first, _, last = spec.partition(":")
    last = last or first
    y, m = map(int, first.split("-"))
    out = []
    while f"{y}-{m:02d}" <= last:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--months", nargs="*", default=[], help="YYYY-MM or YYYY-MM:YYYY-MM")
    ap.add_argument("--processes", type=int, default=8)
    ap.add_argument("--summary", action="store_true", help="only print the table of the months written")
    ap.add_argument("--no-static", dest="static", action="store_false",
                    help="leave out the static mask of H2 (not the cleaning of the estimation)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [ym for spec in args.months for ym in months(spec)]
    if todo and not args.summary:
        if args.processes == 1:
            for ym in todo:
                print(month(ym, args.static), flush=True)
        else:
            with ProcessPoolExecutor(args.processes) as ex:
                for fut in as_completed([ex.submit(month, ym, args.static) for ym in todo]):
                    print(fut.result(), flush=True)
    summary(args.static)


if __name__ == "__main__":
    main()
