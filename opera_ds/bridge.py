"""Pan-European bridge data (S7, #13) read over a time window and set on the OPERA grid as coarse cells.

The files are the monthly netCDF of `scripts/fetch_cds.py` (docs/data.md, *Derived datasets*):

- **ERA5-Land** `tp` (m) is accumulated from 00 UTC: the value at 00 UTC is the total of the previous day, and
  hourly amounts are differences of consecutive hours (docs/data.md, *Inventory*).
- **CERRA-Land** `tp` (kg m-2, i.e. mm) is one analysis a day at 06 UTC: the value labelled D 06 UTC is the
  total from 06 UTC of D−1 to 06 UTC of D (CERRA-Land data user guide, in docs/data.md).

A window (start, end] therefore sums ERA5-Land hours ending after `start` up to `end`, and CERRA-Land days
labelled after `start` up to `end`; for CERRA-Land both must be at 06 UTC.

The bridge cells are coarser than OPERA pixels (about 9 km and 5.5 km against 1–2 km), so each OPERA pixel
takes the cell whose centre is nearest to its own (`cell_index`), and OPERA is averaged over the pixels of each
cell (`cell_mean`) before any comparison: the bridge is never interpolated to pixels.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np


def _open(paths):
    import xarray as xr

    return xr.open_mfdataset([str(p) for p in paths], combine="by_coords", engine="h5netcdf")


def era5land_sum(paths, start: dt.datetime, end: dt.datetime):
    """ERA5-Land total precipitation (mm) over the hours ending in (start, end], with (lat, lon) 1D in degrees.
    `paths` must hold the hour before the first one summed."""
    with _open(paths) as ds:
        tp = ds["tp"].sel(valid_time=slice(np.datetime64(start), np.datetime64(end))).load()
        lat, lon = ds["latitude"].values, ds["longitude"].values
    t = tp["valid_time"].values.astype("datetime64[h]")
    v = tp.values.astype(np.float64)
    hour = (t - t.astype("datetime64[D]")).astype(int)
    # amount of the hour ending at t: the value itself at 01 UTC, otherwise the difference with the hour before
    amount = np.where((hour == 1)[:, None, None], v, v - np.concatenate([[np.full(v.shape[1:], np.nan)], v[:-1]]))
    if hour[0] != 1:                       # the first hour has no predecessor in the slice: drop it
        amount, t = amount[1:], t[1:]
    keep = t > np.datetime64(start, "h")
    expected = int((end - start).total_seconds() // 3600)
    if keep.sum() != expected:
        raise ValueError(f"ERA5-Land: {keep.sum()} hours in ({start}, {end}], expected {expected}")
    return 1000.0 * amount[keep].sum(0), lat, lon


def cerraland_sum(paths, start: dt.datetime, end: dt.datetime):
    """CERRA-Land total precipitation (mm) over the days labelled in (start, end], with (lat, lon) 2D in
    degrees (longitude in −180…180). `start` and `end` must be at 06 UTC."""
    if start.time() != dt.time(6) or end.time() != dt.time(6):
        raise ValueError("CERRA-Land days run from 06 UTC to 06 UTC: start and end must be at 06 UTC")
    with _open(paths) as ds:
        tp = ds["tp"].sel(valid_time=slice(np.datetime64(start + dt.timedelta(days=1)), np.datetime64(end))).load()
        lat, lon = ds["latitude"].values, (ds["longitude"].values + 180.0) % 360.0 - 180.0
    expected = (end - start).days
    if tp.sizes["valid_time"] != expected:
        raise ValueError(f"CERRA-Land: {tp.sizes['valid_time']} days in ({start}, {end}], expected {expected}")
    return tp.values.astype(np.float64).sum(0), lat, lon


def monthly_files(folder: Path, dataset: str, months) -> list[Path]:
    """Monthly files of `fetch_cds.py` for the (year, month) pairs in `months`."""
    return [Path(folder) / f"{y}" / f"{dataset}_{y}{m:02d}.nc" for y, m in months]


def _xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def cell_index(cell_lat, cell_lon, lat, lon) -> np.ndarray:
    """For each point (lat, lon), the flat index of the bridge cell with the nearest centre. `cell_lat` and
    `cell_lon` are 1D axes of a regular grid or 2D arrays; the result has the shape of `lat`."""
    from scipy.spatial import cKDTree

    if np.ndim(cell_lat) == 1:
        cell_lat, cell_lon = np.meshgrid(cell_lat, cell_lon, indexing="ij")
    tree = cKDTree(_xyz(np.ravel(cell_lat), np.ravel(cell_lon)))
    _, idx = tree.query(_xyz(np.ravel(lat), np.ravel(lon)))
    return idx.reshape(np.shape(lat))


def cell_mean(values: np.ndarray, idx: np.ndarray, n_cells: int, min_valid: float = 1.0):
    """Mean of `values` (NaN = not covered) over the pixels of each cell, and the share of its pixels that are
    valid. Cells with no pixel, or with a valid share below `min_valid`, are NaN."""
    ok = np.isfinite(values)
    n = np.bincount(idx[ok], minlength=n_cells).astype(float)
    tot = np.bincount(idx.ravel(), minlength=n_cells).astype(float)
    s = np.bincount(idx[ok], weights=values[ok], minlength=n_cells)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean, share = s / n, n / tot
    mean[~(share >= min_valid)] = np.nan
    return mean, share


def pixel_lonlat(where: dict):
    """Longitude and latitude of the pixel centres of an ODIM composite (`Frame.where`)."""
    from pyproj import Proj

    p = Proj(where["projdef"])
    x0, y0 = p(float(where["UL_lon"]), float(where["UL_lat"]))
    sx, sy = float(where["xscale"]), float(where["yscale"])
    x = x0 + (np.arange(int(where["xsize"])) + 0.5) * sx
    y = y0 - (np.arange(int(where["ysize"])) + 0.5) * sy
    X, Y = np.meshgrid(x, y)
    return p(X, Y, inverse=True)
