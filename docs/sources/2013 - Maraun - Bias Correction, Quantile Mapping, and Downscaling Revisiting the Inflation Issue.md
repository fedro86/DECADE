# Bias Correction, Quantile Mapping, and Downscaling: Revisiting the Inflation Issue

- **Authors, year, venue:** Maraun, D., 2013. Journal of Climate 26, 2137–2143.
- **Link:** [10.1175/JCLI-D-12-00821.1](https://doi.org/10.1175/JCLI-D-12-00821.1)
- **Access:** free PDF on GEOMAR OceanRep, the author's institutional repository (downloaded without login on 12/11/2026); © 2013 American Meteorological Society, no open licence stated.
- **Read:** full text (7 pages): abstract, sections 1–4, appendix.

## What it is

A short note showing, for daily precipitation, what happens when quantile mapping (QM) is used not only to correct a model against data of the same resolution but also to bridge a scale gap: a 25 km regional model grid box (REMO, driven by ERA-40, 1961–2000) mapped onto 20 rain gauges inside that box in the Harz Mountains. The paper calls this "inflation", after the same problem in perfect-prognosis downscaling (von Storch 1999).

## Numbers we use

- **When QM is fine and when it is not:** abstract and section 1. If the reference has a resolution similar to the model, QM is a feasible correction. If the reference is much finer, QM also tries to bridge the scale gap, which "is not feasible".
- **Why:** section 1. QM is deterministic: one simulated value always gives the same corrected value, so it assumes that all local variability is explained by gridbox variability. It adds no small-scale variability; within a grid box the corrected locations are fully dependent on one another.
- **Setup:** section 2. Empirical QM with series of equal length, no separate validation period; drizzle corrected with a wet-day threshold of 1 mm/day for the gauges; separate mappings for winter (DJF) and summer (JJA).
- **Effects found:** section 3, Figs. 3–5.
  - Extremes always cover the whole grid box; the ranking of the gauges never changes for a given quantile.
  - Drizzle is overcorrected: too many days dry across the whole box.
  - Area-mean extremes are overestimated by roughly 30% in both seasons (Fig. 4).
  - Trends are changed: at Thale the negative trend of winter maxima is increased by 0.9 mm per decade (relative trend +85.6%), because the highest values early in the series are amplified by about 80% and later lower values by about 30%; summer totals: absolute trend +3.9 mm per decade more negative. Strong trends tend to be amplified.
- **Averaging neighbouring boxes makes it worse:** section 4. If the target is sub-grid, averaging boxes widens the scale gap.
- **Remedies:** section 4.
  - If day-to-day variability is not needed, correct only the mean, which leaves trends alone.
  - If a total over an area larger than a grid box is needed, correct that total directly rather than downscaling and averaging back.
  - If local day-to-day variability is needed, use stochastic bias correction: a regression with a noise model for the local variability.

## Relevance to DECADE

H3 (#20): the bridges (ERA5-Land at 0.1°, hourly; VMM summed on the same cells) are much coarser than the radar (2 km / 15 min ODYSSEY, 1 km / 5 min CIRRUS).

- **Fit on the bridge grid is the feasible part.** Mapping ODYSSEY and CIRRUS hourly cell sums through the bridge compares like with like (both aggregated to the bridge cells), which is the "similar resolution" case of the paper.
- **The step to pixels is the open part.** Applying the same deterministic mapping to 2 km / 15 min pixel values, as if they were cell-hour sums, is the scale-bridging use that the paper shows is not feasible: it would change the spatial and temporal structure, overstate area extremes and change trends between ODYSSEY and CIRRUS years.
- **What the paper allows instead:** correct only the level (the mean, or a factor per cell and hour from the bridge-grid mapping) and keep the radar's own small-scale variability, or use a stochastic step. Which one DECADE uses is a method choice for G1; the paper tests none of them on radar data.

## Limits

- One grid box, 20 gauges, daily data; a model against gauges, not two radar products against a reanalysis.
- The direction of the scale gap differs: here a coarse simulation is mapped to points; in H3 fine radar data are compared through a coarse bridge.
- The paper shows the problem and names remedies; it does not test the remedies.
