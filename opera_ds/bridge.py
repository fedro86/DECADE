"""Pan-European bridge data (S7, #13) read over a time window and set on the OPERA grid as coarse cells.

The sources are the monthly netCDF of `scripts/fetch_cds.py` (docs/data.md, *Derived datasets*):

- **ERA5-Land** `tp` (m) is accumulated from 00 UTC: the value at 00 UTC is the total of the previous day, and
  hourly amounts are differences of consecutive hours (docs/data.md, *Inventory*). `era5land_to_zarr` turns
  the files into one Zarr store of hourly amounts in mm, with `expver` for every hour (1 final, 5 preliminary),
  and `era5land_sum` reads that store.
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


def era5land_amounts(tp_m: np.ndarray, valid_time: np.ndarray, prev_m=None, prev_time=None) -> np.ndarray:
    """Amount (mm) of each hour ending at `valid_time` from ERA5-Land `tp` (m, accumulated from 00 UTC): the value
    itself at 01 UTC, otherwise the difference with the hour before. `prev_m` and `prev_time` are the last hour
    before `valid_time[0]`; without them the first amount is NaN (unless it ends at 01 UTC)."""
    t = valid_time.astype("datetime64[h]")
    tt = t if prev_time is None else np.concatenate([[np.datetime64(prev_time, "h")], t])
    if np.any(np.diff(tt) != np.timedelta64(1, "h")):
        raise ValueError("ERA5-Land: hours are not consecutive")
    v = tp_m.astype(np.float64)
    before = np.concatenate([[np.full(v.shape[1:], np.nan) if prev_m is None else prev_m], v[:-1]])
    hour = (t - t.astype("datetime64[D]")).astype(int)
    return 1000.0 * np.where((hour == 1)[:, None, None], v, v - before)


def era5land_to_zarr(files, out: Path, chunk_hours: int = 744) -> dict:
    """Monthly ERA5-Land files (in time order, without gaps) to one Zarr store at `out`, written anew.

    `tp` is the amount (mm) of the hour ending at `valid_time`, float32, lossless (zstd with bitshuffle), one chunk
    of `chunk_hours` over the whole domain; the first hour is NaN. Small negative amounts left by the differences
    are set to 0 and counted. `expver` (int8) is 1 for final and 5 for preliminary (ERA5T-based) hours. Returns
    the store attributes."""
    import shutil

    import xarray as xr
    import zarr
    from zarr.codecs import BloscCodec

    out = Path(out)
    part = out.with_name(out.name + ".part")
    shutil.rmtree(part, ignore_errors=True)
    prev_m = prev_time = None
    negative, lowest, preliminary = 0, 0.0, 0
    for i, f in enumerate(files):
        with xr.open_dataset(f, engine="h5netcdf") as ds:
            tp, t = ds["tp"].values, ds["valid_time"].values
            expver = np.array([int(x) for x in np.atleast_1d(ds["expver"].values)], np.int8)
            expver = np.broadcast_to(expver, t.shape) if expver.size == 1 else expver
            lat, lon = ds["latitude"].values, ds["longitude"].values
        mm = era5land_amounts(tp, t, prev_m, prev_time)
        neg = mm < 0
        negative, lowest = negative + int(neg.sum()), min(lowest, float(np.nanmin(mm, initial=0.0)))
        preliminary += int(np.sum(expver != 1))
        mm[neg] = 0.0
        month = xr.Dataset(
            {"tp": (("valid_time", "latitude", "longitude"), mm.astype(np.float32),
                    {"units": "mm", "long_name": "total precipitation in the hour ending at valid_time"}),
             "expver": (("valid_time",), expver, {"long_name": "ERA5 experiment version: 1 final, 5 preliminary"})},
            coords={"valid_time": t, "latitude": lat, "longitude": lon})
        if i == 0:
            enc = {"tp": {"chunks": (chunk_hours, lat.size, lon.size),
                          "compressors": [BloscCodec(cname="zstd", clevel=5, shuffle="bitshuffle")]},
                   "expver": {"chunks": (chunk_hours,)},
                   "valid_time": {"units": "hours since 1970-01-01", "dtype": "int64"}}
            month.to_zarr(part, mode="w", zarr_format=3, consolidated=False, encoding=enc)
        else:
            month.to_zarr(part, append_dim="valid_time", zarr_format=3, consolidated=False)
        prev_m, prev_time = tp[-1], t[-1]
    attrs = {
        "title": "ERA5-Land hourly total precipitation over the Belgian working domain (DECADE, S9)",
        "source": "ERA5-Land hourly, total_precipitation, Copernicus Climate Data Store (reanalysis-era5-land)",
        "licence": "CC BY 4.0; contains modified Copernicus Climate Change Service information",
        "tp_convention": "amount of the hour ending at valid_time, from the accumulation from 00 UTC; the first hour "
                         "is NaN; negative differences set to 0",
        "negative_amounts_set_to_0": negative, "lowest_negative_amount_mm": lowest,
        "preliminary_hours": preliminary,
        "history": f"opera_ds.bridge.era5land_to_zarr, {dt.date.today().isoformat()}",
    }
    zarr.open_group(part, mode="r+").attrs.update(attrs)
    shutil.rmtree(out, ignore_errors=True)
    part.rename(out)
    return attrs


def era5land_sum(store, start: dt.datetime, end: dt.datetime, allow_preliminary: bool = False):
    """ERA5-Land total precipitation (mm) over the hours ending in (start, end], with (lat, lon) 1D in degrees,
    from the store of `era5land_to_zarr`. Preliminary hours raise unless `allow_preliminary`."""
    import xarray as xr

    with xr.open_zarr(store, consolidated=False) as ds:
        win = ds.sel(valid_time=slice(np.datetime64(start + dt.timedelta(hours=1)), np.datetime64(end)))
        tp, expver = win["tp"].values, win["expver"].values
        lat, lon = ds["latitude"].values, ds["longitude"].values
    expected = int((end - start).total_seconds() // 3600)
    if len(expver) != expected:
        raise ValueError(f"ERA5-Land: {len(expver)} hours in ({start}, {end}], expected {expected}")
    if not allow_preliminary and np.any(expver != 1):
        raise ValueError(f"ERA5-Land: ({start}, {end}] holds {int(np.sum(expver != 1))} preliminary hours")
    return tp.astype(np.float64).sum(0), lat, lon


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
