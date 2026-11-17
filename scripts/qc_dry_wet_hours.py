"""Are the extra echoes of CIRRUS rain? Radar against ERA5-Land and the RMI stations, wet and dry hours (H3, #20;
review of #96, comment of 17/11/2026)

The hourly sums of the H3 trial (notebook 09: ODYSSEY cleaned for A, B, C, CIRRUS as it is for D, on the 186
ERA5-Land cells of the trial, complete radar hours, final ERA5-Land only, D to 17/11/2025) are split by whether
the radar and the reference are wet (>= 0.1 mm in the hour) or dry:

- **ERA5-Land**, per cell-hour of the 186 cells;
- **RMI automatic stations**, per station-hour: the station against the radar sum of the ERA5-Land cell that holds
  it (a cell mean against a point), hours validated by the RMI, cells present in both radar products.

Counts are kept per month, hour of day (3 h blocks of the hour end, UTC) and ring of distance from the nearest
Belgian radar in the composite that month (bewid; bejab from 12/2014; behel from 4/2018, data.md, *Radars over
time*): 0-30, 30-60, 60+ km. A station keeps its own distance.

Writes OUT/qc_dry_wet_era5.csv and OUT/qc_dry_wet_rmi.csv, then prints the summary (also alone with --summary):

  uv run python scripts/qc_dry_wet_hours.py --out results/h3_level

Reading. Per month, the radar frequency against the reference is F = N(radar wet) / N(reference wet). It splits
exactly into F = FA + H: FA = N(radar wet, reference dry) / N(reference wet), H = N(radar wet, reference wet) /
N(reference wet). A gap of F between two periods, balanced over the 12 calendar months, is then the part in hours
the reference calls dry (dFA) plus the part in wet hours (dH).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

from opera_ds.paths import DATA_DIR, RESULTS_DIR

H3 = RESULTS_DIR / "h3_level"
THR = 0.1
FULL_FRAMES = {"odyssey": 4, "cirrus": 12}
D_END = np.datetime64("2025-11-18T00")
PERIODS = {"A": ((2013, 4), (2015, 11)), "B": ((2015, 12), (2018, 7)), "C": ((2018, 8), (2024, 6)),
           "D": ((2024, 7), (2025, 11))}
RADARS = {"bewid": ((5.5044, 49.9135), (2000, 1)), "bejab": ((3.0641, 51.1919), (2014, 12)),
          "behel": ((5.4054, 51.0702), (2018, 4))}
RINGS = ((0, 30), (30, 60), (60, 1000))
SEASONS = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}
CATS = ("rw_ew", "rw_ed", "rd_ew", "rd_ed")


def km(lon1, lat1, lon2, lat2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def nearest(lon, lat, ym):
    return np.min([km(lon, lat, *xy) for xy, start in RADARS.values() if ym >= start], axis=0)


def ring_of(d):
    return np.select([(d >= a) & (d < b) for a, b in RINGS], range(len(RINGS)), -1)


def period_of(ym):
    return next(p for p, (a, b) in PERIODS.items() if a <= ym <= b)


def counts(rows, key, r, x, ring, hb, extra=None):
    """Append one row per (ring, hour block) with the four wet/dry counts and the radar sums."""
    good = np.isfinite(r) & np.isfinite(x)
    rw, xw = r >= THR, x >= THR
    cat = {"rw_ew": good & rw & xw, "rw_ed": good & rw & ~xw, "rd_ew": good & ~rw & xw, "rd_ed": good & ~rw & ~xw}
    for g in range(len(RINGS)):
        for b in range(8):
            m = (ring == g) & (hb == b)
            if not m.any():
                continue
            row = dict(key, ring=g, hour_block=b, **(extra or {}))
            for c, v in cat.items():
                row[c] = int((v & m).sum())
            row["radar_rw_ed"] = float(r[cat["rw_ed"] & m].sum())
            row["radar_rw_ew"] = float(r[cat["rw_ew"] & m].sum())
            row["ref_rd_ew"] = float(x[cat["rd_ew"] & m].sum())
            rows.append(row)


def build(out: Path) -> None:
    era = xr.open_zarr(DATA_DIR / "era5land_bel.zarr", consolidated=False)
    expver = era["expver"].load()
    lon, lat = era["longitude"].values, era["latitude"].values

    def full_cells(product):
        z = np.load(H3 / f"era5grid_{product}_2024-07.npz")
        return {tuple(c) for c in z["cells"][z["npix"] >= 0.8 * z["npix"].max()]}

    common = sorted(full_cells("odyssey") & full_cells("cirrus"))
    ci, cj = np.array([c[0] for c in common]), np.array([c[1] for c in common])

    st = json.load(open(DATA_DIR / "rmi_aws" / "stations.json", encoding="utf-8"))
    aws = np.load(DATA_DIR / "rmi_aws" / "aws_1hour_precip.npz")
    scell = {s["code"]: (int(np.abs(lat - s["lat"]).argmin()), int(np.abs(lon - s["lon"]).argmin())) for s in st}
    sll = {s["code"]: (s["lon"], s["lat"]) for s in st}
    gauge = {}
    for code in scell:
        k = (aws["code"] == code) & aws["validated"]
        gauge[code] = pd.Series(aws["precip"][k], index=pd.DatetimeIndex(aws["time"][k]))
        gauge[code] = gauge[code][~gauge[code].index.duplicated()]

    rows_e, rows_s = [], []
    for y in range(2013, 2026):
        for m in range(1, 13):
            if not (2013, 4) <= (y, m) <= (2025, 11):
                continue
            ym, product = (y, m), ("odyssey" if (y, m) < (2024, 7) else "cirrus")
            z = np.load(H3 / (f"era5grid_odyssey_clean_{y}-{m:02d}.npz" if product == "odyssey"
                              else f"era5grid_cirrus_{y}-{m:02d}.npz"))
            pos = {tuple(c): k for k, c in enumerate(z["cells"])}
            he = np.array(z["hour_end"], dtype="datetime64[ns]")
            ok = (z["frames"] == FULL_FRAMES[product]) & (he <= era["valid_time"].values[-1]) & (he <= D_END)
            final = expver.sel(valid_time=he[ok]).values == 1
            hours = he[ok][final]
            if hours.size == 0:
                continue
            rain = (z["rain_clean"] if product == "odyssey" else z["rain"])[ok][final]
            hb = (hours.astype("datetime64[h]").astype(int) % 24) // 3
            key = dict(year=y, month=m, period=period_of(ym), hours=int(hours.size))
            # ERA5-Land, 186 cells
            r = rain[:, [pos[c] for c in common]]
            e = era["tp"].sel(valid_time=hours).values[:, ci, cj]
            d = nearest(lon[cj], lat[ci], ym)
            counts(rows_e, key, r, e, np.broadcast_to(ring_of(d), r.shape), np.broadcast_to(hb[:, None], r.shape))
            # RMI stations, cell of the station
            for code, cell in scell.items():
                if cell not in pos:
                    continue
                g = gauge[code].reindex(pd.DatetimeIndex(hours)).values
                rs = rain[:, pos[cell]]
                ds = float(nearest(*sll[code], ym))
                counts(rows_s, key, rs, g, np.full(rs.shape, int(ring_of(np.array(ds)))), hb,
                       extra=dict(station=code, dist_km=round(ds, 1)))
            print(f"{y}-{m:02d} {product}: {hours.size} hours", flush=True)
    pd.DataFrame(rows_e).to_csv(out / "qc_dry_wet_era5.csv", index=False)
    pd.DataFrame(rows_s).to_csv(out / "qc_dry_wet_rmi.csv", index=False)


# ------------------------------------------------------------------------------------------------- summary
def shares(df):
    s = df[list(CATS)].sum()
    rw, xw = s.rw_ew + s.rw_ed, s.rw_ew + s.rd_ew
    return dict(n=int(s.sum()), radar_wet_ref_dry=s.rw_ed / rw, ref_wet_radar_dry=s.rd_ew / xw, F=rw / xw,
                FA=s.rw_ed / xw, H=s.rw_ew / xw)


def monthly(df):
    g = df.groupby(["year", "month"])[list(CATS)].sum()
    xw = g.rw_ew + g.rd_ew
    return pd.DataFrame(dict(FA=g.rw_ed / xw, H=g.rw_ew / xw, F=(g.rw_ew + g.rw_ed) / xw, xw=xw))


def balanced_gap(df, p, q, keys_p=None, keys_q=None):
    """q minus p, per calendar month then averaged; for F, FA, H (absolute) and log10 F; 95% t interval."""
    mo = monthly(df)
    sel = lambda per, keys: mo.loc[[k for k in mo.index if (keys is None and k in KEYS[per]) or
                                    (keys is not None and k in keys)]]
    a, b = sel(p, keys_p), sel(q, keys_q)
    res = {}
    for col in ("F", "FA", "H"):
        d = []
        for m in range(1, 13):
            va, vb = a[col][a.index.get_level_values(1) == m], b[col][b.index.get_level_values(1) == m]
            if len(va) and len(vb):
                d.append(vb.mean() - va.mean())
        d = np.array(d)
        half = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
        res[col] = (d.mean(), half, len(d))
    return res


KEYS: dict = {}


def summary(out: Path) -> None:
    E = pd.read_csv(out / "qc_dry_wet_era5.csv")
    S = pd.read_csv(out / "qc_dry_wet_rmi.csv")
    for p, (a, b) in PERIODS.items():
        KEYS[p] = sorted({(y, m) for y, m in zip(E.year, E.month) if a <= (y, m) <= b})
    E["season"] = E.month.map({m: s for s, ms in SEASONS.items() for m in ms})
    S["season"] = S.month.map({m: s for s, ms in SEASONS.items() for m in ms})
    ring_names = [f"{a}-{b if b < 1000 else ''} km".replace("- km", "+ km") for a, b in RINGS]

    for name, df in (("ERA5-Land, 186 cells", E), ("RMI stations", S)):
        print(f"\n=== {name}: share of radar-wet hours where the reference is dry / of reference-wet hours where "
              f"the radar is dry; F = radar wet / reference wet")
        print("period  n          radar wet, ref dry   ref wet, radar dry   F")
        for p in PERIODS:
            s = shares(df[df.period == p])
            print(f"{p}       {s['n']:<10d} {s['radar_wet_ref_dry']:.3f}                {s['ref_wet_radar_dry']:.3f}"
                  f"                {s['F']:.2f}")
        for split, labels in (("season", list(SEASONS)), ("hour_block", list(range(8))), ("ring", range(len(RINGS)))):
            print(f"  by {split}: radar wet & ref dry | ref wet & radar dry, per period A B C D")
            for lab in labels:
                cells = []
                for p in PERIODS:
                    sub = df[(df.period == p) & (df[split] == lab)]
                    if sub[list(CATS)].values.sum() == 0:
                        cells.append("   -        -  ")
                        continue
                    s = shares(sub)
                    cells.append(f"{s['radar_wet_ref_dry']:.3f} {s['ref_wet_radar_dry']:.3f}")
                tag = (f"{3 * lab:02d}-{3 * lab + 3:02d} UTC" if split == "hour_block" else
                       ring_names[lab] if split == "ring" else lab)
                print(f"    {str(tag):12s} " + "   ".join(cells))

        print(f"\n  where the frequency gap sits (balanced over calendar months; F = FA + H, absolute; 95% t)")
        tests = [("C", "D", None, None, "C -> D, whole periods"),
                 ("A", "B", KEYS["A"][-12:], KEYS["B"][:12], "step at 12/2015, 12 months each side"),
                 ("B", "C", KEYS["B"][-12:], KEYS["C"][:12], "step at 8/2018, 12 months each side"),
                 ("A", "B", None, None, "A -> B, whole periods"), ("B", "C", None, None, "B -> C, whole periods")]
        for p, q, kp, kq, lab in tests:
            g = balanced_gap(df, p, q, kp, kq)
            dF, dFA, dH = g["F"][0], g["FA"][0], g["H"][0]
            print(f"    {lab:40s} dF {dF:+.3f}±{g['F'][1]:.3f}  dFA (ref dry) {dFA:+.3f}±{g['FA'][1]:.3f}"
                  f"  dH (ref wet) {dH:+.3f}±{g['H'][1]:.3f}  share in dry hours {dFA / dF if dF else np.nan:.2f}")
        for split, labels in (("season", list(SEASONS)), ("ring", range(len(RINGS))),
                              ("hour_block", list(range(8)))):
            print(f"    C -> D by {split}: dFA (ref dry) / dH (ref wet)")
            for lab in labels:
                sub = df[df[split] == lab]
                g = balanced_gap(sub, "C", "D")
                tag = (f"{3 * lab:02d}-{3 * lab + 3:02d} UTC" if split == "hour_block" else
                       ring_names[lab] if split == "ring" else lab)
                print(f"      {str(tag):12s} dFA {g['FA'][0]:+.3f}±{g['FA'][1]:.3f}   dH {g['H'][0]:+.3f}±{g['H'][1]:.3f}"
                      f"   ({g['F'][2]} months)")
        mean_extra = df.radar_rw_ed.sum() / df.rw_ed.sum(), df.radar_rw_ew.sum() / df.rw_ew.sum()
        print(f"  mean radar amount, ref dry {mean_extra[0]:.2f} mm, ref wet {mean_extra[1]:.2f} mm (all periods)")
        for p in PERIODS:
            sub = df[df.period == p]
            print(f"    {p}: ref dry {sub.radar_rw_ed.sum() / sub.rw_ed.sum():.2f} mm, ref wet "
                  f"{sub.radar_rw_ew.sum() / sub.rw_ew.sum():.2f} mm")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", action="store_true", help="only the summary, from the CSV files already written")
    a = ap.parse_args()
    out = Path(a.out)
    if not a.summary:
        build(out)
    summary(out)


if __name__ == "__main__":
    main()
