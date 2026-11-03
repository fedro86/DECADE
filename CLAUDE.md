# CLAUDE.md

Instructions for the Claude Code agent only. Project content lives in the files
listed in the README, *Documentation*; do not copy it here.

## Before working

- Read `docs/roadmap.md` (goals, constraints, status, decisions) and the file
  that matches the task (`docs/data.md`, `docs/method.md`, `docs/usage.md`).
- Follow `CONTRIBUTING.md`: notebooks explore, scripts produce; code map;
  rules for changing the method; which file to update.
- When a task is finished, update `docs/roadmap.md` and the file that owns the
  topic, never two copies of the same fact.

## Language

- Answer the user in Italian.
- Write everything in the repository in English.

## Environment

- Always `uv run python`, never `python`. Dependencies with `uv sync`; tests
  with `uv run pytest`.
- `ls` is an alias of `eza` and changes its output: in scripts use `find`.
- The sandbox's `XDG_CONFIG_HOME` is not the user's: for `gh` use
  `GH_CONFIG_DIR=/home/fedro/.config/gh`, and push with
  `git -c credential.helper= -c "credential.https://github.com.helper=!gh auth git-credential" push`.
- Local data (not in git) are described in `docs/data.md`, *Derived datasets*.
- IRENE webinar materials (FBK code and notebooks):
  `/home/fedro/Code/personal/webinar-forecast-ai`.

## Rules

- **Credentials** are in `.env` (`ARCODATAHUB_USERNAME`, `ARCODATAHUB_ACCESS_KEY`,
  `METEOGATE_USERNAME`, `METEOGATE_ACCESS_KEY`). Read them from scripts, never
  print them: to show the file use `sed -E 's/=.*/=<…>/' .env`.
- **The user's Belgian archive is private**: never ask for it. Validation on it
  is run by the user through the injectable `reader`.
- **Large downloads and long runs**: estimate time and disk space, then ask for
  confirmation.
- **Data contradicting `docs/data.md`**: stop and tell the user before adapting
  the code.
