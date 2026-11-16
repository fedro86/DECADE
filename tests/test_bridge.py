"""Unit tests of the bridge readers (S7, #13; S9, #83; S10, #93): the ERA5-Land and CERRA-Land Zarr stores and
their window sums on synthetic files, and OPERA pixels assigned to coarse cells."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest
import xarray as xr

from opera_ds.bridge import cell_index, cell_mean, cerraland_sum, cerraland_to_zarr, era5land_sum, era5land_to_zarr


def era5land_file(path, start, hours, rate_mm=1.0, expver="0001"):
    """ERA5-Land-like `tp` (m) at a constant rate, accumulated from 00 UTC (00 UTC holds the previous day)."""
    t = np.array([np.datetime64(start) + np.timedelta64(h, "h") for h in range(hours)])
    hour = (t - t.astype("datetime64[D]")).astype("timedelta64[h]").astype(int)
    acc = np.where(hour == 0, 24, hour) * rate_mm / 1000.0
    tp = np.broadcast_to(acc[:, None, None], (hours, 2, 3)).astype(np.float32).copy()
    tp[:, 0, 0] = np.nan                                                 # a sea cell
    ds = xr.Dataset({"tp": (("valid_time", "latitude", "longitude"), tp)},
                    coords={"valid_time": t, "latitude": [51.0, 50.9], "longitude": [4.0, 4.1, 4.2],
                            "expver": ("valid_time", np.full(hours, expver))})
    ds.to_netcdf(path, engine="h5netcdf")
    return path


def era5land_store(tmp_path, second_expver="0001"):
    """Two files, 29/6 00 UTC to 30/6 23 UTC and 1/7 00 UTC to 2/7 23 UTC, as one store."""
    files = [era5land_file(tmp_path / "a.nc", "2013-06-29T00:00", 48),
             era5land_file(tmp_path / "b.nc", "2013-07-01T00:00", 48, expver=second_expver)]
    attrs = era5land_to_zarr(files, tmp_path / "e.zarr", chunk_hours=24)
    return tmp_path / "e.zarr", attrs


def test_era5land_store_window_sum_across_files(tmp_path):
    store, attrs = era5land_store(tmp_path)
    s, lat, lon = era5land_sum(store, dt.datetime(2013, 6, 30, 6), dt.datetime(2013, 7, 2, 6))
    assert s.shape == (2, 3) and lat.shape == (2,) and lon.shape == (3,)
    assert np.isnan(s[0, 0]) and np.allclose(s.ravel()[1:], 48.0)       # two midnights, one at the file change
    assert attrs["negative_amounts_set_to_0"] == 0 and attrs["preliminary_hours"] == 0
    with xr.open_zarr(store, consolidated=False) as ds:
        assert ds.sizes["valid_time"] == 96 and np.isnan(ds["tp"].values[0, 0, 1])   # first hour has no predecessor
        assert np.allclose(ds["tp"].values[1:, 1, 1], 1.0)


def test_era5land_store_missing_hours_raise(tmp_path):
    store, _ = era5land_store(tmp_path)
    with pytest.raises(ValueError, match="hours"):
        era5land_sum(store, dt.datetime(2013, 7, 1, 6), dt.datetime(2013, 7, 3, 6))


def test_era5land_store_preliminary_hours(tmp_path):
    store, attrs = era5land_store(tmp_path, second_expver="0005")
    assert attrs["preliminary_hours"] == 48
    with pytest.raises(ValueError, match="preliminary"):
        era5land_sum(store, dt.datetime(2013, 6, 30, 6), dt.datetime(2013, 7, 1, 6))
    s, _, _ = era5land_sum(store, dt.datetime(2013, 6, 30, 6), dt.datetime(2013, 7, 1, 6), allow_preliminary=True)
    assert np.allclose(s.ravel()[1:], 24.0)
    s, _, _ = era5land_sum(store, dt.datetime(2013, 6, 29, 6), dt.datetime(2013, 6, 30, 6))   # final hours only
    assert np.allclose(s.ravel()[1:], 24.0)


def test_era5land_store_negative_differences_and_gaps(tmp_path):
    a = era5land_file(tmp_path / "a.nc", "2013-06-29T00:00", 48)
    with xr.open_dataset(a, engine="h5netcdf") as ds:
        ds = ds.load()
    ds["tp"][10, 1, 1] = ds["tp"][9, 1, 1] - 1e-8                        # accumulation drops slightly
    ds.to_netcdf(tmp_path / "a2.nc", engine="h5netcdf")
    attrs = era5land_to_zarr([tmp_path / "a2.nc"], tmp_path / "n.zarr")
    assert attrs["negative_amounts_set_to_0"] == 1 and attrs["lowest_negative_amount_mm"] < 0
    with xr.open_zarr(tmp_path / "n.zarr", consolidated=False) as z:
        assert np.nanmin(z["tp"].values) == 0.0
    b = era5land_file(tmp_path / "b.nc", "2013-07-01T03:00", 24)          # three hours missing
    with pytest.raises(ValueError, match="consecutive"):
        era5land_to_zarr([a, b], tmp_path / "g.zarr")


def cerraland_file(path, start, days, lat=None, expver="prod"):
    """CERRA-Land-like daily `tp` (mm) labelled at 06 UTC, value d + 1 on day d, on a 2 × 2 grid in 0–360 longitude."""
    t = np.array([np.datetime64(start) + np.timedelta64(d, "D") for d in range(days)])
    tp = np.broadcast_to(np.arange(1.0, days + 1.0)[:, None, None], (days, 2, 2)).astype(np.float32)
    lat = np.array([[50.0, 50.0], [51.0, 51.0]]) if lat is None else lat
    lon = np.array([[364.0, 365.0], [364.0, 365.0]])
    ds = xr.Dataset({"tp": (("valid_time", "y", "x"), tp)},
                    coords={"valid_time": t, "latitude": (("y", "x"), lat), "longitude": (("y", "x"), lon),
                            "expver": ("valid_time", np.full(days, expver))})
    ds.to_netcdf(path, engine="h5netcdf")
    return path


def test_cerraland_store_days_labelled_at_the_end(tmp_path):
    files = [cerraland_file(tmp_path / "a.nc", "2013-06-29T06:00", 2),      # 29/6, 30/6: values 1, 2
             cerraland_file(tmp_path / "b.nc", "2013-07-01T06:00", 5)]      # 1/7 … 5/7: values 1 … 5
    attrs = cerraland_to_zarr(files, tmp_path / "c.zarr", chunk_days=3)
    assert attrs["licence"].startswith("CC BY 4.0")
    store = tmp_path / "c.zarr"
    s, la, lo = cerraland_sum(store, dt.datetime(2013, 7, 2, 6), dt.datetime(2013, 7, 4, 6))
    assert np.allclose(s, 3.0 + 4.0)                 # days labelled 3/7 and 4/7, not 2/7
    assert np.allclose(lo, [[4.0, 5.0], [4.0, 5.0]]) and la.shape == (2, 2)
    s, _, _ = cerraland_sum(store, dt.datetime(2013, 6, 29, 6), dt.datetime(2013, 7, 1, 6))   # across the files
    assert np.allclose(s, 2.0 + 1.0)
    with xr.open_zarr(store, consolidated=False) as ds:
        assert ds.sizes["valid_time"] == 7 and ds["tp"].dtype == np.float32
    with pytest.raises(ValueError, match="06 UTC"):
        cerraland_sum(store, dt.datetime(2013, 7, 2), dt.datetime(2013, 7, 4))
    with pytest.raises(ValueError, match="days"):
        cerraland_sum(store, dt.datetime(2013, 7, 4, 6), dt.datetime(2013, 7, 7, 6))


def test_cerraland_store_refuses_gaps_other_grids_and_versions(tmp_path):
    a = cerraland_file(tmp_path / "a.nc", "2013-06-29T06:00", 2)
    gap = cerraland_file(tmp_path / "gap.nc", "2013-07-02T06:00", 2)
    with pytest.raises(ValueError, match="consecutive"):
        cerraland_to_zarr([a, gap], tmp_path / "g.zarr")
    moved = cerraland_file(tmp_path / "m.nc", "2013-07-01T06:00", 2, lat=np.array([[50.1, 50.1], [51.0, 51.0]]))
    with pytest.raises(ValueError, match="grid"):
        cerraland_to_zarr([a, moved], tmp_path / "m.zarr")
    other = cerraland_file(tmp_path / "o.nc", "2013-07-01T06:00", 2, expver="0005")
    with pytest.raises(ValueError, match="expver"):
        cerraland_to_zarr([a, other], tmp_path / "o.zarr")
    noon = cerraland_file(tmp_path / "n.nc", "2013-07-01T12:00", 2)
    with pytest.raises(ValueError, match="06 UTC"):
        cerraland_to_zarr([noon], tmp_path / "n.zarr")
    assert not (tmp_path / "g.zarr").exists()


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
