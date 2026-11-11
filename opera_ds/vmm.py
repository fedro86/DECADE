"""VMM radar rasters (Flanders Environment Agency) read as frames and summed per month on bridge cells (H3, #20).

The rasters are those of the VMM raster service (KiWIS, `format=hdf5`; docs/data.md, VMM row): one HDF5 file
per time step with an ODIM-like layout,

- `dataset1/data1/data`: 780 × 900 float64, rain intensity in mm/h for `SRI_1km_cappi` or an amount in mm for
  the `PAC_*` accumulations;
- `where`: `projdef` (azimuthal equidistant centred on 51.19° N, 3.48° E), `xscale` = `yscale` = 500 m and the
  corner coordinates, which are the outer edges of the corner pixels (checked on a 1/10/2026 raster);
- `what/date`, `what/time`: the label of the step.

Pixels outside the radar coverage hold −2 (all four corners of the grid, about 10% of it, on the 1/10/2026
raster); they are read as NaN. No other negative value was seen.

`pixel_lonlat` and `cell_index` of `opera_ds.bridge` apply unchanged: VMM pixels (500 m) take the ERA5-Land
cell with the nearest centre and are averaged over it, never the other way round.
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict
from pathlib import Path

import numpy as np

NODATA = -2.0


def read_vmm(path) -> tuple[np.ndarray, dict, dt.datetime]:
    """Values of one VMM raster (NaN outside coverage), its `where` attributes and its UTC label."""
    import h5py

    with h5py.File(path, "r") as f:
        data = f["dataset1/data1/data"][()].astype(np.float64)
        where = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in f["where"].attrs.items()}
        what = f["what"].attrs
        date = what["date"].decode() if isinstance(what["date"], bytes) else str(what["date"])
        time = what["time"].decode() if isinstance(what["time"], bytes) else str(what["time"])
    data[data <= NODATA] = np.nan
    label = dt.datetime.strptime(date + time.zfill(6), "%Y%m%d%H%M%S")
    return data, where, label


def monthly_cell_sums(paths, idx: np.ndarray, n_cells: int, step_hours: float | None, min_valid: float = 1.0):
    """Monthly rain (mm) on the bridge cells from VMM rasters.

    Each raster is averaged over the pixels of each cell (`bridge.cell_mean`), then summed over the month of its
    label. `step_hours` converts an intensity in mm/h into the amount of its step (5/60 for the 5 min
    `SRI_1km_cappi`); `None` means the rasters already hold amounts (`PAC_*`). A raster labelled at 00:00 of the
    first day belongs to the month before, as its step ends there.

    Returns {(year, month): (sum per cell, number of rasters)}; the caller compares the count with the number
    of steps in the month before using a month. A cell below `min_valid` coverage in any raster of the month
    is NaN for that month.
    """
    from opera_ds.bridge import cell_mean

    sums: dict = defaultdict(lambda: np.zeros(n_cells))
    counts: dict = defaultdict(int)
    for p in paths:
        values, _, label = read_vmm(p)
        end_of_step = label - dt.timedelta(microseconds=1)
        key = (end_of_step.year, end_of_step.month)
        mean, _ = cell_mean(values, idx, n_cells, min_valid)
        sums[key] = sums[key] + (mean * step_hours if step_hours is not None else mean)
        counts[key] += 1
    return {k: (sums[k], counts[k]) for k in sorted(sums)}


def steps_in_month(year: int, month: int, step_minutes: int) -> int:
    """Number of steps of `step_minutes` whose end falls in the month."""
    start = dt.datetime(year, month, 1)
    end = dt.datetime(year + (month == 12), month % 12 + 1, 1)
    return int((end - start).total_seconds() // (60 * step_minutes))


def list_rasters(folder: Path, pattern: str = "*.h5") -> list[Path]:
    """VMM rasters under `folder`, sorted by name."""
    return sorted(Path(folder).rglob(pattern))
