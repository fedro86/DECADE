"""Validazione nel periodo di sovrapposizione ODYSSEY / CIRRUS (2024).

Per ogni coppia ODYSSEY (t0, t0+15) campionata si costruiscono i campi a 1 km per
ogni istante CIRRUS T che cade nell'intervallo e si confrontano con CIRRUS.

Metodi confrontati:
  nearest : frame ODYSSEY piu' vicino nel tempo, upscalato  (baseline "persistenza")
  linear  : media pesata euleriana di F0 e F1               (baseline "cross-fade")
  lk      : interpolazione advettiva Lucas-Kanade

Stratificazione per alpha (posizione nell'intervallo di 15 min): ad alpha=0 non c'e'
interpolazione temporale, quindi quell'errore e' il "pavimento" dovuto a upscaling +
differenze tra i due prodotti (catena di elaborazione, radar, finestre temporali).
L'errore aggiuntivo ad alpha=1/3, 2/3 e' quello dell'interpolazione temporale.

Sfasamento temporale (`shifts`): ODYSSEY usa la finestra [NT-10, NT+5], CIRRUS
(NT-10, NT]; per il prodotto CIRRUS etichettato T si interpola ODYSSEY al tempo
T + shift. Ci si aspetta un ottimo vicino a -2.5 min: la validazione lo stima.

Conservazione della massa (in R, Marshall-Palmer Z = 200 R^1.6, dBZ limitati a
`r_cap_dbz`):
  interni (mass_internal.csv): confronto con ODYSSEY stesso, quindi senza le
    differenze tra prodotti. Ad alpha=0 media a blocchi 2x2 dell'output contro R(F0)
    (errore del solo upscaling); a ogni alpha volume dell'output contro
    (1-a)*V(F0) + a*V(F1), sulla regione e sull'intero ritaglio.
  contro CIRRUS: volumi e errori di R istantanei a piu' scale (colonne r* di
    summary.csv) e accumuli orari sugli istanti CIRRUS disponibili (accum_1h.csv).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import logging
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import cv2
import numpy as np

from .interp import DownscaleConfig, block_repeat
from .odim_io import Frame, check_grid_alignment, coarsen_where, read_odim_composite
from .pipeline import FrameSource, floor_time

log = logging.getLogger(__name__)

DEFAULT_THRESHOLDS = (10.0, 20.0, 30.0, 40.0)   # dBZ
DEFAULT_FSS_THR = (20.0, 30.0)
DEFAULT_FSS_SCALES = (1, 5, 11, 21, 41, 81)     # km (lato della finestra, pixel a 1 km)
DEFAULT_R_SCALES = (1, 2, 5, 10, 25)            # km (lato dei blocchi per R e accumuli)
HIST_BINS = np.arange(-10.0, 75.5, 0.5)
MIN_HOUR_FRAC = 0.5      # accumulo orario solo con almeno meta' degli istanti a 5 min


def degrade_frame(frame: Frame, factor: int = 2) -> Frame:
    """Degrade a fine composite (e.g. CIRRUS, 1 km) to a grid `factor` times coarser
    (e.g. 2 km, as ODYSSEY), for validating the interpolation against a known truth (H1).

    Each coarse pixel is the mean in linear Z (mm^6 m^-3) of its factor x factor block,
    with undetect counted as Z = 0, converted back to dBZ. A coarse pixel is covered only
    if the whole block is covered, and is undetect if the whole block is undetect.
    Input values in dBZ; output a Frame with the coarse 'where' (see `coarsen_where`).
    Rows and columns must be multiples of `factor`."""
    ny, nx = frame.values.shape
    if ny % factor or nx % factor:
        raise ValueError(f"shape {frame.values.shape} is not a multiple of {factor}")
    shape = (ny // factor, factor, nx // factor, factor)
    det = frame.coverage & ~frame.undetect
    z = np.where(det, np.power(10.0, frame.values.astype(np.float64) / 10.0), 0.0)
    z_mean = z.reshape(shape).mean(axis=(1, 3))
    coverage = frame.coverage.reshape(shape).all(axis=(1, 3))
    undetect = coverage & ~det.reshape(shape).any(axis=(1, 3))
    values = np.zeros(z_mean.shape, np.float32)
    ok = coverage & ~undetect
    values[ok] = 10.0 * np.log10(z_mean[ok])
    return Frame(time=frame.time, values=values, coverage=coverage, undetect=undetect,
                 where=coarsen_where(frame.where, factor), path=frame.path, attrs=dict(frame.attrs))


def read_degraded(path: str, quantity: str = "DBZH", factor: int = 2, extent=None) -> Frame:
    """`read_odim_composite` followed by `degrade_frame`. A module-level reader, so that
    `functools.partial(read_degraded, ...)` can be passed to `run_validation` as the
    reader of the coarse files and pickled for the worker processes."""
    return degrade_frame(read_odim_composite(path, quantity, extent=extent), factor)


def _box(a, k):
    if k <= 1:
        return a
    return cv2.boxFilter(a, -1, (k, k), normalize=False, borderType=cv2.BORDER_CONSTANT)


def dbz_to_rain(dbz, floor=0.0, cap_dbz=55.0, a=200.0, b=1.6):
    """Marshall-Palmer Z = a R^b in mm/h. Floor/undetect -> 0; dBZ limitati a cap_dbz
    (sopra ~55 dBZ domina la grandine e R esplode)."""
    d = np.minimum(dbz, cap_dbz).astype(np.float32)
    r = np.power(np.power(np.float32(10), d / 10) / np.float32(a), np.float32(1 / b))
    return np.where(dbz > floor, r, np.float32(0)).astype(np.float32)


def _blocks(F, w, k):
    """Medie pesate da w su blocchi k x k (bordo destro/inferiore troncato) e
    frazione di ogni blocco con peso. k=1 restituisce i pixel."""
    if k <= 1:
        return F, w.astype(np.float32)
    ny, nx = (F.shape[0] // k) * k, (F.shape[1] // k) * k
    shp = (ny // k, k, nx // k, k)
    W = w[:ny, :nx].astype(np.float32).reshape(shp).sum((1, 3))
    S = (F[:ny, :nx] * w[:ny, :nx]).reshape(shp).sum((1, 3))
    return S / np.maximum(W, 1e-9), W / (k * k)


def _scale_stats(s, prefix, P, O, w, scales, min_frac=0.5):
    """Somme additive di errore tra P e O mediati su blocchi, per ogni scala."""
    for k in scales:
        bp, f = _blocks(P, w, k)
        bo, _ = _blocks(O, w, k)
        ok = f >= min_frac
        p, o = bp[ok].astype(np.float64), bo[ok].astype(np.float64)
        e = p - o
        s[f"{prefix}{k}_n"] += e.size
        s[f"{prefix}{k}_se"] += e.sum(); s[f"{prefix}{k}_sae"] += np.abs(e).sum()
        s[f"{prefix}{k}_sse"] += (e ** 2).sum()
        s[f"{prefix}{k}_sp"] += p.sum(); s[f"{prefix}{k}_so"] += o.sum()
        s[f"{prefix}{k}_spp"] += (p ** 2).sum(); s[f"{prefix}{k}_soo"] += (o ** 2).sum()
        s[f"{prefix}{k}_spo"] += (p * o).sum()


def _scale_summary(s, prefix, scales, out):
    for k in scales:
        n = s.get(f"{prefix}{k}_n", 0.0)
        if n == 0:
            continue
        mp, mo = s[f"{prefix}{k}_sp"] / n, s[f"{prefix}{k}_so"] / n
        vp, vo = s[f"{prefix}{k}_spp"] / n - mp ** 2, s[f"{prefix}{k}_soo"] / n - mo ** 2
        out[f"{prefix}{k}_bias"] = s[f"{prefix}{k}_se"] / n
        out[f"{prefix}{k}_mae"] = s[f"{prefix}{k}_sae"] / n
        out[f"{prefix}{k}_rmse"] = np.sqrt(s[f"{prefix}{k}_sse"] / n)
        out[f"{prefix}{k}_corr"] = (s[f"{prefix}{k}_spo"] / n - mp * mo) / np.sqrt(max(vp * vo, 1e-12))


def _to_dict(d):
    return {k: dict(v) for k, v in d.items()}


class Accumulator:
    """Statistiche additive (aggregabili tra processi e periodi)."""

    def __init__(self, thresholds, fss_thr, fss_scales, wet_dbz, r_scales=DEFAULT_R_SCALES,
                 r_cap_dbz=55.0, floor=0.0):
        self.thr, self.fthr, self.fsc, self.wet = thresholds, fss_thr, fss_scales, wet_dbz
        self.rsc, self.rcap, self.floor = r_scales, r_cap_dbz, floor
        self.s = defaultdict(lambda: defaultdict(float))
        self.mi = defaultdict(lambda: defaultdict(float))   # conservazione interna (vs ODYSSEY)
        self.ah = defaultdict(lambda: defaultdict(float))   # accumuli orari (vs CIRRUS)
        self.h = {}
        self.rows = []

    def rain(self, dbz):
        return dbz_to_rain(dbz, self.floor, self.rcap)

    def add(self, key, time, pred, obs, mask, do_fss=True):
        s = self.s[key]
        p, o = pred[mask].astype(np.float64), obs[mask].astype(np.float64)
        wet = (p >= self.wet) | (o >= self.wet)
        pw, ow = p[wet], o[wet]
        e = pw - ow
        n = e.size
        s["n"] += n
        s["se"] += e.sum(); s["sae"] += np.abs(e).sum(); s["sse"] += (e ** 2).sum()
        s["sp"] += pw.sum(); s["so"] += ow.sum()
        s["spp"] += (pw ** 2).sum(); s["soo"] += (ow ** 2).sum(); s["spo"] += (pw * ow).sum()
        for t in self.thr:
            pb, ob = p >= t, o >= t
            s[f"h{t}"] += np.count_nonzero(pb & ob); s[f"m{t}"] += np.count_nonzero(~pb & ob)
            s[f"f{t}"] += np.count_nonzero(pb & ~ob); s[f"c{t}"] += np.count_nonzero(~pb & ~ob)
        # energia alle piccole scale (quanto il campo e' "liscio" rispetto a CIRRUS)
        mf = mask.astype(np.float32)
        for name, F in (("hp", pred), ("ho", obs)):
            Fz = np.where(mask, F, 0).astype(np.float32)
            num = cv2.GaussianBlur(Fz, (0, 0), 2.0)
            den = cv2.GaussianBlur(mf, (0, 0), 2.0)
            hp = Fz - num / np.maximum(den, 1e-6)
            s[name] += float((hp[mask & (den > 0.5)] ** 2).sum())
        # FSS (somme di numeratore e denominatore -> aggregabile)
        if do_fss:
            for t in self.fthr:
                bp = ((pred >= t) & mask).astype(np.float32)
                bo = ((obs >= t) & mask).astype(np.float32)
                for k in self.fsc:
                    m = _box(mf, k)
                    ok = mask & (m > 0)
                    fp = _box(bp, k)[ok] / m[ok]
                    fo = _box(bo, k)[ok] / m[ok]
                    s[f"fssn_{t}_{k}"] += float(((fp - fo) ** 2).sum())
                    s[f"fssd_{t}_{k}"] += float((fp ** 2 + fo ** 2).sum())
            s["n_fss_times"] += 1
        hp_, _ = np.histogram(pw, HIST_BINS); ho_, _ = np.histogram(ow, HIST_BINS)
        hp0, ho0 = self.h.get(key, (0, 0))
        self.h[key] = (hp0 + hp_, ho0 + ho_)
        # massa: volumi e errori di R (mm/h) a piu' scale
        Rp, Ro = self.rain(pred), self.rain(obs)
        vp, vo = float(Rp[mask].sum()), float(Ro[mask].sum())
        s["vol_p"] += vp; s["vol_o"] += vo
        _scale_stats(s, "r", Rp, Ro, mask, self.rsc)
        s["n_times"] += 1
        self.rows.append({"time": time.isoformat(), "method": key[0], "shift_min": key[1],
                          "alpha": key[2], "n_wet": n,
                          "bias": e.mean() if n else np.nan,
                          "rmse": np.sqrt((e ** 2).mean()) if n else np.nan,
                          "corr": np.corrcoef(pw, ow)[0, 1] if n > 2 and pw.std() > 0 and ow.std() > 0 else np.nan,
                          "vol_ratio": vp / vo if vo > 0 else np.nan})

    def add_internal(self, key, val, cov, pi, a, region=None):
        """Conservazione rispetto a ODYSSEY. key = (metodo, alpha)."""
        s = self.mi[key]
        f = pi.cfg.factor
        R = self.rain(val)
        R0 = block_repeat(self.rain(pi.F0), f)
        R1 = block_repeat(self.rain(pi.F1), f)
        regions = {"crop": cov}
        if region is not None:
            regions["region"] = cov & region
        for name, m in regions.items():
            v = float(R[m].sum())
            vref = (1 - a) * float(R0[m].sum()) + a * float(R1[m].sum())
            s[f"{name}_v"] += v; s[f"{name}_vref"] += vref
            s[f"{name}_sae"] += abs(v - vref); s[f"{name}_n"] += 1
        if a == 0:
            # errore del solo upscaling: media 2x2 dell'output contro il pixel ODYSSEY
            m = regions.get("region", cov)
            bR, frac = _blocks(R, m, f)
            ok = frac >= 1.0
            e = (bR[ok] - self.rain(pi.F0)[: bR.shape[0], : bR.shape[1]][ok]).astype(np.float64)
            s["b2_n"] += e.size; s["b2_se"] += e.sum(); s["b2_sae"] += np.abs(e).sum()
            s["b2_sse"] += (e ** 2).sum()
            s["b2_so"] += float(self.rain(pi.F0)[: bR.shape[0], : bR.shape[1]][ok].sum())

    def add_hour(self, key, P, O, valid):
        """Accumulo orario (mm) di previsione P e osservazione O dove `valid`. key = (metodo, shift)."""
        s = self.ah[key]
        s["n_hours"] += 1
        s["vol_p"] += float(P[valid].sum()); s["vol_o"] += float(O[valid].sum())
        _scale_stats(s, "a", P, O, valid, self.rsc)

    def merge(self, other: "Accumulator"):
        for mine, theirs in ((self.s, other.s), (self.mi, other.mi), (self.ah, other.ah)):
            for k, d in theirs.items():
                for kk, v in d.items():
                    mine[k][kk] += v
        for k, (a, b) in other.h.items():
            a0, b0 = self.h.get(k, (0, 0))
            self.h[k] = (a0 + a, b0 + b)
        self.rows.extend(other.rows)

    def to_plain(self):
        return {"s": _to_dict(self.s), "mi": _to_dict(self.mi), "ah": _to_dict(self.ah),
                "h": self.h, "rows": self.rows}

    @classmethod
    def from_plain(cls, d, *args, **kw):
        a = cls(*args, **kw)
        for name in ("s", "mi", "ah"):
            for k, v in d.get(name, {}).items():
                getattr(a, name)[k].update(v)
        a.h, a.rows = d["h"], d["rows"]
        return a

    def summary(self):
        out = []
        for key, s in sorted(self.s.items()):
            n = max(s["n"], 1)
            mp, mo = s["sp"] / n, s["so"] / n
            vp, vo = s["spp"] / n - mp ** 2, s["soo"] / n - mo ** 2
            r = {"method": key[0], "shift_min": key[1], "alpha": key[2],
                 "minutes_from_frame": round(min(key[2], 1 - key[2]) * 15, 2),
                 "n_times": int(s["n_times"]), "n_wet_px": int(s["n"]),
                 "bias": s["se"] / n, "mae": s["sae"] / n, "rmse": np.sqrt(s["sse"] / n),
                 "corr": (s["spo"] / n - mp * mo) / np.sqrt(max(vp * vo, 1e-12)),
                 "hf_energy_ratio": s["hp"] / max(s["ho"], 1e-12)}
            for t in self.thr:
                h, m, f = s[f"h{t}"], s[f"m{t}"], s[f"f{t}"]
                r[f"pod_{t:g}"] = h / max(h + m, 1)
                r[f"far_{t:g}"] = f / max(h + f, 1)
                r[f"csi_{t:g}"] = h / max(h + m + f, 1)
                r[f"fbias_{t:g}"] = (h + f) / max(h + m, 1)
            for t in self.fthr:
                for k in self.fsc:
                    d = s.get(f"fssd_{t}_{k}", 0.0)
                    r[f"fss_{t:g}dBZ_{k}km"] = 1 - s.get(f"fssn_{t}_{k}", 0.0) / d if d > 0 else np.nan
            r["vol_ratio"] = s.get("vol_p", 0.0) / s["vol_o"] if s.get("vol_o", 0) > 0 else np.nan
            _scale_summary(s, "r", self.rsc, r)
            out.append(r)
        return out

    def summary_internal(self):
        out = []
        for (m, a), s in sorted(self.mi.items()):
            r = {"method": m, "alpha": a}
            for name in ("region", "crop"):
                n = s.get(f"{name}_n", 0)
                if not n:
                    continue
                vref = s[f"{name}_vref"]
                r[f"{name}_n_pairs"] = int(n)
                r[f"{name}_vol_ratio"] = s[f"{name}_v"] / vref if vref > 0 else np.nan
                r[f"{name}_mean_abs_rel_err"] = s[f"{name}_sae"] / vref if vref > 0 else np.nan
            if s.get("b2_n", 0):
                n = s["b2_n"]
                r["block2_bias_mmh"] = s["b2_se"] / n
                r["block2_mae_mmh"] = s["b2_sae"] / n
                r["block2_rmse_mmh"] = np.sqrt(s["b2_sse"] / n)
                r["block2_rel_mae"] = s["b2_sae"] / max(s["b2_so"], 1e-12)
            out.append(r)
        return out

    def summary_hourly(self):
        out = []
        for (m, sh), s in sorted(self.ah.items()):
            r = {"method": m, "shift_min": sh, "n_hours": int(s["n_hours"]),
                 "vol_ratio": s["vol_p"] / s["vol_o"] if s["vol_o"] > 0 else np.nan}
            _scale_summary(s, "a", self.rsc, r)
            out.append(r)
        return out


# --------------------------------------------------------------------------- #

def _targets_for_pair(t0, shift_min, dt_in, dt_out, cirrus_times):
    """Istanti CIRRUS T con T+shift in [t0, t0+dt_in): restituisce [(T, alpha)]."""
    out = []
    lo = t0 - dt.timedelta(minutes=shift_min)
    T = floor_time(lo - dt.timedelta(minutes=dt_out), dt_out)
    while T < lo + dt.timedelta(minutes=dt_in):
        a = ((T - t0).total_seconds() / 60 + shift_min) / dt_in
        if 0 <= a < 1 - 1e-9 and T in cirrus_times:
            out.append((T, round(a, 4)))
        T += dt.timedelta(minutes=dt_out)
    return out


def _hour_add(hr, key, Rp, Ro, mask, win):
    """Somma R (mm/h) di un istante a 5 min nell'accumulo dell'ora `hr`."""
    if win is not None:
        Rp, Ro, mask = Rp[win], Ro[win], mask[win]
    e = hr.get(key)
    if e is None:
        hr[key] = [np.where(mask, Rp, 0), np.where(mask, Ro, 0), mask.astype(np.int16), 1]
    else:
        e[0] += np.where(mask, Rp, 0); e[1] += np.where(mask, Ro, 0); e[2] += mask; e[3] += 1


def _hour_merge(a, b):
    for key, e in b.items():
        if key in a:
            for i in range(4):
                a[key][i] = a[key][i] + e[i]
        else:
            a[key] = e


def _hour_finish(acc, hr, n_per_hour):
    """Accumulo orario (mm) = R media sugli istanti disponibili x 1 h, solo dove il pixel
    e' valido in tutti gli istanti. Ore con meno di MIN_HOUR_FRAC istanti scartate."""
    for key, (P, O, W, n) in hr.items():
        if n < MIN_HOUR_FRAC * n_per_hour:
            continue
        acc.add_hour(key, P / n, O / n, W == n)


