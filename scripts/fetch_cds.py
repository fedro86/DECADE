"""Download pan-European bridge data from the Copernicus Climate Data Store (S7, #13), one file per month.

- `era5-land`: ERA5-Land hourly total precipitation, cut on the server to `--area`. The CDS field is
  accumulated from 00 UTC: the value at 00 UTC is the total of the previous day, and hourly amounts are
  differences of consecutive hours (docs/data.md).
- `cerra-land`: CERRA-Land daily total precipitation (analysis, 06 UTC). The CDS serves only the whole
  European grid (1069 x 1069, 5.5 km), so each month is downloaded whole, cut to the smallest window of grid
  cells that covers `--area`, and the whole file is deleted.

Files are netCDF, `<out>/<YYYY>/<dataset>_<YYYYMM>.nc`. Months already on disk are skipped, so an interrupted
run resumes; failures are listed in `<out>/failed.txt`. The token is read from `COPERNICUS_CDS_API_KEY`, in the
environment or in `.env` at the repository root; the dataset licence must be accepted on the CDS website.

The default `--area` is the lon/lat box of the Belgian working crop (Belgium + 350 km; docs/data.md, *Derived
datasets*) plus one ERA5-Land cell.

Example (sizes and times in docs/usage.md, *Costs*):
  uv run python scripts/fetch_cds.py --dataset era5-land --start 2012-01 --end 2026-10 --out data/era5land_bel
  uv run python scripts/fetch_cds.py --dataset cerra-land --start 2012-01 --end 2025-12 --out data/cerraland_bel
"""
from __future__ import annotations

import argparse
import calendar
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from opera_ds.paths import REPO_DIR

CDS_URL = "https://cds.climate.copernicus.eu/api"
AREA = (55.0, -3.9, 45.6, 11.8)  # N, W, S, E
DATASETS = {"era5-land": "reanalysis-era5-land", "cerra-land": "reanalysis-cerra-land"}


def cds_key() -> str:
    key = os.environ.get("COPERNICUS_CDS_API_KEY", "")
    env = REPO_DIR / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*COPERNICUS_CDS_API_KEY\s*=\s*(.*)", line)
            if m:
                key = m.group(1).strip().strip("\"'")
    if not key:
        raise SystemExit("COPERNICUS_CDS_API_KEY is not set (environment or .env)")
    return key


def months(start: str, end: str):
    y, m = map(int, start.split("-"))
    y1, m1 = map(int, end.split("-"))
    while (y, m) <= (y1, m1):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def request(dataset: str, y: int, m: int, area) -> dict:
    days = [f"{d:02d}" for d in range(1, calendar.monthrange(y, m)[1] + 1)]
    req = {"variable": ["total_precipitation"], "year": f"{y}", "month": f"{m:02d}", "day": days,
           "data_format": "netcdf"}
    if dataset == "era5-land":
        req |= {"time": [f"{h:02d}:00" for h in range(24)], "area": list(area), "download_format": "unarchived"}
    else:
        req |= {"time": ["06:00"], "level_type": "surface", "product_type": "analysis"}
    return req


def cut_to_area(src: Path, dst: Path, area) -> None:
    """Keep the smallest window of grid cells of a CERRA-Land file whose cells cover `area`."""
    import xarray as xr

    n, w, s, e = area
    with xr.open_dataset(src) as ds:
        lat = ds["latitude"].values
        lon = (ds["longitude"].values + 180.0) % 360.0 - 180.0
        inside = (lat >= s) & (lat <= n) & (lon >= w) & (lon <= e)
        rows, cols = np.flatnonzero(inside.any(1)), np.flatnonzero(inside.any(0))
        win = ds.isel(y=slice(max(rows[0] - 1, 0), rows[-1] + 2), x=slice(max(cols[0] - 1, 0), cols[-1] + 2))
        win = win.assign_coords(longitude=(win["longitude"] + 180.0) % 360.0 - 180.0).load()
    enc = {v: {"zlib": True, "complevel": 4} for v in win.data_vars}
    win.to_netcdf(dst, engine="h5netcdf", encoding=enc)


def fetch_month(client, dataset: str, y: int, m: int, out: Path, area) -> str:
    path = out / f"{y}" / f"{dataset}_{y}{m:02d}.nc"
    if path.exists():
        return f"{path.name} already there"
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(".part")
    client.retrieve(DATASETS[dataset], request(dataset, y, m, area), str(part))
    if dataset == "cerra-land":
        cut = path.with_suffix(".cut")
        cut_to_area(part, cut, area)
        part.unlink()
        part = cut
    part.rename(path)
    return f"{path.name} {path.stat().st_size / 1e6:.1f} MB"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    ap.add_argument("--start", required=True, help="first month, YYYY-MM")
    ap.add_argument("--end", required=True, help="last month, YYYY-MM")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--area", type=float, nargs=4, default=AREA, metavar=("N", "W", "S", "E"))
    ap.add_argument("--workers", type=int, default=4, help="requests queued on the CDS at the same time")
    a = ap.parse_args()

    import cdsapi

    client = cdsapi.Client(url=CDS_URL, key=cds_key(), quiet=True, progress=False)
    a.out.mkdir(parents=True, exist_ok=True)
    failed = []

    def one(ym):
        try:
            print(fetch_month(client, a.dataset, *ym, a.out, a.area), flush=True)
        except Exception as exc:  # noqa: BLE001 - log every failure and go on with the other months
            failed.append(f"{ym[0]}-{ym[1]:02d} {exc}".replace("\n", " "))
            print(f"FAILED {ym[0]}-{ym[1]:02d}: {exc}", flush=True)

    with ThreadPoolExecutor(a.workers) as pool:
        list(pool.map(one, months(a.start, a.end)))
    if failed:
        (a.out / "failed.txt").write_text("\n".join(sorted(failed)) + "\n", encoding="utf-8")
        raise SystemExit(f"{len(failed)} months failed, see {a.out / 'failed.txt'}")


if __name__ == "__main__":
    main()
