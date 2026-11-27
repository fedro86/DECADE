"""Does the Belgian offset hold on the whole crop? Intensity offsets of A, B and C against D on every land ERA5-Land
cell of the crop, per country of the nearest radar and per ring of distance (H3, #20; review of #96, point 3 of
18/11/2026).

Input: the hourly sums of `scripts/odyssey_clean_era5grid.py --crop` (ODYSSEY cleaned as in H2 for A, B, C;
CIRRUS as it is for D, `--product cirrus`), results/h3_level/era5grid_*_crop_<YYYY-MM>.npz.

Same quantity as notebook 09, sections 7 and 8: per month, the log10 of the wet-hour intensity radar / ERA5-Land,
a wet cell-hour having at least 0.1 mm, on complete radar hours and final ERA5-Land, D to 17/11/2025; a month is
kept if at least half of its hours are complete and final. The offset of a period against D is balanced over the 12
calendar months, with the t interval of 11 df (`balanced` of section 7).

- **Cells:** land cells of the crop whose pixel count in both products, at 7/2024, is at least 0.8 of the median
  of the same grid row, so the cells cut by the edge of the crop are left out. The median, not the largest as for
  the 186 Belgian cells: on the 2 km grid a full cell gets 18 to 24 pixels depending on how the grids fall on each
  other, and the cells shrink to the north.
- **Nearest radar:** each month, among the radars listed in the composite on at least 80% of the days (listed on a
  day: in at least half of its time steps; `results/h2_artefacts/nodes_*.csv`, as `docs/method.md`, *Radars over
  time*), positions and country from the OPERA radar database of 10/11/2026. A cell belongs to the country of
  its nearest radar in that month.
- **Comparison:** each offset minus the Belgian offset decided for G1 (`docs/method.md`, *Level on the
  intensity*: +0.127, +0.023, +0.006), against U of the level over Europe (same section, table 2: 0.056, 0.052,
  0.044). The Belgian offset is also recomputed here on the 186 cells, as a check of the crop sums.

  uv run python scripts/crop_offsets.py --processes 8      # builds results/h3_level/crop_monthly.npz, then the tables
  uv run python scripts/crop_offsets.py --summary          # the tables only

Writes results/h3_level/crop_monthly.npz and results/h3_level/crop_offsets.csv.
"""
from __future__ import annotations

import argparse
import calendar
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats

from opera_ds.paths import DATA_DIR, RESULTS_DIR

H2 = RESULTS_DIR / "h2_artefacts"
H3 = RESULTS_DIR / "h3_level"
THR = 0.1
FULL_FRAMES = {"odyssey": 4, "cirrus": 12}
D_END = np.datetime64("2025-11-18T00")  # target D: CIRRUS to 17/11/2025
PERIODS = {"A": ((2013, 4), (2015, 11)), "B": ((2015, 12), (2018, 7)), "C": ((2018, 8), (2024, 6)),
           "D": ((2024, 7), (2025, 11))}
OFF_BE = {"A": 0.127, "B": 0.023, "C": 0.006}  # docs/method.md, *Level on the intensity*, table 1
# U of the level over Europe (notebook 09, section 8, "U EU"): k from the effective degrees of freedom, and the
# bridge term over Europe either g/sqrt(3) around ERA5-Land or left out (docs/method.md, *Uncertainty budget*)
U_EU_BY_CHOICE = {"g/sqrt3": {"A": 0.076, "B": 0.071, "C": 0.049}, "none": {"A": 0.052, "B": 0.048, "C": 0.048}}
BRIDGE_EU_CHOICE = "g/sqrt3"
U_EU = U_EU_BY_CHOICE[BRIDGE_EU_CHOICE]
RINGS = ((0, 50), (50, 100), (100, 150), (150, 1000))
LAT_N, LON_W, STEP, NLON = 55.0, -3.9, 0.1, 158
MIN_CELLS = 30  # a country with fewer cells on average is not shown


def product_of(ym):
    return "odyssey" if ym < (2024, 7) else "cirrus"


def crop_file(ym):
    y, m = ym
    name = "odyssey_clean" if product_of(ym) == "odyssey" else "cirrus"
    return H3 / f"era5grid_{name}_crop_{y}-{m:02d}.npz"


def all_months():
    return [(y, m) for y in range(2013, 2026) for m in range(1, 13) if (2013, 4) <= (y, m) <= (2025, 11)]


