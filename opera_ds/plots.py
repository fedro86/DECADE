"""Figures of the validation report (static PNG)."""
from __future__ import annotations

import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# fixed order: the colour follows the method, not its rank
STYLE = {
    "nearest": dict(color="#2a78d6", marker="o", label="nearest (closest frame)"),
    "linear": dict(color="#eb6834", marker="s", label="linear (Eulerian cross-fade)"),
    "lk": dict(color="#1baf7a", marker="^", label="Lucas-Kanade (advective)"),
    "lk:dB": dict(color="#eda100", marker="D", label="Lucas-Kanade, blending in dB"),
    "linear:dB": dict(color="#e87ba4", marker="v", label="linear, blending in dB"),
}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def _style_ax(ax, title, xlabel, ylabel):
    ax.set_facecolor(SURF)
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)


def _line(ax, x, y, m):
    st = STYLE.get(m, dict(color=INK2, marker="x", label=m))
    ax.plot(x, y, color=st["color"], marker=st["marker"], linewidth=2, markersize=6,
            markeredgecolor=SURF, markeredgewidth=1.5, label=st["label"])


def make_plots(summary: list[dict], qq: dict, out_dir: str):
    if not summary:
        return
    by = defaultdict(list)
    for r in summary:
        by[(r["method"], r["shift_min"])].append(r)
    shifts = sorted({r["shift_min"] for r in summary})
    methods = [m for m in STYLE if any(r["method"] == m for r in summary)]

    # best shift = lowest RMSE of the lk method, averaged over all alpha
    def mean_rmse(s, m="lk"):
        rs = by.get((m, s), [])
        return np.mean([r["rmse"] for r in rs]) if rs else np.inf
    best = min(shifts, key=mean_rmse)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), facecolor="white")

    ax = axes[0, 0]
    for m in methods:
        rs = sorted(by[(m, best)], key=lambda r: r["alpha"])
        _line(ax, [r["alpha"] * 15 for r in rs], [r["rmse"] for r in rs], m)
    _style_ax(ax, f"RMSE on wet pixels (shift {best:+g} min)",
              "minutes after ODYSSEY frame t0", "RMSE [dBZ]")
    handles, labels = ax.get_legend_handles_labels()

    ax = axes[0, 1]
    thr_keys = sorted({k for k in summary[0] if k.startswith("csi_")}, key=lambda k: float(k[4:]))
    thr = [float(k[4:]) for k in thr_keys]
    for m in methods:
        rs = [r for r in by[(m, best)] if r["alpha"] > 0]
        if not rs:
            continue
        w = np.array([r["n_times"] for r in rs], float)
        _line(ax, thr, [np.average([r[k] for r in rs], weights=w) for k in thr_keys], m)
    _style_ax(ax, "CSI at interpolated times", "threshold [dBZ]", "CSI")

    ax = axes[1, 0]
    fss_keys = [k for k in summary[0] if k.startswith("fss_")]
    if fss_keys:
        t_first = fss_keys[0].split("_")[1]
        ks = [k for k in fss_keys if k.split("_")[1] == t_first]
        scales = [int(k.split("_")[2].replace("km", "")) for k in ks]
        for m in methods:
            rs = [r for r in by[(m, best)] if r["alpha"] > 0]
            if not rs:
                continue
            w = np.array([r["n_times"] for r in rs], float)
            _line(ax, scales, [np.average([r[k] for r in rs], weights=w) for k in ks], m)
        ax.set_xscale("log")
        ax.set_xticks(scales)
        ax.set_xticklabels([str(s) for s in scales])
        _style_ax(ax, f"FSS at {t_first} at interpolated times", "scale [km]", "FSS")

    ax = axes[1, 1]
    for m in methods:
        rs = sorted(by[(m, best)], key=lambda r: r["alpha"])
        _line(ax, [r["alpha"] * 15 for r in rs], [r["hf_energy_ratio"] for r in rs], m)
    ax.axhline(1.0, color=INK2, linewidth=1, linestyle="--")
    ax.annotate("= CIRRUS variability", (0.02, 1.0), xycoords=("axes fraction", "data"),
                textcoords="offset points", xytext=(0, 4), fontsize=8, color=INK2)
    _style_ax(ax, "Small-scale energy (pred / CIRRUS)",
              "minutes after ODYSSEY frame t0", "ratio")

    fig.legend(handles, labels, loc="lower center", ncol=len(labels), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(os.path.join(out_dir, "validation_overview.png"), dpi=130)
    plt.close(fig)

    # mean RMSE by shift: estimate of the time offset between the two products
    fig, ax = plt.subplots(figsize=(6, 4), facecolor="white")
    for m in methods:
        _line(ax, shifts, [mean_rmse(s, m) for s in shifts], m)
    _style_ax(ax, "Time offset ODYSSEY vs CIRRUS", "applied shift [min]", "mean RMSE [dBZ]")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "time_shift.png"), dpi=130)
    plt.close(fig)

    # Q-Q
    fig, ax = plt.subplots(figsize=(5, 5), facecolor="white")
    lim = [0, 65]
    for m in methods:
        keys = [k for k in qq if k.startswith(f"{m}|{best}|") and float(k.split("|")[2]) > 0]
        if not keys:
            continue
        pred = np.mean([qq[k]["pred"] for k in keys], axis=0)
        obs = np.mean([qq[k]["obs"] for k in keys], axis=0)
        st = STYLE[m]
        ax.plot(obs, pred, color=st["color"], linewidth=2, label=st["label"])
    ax.plot(lim, lim, color=INK2, linewidth=1, linestyle="--")
    _style_ax(ax, "Q-Q of wet pixels (interpolated times)", "CIRRUS [dBZ]", "downscaled [dBZ]")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "qq.png"), dpi=130)
    plt.close(fig)
