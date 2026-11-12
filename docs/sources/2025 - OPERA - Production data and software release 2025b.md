# OPERA production data and software release 2025b

- **Authors, year, venue:** EUMETNET OPERA (prepared by M. Radojevic, V. Meyer, V. Klaus, G. Haase, K. Stephan, M. Veldhuizen and others; first draft by A. von Lerber), release notes dated 18/11/2025.
- **Link:** [opera-radar/opera-releases, `release-notes/OPERA_release_notes_20251118.pdf`](https://github.com/opera-radar/opera-releases/tree/main/release-notes)
- **Access:** public GitHub repository of OPERA (downloaded 12/11/2026); no licence stated for the notes.
- **Read:** full text (3 pages).

## What it is

The list of changes that OPERA put into production with release 2025b: new radars in the data exchange, metadata updates, and the software versions of the production lines (CIRRUS 1.5.0, NIMBUS).

## Numbers we use

- **Date:** 18/11/2025 (page 1).
- **CIRRUS 1.5.0** (page 2–3):
  - "Improvement of compositing method: search distance for contributing radar pixels now varies with distance from radar";
  - "Update of satellite filter", with a third option, MTG 10-min, for the transition from MSG to MTG;
  - bugfix: when the satellite products are missing, incoming reflectivity files prone to the satellite filter are not passed to the compositing;
  - update of the advection task; reflectivity data from EVRR40 (Latvia) and EIDB40 (Ireland).
- **Data exchange** (page 2): new radars in Lithuania, Spain, Finland, Denmark and Portugal; Israel cut. No Belgian, Dutch, French or German radar near Belgium is mentioned.

## Relevance to DECADE

#88 and H3 (#20): the CIRRUS crops change their `how/comment` between 18/11/2025 09:15 and 09:25 UTC, the day of this release, and the CIRRUS rain index over Belgium falls against ERA5-Land from late 2025. The compositing change acts on how far from each radar its pixels contribute, which could change the maximum reflectivity near the radars; this is a candidate cause of the local drop near Helchteren and Wideumont, not a proven one.

## Limits

- Release notes, not a technical description: how the search distance varies with distance, and which radars are "prone to the satellite filter", are not given.
- Whether the archive before 18/11/2025 was produced with the earlier version is not stated.
