"""Convective / stratiform classification of reflectivity pixels (Steiner et al. 1995).

Source and parameters: docs/sources/1995 - Steiner - Climatological characterization of
three-dimensional storm structure from operational radar and rain gauge data.md
(section 6c, Eq. 2, Figs. 6b and 7). The parameters were tuned on a 2 km grid, and a
finer grid gives too much convective area (section 6d), so `obs_classes` classifies a
1 km truth on the 2 km grid by default (review of #65).
"""
from __future__ import annotations

import cv2
import numpy as np

INTENSITY_DBZ = 40.0          # convective centre by intensity (Steiner 1995, section 6c)
BACKGROUND_RADIUS_KM = 11.0   # background radius (Steiner 1995, section 6c)
# convective radius by background reflectivity, "medium" curve of Steiner 1995, Fig. 6b:
# (lower bound of background dBZ, radius km)
MEDIUM_RADIUS = ((-np.inf, 1.0), (25.0, 2.0), (30.0, 3.0), (35.0, 4.0), (40.0, 5.0))
# convective centres only, no surrounding area (case 2b of Steiner 1995, Table 3)
CENTRES_ONLY = ((-np.inf, 0.0),)


# ECCO (Dixon and Romatschke 2022, docs/sources/2022 - Dixon - ...md), OPERA 2 km settings
ECCO_TEXTURE_RADIUS_KM = 8.5   # section 5c (7 km on 1 km grids, section 3a)
ECCO_DBZ_BASE = 0.0            # section 3a, S/C/X band
ECCO_TDBZ_LOW, ECCO_TDBZ_HIGH = 0.0, 30.0   # section 3b, Fig. 3
ECCO_MIN_VALID = 0.25          # active point, section 3a
ECCO_MIN_FIT = 0.67            # plane fit, section 3a
ECCO_STRATIFORM_BELOW = 0.4    # section 3c (mixed 0.4-0.5, convective above 0.5)


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


def steiner_centres(dbz: np.ndarray, echo: np.ndarray, pixel_km: float,
                    intensity_dbz: float = INTENSITY_DBZ,
                    radius_km: float = BACKGROUND_RADIUS_KM):
    """Convective centres of Steiner et al. (1995), split by the criterion that makes them.

    Returns (by_intensity, by_peakedness, background): bool masks of the centres that
    are >= `intensity_dbz`, and of those below it that exceed the background by
    `peakedness_threshold`; background in dBZ (`background_dbz`)."""
    dbz = np.where(echo, dbz, -np.inf).astype(np.float64)
    bg = background_dbz(np.where(echo, dbz, 0.0), echo, pixel_km, radius_km)
    by_intensity = echo & (dbz >= intensity_dbz)
    with np.errstate(invalid="ignore"):
        peaked = dbz - bg > peakedness_threshold(np.nan_to_num(bg, nan=0.0))
    by_peakedness = echo & ~by_intensity & peaked
    return by_intensity, by_peakedness, bg


def steiner_convective(dbz: np.ndarray, echo: np.ndarray, pixel_km: float,
                       intensity_dbz: float = INTENSITY_DBZ,
                       radius_km: float = BACKGROUND_RADIUS_KM,
                       conv_radius=MEDIUM_RADIUS) -> np.ndarray:
    """Convective pixels of a reflectivity field (dBZ) after Steiner et al. (1995).

    echo: bool, pixels with a detected echo (everything else is ignored).
    A pixel is a convective centre if it is >= `intensity_dbz`, or if it exceeds the
    background (`background_dbz`) by `peakedness_threshold` (`steiner_centres`); every
    echo pixel within the convective radius of a centre (from the background at the
    centre) is convective. Returns a bool array; stratiform = echo & ~convective."""
    by_int, by_peak, bg = steiner_centres(dbz, echo, pixel_km, intensity_dbz, radius_km)
    centre = by_int | by_peak
    conv = np.zeros(centre.shape, bool)
    bgc = np.nan_to_num(bg, nan=-np.inf)
    bounds = [b for b, _ in conv_radius[1:]] + [np.inf]
    for (lo, r), hi in zip(conv_radius, bounds):
        sel = centre & (bgc >= lo) & (bgc < hi)
        if sel.any():
            conv |= cv2.dilate(sel.astype(np.uint8), _disk(r / pixel_km)).astype(bool)
    return conv & echo


