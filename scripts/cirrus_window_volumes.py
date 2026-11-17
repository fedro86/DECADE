"""Does CIRRUS take the maximum over the volumes of one radar in its time window? (H3, #20; test 1 of the review of
#96, 17/11/2026)

The CIRRUS frame NT has the window (NT-10, NT] ([data.md](../docs/data.md), *Time windows for the label NT*), so
the Belgian radars, with a volume every 5 min, have two volumes in it. For each Belgian radar (bejab, bewid, behel)
and each CIRRUS frame NT of a day:

- the radar's volumes are taken from `data/opera_single/<YYYYMMDD>/<node>/` (the PVOL of the task starting at 0.3 deg,
  `DBZH`); a volume is in the window if its scans, `how/startepochs` to `how/endepochs`, lie in (NT-10, NT];
- each volume is projected onto the CIRRUS 1 km grid within 5-60 km of the radar: pixel centre -> azimuth and
  ground distance (WGS84) -> for each elevation the bin hit by the beam with a 4/3 Earth radius, nearest bin; the
  volume gives the maximum over its elevations;
- E is the earliest volume in the window, L the latest, P the volume just before the window.

Scores, per ring of distance from the radar (5-20, 20-40, 40-60 km):

- **left**: pixels where E >= L + 10 dB and E >= 15 dBZ (rain that has left during the window): count, and how many
  have CIRRUS closer to E than to L. A maximum over both volumes keeps this rain, so CIRRUS should be closer to E.
- **arrived**: L >= E + 10 dB and L >= 15 dBZ: how many have CIRRUS closer to L than to E (both rules agree here).
- **control**: P >= L + 10 dB, P >= 15 dBZ and E < L + 10 dB (rain that left before the window): how many have
  CIRRUS closer to P than to L. P is not in the window, so this share is what "closer" gives without the volume
  being used (other radars, persistence of the rain, OPERA processing).
- for the three candidates max(E, L), L and E, on the pixels where CIRRUS or E or L is >= 10 dBZ: correlation with
  CIRRUS, median and mean absolute difference (candidate - CIRRUS, dB).

Volumes for a few hours of a day can be fetched from the public bucket with `opera_ds.ord.list_keys` and `fetch`
(`YYYY/MM/DD/BE/<node>/PVOL/<node>@<time>@0.3_...@DBZH.h5`), about 0.3-0.9 MB per volume.

  uv run python scripts/cirrus_window_volumes.py --days 2025-01-05 2025-08-28 2025-08-31 \
      --out results/h3_level/window_test1.csv
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import re

import h5py
import numpy as np
import pandas as pd
from pyproj import Geod, Proj

from opera_ds.odim_io import read_odim_composite
from opera_ds.paths import DATA_DIR

AE = 4.0 / 3.0 * 6371000.0
RMIN, RMAX = 5e3, 60e3
RINGS = {"05-20": (5e3, 20e3), "20-40": (20e3, 40e3), "40-60": (40e3, 60e3)}
GAP, WET = 10.0, 15.0
RADARS = ("bejab", "bewid", "behel")
GEOD = Geod(ellps="WGS84")


def epoch(v) -> dt.datetime:
    return dt.datetime.fromtimestamp(int(v), dt.timezone.utc).replace(tzinfo=None)


def read_volume(path):
    """Radar site, first and last scan time, and the sweeps (elevation, range bins, DBZH in dBZ; undetect -32)."""
    with h5py.File(path, "r") as f:
        site = {k: float(f["where"].attrs[k]) for k in ("lon", "lat", "height")}
        t0, t1 = epoch(f["how"].attrs["startepochs"]), epoch(f["how"].attrs["endepochs"])
        sweeps = []
        for name in sorted((k for k in f if k.startswith("dataset")), key=lambda s: int(s[7:])):
            g = f[name]
            w, a = g["where"].attrs, g["data1/what"].attrs
            raw = g["data1/data"][()].astype(np.float32)
            v = raw * float(a["gain"]) + float(a["offset"])
            v[raw == float(a["undetect"])] = -32.0
            v[raw == float(a["nodata"])] = np.nan
            sweeps.append(dict(el=float(w["elangle"]), rscale=float(w["rscale"]), rstart=float(w["rstart"]) * 1000.0,
                               data=v))
    return site, t0, t1, sweeps


class Geometry:
    """Pixels of the CIRRUS crop within RMAX of one radar, and their (ray, bin) for each sweep layout."""

    def __init__(self, where, site):
        p = Proj(where["projdef"])
        sx, sy = float(where["xscale"]), float(where["yscale"])
        xu, yu = p(float(where["UL_lon"]), float(where["UL_lat"]))
        ny, nx = int(where["ysize"]), int(where["xsize"])
        xr, yr = p(site["lon"], site["lat"])
        c, r, n = int((xr - xu) / sx), int((yu - yr) / sy), int(RMAX / sx) + 2
        self.rows = slice(max(r - n, 0), min(r + n, ny))
        self.cols = slice(max(c - n, 0), min(c + n, nx))
        rr, cc = np.mgrid[self.rows, self.cols]
        lon, lat = p(xu + (cc + 0.5) * sx, yu - (rr + 0.5) * sy, inverse=True)
        az, _, s = GEOD.inv(np.full(lon.shape, site["lon"]), np.full(lon.shape, site["lat"]), lon, lat)
        self.az, self.s = np.mod(az, 360.0), s
        self.mask = (s >= RMIN) & (s <= RMAX)
        self._cache: dict = {}

    def sample(self, sw):
        key = (sw["el"], sw["rscale"], sw["rstart"], sw["data"].shape)
        if key not in self._cache:
            g = self.s / AE
            r = AE * np.sin(g) / np.cos(np.deg2rad(sw["el"]) + g)  # slant range of the beam over this ground distance
            ib = np.floor((r - sw["rstart"]) / sw["rscale"]).astype(int)
            nr, nb = sw["data"].shape
            ia = np.floor(self.az * nr / 360.0).astype(int) % nr  # ray i covers [i, i+1) deg (ODIM order)
            ok = (ib >= 0) & (ib < nb)
            self._cache[key] = (ia, np.where(ok, ib, 0), ok)
        ia, ib, ok = self._cache[key]
        return np.where(ok, sw["data"][ia, ib], np.nan)

    def project(self, sweeps):
        st = np.stack([self.sample(sw) for sw in sweeps])
        fin = np.isfinite(st)
        return np.where(fin.any(0), np.where(fin, st, -np.inf).max(0), np.nan)


def closer(c, x, y, m):
    return int((np.abs(c - x) < np.abs(c - y))[m].sum())


def day_rows(day: dt.datetime) -> list[dict]:
    cfiles = {dt.datetime.strptime(re.search(r"@(\d{8}T\d{4})@", p).group(1), "%Y%m%dT%H%M"): p for p in
              glob.glob(str(DATA_DIR / "cirrus_bel" / f"{day:%Y}" / f"{day:%m}" / f"OPERA@{day:%Y%m%d}T*@0@DBZH.h5"))}
    rows = []
    for radar in RADARS:
        paths = sorted(glob.glob(str(DATA_DIR / "opera_single" / f"{day:%Y%m%d}" / radar / "*@0.3_*@DBZH.h5")))
        vols = [read_volume(p) for p in paths]
        if not vols:
            continue
        site, g = vols[0][0], None
        for nt, cp in sorted(cfiles.items()):
            lo = nt - dt.timedelta(minutes=10)
            inside = [v for v in vols if v[1] > lo and v[2] <= nt]
            before = [v for v in vols if v[2] <= lo and v[1] > lo - dt.timedelta(minutes=5)]
            if len(inside) != 2 or len(before) != 1:
                continue
            fr = read_odim_composite(cp, "DBZH")
            g = g or Geometry(fr.where, site)
            cir = fr.to_field(-32.0)[g.rows, g.cols]
            E, L = (g.project(v[3]) for v in inside)
            P = g.project(before[0][3])
            ok = g.mask & np.isfinite(cir) & np.isfinite(E) & np.isfinite(L) & np.isfinite(P)
            left = ok & (E >= L + GAP) & (E >= WET)
            arrived = ok & (L >= E + GAP) & (L >= WET)
            ctrl = ok & (P >= L + GAP) & (P >= WET) & (E < L + GAP)
            wet = ok & ((cir >= 10) | (E >= 10) | (L >= 10))
            base = dict(day=f"{day:%Y-%m-%d}", radar=radar, nt=nt, n_wet=int(wet.sum()))
            if wet.sum() > 50:
                for k, x in (("max", np.fmax(E, L)), ("latest", L), ("earliest", E)):
                    d = (x - cir)[wet]
                    base.update({f"corr_{k}": float(np.corrcoef(x[wet], cir[wet])[0, 1]),
                                 f"median_diff_{k}": float(np.median(d)), f"mad_{k}": float(np.abs(d).mean())})
            for ring, (a, b) in RINGS.items():
                R = (g.s >= a) & (g.s < b)
                rows.append(dict(base, ring=ring,
                                 n_left=int((left & R).sum()), left_closer_E=closer(cir, E, L, left & R),
                                 n_arrived=int((arrived & R).sum()), arrived_closer_L=closer(cir, L, E, arrived & R),
                                 n_control=int((ctrl & R).sum()), control_closer_P=closer(cir, P, L, ctrl & R)))
        print(f"{day:%Y-%m-%d} {radar}: {len(vols)} volumes", flush=True)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for s in a.days:
        rows += day_rows(dt.datetime.strptime(s, "%Y-%m-%d"))
    pd.DataFrame(rows).to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
