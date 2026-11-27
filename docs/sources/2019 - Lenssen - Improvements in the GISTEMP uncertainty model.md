# Improvements in the GISTEMP uncertainty model

- **Authors, year, venue:** N. J. L. Lenssen, G. A. Schmidt, J. E. Hansen, M. J. Menne, A. Persin, R. Ruedy, D. Zyss, 2019; Journal of Geophysical Research: Atmospheres 124, 6307–6326.
- **Link:** <https://doi.org/10.1029/2018JD029522>
- **Access:** publisher's PDF posted by the authors' institute (Columbia University); the licence of the article is not stated on that copy
- **Read:** abstract, sections 1, 4 (sources of uncertainty, how they are combined) and 5.1.4 (homogenisation uncertainty); the rest skimmed.

## What it is

The uncertainty budget of the GISTEMP v4 global temperature record: station
measurement, coverage, homogenisation, ocean processing and other structural
biases, combined into a 95% uncertainty of the global annual mean.

## Numbers we use

- **Combination** (section 4, eqs 4–5): the total error is split into a land
  and an ocean part. If they are independent, the variance of the total is
  the sum of their variances. The authors take them as independent, and
  warn that positive correlations left out, between components or in time,
  make the uncertainty too small. They use annual means to reduce the
  correlation in time.
- **Homogenisation as a term** (section 5.1.4): the homogenisation
  uncertainty of the land stations is split into two independent parts:
  - a parametric part, from an ensemble of 100 runs of the homogenisation
    algorithm with different settings;
  - the shifts left undetected.
- **Result:** about 0.05 °C (95%) for the global annual mean over the last
  50 years.

## Relevance to DECADE

H3 (#20), the uncertainty budget of the level correction (comment of
16/11/2026 on #96). It is a published uncertainty budget of a homogenised
climate record that does what we do:
- it treats method choices as terms;
- it adds independent terms as variances;
- it names the risk of doing so when some terms are correlated.

That risk is why our budget also gives the linear sum, and treats the bridge
term as fully correlated across pixels and periods (JCGM 100:2008).

## Limits

- Temperature, global means; nothing on precipitation or on radar.
- Their structural terms come from ensembles of a homogenisation algorithm;
  ours come from pairs of alternatives (two bridges, one offset or several),
  turned into terms with the rectangular rule of the GUM.
