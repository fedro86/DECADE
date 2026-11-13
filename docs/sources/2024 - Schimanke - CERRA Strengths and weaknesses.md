# CERRA: Strengths and weaknesses

- **Authors, year, venue:** issued by S. Schimanke (SMHI), 16/07/2024, last modified 29/07/2025; C3S report C3S2_D360_Lot1.4.1.1_v2, published as a page of the Copernicus Knowledge Base (ECMWF Confluence).
- **Link:** <https://confluence.ecmwf.int/x/h6QaHQ>
- **Access:** open web page; no licence stated
- **Read:** full text of the web page (no PDF)

## What it is

The C3S assessment of CERRA, CERRA-EDA and CERRA-Land over the original
production (1/9/1984 → 30/6/2021): what each does well, known problems in the
observations used, and homogeneity.

## Numbers we use

- **Rain gauges of the 24 h analysis (RR24) of CERRA-Land:** about twice as
  many as in the earlier MESCAN-SURFEX, mainly thanks to ECA&D, plus national
  data from France, Sweden, Norway, Finland, Iceland and Denmark (section 3.1,
  figure 30).
- **East of 50° E, since 27/11/1999:** almost no gauges enter the analysis,
  because the reports there moved to 03 and 15 UTC and do not fit the
  06–06 UTC day; the analysis there falls back to the CERRA forecast, which is
  wetter, so the mean rises after the change (section 3.1; a short exception in
  2012).
- **Scores of RR24 against gauges, France 1990–2000** (table 3): CERRA-Land
  RMSE 2.91 mm, correlation 0.88; MESCAN-SURFEX 3.32 mm and 0.84; ERA5
  4.32 mm and 0.75.
- **Homogeneity** (section 2.8): CERRA is found homogeneous over the whole
  period, with a test on its own forecasts (6 h against 30 h, 500 hPa
  geopotential), not against observations; this test is about the atmospheric
  reanalysis, not the precipitation analysis.
- **Warning to users:** changes in the distribution of surface stations can
  give misleading trends, especially east of 50° E; where gauges are missing,
  model biases can change the RR24 climatology.

## Relevance to DECADE

H3b (#82): the documented break of the precipitation analysis is east of 50° E,
far from Belgium. The report says plainly that a change in the gauges used can
change the level of CERRA-Land, which is what H3b must check over Belgium; it
does not test the RR24 series for homogeneity.

## Limits

- Covers 1984 → 6/2021 only: nothing on the continuation production.
- No figure for western Europe or Belgium; the observation counts in figure 30
  have no absolute numbers in the text.
