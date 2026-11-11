"""Download pan-European bridge data from the Copernicus Climate Data Store (S7, #13), one file per month.

- `era5-land`: ERA5-Land hourly total precipitation, cut on the server to `--area`. The CDS field is
  accumulated from 00 UTC: the value at 00 UTC is the total of the previous day, and hourly amounts are
  differences of consecutive hours (docs/data.md).
- `cerra-land`: CERRA-Land daily total precipitation (analysis, 06 UTC). The CDS serves only the whole
  European grid (1069 x 1069, 5.5 km), so the data are downloaded whole, cut to the smallest window of grid
  cells that covers `--area`, and the whole file is deleted. CERRA-Land is read from the ECMWF MARS archive,
  which runs one request per user and has a long shared queue, so one request covers all the missing months
  of a year (about 1.9 GB downloaded per year).

Files are netCDF, one per month, `<out>/<YYYY>/<dataset>_<YYYYMM>.nc`. Months already on disk are skipped, so
an interrupted run resumes; failures are listed in `<out>/failed.txt`. The token is read from `COPERNICUS_CDS_API_KEY`, in the
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


def request(dataset: str, y: int, ms: list[int], area) -> dict:
    ndays = max(calendar.monthrange(y, m)[1] for m in ms)
    req = {"variable": ["total_precipitation"], "year": f"{y}", "month": [f"{m:02d}" for m in ms],
           "day": [f"{d:02d}" for d in range(1, ndays + 1)], "data_format": "netcdf"}
    if dataset == "era5-land":
        req |= {"time": [f"{h:02d}:00" for h in range(24)], "area": list(area), "download_format": "unarchived"}
    else:
        req |= {"time": ["06:00"], "level_type": "surface", "product_type": "analysis"}
    return req


def cut_to_area(src: Path, area):
    """The smallest window of grid cells of a CERRA-Land file whose cells cover `area`, loaded in memory."""
    import xarray as xr

    n, w, s, e = area
    with xr.open_dataset(src) as ds:
        lat = ds["latitude"].values
        lon = (ds["longitude"].values + 180.0) % 360.0 - 180.0
        inside = (lat >= s) & (lat <= n) & (lon >= w) & (lon <= e)
        rows, cols = np.flatnonzero(inside.any(1)), np.flatnonzero(inside.any(0))
        win = ds.isel(y=slice(max(rows[0] - 1, 0), rows[-1] + 2), x=slice(max(cols[0] - 1, 0), cols[-1] + 2))
        return win.assign_coords(longitude=(win["longitude"] + 180.0) % 360.0 - 180.0).load()


def month_path(out: Path, dataset: str, y: int, m: int) -> Path:
    return out / f"{y}" / f"{dataset}_{y}{m:02d}.nc"


def requests_to_make(dataset: str, start: str, end: str, out: Path):
    """(year, months) of each request: one month for ERA5-Land, all the missing months of a year for CERRA-Land."""
    todo = [(y, m) for y, m in months(start, end) if not month_path(out, dataset, y, m).exists()]
    if dataset == "era5-land":
        return [(y, [m]) for y, m in todo]
    years = sorted({y for y, _ in todo})
    return [(y, [m for yy, m in todo if yy == y]) for y in years]


def fetch(client, dataset: str, y: int, ms: list[int], out: Path, area) -> str:
    (out / f"{y}").mkdir(parents=True, exist_ok=True)
    part = out / f"{y}" / f"{dataset}_{y}{ms[0]:02d}-{ms[-1]:02d}.part"
    client.retrieve(DATASETS[dataset], request(dataset, y, ms, area), str(part))
    if dataset == "era5-land":
        path = month_path(out, dataset, y, ms[0])
        part.rename(path)
        return f"{path.name} {path.stat().st_size / 1e6:.1f} MB"
    win = cut_to_area(part, area)
    done = []
    for m in ms:
        path = month_path(out, dataset, y, m)
        cut = path.with_suffix(".cut")
        one = win.sel(valid_time=win["valid_time"].dt.month == m)
        one.to_netcdf(cut, engine="h5netcdf", encoding={v: {"zlib": True, "complevel": 4} for v in one.data_vars})
        cut.rename(path)
        done.append(f"{path.name} {path.stat().st_size / 1e6:.1f} MB")
    part.unlink()
    return "\n".join(done)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    ap.add_argument("--start", required=True, help="first month, YYYY-MM")
    ap.add_argument("--end", required=True, help="last month, YYYY-MM")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--area", type=float, nargs=4, default=AREA, metavar=("N", "W", "S", "E"))
    # ECMWF asks for sequential requests and may suspend accounts that send them in parallel
    # (https://forum.ecmwf.int/t/data-stores-service-protection-measures-affecting-data-downloads-and-account-access-cds-ads-ewds-ecds/15481)
    ap.add_argument("--workers", type=int, default=1, help="requests queued on the CDS at the same time")
    a = ap.parse_args()

    import cdsapi

    client = cdsapi.Client(url=CDS_URL, key=cds_key(), quiet=True, progress=False)
    a.out.mkdir(parents=True, exist_ok=True)
    failed = []

    def one(yms):
        y, ms = yms
        label = f"{y}-{ms[0]:02d}" + (f"..{ms[-1]:02d}" if len(ms) > 1 else "")
        try:
            print(fetch(client, a.dataset, y, ms, a.out, a.area), flush=True)
        except Exception as exc:  # noqa: BLE001 - log every failure and go on with the other requests
            failed.append(f"{label} {exc}".replace("\n", " "))
            print(f"FAILED {label}: {exc}", flush=True)

    with ThreadPoolExecutor(a.workers) as pool:
        list(pool.map(one, requests_to_make(a.dataset, a.start, a.end, a.out)))
    if failed:
        (a.out / "failed.txt").write_text("\n".join(sorted(failed)) + "\n", encoding="utf-8")
        raise SystemExit(f"{len(failed)} months failed, see {a.out / 'failed.txt'}")


if __name__ == "__main__":
    main()
