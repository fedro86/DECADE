# OPERA production data and software release 2026a

- **Authors, year, venue:** EUMETNET OPERA (prepared by M. Radojevic, V. Meyer, V. Klaus, G. Haase, H. Leijnse, A. von Lerber, K. Stephan, M. Veldhuizen, S. Klink), release notes dated 16/06/2026.
- **Link:** [opera-radar/opera-releases, `release-notes/OPERA_release_notes_20260617.pdf`](https://github.com/opera-radar/opera-releases/tree/main/release-notes)
- **Access:** public GitHub repository of OPERA (downloaded 17/11/2026); no licence stated for the notes.
- **Read:** full text (3 pages).

## What it is

The list of changes of OPERA release 2026a: data exchanged by the members, metadata, and software versions (CIRRUS 1.6.0, NIMBUS with BALTRAD 3.1.0). The notes do not give the day of the switch in production; the file name gives 17/06/2026.

## Numbers we use

- **Software** (page 1): CIRRUS 1.6.0, with the BALTRAD version dated 2025-10-01; NIMBUS with BALTRAD 3.1.0 dated 2026-06-09.
- **CIRRUS 1.6.0** (page 2): metadata corrections only, in the output (`license` attribute, string termination of the `/how` attributes) and in incoming data (node identifiers of a Swedish, a Polish and a Spanish radar; coordinates of a Spanish and an Estonian radar). No change to the quality control or the compositing is listed.
- **Data exchange** (page 2): changes in Estonia, Spain, Poland, France (a replaced radar, LFPW51) and the Netherlands (EHDB: "improved DBZH data quality", ODIM 2.2, higher precision, more variables). **Nothing for Belgium.**
- **NIMBUS** (pages 2–3): wind profiles, bug fixes; the `hac` quality field is missing from the QC volumes given to NWP although `/how/task` lists it (under investigation).

## Relevance to DECADE

#88 and the review of #96: the release comes after the start of the 2026 drop of CIRRUS (1/2026) and changes neither the CIRRUS quality control nor the Belgian data, so it does not explain the drop. The Dutch DBZH change (EHDB) can affect northern Belgium from 6/2026 on; not checked. The notes do not say since when CIRRUS runs the BALTRAD version of 2025-10-01.

## Limits

Release notes only: what changed, not its effect; "improved DBZH data quality" for the Netherlands is not explained.
