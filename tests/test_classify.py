"""Unit tests of the Steiner et al. (1995) convective / stratiform classification."""
from __future__ import annotations

import numpy as np
import pytest

from opera_ds.classify import (CENTRES_ONLY, background_dbz, classes_on_coarse_grid, obs_classes,
                               peakedness_threshold, steiner_convective)


def test_peakedness_curve():
    d = peakedness_threshold(np.array([-5.0, 0.0, 30.0, 42.43, 50.0]))
    assert d == pytest.approx([10.0, 10.0, 5.0, 0.0, 0.0], abs=1e-3)


def test_uniform_field_is_stratiform():
    dbz = np.full((40, 40), 30.0)
    echo = np.ones_like(dbz, bool)
    assert not steiner_convective(dbz, echo, 2.0).any()
    assert background_dbz(dbz, echo, 2.0)[20, 20] == pytest.approx(30.0)


def test_intensity_centre_and_radius():
    dbz = np.full((41, 41), 20.0)
    dbz[20, 20] = 45.0
    echo = np.ones_like(dbz, bool)
    conv = steiner_convective(dbz, echo, 1.0)
    assert conv[20, 20]
    # background around the centre is about 21-22 dBZ -> radius 1 km (Fig. 6b, medium)
    assert conv[20, 21] and not conv[20, 22]
    assert conv.sum() == 5


def test_peakedness_centre():
    dbz = np.full((41, 41), 20.0)
    dbz[20, 20] = 35.0                      # below 40 dBZ but well above a 20 dBZ background
    echo = np.ones_like(dbz, bool)
    assert steiner_convective(dbz, echo, 1.0)[20, 20]
    dbz[20, 20] = 24.0                      # 4 dB above: below Delta Z(20 dBZ) = 7.8 dB
    assert not steiner_convective(dbz, echo, 1.0).any()


def test_no_echo_is_no_class():
    dbz = np.zeros((20, 20))
    echo = np.zeros_like(dbz, bool)
    c = classes_on_coarse_grid(dbz, echo)
    assert not c["convective"].any() and not c["stratiform"].any()


def test_coarse_grid_and_obs_field():
    obs = np.full((40, 40), 0.0)            # floor = no echo
    obs[10:30, 10:30] = 25.0                # stratiform area
    obs[18:22, 18:22] = 50.0                # convective core
    obs[0, 0] = np.nan                      # no coverage
    c = obs_classes(obs)
    assert c["convective"][19, 19] and c["stratiform"][12, 12]
    assert not (c["convective"] & c["stratiform"]).any()
    assert not c["convective"][0, 0] and not c["stratiform"][0, 0] and not c["stratiform"][5, 5]
    # default 2 km grid: the classification is per 2 x 2 block
    assert (c["convective"][::2, ::2] == c["convective"][1::2, 1::2]).all()
    c1 = obs_classes(obs, factor=1)
    assert c1["convective"][19, 19]


def test_centres_only_is_smaller():
    dbz = np.full((40, 40), 20.0)
    dbz[20, 20] = 45.0
    echo = np.ones_like(dbz, bool)
    med = classes_on_coarse_grid(dbz, echo, factor=1)["convective"]
    cen = classes_on_coarse_grid(dbz, echo, factor=1, conv_radius=CENTRES_ONLY)["convective"]
    assert cen.sum() == 1 and med.sum() > cen.sum() and (med | cen).sum() == med.sum()
