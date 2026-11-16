# A combined statistical bias correction and stochastic downscaling method for precipitation

- **Authors, year, venue:** Volosciuk, C., Maraun, D., Vrac, M., Widmann, M., 2017. Hydrology and Earth System Sciences 21, 1693–1719.
- **Link:** [10.5194/hess-21-1693-2017](https://doi.org/10.5194/hess-21-1693-2017)
- **Access:** open (CC BY 3.0); PDF downloaded from the journal on 12/11/2026.
- **Read:** abstract, section 1 (introduction, first part), section 6 (conclusions, first two pages). Sections 2–5 (data, method details, results per region) were not read.

## What it is

A two-step method for daily precipitation from a regional model (KNMI-RACMO2, EURO-CORDEX, driven by ERA-Interim) at 86 European rain gauges, 1979–2008, with 5-fold cross-validation in the VALUE framework. Step 1 corrects the model against gridded observations (E-OBS) at the same scale. Step 2 bridges the gap from grid box to station with a stochastic regression calibrated between gridded and station observations.

## Numbers we use

- **Why two steps:** section 1. Quantile mapping is reasonable for biases at the same spatial scale, but local variability (location, size and intensity of a storm) is not set by the grid box; a deterministic mapping inflates the variance, overestimates spatial extremes and keeps the smoother temporal structure of the grid box (citing Maraun 2013).
- **Step 1, bias correction at the same scale:** abstract and section 6. Parametric quantile mapping, a gamma distribution for the bulk and a generalized Pareto distribution for the tail; the drizzle effect corrected by raising the model wet-day threshold until its number of wet days matches the gridded observations with 0.1 mm/day.
- **Step 2, scale gap:** abstract and section 6. A logistic regression for wet-day probability and a vector generalized linear gamma model for intensities, with the coarse (corrected) precipitation as predictor, calibrated between gridded and station data (a perfect-prognosis step), then applied to the corrected model.
- **Results:** abstract and section 6. Precipitation is improved in most cases; better in summer than in winter, worst for continental winter. Classical QM straight from model to station performs similarly for bias and heavy precipitation but does not reproduce the spatial dependence between stations in summer.
- **Modularity:** abstract. The best method can be chosen for each step separately.

## Relevance to DECADE

H3 (#20). It is the published form of "correct on the coarse grid, then handle the fine scale separately":

- the first step matches the H3 fit on the bridge grid (radar hourly cell sums against the bridge at the same scale);
- the second step shows that going to finer scales needs its own model of the small-scale variability, not the same deterministic mapping. In DECADE the small-scale structure is already in the radar data, so a level correction that keeps it would need no stochastic step; whether that is enough is a G1 choice.

## Limits

- Daily data, a regional model against gauges, not radar products; the downscaling step targets stations, not a fine grid.
- Only the abstract, the start of the introduction and part of the conclusions were read; the method sections are summarised here from those parts only.
