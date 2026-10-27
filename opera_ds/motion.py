"""Stima del moto con Lucas-Kanade (schema di pysteps.motion.lucaskanade).

0. (opzionale, default) filtro passa-alto del campo in dBZ
1. feature di Shi-Tomasi sul campo t0 (cv2.goodFeaturesToTrack)
2. tracking piramidale LK verso t1 (cv2.calcOpticalFlowPyrLK)
3. controllo forward-backward (scarta vettori non reversibili)
4. rimozione outlier locali (k vicini, soglia in deviazioni standard)
5. declustering su celle regolari
6. interpolazione IDW su griglia grossolana + smoothing -> campo denso

Tutti i vettori sono in pixel della griglia di input per intervallo dt di input
(es. pixel 2 km / 15 min).
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from scipy.ndimage import binary_erosion, gaussian_filter
from scipy.spatial import cKDTree


@dataclass
class LKParams:
    backend: str = "opencv"          # "opencv" (questa implementazione) o "pysteps"
    vmin: float = 0.0                # range dBZ per la conversione a uint8
    vmax: float = 65.0
    highpass_sigma: float = 15.0     # px; LK su campo passa-alto: robusto a crescita/decadimento
    highpass_range: float = 12.0     # dB mappati sull'intero range uint8; 0 = disattiva
    feature_min_dbz: float = 10.0    # feature solo dove il campo supera questa soglia
    max_corners: int = 5000          # dominio pan-europeo: piu' feature dei default pysteps (1000)
    quality_level: float = 0.01
    min_distance: int = 10
    block_size: int = 5
    win_size: int = 50
    pyr_levels: int = 3
    fb_max_err_px: float = 1.0       # soglia forward-backward
    buffer_px: int = 5               # niente feature vicino al bordo della copertura
    outlier_k: int = 30
    outlier_nstd: float = 3.0
    decluster_px: int = 20
    min_vectors: int = 10
    grid_step: int = 10              # passo della griglia per l'interpolazione
    idw_k: int = 30
    idw_power: float = 2.0
    smooth_sigma: float = 1.5        # smoothing in celle della griglia grossolana


def _to_uint8(f: np.ndarray, p: "LKParams") -> np.ndarray:
    """Immagine per OpenCV. Con highpass_sigma>0 si sottrae la media locale: le
    variazioni lisce di intensita' (crescita/decadimento) non vengono scambiate per moto."""
    g = np.clip(np.nan_to_num(f, nan=p.vmin), p.vmin, p.vmax).astype(np.float32)
    if p.highpass_sigma > 0 and p.highpass_range > 0:
        h = g - gaussian_filter(g, p.highpass_sigma, mode="nearest")
        return (np.clip(h / p.highpass_range, -1, 1) * 127 + 128).astype(np.uint8)
    return ((g - p.vmin) / (p.vmax - p.vmin) * 255.0).astype(np.uint8)


def sparse_vectors(f0: np.ndarray, f1: np.ndarray, p: LKParams) -> tuple[np.ndarray, np.ndarray]:
    """Vettori sparsi da f0 a f1. Restituisce (xy[n,2], uv[n,2]) in pixel/dt."""
    img0, img1 = _to_uint8(f0, p), _to_uint8(f1, p)
    valid = np.isfinite(f0) & np.isfinite(f1)
    if p.buffer_px > 0:
        valid = binary_erosion(valid, iterations=p.buffer_px)
    mask = (valid & (np.nan_to_num(f0, nan=-999) >= p.feature_min_dbz)).astype(np.uint8) * 255
    if mask.sum() == 0:
        return np.empty((0, 2), np.float32), np.empty((0, 2), np.float32)

    p0 = cv2.goodFeaturesToTrack(img0, maxCorners=p.max_corners, qualityLevel=p.quality_level,
                                 minDistance=p.min_distance, mask=mask, blockSize=p.block_size)
    if p0 is None or len(p0) == 0:
        return np.empty((0, 2), np.float32), np.empty((0, 2), np.float32)

    lk = dict(winSize=(p.win_size, p.win_size), maxLevel=p.pyr_levels,
              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.01))
    p1, st1, _ = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk)
    p0b, st2, _ = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk)
    fb = np.linalg.norm((p0 - p0b).reshape(-1, 2), axis=1)
    ok = (st1.ravel() == 1) & (st2.ravel() == 1) & (fb <= p.fb_max_err_px)

    xy = p0.reshape(-1, 2)[ok]
    uv = (p1 - p0).reshape(-1, 2)[ok]
    # scarta punti di arrivo fuori dalla copertura
    ny, nx = f0.shape
    xi = np.clip(np.round(xy[:, 0] + uv[:, 0]).astype(int), 0, nx - 1)
    yi = np.clip(np.round(xy[:, 1] + uv[:, 1]).astype(int), 0, ny - 1)
    inside = np.isfinite(f1[yi, xi])
    return xy[inside].astype(np.float32), uv[inside].astype(np.float32)


