"""T0 (#34): test training of IRENE (ConvGRU-Ensemble, FBK) on fake data shaped like the DECADE windows.

Runs IRENE's own training code (`convgru_ensemble.train`, IT4LIA-FBK-Seminar, module2-irene-nowcasting) unchanged,
with the DataModule pointed at a fake Zarr store. Only the settings that do not work on native Windows are changed
(DataLoader `fork` -> `spawn`, persistent workers), plus the paths, the batch size and the number of steps.

Fake data, like the training windows of `docs/method.md` (*Window content*): windows of 24 x 256 x 256 frames at
5 min, rain rate `RR` in mm/h, NaN outside coverage, and `alpha` per frame (unused by IRENE). Rain is a few Gaussian
cells moving at constant speed (peaks 0.5-80 mm/h, so that the 60 dBZ clip of IRENE is reached); one window in four
has a strip outside coverage, to exercise IRENE's NaN mask. IRENE reads `RR[t, x, y]` by position and a CSV of the
top-left corners (t, x, y); here window k starts at t = 24 k, x = y = 0.

Must run with the Python of the IRENE environment, not DECADE's (IRENE needs Python >= 3.13 and torch with CUDA):

  <IRENE>/.venv/Scripts/python.exe scripts/irene_t0.py --out results/irene_t0 --batch-size 16 --steps 300

Prints the time per step and the peak GPU memory, and writes them to
<out>/stats_bs<batch>_k<members>_<loss>_<precision>_acc<accumulate>.json.

T9 (#90) runs the same training with other settings: `--loss-class afcrps` (IRENE's `PIXEL_LOSSES`), `--accumulate`
(gradient accumulation), `--no-checkpoints` (no model files written; they are not needed to measure). A case that runs
out of GPU memory writes `"oom": true` instead of the measurements; on Windows the driver may instead spill into shared
system memory and slow down, which `"exceeds_gpu_memory": true` flags (peak above the memory of the GPU). `--table <dir>` prints the stats files of a folder
as a table, with hours per 10^5 optimiser steps:

  <IRENE>/.venv/Scripts/python.exe scripts/irene_t0.py --out results/irene_t9 --ensemble-size 10 --loss-class afcrps \\
      --batch-size 16 --steps 110 --no-checkpoints
  <IRENE>/.venv/Scripts/python.exe scripts/irene_t0.py --table results/irene_t9
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

T, H, W = 24, 256, 256


def fake_window(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """One fake window: (T, H, W) rain rate in mm/h with NaN outside coverage, and alpha (T,)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.zeros((T, H, W), np.float32)
    for _ in range(rng.integers(1, 8)):
        y0, x0 = rng.uniform(-50, H + 50), rng.uniform(-50, W + 50)
        vy, vx = rng.uniform(-4, 4, 2)                   # pixels (km) per 5 min, up to about 50 km/h
        sig = rng.uniform(4, 30)
        peak = float(np.exp(rng.uniform(np.log(0.5), np.log(80.0))))
        for t in range(T):
            d2 = (yy - y0 - vy * t) ** 2 + (xx - x0 - vx * t) ** 2
            rr[t] += peak * np.exp(-d2 / (2 * sig**2))
    rr[rr < 0.05] = 0.0
    if rng.random() < 0.25:                              # strip outside coverage, the same in every frame
        w = int(rng.integers(8, 64))
        rr[:, :, -w:] = np.nan
    alpha = np.tile(np.array([0.0, 1 / 3, 2 / 3], np.float32), T // 3)
    return rr, alpha


def make_fake_store(out: Path, n_windows: int, seed: int = 0) -> tuple[Path, Path]:
    import pandas as pd
    import xarray as xr

    zarr_path, csv_path = out / "fake_windows.zarr", out / "fake_windows.csv"
    if zarr_path.exists() and csv_path.exists():
        found = len(pd.read_csv(csv_path))
        if found != n_windows:
            raise SystemExit(f"{out} already holds {found} fake windows, not {n_windows}: use a new --out")
        return zarr_path, csv_path
    rng = np.random.default_rng(seed)
    rr = np.empty((n_windows * T, H, W), np.float32)
    alpha = np.empty(n_windows * T, np.float32)
    for k in range(n_windows):
        rr[k * T:(k + 1) * T], alpha[k * T:(k + 1) * T] = fake_window(rng)
    ds = xr.Dataset({"RR": (("time", "x", "y"), rr, {"units": "mm/h"}), "alpha": (("time",), alpha)})
    ds.chunk({"time": T, "x": H, "y": W}).to_zarr(zarr_path, mode="w")
    pd.DataFrame({"t": np.arange(n_windows) * T, "x": 0, "y": 0}).to_csv(csv_path, index=False)
    return zarr_path, csv_path


def print_table(folder: Path) -> None:
    """Markdown table of the stats files of `folder`; time per optimiser step = time per batch x accumulate."""
    rows = [json.loads(f.read_text()) for f in sorted(folder.glob("stats_*.json"))]
    rows.sort(key=lambda r: (r["ensemble_size"], r["loss_class"], r["precision"], r["batch_size"], r["accumulate"]))
    print("| K | loss | precision | batch | accumulate | s per batch (median) | s per optimiser step | h per 1e5 steps |"
          " train GiB | val GiB |")
    print("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        head = (f"| {r['ensemble_size']} | {r['loss_class']} | {r['precision']} | {r['batch_size']} |"
                f" {r['accumulate']} |")
        if r["oom"]:
            print(head + " out of memory | | | | |")
            continue
        step = r["step_s_median"] * r["accumulate"]
        spill = " (beyond GPU memory)" if r.get("exceeds_gpu_memory") else ""
        print(head + f" {r['step_s_median']:.3f}{spill} | {step:.3f} | {step * 1e5 / 3600:.1f} |"
              f" {r['train_peak_allocated_GiB']:.1f} | {r['val_peak_allocated_GiB']:.1f} |")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=Path("results/irene_t0"))
    p.add_argument("--windows", type=int, default=400, help="fake windows (90%% train, 5%% val, 5%% test); a store already in --out is reused only if it has this number")
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--steps", type=int, default=300, help="training steps")
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--ensemble-size", type=int, default=2, help="members in training (IRENE default 2)")
    p.add_argument("--precision", default="32-true", help="Lightning precision, e.g. 32-true or bf16-mixed")
    p.add_argument("--loss-class", default="crps", help="IRENE loss, a key of PIXEL_LOSSES: crps, afcrps, mse, mae (T9)")
    p.add_argument("--accumulate", type=int, default=1, help="batches per optimiser step (accumulate_grad_batches, T9)")
    p.add_argument("--no-checkpoints", action="store_true", help="do not write model checkpoints (T9)")
    p.add_argument("--table", type=Path, help="print the stats_*.json of this folder as a table and exit")
    args = p.parse_args()
    if args.table:
        print_table(args.table)
        return
    args.out.mkdir(parents=True, exist_ok=True)

    import fiddle as fdl
    import torch
    from pytorch_lightning.callbacks import Callback

    from convgru_ensemble import train as irene_train

    zarr_path, csv_path = make_fake_store(args.out, args.windows)
    case = f"bs{args.batch_size}_k{args.ensemble_size}_{args.loss_class}_{args.precision}_acc{args.accumulate}"

    class StepStats(Callback):
        """Wall time per training step (CUDA-synchronised) and peak GPU memory, apart for training and validation
        steps (validation uses 10 ensemble members, training `--ensemble-size`)."""

        def __init__(self) -> None:
            self.times: list[float] = []
            self.t0 = 0.0
            self.peak = {"train": 0, "val": 0}

        def _start(self) -> None:
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            self.t0 = time.perf_counter()

        def _end(self, split: str) -> float:
            torch.cuda.synchronize()
            self.peak[split] = max(self.peak[split], torch.cuda.max_memory_allocated())
            return time.perf_counter() - self.t0

        def on_train_batch_start(self, trainer, pl_module, batch, batch_idx) -> None:
            self._start()

        def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx) -> None:
            self.times.append(self._end("train"))

        def on_validation_batch_start(self, trainer, pl_module, batch, batch_idx, dataloader_idx=0) -> None:
            self._start()

        def on_validation_batch_end(self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx=0) -> None:
            self._end("val")

        def on_train_end(self, trainer, pl_module) -> None:
            t = np.array(self.times[10:] or self.times)
            stats = {
                "oom": False,
                "loss_class": args.loss_class,
                "accumulate": args.accumulate,
                "gpu": torch.cuda.get_device_name(0),
                "torch": torch.__version__,
                "batch_size": args.batch_size,
                "ensemble_size": args.ensemble_size,
                "precision": args.precision,
                "steps": len(self.times),
                "step_s_median": float(np.median(t)),
                "step_s_p90": float(np.percentile(t, 90)),
                "train_peak_allocated_GiB": self.peak["train"] / 2**30,
                "val_peak_allocated_GiB": self.peak["val"] / 2**30,
                "val_batch_size": min(args.batch_size, len(trainer.datamodule.val_dataset)),
                "peak_reserved_GiB": torch.cuda.max_memory_reserved() / 2**30,
                "parameters": sum(q.numel() for q in pl_module.parameters()),
                "gpu_total_GiB": torch.cuda.get_device_properties(0).total_memory / 2**30,
            }
            # on Windows the driver may spill into shared system memory instead of failing (T9): flag it
            stats["exceeds_gpu_memory"] = max(stats["train_peak_allocated_GiB"], stats["val_peak_allocated_GiB"],
                                              stats["peak_reserved_GiB"]) > stats["gpu_total_GiB"]
            print("T0 STATS " + json.dumps(stats), flush=True)
            (args.out / f"stats_{case}.json").write_text(json.dumps(stats, indent=1))

    cfg = irene_train.experiment()
    dm = cfg.datamodule
    dm.zarr_path, dm.csv_path = str(zarr_path), str(csv_path)
    dm.batch_size, dm.num_workers = args.batch_size, args.num_workers
    dm.multiprocessing_context = "spawn" if args.num_workers > 0 else None   # no fork on Windows
    dm.persistent_workers = args.num_workers > 0                              # spawn is slow to restart per epoch
    cfg.model.ensemble_size = args.ensemble_size
    cfg.model.loss_class = args.loss_class
    cfg.trainer.accumulate_grad_batches = args.accumulate
    cfg.trainer.max_steps = args.steps
    cfg.trainer.max_epochs = -1
    cfg.trainer.precision = args.precision
    cfg.trainer.log_every_n_steps = 10
    cfg.loggers.tensorboard.save_dir = str(args.out / "logs")
    cfg.loggers.tensorboard.version = case
    cfg.callbacks.step_stats = fdl.Config(StepStats)
    if args.no_checkpoints:                                                   # IRENE needs both callbacks: keep 0 files
        cfg.callbacks.checkpoint_val.save_top_k = 0
        cfg.callbacks.checkpoint_train.save_top_k = 0
    try:
        irene_train.train(cfg)
    except torch.cuda.OutOfMemoryError as e:                                 # recorded, not fatal (T9)
        stats = {"oom": True, "error": str(e).splitlines()[0], "batch_size": args.batch_size,
                 "ensemble_size": args.ensemble_size, "precision": args.precision, "loss_class": args.loss_class,
                 "accumulate": args.accumulate, "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__}
        print("T0 STATS " + json.dumps(stats), flush=True)
        (args.out / f"stats_{case}.json").write_text(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
