"""T8 (#86): GPU memory and time of one IRENE forecast of the whole DECADE domain, against the ensemble size.

IRENE's own `RadarLightningModel.predict` (IT4LIA-FBK-Seminar, module2-irene-nowcasting) is called unchanged on 6
CIRRUS frames of the Belgian crop (956 x 998 at 1 km, padded by `predict` to 960 x 1024), with the pre-trained
weights `it4lia/irene` from HuggingFace. `predict` runs without gradients and decodes the members one after the
other.

Two steps, each with its own environment:

1. Input, with DECADE's environment (reads the crops with `opera_ds`): six consecutive frames ending at `--end`,
   rain rate from Marshall-Palmer as in `opera_ds.clean.rain_rate`, NaN outside coverage:

     uv run python scripts/irene_inference_cost.py --make-input --end 2024-07-05T22:45 --out results/irene_inference

   -> <out>/cirrus_6frames.npy (6, 956, 998) float32 mm/h, and cirrus_6frames.json (files and times).

2. Measurement, with the Python of the IRENE environment of T0 (`docs/usage.md`), alone on the GPU:

     <IRENE>/.venv/Scripts/python.exe scripts/irene_inference_cost.py \
       --input results/irene_inference/cirrus_6frames.npy --out results/irene_inference

   For each forecast length (12 and 24 steps of 5 min) and ensemble size K (1, 5, 10, 15, 20, 25), fp32: one
   warm-up forecast, then `--reps` timed forecasts. Per case: wall time of `predict` with `torch.cuda.synchronize()`
   (from rain rate in to rain rate out, with the copy of the members to the CPU), the time of the model's forward
   pass alone, the peak memory allocated and reserved by PyTorch (reset before each case), and the peak GPU memory
   in use by `nvidia-smi` (CUDA context and the other processes included), polled during the case. A case that runs
   out of GPU memory is recorded as such. Then the same on the central 256 x 256 patch with K = 10, to compare with
   T0. Writes <out>/stats.json and <out>/irene_inference_cost.png.

`--random-weights` builds the model from IRENE's defaults without downloading the weights: only to check the
script, never for the numbers.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gc
import json
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

STEP_MIN = 5
N_PAST = 6
PATCH = 256


# --- step 1: input, DECADE environment ---------------------------------------------------------------------------

def make_input(cirrus: Path, end: dt.datetime, out: Path) -> Path:
    from opera_ds.clean import rain_rate
    from opera_ds.odim_io import read_odim_composite

    times = [end - dt.timedelta(minutes=STEP_MIN * k) for k in range(N_PAST - 1, -1, -1)]
    frames, files = [], []
    for t in times:
        path = cirrus / f"{t:%Y}" / f"{t:%m}" / f"OPERA@{t:%Y%m%dT%H%M}@0@DBZH.h5"
        if not path.exists():
            raise SystemExit(f"missing frame {path}: the {N_PAST} frames must be consecutive")
        fr = read_odim_composite(str(path))
        rr = rain_rate(fr.to_field(0.0)).astype(np.float32)
        rr[~fr.coverage] = np.nan
        frames.append(rr)
        files.append(path.name)
    past = np.stack(frames)
    out.mkdir(parents=True, exist_ok=True)
    npy = out / "cirrus_6frames.npy"
    np.save(npy, past)
    wet = float(np.nanmean(past[-1] >= 0.1))
    meta = {"files": files, "times_utc": [t.isoformat() for t in times], "shape": list(past.shape),
            "units": "mm/h", "wet_share_last_frame_ge_0.1": wet,
            "outside_coverage_share": float(np.isnan(past).mean())}
    (out / "cirrus_6frames.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"{npy}: {past.shape}, wet share (>= 0.1 mm/h) in the last frame {wet:.3f}")
    return npy


# --- step 2: measurement, IRENE environment ------------------------------------------------------------------------

def _smi(query: str, kind: str = "gpu") -> list[str]:
    arg = f"--query-{kind}={query}"
    res = subprocess.run(["nvidia-smi", arg, "--format=csv,noheader,nounits"], capture_output=True, text=True,
                         check=True)
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


class SmiPeak:
    """Peak of `nvidia-smi` memory.used (MiB) on GPU 0, polled in a thread."""

    def __init__(self, every: float = 0.2):
        self.every, self.peak, self._stop = every, 0, threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            self.peak = max(self.peak, int(_smi("memory.used")[0]))
            self._stop.wait(self.every)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        self.peak = max(self.peak, int(_smi("memory.used")[0]))


def other_gpu_jobs() -> list[str]:
    """Compute processes on the GPU other than the desktop: on Windows `nvidia-smi` also lists every graphical
    application, so only Python and known compute programs count."""
    rows = _smi("pid,process_name", kind="compute-apps")
    return [r for r in rows if any(k in r.lower() for k in ("python", "jupyter", "torch", "cuda"))]


def load_model(args):
    import torch
    from convgru_ensemble.lightning_model import RadarLightningModel

    info: dict = {"repo": args.repo}
    if args.random_weights:
        model = RadarLightningModel(input_channels=1, num_blocks=5, ensemble_size=10, noisy_decoder=True,
                                    forecast_steps=12, loss_class="crps")
        info.update(revision=None, weights="random (script check only)")
        return model.to("cuda"), info
    from huggingface_hub import HfApi, hf_hub_download

    revision = args.revision or HfApi().model_info(args.repo).sha
    ckpt = hf_hub_download(repo_id=args.repo, filename="model.ckpt", revision=revision)
    cfg = hf_hub_download(repo_id=args.repo, filename="config.json", revision=revision)
    info.update(revision=revision, weights=str(ckpt), checkpoint_bytes=Path(ckpt).stat().st_size,
                config=json.loads(Path(cfg).read_text(encoding="utf-8")))
    model = RadarLightningModel.from_checkpoint(ckpt, device="cuda")
    info["hparams"] = {k: str(v) for k, v in model.hparams.items()}
    return model, info


class ForwardTimer:
    """Time of the model's forward pass alone (encoder and all decoders), from hooks on `model.model`."""

    def __init__(self, module):
        import torch

        self.times, self._t0 = [], 0.0

        def pre(_m, _a):
            torch.cuda.synchronize()
            self._t0 = time.perf_counter()

        def post(_m, _a, _o):
            torch.cuda.synchronize()
            self.times.append(time.perf_counter() - self._t0)

        self._h = [module.register_forward_pre_hook(pre), module.register_forward_hook(post)]


