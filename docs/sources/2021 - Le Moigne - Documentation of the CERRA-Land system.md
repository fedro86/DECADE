# Documentation of the CERRA-Land system

- **Authors, year, venue:** P. Le Moigne, E. Bazile, M. Glinton, A. Verrelle (Météo-France), 15/10/2021; Copernicus Climate Change Service note C3S_D322_Lot1.1.1.12_202110_documentation_CERRA-Land.
- **Link:** <https://dast.copernicus-climate.eu/documents/reanalysis-cerra/D322_Lot1.1.1.12_Documentation_CERRA-Land.pdf>
- **Access:** open (Copernicus document; no licence stated in the note)
- **Read:** full text (16 pages)

## What it is

The system note of CERRA-Land, the 5.5 km land-surface reanalysis of the
original C3S production (9/1984 → 6/2021): SURFEX driven by the CERRA
atmospheric reanalysis, on the same grid as CERRA. Its daily precipitation is a
MESCAN analysis: optimal interpolation between the CERRA forecast precipitation
(first guess) and daily rain-gauge totals (Soci et al., 2016).

## Numbers we use

- **Rain-gauge sources** (section 1.2.2): synoptic gauges of the national
  services of France, Sweden, Norway, Finland, Iceland and part of Denmark;
  synoptic reports from the GTS stored in ECMWF's MARS archive; and ECA&D.
- **Observation error** used in the analysis (section 1.2.2): 0.001 mm for a
  dry gauge; 0.7 + 0.1 · RR mm below 50 mm; 5.7 mm from 50 mm.
- **Gauges per day over time** (figure 1.2.2.2, read off the graph, monthly
  means of the input before quality control, 1984 → about 2019): about 8,000
  to 8,700 a day until the early 2000s; then a fall in steps, mostly in the
  ECA&D series (about 5,000 → 2,600), to about 6,600 by about 2008; about
  6,500–6,800 from 2008 to the end of the graph, with a small step up around
  2016 (MARS series, about 1,200 → 1,550).
- **Map** of the same figure (1/9/2016): Germany is covered by MARS (synoptic)
  reports, France by the national network; Belgium is not readable at the
  scale of the map.

## Relevance to DECADE

H3b (#82): the input network of CERRA-Land is stable in total over 2012–2019,
the part of the record before the continuation production. The steps of the
early 2000s are outside our period. Whether the Belgian gauges change inside
2012–2025, and whether the continuation after 6/2021 receives the same gauges,
is not in this note.

## Limits

- Written at the end of the original production: nothing on the continuation
  after 6/2021 (new contract), nor on the 12-bit packing of 5/2021–7/2025.
- The counts are for the whole domain and read off a graph; no counts by
  country.
