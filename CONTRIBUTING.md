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

- Start JupyterLab with `uv run jupyter lab`, or in VS Code pick the `.venv`
  kernel (see the README).
- Name new notebooks `NN-<initials>-<topic>.ipynb`, e.g.
  `02-mr-quantile-mapping.ipynb`, and add a line to `notebooks/README.md`.
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
- A figure that a document cites goes in `docs/figures/<topic>/`, one subfolder
  per topic (e.g. `cirrus-qc/`), not per ticket, so that it stays findable
  after the ticket is closed. Keep it under 1 MB and link it from the section
  that cites it.
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

Production code must not depend on notebooks or interactive input.

## Portability

Production runs on Linux HPC (Leonardo Booster); colleagues work on Linux,
macOS and Windows. CI runs the tests on Linux and Windows.

- Nowhere in the repository (code, notebooks, documentation) write a path of a
  specific machine: use paths relative to the repository, `DATA_DIR` and
  `RESULTS_DIR`, or a URL.
- No shell commands, aliases or OS-specific tools in code or notebooks: use
  Python (`pathlib`, `shutil`, `glob`).
- Open text files with `encoding="utf-8"`.
- Processing code must not access the network: HPC compute nodes have no
  internet ([docs/usage.md](docs/usage.md), *Running on Leonardo Booster*).
  Downloads are separate steps (`scripts/fetch_*.py`).
- Code that runs several processes must work with the `spawn` start method
  (Windows, macOS): workers and `reader`s are module-level functions or
  `functools.partial` of them, never lambdas or functions defined in a notebook.
  Scripts keep their `if __name__ == "__main__":` guard.

## Code map

| module | content |
|---|---|
| `opera_ds/odim_io.py` | `read_odim_composite(path, quantity, extent=None)`, crops (`bbox_extent`, `extent_window`, `crop_where`), ODIM writing, `index_files` |
| `opera_ds/ord.py` | public ORD bucket: `ord_key`, `list_keys`, `fetch`, `download(t, product, out_dir)` |
| `opera_ds/paths.py` | `DATA_DIR`, `RESULTS_DIR` |
| `opera_ds/motion.py` | LK on OpenCV (pysteps scheme), high-pass, cache of sparse vectors |
| `opera_ds/interp.py` | `DownscaleConfig`, `PairInterpolator.get(alpha, method)` with methods `nearest`, `linear`, `lk` and suffixes `:Z`, `:dB` |
| `opera_ds/pipeline.py` | `FrameSource`, `output_times`, `run_downscaling`, `run_downscaling_parallel` |
| `opera_ds/validate.py` | validation metrics; `degrade_frame`, `read_degraded` (CIRRUS degraded to the ODYSSEY grid) |
| `opera_ds/classify.py` | convective / stratiform pixels after Steiner et al. (1995): `steiner_convective`, `steiner_centres` (centres by intensity and by peakedness), `obs_classes`; ECCO convectivity after Dixon and Romatschke (2022): `ecco_convectivity`; `steiner_ecco_fields`, `intensity_centres_vs_ecco` |
| `opera_ds/sampling.py` | window selection on ODYSSEY: `SamplerConfig`, `sample_block`, `block_times` |
| `opera_ds/windows.py` | ML windows: `Window`, `make_window`, `WindowStore`, `dbz_to_rr` |
| `opera_ds/plots.py` | validation figures |
| `opera_ds/clean.py` | first-version cleaning (H2): `clean_composite` (> 70 dBZ, Gabella as a switch, static mask), `StaticCounts` (per-pixel counts on past composites and the mask rule), `StaticMask` (fill tables, radar of each masked pixel, switched with `how/nodes`), `static_fill` (EURADCLIM fill), `odyssey_period` |
| `opera_ds/bridge.py` | bridge data (S7, S9): `era5land_to_zarr` and `era5land_amounts` (ERA5-Land files to one store of hourly amounts), `era5land_sum`, `cerraland_sum` (totals over a window), `cell_index` and `cell_mean` (OPERA pixels on the bridge cells), `pixel_lonlat`, `monthly_files` |
| `scripts/opera_ds_cli.py` | sub-commands `downscale`, `validate`, `sample`, `windows` |
| `site/index.html`, `site/fetch_data.sh` | project plan page; ticket status, owners, dates and dependencies are read from the issues by `fetch_data.sh` when `.github/workflows/pages.yml` publishes it, so only the plan text lives in the page |
| `scripts/fetch_ord_archive.py`, `scripts/fetch_cog_crop.py`, `scripts/make_region_mask.py`, `scripts/fetch_pvol_positions.py`, `scripts/fetch_cds.py`, `scripts/bridge_to_zarr.py` | download and masks; single-radar files for the radar positions of a day; ERA5-Land and CERRA-Land from the Copernicus Climate Data Store, ERA5-Land as one Zarr store |
| `scripts/irene_t0.py` | IRENE test training on fake windows (T0) and its training cost for other losses, members, batches and gradient accumulation (T9); runs with the IRENE environment, not DECADE's |
| `scripts/irene_inference_cost.py` | GPU memory and time of one IRENE forecast of the whole domain against the ensemble size (T8); input with DECADE's environment, measurement with IRENE's |

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