def _worker(args):
    (pairs, ody_files, cir_files, cfg, shifts, methods, quantity, thr, fthr, fsc,
     wet_dbz, min_wet_frac, region_mask_path, fss_every, reader, r_scales, r_cap_dbz) = args
    acc = Accumulator(thr, fthr, fsc, wet_dbz, r_scales, r_cap_dbz, cfg.dbz_floor)
    src = FrameSource(ody_files, cfg, quantity, reader=reader)
    region = np.load(region_mask_path) if region_mask_path else None
    win = None   # rettangolo della regione: gli accumuli orari si tengono solo li'
    if region is not None and region.any():
        rr, cc = np.nonzero(region)
        win = (slice(rr.min(), rr.max() + 1), slice(cc.min(), cc.max() + 1))
    cir_times = set(cir_files)
    hours: dict = {}
    count = 0
    for t0 in pairs:
        targets = {s: _targets_for_pair(t0, s, cfg.dt_in_min, cfg.dt_out_min, cir_times) for s in shifts}
        if not any(targets.values()):
            continue
        pi = src.pair(t0)
        if pi is None:
            continue
        for k in range(cfg.n_sub):
            a = k / cfg.n_sub
            for m in methods:
                val, cov, _ = pi.get(a, m)
                acc.add_internal((m, round(a, 4)), val, cov, pi, a, region)
        for s, lst in targets.items():
            for T, a in lst:
                try:
                    fr = reader(cir_files[T], quantity)
                except Exception as e:
                    log.warning("CIRRUS %s: %s", T, e)
                    continue
                obs = fr.to_field(cfg.dbz_floor, cfg.rain_threshold_dbz)
                if obs.shape != pi.cov_out.shape:
                    raise ValueError(f"griglie diverse: CIRRUS {obs.shape} vs output {pi.cov_out.shape}")
                obs_cov = np.isfinite(obs)
                # gli istanti asciutti entrano negli accumuli (falsi allarmi di massa),
                # non nelle metriche istantanee
                wet = np.count_nonzero(obs[obs_cov] >= wet_dbz) >= min_wet_frac * obs_cov.sum()
                obs = np.where(obs_cov, obs, cfg.dbz_floor)
                do_fss = (count % fss_every) == 0
                hr = hours.setdefault(floor_time(T, 60), {})
                Ro = acc.rain(obs)
                for m in methods:
                    val, cov, _ = pi.get(a, m)
                    mask = cov & obs_cov
                    if region is not None:
                        mask &= region
                    if wet:
                        acc.add((m, s, a), T, val, obs, mask, do_fss)
                    _hour_add(hr, (m, s), acc.rain(val), Ro, mask, win)
                if wet:
                    count += 1
    # le ore al bordo del blocco possono avere istanti in un altro processo: si
    # restituiscono parziali e le chiude il processo principale
    edge = {min(hours), max(hours)} if hours else set()
    n_per_hour = round(60 / cfg.dt_out_min)
    for H in sorted(hours.keys() - edge):
        _hour_finish(acc, hours[H], n_per_hour)
    return acc.to_plain(), {H: hours[H] for H in edge}