def full_cells():
    """Cells of the crop fully covered in both products at 7/2024: npix at least 0.8 of the row median."""
    keep = None
    for name in ("odyssey_clean", "cirrus"):
        z = np.load(H3 / f"era5grid_{name}_crop_2024-07.npz")
        c, n = z["cells"], z["npix"]
        rowmed = pd.Series(n).groupby(c[:, 0]).transform("median").values
        s = {tuple(x) for x in c[n >= 0.8 * rowmed]}
        keep = s if keep is None else keep & s
    return np.array(sorted(keep))


def belgian_cells():
    """The 186 cells of notebook 07 and 09 (Belgian sums of scripts/odyssey_clean_era5grid.py, 7/2024)."""
    out = None
    for name in ("odyssey_clean", "cirrus"):
        z = np.load(H3 / f"era5grid_{name}_2024-07.npz")
        s = {tuple(c) for c in z["cells"][z["npix"] >= 0.8 * z["npix"].max()]}
        out = s if out is None else out & s
    return out


def month_counts(ym, cells):
    """Per cell: radar wet count and sum, ERA5-Land wet count and sum (>= 0.1 mm), on complete and final hours."""
    import xarray as xr

    era = xr.open_zarr(DATA_DIR / "era5land_bel.zarr", consolidated=False)
    product = product_of(ym)
    z = np.load(crop_file(ym))
    pos = {tuple(c): k for k, c in enumerate(z["cells"])}
    sel = np.array([pos.get(tuple(c), -1) for c in cells])
    he = np.array(z["hour_end"], dtype="datetime64[ns]")
    ok = (z["frames"] == FULL_FRAMES[product]) & (he <= era["valid_time"].values[-1]) & (he <= D_END)
    final = era["expver"].sel(valid_time=he[ok]).values == 1
    hours = he[ok][final]
    y, m = ym
    nmax = (17 if ym == (2025, 11) else calendar.monthrange(y, m)[1]) * 24
    keep = bool(hours.size >= 0.5 * nmax and final.mean() >= 0.5)
    out = np.zeros((len(cells), 4))
    if hours.size == 0:
        return ym, keep, out
    rain = z["rain_clean"] if product == "odyssey" else z["rain"]
    r = rain[ok][final][:, np.maximum(sel, 0)].astype(float)
    r[:, sel < 0] = np.nan
    e = era["tp"].sel(valid_time=hours).values[:, cells[:, 0], cells[:, 1]]
    good = np.isfinite(r) & np.isfinite(e)
    wr, we = good & (r >= THR), good & (e >= THR)
    out[:, 0], out[:, 1] = wr.sum(0), np.where(wr, r, 0).sum(0)
    out[:, 2], out[:, 3] = we.sum(0), np.where(we, e, 0).sum(0)
    return ym, keep, out


