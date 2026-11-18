"""Unit tests of the level correction (H3, #20): known synthetic offsets, one per period, are removed."""
from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from opera_ds.clean import rain_rate
from opera_ds.correct import V1, LevelOffsets, correct_composite, correction_attrs, period_index, shift_dbz

KNOWN = LevelOffsets(name="test", target="synthetic", log10_k=(0.15, -0.05, 0.02), source="test")
TIMES = (dt.datetime(2014, 6, 1, 12), dt.datetime(2017, 1, 15), dt.datetime(2021, 9, 30, 23, 45))


def rain_field(shape=(40, 40), peak=45.0, sigma=6.0):
    """A smooth rain cell in dBZ on a dry (0 dBZ) background, with an edge of no coverage."""
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    d2 = (y - shape[0] / 2) ** 2 + (x - shape[1] / 2) ** 2
    f = np.maximum(peak - d2 / (2 * sigma ** 2) * 10.0, 0.0).astype(np.float32)
    f[:, :3] = np.nan
    return f


def test_period_boundaries():
    assert period_index(dt.datetime(2013, 4, 1)) == 0
    assert period_index(dt.datetime(2015, 11, 30, 23, 45)) == 0
    assert period_index(dt.datetime(2015, 12, 1)) == 1
    assert period_index(dt.datetime(2018, 7, 31, 23, 45)) == 1
    assert period_index(dt.datetime(2018, 8, 1)) == 2
    assert period_index(dt.datetime(2024, 7, 5, 6)) == 2       # last ODYSSEY file, overlap days
    with pytest.raises(ValueError):
        period_index(dt.datetime(2013, 3, 31, 23, 45))


def test_v1_shifts():
    assert V1.shift_db(0) == pytest.approx(16 * 0.127)          # A about +2 dB
    assert V1.shift_db(1) == pytest.approx(16 * 0.023)
    assert V1.shift_db(2) == pytest.approx(16 * 0.006)


@pytest.mark.parametrize("p", [0, 1, 2])
def test_known_offset_removed(p):
    """A field made weaker by a known offset of its period comes back to the truth once corrected."""
    t = TIMES[p]
    truth = rain_field()
    weak = shift_dbz(truth, -KNOWN.shift_db(p))
    back = correct_composite(weak, t, KNOWN)
    # echoes that the weakening kept above 0 dBZ come back exactly
    kept = np.isfinite(truth) & (truth + min(0.0, -KNOWN.shift_db(p)) > 0)
    np.testing.assert_allclose(back[kept], truth[kept], atol=1e-4)
    assert np.isnan(back[:, :3]).all()


@pytest.mark.parametrize("p", [0, 1, 2])
def test_rain_rate_scales_by_k(p):
    """Between the rain threshold and the cap, every rain rate is multiplied by k."""
    f = rain_field()
    out = correct_composite(f, TIMES[p], KNOWN)
    s = KNOWN.shift_db(p)
    inside = np.isfinite(f) & (f >= 7.0 - min(s, 0)) & (f + max(s, 0) <= 55.0) & (f + s >= 7.0)
    ratio = rain_rate(out[inside]) / rain_rate(f[inside])
    np.testing.assert_allclose(ratio, 10 ** KNOWN.log10_k[p], rtol=1e-4)


def test_no_echo_and_coverage_kept():
    f = rain_field()
    out = correct_composite(f, TIMES[0], V1)
    dry = f == 0
    assert (out[dry] == 0).all()
    assert np.isnan(out[np.isnan(f)]).all()
    assert out.dtype == f.dtype


def test_negative_shift_stops_at_floor():
    f = np.array([[0.0, 0.5, 3.0, np.nan, 30.0]], np.float32)
    out = shift_dbz(f, -2.0)
    np.testing.assert_array_equal(out[0, [0, 1, 2, 4]], [0.0, 0.0, 1.0, 28.0])
    assert np.isnan(out[0, 3])


def test_attrs():
    a = correction_attrs(dt.datetime(2014, 1, 1), V1)
    assert a["level_period"] == "A"
    assert a["level_shift_db"] == pytest.approx(2.032)
    assert a["level_correction"] == "h3-intensity-v1"
    assert correction_attrs(dt.datetime(2019, 1, 1))["level_period"] == "C"
