# Spatial and temporal evaluation of radar rainfall nowcasting techniques on 1,533 events

- **Authors, year, venue:** R. O. Imhoff, C. C. Brauer, A. Overeem,
  A. H. Weerts, R. Uijlenhoet, 2020, *Water Resources Research* 56,
  e2019WR026723
- **Link:** https://doi.org/10.1029/2019WR026723 · KNMI record:
  https://www.knmi.nl/research/publications/spatial-and-temporal-evaluation-of-radar-rainfall-nowcasting-techniques-on-1-533-events
- **Access:** open access, Creative Commons Attribution licence (p. 1)
- **Read:** full text of sections 1, 2.2 (data and event selection) and 3.2
  (seasonal dependency), abstract and conclusions; the algorithm and metric
  sections skimmed.

## What it is

Verification of four nowcasting algorithms (two from Rainymotion, deterministic
and probabilistic pysteps) against Eulerian persistence, over 12 Dutch
catchments and polders (6.5–957 km²), on the KNMI 1 km / 5 min radar composite
for 2008–2018.

## Numbers we use

- **Event selection** (section 2.2.2, p. 4): per catchment, season and duration
  (1, 3, 6, 24 h), the 4 highest catchment-mean rainfall sums plus the 4 highest
  single-cell sums, without overlap, from the gauge-adjusted composite:
  4 × 4 × 12 × 8 = 1,536 events selected (the title says 1,533; the reason for
  the difference was not found in the parts read).
- **Seasons** are the meteorological ones, DJF, MAM, JJA, SON (Table 1). An
  "event" is a fixed-duration window, not the start and end of rain.
- **Reflectivity limits:** below 7 dBZ ignored (about 0.1 mm/h), above 55 dBZ
  capped (about 100 mm/h) (section 2.2.1, p. 3).
- **Seasonal contrast** (section 3.2, p. 13): event- and catchment-averaged MAE
  and CRPS 0.2–0.5 mm/h in winter against 0.8–1.7 mm/h in summer, a factor of
  about 3; spring only 22% lower than summer; autumn in between (26% lower
  than spring, conclusions). Errors grow by about 45% from the first hour to
  35–60 min lead time in every season.
- Decorrelation times of deterministic pysteps: 25, 40, 56 and 116 min for 1, 3,
  6 and 24 h events; skilful lead times about twice as long downwind as upwind
  (abstract).

## Relevance to DECADE

Supports season (summer against winter) as a coarse split in H1 and WP4: the
convective/stratiform contrast shows up there as a factor of about 3 in error,
without a per-event label. The fixed-duration, catchment-based event selection
is a model for V5. The 7 dBZ / 55 dBZ limits match the cap used in DECADE's
rain-rate scores (55 dBZ).

## Limits

Dutch composite and lowland catchments; errors in rain rate (mm/h) on
catchment means, not in dBZ on pixels, so the factor of 3 does not transfer as
a number to H1. Events are chosen by rain amount, not by precipitation type.