def remove_outliers(xy, uv, k=30, nstd=3.0):
    n = len(xy)
    if n < 4:
        return xy, uv
    kk = min(k + 1, n)
    _, idx = cKDTree(xy).query(xy, k=kk)
    neigh = uv[idx[:, 1:]]                       # escludi il punto stesso
    mu = neigh.mean(axis=1)
    sd = neigh.std(axis=1) + 0.1                 # evita sd=0 in flussi uniformi
    keep = np.all(np.abs(uv - mu) <= nstd * sd, axis=1)
    return xy[keep], uv[keep]


def decluster(xy, uv, scale):
    if len(xy) == 0 or scale <= 1:
        return xy, uv
    keys = np.floor(xy / scale).astype(np.int64)
    _, inv = np.unique(keys[:, 0] * 1_000_003 + keys[:, 1], return_inverse=True)
    cnt = np.bincount(inv).astype(np.float32)
    out_xy = np.stack([np.bincount(inv, xy[:, i]) / cnt for i in (0, 1)], 1)
    out_uv = np.stack([np.bincount(inv, uv[:, i]) / cnt for i in (0, 1)], 1)
    return out_xy.astype(np.float32), out_uv.astype(np.float32)


def dense_field(xy, uv, shape, p: LKParams) -> np.ndarray:
    """IDW su griglia grossolana + smoothing gaussiano + interpolazione bilineare."""
    ny, nx = shape
    if len(xy) < p.min_vectors:
        return np.zeros((2, ny, nx), np.float32)
    s = p.grid_step
    gy = np.arange(0, ny - 1 + s, s, dtype=np.float32)
    gx = np.arange(0, nx - 1 + s, s, dtype=np.float32)
    GX, GY = np.meshgrid(gx, gy)
    k = min(p.idw_k, len(xy))
    d, idx = cKDTree(xy).query(np.c_[GX.ravel(), GY.ravel()], k=k)
    if k == 1:
        d, idx = d[:, None], idx[:, None]
    w = 1.0 / np.maximum(d, 1.0) ** p.idw_power
    w /= w.sum(axis=1, keepdims=True)
    coarse = [(w * uv[idx, i]).sum(axis=1).reshape(GX.shape).astype(np.float32) for i in (0, 1)]
    if p.smooth_sigma > 0:
        coarse = [gaussian_filter(c, p.smooth_sigma, mode="nearest") for c in coarse]
    mx = (np.arange(nx, dtype=np.float32) / s)[None, :].repeat(ny, 0)
    my = (np.arange(ny, dtype=np.float32) / s)[:, None].repeat(nx, 1)
    return np.stack([cv2.remap(c, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                     for c in coarse]).astype(np.float32)


def estimate_motion(fields: list[np.ndarray], p: LKParams | None = None) -> tuple[np.ndarray, dict]:
    """Campo di moto denso (2, ny, nx) [vx, vy] in pixel per intervallo, da >=2 campi
    consecutivi equispaziati (NaN = fuori copertura). I vettori di tutte le coppie
    consecutive vengono uniti prima dell'interpolazione (come fa pysteps)."""
    p = p or LKParams()
    if p.backend == "pysteps":
        from pysteps import motion  # opzionale
        V = motion.get_method("LK")(np.stack(fields))
        return np.nan_to_num(V).astype(np.float32), {"backend": "pysteps"}

    sparse = [sparse_vectors(a, b, p) for a, b in zip(fields[:-1], fields[1:])]
    return motion_from_sparse(sparse, fields[0].shape, p)


def motion_from_sparse(sparse: list, shape, p: LKParams | None = None):
    """Campo denso da una lista di (xy, uv) di coppie consecutive (riusabili tra coppie)."""
    p = p or LKParams()
    all_xy = [s[0] for s in sparse]
    all_uv = [s[1] for s in sparse]
    xy = np.concatenate(all_xy) if all_xy else np.empty((0, 2), np.float32)
    uv = np.concatenate(all_uv) if all_uv else np.empty((0, 2), np.float32)
    n_raw = len(xy)
    xy, uv = remove_outliers(xy, uv, p.outlier_k, p.outlier_nstd)
    n_clean = len(xy)
    xy, uv = decluster(xy, uv, p.decluster_px)
    V = dense_field(xy, uv, shape, p)
    return V, {"n_raw": n_raw, "n_clean": n_clean, "n_decl": len(xy)}
