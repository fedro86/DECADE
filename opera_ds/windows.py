"""Finestre spazio-temporali per il ML (formato compatibile con IRENE).

Una finestra e' una sequenza di T frame a 1 km / 5 min su un'area H x W, prodotta
da ODYSSEY con `PairInterpolator`. Il moto si stima su un ritaglio piu' largo
(`context_km` per lato), poi si tiene solo l'area della finestra.

Store Zarr (zarr >= 3), una riga per finestra:
  RR      (n, T, H, W) float16   pioggia in mm/h (Marshall-Palmer, dBZ limitati come
                                 IRENE a [0, dbz_clip]); NaN = fuori copertura
  alpha   (n, T)       float32   posizione nell'intervallo di 15 min; 0 = frame vero
  time    (n, T)       int64     secondi dal 1970-01-01 UTC (etichetta del frame)
  row0, col0 (n,)      int32     origine della finestra sulla griglia OPERA a 1 km
Gli attributi del gruppo descrivono griglia (projdef, angolo UL, passo), conversione
Z-R, limite in dBZ, shift delle etichette e configurazione del downscaling.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import functools
import json
from typing import Callable

import numpy as np

from .interp import DownscaleConfig
from .odim_io import read_odim_composite
from .pipeline import FrameSource, output_times

EPOCH = dt.datetime(1970, 1, 1)


@dataclasses.dataclass
class Window:
    """Richiesta di una finestra: primo frame `t_start` (etichetta), origine
    (row0, col0) sulla griglia a 1 km dell'intero dominio, dimensioni in pixel."""
    t_start: dt.datetime
    row0: int
    col0: int
    T: int = 24
    H: int = 256
    W: int = 256


def dbz_to_rr(dbz, floor=0.0, clip_dbz=60.0, a=200.0, b=1.6):
    """Come IRENE: dBZ limitati a [floor, clip_dbz], poi R = (Z/a)^(1/b); floor -> 0."""
    d = np.clip(dbz, floor, clip_dbz).astype(np.float32)
    r = np.power(np.power(np.float32(10), d / 10) / np.float32(a), np.float32(1 / b))
    return np.where(dbz > floor, r, np.float32(0)).astype(np.float32)


def window_extent(win: Window, scale_fine: float, context_km: float, factor: int = 2):
    """Estensione di lettura (x_off, y_off, w, h in metri dall'angolo UL) che contiene la
    finestra piu' `context_km` per lato, allineata ai pixel grossolani. Restituisce anche
    l'offset (righe, colonne a 1 km) della finestra dentro il ritaglio."""
    if win.row0 % factor or win.col0 % factor or win.H % factor or win.W % factor:
        raise ValueError("origine e dimensioni della finestra devono essere multipli di factor")
    pad = int(np.ceil(context_km * 1000.0 / (scale_fine * factor))) * factor   # px fini
    r0, c0 = max(win.row0 - pad, 0), max(win.col0 - pad, 0)
    r1, c1 = win.row0 + win.H + pad, win.col0 + win.W + pad
    ext = (c0 * scale_fine, r0 * scale_fine, (c1 - c0) * scale_fine, (r1 - r0) * scale_fine)
    return ext, (win.row0 - r0, win.col0 - c0)


