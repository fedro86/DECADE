---
name: Ticket
about: A unit of work in the DECADE plan (docs/roadmap.md)
title: "<ID> · Imperative one-liner: what this ticket delivers"
labels: []
assignees: []
---

<!--
Set labels (area, type, who, review, condition), milestone (gate) and assignee.
Status comes from GitHub: open = to do, linked pull request = in review,
closed = done. Delete the paths in "How to verify" that do not apply.
Links to repository files must be absolute
(https://github.com/fedro86/DECADE/blob/main/...): relative links do not work in issues.
-->

| | |
|---|---|
| Owner | Federico / Marìca / Federico and Marìca / Marìca explores, Federico codes |
| Spec | [roadmap.md](https://github.com/fedro86/DECADE/blob/main/docs/roadmap.md) <WP, ID> · <method.md or data.md section, if any> |
| Planned | dd/mm/yyyy → dd/mm/yyyy |
| Depends on | #<n> <ID>, … (or —) |
| Condition | only if the call is won / lost / the budget allows (or delete the row) |
| Review | Vito (or delete the row) |

## Goal

One to three sentences on **why**: the question this ticket answers or the
capability it adds, and what it unblocks.

## In scope

- What this ticket does, as concrete steps.

## Out of scope

- What a reader might assume is included but is not, and which ticket has it.

## Data and compute

- Input: <products, period, domain>, <size on disk>
- Where it runs: laptop / workstation / Leonardo (<node-hours>)
- Expected time: <hours>; output: <size>, written to <relative path>

## How to verify

Concrete enough to run blind.

### Notebook path

1. Open `notebooks/NN-<initials>-<topic>.ipynb`, run all from a clean kernel.
2. Expect: <figure, table or number>.

### CLI path

```bash
uv run python scripts/<script>.py <args>
```

Expected:

- Exit code `0`; `<output>` contains `<files>`; `<file>` shows `<value or range>`.

### Leonardo path

1. Submit `<job script>` (a chain of jobs if longer than 24 h).
2. Expect: <output on the cluster storage>; a stopped job resumes.

### Review path

1. <Who> reads <what> and checks <what>.

## Acceptance criteria

- [ ] Yes/no statement about the result.
- [ ] `uv run pytest` passes (CI on Linux and Windows), if code changed.
- [ ] If a default changed: before/after metrics stratified by `alpha` in the pull request.
- [ ] Result recorded in the doc that owns it (see below).

## Affected files and docs

- `opera_ds/<module>.py`: what changes
- `notebooks/NN-<initials>-<topic>.ipynb`: what it shows
- `docs/<file>.md`, *<section>*: what is written there

## Notes

- Open questions, related tickets and decisions.
