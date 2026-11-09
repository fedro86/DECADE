# EURADCLIM: the European climatological high-resolution gauge-adjusted radar precipitation dataset

- **Authors, year, venue:** A. Overeem, E. van den Besselaar, G. van der
  Schrier, J. F. Meirink, E. van der Plas, H. Leijnse, 2023, *Earth System
  Science Data* 15, 1441–1464
- **Link:** [10.5194/essd-15-1441-2023](https://doi.org/10.5194/essd-15-1441-2023)
- **Access:** open, CC BY 4.0
- **Read:** full text (24 pages)

## What it is

EURADCLIM is a 1 h and 24 h precipitation dataset on the 2 km OPERA grid for
2013–2020. It starts from the ODYSSEY instantaneous surface rain-rate composite
(15 min), removes non-meteorological echoes in three steps, then merges the
hourly radar accumulations with about 7700 ECA&D gauges. Each step is evaluated
over Europe on 8 years against gauges.

## Numbers we use

All three filters run on the 2D composite, not on single-radar data
(section 3).

- **Gabella filter** (section 3.1): wradlib `clutter.gabella` (version 1.9.0),
  after Gabella and Notarpietro (2002), on each 15 min composite. Rain rates are
  turned back into Z with Z = 200 R^1.6, with `undetect` and `nodata` set to
  0 mm/h first.
  - **Gradient part:** in a 5 × 5 window, if fewer than 6 neighbours are less
    than 6 dBZ below the central cell, the cell is clutter.
  - **Shape part:** for contiguous echoes above 0 dBZ, an area-to-perimeter
    ratio below 1.3 means clutter.
  - **Effect:** flagged cells are set to 0 mm/h; `nodata` cells are kept.
  - **Artefacts targeted:** isolated echoes, sea clutter, and thin spokes and
    rings (section 4.1). **Input:** one composite.
- **Satellite cloud-type mask** (sections 2.3, 3.2): CLAAS-2 cloud type
  (SEVIRI, CM SAF, 15 min, about 4 × 7 km at 52° N), resampled by nearest
  neighbour to the OPERA grid.
  - **Rule:** a radar cell is set to 0 mm/h when all cells of the 7 × 7 window
    around it are cloud-free, snow- or ice-covered, or high semi-transparent
    clouds (seven categories). Missing satellite pixels are not used, so they
    never trigger the mask.
  - **Timing:** the satellite slot of 12:00 is paired with the radar composite
    of 12:15, because satellite times mark the start of the scan and radar
    times the end.
  - **Artefacts targeted:** echoes without rain; it also reduces interference,
    for example over eastern Spain (section 4.1). **Input:** the composite plus
    satellite cloud type.
- **Static clutter mask** (section 3.3): wradlib `clutter.histo_cut` on the
  **annual** accumulation.
  - **Rule:** a histogram of 50 classes is built over all cells. Classes whose
    frequency is below 5% of the most frequent class are removed iteratively
    (the default is 1%), until the maximum changes by less than 1 mm. One mask
    is made per year.
  - **Correction:** hourly values inside the mask are replaced by an
    inverse-distance-weighted interpolation (power 2, at most 4 neighbours),
    and only when the interpolated value is lower than the original.
  - **Artefacts targeted:** fixed clutter. It can also catch beam blockage,
    which the paper considers rare because OPERA corrects it.
    **Input:** a long series of composites (one year).
- **Effect** (section 4.1, Table 1): the three filters together lower the
  daily radar sum on gauge-dry days from 0.5 to 0.2 mm. Correlation and CV
  improve most with the Gabella and static filters, while the radar bias
  becomes more negative. The static mask may wrongly remove real rain on the
  rainy Norwegian coast.
- **Impossible values** (section 4.3, Fig. 8): the three filters do not remove
  outliers such as more than 500 mm/h over a French radar on 28/11/2018. The
  authors suggest two remedies:
  - flag whole composites whose radar–gauge ratios are extreme;
  - cap or discard cells above a threshold, a choice they call "a bit
    arbitrary".
- **Accumulation rule** (section 2.1): an hourly sum is made only when all four
  15 min rain rates are valid, with `undetect` = 0. A cell needs at least
  83.3% availability.

## Relevance to DECADE

H2 (#19) names EURADCLIM as the model. Three of its filters apply to our
data, because they work on the composite:
- Gabella, for isolated echoes and thin spokes;
- the satellite mask, for echoes without rain;
- histo_cut on annual sums, for fixed clutter and blockage.

The paper also shows what these filters leave behind, namely extreme outliers,
which is what the "impossible values" class of H2 needs. Our input is the
ODYSSEY `DBZH` maximum-reflectivity composite, not the rain-rate composite
EURADCLIM used, so thresholds in dBZ have to be checked against our product.

## Limits

- **Product:** the paper uses the ODYSSEY rain-rate composite (quality-weighted
  mean), not the maximum-reflectivity composite of DECADE.
- **Period and area:** 2013–2020 over Europe, with no Belgian analysis.
- **Satellite data:** CLAAS-2 is a CM SAF climate record, and access to it is
  not discussed for later years.
- **Static mask:** it is made per year and relies on outliers in the annual
  sum, so it does not see artefacts that come and go within a year.
- **Parameters:** the Gabella parameters are those of wradlib and were not
  tuned to OPERA in the paper.
