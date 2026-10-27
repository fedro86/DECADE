"""Scelta delle finestre per il ML su ODYSSEY a 2 km (schema di importance_sampler di IRENE).

Una finestra di T frame a 1 km / 5 min che parte da un frame ODYSSEY (alpha = 0)
richiede `frames_needed(T)` frame ODYSSEY consecutivi a 15 min. Per ogni posizione
candidata (passi `step_t` frame, `step_px` pixel a 2 km):
  1. si scarta se manca un frame ODYSSEY (buco temporale);
  2. si scarta se la frazione di pixel fuori copertura supera `max_nan_frac`;
  3. si accetta con probabilita' q = min(1, q_min + m * media(1 - exp(-R/s))),
     con R da ODYSSEY convertito come in IRENE (`dbz_to_rr`), `n_rand` estrazioni.
Le somme per cubo si calcolano per frame solo nelle posizioni candidate (integral
image) e si accumulano su una finestra mobile di frame: la memoria resta piccola
anche sull'intero dominio europeo.

Le coordinate in uscita (row0, col0) sono sulla griglia a 1 km dell'intero dominio,
pronte per il sottocomando `windows`.
"""
from __future__ import annotations

import collections
import dataclasses
import datetime as dt
import logging
from typing import Callable

import numpy as np

from .odim_io import read_odim_composite
from .windows import dbz_to_rr

log = logging.getLogger(__name__)


@dataclasses.dataclass
class SamplerConfig:
    T: int = 24                 # frame a 5 min per finestra (come IRENE)
    H: int = 256                # pixel a 1 km
    W: int = 256
    step_t: int = 1             # passo in frame ODYSSEY (1 = ogni 15 min, come IRENE step_T=3 a 5 min)
    step_px: int = 8            # passo in pixel a 2 km (8 = 16 km, come IRENE step_X=16 a 1 km)
    max_nan_frac: float = 10000 / (24 * 256 * 256)   # soglia di IRENE (n_nan=10000)
    q_min: float = 1e-4
    m: float = 0.1
    s: float = 1.0
    n_rand: int = 1
    clip_dbz: float = 60.0
    dbz_floor: float = 0.0
    factor: int = 2             # 2 km -> 1 km
    dt_in_min: float = 15.0
    dt_out_min: float = 5.0

    @property
    def frames_needed(self) -> int:
        return int((self.T - 1) * self.dt_out_min // self.dt_in_min) + 2

    @property
    def hc(self) -> int:
        return self.H // self.factor

    @property
    def wc(self) -> int:
        return self.W // self.factor


def _box_sums(a: np.ndarray, rows: np.ndarray, cols: np.ndarray, h: int, w: int) -> np.ndarray:
    """Somme di `a` sui rettangoli h x w con angolo in (rows, cols), via integral image."""
    ii = np.zeros((a.shape[0] + 1, a.shape[1] + 1), np.float64)
    np.cumsum(np.cumsum(a, axis=0, dtype=np.float64), axis=1, out=ii[1:, 1:])
    r, c = rows[:, None], cols[None, :]
    return ii[r + h, c + w] - ii[r, c + w] - ii[r + h, c] + ii[r, c]


def _frame_sums(fr, cfg: SamplerConfig, rows, cols):
    nan = (~fr.coverage).astype(np.float32)
    rr = dbz_to_rr(np.where(fr.undetect, cfg.dbz_floor, fr.values), cfg.dbz_floor, cfg.clip_dbz)
    g = np.where(fr.coverage, 1 - np.exp(-rr / cfg.s), 0).astype(np.float32)
    return _box_sums(nan, rows, cols, cfg.hc, cfg.wc), _box_sums(g, rows, cols, cfg.hc, cfg.wc)


EPOCH = dt.datetime(1970, 1, 1)


def sample_block(files: dict, times: list, n_starts: int, cfg: SamplerConfig, seed: int,
                 reader: Callable = read_odim_composite, origin_c=(0, 0)):
    """Campiona le finestre che partono ai primi `n_starts` tempi di `times` (tempi
    ODYSSEY attesi a passo dt_in; i successivi servono solo a completare le ultime
    finestre). Il passo `step_t` e' allineato al 1970, quindi i blocchi sono indipendenti.
    origin_c: offset (righe, colonne a 2 km) dell'area letta dentro il dominio.
    Restituisce (righe accettate, statistiche)."""
    rng = np.random.default_rng(seed)
    step = dt.timedelta(minutes=cfg.dt_in_min)
    n = cfg.frames_needed
    starts = set(times[:n_starts])
    win = collections.deque(maxlen=n)     # (somme NaN, somme pioggia) o None se il frame manca
    rows = cols = None
    out, stats = [], collections.Counter()
    cube_px = n * cfg.hc * cfg.wc
    for t in times[:n_starts + n - 1]:
        fr = None
        if t in files:
            try:
                fr = reader(files[t], "DBZH")
            except Exception as e:   # file corrotto -> trattato come mancante
                log.warning("lettura fallita %s: %s", files[t], e)
        if fr is not None and rows is None:
            ny, nx = fr.values.shape
            rows = np.arange(0, ny - cfg.hc + 1, cfg.step_px)
            cols = np.arange(0, nx - cfg.wc + 1, cfg.step_px)
        win.append(None if fr is None else _frame_sums(fr, cfg, rows, cols))
        if len(win) < n:
            continue
        t_start = t - (n - 1) * step
        if t_start not in starts or int((t_start - EPOCH) / step) % cfg.step_t:
            continue
        stats["start_times"] += 1
        if any(w is None for w in win):
            stats["start_times_with_gap"] += 1
            continue
        n_nan = sum(w[0] for w in win)
        nan_frac = n_nan / cube_px
        score = sum(w[1] for w in win) / np.maximum(cube_px - n_nan, 1)
        ok = nan_frac <= cfg.max_nan_frac
        q = np.minimum(1.0, cfg.q_min + cfg.m * score)
        hits = (rng.random((cfg.n_rand,) + q.shape) <= q).sum(axis=0) * ok
        stats["candidates"] += q.size
        stats["valid"] += int(ok.sum())
        for i, j in zip(*np.nonzero(hits)):
            for _ in range(int(hits[i, j])):
                out.append({"t_start": t_start.isoformat(timespec="minutes"),
                            "row0": int(rows[i] + origin_c[0]) * cfg.factor,
                            "col0": int(cols[j] + origin_c[1]) * cfg.factor,
                            "q": round(float(q[i, j]), 6), "rain_score": round(float(score[i, j]), 6),
                            "nan_frac": round(float(nan_frac[i, j]), 6)})
    stats["accepted"] = len(out)
    return out, dict(stats)


def block_times(start: dt.datetime, end: dt.datetime, cfg: SamplerConfig, block_days: float = 7):
    """Blocchi di tempi di partenza [s, e) a passo dt_in. Ogni blocco e' (tempi, n_starts):
    i primi n_starts sono tempi di partenza, gli altri i frame che completano le
    finestre che partono vicino alla fine del blocco."""
    step = dt.timedelta(minutes=cfg.dt_in_min)
    start = start + dt.timedelta(seconds=-(start - EPOCH).total_seconds() % step.total_seconds())
    t, blocks = start, []
    while t < end:
        e = min(t + dt.timedelta(days=block_days), end)
        k = int(np.ceil((e - t) / step))
        blocks.append(([t + i * step for i in range(k + cfg.frames_needed - 1)], k))
        t = t + k * step
    return blocks
