"""Driver: da un archivio ODYSSEY (2 km / 15 min) a compositi 1 km / 5 min."""
from __future__ import annotations

import datetime as dt
import logging
import os
from collections import OrderedDict
from typing import Callable

import numpy as np

from .interp import DownscaleConfig, PairInterpolator
from .motion import estimate_motion, motion_from_sparse, sparse_vectors
from .odim_io import Frame, read_odim_composite, refine_where, write_odim_composite

log = logging.getLogger(__name__)


class FrameSource:
    """Accesso con cache ai campi grossolani indicizzati per tempo."""

    def __init__(self, files: dict[dt.datetime, str], cfg: DownscaleConfig,
                 quantity: str = "DBZH", reader: Callable = read_odim_composite, cache_size: int = 8):
        self.files, self.cfg, self.quantity, self.reader = files, cfg, quantity, reader
        self._cache: OrderedDict = OrderedDict()
        self._sparse: OrderedDict = OrderedDict()
        self.cache_size = cache_size

    def __contains__(self, t):
        return t in self.files

    def frame(self, t: dt.datetime) -> Frame | None:
        if t not in self.files:
            return None
        if t in self._cache:
            self._cache.move_to_end(t)
            return self._cache[t]
        try:
            fr = self.reader(self.files[t], self.quantity)
        except Exception as e:  # file corrotto -> trattato come mancante
            log.warning("lettura fallita %s: %s", self.files[t], e)
            fr = None
        self._cache[t] = fr
        if len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)
        return fr

    def field(self, t):
        fr = self.frame(t)
        return None if fr is None else fr.to_field(self.cfg.dbz_floor, self.cfg.rain_threshold_dbz)

    def motion_for_pair(self, t0: dt.datetime):
        """Moto per la coppia (t0, t0+dt) usando fino a `context_pairs` coppie
        contigue prima e dopo."""
        step = dt.timedelta(minutes=self.cfg.dt_in_min)
        times = [t0, t0 + step]
        for _ in range(self.cfg.context_pairs):
            if self.field(times[0] - step) is None:
                break
            times.insert(0, times[0] - step)
        for _ in range(self.cfg.context_pairs):
            if self.field(times[-1] + step) is None:
                break
            times.append(times[-1] + step)
        if self.cfg.lk.backend == "pysteps":
            return estimate_motion([self.field(t) for t in times], self.cfg.lk)
        sparse = [self._sparse_pair(a) for a in times[:-1]]
        return motion_from_sparse(sparse, self.field(t0).shape, self.cfg.lk)

    def _sparse_pair(self, ta):
        """Vettori LK sparsi della coppia (ta, ta+dt), con cache: ogni coppia
        contribuisce al moto di 2*context_pairs+1 intervalli."""
        if ta not in self._sparse:
            tb = ta + dt.timedelta(minutes=self.cfg.dt_in_min)
            self._sparse[ta] = sparse_vectors(self.field(ta), self.field(tb), self.cfg.lk)
            if len(self._sparse) > self.cache_size:
                self._sparse.popitem(last=False)
        return self._sparse[ta]

    def pair(self, t0: dt.datetime) -> PairInterpolator | None:
        t1 = t0 + dt.timedelta(minutes=self.cfg.dt_in_min)
        F0, F1 = self.field(t0), self.field(t1)
        if F0 is None or F1 is None:
            return None
        V, info = self.motion_for_pair(t0)
        log.debug("%s moto: %s", t0, info)
        return PairInterpolator(F0, F1, V, self.cfg)


def floor_time(t: dt.datetime, minutes: float) -> dt.datetime:
    s = int(minutes * 60)
    epoch = dt.datetime(1970, 1, 1, tzinfo=t.tzinfo)
    return epoch + dt.timedelta(seconds=((t - epoch).total_seconds() // s) * s)


def run_downscaling(files: dict[dt.datetime, str], start: dt.datetime, end: dt.datetime,
                    out_dir: str, cfg: DownscaleConfig | None = None, quantity: str = "DBZH",
                    name_fmt: str = "OPERA_DS_1km_5min_%Y%m%d%H%M.h5",
                    method: str = "lk", overwrite: bool = False,
                    reader: Callable = read_odim_composite,
                    writer: Callable = write_odim_composite) -> list[str]:
    """Genera i compositi 1 km / 5 min tra start (incluso) e end (escluso).
    reader(path, quantity) -> Frame ; writer(path, Frame, quantity)."""
    cfg = cfg or DownscaleConfig()
    src = FrameSource(files, cfg, quantity, reader=reader)
    os.makedirs(out_dir, exist_ok=True)
    step_in = dt.timedelta(minutes=cfg.dt_in_min)
    step_out = dt.timedelta(minutes=cfg.dt_out_min)
    written = []
    t0 = floor_time(start, cfg.dt_in_min)
    while t0 < end:
        fr0 = src.frame(t0)
        if fr0 is None:
            t0 += step_in
            continue
        where = refine_where(fr0.where, cfg.factor)
        pi = src.pair(t0)
        if pi is None:
            log.info("%s: manca t0+%s, scrivo solo l'istante nominale", t0, step_in)
            alphas = [0.0]
            pi = PairInterpolator(src.field(t0), src.field(t0), np.zeros((2,) + fr0.values.shape, np.float32), cfg)
        else:
            alphas = [k / cfg.n_sub for k in range(cfg.n_sub)]
        for k, a in enumerate(alphas):
            t = t0 + k * step_out
            if not (start <= t < end):
                continue
            path = os.path.join(out_dir, t.strftime(name_fmt))
            if os.path.exists(path) and not overwrite:
                written.append(path)
                continue
            val, cov, und = pi.get(a, method)
            writer(path, Frame(t, val, cov, und, where), quantity)
            written.append(path)
        t0 += step_in
    return written


def _chunk_job(args):
    files, s, e, out_dir, cfg, quantity, name_fmt, method, overwrite, reader = args
    return run_downscaling(files, s, e, out_dir, cfg, quantity, name_fmt, method, overwrite, reader)


def run_downscaling_parallel(files, start, end, out_dir, cfg=None, quantity="DBZH",
                             name_fmt="OPERA_DS_1km_5min_%Y%m%d%H%M.h5", method="lk",
                             overwrite=False, workers=4, chunk_days=1,
                             reader: Callable = read_odim_composite):
    """Come run_downscaling, a blocchi di `chunk_days` giorni su piu' processi.
    I frame di contesto ai bordi dei blocchi vengono letti comunque (indice completo).
    `reader` deve essere serializzabile (es. functools.partial di una funzione di modulo)."""
    from concurrent.futures import ProcessPoolExecutor
    cfg = cfg or DownscaleConfig()
    jobs, s = [], start
    while s < end:
        e = min(s + dt.timedelta(days=chunk_days), end)
        jobs.append((files, s, e, out_dir, cfg, quantity, name_fmt, method, overwrite, reader))
        s = e
    out = []
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(_chunk_job, jobs):
            out.extend(r)
    return out
