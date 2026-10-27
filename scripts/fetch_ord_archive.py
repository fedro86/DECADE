"""Scarica compositi OPERA dal bucket pubblico ORD (openradar-archive, CC BY 4.0).

Struttura del bucket: AAAA/MM/GG/OPERA/COMP/OPERA@AAAAMMGGTHHMM@0@<prodotto>.h5
  ODYSSEY (fino al 5/7/2024): DBZH_QIND.h5, 2 km / 15 min
  CIRRUS  (dall'1/7/2024):    DBZH.h5,      1 km / 5 min

Esempio:
  uv run python scripts/fetch_ord_archive.py --product DBZH_QIND \
      --start 2024-07-01 --end 2024-07-06 --out data/odyssey
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BUCKET = "https://s3.waw3-1.cloudferro.com/openradar-archive"


def list_keys(prefix: str) -> list[tuple[str, int]]:
    keys, token = [], None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        with urllib.request.urlopen(f"{BUCKET}/?{urllib.parse.urlencode(q)}", timeout=120) as r:
            xml = r.read().decode()
        keys += [(k, int(s)) for k, s in re.findall(r"<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>", xml)]
        m = re.search(r"<NextContinuationToken>([^<]+)<", xml)
        if not m:
            return keys
        token = m.group(1)


def fetch(key: str, size: int, out_dir: str) -> int:
    path = os.path.join(out_dir, os.path.basename(key))
    if os.path.exists(path) and os.path.getsize(path) == size:
        return 0
    tmp = path + ".part"
    urllib.request.urlretrieve(f"{BUCKET}/{urllib.parse.quote(key)}", tmp)
    os.replace(tmp, path)
    return size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", required=True, help="suffisso del file, es. DBZH_QIND (ODYSSEY) o DBZH (CIRRUS)")
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat, help="escluso")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    todo, d = [], a.start
    while d < a.end:
        suffix = f"@{a.product}.h5"
        todo += [(k, s) for k, s in list_keys(d.strftime("%Y/%m/%d/OPERA/COMP/")) if k.endswith(suffix)]
        d += dt.timedelta(days=1)
    print(f"{len(todo)} file, {sum(s for _, s in todo) / 1e9:.2f} GB")
    if a.dry_run:
        return
    with ThreadPoolExecutor(a.workers) as ex:
        got = sum(ex.map(lambda ks: fetch(ks[0], ks[1], a.out), todo))
    print(f"scaricati {got / 1e9:.2f} GB in {a.out}")


if __name__ == "__main__":
    main()
