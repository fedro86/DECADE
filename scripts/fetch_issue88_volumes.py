"""#88: single-radar volumes of three Belgian radars on rainy hours before and after 18/11/2025 (H3).

For each radar (Helchteren `behel`, Wideumont `bewid`, Jabbeke `bejab`) and each window (before: 15/9–17/11/2025,
after: 19/11/2025–31/1/2026) the script picks the N rainiest hours, one per day, by the mean ERA5-Land rain within
50 km of the radar, among the hours with a complete CIRRUS hour on the ERA5-Land grid
(`<RESULTS_DIR>/h3_level/era5grid_cirrus_YYYY-MM.npz`, written by `scripts/odyssey_clean_era5grid.py`). It then
downloads from the public ORD bucket the lowest-elevation DBZH volume of that hour (`@0.3_` scan of minute 00).

It also lists which quantities each radar delivers at 12 UTC on a few days around the change, for the comparison
of notebook 07, section 11.

Output in <DATA_DIR>/opera_pvol/issue88/: the volumes (about 75 MB), `hours.json` with the hours picked per radar
and window, and `delivered.json` with the listings. Files already present are not downloaded again.

    uv run python scripts/fetch_issue88_volumes.py
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import urllib.request

import numpy as np

from opera_ds.ord import BUCKET, list_keys
from opera_ds.paths import DATA_DIR, RESULTS_DIR

OUT = DATA_DIR / "opera_pvol" / "issue88"
RADARS = {"behel": (5.4054, 51.0702), "bewid": (5.5044, 49.9135), "bejab": (3.0641, 51.1919)}
WINDOWS = {"before": ("2025-09-15", "2025-11-18"), "after": ("2025-11-19", "2026-02-01")}
N = 15
DELIVERED_DAYS = {"bewid": ("2025-12-31", "2026-01-01"), "behel": ("2026-01-06", "2026-01-07"),
                  "bejab": ("2025-07-20", "2026-03-10")}


def rainy_hours(node: str) -> dict[str, list[str]]:
    """Top-N hours (one per day) by ERA5-Land rain within 50 km of the radar, per window; complete CIRRUS hours."""
    import xarray as xr

    era = xr.open_zarr(DATA_DIR / "era5land_bel.zarr", consolidated=False)
    x, y = RADARS[node]
    out = {}
    for name, (a, b) in WINDOWS.items():
        cand = []
        for f in sorted(glob.glob(str(RESULTS_DIR / "h3_level" / "era5grid_cirrus_20*.npz"))):
            ym = os.path.basename(f)[-11:-4]
            if not a[:7] <= ym <= b[:7]:
                continue
            z = np.load(f)
            lat = 55.0 - 0.1 * z["cells"][:, 0]
            lon = -3.9 + 0.1 * z["cells"][:, 1]
            near = np.hypot((lon - x) * 0.63, lat - y) * 111 <= 50
            hours = np.array(z["hour_end"], dtype="datetime64[ns]")
            ok = (z["frames"] == 12) & (hours >= np.datetime64(a)) & (hours < np.datetime64(b))
            if not ok.any():
                continue
            e = era["tp"].sel(valid_time=hours[ok]).values[:, z["cells"][near, 0], z["cells"][near, 1]]
            e = np.nanmean(e, 1)
            cand += [(v, h) for v, h in zip(e, hours[ok]) if np.isfinite(v)]
        cand.sort(key=lambda c: -c[0])
        days, pick = set(), []
        for _, h in cand:
            d = str(h)[:10]
            if d not in days:
                days.add(d)
                pick.append(str(h.astype("datetime64[m]")))
            if len(pick) == N:
                break
        out[name] = pick
    return out


def volume(node: str, t: dt.datetime) -> str | None:
    """Lowest-elevation DBZH volume of the radar at time t, downloaded once; None if the bucket has none."""
    keys = [k for k, _ in list_keys(f"{t:%Y/%m/%d}/BE/{node}/PVOL/")
            if f"@{t:%Y%m%dT%H%M}@0.3_" in k and k.endswith("@DBZH.h5")]
    if not keys:
        return None
    key = sorted(keys)[0]
    path = OUT / os.path.basename(key)
    if not path.exists():
        urllib.request.urlretrieve(f"{BUCKET}/{key}", path)
    return path.name


def delivered(day: dt.date, node: str) -> list[str]:
    """Quantities of the files the radar delivered at 12 UTC of that day."""
    return sorted({k.split("@", 2)[2] for k, _ in list_keys(f"{day:%Y/%m/%d}/BE/{node}/") if f"@{day:%Y%m%d}T12" in k})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hours, files = {}, {}
    for node in RADARS:
        hours[node] = rainy_hours(node)
        for name, ts in hours[node].items():
            for t in ts:
                files[f"{node} {t}"] = volume(node, dt.datetime.fromisoformat(t))
        print(node, {k: len(v) for k, v in hours[node].items()})
    with open(OUT / "hours.json", "w", encoding="utf-8") as f:
        json.dump({"hours": hours, "files": files}, f, indent=1)
    listing = {node: {d: [x for x in delivered(dt.date.fromisoformat(d), node) if "_" in x.split("@")[0]]
                      for d in days} for node, days in DELIVERED_DAYS.items()}
    with open(OUT / "delivered.json", "w", encoding="utf-8") as f:
        json.dump(listing, f, indent=1)
    print("written", OUT)


if __name__ == "__main__":
    main()
