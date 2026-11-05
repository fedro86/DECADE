"""Lettura/scrittura di compositi OPERA in formato ODIM HDF5 e indicizzazione dei file.

ODYSSEY (fino al 2024): 2 km, 1900x2200, ODIM 2.0 (quantity spesso a livello dataset).
CIRRUS (dal 2024):      1 km, 3800x4400, ODIM 2.4 (quantity a livello data).
Stessa estensione e stessa proiezione LAEA: la griglia a 1 km e' esattamente la
griglia a 2 km con ogni pixel diviso in 2x2.
"""
from __future__ import annotations

import datetime as dt
import glob
import os
import re
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Frame:
    """Un composito decodificato.

    values   : float32, valori fisici (dBZ); privi di significato dove ~coverage o undetect
    coverage : bool, True = pixel coperto da almeno un radar (non 'nodata')
    undetect : bool, True = coperto ma senza eco
    """
    time: dt.datetime
    values: np.ndarray
    coverage: np.ndarray
    undetect: np.ndarray
    where: dict = field(default_factory=dict)
    path: str = ""
    attrs: dict = field(default_factory=dict)   # metadati di produzione (es. alpha), in dataset1/how

    def to_field(self, floor: float, threshold: float | None = None) -> np.ndarray:
        """Campo pronto per l'elaborazione: undetect e valori < floor -> floor.
        Se `threshold` e' dato, anche gli echi < threshold vengono portati a floor.
        I pixel non coperti restano NaN."""
        f = np.where(self.undetect, floor, self.values).astype(np.float32)
        lim = floor if threshold is None else max(floor, threshold)
        f[f < lim] = floor
        f[~self.coverage] = np.nan
        return f


def _attrs(group) -> dict:
    out = {}
    for k, v in group.attrs.items():
        if isinstance(v, bytes):
            v = v.decode("utf-8", "ignore")
        elif isinstance(v, np.ndarray) and v.size == 1:
            v = v.item()
            if isinstance(v, bytes):
                v = v.decode("utf-8", "ignore")
        out[k] = v
    return out


def _parse_odim_time(what: dict) -> dt.datetime | None:
    d, t = what.get("date"), what.get("time")
    if not d or not t:
        return None
    return dt.datetime.strptime(f"{d}{str(t)[:6]}", "%Y%m%d%H%M%S")


def bbox_extent(where: dict, bbox_lonlat, buffer_km: float = 0.0,
                align_m: float = 2000.0) -> tuple[float, float, float, float]:
    """Estensione di ritaglio (x_off, y_off, width, height) in metri dall'angolo UL della
    griglia, che contiene il bbox (lon_min, lat_min, lon_max, lat_max) piu' un buffer.
    I valori sono multipli di `align_m`: con 2000 m il ritaglio resta allineato 2:1
    tra la griglia a 2 km e quella a 1 km."""
    from pyproj import Proj

    where = full_grid_where(where)
    p = Proj(where["projdef"])
    x_ul, y_ul = p(float(where["UL_lon"]), float(where["UL_lat"]))
    lo0, la0, lo1, la1 = bbox_lonlat
    lon = np.r_[np.linspace(lo0, lo1, 50), np.full(50, lo1), np.linspace(lo1, lo0, 50), np.full(50, lo0)]
    lat = np.r_[np.full(50, la0), np.linspace(la0, la1, 50), np.full(50, la1), np.linspace(la1, la0, 50)]
    x, y = p(lon, lat)
    b = buffer_km * 1000.0
    x0 = max(np.floor((x.min() - b - x_ul) / align_m) * align_m, 0.0)
    y0 = max(np.floor((y_ul - y.max() - b) / align_m) * align_m, 0.0)
    x1 = min(np.ceil((x.max() + b - x_ul) / align_m) * align_m, int(where["xsize"]) * float(where["xscale"]))
    y1 = min(np.ceil((y_ul - y.min() + b) / align_m) * align_m, int(where["ysize"]) * float(where["yscale"]))
    return float(x0), float(y0), float(x1 - x0), float(y1 - y0)


