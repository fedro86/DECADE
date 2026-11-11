"""Monthly VMM radar rain on the ERA5-Land cells over Belgium, for the homogeneity test of the bridge (H3, #20).

Reads every VMM raster under `--vmm-dir` (5 min intensity in mm/h, `opera_ds/vmm.py`), averages it over the
ERA5-Land cells (nearest cell centre, `opera_ds/bridge.py`) and sums it per month. The ERA5-Land grid is the
0.1° grid of `scripts/fetch_cds.py` over its default `--area`; the axes are written to the output so that the
comparison can check them against the ERA5-Land files.

Output `<out>/vmm_monthly_era5grid.npz`: `months` (n, 2: year, month), `sums` (n, cells; mm), `counts`
(rasters per month), `expected` (5 min steps per month), `bel_cells` (flat indices of the cells holding VMM
pixels inside Belgium), `lat`, `lon` (ERA5-Land axes).

    uv run python scripts/vmm_monthly.py --vmm-dir data/vmm --out results/h3_level --processes 16
"""
from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # scripts/ is not a package of opera_ds

from opera_ds.bridge import cell_index, pixel_lonlat  # noqa: E402
from opera_ds.paths import DATA_DIR  # noqa: E402
from opera_ds.vmm import list_rasters, monthly_cell_sums, read_vmm, steps_in_month  # noqa: E402

AREA = (55.0, -3.9, 45.6, 11.8)  # N, W, S, E: default of scripts/fetch_cds.py


def era5land_axes(area=AREA, step: float = 0.1):
    """Latitude (north to south) and longitude axes of the ERA5-Land grid cut to `area` by the CDS."""
    n, w, s, e = area
    lat = np.round(np.arange(round((n - s) / step) + 1) * -step + n, 4)
    lon = np.round(np.arange(round((e - w) / step) + 1) * step + w, 4)
    return lat, lon


_IDX = None
_NCELLS = None


def _init(idx, n_cells):
    global _IDX, _NCELLS
    _IDX, _NCELLS = idx, n_cells


def _chunk(paths):
    return monthly_cell_sums(paths, _IDX, _NCELLS, step_hours=5 / 60)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vmm-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pattern", default="*.h5", help="file name pattern of the rasters (default *.h5)")
    ap.add_argument("--processes", type=int, default=8)
    ap.add_argument("--chunk", type=int, default=2000, help="rasters per task")
    a = ap.parse_args()

    from scripts.make_region_mask import country_geometry, grid_mask

    paths = list_rasters(a.vmm_dir, a.pattern)
    if not paths:
        raise SystemExit(f"no {a.pattern} under {a.vmm_dir}")
    _, where, _ = read_vmm(paths[0])
    lon, lat = pixel_lonlat(where)
    elat, elon = era5land_axes()
    idx = cell_index(elat, elon, lat, lon)
    n_cells = elat.size * elon.size
    bel = grid_mask(where, country_geometry("BEL", str(DATA_DIR / "naturalearth")))
    bel_cells = np.unique(idx[bel])
    print(f"{len(paths)} rasters; {bel.sum()} VMM pixels in Belgium on {bel_cells.size} ERA5-Land cells", flush=True)

    chunks = [paths[i:i + a.chunk] for i in range(0, len(paths), a.chunk)]
    total: dict = {}
    with ProcessPoolExecutor(a.processes, initializer=_init, initargs=(idx, n_cells)) as ex:
        for k, part in enumerate(ex.map(_chunk, chunks), 1):
            for key, (s, c) in part.items():
                if key in total:
                    total[key] = (total[key][0] + s, total[key][1] + c)
                else:
                    total[key] = (s, c)
            print(f"  {k}/{len(chunks)} chunks", flush=True)

    months = sorted(total)
    a.out.mkdir(parents=True, exist_ok=True)
    out = a.out / "vmm_monthly_era5grid.npz"
    np.savez_compressed(
        out,
        months=np.array(months),
        sums=np.stack([total[m][0] for m in months]),
        counts=np.array([total[m][1] for m in months]),
        expected=np.array([steps_in_month(y, m, 5) for y, m in months]),
        bel_cells=bel_cells,
        lat=elat,
        lon=elon,
    )
    for (y, m), c in zip(months, [total[k][1] for k in months]):
        print(f"{y}-{m:02d}: {c} / {steps_in_month(y, m, 5)} rasters")
    print(out)


if __name__ == "__main__":
    main()
