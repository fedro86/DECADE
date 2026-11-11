"""Unit tests of the bridge readers (S7, #13): window sums of synthetic ERA5-Land and CERRA-Land files, and
OPERA pixels assigned to coarse cells."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest
import xarray as xr

from opera_ds.bridge import cell_index, cell_mean, cerraland_sum, era5land_sum


def era5land_file(path, start, hours, rate_mm=1.0):
    """ERA5-Land-like `tp` (m) at a constant rate, accumulated from 00 UTC (00 UTC holds the previous day)."""
    t = np.array([np.datetime64(start) + np.timedelta64(h, "h") for h in range(hours)])
    hour = (t - t.astype("datetime64[D]")).astype("timedelta64[h]").astype(int)
    acc = np.where(hour == 0, 24, hour) * rate_mm / 1000.0
    tp = np.broadcast_to(acc[:, None, None], (hours, 2, 3)).astype(np.float32)
    ds = xr.Dataset({"tp": (("valid_time", "latitude", "longitude"), tp)},
                    coords={"valid_time": t, "latitude": [51.0, 50.9], "longitude": [4.0, 4.1, 4.2]})
    ds.to_netcdf(path, engine="h5netcdf")
    return path


def test_era5land_window_sum_across_midnight(tmp_path):
    p = era5land_file(tmp_path / "e.nc", "2013-07-01T00:00", 72)
    s, lat, lon = era5land_sum([p], dt.datetime(2013, 7, 1, 6), dt.datetime(2013, 7, 3, 6))
    assert s.shape == (2, 3) and lat.shape == (2,) and lon.shape == (3,)
    assert np.allclose(s, 48.0)                      # 48 hours at 1 mm/h, two midnights included


def test_era5land_missing_hours_raise(tmp_path):
    p = era5land_file(tmp_path / "e.nc", "2013-07-01T00:00", 30)
    with pytest.raises(ValueError):
        era5land_sum([p], dt.datetime(2013, 7, 1, 6), dt.datetime(2013, 7, 3, 6))


def test_cerraland_days_labelled_at_the_end(tmp_path):
    t = np.array([np.datetime64("2013-07-01T06:00") + np.timedelta64(d, "D") for d in range(5)])
    tp = np.broadcast_to(np.arange(1.0, 6.0)[:, None, None], (5, 2, 2)).astype(np.float32)
    lat = np.array([[50.0, 50.0], [51.0, 51.0]])
    lon = np.array([[364.0, 365.0], [364.0, 365.0]])                     # 0–360 as in the CDS files
    ds = xr.Dataset({"tp": (("valid_time", "y", "x"), tp)},
                    coords={"valid_time": t, "latitude": (("y", "x"), lat), "longitude": (("y", "x"), lon)})
    p = tmp_path / "c.nc"
    ds.to_netcdf(p, engine="h5netcdf")
    s, la, lo = cerraland_sum([p], dt.datetime(2013, 7, 2, 6), dt.datetime(2013, 7, 4, 6))
    assert np.allclose(s, 3.0 + 4.0)                 # days labelled 3/7 and 4/7, not 2/7
    assert np.allclose(lo, [[4.0, 5.0], [4.0, 5.0]])
    with pytest.raises(ValueError):
        cerraland_sum([p], dt.datetime(2013, 7, 2), dt.datetime(2013, 7, 4))


def test_cell_index_and_mean_on_a_regular_grid():
    cell_lat, cell_lon = np.array([51.0, 50.9]), np.array([4.0, 4.1])
    lat = np.array([[51.02, 51.03], [50.88, 50.91]])
    lon = np.array([[3.98, 4.12], [4.03, 4.09]])
    idx = cell_index(cell_lat, cell_lon, lat, lon)
    assert idx.tolist() == [[0, 1], [2, 3]]
    values = np.array([1.0, 3.0, np.nan, 5.0, 7.0])
    mean, share = cell_mean(values, np.array([0, 0, 1, 1, 2]), 4, min_valid=0.5)
    assert mean[0] == 2.0 and mean[1] == 5.0 and mean[2] == 7.0 and np.isnan(mean[3])
    assert share.tolist()[:3] == [1.0, 0.5, 1.0]