def extent_window(where: dict, extent) -> tuple[int, int, int, int]:
    """(r0, r1, c0, c1) in pixel della griglia descritta da `where`."""
    sx, sy = float(where["xscale"]), float(where["yscale"])
    x0, y0, w, h = extent
    idx = [y0 / sy, (y0 + h) / sy, x0 / sx, (x0 + w) / sx]
    if any(abs(v - round(v)) > 1e-6 for v in idx):
        raise ValueError(f"estensione {extent} non allineata alla griglia ({sx} x {sy} m)")
    return tuple(int(round(v)) for v in idx)


CROP_KEYS = ("crop_row0", "crop_col0", "full_xsize", "full_ysize", "full_UL_lon", "full_UL_lat")


def full_grid_where(where: dict) -> dict:
    """Metadati della griglia intera da cui proviene un ritaglio (o `where` stesso se
    non e' un ritaglio). Servono per esprimere estensioni e origini sempre sulla griglia
    intera, anche leggendo file gia' ritagliati."""
    if "crop_row0" not in where:
        return where
    w = {k: v for k, v in where.items() if k not in CROP_KEYS and not k[:2] in ("LL", "LR", "UR")}
    w.update(xsize=int(where["full_xsize"]), ysize=int(where["full_ysize"]),
             UL_lon=float(where["full_UL_lon"]), UL_lat=float(where["full_UL_lat"]))
    return w


def crop_where(where: dict, window) -> dict:
    """Metadati 'where' (dimensioni e angoli) della sotto-griglia `window`, relativa alla
    griglia descritta da `where`. Aggiunge (o aggiorna) l'offset del ritaglio sulla
    griglia intera (`crop_row0`, `crop_col0`) e i dati della griglia intera (`full_*`)."""
    from pyproj import Proj

    r0, r1, c0, c1 = window
    p = Proj(where["projdef"])
    sx, sy = float(where["xscale"]), float(where["yscale"])
    x_ul, y_ul = p(float(where["UL_lon"]), float(where["UL_lat"]))
    xa, xb = x_ul + c0 * sx, x_ul + c1 * sx
    ya, yb = y_ul - r0 * sy, y_ul - r1 * sy
    w = dict(where)
    if "crop_row0" not in where:
        w.update(crop_row0=0, crop_col0=0, full_xsize=int(where["xsize"]), full_ysize=int(where["ysize"]),
                 full_UL_lon=float(where["UL_lon"]), full_UL_lat=float(where["UL_lat"]))
    w["crop_row0"], w["crop_col0"] = int(w["crop_row0"]) + r0, int(w["crop_col0"]) + c0
    w["xsize"], w["ysize"] = c1 - c0, r1 - r0
    for c, (x, y) in {"UL": (xa, ya), "UR": (xb, ya), "LL": (xa, yb), "LR": (xb, yb)}.items():
        w[f"{c}_lon"], w[f"{c}_lat"] = (float(v) for v in p(x, y, inverse=True))
    return w


