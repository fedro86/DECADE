"""Unit tests of the first-version cleaning (H2, #19): synthetic artefacts removed, synthetic rain kept."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from opera_ds.clean import (StaticCounts, StaticMask, clean_composite, dbz_from_rain, odyssey_period, rain_rate,
                            static_fill)


def rain_blob(shape=(60, 60), centre=(30, 30), peak=45.0, sigma=8.0):
    """A smooth rain cell in dBZ on a dry (0 dBZ) background."""
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    d2 = (y - centre[0]) ** 2 + (x - centre[1]) ** 2
    return np.maximum(peak - d2 / (2 * sigma ** 2) * 10.0, 0.0)


def test_impossible_values_removed_rain_kept():
    f = rain_blob()
    f[5, 5] = 95.0
    out = clean_composite(f, gabella=False)
    assert out[5, 5] == 0.0
    assert out[30, 30] == pytest.approx(45.0)
    assert np.array_equal(out[10:50, 10:50], f[10:50, 10:50])


def test_gabella_switch_removes_isolated_spike_only_when_on():
    f = rain_blob()
    f[5, 50] = 60.0                       # isolated strong echo on a dry background
    on, off = clean_composite(f, gabella=True), clean_composite(f, gabella=False)
    assert on[5, 50] == 0.0
    assert off[5, 50] == 60.0
    core = slice(25, 36)
    assert np.array_equal(on[core, core], f[core, core])    # the smooth cell keeps its core


def test_coverage_kept():
    f = rain_blob()
    f[:, :5] = np.nan
    out = clean_composite(f)
    assert np.isnan(out[:, :5]).all()
    assert np.isfinite(out[:, 5:]).all()


def test_static_counts_and_mask():
    counts = StaticCounts.zeros((3, 3))
    for i in range(1000):
        z = np.full((3, 3), 20.0)
        z[0, 0] = 58.0 if i % 20 == 0 else 20.0      # >= 55 dBZ in 5% of the times: fixed point
        z[1, 1] = 58.0 if i % 400 == 0 else 20.0     # 0.25%: rain-like
        z[2, 2] = 80.0 if i % 500 == 0 else 20.0     # > 70 dBZ in 0.2%
        z[2, 0] = np.nan if i % 2 else 20.0          # covered half of the time
        counts.add(z)
    m = counts.mask()
    assert m[0, 0] and m[2, 2]
    assert not m[1, 1] and not m[0, 1]
    assert counts.valid[2, 0] == 500
    total = counts + counts
    assert total.valid[0, 0] == 2000 and total.mask()[0, 0]


def test_fill_lowers_only():
    f = np.full((20, 20), 30.0)
    f[10, 10] = 52.0                      # masked pixel above its neighbours: lowered
    f[3, 3] = 10.0                        # masked pixel below its neighbours: kept
    mask = np.zeros(f.shape, bool)
    mask[10, 10] = mask[3, 3] = True
    out = static_fill(f, StaticMask(mask))
    assert out[10, 10] == pytest.approx(30.0, abs=1e-6)
    assert out[3, 3] == 10.0
    assert np.array_equal(np.delete(out.ravel(), [10 * 20 + 10, 3 * 20 + 3]), np.delete(f.ravel(), [10 * 20 + 10, 3 * 20 + 3]))


def test_mask_switched_with_how_nodes():
    f = np.full((40, 40), 30.0)
    f[5, 5] = f[35, 35] = 52.0
    mask = np.zeros(f.shape, bool)
    mask[5, 5] = mask[35, 35] = True
    static = StaticMask(mask, radars={"aaaaa": (5, 8)}, pixel_km=1.0)    # (35, 35) is 40 km from the radar
    assert list(static.owner) == ["aaaaa", ""]
    off = static_fill(f, static, listed={"bbbbb"})
    assert off[5, 5] == 52.0                          # radar not listed: its pixel untouched
    assert off[35, 35] == pytest.approx(30.0, abs=1e-6)   # no radar: always used
    on = static_fill(f, static, listed={"aaaaa"})
    assert on[5, 5] == pytest.approx(30.0, abs=1e-6)


def test_full_chain_on_a_cell_with_artefacts():
    f = rain_blob()
    f[2, 2] = 100.0                       # impossible value
    f[2, 57] = 57.0                       # fixed point on a dry background, also in the mask
    mask = np.zeros(f.shape, bool)
    mask[2, 57] = True
    out = clean_composite(f, StaticMask(mask), gabella=True)
    assert out[2, 2] == 0.0 and out[2, 57] == 0.0
    assert rain_rate(out)[25:36, 25:36].sum() == pytest.approx(rain_rate(f)[25:36, 25:36].sum())


def test_rain_rate_roundtrip_and_periods():
    z = np.array([0.0, 6.9, 7.0, 30.0, 54.0])
    r = rain_rate(z)
    assert r[0] == 0.0 and r[1] == 0.0
    assert dbz_from_rain(r)[2:] == pytest.approx(z[2:])
    assert rain_rate(np.array([65.0]))[0] == pytest.approx(rain_rate(np.array([55.0]))[0])
    assert odyssey_period(dt.datetime(2015, 11, 30, 23, 45)) == 0
    assert odyssey_period(dt.datetime(2015, 12, 1)) == 1
    assert odyssey_period(dt.datetime(2018, 7, 31, 23, 45)) == 1
    assert odyssey_period(dt.datetime(2018, 8, 1)) == 2