def coarse_field(dbz_fine: np.ndarray, echo_fine: np.ndarray, factor: int):
    """Field `factor` times coarser: mean in linear Z over factor x factor blocks (no echo
    = Z 0); a coarse pixel has echo if any of its fine pixels has. Returns (dbz, echo)."""
    ny, nx = dbz_fine.shape
    if ny % factor or nx % factor:
        raise ValueError(f"shape {dbz_fine.shape} is not a multiple of {factor}")
    if factor == 1:
        return np.where(echo_fine, dbz_fine, 0.0).astype(np.float64), echo_fine
    shape = (ny // factor, factor, nx // factor, factor)
    z = np.where(echo_fine, np.power(10.0, dbz_fine.astype(np.float64) / 10.0), 0.0)
    zc = z.reshape(shape).mean(axis=(1, 3))
    echo_c = echo_fine.reshape(shape).any(axis=(1, 3))
    return np.where(echo_c, 10.0 * np.log10(np.maximum(zc, 1e-12)), 0.0), echo_c


def classes_on_coarse_grid(dbz_fine: np.ndarray, echo_fine: np.ndarray, pixel_km: float = 1.0,
                           factor: int = 1, conv_radius=MEDIUM_RADIUS) -> dict[str, np.ndarray]:
    """Convective and stratiform masks of a field with pixels of `pixel_km`. With
    factor = 1 the field is classified as it is; with factor > 1 it is classified on the
    grid `factor` times coarser (mean in linear Z over factor x factor blocks) and each
    coarse class is copied to its block. Pixels without echo belong to no class."""
    dbz_c, echo_c = coarse_field(dbz_fine, echo_fine, factor)
    conv_c = steiner_convective(dbz_c, echo_c, pixel_km * factor, conv_radius=conv_radius)
    conv = np.repeat(np.repeat(conv_c, factor, axis=0), factor, axis=1) & echo_fine
    return {"convective": conv, "stratiform": echo_fine & ~conv}


def obs_classes(obs: np.ndarray, floor: float = 0.0, factor: int = 2, pixel_km: float = 1.0,
                conv_radius=MEDIUM_RADIUS) -> dict[str, np.ndarray]:
    """Classes of a truth field as used in the validation (`Frame.to_field`: undetect and
    values below the floor set to `floor`, NaN outside coverage): echo = above the floor.
    By default a 1 km field is classified on the 2 km grid (factor = 2)."""
    echo = np.isfinite(obs) & (obs > floor)
    return classes_on_coarse_grid(np.nan_to_num(obs, nan=floor), echo, pixel_km, factor, conv_radius)


def ecco_convectivity(dbz: np.ndarray, valid: np.ndarray, pixel_km: float,
                      texture_radius_km: float = ECCO_TEXTURE_RADIUS_KM,
                      dbz_base: float = ECCO_DBZ_BASE,
                      tdbz_low: float = ECCO_TDBZ_LOW, tdbz_high: float = ECCO_TDBZ_HIGH,
                      min_valid: float = ECCO_MIN_VALID, min_fit: float = ECCO_MIN_FIT) -> np.ndarray:
    """Convectivity (0 stratiform ... 1 convective) of a 2D reflectivity field after the
    ECCO algorithm of Dixon and Romatschke (2022), sections 3a-b.

    For each pixel with valid reflectivity, in a circle of `texture_radius_km`: the pixel
    is active if at least `min_valid` of the circle is valid; if at least `min_fit` is
    valid, a plane a*x + b*y + c is fitted to the valid values and removed, adding back
    the kernel mean (Eqs. 1-2); DBZ_adj = DBZ_corr - dbz_base, negative values set to 0
    (Eq. 3); texture TDBZ = sqrt(stdev(DBZ_adj**2)) (Eq. 4); convectivity maps TDBZ
    linearly from `tdbz_low` (0) to `tdbz_high` (1) (Fig. 3).
    dbz: field in dBZ; valid: bool, pixels with reflectivity (here: echo). Returns
    convectivity, NaN where the pixel is not valid or not active."""
    disk = _disk(texture_radius_km / pixel_km).astype(bool)
    r = disk.shape[0] // 2
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    xs, ys = xx[disk].astype(np.float64), yy[disk].astype(np.float64)
    zp = np.pad(np.where(valid, dbz, 0.0).astype(np.float64), r)
    vp = np.pad(valid, r)
    win_z = np.lib.stride_tricks.sliding_window_view(zp, disk.shape)[..., disk]
    win_v = np.lib.stride_tricks.sliding_window_view(vp, disk.shape)[..., disk]
    out = np.full(dbz.shape, np.nan)
    frac = win_v.mean(axis=-1)
    active = valid & (frac >= min_valid)
    rows, cols = np.nonzero(active)
    if rows.size == 0:
        return out
    Z = win_z[rows, cols]                    # (n, k)
    V = win_v[rows, cols].astype(np.float64)
    n_v = V.sum(axis=1)
    mean = (Z * V).sum(axis=1) / n_v
    corr = Z.copy()
    fit = frac[rows, cols] >= min_fit
    if fit.any():
        w = V[fit]
        ones = np.ones_like(xs)
        A = np.stack([xs, ys, ones], axis=1)           # (k, 3)
        AtA = np.einsum("nk,ki,kj->nij", w, A, A)
        Atz = np.einsum("nk,ki,nk->ni", w, A, Z[fit])
        coef = np.linalg.solve(AtA, Atz[..., None])[..., 0]   # (n, 3): a, b, c
        plane = coef @ A.T                              # (n, k)
        corr[fit] = Z[fit] - plane + mean[fit][:, None]
    adj = np.maximum(corr - dbz_base, 0.0)
    a2 = np.where(V > 0, adj * adj, np.nan)
    tdbz = np.sqrt(np.nanstd(a2, axis=1))
    out[rows, cols] = np.clip((tdbz - tdbz_low) / (tdbz_high - tdbz_low), 0.0, 1.0)
    return out


def steiner_ecco_fields(obs: np.ndarray, floor: float = 0.0, factor: int = 2,
                        pixel_km: float = 1.0) -> dict[str, np.ndarray]:
    """Both classifications of a truth field (`Frame.to_field`) on the grid `factor`
    times coarser, for comparing them: 'dbz', 'echo', Steiner centres 'by_intensity' and
    'by_peakedness', Steiner 'convective' (medium radius), and ECCO 'convectivity'."""
    echo = np.isfinite(obs) & (obs > floor)
    dbz_c, echo_c = coarse_field(np.nan_to_num(obs, nan=floor), echo, factor)
    by_int, by_peak, _ = steiner_centres(dbz_c, echo_c, pixel_km * factor)
    conv = steiner_convective(dbz_c, echo_c, pixel_km * factor)
    return {"dbz": dbz_c, "echo": echo_c, "by_intensity": by_int, "by_peakedness": by_peak,
            "convective": conv, "convectivity": ecco_convectivity(dbz_c, echo_c, pixel_km * factor)}


def intensity_centres_vs_ecco(path: str, region_coarse_path: str, quantity: str = "DBZH") -> dict:
    """Counts, inside a region on the coarse grid (.npy), of the Steiner intensity centres
    of one composite and of those that ECCO calls stratiform (convectivity <
    ECCO_STRATIFORM_BELOW), mixed, or not active. Module-level, so it can run in worker
    processes."""
    from .odim_io import read_odim_composite
    region = np.load(region_coarse_path)
    f = steiner_ecco_fields(read_odim_composite(path, quantity).to_field(0.0))
    sel = f["by_intensity"] & region
    c = f["convectivity"]
    return {"intensity_centres": int(sel.sum()),
            "ecco_stratiform": int((sel & (c < ECCO_STRATIFORM_BELOW)).sum()),
            "ecco_mixed": int((sel & (c >= ECCO_STRATIFORM_BELOW) & (c <= 0.5)).sum()),
            "ecco_inactive": int((sel & np.isnan(c)).sum()),
            "echo_px": int((f["echo"] & region).sum())}
