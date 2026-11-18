"""Level correction of ODYSSEY towards CIRRUS, one offset per period (H3, #20).

The method and its numbers are in docs/method.md, *Level correction (H3)*: the offsets are on the intensity of
the wet hours (the mean rain of the ERA5-Land cell-hours of at least 0.1 mm), radar against the bridge
ERA5-Land, each ODYSSEY period against CIRRUS 7/2024-17/11/2025 (period D, the target). They were decided for
G1 and archive v1 on 17/11/2026 (#96). The wet frequency is not corrected: its gap is documented as a difference
of quality control.

An intensity offset k is applied to each composite as one shift in dBZ. With Marshall-Palmer (Z = 200 R^1.6) a
rain rate scales by k when the reflectivity moves by 10 * 1.6 * log10(k) = 16 * log10(k) dB. The shift moves
every echo, so the radar keeps its own structure; it changes the wet frequency only through the echoes near
the rain threshold.

Order in the chain: after the cleaning of H2 (``opera_ds.clean.clean_composite``), whose static mask is counted
on uncorrected composites, and before the interpolation.

Fields are in dBZ as returned by ``Frame.to_field(0.0)``: NaN outside the coverage, 0 for ``undetect`` and for
echoes at or below 0 dBZ. Only echoes above 0 dBZ are shifted, and a negative shift never takes an echo below 0.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import numpy as np

from .clean import ODYSSEY_PERIOD_STARTS, odyssey_period

MP_B = 1.6                       # Marshall-Palmer exponent, Z = 200 R^1.6 (method.md, as NIMBUS and IRENE)
# The archive becomes regular only in April 2013 (data.md, *Known problems*); period A starts there.
ODYSSEY_FIRST = dt.datetime(2013, 4, 1)
PERIOD_NAMES = ("A", "B", "C")


@dataclass(frozen=True)
class LevelOffsets:
    """Intensity offsets of the ODYSSEY periods A, B and C against a CIRRUS target, as log10 of the ratio
    (target / period), with where they come from."""

    name: str
    target: str
    log10_k: tuple[float, float, float]
    source: str

    def shift_db(self, period: int) -> float:
        """Shift in dBZ of period index `period` (0 = A, 1 = B, 2 = C)."""
        return 10.0 * MP_B * self.log10_k[period]


# Decided on 17/11/2026 on #96 for G1 and archive v1: docs/method.md, *Level on the intensity*, table 1
# (A x1.34, B x1.06, C x1.01; 95% intervals about +-0.7 to 0.9 dB). E is assessed again in May 2027 (H8, #24).
V1 = LevelOffsets(
    name="h3-intensity-v1",
    target="CIRRUS 2024-07-01/2025-11-17 (period D)",
    log10_k=(0.127, 0.023, 0.006),
    source="docs/method.md, Level on the intensity; decided 2026-11-17 on fedro86/DECADE#96",
)


def period_index(t: dt.datetime) -> int:
    """ODYSSEY period of time `t`: 0 = A (4/2013-11/2015), 1 = B (12/2015-7/2018), 2 = C (from 8/2018).
    Times before April 2013 have no offset and raise ValueError."""
    if t < ODYSSEY_FIRST:
        raise ValueError(f"{t:%Y-%m-%d %H:%M} is before {ODYSSEY_FIRST:%m/%Y}: no level offset (period A starts "
                         "when the archive becomes regular)")
    return odyssey_period(t)


def shift_dbz(dbz: np.ndarray, shift_db: float, floor: float = 0.0) -> np.ndarray:
    """Add `shift_db` to the echoes above `floor`; `floor` (no echo) and NaN (no coverage) are kept, and no
    echo goes below `floor`. Returns a new array of the same dtype."""
    dbz = np.asarray(dbz)
    echo = dbz > floor                              # False for NaN
    out = np.where(echo, np.maximum(dbz + shift_db, floor), dbz)
    return out.astype(dbz.dtype, copy=False)


def correct_composite(dbz: np.ndarray, t: dt.datetime, offsets: LevelOffsets = V1) -> np.ndarray:
    """Level correction of one cleaned ODYSSEY composite at time `t` (dBZ field from `Frame.to_field(0.0)`)."""
    return shift_dbz(dbz, offsets.shift_db(period_index(t)))


def correction_attrs(t: dt.datetime, offsets: LevelOffsets = V1) -> dict:
    """Attributes to store with a corrected frame, so that the correction can be traced and undone."""
    p = period_index(t)
    return {
        "level_correction": offsets.name,
        "level_target": offsets.target,
        "level_period": PERIOD_NAMES[p],
        "level_log10_k": float(offsets.log10_k[p]),
        "level_shift_db": float(offsets.shift_db(p)),
        "level_source": offsets.source,
    }


__all__ = ["LevelOffsets", "V1", "MP_B", "ODYSSEY_FIRST", "ODYSSEY_PERIOD_STARTS", "PERIOD_NAMES",
           "period_index", "shift_dbz", "correct_composite", "correction_attrs"]