def make_window(files: dict, win: Window, cfg: DownscaleConfig | None = None, method: str = "lk",
                quantity: str = "DBZH", scale_fine: float = 1000.0, context_km: float = 150.0,
                time_shift_min: float = 0.0, clip_dbz: float = 60.0,
                reader: Callable = read_odim_composite):
    """Produce una finestra. Restituisce (RR[T,H,W] float32, alpha[T], times[T]) oppure
    None se manca un frame ODYSSEY necessario (finestre con buchi temporali scartate,
    come in IRENE). `files` e' l'indice tempo -> file ODYSSEY (griglia intera)."""
    cfg = cfg or DownscaleConfig()
    ext, (dr, dc) = window_extent(win, scale_fine, context_km, cfg.factor)
    src = FrameSource(files, cfg, quantity, reader=functools.partial(reader, extent=ext))
    step_out = dt.timedelta(minutes=cfg.dt_out_min)
    wanted = [win.t_start + k * step_out for k in range(win.T)]
    out = np.full((win.T, win.H, win.W), np.nan, np.float32)
    alpha = np.full(win.T, np.nan, np.float32)
    done = 0
    t0 = wanted[0] - dt.timedelta(minutes=cfg.dt_in_min + max(time_shift_min, 0))
    t0 = t0 - dt.timedelta(seconds=(t0 - EPOCH).total_seconds() % (cfg.dt_in_min * 60))
    index = {t: i for i, t in enumerate(wanted)}
    while t0 <= wanted[-1] and done < win.T:
        targets = [(T, a) for T, a in output_times(t0, cfg, time_shift_min) if T in index]
        if targets:
            pi = src.pair(t0)
            if pi is None:
                return None
            for T, a in targets:
                val, cov, _ = pi.get(a, method)
                rr = dbz_to_rr(val, cfg.dbz_floor, clip_dbz)
                rr = np.where(cov, rr, np.nan)[dr:dr + win.H, dc:dc + win.W]
                if rr.shape != (win.H, win.W):
                    raise ValueError(f"finestra fuori dal dominio: {win}")
                out[index[T]], alpha[index[T]] = rr, a
                done += 1
        t0 += dt.timedelta(minutes=cfg.dt_in_min)
    if done < win.T:
        return None
    return out, alpha, wanted


class WindowStore:
    """Store Zarr di finestre, aperto in aggiunta (le righe esistenti non si toccano)."""

    def __init__(self, path: str, T: int, H: int, W: int, attrs: dict | None = None):
        import zarr

        self.path = path
        try:
            self.root = zarr.open_group(path, mode="r+")
            shp = self.root["RR"].shape[1:]
            if tuple(shp) != (T, H, W):
                raise ValueError(f"lo store {path} ha finestre {shp}, non {(T, H, W)}")
        except FileNotFoundError:
            self.root = zarr.open_group(path, mode="w")
            self.root.create_array("RR", shape=(0, T, H, W), chunks=(1, T, H, W), dtype="float16",
                                   fill_value=np.nan)
            self.root.create_array("alpha", shape=(0, T), chunks=(4096, T), dtype="float32",
                                   fill_value=np.nan)
            self.root.create_array("time", shape=(0, T), chunks=(4096, T), dtype="int64", fill_value=0)
            for k in ("row0", "col0"):
                self.root.create_array(k, shape=(0,), chunks=(4096,), dtype="int32", fill_value=-1)
            self.root.attrs.update(attrs or {})

    def __len__(self):
        return self.root["RR"].shape[0]

    def append(self, rr, alpha, times, row0, col0):
        n = len(self)
        for k in ("RR", "alpha", "time", "row0", "col0"):
            a = self.root[k]
            a.resize((n + 1,) + a.shape[1:])
        self.root["RR"][n] = rr.astype(np.float16)
        self.root["alpha"][n] = alpha
        self.root["time"][n] = [int((t - EPOCH).total_seconds()) for t in times]
        self.root["row0"][n] = row0
        self.root["col0"][n] = col0
        return n


def store_attrs(where_fine: dict, cfg: DownscaleConfig, method: str, time_shift_min: float,
                clip_dbz: float, context_km: float) -> dict:
    """Attributi descrittivi dello store (griglia a 1 km dell'intero dominio)."""
    keep = ("projdef", "xscale", "yscale", "xsize", "ysize", "UL_lon", "UL_lat")
    return {
        "description": "Finestre ODYSSEY downscalate a 1 km / 5 min per il ML (formato IRENE: RR in mm/h)",
        "grid": {k: (v.item() if hasattr(v, "item") else v) for k, v in where_fine.items() if k in keep},
        "zr": {"a": 200.0, "b": cfg.zr_b}, "dbz_clip": [cfg.dbz_floor, clip_dbz],
        "time_units": "seconds since 1970-01-01T00:00:00Z", "time_shift_min": time_shift_min,
        "alpha_note": "0 = frame ODYSSEY vero; >0 = interpolato",
        "method": method, "context_km": context_km,
        "downscale_config": json.loads(json.dumps(dataclasses.asdict(cfg), default=str)),
    }
