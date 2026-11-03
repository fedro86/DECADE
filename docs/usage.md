# Usage

How to run the command-line tools, what they write, and how much they cost.
These are the entry points for batch jobs on HPC. Installation is in the
[README](../README.md); why the tools work the way they do is in
[method.md](method.md).

Every script prints its full options with `--help`.

The examples are written for bash (Linux, macOS, Git Bash). In Windows
PowerShell, end continued lines with a backtick `` ` `` instead of `\`, or
write the command on one line.

## Download

```bash
# whole files from the public ORD bucket
uv run python scripts/fetch_ord_archive.py --product DBZH_QIND \
  --start 2024-07-01 --end 2024-07-06 --out data/odyssey
uv run python scripts/fetch_ord_archive.py --product DBZH \
  --start 2024-07-01 --end 2024-07-06 --out data/cirrus

# only Belgium + 350 km: reads the GeoTIFFs in pieces, or downloads and crops
# the whole HDF5 where there is no GeoTIFF (about 3 h for 12 years of ODYSSEY)
uv run python scripts/fetch_cog_crop.py --product DBZH_QIND \
  --ref "data/odyssey/OPERA@20240702T1200@0@DBZH_QIND.h5" \
  --bbox 2.5 49.45 6.45 51.55 --buffer-km 350 \
  --start 2012-09-01 --end 2024-07-06 --out data/odyssey_bel --threads 32

# Belgium mask on the full CIRRUS 1 km grid (Natural Earth 1:10m)
uv run python scripts/make_region_mask.py --ref "data/cirrus/OPERA@20240702T1205@0@DBZH.h5" \
  --country BEL --out data/mask_BEL_1km.npy
