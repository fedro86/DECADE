<!--
Title: "<ID> · One sentence: what the branch delivers".
While the pull request is a draft, "Closes #<n>" is enough. Fill the rest before
`gh pr ready`, then ask for a review (CONTRIBUTING.md, *Issues, branches and
pull requests*). English only. Facts only: a number not known yet stays a
visible <placeholder>, never an estimate. Delete sections that do not apply.
-->

Closes #<n> · `<branch>` → `main` · <WP> · gate <G1–G4>

**Before:** <what could not be done, or went wrong, before this pull request>
**After:** <what can be done now, by whom, and where>

<Why, in two to four sentences, and the spec it implements: issue, roadmap
ticket, method.md or data.md section.>

- <the changes, one per line: modules, scripts, notebooks, docs>

**At a glance**

- Files: <n> · +<insertions> / −<deletions>
- Tests: <new or changed tests>; `uv run pytest` <passed / not affected>
- Docs updated: `docs/roadmap.md` (ticket ticked), <the file that owns the result>
- Outputs not in git: <path under results/ or data/, size>, or none
- Steps someone must do by hand: <downloads, re-crops, Leonardo jobs>, or none

## Commits

<!-- Only if there is more than one meaningful commit. -->

| commit | what changes |
|---|---|
| `<sha8>` | <one or two lines; say "docs only" or "bugfix with a test" where it applies> |

## How it works now

<!-- For method or pipeline changes: the stages, in order. -->

1. **<stage>**: <what happens there>

<!--
Callouts, as needed:
  > [!NOTE]     why this shape, and the alternative turned down
  > [!WARNING]  a consequence for a later ticket, or a decision the reviewer may overturn
  > [!CAUTION]  a defect found (with its test), or an approach tried and dropped
-->

> [!NOTE]
> **<Why this shape.>** <The reason, and the alternative turned down.>

## Figures

<!-- Drag the images here; notebooks are stripped of outputs. -->

<image> — <one sentence: what to look at>

## Measurements

<!-- Validation scores, costs, sizes. If a default changed: before/after
     stratified by `alpha` (CONTRIBUTING.md, *Changing the method*). -->

| <data> | <metric> | before | after |
|---|---|---:|---:|
| <…> | <…> | <…> | <…> |

Machine, versions, period and command: <…>. A check that fails is written as failed.

## How to verify

<!-- From the issue's "How to verify", made concrete: each step with what the
     reviewer sees. -->

1. `<command, or notebook to run>`
   → <expected: exit code, files, numbers>
2. `uv run pytest`
   → passes

## Acceptance criteria

<!-- Copied from the issue, ticked only when true. -->

- [ ] <criterion 1>
- [ ] <criterion 2>

## What remains open

- #<n> <ID or problem>: <what, and who or when>
