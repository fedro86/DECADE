"""Scarica solo un'area dei compositi OPERA leggendo a pezzi i GeoTIFF del bucket ORD.

I GeoTIFF del bucket pubblico sono tiled (512 x 512, deflate) e contengono gli stessi
valori degli HDF5 (verificato pixel per pixel su 2013, 2018, 2024), con undetect
codificato come NaN. La loro georeferenziazione e' sfasata di mezzo pixel, quindi la
griglia si prende da un HDF5 di riferimento (`--ref`) e la finestra si legge per indici.

Ogni frame diventa un HDF5 ritagliato leggibile da `read_odim_composite`, con lo
stesso nome del file originale e l'offset del ritaglio in `where` (`crop_row0`, ...).
Il download riprende da dove si era fermato; i fallimenti finiscono in `failed.txt`.

Esempio (Belgio + 350 km: 200 di area di campionamento + 150 di contesto per il moto):
  uv run python scripts/fetch_cog_crop.py --product DBZH_QIND \
      --ref "data/odyssey/OPERA@20240702T1200@0@DBZH_QIND.h5" \
      --bbox 2.5 49.45 6.45 51.55 --buffer-km 350 \
      --start 2012-09-01 --end 2024-07-06 --out data/odyssey_bel --threads 32
  uv run python scripts/fetch_cog_crop.py --product DBZH \
      --ref "data/cirrus/OPERA@20240701T0720@0@DBZH.h5" \
      --bbox 2.5 49.45 6.45 51.55 --buffer-km 350 \
      --start 2024-07-01 --end 2026-10-27 --out data/cirrus_bel --threads 32
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import h5py
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from opera_ds.odim_io import bbox_extent, crop_where, extent_window, read_odim_composite  # noqa: E402
from fetch_ord_archive import BUCKET, list_keys  # noqa: E402

GDAL_ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tiff",
                GDAL_HTTP_MULTIRANGE="YES", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="FALSE",
                CPL_VSIL_CURL_NON_CACHED="/vsicurl/", GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2")
NODATA, UNDETECT = -9999000.0, -8888000.0
WHAT_KEYS = ("date", "time", "source", "object", "version")
DS_WHAT_KEYS = ("product", "quantity", "startdate", "starttime", "enddate", "endtime")


def write_crop(path, data, tags, where, quantity):
    """HDF5 ODIM 2.0 minimale: valori float32, nodata/undetect come negli originali.
    I tag dei GeoTIFF CIRRUS non hanno `quantity`: in quel caso si usa quella data."""
    tmp = path + ".part"
    with h5py.File(tmp, "w") as f:
        f.attrs["Conventions"] = np.bytes_("ODIM_H5/V2_0")
        w = f.create_group("what")
        for k in WHAT_KEYS:
            if k in tags:
                w.attrs[k] = np.bytes_(tags[k])
        wh = f.create_group("where")
        for k, v in where.items():
            wh.attrs[k] = np.bytes_(v) if isinstance(v, str) else v
        how = f.create_group("how")
        how.attrs["nodes"] = np.bytes_(tags.get("nodes", ""))
        if "comment" in tags:
            how.attrs["comment"] = np.bytes_(tags["comment"])
        how.attrs["crop_source"] = np.bytes_("GeoTIFF ORD, lettura a pezzi (fetch_cog_crop.py)")
        d = f.create_group("dataset1/data1")
        d.create_dataset("data", data=data, compression="gzip", compression_opts=4, shuffle=True,
                         chunks=data.shape)
        dw = f["dataset1"].create_group("what")
        for k in DS_WHAT_KEYS:
            if k in tags:
                dw.attrs[k] = np.bytes_(tags[k])
        if "quantity" not in tags:
            dw.attrs["quantity"] = np.bytes_(quantity)
        dw.attrs.update({"gain": 1.0, "offset": 0.0, "nodata": NODATA, "undetect": UNDETECT})
    os.replace(tmp, path)


def fetch_one(key, window, where_crop, out_dir, quantity):
    import rasterio
    from rasterio.windows import Window

    name = os.path.basename(key).replace(".tiff", ".h5")
    sub = os.path.join(out_dir, key[:7])               # AAAA/MM
    path = os.path.join(sub, name)
    if os.path.exists(path):
        return 0
    os.makedirs(sub, exist_ok=True)
    r0, r1, c0, c1 = window
    with rasterio.Env(**GDAL_ENV):
        with rasterio.open(f"/vsicurl/{BUCKET}/{key}") as ds:
            if (ds.height, ds.width) != (int(where_crop["full_ysize"]), int(where_crop["full_xsize"])):
                raise ValueError(f"griglia inattesa {ds.height}x{ds.width}")
            a = ds.read(1, window=Window(c0, r0, c1 - c0, r1 - r0))
            tags = ds.tags()
    a = np.where(np.isnan(a), UNDETECT, a).astype(np.float32)
    write_crop(path, a, tags, where_crop, quantity)
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", default="DBZH_QIND")
    ap.add_argument("--ref", required=True, help="HDF5 del prodotto sulla griglia intera, per i metadati 'where'")
    ap.add_argument("--bbox", type=float, nargs=4, required=True, metavar=("LON_MIN", "LAT_MIN", "LON_MAX", "LAT_MAX"))
    ap.add_argument("--buffer-km", type=float, default=0.0)
    ap.add_argument("--align-m", type=float, default=2000.0,
                    help="allineamento del ritaglio; 2000 = stessa area per ODYSSEY e CIRRUS")
    ap.add_argument("--quantity", default="DBZH", help="se manca nei tag del GeoTIFF (CIRRUS)")
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat, help="escluso")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    full = read_odim_composite(a.ref, a.quantity).where
    ext = bbox_extent(full, a.bbox, a.buffer_km, align_m=a.align_m)
    window = extent_window(full, ext)
    where_crop = crop_where(full, window)
    print(f"finestra (righe, colonne) {window}: {(window[1]-window[0])} x {(window[3]-window[2])} px", flush=True)
    os.makedirs(a.out, exist_ok=True)
    failed_path = os.path.join(a.out, "failed.txt")
    t_start, n_ok, n_skip, n_fail = time.time(), 0, 0, 0
    d = a.start
    with ThreadPoolExecutor(a.threads) as ex, open(failed_path, "a") as failed:
        while d < a.end:
            # un mese alla volta: elenco dei file, poi download in parallelo
            m_end = min((d.replace(day=1) + dt.timedelta(days=32)).replace(day=1), a.end)
            keys = []
            while d < m_end:
                keys += [k for k, _ in list_keys(d.strftime("%Y/%m/%d/OPERA/COMP/"))
                         if k.endswith(f"@{a.product}.tiff")]
                d += dt.timedelta(days=1)
            if a.dry_run:
                print(f"{m_end:%Y-%m}: {len(keys)} file")
                continue
            futs = {ex.submit(fetch_one, k, window, where_crop, a.out, a.quantity): k for k in keys}
            for fu, k in futs.items():
                try:
                    if fu.result():
                        n_ok += 1
                    else:
                        n_skip += 1
                except Exception as e:
                    n_fail += 1
                    failed.write(f"{k}\t{e}\n")
                    failed.flush()
            el = time.time() - t_start
            print(f"{(m_end - dt.timedelta(days=1)):%Y-%m}: {len(keys)} file | totale scaricati {n_ok}, "
                  f"gia' presenti {n_skip}, falliti {n_fail} | {el/60:.1f} min, {n_ok/max(el, 1):.1f} file/s",
                  flush=True)


if __name__ == "__main__":
    main()
