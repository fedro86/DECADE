# The ERA5 global reanalysis from 1940 to 2022

- **Authors, year, venue:** Soci, C., Hersbach, H., Simmons, A., Poli, P., Bell, B., Berrisford, P., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Radu, R., Schepers, D., Villaume, S., Haimberger, L., Woollen, J., Buontempo, C., Thépaut, J.-N., 2024. Quarterly Journal of the Royal Meteorological Society 150, 4014–4048.
- **Link:** [10.1002/qj.4803](https://doi.org/10.1002/qj.4803)
- **Access:** open access, CC BY (Creative Commons Attribution). The Wiley site blocks automatic download; the published version was taken from the [NOAA Institutional Repository](https://repository.library.noaa.gov/view/noaa/68132).
- **Read:** full text of the parts on the observing system and on precipitation: abstract and section 1 (pp. 4014–4017), section 2.1 and Table 1 (production streams, pp. 4018–4019), section 4.1–4.2 with Figs 11–16 and Table 2 (soil moisture, precipitation, hydrological balance and spin-up, pp. 4027–4033), section 6 (conclusions, pp. 4045–4046). Sections 3 and 5 (synoptic quality, temperature) were skimmed. Figures could not be rendered here: their content is known only from the captions and the text.

## What it is

The ECMWF description of the final ERA5 back extension to 1940, released in March 2023, with an evaluation of the whole record 1940–2022. It complements Hersbach et al. (2020), which documents the ERA5 system and the observations from 1979; the post-1979 observing system is not described again here. Precipitation is evaluated as 12-month running means and 36-month running correlations against GPCC (monthly gauge analysis) over six continental boxes, plus global water balance and the sensitivity of precipitation to the forecast range from which it is accumulated.

## Numbers we use

- **Observation volume grows with time:** abstract (p. 4014). ERA5 assimilates about 17,000 observations per day in 1940 and 25 million per day by 2022; the paper says the quality of the reanalysis improves accordingly. No yearly count for 2012–2022 is given in the text.
- **No attempt to freeze the observing system:** section 1 (p. 4015). ERA5 deliberately uses all available observations, weighted by quality, rather than a homogeneous subset. The authors state that varying amounts of observations "modulate the biases" of the reanalysis. In-situ reports contribute only temperature, humidity, pressure, wind and snow depth (no rain gauges).
- **Radar rain rates only over the United States:** section 1 and Fig. 2 (p. 4015). The map of remotely sensed observations includes radar rain rates over the United States; all other entries are satellite data. No European radar or gauge precipitation input is mentioned.
- **Production streams and seams:** section 2.1 and Table 1 (pp. 4018–4019) for 1940–1978; section 4.1 (p. 4028). ERA5 is produced in parallel streams spliced together. Sharp changes in soil moisture occurred where one stream ended and another began, and the paper notes that this "also happened" in the post-1978 production at the beginning of 2015. The effect on precipitation at that seam is not shown.
- **ERA5 vs GPCC precipitation over time:** section 4.1, Figs 13–14 (pp. 4029–4031). ERA5 and GPCC correlations of monthly precipitation (36-month windows, 1° grid) change little after about 1970 but "tend to decline in recent years by amounts that vary regionally"; the authors do not attribute this to ERA5, because GPCC uses fewer stations in recent years. For 1950–1969, Europe has the highest correlation, 84 % (p. 4031). No break near 2022 or earlier in Europe is reported in the text.
- **Global water balance not stable:** section 4.2, Fig. 15 (p. 4031). Precipitation and evaporation are in good global balance for about 20 years from the mid-1990s; the imbalance worsens from 2015 (evaporation declines, precipitation does not), then reverses over the last 3 years (2020–2022). Over sea, precipitation rises from the early 1990s to around 2010, mainly in the tropics, "of questionable realism".
- **Precipitation depends on the forecast range:** section 4.2, Table 2 (p. 4032). Standard ERA5 precipitation (the CDS field) is accumulated over the first 12 h of the 06 and 18 UTC forecasts. Averaged over oceans for 2003–2022, it gives 2.30 mm day⁻¹, against 2.16 for the 4D-Var final trajectory and 2.25 for the 24–36 h forecasts. The spin-up is read by the authors as a conflict between the observations of the data-rich recent years and the model's preferred state (p. 4032).
- **Europe and the final trajectory:** section 4.2 (p. 4032), citing Lavers et al. (2023). Final-trajectory precipitation has smaller random errors against stations for 2001–2020, but larger biases in some regions, including Europe, from too much precipitation when little or none was observed. Fig. 16b,d shows decreasing precipitation over much of Europe for longer spin-up (text, p. 4032).
- **Next reanalysis:** section 6 (p. 4046). ERA6 was due to start production in 2024; ERA5 continues in near real time with the same system.

## Relevance to DECADE

H3 (#20), homogeneity of the ERA5-Land bridge over 2012–2026 and across July 2024.

- **The system is fixed, the inputs are not.** The paper confirms that ERA5 keeps one model and assimilation system but ingests a changing observation set (section 1). Any step in ERA5-Land precipitation would therefore come from the observations or from a production seam, not from a model upgrade.
- **Known seam in 2015, none reported for 2024.** The only post-1978 stream change named is at the start of 2015, for soil moisture (p. 4028). The study ends in December 2022 and says nothing about 2023–2026, so it cannot confirm or exclude a change near July 2024. The ECMWF documentation (summarised in `2026 - ECMWF - ERA5 data documentation and known issues.md`) lists the stream dates after 2022.
- **Changes after 2015 are visible in global means.** The 2015–2022 change in global precipitation–evaporation balance (Fig. 15) shows that ERA5 hydrology is not perfectly stationary in our period. The paper does not say whether this reaches western Europe; a regional check of the bridge against gauges before and after July 2024 remains necessary.
- **Use the standard field consistently.** Precipitation amounts depend on the forecast range (Table 2). ERA5-Land is built from the standard 06/18 UTC field, which has been the same since 1940; the bridge should not mix in other ERA5 precipitation estimates.

## Limits

- **Ends in 2022:** the evaluation covers 1940–2022, so July 2024 is outside it. No ERA5T or near-real-time aspect is discussed.
- **Global and continental scale:** precipitation is assessed as means over large boxes (Europe is 25° W–40° E, 34–72° N, Fig. 11 caption) and as global balances; no Belgian or Benelux value is given.
- **No list of satellite instruments by date** for the post-1979 period; the paper refers to Hersbach et al. (2020) for that. Which instruments started or stopped between 2012 and 2022 cannot be read from this paper.
- **Focus on 1940–1978:** most of the methodological changes (pressure bias correction, IBTrACS, spin-up of streams) concern the back extension, not our period.
- **Figures not inspected:** values that appear only in the figures (for example the 2012–2022 part of the European curves in Figs 13–14) were not read.
