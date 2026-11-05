---
name: Problem
about: Something wrong or missing found while working on a ticket (code, data, docs)
title: "Short statement of the problem"
labels: []
assignees: []
---

<!--
Set an area: label, a who: label for whoever should fix it, and the milestone
of the ticket it blocks. Facts only: say what was run and what was seen.
Links to repository files must be absolute
(https://github.com/fedro86/DECADE/blob/main/...).
-->

Found while working on #<n> (<ID>).

## Problem

What is wrong, and where (file, section, function, data product). What was
expected instead and why (the doc or ticket that says so).

## How it was found

The exact command or notebook, the period and data, and what came out:
numbers, file names, error messages.

```bash
uv run python scripts/<script>.py <args>
```

## Proposed fix

- What to change, and what to check before changing it.

## Environment

OS, Python and `uv` version, commit (`git rev-parse --short HEAD`).
