# Comparison of high-resolution climate reanalysis datasets for hydro-climatic impact studies

- **Authors, year, venue:** Wood, R. R., Janzing, J., van Hamel, A., Götte, J., Schumacher, D. L., Brunner, M. I., 2025. Hydrology and Earth System Sciences 29, 4153–4178.
- **Link:** [10.5194/hess-29-4153-2025](https://doi.org/10.5194/hess-29-4153-2025)
- **Access:** open access, CC BY 4.0.
- **Read:** full text; sections 2.1–2.2 (datasets, including how ERA5-Land and CERRA-Land precipitation are made), 3.1–3.2 (metrics, variability, trends), 4.1–4.2 (mean and extreme climatology), 5.1–5.2 (variability, trends), 6.2 (heavy-precipitation events), 7.1–7.4 (discussion, limitations), 8 (recommendations). Values marked "about" were read off the box plots of Figs. 2, 3 and 5 in the PDF; the text gives no numbers for them. The supplement (Figs. S1–S18) was not read.

## What it is

An evaluation of four reanalyses (ERA5, ERA5-Land, CERRA with CERRA-Land precipitation, CHELSA v2.1) against the MeteoSwiss gridded daily observations over Switzerland, 1986–2020. All comparisons are daily, as catchment averages over 97 headwater catchments of CAMELS-CH, split into three elevation bins: ≤ 1000 m (n = 32), 1000–2000 m (n = 36) and > 2000 m (n = 29). The paper covers mean and extreme precipitation and temperature, solid precipitation, variability from daily to inter-annual, trend consistency, two droughts (2003, 2018) and three flood-producing rain events (May 1999, August 2005). CERRA is closest to the observations for almost every precipitation metric. ERA5 and ERA5-Land have too many wet days and too weak extremes.

## Numbers we use

- **Benchmark:** section 2.1. RhiresD, a daily precipitation total starting at 06:00 UTC, interpolated from 650 stations onto a 75 arcsec (about 2 km) grid. Section 7.1 (p. 4170) gives its effective resolution as 15–20 km, coarser for intense convective rain. Section 7.4 (p. 4173) says it overestimates light precipitation and underestimates strong precipitation, so the reanalysis underestimation of extremes is "likely even larger than shown".
- **ERA5-Land precipitation = ERA5, interpolated:** section 2.2.1 (p. 4156). ERA5-Land precipitation is the ERA5 field linearly interpolated to the 9 km grid "without any adjustments" and accumulated to 24 h. Only temperature gets a lapse-rate correction. Section 7.1 (p. 4170) finds the precipitation differences between ERA5 and ERA5-Land "marginal". Section 7.2 (p. 4171) concludes that pure interpolation does not improve any precipitation metric.
- **CERRA-Land precipitation:** section 2.2.2 (p. 4156) and Table 1. CERRA is a regional reanalysis (HARMONIE-ALADIN, 5.5 km) with ERA5 lateral boundaries. CERRA-Land is an offline SURFEX v8.1 run whose precipitation comes from MESCAN. MESCAN takes the CERRA precipitation as first guess and adds rain-gauge observations by optimal interpolation. The product is a daily accumulation at 5.5 km, used here for mid-1984 to mid-2021.
- **ERA5 assimilates precipitation only over the USA:** section 7.1 (p. 4169). Apart from CERRA-Land, none of the datasets assimilates precipitation observations. The only exception is ERA5, which uses a radar–gauge product over the contiguous USA since 2010.
- **Wet day = ≥ 1 mm/day:** Table 2 (p. 4160). The number of wet days per calendar year is counted with this threshold.
- **Wet-day excess, ERA5 and ERA5-Land:** Fig. 3d (p. 4162) and section 4.2 (pp. 4160–4161). The median catchment bias is about +45 wet days per year for both ERA5 and ERA5-Land (boxes about +40 to +55). It is about +8 for CERRA and about +52 for CHELSA. The median of the low-elevation bin is about +40 for ERA5 and ERA5-Land and close to 0 for CERRA. The paper's cause: precipitation is "distributed across too many days with moderate precipitation intensity". In CERRA the wet-day excess is concentrated in high catchments. The abstract and section 8 list the wet days of ERA5 and ERA5-Land as one of their two clear failures, the other being snowfall.
- **Extremes too weak, ERA5 and ERA5-Land:** Fig. 3a–c (p. 4162) and section 4.2. Rx1d has a median bias of about −22 % in ERA5 and ERA5-Land and about −3 % in CERRA. Rx5d is about −13 % in ERA5 and ERA5-Land and about −4 % in CERRA. R99pTot is about −3 percentage points in ERA5 and ERA5-Land and about −1 in CERRA. The underestimation holds in all elevation bins.
- **Mean precipitation too high, especially in summer:** Fig. 2a (p. 4161) and section 4.1. Annually, the median bias is about +10 % for ERA5 and ERA5-Land and close to 0 for CERRA. In summer (JJA) all reanalyses overestimate: about +12 % for ERA5 and ERA5-Land, about +5 % for CERRA and about +20 % for CHELSA. The overestimation is larger in low (≤ 1000 m) and high (> 2000 m) catchments than in mid-elevation ones.
- **Variability too low, ERA5 and ERA5-Land:** Fig. 5 (p. 4164) and section 5.1. Daily precipitation variability has a median bias of about −20 % in ERA5 and ERA5-Land and about −5 % in CERRA. Inter-annual summer variability is about −15 % in ERA5 and ERA5-Land and close to 0 in CERRA. CERRA overestimates inter-annual variability in many catchments.
- **Trend consistency:** section 5.2 and Fig. 7e–h (pp. 4164–4167), Mann–Kendall test at 0.05 (0.05–0.1 counted as weakly significant), Theil–Sen slopes. In the observations about 20 % of catchments have a significant decrease in mean precipitation over 1986–2020. ERA5, ERA5-Land and CHELSA show no significant trend anywhere, so they miss all of these. CERRA detects about half of them but adds many trends absent from the observations. Agreement on sign and significance (numbers printed above the bars in Fig. 7) is:
  - mean precipitation: ERA5 77 %, ERA5-Land 77 %, CERRA 55 %, CHELSA 77 %;
  - Rx1d: 80 %, 79 %, 72 %, 85 %;
  - wet days: 65 %, 66 %, 55 %, 62 %.
  The observations and CERRA show fewer wet days over time, while ERA5 and ERA5-Land show no clear trend (p. 4165).
- **CERRA homogeneity:** section 7.4 (p. 4173). The number and quality of stations changes over time, and this may create "spurious or artificial trends". The authors give it as a possible reason for the many significant or opposite trends in CERRA (Fig. S18). The good recent performance is credited to the dense station input to MESCAN; it has to be re-checked for the planned back-extension to 1961, when there will be fewer stations. A forward extension to the present is also planned.
- **CERRA artefacts:** section 7.1 (p. 4169). Spurious local precipitation events appear over complex terrain and offset droughts (2003, 2018). There are "bubble" artefacts in Switzerland and the Apennines (Fig. S12). The authors attribute them to too few assimilated data, which leaves more weight on the model, and cite similar problems in station-poor northern and eastern Europe (Le Moigne et al., 2021).
- **Spatial extent of heavy rain:** sections 6.2 and 7.1 (pp. 4167–4170). ERA5, ERA5-Land and CHELSA spread the 1999 and 2005 events over too large an area. They overestimate catchments with low to moderate rain and slightly underestimate the most severe ones. CERRA matches the centre and intensity best. The authors note that the actual spatial scale of the interpolated and downscaled datasets is coarser than their grid spacing.

## Relevance to DECADE

H3 (#20), choice of the bridge between ODYSSEY and CIRRUS.

- **ERA5-Land as bridge:** its precipitation is the interpolated ERA5 field, with about +45 wet days per year at ≥ 1 mm/day, a peak day about 22 % too low, daily variability about 20 % too low, and too much rain in summer. This is the drizzle-and-flattening pattern listed among the bridge criteria, now with numbers. With the wet-pixel frequency matched first (as planned in H3), the low end of the ERA5-Land distribution has to be treated as dry rather than copied onto the radar; otherwise the radar inherits the excess of wet hours. The upper quantiles of the bridge are too low and too smooth, so the radar must not be scaled to them. A bias of the bridge cancels only if it is the same before and after July 2024 and the comparison is matched by season.
- **CERRA-Land as bridge:** it has the most realistic wet-day frequency, extremes and variability at the daily scale, because MESCAN adds gauges. It is the better candidate for the level and the shape of the daily distribution. Against it:
  - it is daily only, so it cannot calibrate or check sub-daily or diurnal behaviour;
  - its quality depends on the gauge network at each time, so a change in the gauges received around 2024 would show up as a step in the bridge;
  - the paper links CERRA-Land to spurious trends and to artefacts where gauges are sparse.
  The paper ends in mid-2021, so the 2021–2025 part used for CIRRUS is not evaluated here. Whether it is produced with the same system and gauge input must be checked in the CERRA-Land documentation.
- **Trend consistency as a homogeneity test:** ERA5 and ERA5-Land damp trends (they miss every observed significant decrease), and CERRA creates extra ones. Neither result shows a step in 2024, but for CERRA-Land the paper names time-varying station input as a mechanism that could create one.
- **Day windows:** the benchmark is 06–06 UTC, and ERA5-Land is accumulated over 24 h. The paper does not say how the windows were aligned. In H3 the radar must be accumulated over the bridge's own day: 06–06 UTC for CERRA-Land, 00–24 UTC for ERA5-Land.

## Limits

- The region is Switzerland, mostly complex terrain; Belgium (below about 700 m) falls entirely in the lowest bin (≤ 1000 m, 32 catchments). Several ERA5 and CERRA problems are tied to orography (spatial extent of heavy rain, CERRA "bubbles", elevation-dependent biases) and may be weaker over flat land. The low-bin values above are the closest analogue, but they still come from Swiss catchments close to the mountains.
- The comparison is daily and averaged over catchments (median area not given in the text). Nothing is said about hourly precipitation, the diurnal cycle or the 0.1° pixel scale at which H3 compares the radar.
- The reference is a gridded gauge product with an effective resolution of 15–20 km, which itself smooths extremes and has too much light rain. It is not radar, and it is not point data.
- The period is 1986–2020, so the July 2024 change from ODYSSEY to CIRRUS and the CERRA-Land years after mid-2021 are outside the study.
- Summer convective extremes in flat terrain, the case most relevant to the radar, are not evaluated separately; the three heavy-rain events are large-scale and orographic.
- Minor inconsistencies in the paper:
  - the text cites Fig. 3b for R99pTot and Fig. 3c for wet days, while the caption assigns them to Fig. 3c and 3d (the values above follow the caption);
  - the caption of Fig. 9 says "2008 drought" for 2018;
  - section 7.4 cites Fig. 7c for extreme-precipitation trends, which are in Fig. 7b.
