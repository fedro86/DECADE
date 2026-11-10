"""Cleaning of OPERA maximum-reflectivity composites, first version (H2, #19).

The method and its numbers are in docs/method.md, *Cleaning of ODYSSEY (H2)*, *Choice* and *Static mask:
rules in the literature*; the prototypes in notebooks/05-mr-artefacts.ipynb, sections 9 and 10. Each composite
goes through three steps, in this order:

1. **Impossible values:** echoes above 70 dBZ are set to no rain (Fluck et al. 2021).
2. **Gabella** (optional, ``gabella=True``): ``wradlib.classify.filter_gabella`` with its defaults; flagged
   cells are set to no rain, as in EURADCLIM (Overeem et al. 2023, section 3.1). Every before/after is to be
   reported with and without it (review of #74).
3. **Static mask:** pixels with >= 55 dBZ in at least 1% of their valid times, or > 70 dBZ in at least 0.1%,
   counted on past composites of the same period (the thresholds are ours, set on our data). Each masked pixel
   belongs to its nearest radar within 20 km and is used only while that radar is listed in ``how/nodes``;
   masked pixels farther than 20 km from any radar are always used. A masked pixel takes the inverse-distance
   mean (power 2) of the rain rate of its 4 nearest unmasked pixels, only where that is lower than its own
   (EURADCLIM, section 3.3; there on hourly sums, here on each composite).

Fields are in dBZ as returned by ``Frame.to_field(0.0)``: NaN outside the coverage, 0 for ``undetect``.
Rain rate for the fill: Marshall-Palmer (Z = 200 R^1.6), from 7 dBZ, capped at 55 dBZ (Imhoff et al. 2020).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import numpy as np
from scipy.spatial import cKDTree

IMPOSSIBLE_DBZ = 70.0          # Fluck et al. 2021 (method.md, Impossible values)
STRONG_DBZ = 55.0              # top reflectivity class of Wagner et al. 2012; cap of Imhoff et al. 2020
STRONG_SHARE = 0.01            # ours: rain far from the radars stays below 0.22% (method.md)
IMPOSSIBLE_SHARE = 0.001       # ours
# a masked pixel within this distance belongs to its nearest radar. Ours, not from the literature: from the disc
# check of method.md, Catalogue: ODYSSEY 2013-2024 (31 of the 44 discs centred within 20 km of a radar)
OWNER_KM = 20.0
FILL_NEIGHBOURS = 4            # EURADCLIM, section 3.3
FILL_POWER = 2.0
RAIN_MIN_DBZ, RAIN_MAX_DBZ = 7.0, 55.0
# Changes of OPERA's central processing that split ODYSSEY into three periods (method.md, Radars over time)
ODYSSEY_PERIOD_STARTS = (dt.datetime(2015, 12, 1), dt.datetime(2018, 8, 1))


def odyssey_period(t: dt.datetime) -> int:
    """0 before December 2015, 1 from December 2015 to July 2018, 2 from August 2018."""
    return sum(t >= s for s in ODYSSEY_PERIOD_STARTS)


def rain_rate(dbz: np.ndarray) -> np.ndarray:
    """Marshall-Palmer rain rate (mm/h) from 7 dBZ, capped at 55 dBZ; NaN and lower values give 0."""
    z = np.nan_to_num(dbz, nan=0.0)
    return np.where(z >= RAIN_MIN_DBZ, (10 ** (np.minimum(z, RAIN_MAX_DBZ) / 10) / 200.0) ** (1 / 1.6), 0.0)


def dbz_from_rain(r: np.ndarray) -> np.ndarray:
    """Inverse of `rain_rate` below the cap; 0 dBZ (no rain) where the rate is 0."""
    with np.errstate(divide="ignore"):
        return np.where(r > 0, 10 * np.log10(200.0 * np.power(r, 1.6)), 0.0)


@dataclass
class StaticCounts:
    """Per-pixel counts on past composites, from which the static mask is drawn."""

    valid: np.ndarray
    strong: np.ndarray
    impossible: np.ndarray

    @classmethod
    def zeros(cls, shape) -> "StaticCounts":
        return cls(*(np.zeros(shape, np.int64) for _ in range(3)))

    def add(self, dbz: np.ndarray) -> None:
        """Add one composite (dBZ field, NaN outside the coverage)."""
        ok = np.isfinite(dbz)
        z = np.nan_to_num(dbz, nan=0.0)
        self.valid += ok
        self.strong += ok & (z >= STRONG_DBZ)
        self.impossible += ok & (z > IMPOSSIBLE_DBZ)

    def __add__(self, other: "StaticCounts") -> "StaticCounts":
        return StaticCounts(self.valid + other.valid, self.strong + other.strong, self.impossible + other.impossible)

    def mask(self, strong_share: float = STRONG_SHARE, impossible_share: float = IMPOSSIBLE_SHARE) -> np.ndarray:
        n = np.maximum(self.valid, 1)
        return (self.strong / n >= strong_share) | (self.impossible / n >= impossible_share)


@dataclass
class StaticMask:
    """A static mask with its fill tables and the radar each masked pixel belongs to."""

    mask: np.ndarray
    pixels: np.ndarray = field(init=False)      # (n, 2) rows and columns of the masked pixels
    owner: np.ndarray = field(init=False)       # (n,) ODIM code of the owning radar, "" when none within OWNER_KM
    neighbours: np.ndarray = field(init=False)  # (n, k, 2) unmasked neighbours used for the fill
    weights: np.ndarray = field(init=False)     # (n, k) inverse-distance weights, summing to 1
    radars: dict = field(default_factory=dict)  # {odim code: (row, col)} on the same grid, may lie outside it
    pixel_km: float = 1.0

    def __post_init__(self):
        self.pixels = np.argwhere(self.mask)
        good = np.argwhere(~self.mask)
        self.owner = np.full(len(self.pixels), "", dtype=object)
        if len(self.pixels) and self.radars:
            names = sorted(self.radars)
            d, i = cKDTree(np.array([self.radars[n] for n in names], float)).query(self.pixels)
            near = d * self.pixel_km <= OWNER_KM
            self.owner[near] = np.array(names, dtype=object)[i[near]]
        k = min(FILL_NEIGHBOURS, len(good))
        if len(self.pixels) and k:
            d, i = cKDTree(good).query(self.pixels, k=k)
            d, i = d.reshape(len(self.pixels), k), i.reshape(len(self.pixels), k)
            w = 1.0 / np.maximum(d, 1e-9) ** FILL_POWER
            self.neighbours, self.weights = good[i], w / w.sum(1, keepdims=True)
        else:
            self.neighbours = np.zeros((len(self.pixels), 0, 2), int)
            self.weights = np.zeros((len(self.pixels), 0))

    def active(self, listed: set[str] | None) -> np.ndarray:
        """Masked pixels in use: those of a radar listed in `how/nodes`, and those with no radar.
        With `listed` None every masked pixel is in use."""
        if listed is None:
            return np.ones(len(self.pixels), bool)
        return np.array([o == "" or o in listed for o in self.owner], bool)


def static_fill(dbz: np.ndarray, static: StaticMask, listed: set[str] | None = None) -> np.ndarray:
    """EURADCLIM fill of the masked pixels in use: inverse-distance mean of the rain rate of the unmasked
    neighbours, only where it is lower than the pixel's own rate. Returns a new dBZ field."""
    out = dbz.copy()
    on = static.active(listed)
    if not on.any() or static.weights.shape[1] == 0:
        return out
    r = rain_rate(dbz)
    px, nb, w = static.pixels[on], static.neighbours[on], static.weights[on]
    fill = (r[nb[..., 0], nb[..., 1]] * w).sum(1)
    own = r[px[:, 0], px[:, 1]]
    lower = fill < own
    rows, cols = px[lower, 0], px[lower, 1]
    out[rows, cols] = dbz_from_rain(fill[lower])
    return out


def clean_composite(dbz: np.ndarray, static: StaticMask | None = None, listed: set[str] | None = None,
                    gabella: bool = True) -> np.ndarray:
    """First-version cleaning of one composite (dBZ field from `Frame.to_field(0.0)`): > 70 dBZ, then Gabella
    (if `gabella`), then the static mask (if given), switched with the radars `listed` in `how/nodes`."""
    out = np.where(dbz > IMPOSSIBLE_DBZ, 0.0, dbz)
    if gabella:
        from wradlib.classify import filter_gabella

        flag = filter_gabella(out.copy(), wsize=5, cartesian=True)
        out = np.where(flag & np.isfinite(out), 0.0, out)     # cells outside the coverage stay NaN
    if static is not None:
        out = static_fill(out, static, listed)
    return out
