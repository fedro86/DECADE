# Working on DECADE

Two kinds of work happen in this repository:

- **exploration** in Jupyter notebooks: looking at data, trying a method,
  making figures;
- **production code** in `opera_ds/` and `scripts/`: what builds the archive and
  the training data on HPC (Leonardo Booster), as batch jobs without notebooks.

Notebooks are where ideas start. Results that go into the archive, the training
data or a paper must come from production code.

Installation is in the [README](README.md). Run `uv sync` again after pulling
changes to `pyproject.toml`.

## Notebooks

- Start JupyterLab with `uv run jupyter lab`, or in VS Code pick
  `.venv/bin/python` as the kernel.
- Name new notebooks `NN-<initials>-<topic>.ipynb`, e.g.
  `02-ab-quantile-mapping.ipynb`, and add a line to `notebooks/README.md`.
- Start every notebook with

  ```python
  %load_ext autoreload
  %autoreload 2
  from opera_ds.paths import DATA_DIR, RESULTS_DIR
  ```

  `opera_ds` is installed in editable mode, so with `%autoreload` a change to a
  file in `opera_ds/` is visible without restarting. Read and write files only
  under `DATA_DIR` and `RESULTS_DIR`, never with absolute paths of your own
  machine; if your data are elsewhere, set `OPERA_DATA_DIR` (and
  `OPERA_RESULTS_DIR`) before starting Jupyter.
- Use functions from `opera_ds` (see `notebooks/01-quickstart.ipynb`). If you
  write a function longer than a few lines, or copy one from another notebook,
  it probably belongs in `opera_ds/`.
- **Outputs are removed at commit** by `nbstripout` (installed by
  `pre-commit install`), so figures do not show on GitHub: save the ones worth
  sharing in `results/` and attach them to the pull request or issue. CI fails
  if a notebook with outputs is pushed.
- Never commit data: `data/`, `results/`, `*.h5`, `*.npy`, `*.zarr` are ignored,
  and a hook blocks files over 1 MB.

## From notebook to production code

1. Move the functions into a module of `opera_ds/` (one module per topic, with
   docstrings stating inputs and outputs, units included).
2. Expose them through a script in `scripts/` (or a sub-command of
   `scripts/opera_ds_cli.py`) with explicit arguments for paths, period, area
   and number of processes, so that it runs as a batch job.
3. Add a test in `tests/` that runs in a few minutes without real data
   (synthetic fields, as in `tests/test_synthetic.py`).
4. Make the notebook call the new function, so that exploration and production
   use the same code.

Production code must not depend on notebooks, interactive input or paths of a
specific machine.

## Code map

| module | content |
|---|---|
| `opera_ds/odim_io.py` | `read_odim_composite(path, quantity, extent=None)`, crops (`bbox_extent`, `extent_window`, `crop_where`), ODIM writing, `index_files` |
| `opera_ds/ord.py` | public ORD bucket: `ord_key`, `list_keys`, `fetch`, `download(t, product, out_dir)` |
| `opera_ds/paths.py` | `DATA_DIR`, `RESULTS_DIR` |
| `opera_ds/motion.py` | LK on OpenCV (pysteps scheme), high-pass, cache of sparse vectors |
| `opera_ds/interp.py` | `DownscaleConfig`, `PairInterpolator.get(alpha, method)` with methods `nearest`, `linear`, `lk` and suffixes `:Z`, `:dB` |
| `opera_ds/pipeline.py` | `FrameSource`, `output_times`, `run_downscaling`, `run_downscaling_parallel` |
| `opera_ds/validate.py` | validation metrics |
| `opera_ds/sampling.py` | window selection on ODYSSEY: `SamplerConfig`, `sample_block`, `block_times` |
| `opera_ds/windows.py` | ML windows: `Window`, `make_window`, `WindowStore`, `dbz_to_rr` |
| `opera_ds/plots.py` | validation figures |
| `scripts/opera_ds_cli.py` | sub-commands `downscale`, `validate`, `sample`, `windows` |
| `scripts/fetch_ord_archive.py`, `scripts/fetch_cog_crop.py`, `scripts/make_region_mask.py` | download and masks |

Rules the code relies on:

- `reader(path, quantity) -> Frame` can be injected everywhere (validation,
  production, windows). For crops use
  `functools.partial(read_odim_composite, extent=...)`, which can be pickled for
  multiprocessing.
- Crops are in metres from the upper-left corner, aligned to 2000 m.
- `pipeline.output_times(t0, cfg, shift)` is the only rule linking output labels
  and `alpha`.
- The file index is sent to the worker processes once (`_map` with an
  initializer in the CLI).

## Changing the method

- Run `uv run pytest` after every change.
- When a default changes, put in the pull request a before/after table of the
  validation metrics stratified by `alpha`.
- Do not overwrite existing outputs or archives: write to a new folder.
- If real data contradict [docs/data.md](docs/data.md), report it before
  adapting the code, and correct the page.

## Documentation: what goes where

Each topic lives in one file only; elsewhere, link to it. Before adding a
paragraph, check that it is not already written somewhere else.

| if you… | update |
|---|---|
| verify a fact about the data (format, gap, anomaly, new source) | `docs/data.md` |
| change how a method works, or get new evidence for a design choice | `docs/method.md` |
| add or change a script option, an output file, or measure a cost | `docs/usage.md` |
| finish a task, start a new one, take or open a decision | `docs/roadmap.md` |
| change installation or the folder layout | `README.md` |
| change how we work, or add a module | `CONTRIBUTING.md` |
| add a notebook | `notebooks/README.md` |

Status ("done", "to do") is written only in `docs/roadmap.md`.

## Git workflow

- Do not push to `main`: create a branch (`git switch -c ab/quantile-mapping`),
  commit, push, and open a pull request.
- CI runs on every pull request: notebook stripping, large-file check and the
  synthetic test.
- Keep pull requests small: one method or one notebook at a time.

## Language

Everything in the repository is written in English: documentation, notebooks,
docstrings and comments. Some older comments in the code are still in Italian;
translate them when you touch that code.
