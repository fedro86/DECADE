"""Accesso al bucket pubblico ORD (openradar-archive, CC BY 4.0, nessuna credenziale).

Chiavi: AAAA/MM/GG/OPERA/COMP/OPERA@AAAAMMGGTHHMM@0@<prodotto>.{h5,tiff}
  ODYSSEY (fino al 5/7/2024): DBZH_QIND, QIND_RATE, ACRR_QIND - 2 km / 15 min
  CIRRUS  (dall'1/7/2024):    DBZH                            - 1 km / 5 min
  NIMBUS  (dal 5/7/2024):     RATE, ACRR                      - 2 km / 15 min
"""
from __future__ import annotations

import datetime as dt
import os
import re
import urllib.parse
import urllib.request

BUCKET = "https://s3.waw3-1.cloudferro.com/openradar-archive"


def ord_key(t: dt.datetime, product: str, ext: str = "h5") -> str:
    """Chiave del composito `product` (es. 'DBZH_QIND', 'DBZH') all'istante t."""
    return f"{t:%Y/%m/%d}/OPERA/COMP/OPERA@{t:%Y%m%dT%H%M}@0@{product}.{ext}"


def list_keys(prefix: str) -> list[tuple[str, int]]:
    """(chiave, dimensione in byte) di tutti gli oggetti con il prefisso dato."""
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


def fetch(key: str, size: int | None, out_dir: str) -> int:
    """Scarica `key` in out_dir (salta se c'e' gia' con la stessa dimensione).
    Restituisce i byte scaricati."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, os.path.basename(key))
    if os.path.exists(path) and (size is None or os.path.getsize(path) == size):
        return 0
    tmp = path + ".part"
    urllib.request.urlretrieve(f"{BUCKET}/{urllib.parse.quote(key)}", tmp)
    os.replace(tmp, path)
    return os.path.getsize(path)


def download(t: dt.datetime, product: str, out_dir: str) -> str:
    """Scarica (se manca) il composito `product` all'istante t e ne restituisce il percorso."""
    key = ord_key(t, product)
    fetch(key, None, out_dir)
    return os.path.join(out_dir, os.path.basename(key))