def measure(model, past: np.ndarray, steps: int, k: int, reps: int, fwd: ForwardTimer) -> dict:
    import torch

    row = {"H": past.shape[1], "W": past.shape[2], "steps": steps, "minutes": steps * STEP_MIN, "K": k}
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    times = []
    smi = SmiPeak()
    try:
        with smi:
            model.predict(past, forecast_steps=steps, ensemble_size=k)          # warm-up
            fwd.times.clear()
            for _ in range(reps):
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                preds = model.predict(past, forecast_steps=steps, ensemble_size=k)
                torch.cuda.synchronize()
                times.append(time.perf_counter() - t0)
                del preds
        row.update(oom=False, predict_s=times, forward_s=list(fwd.times),
                   predict_s_median=float(np.median(times)), predict_s_min=float(np.min(times)),
                   predict_s_max=float(np.max(times)), forward_s_median=float(np.median(fwd.times)))
    except torch.cuda.OutOfMemoryError as e:
        row.update(oom=True, error=str(e).splitlines()[0])
    gib = 2**30
    row.update(max_allocated_GiB=torch.cuda.max_memory_allocated() / gib,
               max_reserved_GiB=torch.cuda.max_memory_reserved() / gib,
               smi_peak_MiB=smi.peak,
               output_GiB=k * steps * row["H"] * row["W"] * 4 / gib)
    gc.collect()
    torch.cuda.empty_cache()
    shown = "OUT OF MEMORY" if row["oom"] else (
        f"{row['predict_s_median']:.2f} s (forward {row['forward_s_median']:.2f} s), "
        f"allocated {row['max_allocated_GiB']:.2f} GiB, reserved {row['max_reserved_GiB']:.2f} GiB, "
        f"nvidia-smi {row['smi_peak_MiB']} MiB")
    print(f"{row['H']}x{row['W']} K={k:2d} {steps * STEP_MIN:3d} min: {shown}", flush=True)
    return row


