# Evaluating long-term trends in annual precipitation: A temporal consistency analysis of ERA5 data in the Alps and Italy

- **Authors, year, venue:** Lussana, C., Cavalleri, F., Brunetti, M., Manara, V., Maugeri, M., 2024. Atmospheric Science Letters 25, e1239.
- **Link:** [10.1002/asl.1239](https://doi.org/10.1002/asl.1239)
- **Access:** open access, CC BY (Creative Commons Attribution). The Wiley site blocks automatic download; the published version was taken from the [University of Milan repository (AIR)](https://hdl.handle.net/2434/1048648).
- **Read:** full text (12 pages): sections 1–5, Tables 1–2, figure captions. Figures could not be rendered here: their content is known only from the captions and the text.

## What it is

A test of whether long-term changes in ERA5 annual precipitation over the Greater Alpine Region (GAR) and Italy reflect climate or changes in the assimilated observations. Annual totals from ERA5 (hourly, 0.25°, 1940–2020), the ERA5 ensemble (ERA5-EDA) and three century reanalyses (CERA-20C, ERA-20C and the model-only ERA-20CM) are compared with two gridded datasets built from homogenised stations: LAPrec1901 (Alps, monthly) and UniMi/ISAC-CNR (Italy, monthly, 1921–2020). The deviations (reanalysis minus observations, averaged over each domain) are examined as 3-year running means, with Theil–Sen trends and Mann–Kendall tests over the common period 1940–2010.

## Numbers we use

- **Reference datasets agree well with each other:** section 4 and Fig. 2 (p. 5). LAPrec1901 minus UniMi/ISAC-CNR in northern Italy: mean deviation 4 mm, trend +4 mm per 10 years, about 4 % of the 1,072 mm mean annual total over a century. This sets the noise floor of the test.
- **ERA5 deviation trends, Italy:** Table 1 (p. 7), 1940–2010. ERA5 mean bias +50 mm, trend +12 mm per 10 years (+1.4 % per 10 years, p < 0.01). CERA-20C: trend 0 mm per 10 years (ensemble range −1 to 2), not significant.
- **ERA5 deviation trends, Alps:** Table 2 (p. 8), 1940–2010. ERA5 mean bias +99 mm, trend +17 mm per 10 years (+1.6 % per 10 years, p < 0.01). ERA5-EDA behaves the same (+18 mm per 10 years). CERA-20C: −3 mm per 10 years, not significant.
- **Size of the drift:** section 4 (p. 7). Over 1940–2010 the ERA5 deviation grows by about +10 % (Italy) and +11 % (Alps) of the annual total, against −1 to +1 % and −3 to 0 % for CERA-20C.
- **Shape of the drift:** section 4 (p. 7). The ERA5 deviation rises from 1940 to 1970, decreases from 1970 to 1995, then increases again from 1995 to 2020, more strongly over the Alps (Fig. 5). The paper gives no trend number for 1995–2020 alone and does not identify a single break year.
- **Suggested cause:** section 4 (pp. 7–8) and section 5 (p. 9). The authors relate slope changes to the periods in which the ERA5 background-error covariance matrix B is redefined (1950–1973, 1974–1979, 1979–2006 and after 2006, quoted from an EGU 2020 abstract by Hersbach and co-authors). They state that this link "lacks direct evidence" and would need reruns of ERA5 to test. Changes in the observing network, time-varying representativeness bias and their effect on the model are the other influences named (section 5).
- **ERA5 is wetter than the references:** section 4 (p. 6). ERA5 and ERA5-EDA are "consistently wetter", which the authors attribute to their higher effective resolution; ERA-20C and ERA-20CM are drier.
- **Wider validity:** section 5 (p. 9). A preliminary analysis over Fennoscandia, not shown, suggests similar patterns elsewhere. The authors recommend comparing ERA5 with regional homogenised gridded datasets before reading trends from it.

## Relevance to DECADE

H3 (#20), homogeneity of the ERA5-Land bridge over 2012–2026 and across July 2024. ERA5-Land precipitation is the ERA5 field interpolated to 0.1° (Muñoz-Sabater et al., 2021), so the result applies to it.

- **ERA5 precipitation is not homogeneous in the long run.** This is the main peer-reviewed evidence that ERA5 annual precipitation drifts with respect to homogenised observations, by about 1.4–1.6 % per 10 years over 1940–2010 in the Alps and Italy, with a renewed increase from 1995 to 2020. Over our 14-year window (2012–2026), a drift of that size would amount to about 2–2.2 % (1.4–1.6 % × 1.4 decades, computed here), if it continued at the 1940–2010 rate.
- **It is a slow drift, not a step.** The paper describes changes in slope, not abrupt breaks, and does not look at single years or months. A slow drift affects the bridge only through the difference between the calibration periods on each side of July 2024; comparing short windows close to the switch (for example 12 months before and after) limits it.
- **Nothing on 2021–2026.** The data end in 2020. The paper neither shows nor excludes a change in 2024.
- **How to check our bridge.** Its approach (time series of reanalysis minus homogenised gridded observations, with a model-only reference when available) is the template for a homogeneity check of ERA5-Land over Belgium, for example against a gauge-based gridded product over 2012–2026.

## Limits

- **Region:** Alps and Italy, with strong orography; Belgium is mostly flat, so the size of the drift may differ. The Fennoscandia result is only mentioned, not shown.
- **Annual totals only:** no seasonal, daily or hourly analysis, no wet-day frequency; our bridge works with seasonal levels and hourly data.
- **Period 1940–2020:** trends are computed over 1940–2010; the post-1995 increase is only described qualitatively. July 2024 is outside the study.
- **Cause not established:** the link with the B-matrix updates is a hypothesis; no change in the observing system is identified by date for the recent decades.
- **References are themselves gridded data** with residual inhomogeneity (LAPrec's error decreases by about 0.7 % per 10 years, section 3.1, p. 4) and fewer stations in 2020 (about 500–1,000 for UniMi/ISAC-CNR, section 3.2, p. 5).
