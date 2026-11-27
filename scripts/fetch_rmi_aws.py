"""Hourly precipitation of the RMI automatic weather stations (AWS), Belgium, from the RMI open-data WFS.

Licence: CC BY 4.0 (RMI open-data catalogue, record RMI_DATASET_AWS_1HOUR; terms at
https://opendata.meteo.be/termsandconditions). Source to cite: Royal Meteorological Institute of Belgium (RMI).

One request per station and year; only the station code, the time stamp (UTC), the hourly precipitation and
the RMI validation flag of precipitation are kept. Output: <DATA_DIR>/rmi_aws/aws_1hour_precip.npz with
`code`, `time` (datetime64[s], UTC, as published), `precip` (mm, NaN when missing) and `validated` (bool), plus
the station list `stations.json`. Years already fetched are kept in <DATA_DIR>/rmi_aws/parts/ and skipped.

    uv run python scripts/fetch_rmi_aws.py --first 2012 --last 2025
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import time
import urllib.parse
import urllib.request

import numpy as np

from opera_ds.paths import DATA_DIR

WFS = "https://opendata.meteo.be/service/aws/wfs"


def get(params: dict, tries: int = 5) -> bytes:
    url = WFS + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return r.read()
        except OSError:
            if k == tries - 1:
                raise
            time.sleep(10 * (k + 1))
    raise RuntimeError("unreachable")


def stations() -> list[dict]:
    d = json.loads(get(dict(service="WFS", version="2.0.0", request="GetFeature", typeName="aws:aws_station",
                            outputFormat="application/json")))
    return [dict(f["properties"], lon=f["geometry"]["coordinates"][0], lat=f["geometry"]["coordinates"][1])
            for f in d["features"]]


def year(code: int, y: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = get(dict(service="WFS", version="2.0.0", request="GetFeature", typeNames="aws:aws_1hour",
                   outputFormat="csv", propertyName="code,timestamp,precip_quantity,qc_flags",
                   CQL_FILTER=f"code={code} AND timestamp DURING {y}-01-01T00:00:00Z/{y + 1}-01-01T00:00:00Z"))
    t, p, v = [], [], []
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8"))):
        t.append(np.datetime64(row["timestamp"].replace("Z", ""), "s"))
        p.append(float(row["precip_quantity"]) if row["precip_quantity"] not in ("", None) else np.nan)
        flags = json.loads(row["qc_flags"]) if row.get("qc_flags") else {}
        v.append(bool(flags.get("validated", {}).get("PRECIP_QUANTITY", False)))
    order = np.argsort(t)
    return np.array(t)[order], np.array(p)[order], np.array(v)[order]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", type=int, default=2012)
    ap.add_argument("--last", type=int, default=2025)
    ap.add_argument("--codes", type=int, nargs="*", help="only these stations (several processes can share the work)")
    a = ap.parse_args()
    out = DATA_DIR / "rmi_aws"
    parts = out / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    st = stations()
    (out / "stations.json").write_text(json.dumps(st, indent=1), encoding="utf-8")
    for s in st:
        if a.codes and s["code"] not in a.codes:
            continue
        for y in range(a.first, a.last + 1):
            f = parts / f"{s['code']}_{y}.npz"
            if f.exists() or np.datetime64(s["date_begin"][:10]) >= np.datetime64(f"{y + 1}-01-01"):
                continue
            t, p, v = year(s["code"], y)
            np.savez_compressed(f, time=t, precip=p, validated=v)
            print(f"{s['code']} {s['name']:22s} {y}: {t.size} hours, {np.isnan(p).sum()} missing,"
                  f" {(~v).sum()} not validated", flush=True)
    C, T, P, V = [], [], [], []
    for f in sorted(parts.glob("*.npz")):
        z = np.load(f)
        C.append(np.full(z["time"].size, int(f.stem.split("_")[0])))
        T.append(z["time"]); P.append(z["precip"]); V.append(z["validated"])
    np.savez_compressed(out / "aws_1hour_precip.npz", code=np.concatenate(C), time=np.concatenate(T),
                        precip=np.concatenate(P), validated=np.concatenate(V))
    print("written", out / "aws_1hour_precip.npz")


if __name__ == "__main__":
    main()