def read_odim_composite(path: str, quantity: str = "DBZH", extent=None) -> Frame:
    """Legge il primo campo `quantity` da un composito ODIM (2.0 o 2.4).
    extent: (x_off, y_off, width, height) in metri dall'angolo UL della griglia intera
    (vedi `bbox_extent`); se dato, legge solo quella finestra e aggiorna i metadati
    'where'. Funziona anche su file gia' ritagliati (con `crop_row0`/`crop_col0`),
    purche' la finestra stia dentro il ritaglio."""
    import h5py

    with h5py.File(path, "r") as f:
        root_what = _attrs(f["what"]) if "what" in f else {}
        root_where = _attrs(f["where"]) if "where" in f else {}
        for ds_name in sorted(k for k in f.keys() if k.startswith("dataset")):
            ds = f[ds_name]
            ds_what = _attrs(ds["what"]) if "what" in ds else {}
            ds_where = _attrs(ds["where"]) if "where" in ds else {}
            for d_name in sorted(k for k in ds.keys() if re.fullmatch(r"data\d+", k)):
                grp = ds[d_name]
                d_what = _attrs(grp["what"]) if "what" in grp else {}
                what = {**root_what, **ds_what, **d_what}
                if str(what.get("quantity", "")).strip() != quantity:
                    continue
                where = {**root_where, **ds_where}
                if extent is not None:
                    r0, r1, c0, c1 = extent_window(where, extent)          # griglia intera
                    dr, dc = int(where.get("crop_row0", 0)), int(where.get("crop_col0", 0))
                    win = (r0 - dr, r1 - dr, c0 - dc, c1 - dc)                # nel file
                    ny, nx = grp["data"].shape
                    if win[0] < 0 or win[2] < 0 or win[1] > ny or win[3] > nx:
                        raise ValueError(f"estensione {extent} fuori dal ritaglio del file {path}")
                    raw = grp["data"][win[0]:win[1], win[2]:win[3]]
                    where = crop_where(where, win)
                else:
                    raw = grp["data"][...]
                gain = float(what.get("gain", 1.0))
                offset = float(what.get("offset", 0.0))
                nodata = what.get("nodata", None)
                undet = what.get("undetect", None)

                if nodata is None:
                    coverage = np.ones(raw.shape, bool)
                elif np.issubdtype(raw.dtype, np.floating) and np.isnan(float(nodata)):
                    coverage = ~np.isnan(raw)
                else:
                    coverage = raw != nodata
                if np.issubdtype(raw.dtype, np.floating):
                    coverage &= np.isfinite(raw)
                undetect = (raw == undet) if undet is not None else np.zeros(raw.shape, bool)
                undetect &= coverage

                values = raw.astype(np.float32) * np.float32(gain) + np.float32(offset)
                time = _parse_odim_time(root_what) or _parse_odim_time(ds_what)
                return Frame(time=time, values=values, coverage=coverage, undetect=undetect,
                             where=where, path=path)
    raise KeyError(f"quantity {quantity!r} non trovata in {path}")


def write_odim_composite(path: str, frame: Frame, quantity: str = "DBZH",
                         gain: float = 0.01, offset: float = -50.0,
                         source: str = "ODYSSEY downscaled 1km/5min") -> None:
    """Scrive un composito ODIM 2.4 minimale (uint16, gzip)."""
    import h5py

    NODATA, UNDETECT = 65535, 0
    q = np.round((frame.values - offset) / gain)
    q = np.clip(q, 1, 65534).astype(np.uint16)
    q[frame.undetect] = UNDETECT
    q[~frame.coverage] = NODATA

    t = frame.time
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with h5py.File(path, "w") as f:
        f.attrs["Conventions"] = np.bytes_("ODIM_H5/V2_4")
        w = f.create_group("what")
        w.attrs.update({"object": np.bytes_("COMP"), "version": np.bytes_("H5rad 2.4"),
                        "date": np.bytes_(t.strftime("%Y%m%d")),
                        "time": np.bytes_(t.strftime("%H%M%S")),
                        "source": np.bytes_(source)})
        wh = f.create_group("where")
        for k, v in frame.where.items():
            wh.attrs[k] = np.bytes_(v) if isinstance(v, str) else v
        d = f.create_group("dataset1/data1")
        d.create_dataset("data", data=q, compression="gzip", compression_opts=4, chunks=True)
        dw = d.create_group("what")
        dw.attrs.update({"quantity": np.bytes_(quantity), "gain": gain, "offset": offset,
                         "nodata": float(NODATA), "undetect": float(UNDETECT)})
        if frame.attrs:
            how = f["dataset1"].create_group("how")
            for k, v in frame.attrs.items():
                how.attrs[k] = np.bytes_(v) if isinstance(v, str) else v
        ds_what = f["dataset1"].create_group("what")
        ds_what.attrs.update({"product": np.bytes_("MAX"),
                              "startdate": np.bytes_(t.strftime("%Y%m%d")),
                              "starttime": np.bytes_(t.strftime("%H%M%S")),
                              "enddate": np.bytes_(t.strftime("%Y%m%d")),
                              "endtime": np.bytes_(t.strftime("%H%M%S"))})


