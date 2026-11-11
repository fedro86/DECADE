"""Turn the monthly bridge files of `fetch_cds.py` into one Zarr store (S9, #83).

- `era5-land`: hourly amounts in mm (the hour ending at `valid_time`), float32 and lossless, with `expver` for
  every hour (1 final, 5 preliminary). The store is written anew each time, so a rerun after `fetch_cds.py` has
  replaced preliminary months picks up the final data. Details in `opera_ds.bridge.era5land_to_zarr` and
  docs/data.md, *Derived datasets*.

Example (size and time in docs/usage.md, *Measured costs*):
  uv run python scripts/bridge_to_zarr.py --dataset era5-land --src data/era5land_bel --out data/era5land_bel.zarr
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from opera_ds.bridge import era5land_to_zarr


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dataset", choices=["era5-land"], required=True)
    ap.add_argument("--src", type=Path, required=True, help="folder of fetch_cds.py, <src>/<YYYY>/<dataset>_<YYYYMM>.nc")
    ap.add_argument("--out", type=Path, required=True, help="Zarr store, replaced if it exists")
    a = ap.parse_args()

    files = sorted(a.src.glob(f"*/{a.dataset}_*.nc"))
    if not files:
        raise SystemExit(f"no {a.dataset} files in {a.src}")
    t0 = time.time()
    attrs = era5land_to_zarr(files, a.out)
    size = sum(f.stat().st_size for f in a.out.rglob("*") if f.is_file())
    print(json.dumps(attrs, indent=1))
    print(f"{len(files)} files -> {a.out}: {size / 1e9:.2f} GB in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
