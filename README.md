# DECADE – a harmonised decade of OPERA radar data

**DE**ep-learning now**C**asting from **A** harmonised **DE**cade of radar data.

![status: in progress](https://img.shields.io/badge/status-in%20progress-orange)

**The project is in progress.** The code below already reads, interpolates and
validates OPERA data, but the harmonised archive and the IRENE experiments are
still being built. The plan, what is done and the decisions are in
[docs/roadmap.md](docs/roadmap.md); the work is tracked as
[issues](https://github.com/fedro86/DECADE/issues) grouped by gate:

| gate | progress |
|---|---|
| [G1 · method frozen](https://github.com/fedro86/DECADE/milestone/1) | [![G1 · method frozen](https://img.shields.io/github/milestones/progress-percent/fedro86/DECADE/1?label=issues%20closed)](https://github.com/fedro86/DECADE/milestone/1) |
| [G2 · archive v1 and stores](https://github.com/fedro86/DECADE/milestone/2) | [![G2 · archive v1 and stores](https://img.shields.io/github/milestones/progress-percent/fedro86/DECADE/2?label=issues%20closed)](https://github.com/fedro86/DECADE/milestone/2) |
| [G3 · archive tested with IRENE](https://github.com/fedro86/DECADE/milestone/3) | [![G3 · archive tested with IRENE](https://img.shields.io/github/milestones/progress-percent/fedro86/DECADE/3?label=issues%20closed)](https://github.com/fedro86/DECADE/milestone/3) |
| [G4 · final archive and results](https://github.com/fedro86/DECADE/milestone/4) | [![G4 · final archive and results](https://img.shields.io/github/milestones/progress-percent/fedro86/DECADE/4?label=issues%20closed)](https://github.com/fedro86/DECADE/milestone/4) |

Deep-learning nowcasting models such as IRENE are trained on multi-year radar
archives at 1 km / 5 min. In Europe, the EUMETNET OPERA composites reach that
resolution only since July 2024; the 2012–2024 legacy archive covers a decade
at 2 km / 15 min. DECADE harmonises that decade to 1 km / 5 min and measures,
over a Belgian pilot domain, whether pre-training IRENE on it improves
nowcasts.

This repository holds the data side: reading OPERA composites, optical-flow
interpolation of the legacy archive, validation, and training windows in IRENE
format.

## Getting started

You need [`uv`](https://docs.astral.sh/uv/). It installs the right Python (3.12)
and every dependency, including JupyterLab.

```bash
git clone https://github.com/fedro86/DECADE.git
cd DECADE
uv sync                      # creates .venv with opera_ds installed in editable mode
uv run pre-commit install    # strips notebook outputs at every commit
uv run jupyter lab           # then open notebooks/01-quickstart.ipynb
```

In VS Code, select the interpreter in `.venv` as the notebook kernel
(`.venv/bin/python` on Linux and macOS, `.venv\Scripts\python.exe` on Windows). Run Python
through `uv run` (for example `uv run python scripts/...`), so that it uses the
project environment.

The quickstart notebook downloads about 10 MB from the public OPERA archive and
runs in under a minute: it reads the legacy and current products over Belgium,
interpolates one 15 min pair to 5 min and compares the result with the real
5 min product.

## Repository layout

```
opera_ds/        the library: everything that must run in production
scripts/         command-line entry points, used for batch jobs on HPC
notebooks/       exploration and figures, built on opera_ds
tests/           synthetic end-to-end test, run by CI
configs/         parameter files for the scripts
docs/            project documentation (below)
data/, results/  downloaded data and outputs, never in git
```

## Documentation

Each topic lives in exactly one file; the others link to it.

| file | answers |
|---|---|
| [README.md](README.md) | what the project is, how to install it, where things are |
| [CONTRIBUTING.md](CONTRIBUTING.md) | how we work: notebooks and production code, git, code map, which file to update |
| [docs/roadmap.md](docs/roadmap.md) | the specification: goals, plan, what is done and what is left, decisions |
| [docs/data.md](docs/data.md) | facts about the input data: sources, formats, time windows, gaps, known problems |
| [docs/method.md](docs/method.md) | how the processing works and why, with the evidence and the validation results |
| [docs/usage.md](docs/usage.md) | how to run the scripts, locally and on Leonardo Booster; what they write; measured costs |
| [notebooks/README.md](notebooks/README.md) | list of notebooks |
| [CLAUDE.md](CLAUDE.md) | instructions for the Claude Code agent only |

## License

Code: [MIT](LICENSE). OPERA data from the ORD archive are licensed CC BY 4.0
by EUMETNET; cite the source when you publish results or derived data.
