"""Unit test of the CIRRUS degradation used in H1 (`degrade_frame`, `coarsen_where`)."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from opera_ds.odim_io import Frame, check_grid_alignment, coarsen_where, refine_where
from opera_ds.validate import degrade_frame

WHERE_FINE = {
    "projdef": "+proj=laea +lat_0=55.0 +lon_0=10.0 +x_0=1950000.0 +y_0=-2100000.0 +units=m +ellps=WGS84",
    "xsize": 6, "ysize": 4, "xscale": 1000.0, "yscale": 1000.0,
    "UL_lon": 1.0, "UL_lat": 52.0, "LR_lon": 1.1, "LR_lat": 51.96,
    "crop_row0": 2106, "crop_col0": 1056, "full_xsize": 3800, "full_ysize": 4400,
}


def _frame(values, coverage=None, undetect=None):
    values = np.asarray(values, np.float32)
    coverage = np.ones(values.shape, bool) if coverage is None else np.asarray(coverage)
    undetect = np.zeros(values.shape, bool) if undetect is None else np.asarray(undetect)
    return Frame(time=dt.datetime(2025, 7, 1, 12, 0), values=values, coverage=coverage,
                 undetect=undetect, where=dict(WHERE_FINE))


def test_mean_in_linear_z():
    v = np.full((4, 6), 20.0)
    v[0:2, 0:2] = [[10.0, 20.0], [30.0, 40.0]]
    out = degrade_frame(_frame(v))
    assert out.values.shape == (2, 3)
    expected = 10 * np.log10(np.mean(10 ** (np.array([10.0, 20.0, 30.0, 40.0]) / 10)))
    assert out.values[0, 0] == pytest.approx(expected, abs=1e-4)
    assert np.allclose(out.values[1:, :], 20.0) and np.allclose(out.values[0, 1:], 20.0)
    assert out.coverage.all() and not out.undetect.any()


def test_undetect_counts_as_zero_and_coverage_needs_whole_block():
    v = np.full((4, 6), 30.0)
    u = np.zeros((4, 6), bool)
    c = np.ones((4, 6), bool)
    u[0:2, 0:2] = [[True, True], [True, False]]     # one echo in the block
    u[0:2, 2:4] = True                              # whole block undetect
    c[2, 4] = False                                 # one pixel without coverage
    out = degrade_frame(_frame(v, coverage=c, undetect=u))
    assert out.values[0, 0] == pytest.approx(30.0 + 10 * np.log10(0.25), abs=1e-4)
    assert out.undetect[0, 1] and out.coverage[0, 1]
    assert not out.coverage[1, 2]
    assert out.coverage.sum() == 5


def test_where_is_coarse_and_aligned():
    out = degrade_frame(_frame(np.zeros((4, 6))))
    w = out.where
    assert (w["xsize"], w["ysize"], w["xscale"], w["yscale"]) == (3, 2, 2000.0, 2000.0)
    assert (w["crop_row0"], w["crop_col0"], w["full_xsize"], w["full_ysize"]) == (1053, 528, 1900, 2200)
    assert check_grid_alignment(w, WHERE_FINE, 2) == []
    assert refine_where(coarsen_where(WHERE_FINE, 2), 2) == WHERE_FINE


def test_max_and_sample():
    v = np.full((4, 6), 20.0)
    v[0:2, 0:2] = [[10.0, 20.0], [30.0, 40.0]]
    u = np.zeros((4, 6), bool)
    u[0, 0] = True                                  # sampled pixel of block (0, 0) is undetect
    mx = degrade_frame(_frame(v, undetect=u), how="max")
    assert mx.values[0, 0] == pytest.approx(40.0) and not mx.undetect[0, 0]
    assert np.allclose(mx.values[1:, :], 20.0)
    sp = degrade_frame(_frame(v, undetect=u), how="sample")
    assert sp.undetect[0, 0] and sp.values.shape == (2, 3)
    assert np.allclose(sp.values[1:, :], 20.0)
    assert sp.where == mx.where == coarsen_where(WHERE_FINE, 2)


def test_odd_shape_and_unknown_how_are_rejected():
    with pytest.raises(ValueError):
        degrade_frame(_frame(np.zeros((3, 6))))
    with pytest.raises(ValueError):
        degrade_frame(_frame(np.zeros((4, 6))), how="median")
