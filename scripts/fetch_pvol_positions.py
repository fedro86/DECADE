"""Download one single-radar file per radar and per day from the public ORD bucket, to
read the radar position (`where`: lon, lat, height) of that day.

Used in notebooks/03-mr-cirrus-analysis.ipynb to draw the radars on the maps of the
January disagreements between Steiner and ECCO (review of #65): only to see whether a
ring is centred on a radar, not to compute anything.

Bucket layout: YYYY/MM/DD/<country>/<node>/{PVOL,SCAN}/<node>@YYYYMMDDTHHMM@<elevations>@<quantities>.h5
Some countries store volumes (PVOL, e.g. BE, NL), others single scans (SCAN, e.g. DE,
FR); every file carries the radar position. For each radar and day the smallest file
with DBZH among the first ones of the day is taken (tens of kB to about 2 MB).

Example:
  uv run python scripts/fetch_pvol_positions.py \
      --times-csv results/cirrus_analysis/selected_january_times.csv \
      --countries BE NL LU DE FR --out data/opera_pvol --dry-run
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import urllib.parse
import urllib.request

from opera_ds.ord import BUCKET, fetch


def _list(prefix: str, delimiter: str | None = None, max_keys: int = 1000) -> str:
    q = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
    if delimiter:
        q["delimiter"] = delimiter
    with urllib.request.urlopen(f"{BUCKET}/?{urllib.parse.urlencode(q)}", timeout=120) as r:
        return r.read().decode()


def nodes(day: dt.date, country: str) -> list[str]:
    """Radar nodes with data in the bucket for one country and day."""
    xml = _list(f"{day:%Y/%m/%d}/{country}/", delimiter="/")
    return [p.rstrip("/").split("/")[-1] for p in re.findall(r"<Prefix>([^<]+/)</Prefix>", xml)
            if p.count("/") == 5]


def first_volume(day: dt.date, country: str, node: str) -> tuple[str, int] | None:
    """(key, size) of the smallest file with DBZH among the first 50 of the day for a node
    (volumes or single scans), or None."""
    xml = _list(f"{day:%Y/%m/%d}/{country}/{node}/", max_keys=50)
    found = [(k, int(s)) for k, s in re.findall(r"<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>", xml)
             if "DBZH" in k.rsplit("@", 1)[-1] and ("/PVOL/" in k or "/SCAN/" in k)]
    return min(found, key=lambda v: v[1]) if found else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--times-csv", required=True, help="CSV with a 'time' column (ISO); one volume per day")
    ap.add_argument("--countries", nargs="+", required=True, help="country folders of the bucket, e.g. BE NL")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true", help="list files and sizes, download nothing")
    a = ap.parse_args()

    with open(a.times_csv, encoding="utf-8") as f:
        days = sorted({dt.datetime.fromisoformat(r["time"]).date() for r in csv.DictReader(f)})
    todo = []
    for day in days:
        for c in a.countries:
            for n in nodes(day, c):
                v = first_volume(day, c, n)
                if v:
                    todo.append((day, c, n, *v))
                else:
                    print(f"{day} {c}/{n}: no DBZH volume")
    for day, c, n, k, s in todo:
        print(f"{day} {c}/{n}: {os.path.basename(k)} ({s / 1e6:.2f} MB)")
    print(f"{len(days)} days, {len(todo)} files, {sum(t[4] for t in todo) / 1e6:.1f} MB")
    if a.dry_run:
        return
    for day, c, n, k, s in todo:
        fetch(k, s, os.path.join(a.out, f"{day:%Y%m%d}"))
    print(f"downloaded into {a.out}")


if __name__ == "__main__":
    main()
