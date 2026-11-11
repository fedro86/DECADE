"""Hourly VMM radar rain on the ERA5-Land cells over Belgium, for the homogeneity test of the bridge (H3, #20).

Reads every VMM raster under `--vmm-dir` (5 min intensity in mm/h, `opera_ds/vmm.py`), averages it over the
ERA5-Land cells (nearest cell centre, `opera_ds/bridge.py`) and sums it per hour on the Belgian cells, so that
the comparison can use, on both sides, only the hours in which VMM is complete. The ERA5-Land grid is the
0.1° grid of `scripts/fetch_cds.py` over its default `--area`; the axes are written to the output so that the
comparison can check them against the ERA5-Land files.

Output `<out>/vmm_hourly_era5grid.npz`: `hours` (n, datetime64[h], end of the hour), `sums` (n, Belgian
cells; mm), `counts` (rasters per hour; 12 = complete), `bel_cells` (flat indices of the ERA5-Land cells holding
VMM pixels inside Belgium, the columns of `sums`), `lat`, `lon` (ERA5-Land axes).

    uv run python scripts/vmm_hourly.py --vmm-dir data/vmm --out results/h3_level --processes 16
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
from opera_ds.vmm import hourly_cell_sums, list_rasters, read_vmm  # noqa: E402

AREA = (55.0, -3.9, 45.6, 11.8)  # N, W, S, E: default of scripts/fetch_cds.py


def era5land_axes(area=AREA, step: float = 0.1):
    """Latitude (north to south) and longitude axes of the ERA5-Land grid cut to `area` by the CDS."""
    n, w, s, e = area
    lat = np.round(np.arange(round((n - s) / step) + 1) * -step + n, 4)
    lon = np.round(np.arange(round((e - w) / step) + 1) * step + w, 4)
    return lat, lon


_IDX = None
_NCELLS = None
_CELLS = None


def _init(idx, n_cells, cells):
    global _IDX, _NCELLS, _CELLS
    _IDX, _NCELLS, _CELLS = idx, n_cells, cells


def _chunk(paths):
    return hourly_cell_sums(paths, _IDX, _NCELLS, _CELLS, step_hours=5 / 60)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vmm-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pattern", default="*.hdf5",
                    help="file name pattern of the rasters (default *.hdf5, as in the project's copy)")
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
    with ProcessPoolExecutor(a.processes, initializer=_init, initargs=(idx, n_cells, bel_cells)) as ex:
        for k, part in enumerate(ex.map(_chunk, chunks), 1):
            for key, (s, c) in part.items():
                if key in total:
                    total[key] = (total[key][0] + s, total[key][1] + c)
                else:
                    total[key] = (s, c)
            print(f"  {k}/{len(chunks)} chunks", flush=True)

    hours = sorted(total)
    a.out.mkdir(parents=True, exist_ok=True)
    out = a.out / "vmm_hourly_era5grid.npz"
    counts = np.array([total[h][1] for h in hours])
    np.savez_compressed(
        out,
        hours=np.array(hours, dtype="datetime64[h]"),
        sums=np.stack([total[h][0] for h in hours]).astype(np.float32),
        counts=counts,
        bel_cells=bel_cells,
        lat=elat,
        lon=elon,
    )
    print(f"{len(hours)} hours, {int((counts == 12).sum())} complete (12 rasters), {int((counts > 12).sum())} with more")
    print(out)


if __name__ == "__main__":
    main()
