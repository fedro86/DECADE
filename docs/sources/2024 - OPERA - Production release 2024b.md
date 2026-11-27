# OPERA production release 2024b

- **Authors, year, venue:** EUMETNET OPERA, release notes, target date
  07/11/2024
- **Link:** [opera-radar/opera-releases, `release-notes/OPERA_Production_release_notes_2024b.pdf` and `OPERA_Release_2024b.md`](https://github.com/opera-radar/opera-releases/tree/main/release-notes)
- **Access:** public GitHub repository of OPERA (downloaded 17/11/2026); no
  licence stated for the notes
- **Read:** full text (1 page)

## What it is

The list of changes of OPERA release 2024b: radars added or removed, filter
changes and metadata of CIRRUS v1.3.5.

## Numbers we use

- **Belgium** (CIRRUS v1.3.5): Wideumont (PAGW) switched to its "best" volume
  data in CIRRUS, completed on 18/12/2024.
- **Satellite filter** (CIRRUS v1.3.5): satellite filtering reintroduced for all
  11 Finnish radars, which shows that the filter is switched per radar in
  CIRRUS and had been off for Finland.
- **Bugfix**: stronger control of the BALTRAD pre-processing so that corrupted
  incoming files do not stop production.
- New radars in Norway, Ireland, Romania, Poland and Croatia; Gdańsk removed.

## Relevance to DECADE

PR #96 and #88: a dated change of the Belgian input to CIRRUS (Wideumont,
18/12/2024), and evidence that the CIRRUS satellite filter is applied radar by
radar.

## Limits

Release notes only: no description of what the "best" Wideumont volume
contains, and no list of the filters applied to each Belgian radar.
