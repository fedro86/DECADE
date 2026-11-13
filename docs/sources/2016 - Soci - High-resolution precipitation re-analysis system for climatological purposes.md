# High-resolution precipitation re-analysis system for climatological purposes

- **Authors, year, venue:** C. Soci, E. Bazile, F. Besson, T. Landelius, 2016; Tellus A: Dynamic Meteorology and Oceanography 68, 29879.
- **Link:** <https://doi.org/10.3402/tellusa.v68.29879>
- **Access:** open, CC BY 4.0
- **Read:** full text (sections 1–2, method and validation)

## What it is

The paper of MESCAN, the daily precipitation analysis later used in
CERRA-Land: a two-dimensional optimal interpolation of 24 h gauge totals
(06 UTC to 06 UTC) with a model forecast as first guess, at 5.5 km over
Europe (EURO4M, 2007–2010), validated over France against SAFRAN and
independent gauges.

## Numbers we use

- **Gauges used per grid point:** the 16 nearest observations within 200 km
  (section 2.1).
- **Error settings of this first version** (section 2.2): observation error
  standard deviation 5 mm, background error 13 mm, horizontal correlation
  length 35 km. The ratio of the two error variances sets how closely the
  analysis follows the gauges.
- **Inputs:** 24 h totals from SYNOP and climate stations of European
  databases such as ECA&D and ECMWF; radar is not used, as it is neither long
  nor Europe-wide (section 1).
- **Quality control:** reports with a large height difference from the model
  orography, duplicated reports and large departures from the first guess are
  rejected (section 2.1).

## Relevance to DECADE

H3b (#82): it explains why the number of gauges matters for the level of
CERRA-Land. Each correction reaches only a few tens of kilometres from a gauge
(correlation length 35 km here); away from gauges the analysis is the model
forecast. So a change in the Belgian gauges that enter the analysis, or in
those just across the border, changes how much of the Belgian field is gauge
and how much is model, and with it the level whenever the model is biased.

## Limits

- Error settings of the EURO4M version; CERRA-Land uses an observation error
  that grows with the amount (Le Moigne et al., 2021) and its background
  error and length scale are not given in the sources read.
- Validation over France only.
