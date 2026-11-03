# Working on DECADE

Two kinds of work happen in this repository:

- **exploration** in Jupyter notebooks: looking at data, trying a method,
  making figures;
- **production code** in `opera_ds/` and `scripts/`: what builds the archive and
  the training data on HPC (Leonardo Booster), as batch jobs without notebooks.

Notebooks are where ideas start. Results that go into the archive, the training
data or a paper must come from production code.

## Setup (once)

```bash
git clone https://github.com/fedro86/DECADE.git
cd DECADE
uv sync
uv run pre-commit install
```

`uv sync` creates `.venv/` with all dependencies and installs `opera_ds` in
editable mode: a change to a file in `opera_ds/` is visible in your notebooks
without reinstalling (with `%autoreload`, see below). Run `uv sync` again after
pulling changes to `pyproject.toml`.

## Notebooks

- Start JupyterLab with `uv run jupyter lab`, or in VS Code pick
  `.venv/bin/python` as the kernel.
- Name new notebooks `NN-<initials>-<topic>.ipynb`, e.g.
  `02-ab-quantile-mapping.ipynb`. `NN` is just the next free number.
- Start every notebook with

  ```python
  %load_ext autoreload
  %autoreload 2
  from opera_ds.paths import DATA_DIR, RESULTS_DIR
  ```

  and read and write files only under `DATA_DIR` and `RESULTS_DIR`, never with
  absolute paths of your own machine. If your data are elsewhere, set
  `OPERA_DATA_DIR` before starting Jupyter.
- Use functions from `opera_ds` (see `notebooks/01-quickstart.ipynb`). If you
  write a function longer than a few lines, or copy one from another notebook,
  it probably belongs in `opera_ds/`: ask, or open a pull request.
- **Outputs are removed at commit** by `nbstripout` (installed by
  `pre-commit install`). Figures therefore do not show on GitHub: save the ones
  worth sharing in `results/` and post them in the pull request or the issue.
  CI fails if a notebook with outputs is pushed.
- Never commit data: `data/`, `results/`, `*.h5`, `*.npy`, `*.zarr` are ignored,
  and a hook blocks files over 1 MB.

## From notebook to production code

When a method explored in a notebook should become part of the pipeline:

1. move the functions into a module of `opera_ds/` (one module per topic, with a
   docstring saying what goes in and what comes out, units included);
2. expose it through a script in `scripts/` (or a sub-command of
   `scripts/opera_ds_cli.py`) with explicit arguments for paths, periods, area
   and number of processes, so it can run as a batch job;
3. add a test in `tests/` that runs in a few minutes without real data
   (synthetic fields, as in `tests/test_synthetic.py`);
4. make the notebook call the new function, so that exploration and production
   use the same code.

Production code must not depend on notebooks, on interactive input or on paths
of a specific machine.

## Git workflow

- Do not push to `main`: create a branch (`git switch -c ab/quantile-mapping`),
  commit, push, and open a pull request on GitHub.
- CI runs on every pull request: notebook stripping, large-file check and the
  synthetic test (`uv run pytest`, about 3 min locally).
- Keep pull requests small: one method or one notebook at a time.

## Language and conventions

- README, this guide, notebooks and new docstrings: English. Existing comments,
  `CLAUDE.md` and `docs/handoff.md` are in Italian.
- Reflectivity in dBZ, rain rate in mm/h, conversions with Marshall-Palmer
  (Z = 200 R^1.6) capped at 55 dBZ for metrics (see `CLAUDE.md`).
- Only pan-European data sources in the method (OPERA, ECA&D, EURADCLIM);
  national products only for validation.
