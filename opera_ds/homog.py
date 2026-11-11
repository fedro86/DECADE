"""Monthly ratio of a radar product to a bridge, and its step at a date (H3, #20, *Homogeneity of the bridge*).

The weather is in both series, so it cancels in their ratio; a step in the ratio at a date points to a change
in one of the two products (docs/method.md, *Homogeneity of the bridge*). These functions only describe the
step and the month-to-month spread around it; the test statistic and any threshold are still to be chosen from
the homogenisation literature, so none is applied here.
"""
from __future__ import annotations

import numpy as np


def area_ratio(product: np.ndarray, bridge: np.ndarray, cells: np.ndarray) -> float:
    """Ratio of the totals of `product` and `bridge` over `cells`, using only cells finite in both.
    NaN if the bridge total is not positive."""
    p, b = np.asarray(product)[cells], np.asarray(bridge)[cells]
    ok = np.isfinite(p) & np.isfinite(b)
    tb = b[ok].sum()
    return float(p[ok].sum() / tb) if tb > 0 else np.nan


def _months_between(a: tuple[int, int], b: tuple[int, int]) -> int:
    return (b[0] - a[0]) * 12 + (b[1] - a[1])


def step(series: dict, at: tuple[int, int], n: int, exclude=()) -> dict:
    """Step of log10 of a monthly ratio at month `at`.

    `series` maps (year, month) to the ratio. The n months before `at` and the n months from `at` on are
    compared; months in `exclude` or with a non-finite or non-positive ratio are left out. Returns the mean of
    each side and their difference in log10 units (0.1 ≈ 26%), the number of months used on each side, and the
    standard deviation of the months before, the spread a step is to be compared with.
    """
    before, after = [], []
    for k, v in series.items():
        if k in exclude or not np.isfinite(v) or v <= 0:
            continue
        d = _months_between(at, k)
        if -n <= d < 0:
            before.append(np.log10(v))
        elif 0 <= d < n:
            after.append(np.log10(v))
    mb = float(np.mean(before)) if before else np.nan
    ma = float(np.mean(after)) if after else np.nan
    return {
        "mean_before": mb,
        "mean_after": ma,
        "step": ma - mb,
        "n_before": len(before),
        "n_after": len(after),
        "sd_before": float(np.std(before, ddof=1)) if len(before) > 1 else np.nan,
    }