def run_validation(ody_files, cir_files, start, end, out_dir, cfg: DownscaleConfig | None = None,
                   shifts=(0.0, -2.5), methods=("nearest", "linear", "lk"), quantity="DBZH",
                   thresholds=DEFAULT_THRESHOLDS, fss_thr=DEFAULT_FSS_THR,
                   fss_scales=DEFAULT_FSS_SCALES, wet_dbz=10.0, min_wet_frac=0.002,
                   pair_stride=4, fss_every=1, region_mask_path=None, workers=1,
                   reader=read_odim_composite, r_scales=DEFAULT_R_SCALES, r_cap_dbz=55.0):
    """pair_stride: usa una coppia ODYSSEY ogni N (4 = una all'ora). Gli accumuli
    orari richiedono pair_stride=1, altrimenti le ore restano senza istanti.
    region_mask_path: .npy bool (griglia 1 km) per limitare l'area (es. escludere la
    Spagna, che in CIRRUS e' estrapolata con LK).
    r_scales, r_cap_dbz: scale (km) e limite in dBZ per le metriche in R."""
    cfg = cfg or DownscaleConfig()
    os.makedirs(out_dir, exist_ok=True)
    step = dt.timedelta(minutes=cfg.dt_in_min)
    pairs = [t for t in ody_files if start <= t < end and (t + step) in ody_files]
    pairs = pairs[::pair_stride]
    log.info("coppie da valutare: %d", len(pairs))
    if not pairs:
        raise RuntimeError("nessuna coppia ODYSSEY nel periodo")

    # controllo allineamento griglie sulla prima coppia disponibile
    t_c = next((t for t in cir_files if start <= t < end), None)
    if t_c is not None:
        w2 = reader(ody_files[pairs[0]], quantity).where
        w1 = reader(cir_files[t_c], quantity).where
        issues = check_grid_alignment(w2, w1, cfg.factor)
        with open(os.path.join(out_dir, "grid_check.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(issues) if issues else "OK: griglie allineate\n")
        for i in issues:
            log.warning("griglia: %s", i)

    # blocchi contigui: ogni ora di accumulo sta quasi sempre in un solo processo
    chunks = [list(c) for c in np.array_split(np.array(pairs, dtype=object), workers)]
    args = [(c, ody_files, cir_files, cfg, tuple(shifts), tuple(methods), quantity,
             tuple(thresholds), tuple(fss_thr), tuple(fss_scales), wet_dbz, min_wet_frac,
             region_mask_path, fss_every, reader, tuple(r_scales), r_cap_dbz) for c in chunks if c]
    acc_args = (thresholds, fss_thr, fss_scales, wet_dbz, tuple(r_scales), r_cap_dbz, cfg.dbz_floor)
    acc = Accumulator(*acc_args)
    edge_hours: dict = {}
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            results = list(ex.map(_worker, args))
    else:
        results = [_worker(a) for a in args]
    for plain, edges in results:
        acc.merge(Accumulator.from_plain(plain, *acc_args))
        for H, hr in edges.items():
            _hour_merge(edge_hours.setdefault(H, {}), hr)
    for H in sorted(edge_hours):
        _hour_finish(acc, edge_hours[H], round(60 / cfg.dt_out_min))
    return write_reports(acc, out_dir)


def write_reports(acc: Accumulator, out_dir: str):
    summ = acc.summary()
    if summ:
        with open(os.path.join(out_dir, "summary.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in summ for k in r)))
            w.writeheader(); w.writerows(summ)
    if acc.rows:
        with open(os.path.join(out_dir, "per_time.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(acc.rows[0].keys()))
            w.writeheader(); w.writerows(acc.rows)
    for name, rows in (("mass_internal.csv", acc.summary_internal()),
                       ("accum_1h.csv", acc.summary_hourly())):
        if rows:
            fields = list(dict.fromkeys(k for r in rows for k in r))
            with open(os.path.join(out_dir, name), "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader(); w.writerows(rows)
    qq = {}
    for key, (hp, ho) in acc.h.items():
        qs = np.linspace(0.01, 0.999, 60)
        centers = 0.5 * (HIST_BINS[1:] + HIST_BINS[:-1])
        def quant(h):
            c = np.cumsum(h) / max(np.sum(h), 1)
            return np.interp(qs, c, centers).tolist()
        qq["|".join(map(str, key))] = {"q": qs.tolist(), "pred": quant(hp), "obs": quant(ho)}
    with open(os.path.join(out_dir, "qq.json"), "w", encoding="utf-8") as f:
        json.dump(qq, f)
    try:
        from .plots import make_plots
        make_plots(summ, qq, out_dir)
    except Exception as e:  # i grafici non devono bloccare il report
        log.warning("grafici non generati: %s", e)
    return summ