## Literature before numbers

Every method choice that rests on a number (a threshold, a parameter, a
classification rule) starts with a literature search: where the number comes
from, who uses it on similar data (Belgium, Benelux, OPERA), and its known
limits. Each source gets a summary in `docs/sources/`, named
`YEAR - AUTHOR - TITLE.md`; the PDF goes next to it with the same name and is
never committed (git ignores everything in that folder except `.md`). The
rules and a template are in [docs/sources/README.md](docs/sources/README.md).
`docs/method.md` then cites the summaries next to the number.

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
| read an article or report used for a choice | `docs/sources/<YEAR - AUTHOR - TITLE>.md` |
| add a figure that a document cites | `docs/figures/<topic>/`, linked from the citing section |

Status ("done", "to do") is written only in `docs/roadmap.md`.

## Issues, branches and pull requests

Every ticket of `docs/roadmap.md` is a GitHub issue written with the *Ticket*
template (`.github/ISSUE_TEMPLATE/ticket.md`). Work on it goes through one
branch and one pull request:

1. **Start.** From an up-to-date `main`, create a branch named
   `<initials>/<id>-<topic>` (e.g. `mr/s0-reproduce`), push it and open a
   **draft** pull request at once, titled like the issue and linked to it:

   ```bash
   git switch main && git pull
   git switch -c mr/s0-reproduce
   git push -u origin mr/s0-reproduce
   gh pr create --draft --title "S0 · Reproduce the existing pipeline" --body "Closes #9"
   ```

   The draft shows what is in progress; discussion about the work goes there.
2. **Work.** Commit and push to the branch often. Attach figures that are not in
   git to the pull request. If `main` moves on, merge it into the branch.
3. **Problems found on the way** that are not part of the ticket become new
   issues with the *Problem* template (`.github/ISSUE_TEMPLATE/problem.md`),
   with `area:` and `who:` labels and the milestone of the ticket they block;
   mention them in the pull request.
4. **Ready for review.** When the acceptance criteria of the issue are met:
   tick the ticket in `docs/roadmap.md` and update the file that owns the result,
   in the same pull request; fill the description from
   `.github/pull_request_template.md`; then mark the pull request ready and ask
   Federico for a review, which notifies him:

   ```bash
   gh pr ready
   gh pr edit --add-reviewer fedro86
   ```

   Tickets labelled `review:vito` are also sent to Vito.
5. **Review and merge.** Requested changes are new commits on the same branch;
   ask for a review again when they are done. Federico merges when CI is green
   and the review is approved; the merge closes the issue and deletes the branch.

A ticket whose result is not a file (an email, a decision) still gets a short
pull request: it records the result in the file that owns it and ticks the
ticket in the roadmap.

Further rules:

- Never push to `main`. On GitHub `main` is protected: changes arrive only
  through a pull request with the notebook and large-file check green and one
  approving review. Federico's own pull requests have no other reviewer, so he
  merges them as administrator (`gh pr merge --admin`).
- CI checks every pull request for notebook outputs and large files. The
  synthetic test runs only when code, configuration or the environment change
  (paths in `.github/workflows/tests.yml`), not for documentation or notebooks.
- Keep pull requests small: one ticket, one method or one notebook at a time.

## Language

Everything in the repository is written in English: documentation, notebooks,
docstrings and comments. Some older comments in the code are still in Italian;
translate them when you touch that code.
