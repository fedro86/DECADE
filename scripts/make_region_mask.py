"""Maschera booleana di un paese sulla griglia di un composito OPERA (es. CIRRUS 1 km).

I confini vengono da Natural Earth (admin 0, 1:10m, dominio pubblico). La griglia
si ricava dai metadati `where` del file di riferimento: projdef, angolo UL,
xscale/yscale, xsize/ysize (riga 0 = nord).

Esempio:
  uv run python scripts/make_region_mask.py --ref data/cirrus/OPERA@20240702T1205@0@DBZH.h5 \
      --country BEL --buffer-km 0 --out data/mask_BEL_1km.npy
"""
from __future__ import annotations

import argparse
import io
import os
import urllib.request
import zipfile

import numpy as np

from opera_ds.odim_io import read_odim_composite

NE_URL = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"


def country_geometry(iso3: str, cache_dir: str):
    import shapefile  # pyshp
    from shapely.geometry import shape

    path = os.path.join(cache_dir, "ne_10m_admin_0_countries.zip")
    if not os.path.exists(path):
        os.makedirs(cache_dir, exist_ok=True)
        urllib.request.urlretrieve(NE_URL, path)
    with zipfile.ZipFile(path) as z:
        r = shapefile.Reader(shp=io.BytesIO(z.read("ne_10m_admin_0_countries.shp")),
                             dbf=io.BytesIO(z.read("ne_10m_admin_0_countries.dbf")))
        fields = [f[0] for f in r.fields[1:]]
        for sr in r.iterShapeRecords():
            rec = dict(zip(fields, sr.record))
            if iso3 in (rec.get("ADM0_A3"), rec.get("ISO_A3")):
                return shape(sr.shape.__geo_interface__)
    raise KeyError(f"paese {iso3} non trovato")


def grid_mask(where: dict, geom_lonlat, buffer_km: float = 0.0) -> np.ndarray:
    from pyproj import Proj
    from shapely import contains_xy, transform

    p = Proj(where["projdef"])
    g = transform(geom_lonlat, lambda c: np.column_stack(p(c[:, 0], c[:, 1])))
    if buffer_km:
        g = g.buffer(buffer_km * 1000.0)
    x0, y0 = p(float(where["UL_lon"]), float(where["UL_lat"]))   # angolo UL del pixel (0, 0)
    sx, sy = float(where["xscale"]), float(where["yscale"])
    nx, ny = int(where["xsize"]), int(where["ysize"])
    minx, miny, maxx, maxy = g.bounds
    c0, c1 = max(int((minx - x0) // sx) - 1, 0), min(int((maxx - x0) // sx) + 2, nx)
    r0, r1 = max(int((y0 - maxy) // sy) - 1, 0), min(int((y0 - miny) // sy) + 2, ny)
    xc = x0 + (np.arange(c0, c1) + 0.5) * sx
    yc = y0 - (np.arange(r0, r1) + 0.5) * sy
    X, Y = np.meshgrid(xc, yc)
    m = np.zeros((ny, nx), bool)
    m[r0:r1, c0:c1] = contains_xy(g, X, Y)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, help="composito ODIM di riferimento per la griglia")
    ap.add_argument("--country", default="BEL", help="codice ISO a 3 lettere")
    ap.add_argument("--buffer-km", type=float, default=0.0)
    ap.add_argument("--cache-dir", default="data/naturalearth")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    where = read_odim_composite(a.ref).where
    m = grid_mask(where, country_geometry(a.country, a.cache_dir), a.buffer_km)
    rows, cols = np.nonzero(m)
    np.save(a.out, m)
    print(f"{a.out}: {m.sum()} pixel, righe {rows.min()}-{rows.max()}, colonne {cols.min()}-{cols.max()}")


if __name__ == "__main__":
    main()
