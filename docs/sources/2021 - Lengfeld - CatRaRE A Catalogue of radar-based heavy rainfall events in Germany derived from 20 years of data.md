# CatRaRE: A Catalogue of radar-based heavy rainfall events in Germany derived from 20 years of data

- **Authors, year, venue:** K. Lengfeld, E. Walawender, T. Winterrath,
  A. Becker (DWD), 2021, *Meteorologische Zeitschrift* 30(6), 469–487
- **Link:** https://doi.org/10.1127/metz/2021/1088 · catalogue and method
  note: https://opendata.dwd.de/climate_environment/CDC/help/landing_pages/doi_landingpage_CatRaRE_W3_Eta_v2022.01-en.html
- **Access:** open access (free download from the publisher); "© 2021 The
  authors"; the licence is not stated in the PDF. Also read: the DWD 3-page
  note "Event selection in CatRaRE" (CatRaRE v2022.01, DWD open data).
- **Read:** full text of sections 1, 2 (method), 3 (results, opening and 3.1),
  4 and 5; case studies 3.3 skimmed.

## What it is

The DWD objective catalogue of heavy-rain events in Germany, 2001–2020, from
the gauge-adjusted radar climatology RADKLIM-RW (1 km, hourly). Events of 11
durations from 1 to 72 h, each with time, area, mean and maximum rain, return
period and severity indices. Updated every year.

## Numbers we use

- **Durations:** 1, 2, 3, 4, 6, 9, 12, 18, 24, 48, 72 h, accumulated every hour
  (section 2.1, p. 471).
- **Threshold W3** (DWD warning level 3, severe weather; Table 1, p. 472):
  25, 27, 29, 31, 35, 37.5, 40, 45, 50, 60, 90 mm for those durations. Official
  values: 25 mm in 1 h, 35 mm in 6 h, 40 mm in 12 h, 50 mm in 24 h, 60 mm in
  48 h, 90 mm in 72 h; the others are linear interpolations (section 2.2).
- **Alternative threshold T5:** local 5-year return level per grid cell and
  duration (section 2.2, p. 472).
- **Minimum object size** (section 2.3, p. 473): contiguous cells (sides or
  corners) above threshold, at least 9 km² for durations up to 3 h, otherwise
  3 × D km².
- **Independence** (section 2.3, Fig. 3): two events at the same place need a
  gap of the shorter of their durations, at least 4 h; overlapping dependent
  objects are one event.
- **Which object represents an event:** the one with the largest return period
  T_max, or the largest extremity E_T,A, which combines log return period and
  affected area (Müller and Kaspar 2014; eq. 2.2).
- **Counts** (section 3, p. 476): W3_ET,A has 23,020 events in 20 years; more
  than 90% last 9 h or less. Most events May–August (section 3.1).
- **Impact caveat** (section 4, p. 483; also section 3.3): the Münster flood of 28/7/2014 is not
  in the top 100 by extremity despite severe damage; impact needs geographical
  and demographic data too.

## Relevance to DECADE (D3)

The most complete objective definition of a heavy-rain event found: an
accumulation threshold per duration, a minimum area, an independence rule and
a ranking. It can be applied to CIRRUS or RADCLIM accumulations over Belgium
almost unchanged. Belgian thresholds would replace W3 (see the RMI warning
criteria, which are close: 20–30 mm/h yellow, above 30 mm/h orange).

## Limits

German thresholds and hourly gauge-adjusted data; DECADE has 5 min reflectivity
composites, so accumulations must first be built. Not specific to convection:
long-duration events are mostly stratiform.