def figure(stats: dict, path: Path, total_gib: float) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in stats["rows"] if r["case"] == "domain"]
    fig, (ax_t, ax_m) = plt.subplots(1, 2, figsize=(10, 4.2))
    colours = ("tab:blue", "tab:orange", "tab:green", "tab:red")
    for minutes, colour in zip(sorted({r["minutes"] for r in rows}), colours):
        ok = sorted((r for r in rows if r["minutes"] == minutes and not r["oom"]), key=lambda r: r["K"])
        if not ok:
            continue
        k = [r["K"] for r in ok]
        med = np.array([r["predict_s_median"] for r in ok])
        err = [med - [r["predict_s_min"] for r in ok], [r["predict_s_max"] for r in ok] - med]
        ax_t.errorbar(k, med, yerr=err, marker="o", color=colour, capsize=3, label=f"{minutes} min")
        ax_m.plot(k, [r["max_reserved_GiB"] for r in ok], marker="o", color=colour,
                  label=f"{minutes} min, reserved by PyTorch")
        ax_m.plot(k, [r["smi_peak_MiB"] / 1024 for r in ok], marker="s", ls="--", color=colour,
                  label=f"{minutes} min, nvidia-smi")
        for r in rows:
            if r["minutes"] == minutes and r["oom"]:
                ax_m.plot(r["K"], total_gib, marker="x", ms=10, color=colour)
    ax_m.axhline(total_gib, color="k", lw=1)
    ax_m.text(1, total_gib, f" RTX 4090, {total_gib:.0f} GiB", va="bottom", ha="left", fontsize=8)
    ax_m.set_ylim(0, total_gib * 1.12)
    ax_t.set(xlabel="ensemble members K", ylabel="time per forecast (s), median, min-max",
             title="Time, whole domain 956 x 998 km")
    ax_m.set(xlabel="ensemble members K", ylabel="peak GPU memory (GiB)", title="Memory, whole domain")
    ax_t.set_ylim(bottom=0)
    ax_t.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    ax_m.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    for ax in (ax_t, ax_m):
        ax.grid(alpha=0.3)
        ax.set_xticks(sorted({r["K"] for r in rows}))
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run(args) -> None:
    import torch

    others = other_gpu_jobs()
    if others and not args.force:
        raise SystemExit(f"other jobs on the GPU, the measurement must run alone: {others} (--force to ignore)")
    baseline = int(_smi("memory.used")[0])
    name, driver, total = _smi("name,driver_version,memory.total")[0].split(", ")
    past = np.load(args.input).astype(np.float32)
    meta_path = Path(args.input).with_suffix(".json")
    model, weights = load_model(args)
    fwd = ForwardTimer(model.model)
    irene_dir = Path(sys.modules["convgru_ensemble"].__file__).resolve().parents[1]
    irene_commit = subprocess.run(["git", "-C", str(irene_dir), "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
    stats = {
        "date": dt.datetime.now().isoformat(timespec="seconds"),
        "gpu": name, "driver": driver, "gpu_total_MiB": int(total), "smi_baseline_MiB": baseline,
        "other_gpu_jobs": others, "python": platform.python_version(), "torch": torch.__version__,
        "cuda": torch.version.cuda, "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "float32_matmul_precision": torch.get_float32_matmul_precision(), "precision": "fp32",
        "irene_code": f"{irene_dir} @ {irene_commit}", "weights": weights,
        "input": str(args.input), "input_meta": json.loads(meta_path.read_text()) if meta_path.exists() else None,
        "reps": args.reps, "rows": [],
    }
    for steps in args.steps:
        for k in args.ensemble:
            stats["rows"].append({"case": "domain", **measure(model, past, steps, k, args.reps, fwd)})
    if not args.no_reference:
        h, w = past.shape[1:]
        y0, x0 = (h - PATCH) // 2, (w - PATCH) // 2
        patch = np.ascontiguousarray(past[:, y0:y0 + PATCH, x0:x0 + PATCH])
        for steps in args.steps:
            stats["rows"].append({"case": "patch", "patch_corner": [y0, x0],
                                  **measure(model, patch, steps, 10, args.reps, fwd)})
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    figure(stats, args.out / "irene_inference_cost.png", int(total) / 1024)
    print(f"written {args.out / 'stats.json'} and {args.out / 'irene_inference_cost.png'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("results/irene_inference"))
    ap.add_argument("--make-input", action="store_true", help="step 1, with DECADE's environment")
    ap.add_argument("--cirrus", type=Path, default=Path("data/cirrus_bel"))
    ap.add_argument("--end", default="2024-07-05T22:45", help="time of the last of the 6 frames (UTC)")
    ap.add_argument("--input", type=Path, help="step 2: the .npy written by --make-input")
    ap.add_argument("--repo", default="it4lia/irene")
    ap.add_argument("--revision", help="HuggingFace revision; default: the current one, recorded")
    ap.add_argument("--ensemble", type=int, nargs="+", default=[1, 5, 10, 15, 20, 25])
    ap.add_argument("--steps", type=int, nargs="+", default=[12, 24], help="forecast steps of 5 min")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--no-reference", action="store_true", help="skip the 256 x 256 patch with K = 10")
    ap.add_argument("--random-weights", action="store_true", help="no download; to check the script only")
    ap.add_argument("--force", action="store_true", help="run even with other jobs on the GPU")
    args = ap.parse_args()
    if args.make_input:
        make_input(args.cirrus, dt.datetime.fromisoformat(args.end), args.out)
    elif args.input is None:
        ap.error("--input is required for the measurement (or --make-input for step 1)")
    else:
        run(args)


if __name__ == "__main__":
    main()
