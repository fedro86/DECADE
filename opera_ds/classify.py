"""Convective / stratiform classification of reflectivity pixels (Steiner et al. 1995).

Source and parameters: docs/sources/1995 - Steiner - Climatological characterization of
three-dimensional storm structure from operational radar and rain gauge data.md
(section 6c, Eq. 2, Figs. 6b and 7). `obs_classes` classifies the field at its own
resolution; `classes_on_coarse_grid` with factor > 1 classifies it on a coarser grid
(the method was tuned on 2 km) and is available if that is chosen.
"""
from __future__ import annotations

import cv2
import numpy as np

INTENSITY_DBZ = 40.0          # convective centre by intensity (Steiner 1995, section 6c)
BACKGROUND_RADIUS_KM = 11.0   # background radius (Steiner 1995, section 6c)
# convective radius by background reflectivity, "medium" curve of Steiner 1995, Fig. 6b:
# (lower bound of background dBZ, radius km)
MEDIUM_RADIUS = ((-np.inf, 1.0), (25.0, 2.0), (30.0, 3.0), (35.0, 4.0), (40.0, 5.0))


def _disk(radius_px: float) -> np.ndarray:
    r = int(np.floor(radius_px))
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y <= radius_px * radius_px + 1e-9).astype(np.uint8)


def peakedness_threshold(z_bg_dbz: np.ndarray) -> np.ndarray:
    """Delta Z (dB) a pixel must exceed its background by to be a convective centre,
    as a function of the background Z_bg (dBZ): Steiner 1995, Eq. 2."""
    z = np.asarray(z_bg_dbz, np.float64)
    d = 10.0 - z * z / 180.0
    d = np.where(z < 0.0, 10.0, d)
    return np.where(z >= 42.43, 0.0, d)


def background_dbz(dbz: np.ndarray, echo: np.ndarray, pixel_km: float,
                   radius_km: float = BACKGROUND_RADIUS_KM) -> np.ndarray:
    """Mean in linear Z of the echo pixels within `radius_km` of each pixel, in dBZ
    (NaN where there is no echo in the circle)."""
    k = _disk(radius_km / pixel_km).astype(np.float64)
    z = np.where(echo, np.power(10.0, dbz / 10.0), 0.0)
    s = cv2.filter2D(z, -1, k, borderType=cv2.BORDER_CONSTANT)
    n = cv2.filter2D(echo.astype(np.float64), -1, k, borderType=cv2.BORDER_CONSTANT)
    out = np.full(dbz.shape, np.nan)
    ok = n > 0.5
    out[ok] = 10.0 * np.log10(np.maximum(s[ok] / n[ok], 1e-12))
    return out


def steiner_convective(dbz: np.ndarray, echo: np.ndarray, pixel_km: float,
                       intensity_dbz: float = INTENSITY_DBZ,
                       radius_km: float = BACKGROUND_RADIUS_KM,
                       conv_radius=MEDIUM_RADIUS) -> np.ndarray:
    """Convective pixels of a reflectivity field (dBZ) after Steiner et al. (1995).

    echo: bool, pixels with a detected echo (everything else is ignored).
    A pixel is a convective centre if it is >= `intensity_dbz`, or if it exceeds the
    background (`background_dbz`) by `peakedness_threshold`; every echo pixel within
    the convective radius of a centre (from the background at the centre) is convective.
    Returns a bool array; stratiform = echo & ~convective."""
    dbz = np.where(echo, dbz, -np.inf).astype(np.float64)
    bg = background_dbz(np.where(echo, dbz, 0.0), echo, pixel_km, radius_km)
    with np.errstate(invalid="ignore"):
        centre = echo & ((dbz >= intensity_dbz) | (dbz - bg > peakedness_threshold(np.nan_to_num(bg, nan=0.0))))
    conv = np.zeros(dbz.shape, bool)
    bgc = np.nan_to_num(bg, nan=-np.inf)
    bounds = [b for b, _ in conv_radius[1:]] + [np.inf]
    for (lo, r), hi in zip(conv_radius, bounds):
        sel = centre & (bgc >= lo) & (bgc < hi)
        if sel.any():
            conv |= cv2.dilate(sel.astype(np.uint8), _disk(r / pixel_km)).astype(bool)
    return conv & echo


def classes_on_coarse_grid(dbz_fine: np.ndarray, echo_fine: np.ndarray, pixel_km: float = 1.0,
                           factor: int = 1) -> dict[str, np.ndarray]:
    """Convective and stratiform masks of a field with pixels of `pixel_km`. With
    factor = 1 the field is classified as it is; with factor > 1 it is classified on the
    grid `factor` times coarser (mean in linear Z over factor x factor blocks) and each
    coarse class is copied to its block. Pixels without echo belong to no class."""
    ny, nx = dbz_fine.shape
    if ny % factor or nx % factor:
        raise ValueError(f"shape {dbz_fine.shape} is not a multiple of {factor}")
    shape = (ny // factor, factor, nx // factor, factor)
    z = np.where(echo_fine, np.power(10.0, dbz_fine.astype(np.float64) / 10.0), 0.0)
    zc = z.reshape(shape).mean(axis=(1, 3))
    echo_c = echo_fine.reshape(shape).any(axis=(1, 3))
    dbz_c = np.where(echo_c, 10.0 * np.log10(np.maximum(zc, 1e-12)), 0.0)
    conv_c = steiner_convective(dbz_c, echo_c, pixel_km * factor)
    conv = np.repeat(np.repeat(conv_c, factor, axis=0), factor, axis=1) & echo_fine
    return {"convective": conv, "stratiform": echo_fine & ~conv}


def obs_classes(obs: np.ndarray, floor: float = 0.0, factor: int = 1, pixel_km: float = 1.0) -> dict[str, np.ndarray]:
    """Classes of a truth field as used in the validation (`Frame.to_field`: undetect and
    values below the floor set to `floor`, NaN outside coverage): echo = above the floor.
    Classified at the resolution of the field (factor = 1)."""
    echo = np.isfinite(obs) & (obs > floor)
    return classes_on_coarse_grid(np.nan_to_num(obs, nan=floor), echo, pixel_km, factor)
