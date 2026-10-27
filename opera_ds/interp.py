"""Downscaling spazio-temporale di una coppia di compositi consecutivi.

Idea chiave: il moto e le traiettorie si calcolano sulla griglia grossolana (2 km),
dove il campo di velocita' e' liscio e il costo e' 4 volte minore; i valori vengono
poi campionati UNA sola volta dal campo a 2 km nei punti di partenza dei pixel a 1 km.
Upscaling e avvezione sono quindi un'unica interpolazione (niente doppio smoothing),
e per alpha=0 il metodo si riduce al semplice upscaling bilineare.

Interpolazione temporale (advection-based, schema "forward/backward blending"):
    F(x, t0 + a*dt) = (1-a) * F0( x - a*V ) + a * F1( x + (1-a)*V )
con traiettorie integrate a passo multiplo (punto medio) nel campo V stazionario.
Crescita/decadimento sono lineari nel riferimento lagrangiano.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np

from .motion import LKParams

_INTERP = {"nearest": cv2.INTER_NEAREST, "linear": cv2.INTER_LINEAR, "cubic": cv2.INTER_CUBIC}


@dataclass
class DownscaleConfig:
    factor: int = 2                       # 2 km -> 1 km
    dt_in_min: float = 15.0
    dt_out_min: float = 5.0
    dbz_floor: float = 0.0                # undetect e valori bassi -> floor
    rain_threshold_dbz: float | None = None   # es. 7 dBZ (~0.1 mm/h con Marshall-Palmer)
    spatial_interp: str = "linear"        # nearest | linear | cubic
    coverage_rule: str = "intersection"   # copertura in uscita: intersection | union
    blend_space: str = "Z"                # "Z": media in riflettivita' lineare (undetect = 0); "dB"
    max_step_px: float = 2.0              # passo massimo delle sotto-traiettorie (px grossolani)
    context_pairs: int = 1                # coppie extra prima/dopo per la stima del moto
    lk: LKParams = field(default_factory=LKParams)

    @property
    def n_sub(self) -> int:
        n = self.dt_in_min / self.dt_out_min
        if abs(n - round(n)) > 1e-9:
            raise ValueError("dt_in deve essere multiplo di dt_out")
        return int(round(n))


def _remap(a, x, y, interp=cv2.INTER_LINEAR, border=cv2.BORDER_REPLICATE, value=0.0):
    return cv2.remap(a, x, y, interp, borderMode=border, borderValue=value)


def trajectory_displacement(V: np.ndarray, tau: float, max_step_px: float = 2.0) -> np.ndarray:
    """Spostamento D(x) tale che x+D e' il punto di partenza al tempo t-tau di una
    particella che arriva in x al tempo t (tau in unita' di dt; tau<0 = verso il futuro).
    Integrazione a punto medio sul campo stazionario V (px/dt)."""
    vx, vy = V[0].astype(np.float32), V[1].astype(np.float32)
    ny, nx = vx.shape
    gx = np.arange(nx, dtype=np.float32)[None, :].repeat(ny, 0)
    gy = np.arange(ny, dtype=np.float32)[:, None].repeat(nx, 1)
    if tau == 0:
        return np.zeros((2, ny, nx), np.float32)
    vmax = float(np.hypot(vx, vy).max())
    n = max(1, math.ceil(abs(tau) * vmax / max_step_px))
    h = np.float32(tau / n)
    x, y = gx.copy(), gy.copy()
    for _ in range(n):
        ux, uy = _remap(vx, x, y), _remap(vy, x, y)
        xm, ym = x - 0.5 * h * ux, y - 0.5 * h * uy
        ux, uy = _remap(vx, xm, ym), _remap(vy, xm, ym)
        x, y = x - h * ux, y - h * uy
    return np.stack([x - gx, y - gy])


def fine_grid_in_coarse_coords(ny: int, nx: int, f: int) -> tuple[np.ndarray, np.ndarray]:
    """Coordinate (in indici della griglia grossolana) dei centri dei pixel fini.
    Pixel fine j -> (j + 0.5)/f - 0.5 (stessa convenzione di cv2.resize)."""
    xc = (np.arange(nx * f, dtype=np.float32) + 0.5) / f - 0.5
    yc = (np.arange(ny * f, dtype=np.float32) + 0.5) / f - 0.5
    return xc[None, :].repeat(ny * f, 0), yc[:, None].repeat(nx * f, 1)


def upsample_field(a: np.ndarray, f: int) -> np.ndarray:
    """Interpolazione bilineare (centri allineati) di un campo liscio, es. velocita'."""
    return cv2.resize(a.astype(np.float32), (a.shape[1] * f, a.shape[0] * f),
                      interpolation=cv2.INTER_LINEAR)


def block_repeat(m: np.ndarray, f: int) -> np.ndarray:
    return np.repeat(np.repeat(m, f, axis=0), f, axis=1)


class PairInterpolator:
    """Interpola una coppia (F0 a t0, F1 a t1=t0+dt) su griglia fine a qualsiasi alpha."""

    def __init__(self, F0, F1, V, cfg: DownscaleConfig):
        self.cfg = cfg
        f = cfg.factor
        self.ny, self.nx = F0.shape
        self.cov0, self.cov1 = np.isfinite(F0), np.isfinite(F1)
        fl = np.float32(cfg.dbz_floor)
        self.F0 = np.where(self.cov0, F0, fl).astype(np.float32)
        self.F1 = np.where(self.cov1, F1, fl).astype(np.float32)
        self.c0f, self.c1f = self.cov0.astype(np.float32), self.cov1.astype(np.float32)
        self.V = V
        self._dep_cache: dict = {}
        self._space = cfg.blend_space
        self.XC, self.YC = fine_grid_in_coarse_coords(self.ny, self.nx, f)
        cov0f, cov1f = block_repeat(self.cov0, f), block_repeat(self.cov1, f)
        self.cov_out = (cov0f & cov1f) if cfg.coverage_rule == "intersection" else (cov0f | cov1f)
        self.cov0f, self.cov1f = cov0f, cov1f
        detected = np.concatenate([self.F0[self.cov0 & (self.F0 > fl)],
                                   self.F1[self.cov1 & (self.F1 > fl)]])
        if cfg.rain_threshold_dbz is not None:
            self.out_thr = float(cfg.rain_threshold_dbz)
        else:
            self.out_thr = float(detected.min()) if detected.size else float(fl) + 1.0
        self.vmax_in = float(detected.max()) if detected.size else float(fl)

    # -- campionamento ------------------------------------------------------
    def _sample(self, F, cov_f, X, Y):
        interp = _INTERP[self.cfg.spatial_interp]
        val = _remap(F, X, Y, interp, cv2.BORDER_REPLICATE)
        ok = _remap(cov_f, X, Y, cv2.INTER_NEAREST, cv2.BORDER_CONSTANT, 0.0) > 0.5
        if self.cfg.spatial_interp == "cubic":
            np.clip(val, self.cfg.dbz_floor, self.vmax_in, out=val)
        return val, ok

    def _departure(self, tau):
        if tau == 0:
            return self.XC, self.YC
        key = round(tau, 6)
        if key not in self._dep_cache:
            D = trajectory_displacement(self.V, tau, self.cfg.max_step_px)
            f = self.cfg.factor
            self._dep_cache[key] = (self.XC + upsample_field(D[0], f),
                                    self.YC + upsample_field(D[1], f))
        return self._dep_cache[key]

    def _finish(self, val):
        und = val < self.out_thr
        cov = self.cov_out
        val = val.astype(np.float32)
        val[und] = self.cfg.dbz_floor
        return val, cov.copy(), und & cov

    # -- metodi -------------------------------------------------------------
    def eulerian(self, a, method="linear"):
        A, okA = self._sample(self.F0, self.c0f, self.XC, self.YC)
        if a == 0:
            return self._finish(A)
        B, okB = self._sample(self.F1, self.c1f, self.XC, self.YC)
        if method == "nearest":
            return self._finish(A if a < 0.5 else B)
        return self._finish(self._blend(A, okA, B, okB, a))

    def advect(self, a):
        """Interpolazione advettiva (Lucas-Kanade + semi-lagrangiano)."""
        if a == 0:
            return self.eulerian(0.0)
        XA, YA = self._departure(a)
        XB, YB = self._departure(-(1.0 - a))
        A, okA = self._sample(self.F0, self.c0f, XA, YA)
        B, okB = self._sample(self.F1, self.c1f, XB, YB)
        out = self._blend(A, okA, B, okB, a, floor_if_none=False)
        # dove nessuna traiettoria resta in copertura (eco che entra dall'esterno
        # della rete radar) si ricade sull'interpolazione euleriana
        miss = ~(okA | okB)
        if miss.any():
            Ae, okAe = self._sample(self.F0, self.c0f, self.XC, self.YC)
            Be, okBe = self._sample(self.F1, self.c1f, self.XC, self.YC)
            eul = self._blend(Ae, okAe, Be, okBe, a)
            out[miss] = eul[miss]
        return self._finish(out)

    def _blend(self, A, okA, B, okB, a, floor_if_none=True):
        a = np.float32(a)
        if self._space == "Z":
            # media in Z lineare: un pixel asciutto (floor) pesa 0 invece di trascinare
            # il valore in dB sotto la soglia di rilevazione ai bordi delle celle
            fl = np.float32(self.cfg.dbz_floor)
            zA = np.where(A > fl, np.power(np.float32(10), A / 10), 0).astype(np.float32)
            zB = np.where(B > fl, np.power(np.float32(10), B / 10), 0).astype(np.float32)
            z = (1 - a) * zA + a * zB
            out = np.where(z > 0, 10 * np.log10(np.maximum(z, 1e-10)), fl).astype(np.float32)
        else:
            out = (1 - a) * A + a * B
        out = np.where(okA & ~okB, A, out)
        out = np.where(okB & ~okA, B, out)
        if floor_if_none:
            out = np.where(okA | okB, out, np.float32(self.cfg.dbz_floor))
        return out

    def get(self, a: float, method: str = "lk"):
        """method: 'lk' | 'linear' | 'nearest', con suffisso opzionale ':Z' o ':dB'
        per forzare lo spazio di blending (es. 'lk:dB')."""
        base, _, space = method.partition(":")
        self._space = space or self.cfg.blend_space
        if self._space not in ("Z", "dB"):
            raise ValueError(f"blend_space sconosciuto: {self._space}")
        if base == "lk":
            return self.advect(a)
        if base in ("linear", "nearest"):
            return self.eulerian(a, base)
        raise ValueError(method)
