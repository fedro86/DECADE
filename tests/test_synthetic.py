"""Test end-to-end su dati sintetici con moto noto.

Verita' 1 km / 2.5 min: campo multiscala (spettro a legge di potenza) avvettato da un
moto rigido (traslazione + rotazione) con crescita/decadimento euleriani.
  "CIRRUS"  : verita' a 1 km, etichetta T  = stato al tempo T
  "ODYSSEY" : media 2x2 a 2 km, etichetta NT = stato al tempo NT + 2.5 min
              (imita la finestra [NT-10, NT+5] contro (NT-10, NT])
La validazione deve quindi trovare lo shift ottimo a -2.5 min, LK deve battere
nearest e linear negli istanti interpolati, e i default (correzione di massa e
blending in R) devono conservare il volume di pioggia di "ODYSSEY".

Uso:  python tests/test_synthetic.py [outdir]
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys
import tempfile
import time

import numpy as np
from scipy.ndimage import map_coordinates

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from opera_ds import DownscaleConfig, Frame, LKParams, estimate_motion  # noqa: E402
from opera_ds import pipeline as pl  # noqa: E402
from opera_ds.validate import run_validation  # noqa: E402
from opera_ds.sampling import SamplerConfig, block_times, sample_block  # noqa: E402
from opera_ds.windows import Window, WindowStore, dbz_to_rr, make_window  # noqa: E402

NY, NX = 600, 800             # griglia fine (1 km)
FLOOR, DET = 0.0, 12.0        # undetect sotto DET dBZ
U = np.array([0.9, 0.4])      # traslazione [px 1km / min]  (~60 km/h verso ESE)
OMEGA = np.deg2rad(0.1)       # rotazione [rad / min] (periodo 60 h)
T0 = dt.datetime(2024, 8, 1, 0, 0)
DURATION_MIN = 240


def powerlaw_field(ny, nx, beta=3.2, seed=0):
    rng = np.random.default_rng(seed)
    ky = np.fft.fftfreq(ny)[:, None]; kx = np.fft.fftfreq(nx)[None, :]
    k = np.sqrt(kx ** 2 + ky ** 2); k[0, 0] = 1
    amp = k ** (-beta / 2); amp[0, 0] = 0
    f = np.fft.ifft2(amp * np.exp(2j * np.pi * rng.random((ny, nx)))).real
    return (f - f.mean()) / f.std()


PAD = 500
BASE = 22 + 13 * powerlaw_field(NY + 2 * PAD, NX + 2 * PAD, seed=1)
GROW = powerlaw_field(NY + 2 * PAD, NX + 2 * PAD, beta=5.0, seed=2)


def truth(tmin: float) -> np.ndarray:
    """Stato al tempo tmin [min] sulla griglia fine (senza soglia)."""
    yy, xx = np.mgrid[0:NY, 0:NX].astype(float)
    c = np.array([NX / 2, NY / 2])
    J = np.array([[0, -1], [1, 0]])
    xs = c + J @ U / OMEGA                         # punto fisso del moto rigido
    ang = -OMEGA * tmin
    R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
    d = np.stack([xx - xs[0], yy - xs[1]])
    x0 = xs[0] + R[0, 0] * d[0] + R[0, 1] * d[1]
    y0 = xs[1] + R[1, 0] * d[0] + R[1, 1] * d[1]
    f = map_coordinates(BASE, [y0 + PAD, x0 + PAD], order=3, mode="nearest")
    g = map_coordinates(GROW, [yy + PAD, xx + PAD], order=1)
    return (f + 8 * np.sin(2 * np.pi * tmin / 180) * g).astype(np.float32)


def coverage_fine():
    yy, xx = np.mgrid[0:NY, 0:NX]
    radars = [(150, 200), (420, 180), (300, 450), (120, 620), (480, 640), (300, 780)]
    cov = np.zeros((NY, NX), bool)
    for y, x in radars:
        cov |= (yy - y) ** 2 + (xx - x) ** 2 < 175 ** 2
    return cov


COV1 = coverage_fine()
COV2 = COV1.reshape(NY // 2, 2, NX // 2, 2).all(axis=(1, 3))


def make_frame(f, cov, t):
    und = (f < DET) & cov
    return Frame(t, np.where(und, FLOOR, f).astype(np.float32), cov.copy(), und, {})


def npz_reader(path, quantity="DBZH", extent=None, scale=2000.0):
    """Lettore dei file sintetici; `extent` (metri dall'angolo UL) come read_odim_composite."""
    d = np.load(path)
    t = dt.datetime.fromisoformat(str(d["time"]))
    v, c, u = d["values"], d["coverage"], d["undetect"]
    if extent is not None:
        x0, y0, w, h = (int(round(e / scale)) for e in extent)
        v, c, u = (a[y0:y0 + h, x0:x0 + w] for a in (v, c, u))
    return Frame(t, v, c, u, {})


def save(fr: Frame, path):
    np.savez(path, values=fr.values, coverage=fr.coverage, undetect=fr.undetect,
             time=fr.time.isoformat())


def build_archive(root):
    ody, cir = {}, {}
    os.makedirs(os.path.join(root, "ody"), exist_ok=True)
    os.makedirs(os.path.join(root, "cir"), exist_ok=True)
    for m in range(0, DURATION_MIN + 1, 5):
        t = T0 + dt.timedelta(minutes=m)
        p = os.path.join(root, "cir", f"{t:%Y%m%d%H%M}.npz")
        save(make_frame(truth(m), COV1, t), p)
        cir[t] = p
        if m % 15 == 0:
            f2 = truth(m + 2.5).reshape(NY // 2, 2, NX // 2, 2).mean(axis=(1, 3))
            p = os.path.join(root, "ody", f"{t:%Y%m%d%H%M}.npz")
            save(make_frame(f2, COV2, t), p)
            ody[t] = p
    return ody, cir


def test_motion():
    """Errore del campo LK rispetto al moto vero (griglia 2 km, px/15 min)."""
    f = [np.where(COV2, truth(m).reshape(NY // 2, 2, NX // 2, 2).mean(axis=(1, 3)), np.nan)
         for m in (0, 15, 30)]
    f = [np.where(np.isfinite(a) & (a < DET), FLOOR, a).astype(np.float32) for a in f]
    V, info = estimate_motion(f, LKParams())
    yy, xx = np.mgrid[0:NY // 2, 0:NX // 2].astype(float)
    c = np.array([NX / 4, NY / 4])
    # velocita' vera su griglia 2 km per 15 min, valutata a meta' intervallo
    vx = (U[0] - OMEGA * 2 * (yy - c[1])) * 15 / 2
    vy = (U[1] + OMEGA * 2 * (xx - c[0])) * 15 / 2
    m = COV2 & (f[1] > 20)
    err = np.hypot(V[0] - vx, V[1] - vy)[m]
    spd = np.hypot(vx, vy)[m]
    print(f"[moto] vettori {info} | |V| medio {spd.mean():.2f} px/15min | "
          f"errore medio {err.mean():.2f}, p90 {np.percentile(err, 90):.2f} px/15min")
    return err.mean() / spd.mean()


def main(out):
    os.makedirs(out, exist_ok=True)
    rel = test_motion()
    assert rel < 0.35, f"errore relativo del moto troppo alto: {rel:.2f}"

    root = tempfile.mkdtemp(dir=out)
    ody, cir = build_archive(root)

    cfg = DownscaleConfig(dbz_floor=FLOOR)
    t = time.time()
    summ = run_validation(ody, cir, T0, T0 + dt.timedelta(minutes=DURATION_MIN), out, cfg,
                          shifts=(0.0, -2.5, -5.0, 2.5), pair_stride=1, reader=npz_reader,
                          methods=("nearest", "linear", "lk", "lk:Z", "lk:dB"),
                          fss_scales=(1, 5, 11, 21, 41), min_wet_frac=0.0)
    print(f"[validazione] {time.time() - t:.1f} s")

    def get(m, s, a):
        return next(r for r in summ if r["method"] == m and r["shift_min"] == s and abs(r["alpha"] - a) < 1e-3)

    print(f"{'metodo':8s} {'shift':>6s} {'alpha':>6s} {'RMSE':>6s} {'bias':>6s} {'CSI20':>6s} "
          f"{'CSI30':>6s} {'FSS20@11':>8s} {'HF':>5s}")
    for r in summ:
        print(f"{r['method']:8s} {r['shift_min']:+6.1f} {r['alpha']:6.3f} {r['rmse']:6.2f} "
              f"{r['bias']:+6.2f} {r['csi_20']:6.3f} {r['csi_30']:6.3f} "
              f"{r['fss_20dBZ_11km']:8.3f} {r['hf_energy_ratio']:5.2f}")

    # controlli
    shifts = sorted({r["shift_min"] for r in summ})
    best = min(shifts, key=lambda s: np.mean([r["rmse"] for r in summ if r["method"] == "lk" and r["shift_min"] == s]))
    assert best == -2.5, f"shift stimato {best}, atteso -2.5"
    for a in (1 / 6, 1 / 2, 5 / 6):
        lk, lin, nn = get("lk", -2.5, a), get("linear", -2.5, a), get("nearest", -2.5, a)
        assert lk["rmse"] < lin["rmse"] and lk["rmse"] < nn["rmse"], (a, lk["rmse"], lin["rmse"], nn["rmse"])
        assert lk["csi_30"] > lin["csi_30"], a

    # conservazione della massa rispetto a "ODYSSEY" (default: correzione + blending in R)
    with open(os.path.join(out, "mass_internal.csv")) as f:
        mass = {(r["method"], round(float(r["alpha"]), 3)): r for r in csv.DictReader(f)}
    for a in (0.0, 0.333, 0.667):
        ratio = float(mass[("lk", a)]["crop_vol_ratio"])
        print(f"[massa] lk alpha={a:.3f}: volume / riferimento = {ratio:.4f}")
        assert abs(ratio - 1) < 0.02, (a, ratio)
    b2 = float(mass[("lk", 0.0)]["block2_rel_mae"])
    print(f"[massa] errore relativo medio sui blocchi 2x2 ad alpha=0: {b2:.4f}")
    assert b2 < 0.01, b2

    # pipeline di produzione (scrittura su npz al posto di ODIM)
    files = pl.run_downscaling(ody, T0, T0 + dt.timedelta(hours=1), os.path.join(out, "ds"),
                               cfg, overwrite=True, reader=npz_reader,
                               writer=lambda path, fr, q: save(fr, path.replace(".h5", ".npz")))
    files = [p.replace(".h5", ".npz") for p in files]
    times = [npz_reader(p).time for p in files]
    assert [int((t - T0).total_seconds() // 60) for t in times] == list(range(0, 60, 5)), times
    fr = npz_reader(files[1])
    assert fr.values.shape == (NY, NX)
    print(f"[pipeline] {len(files)} file 1 km / 5 min, primo intervallo ok")

    # metadati di produzione ed etichette in convenzione CIRRUS
    captured = {}
    pl.run_downscaling(ody, T0 + dt.timedelta(minutes=15), T0 + dt.timedelta(minutes=45),
                       os.path.join(out, "ds_shift"), cfg, overwrite=True, reader=npz_reader,
                       writer=lambda path, fr, q: captured.__setitem__(fr.time, fr.attrs),
                       time_shift_min=-2.5)
    got = [(int((t - T0).total_seconds() // 60), round(at["alpha"], 3)) for t, at in sorted(captured.items())]
    exp = [(15, 0.833), (20, 0.167), (25, 0.5), (30, 0.833), (35, 0.167), (40, 0.5)]
    assert got == exp, got
    print(f"[pipeline] shift -2.5 min: etichette e alpha {got}")

    # finestre per il ML: a alpha=0 devono coincidere col downscaling sul dominio intero
    import zarr
    win = Window(T0 + dt.timedelta(minutes=30), row0=200, col0=300, T=12, H=128, W=128)
    rr, alpha, times = make_window(ody, win, cfg, context_km=60, reader=npz_reader)
    assert rr.shape == (12, 128, 128) and np.isfinite(rr).any()
    assert np.allclose(alpha, [0, 1 / 3, 2 / 3] * 4), alpha
    full = pl.FrameSource(ody, cfg, reader=npz_reader).pair(win.t_start)
    val, cov, _ = full.get(0.0, "lk")
    ref = np.where(cov, dbz_to_rr(val, FLOOR), np.nan)[200:328, 300:428]
    both = np.isfinite(ref) & np.isfinite(rr[0])
    assert both.mean() > 0.5 and np.allclose(rr[0][both], ref[both], rtol=1e-5, atol=1e-6), \
        np.nanmax(np.abs(rr[0] - ref))
    store = WindowStore(os.path.join(out, "windows.zarr"), 12, 128, 128, {"test": True})
    store.append(rr, alpha, times, win.row0, win.col0)
    store.append(rr, alpha, times, win.row0, win.col0)
    g = zarr.open_group(os.path.join(out, "windows.zarr"), mode="r")
    assert g["RR"].shape == (2, 12, 128, 128) and g["RR"].dtype == np.float16
    assert int(g["time"][1, 0]) == int((win.t_start - dt.datetime(1970, 1, 1)).total_seconds())
    # float16: errore relativo di arrotondamento sotto 1e-3
    rel = np.nanmax(np.abs(np.asarray(g["RR"][0, 0], np.float32) - rr[0]) / np.maximum(rr[0], 1e-3))
    assert rel < 1e-3, rel
    print(f"[finestre] {g['RR'].shape} float16, alpha {alpha[:3]}, coincide col dominio intero ad alpha=0")

    test_sampler(ody, cfg)
    print("TUTTI I TEST SUPERATI")


def test_sampler(ody, cfg):
    """Campionatore su "ODYSSEY" a 2 km: buchi, frazione di NaN, indipendenza dai blocchi."""
    scfg = SamplerConfig(T=12, H=128, W=128, step_px=16, max_nan_frac=0.2, q_min=1.0)
    n = scfg.frames_needed
    assert n == 5, n
    end = T0 + dt.timedelta(minutes=DURATION_MIN - (n - 1) * 15 + 1)
    gap = dict(ody)
    del gap[T0 + dt.timedelta(minutes=60)]

    def run(block_days, files):
        rows = []
        for times, k in block_times(T0, end, scfg, block_days):
            rows += sample_block(files, times, k, scfg, seed=0, reader=npz_reader)[0]
        return rows

    full = run(1.0, ody)
    split = run(1 / 24, ody)          # blocchi di un'ora
    key = lambda r: (r["t_start"], r["row0"], r["col0"])
    assert sorted(map(key, full)) == sorted(map(key, split)), (len(full), len(split))
    starts = sorted({r["t_start"] for r in full})
    assert len(starts) == (DURATION_MIN // 15) - n + 2, starts
    # frazione di NaN contro il calcolo diretto
    r = full[len(full) // 2]
    t = dt.datetime.fromisoformat(r["t_start"])
    i, j = r["row0"] // 2, r["col0"] // 2
    cov = np.stack([npz_reader(ody[t + k * dt.timedelta(minutes=15)]).coverage for k in range(n)])
    direct = 1 - cov[:, i:i + 64, j:j + 64].mean()
    assert abs(direct - r["nan_frac"]) < 1e-6, (direct, r["nan_frac"])
    assert all(x["nan_frac"] <= 0.2 for x in full)
    # buco a T0+60: escluse le partenze da T0 a T0+60
    holed = run(1.0, gap)
    bad = {(T0 + dt.timedelta(minutes=m)).isoformat(timespec="minutes") for m in (0, 15, 30, 45, 60)}
    assert holed and not bad & {x["t_start"] for x in holed}
    # le finestre scelte si producono davvero
    x = holed[0]
    w = Window(dt.datetime.fromisoformat(x["t_start"]), x["row0"], x["col0"], T=12, H=128, W=128)
    assert make_window(gap, w, cfg, context_km=60, reader=npz_reader, domain_fine=(NY, NX)) is not None
    print(f"[campionatore] {len(full)} finestre su {len(starts)} partenze, uguali con blocchi di 1 h; "
          f"buco escluso ({len(holed)} finestre)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "synthetic_out")
