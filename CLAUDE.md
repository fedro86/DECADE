# CLAUDE.md

Instructions for the Claude Code agent only. Project content lives in the files
listed in the README, *Documentation*; do not copy it here.

## Before working

- Read `docs/roadmap.md` (goals, constraints, status, decisions) and the file
  that matches the task (`docs/data.md`, `docs/method.md`, `docs/usage.md`).
- Follow `CONTRIBUTING.md`: notebooks explore, scripts produce; code map;
  portability; rules for changing the method; which file to update.
- When a task is finished, update `docs/roadmap.md` and the file that owns the
  topic, never two copies of the same fact.

## Git and GitHub

- Follow `CONTRIBUTING.md`, *Issues, branches and pull requests*. Use `gh` for
  GitHub operations.
- When work on a ticket starts, create its branch and its draft pull request
  without asking; commit and push to that branch as the work goes.
- Never commit or push to `main`, never merge, never close an issue by hand.
- Before marking a pull request ready and requesting a review, show the user
  the filled description and ask.
- Problems outside the ticket: open an issue with the *Problem* template, with
  labels and milestone, and tell the user.

## Language

- Answer the user in Italian.
- Write everything in the repository in English.

## Environment

- Always `uv run python`, never `python`. Dependencies with `uv sync`; tests
  with `uv run pytest`.
- Local data (not in git) are described in `docs/data.md`, *Derived datasets*.
- IRENE webinar materials (FBK code and notebooks):
  https://github.com/DSIP-FBK/IT4LIA-FBK-Seminar

## Rules

- **Credentials** are in `.env` (`ARCODATAHUB_USERNAME`, `ARCODATAHUB_ACCESS_KEY`,
  `METEOGATE_USERNAME`, `METEOGATE_ACCESS_KEY`). Read them from scripts, never
  print their values: to show the file, print only the variable names.
- **The user's Belgian archive is private**: never ask for it. Validation on it
  is run by the user through the injectable `reader`.
- **Large downloads and long runs**: estimate time and disk space, then ask for
  confirmation.
- **Data contradicting `docs/data.md`**: stop and tell the user before adapting
  the code.
- **Numbers need sources.** Before proposing a threshold, parameter or
  classification rule, search the literature (`CONTRIBUTING.md`, *Literature
  before numbers*): save open-access PDFs in `docs/sources/` as
  `YEAR - AUTHOR - TITLE.pdf` (never committed) and write the summary `.md`
  with the same name, in your own words, saying what was read in full and
  what only in the abstract. Never present a number without its source.
- **Articles you cannot download** (paywall, login, blocked site): ask the user
  to download them into `docs/sources/` under any name. When they have, rename
  each PDF to `YEAR - AUTHOR - TITLE.pdf` and write its summary.
