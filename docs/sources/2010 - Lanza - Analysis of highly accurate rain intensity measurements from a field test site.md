# Analysis of highly accurate rain intensity measurements from a field test site

- **Authors, year, venue:** L. G. Lanza, E. Vuerich, I. Gnecco, 2010; Advances in Geosciences 25, 37–44.
- **Link:** <https://doi.org/10.5194/adgeo-25-37-2010>
- **Access:** open, CC BY 3.0
- **Read:** full text (8 pages); the values of Fig. 4 and Table 2 were not read as numbers.

## What it is

The analysis of the one-minute data of the WMO Field Intercomparison of
Rainfall Intensity Gauges (Vigna di Valle, Italy, 10/2007–4/2009): 26 gauges of
several kinds (tipping-bucket, weighing, level, disdrometers, a radar gauge)
against a reference of four gauges in a pit, 79 events, 1,325 mm.

## Numbers we use

- **Tolerance:** the WMO required uncertainty of rain intensity is 5 %
  (section 3, citing the WMO guide of 2008); the reference itself has an
  expanded uncertainty of 4.3 mm h⁻¹ at one minute, below 5 % only above
  90 mm h⁻¹.
- **Tipping-bucket gauges:** without correction they fall outside the
  tolerance (section 3.1, Fig. 4a); with a software or extra-pulse
  correction they are within it over the whole range of intensities of the
  campaign. The loss of the uncorrected gauge comes from the water that
  falls while the bucket tips, so it grows with intensity (section 1 and
  conclusions, qualitatively).
- **Weighing gauges** are linear over a wider range than tipping buckets
  (conclusions).

## Relevance to DECADE

H3 (#20), the check of ERA5-Land against the RMI automatic stations
(comment of 16/11/2026 on #96): it is the reference for the
intensity-dependent loss of tipping-bucket gauges, one of the two cautions on
gauges. A loss that grows with intensity can move the ratio of a bridge to
the gauges in years with more heavy rain, which is why the drift test is
repeated without each station's wettest days.

## Limits

- One site in Italy, 18 months, mostly convective events; the size of the
  loss of an uncorrected gauge at a given intensity is in Fig. 4, not in the
  text.
- Nothing on wind-induced undercatch, which this campaign did not address
  (gauges compared at the same site, against gauges in a pit).
- The paper does not say which gauges the RMI automatic stations use.