def active_radars(months):
    """{month: radars listed on at least 80% of the days}; ODYSSEY lists before 7/2024, CIRRUS lists after."""
    lists = {"odyssey": pd.read_csv(H2 / "nodes_odyssey.csv"),
             "cirrus": pd.concat([pd.read_csv(H2 / f"nodes_cirrus_{y}.csv") for y in (2024, 2025)])}
    out = {}
    for product, nd in lists.items():
        # from 18/11/2025 (CIRRUS 1.5.0) the node names are quoted; D ends on 17/11/2025
        nd = nd[nd.day <= 20251117].assign(ym=lambda x: x.day // 100, node=lambda x: x.node.str.strip("'"))
        days = nd.groupby("ym").day.nunique()
        listed = nd[nd.steps_listed >= 0.5 * nd.steps_day].groupby(["ym", "node"]).day.nunique()
        for (ym, node), n in listed.items():
            key = (ym // 100, ym % 100)
            if key in months and product_of(key) == product and n >= 0.8 * days[ym]:
                out.setdefault(key, set()).add(node)
    return out


def km(lon1, lat1, lon2, lat2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def nearest_radar(cells, months):
    """Per month and cell: country and distance (km) of the nearest radar listed that month."""
    db = {r["odimcode"]: (float(r["longitude"]), float(r["latitude"]), r["country"])
          for r in json.load(open(DATA_DIR / "opera_radars" / "OPERA_RADARS_DB_20261110.json", encoding="utf-8"))
          if r.get("odimcode") and r.get("longitude") and r.get("latitude")}
    act = active_radars(set(months))
    lat, lon = LAT_N - STEP * cells[:, 0], LON_W + STEP * cells[:, 1]
    country = np.empty((len(months), len(cells)), object)
    dist = np.full((len(months), len(cells)), np.nan)
    missing = set()
    for i, ym in enumerate(months):
        radars = sorted(r for r in act.get(ym, ()) if r in db)
        missing |= set(act.get(ym, ())) - set(db)
        if not radars:
            continue
        d = np.array([km(lon, lat, db[r][0], db[r][1]) for r in radars])
        k = d.argmin(0)
        dist[i] = d[k, np.arange(len(cells))]
        country[i] = np.array([db[r][2] for r in radars], object)[k]
    if missing:
        print("radars listed but not in the OPERA database (left out):", ", ".join(sorted(missing)))
    return country, dist


def build(processes):
    cells = full_cells()
    months = [ym for ym in all_months() if crop_file(ym).exists()]
    lost = [ym for ym in all_months() if not crop_file(ym).exists()]
    if lost:
        print(f"{len(lost)} months without crop sums: {lost[0]} ... {lost[-1]}")
    res = {}
    with ProcessPoolExecutor(processes) as ex:
        for ym, keep, c in ex.map(month_counts, months, [cells] * len(months)):
            res[ym] = (keep, c)
    months = [ym for ym in months if res[ym][0]]
    counts = np.stack([res[ym][1] for ym in months])
    country, dist = nearest_radar(cells, months)
    be = belgian_cells()
    np.savez_compressed(H3 / "crop_monthly.npz", months=np.array(months), cells=cells, counts=counts,
                        country=country.astype(str), dist=dist,
                        belgian=np.array([tuple(c) in be for c in cells]))
    print(f"{len(months)} months, {len(cells)} cells, {sum(tuple(c) in be for c in cells)} of the 186 Belgian ones")


def lr(counts, member):
    """Monthly log10 of the wet-hour intensity radar / ERA5-Land over the member cells (months x cells mask)."""
    m = member[..., None]
    nr, sr, ne, se = (np.where(m, counts, 0).sum(1)[:, i] for i in range(4))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.log10((sr / nr) / (se / ne))


def balanced(series, months, p):
    """Offset of period p against D, balanced over the 12 calendar months, t interval (df = months - 1)."""
    per = np.array([next(q for q, (a, b) in PERIODS.items() if a <= ym <= b) for ym in months])
    mo = np.array([ym[1] for ym in months])
    d = np.array([np.nanmean(series[(per == "D") & (mo == m)]) - np.nanmean(series[(per == p) & (mo == m)])
                  for m in range(1, 13)])
    d = d[np.isfinite(d)]
    half = stats.t.ppf(0.975, d.size - 1) * d.std(ddof=1) / np.sqrt(d.size)
    return d.mean(), half, d.size


def summary():
    z = np.load(H3 / "crop_monthly.npz", allow_pickle=False)
    months = [tuple(int(v) for v in ym) for ym in z["months"]]
    counts, country, dist, belg = z["counts"], z["country"], z["dist"], z["belgian"]
    nm = len(months)
    groups = {"Belgium, the 186 cells (check)": np.repeat(belg[None], nm, 0),
              "whole crop": np.ones(country.shape, bool)}
    for c in sorted(set(country.ravel()) - {"None", ""}):
        mem = country == c
        if mem.sum(1).mean() >= MIN_CELLS:
            groups[f"country of the nearest radar: {c}"] = mem
    for a, b in RINGS:
        groups[f"ring {a}-{b if b < 1000 else ''} km".replace("- km", "+ km")] = (dist >= a) & (dist < b)
    rows = []
    for name, mem in groups.items():
        s = lr(counts, mem)
        for p in "ABC":
            o, h, n = balanced(s, months, p)
            diff = o - OFF_BE[p]
            rows.append(dict(group=name, period=p, cells=round(float(mem.sum(1).mean())), offset=o, half95=h,
                             calendar_months=n, minus_belgian=diff, U_EU=U_EU[p], beyond_U=abs(diff) > U_EU[p]))
    df = pd.DataFrame(rows)
    df.to_csv(H3 / "crop_offsets.csv", index=False)
    print(f"{nm} months, {counts.shape[1]} cells; intensity offset against D (log10, x factor, 95%);"
          " minus the Belgian offset; * beyond U of the level over Europe")
    for p in "ABC":
        print(f"\n{p}: Belgian offset {OFF_BE[p]:+.3f} (x{10 ** OFF_BE[p]:.2f}), U {U_EU[p]:.3f}")
        for r in df[df.period == p].itertuples():
            print(f"   {r.group:52s} {r.cells:5d} cells  {r.offset:+.3f} (x{10 ** r.offset:.2f},"
                  f" x{10 ** (r.offset - r.half95):.2f}-{10 ** (r.offset + r.half95):.2f})"
                  f"  {r.minus_belgian:+.3f}{'*' if r.beyond_U else ' '}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--processes", type=int, default=8)
    ap.add_argument("--summary", action="store_true", help="only the tables, from crop_monthly.npz")
    args = ap.parse_args()
    if not args.summary:
        build(args.processes)
    summary()


if __name__ == "__main__":
    main()
