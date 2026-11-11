"""Unit tests of the VMM reader and of the monthly ratio step (H3, #20), on synthetic rasters in the layout of
the VMM raster service."""
import datetime as dt

import h5py
import numpy as np
import pytest

from opera_ds.bridge import pixel_lonlat
from opera_ds.homog import area_ratio, step
from opera_ds.vmm import monthly_cell_sums, read_vmm, steps_in_month

PROJ = "+proj=aeqd +lat_0=51.1926 +lon_0=3.48366 +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs"


def _write(path, label: dt.datetime, data: np.ndarray):
    from pyproj import Proj

    ny, nx = data.shape
    p = Proj(PROJ)
    ul = p(-nx * 250.0, ny * 250.0, inverse=True)
    with h5py.File(path, "w") as f:
        f.create_dataset("dataset1/data1/data", data=data.astype(np.float64))
        what = f.require_group("what")
        what.attrs["date"] = np.bytes_(label.strftime("%Y%m%d"))
        what.attrs["time"] = np.bytes_(label.strftime("%H%M%S"))
        where = f.require_group("where")
        where.attrs["projdef"] = np.bytes_(PROJ)
        where.attrs["xscale"], where.attrs["yscale"] = 500.0, 500.0
        where.attrs["xsize"], where.attrs["ysize"] = nx, ny
        where.attrs["UL_lon"], where.attrs["UL_lat"] = ul


def test_read_vmm_nodata_label_and_grid(tmp_path):
    data = np.full((4, 6), 1.5)
    data[0, 0] = -2.0
    path = tmp_path / "a.h5"
    _write(path, dt.datetime(2024, 7, 1, 12, 5), data)
    values, where, label = read_vmm(path)
    assert np.isnan(values[0, 0]) and np.isfinite(values[1:, 1:]).all()
    assert label == dt.datetime(2024, 7, 1, 12, 5)
    lon, lat = pixel_lonlat(where)
    # the grid is centred on the projection origin: the two central pixels straddle it
    assert lat[1, 2] > 51.1926 > lat[2, 2]
    assert lon[1, 2] < 3.48366 < lon[1, 3]


def test_monthly_cell_sums_intensity_and_month_boundary(tmp_path):
    idx = np.zeros((4, 6), dtype=int)
    idx[:, 3:] = 1
    paths = []
    # three 5 min steps of 12 mm/h at the end of June (the 00:00 label of 1 July closes a June step)
    for i, label in enumerate([dt.datetime(2024, 6, 30, 23, 55), dt.datetime(2024, 7, 1, 0, 0),
                               dt.datetime(2024, 7, 1, 0, 5)]):
        p = tmp_path / f"{i}.h5"
        _write(p, label, np.full((4, 6), 12.0))
        paths.append(p)
    out = monthly_cell_sums(paths, idx, 2, step_hours=5 / 60)
    assert out[(2024, 6)][1] == 2 and out[(2024, 7)][1] == 1
    np.testing.assert_allclose(out[(2024, 6)][0], [2.0, 2.0])
    np.testing.assert_allclose(out[(2024, 7)][0], [1.0, 1.0])


def test_monthly_cell_sums_partial_cell_is_nan(tmp_path):
    idx = np.zeros((4, 6), dtype=int)
    idx[:, 3:] = 1
    data = np.full((4, 6), 3.0)
    data[0, 5] = -2.0                       # cell 1 not fully covered
    p = tmp_path / "a.h5"
    _write(p, dt.datetime(2024, 7, 2), data)
    sums, n = monthly_cell_sums([p], idx, 2, step_hours=None)[(2024, 7)]
    assert n == 1 and sums[0] == 3.0 and np.isnan(sums[1])


def test_steps_in_month():
    assert steps_in_month(2024, 2, 5) == 29 * 288
    assert steps_in_month(2024, 12, 60) == 31 * 24


def test_area_ratio_uses_cells_finite_in_both():
    product = np.array([2.0, np.nan, 4.0, 100.0])
    bridge = np.array([1.0, 1.0, 2.0, np.nan])
    assert area_ratio(product, bridge, np.array([0, 1, 2, 3])) == pytest.approx(2.0)
    assert np.isnan(area_ratio(product, np.zeros(4), np.array([0, 2])))


def test_step_finds_a_known_step_and_respects_exclusions():
    rng = np.random.default_rng(0)
    series = {}
    for k in range(24):
        y, m = 2023 + k // 12, k % 12 + 1
        level = 1.0 if (y, m) < (2024, 1) else 1.5
        series[(y, m)] = level * 10 ** rng.normal(0, 0.01)
    series[(2023, 6)] = 100.0               # an outlier month, excluded below
    out = step(series, (2024, 1), 12, exclude={(2023, 6)})
    assert out["n_before"] == 11 and out["n_after"] == 12
    assert out["step"] == pytest.approx(np.log10(1.5), abs=0.02)
    assert out["sd_before"] < 0.03
