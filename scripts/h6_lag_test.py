"""Which CIRRUS label matches the content of the ODYSSEY frame at T? Lag test for the time shift (H6, #21).

For the label NT the files declare the windows [NT-10, NT+5] for ODYSSEY and (NT-10, NT] for CIRRUS
(docs/data.md, *Time windows for the label NT*), so ODYSSEY at T should match CIRRUS at about T+2.5. This test
checks it on the data: each ODYSSEY frame of the overlap days (1/7/2024 00:00 to 5/7/2024 06:00) against the CIRRUS
frames at T-15 ... T+15 min, degraded to 2 km by `zmean` (`opera_ds.validate.read_degraded`), on the pixels covered
in both crops (Belgium + 350 km), values capped at 55 dBZ.

Scores per lag, summed over the times that have the lags -10, -5, +5 and +10 (CIRRUS has almost no frames at the
quarter hours on those days, so lag 0 cannot be scored):
- CSI at 20 and 30 dBZ;
- Pearson r of dBZ on the pixels at or above 10 dBZ in either product.

The lag comparison is not affected by the level difference between the products, which is the same at every lag.
Differences between lags get a 95% interval from a block bootstrap over hours (1000 draws, seed 0).

  uv run python scripts/h6_lag_test.py --processes 12

Writes results/h6/lag_records.json (one record per ODYSSEY time) and prints the tables.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from opera_ds.paths import DATA_DIR, RESULTS_DIR

OUT = RESULTS_DIR / "h6"
LAGS = (-15, -10, -5, 0, 5, 10, 15)
CORE = ("-10", "-5", "5", "10")
THR = (20.0, 30.0)
WET = 10.0
CAP = 55.0
FIRST, LAST = dt.datetime(2024, 7, 1), dt.datetime(2024, 7, 5, 6)   # ODYSSEY times of the overlap


def label_time(path: str) -> dt.datetime:
    m = re.search(r"(\d{8}T\d{4})", Path(path).name)
    return dt.datetime.strptime(m.group(1), "%Y%m%dT%H%M")


def capped(frame) -> np.ndarray:
    return np.minimum(frame.to_field(0.0), CAP)


def pair(ody, cirrus_path: str) -> dict:
    """Contingency counts and sums for r of one ODYSSEY frame against one CIRRUS file degraded to 2 km."""
    from opera_ds.validate import read_degraded

    cir = read_degraded(cirrus_path, "DBZH", 2, how="zmean")
    (ro, co), (rc, cc) = [(int(f.where["crop_row0"]), int(f.where["crop_col0"])) for f in (ody, cir)]
    r0, c0 = max(ro, rc), max(co, cc)
    r1 = min(ro + ody.values.shape[0], rc + cir.values.shape[0])
    c1 = min(co + ody.values.shape[1], cc + cir.values.shape[1])
    o = capped(ody)[r0 - ro:r1 - ro, c0 - co:c1 - co]
    q = capped(cir)[r0 - rc:r1 - rc, c0 - cc:c1 - cc]
    ok = np.isfinite(o) & np.isfinite(q)
    o, q = o[ok], q[ok]
    out = {}
    for t in THR:
        a, b = o >= t, q >= t
        out[f"hits{int(t)}"], out[f"union{int(t)}"] = int((a & b).sum()), int((a | b).sum())
    w = (o >= WET) | (q >= WET)
    x, y = o[w].astype(np.float64), q[w].astype(np.float64)
    out.update(n=int(w.sum()), sx=x.sum(), sy=y.sum(), sxx=(x * x).sum(), syy=(y * y).sum(), sxy=(x * y).sum())
    return out


def one_time(args) -> dict:
    from opera_ds.odim_io import read_odim_composite

    ody_path, cirrus = args
    ody = read_odim_composite(ody_path, "DBZH")
    t = label_time(ody_path)
    rec = {"time": t.isoformat()}
    for lag in LAGS:
        p = cirrus.get((t + dt.timedelta(minutes=lag)).isoformat())
        if p:
            rec[str(lag)] = pair(ody, p)
    return rec


def scores(records: list[dict], lag: str) -> dict:
    s = {k: sum(r[lag][k] for r in records) for k in records[0][lag]}
    n = s["n"]
    cov = s["sxy"] / n - s["sx"] / n * s["sy"] / n
    r = cov / np.sqrt((s["sxx"] / n - (s["sx"] / n) ** 2) * (s["syy"] / n - (s["sy"] / n) ** 2))
    return {"csi20": s["hits20"] / s["union20"], "csi30": s["hits30"] / s["union30"], "r": float(r)}


def summary(records: list[dict]) -> None:
    paired = [r for r in records if all(lag in r for lag in CORE)]
    print(f"ODYSSEY times: {len(records)}; with the lags -10, -5, +5, +10: {len(paired)}; "
          f"with lag 0: {sum('0' in r for r in records)}")
    table = {lag: scores(paired, lag) for lag in CORE}
    print("lag (min) | CSI 20 dBZ | CSI 30 dBZ | r")
    for lag in CORE:
        print(f"{int(lag):+d} | {table[lag]['csi20']:.3f} | {table[lag]['csi30']:.3f} | {table[lag]['r']:.3f}")

    def contrasts(rs):
        a = {lag: scores(rs, lag) for lag in CORE}
        return [a["5"][k] - a["-5"][k] for k in ("csi20", "csi30", "r")] + \
               [a["-5"][k] - a["10"][k] for k in ("csi20", "csi30", "r")]

    hours = sorted({r["time"][:13] for r in paired})
    by_hour = {h: [r for r in paired if r["time"][:13] == h] for h in hours}
    rng = np.random.default_rng(0)
    boot = np.array([contrasts([r for h in rng.choice(hours, len(hours)) for r in by_hour[h]]) for _ in range(1000)])
    names = ("(+5) - (-5), CSI 20", "(+5) - (-5), CSI 30", "(+5) - (-5), r",
             "(-5) - (+10), CSI 20", "(-5) - (+10), CSI 30", "(-5) - (+10), r")
    print(f"differences, 95% from a block bootstrap over {len(hours)} hours:")
    for name, value, b in zip(names, contrasts(paired), boot.T):
        print(f"{name}: {value:+.3f} ({np.percentile(b, 2.5):+.3f} to {np.percentile(b, 97.5):+.3f})")
    print("CSI 20 per day:")
    for day in sorted({r["time"][:10] for r in paired}):
        rs = [r for r in paired if r["time"][:10] == day]
        print(f"{day} ({len(rs)} times): " + ", ".join(f"{int(lag):+d}: {scores(rs, lag)['csi20']:.3f}" for lag in CORE))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--processes", type=int, default=8)
    ap.add_argument("--summary", action="store_true", help="only print the tables of the records written")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "lag_records.json"
    if not args.summary:
        ody = sorted(p for p in glob.glob(str(DATA_DIR / "odyssey_bel" / "2024" / "07" / "*.h5"))
                     if FIRST <= label_time(p) <= LAST)
        cirrus = {label_time(p).isoformat(): p
                  for p in glob.glob(str(DATA_DIR / "cirrus_bel" / "2024" / "07" / "*DBZH.h5"))
                  if FIRST - dt.timedelta(minutes=15) <= label_time(p) <= LAST + dt.timedelta(minutes=15)}
        with ProcessPoolExecutor(args.processes) as ex:
            records = list(ex.map(one_time, [(p, cirrus) for p in ody], chunksize=4))
        path.write_text(json.dumps(records), encoding="utf-8")
    summary(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