```

`fetch_ord_archive.py --dry-run` prints the number of files and the size
without downloading. Cropped files keep the crop offset in `where`, so they are
read like whole files.

## Validation against CIRRUS

```bash
uv run python scripts/opera_ds_cli.py validate \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" --cirrus-glob "data/cirrus/*@DBZH.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --start 2024-07-01 --end 2024-07-06 \
  --bbox 2.5 49.45 6.45 51.55 --buffer-km 200 --region-mask data/mask_BEL_1km.npy \
  --shifts 0 -2.5 -5 2.5 --methods nearest linear lk lk:dB \
  --pair-stride 1 --workers 12 --out results/val_2024-07_BEL
```

About 21 min with 12 processes for these 4 days. Output folder:

| file | content |
|---|---|
| `summary.csv` | scores by method, shift and `alpha`: dBZ scores, categorical scores, FSS, small-scale energy, `r*` columns in R by scale (1, 2, 5, 10, 25 km) |
| `mass_internal.csv` | conservation against ODYSSEY itself: output volume against (1−a)·V(F0) + a·V(F1), 2 × 2 block means at `a = 0` |
| `accum_1h.csv` | hourly accumulations against CIRRUS on the available times, by scale (needs `--pair-stride 1`) |
| `per_time.csv` | scores for each time |
| `qq.json` | quantiles for the QQ plot |
| `grid_check.txt` | alignment of the two grids from the `where` metadata |
| `*.png` | `validation_overview.png`, `qq.png`, `time_shift.png` (which shift minimises the error) |

## Production of 1 km / 5 min frames

```bash
uv run python scripts/opera_ds_cli.py downscale \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --start 2024-07-01 --end 2024-07-02 \
  --bbox 2.5 49.45 6.45 51.55 --buffer-km 200 --workers 8 --out results/ds
```

Output: ODIM HDF5 2.4, DBZH uint16 (gain 0.01, offset −50), gzip. `alpha`,
`interpolated`, `time_shift_min`, `source_t0` and `method` are in
`dataset1/how`. `--time-shift -2.5` gives CIRRUS-convention labels (see
[method.md](method.md), *Output labels*).

## Training windows

```bash
# 1. choose windows on ODYSSEY at 2 km
uv run python scripts/opera_ds_cli.py sample \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --start 2024-07-01 --end 2024-07-06 --workers 10 --out results/windows.csv

# 2. interpolate them into a Zarr store in IRENE format
uv run python scripts/opera_ds_cli.py windows \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --windows-csv results/windows.csv --T 24 --H 256 --W 256 --context-km 150 \
  --workers 8 --out results/windows.zarr
```

- `sample` writes a CSV with `t_start`, `row0`, `col0` (1 km grid), `q`,
  `rain_score`, `nan_frac`, and next to it a JSON with parameters and
  statistics. `--max-nan-frac`, `--q-min`, `--m` and the steps control the
  selection.
- The store has `RR` (n, T, H, W) in mm/h float16, `alpha` and `time` (n, T),
  `row0` and `col0` (n,) on the OPERA 1 km grid; its attributes describe grid,
  Z–R and configuration.

## Options shared by the sub-commands

- `--time-regex` must capture the timestamp in the file name; without it the
  time is read from the ODIM attributes, more slowly.
- `--bbox` and `--buffer-km` crop on read a window aligned to 2 km, identical
  for the two grids. A `--region-mask` on the full grid is cropped the same way.
- `--config configs/config_example.json` changes the parameters of
  `DownscaleConfig` and of LK.
- `--workers` sets the number of processes.

## Running on Leonardo Booster

Leonardo Booster (EuroHPC, CINECA) runs jobs with Slurm. Facts from the
[CINECA documentation](https://docs.hpc.cineca.it/hpc/hpc_data_storage.html)
(checked 3/11/2026):

- **Compute nodes have no internet access.** Every input must be on the
  cluster storage before a job starts: ORD files, the Natural Earth shapes used
  by `make_region_mask.py`, Python packages.
- **Login nodes stop a process after 10 min of CPU time**: enough for
  `uv sync`, `make_region_mask.py` or a `--dry-run`, not for long downloads.
- **Data movers** (`data.leonardo.cineca.it`) have no CPU time limit but no
  interactive shell and no Python: only `scp`, `rsync`, `sftp`, `wget`, `curl`,
  `rclone` and `aws s3`. `$WORK` and the other storage variables are not
  defined there, so paths must be absolute. From a login node they are reached
  without a new certificate, but not from inside a batch job.
- **Storage:** `$WORK` 1 TB per project by default (can be extended), `$FAST`
  1 TB per project, `$SCRATCH` deleted after 40 days without access.

### 1. Environment (login node)

```bash
uv sync
```

In job scripts set `UV_OFFLINE=1` and `UV_FROZEN=1`, so that `uv run` never
tries to reach the network.

### 2. Data (data mover)

The Python download scripts cannot run on the data movers. Two ways:

```bash
# whole files of one year straight from the public bucket (no credentials);
# run from a login node: $WORK is expanded there, before ssh
ssh -xt data.leonardo.cineca.it rclone copy \
  ":s3,provider=Other,endpoint='https://s3.waw3-1.cloudferro.com':openradar-archive/2013/" \
  "$WORK/opera/odyssey/2013" --include "*/*/OPERA/COMP/OPERA@*@0@DBZH_QIND.h5" \
  --transfers 16

# files that already exist on another machine (e.g. the Belgian crops),
# from that machine
rsync -PravzHS data/odyssey_bel/ <username>@data.leonardo.cineca.it:<absolute path>/odyssey_bel/
```

`rclone` keeps the bucket layout (`MM/DD/OPERA/COMP/` under the year), so the
globs become recursive, e.g. `--odyssey-glob "<path>/**/*@DBZH_QIND.h5"`. Make
the region mask on a login node (it downloads Natural Earth once into
`--cache-dir`), or copy it.

### 3. Jobs (compute nodes)

Run the sub-commands of `opera_ds_cli.py` inside Slurm jobs, with `--workers`
equal to the CPUs of the task (`$SLURM_CPUS_PER_TASK`) and every path on the
cluster storage.

## Measured costs (16 cores, local disk)

| step | cost |
|---|---|
| `validate`, Belgium + 200 km, 4 days, 4 methods, 4 shifts | about 21 min with 12 processes |
| `sample`, whole domain | 5 days in 43 s with 10 processes, so about 10 h for 12 years of ODYSSEY |
| windows selected with the IRENE parameters | about 56,000 in 5 days, so about 50 million over 12 years |
| `windows` | about 8 s of CPU and 1.1–1.6 MB per 24 × 256 × 256 window |
| `fetch_cog_crop.py`, Belgium + 350 km | about 3 h for 12 years of ODYSSEY with 32 threads |
| synthetic test (`uv run pytest`) | about 2.5 min locally, 3 min on GitHub Actions |

Each window currently rereads and decompresses its 9–11 whole ODYSSEY files:
see [roadmap.md](roadmap.md) for the planned grouping by time.