def refine_where(where_coarse: dict, factor: int) -> dict:
    """Aggiorna i metadati 'where' per la griglia raffinata (stessa estensione)."""
    w = dict(where_coarse)
    for k in ("xsize", "ysize", "full_xsize", "full_ysize", "crop_row0", "crop_col0"):
        if k in w:
            w[k] = int(w[k]) * factor
    for k in ("xscale", "yscale"):
        if k in w:
            w[k] = float(w[k]) / factor
    return w


def coarsen_where(where_fine: dict, factor: int) -> dict:
    """Inverse of `refine_where`: 'where' metadata of the grid `factor` times coarser
    with the same extent (corners unchanged). Sizes and crop offsets must be multiples
    of `factor`."""
    w = dict(where_fine)
    for k in ("xsize", "ysize", "full_xsize", "full_ysize", "crop_row0", "crop_col0"):
        if k in w:
            if int(w[k]) % factor:
                raise ValueError(f"{k} = {w[k]} is not a multiple of {factor}")
            w[k] = int(w[k]) // factor
    for k in ("xscale", "yscale"):
        if k in w:
            w[k] = float(w[k]) * factor
    return w


def check_grid_alignment(where_coarse: dict, where_fine: dict, factor: int,
                         tol_deg: float = 1e-3) -> list[str]:
    """Restituisce una lista di incongruenze (vuota = griglie allineate)."""
    issues = []
    for k in ("xsize", "ysize"):
        if k in where_coarse and k in where_fine:
            if int(where_coarse[k]) * factor != int(where_fine[k]):
                issues.append(f"{k}: {where_coarse[k]}*{factor} != {where_fine[k]}")
    for k in ("xscale", "yscale"):
        if k in where_coarse and k in where_fine:
            if abs(float(where_coarse[k]) / factor - float(where_fine[k])) > 1e-6 * float(where_fine[k]):
                issues.append(f"{k}: {where_coarse[k]}/{factor} != {where_fine[k]}")
    for c in ("LL", "UL", "UR", "LR"):
        for a in ("lon", "lat"):
            k = f"{c}_{a}"
            if k in where_coarse and k in where_fine:
                if abs(float(where_coarse[k]) - float(where_fine[k])) > tol_deg:
                    issues.append(f"{k}: {where_coarse[k]} vs {where_fine[k]}")
    if "projdef" in where_coarse and "projdef" in where_fine:
        a = " ".join(sorted(str(where_coarse["projdef"]).split()))
        b = " ".join(sorted(str(where_fine["projdef"]).split()))
        if a != b:
            issues.append(f"projdef diversa: {where_coarse['projdef']!r} vs {where_fine['projdef']!r}")
    return issues


def index_files(pattern: str, time_regex: str | None = None,
                time_format: str = "%Y%m%d%H%M",
                quantity: str = "DBZH") -> dict[dt.datetime, str]:
    """Indicizza i file per tempo nominale.

    pattern     : glob, es. 'data/odyssey/**/*.h5' (ricorsivo)
    time_regex  : regex con UN gruppo che cattura il timestamp nel nome file,
                  es. r'(\\d{12})'. Se None il tempo viene letto dagli attributi ODIM
                  (piu' lento: apre ogni file).
    """
    files = glob.glob(pattern, recursive=True)
    out: dict[dt.datetime, str] = {}
    rx = re.compile(time_regex) if time_regex else None
    for p in files:
        if rx is not None:
            m = rx.search(os.path.basename(p))
            if not m:
                continue
            t = dt.datetime.strptime(m.group(1), time_format)
        else:
            t = read_odim_composite(p, quantity).time
        out[t] = p
    return dict(sorted(out.items()))
