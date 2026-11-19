# Enhancing the usability of weather radar data for the statistical analysis of extreme precipitation events

- **Authors, year, venue:** Hänsler, A., Weiler, M., 2022. Hydrology and Earth System Sciences 26, 5069–5084.
- **Link:** [10.5194/hess-26-5069-2022](https://doi.org/10.5194/hess-26-5069-2022)
- **Access:** open access, CC BY 4.0.
- **Read:** full text; sections 2.1–2.2 (data), 2.3.1–2.3.5 (event selection, regional subsampling, extreme value analysis, bias correction, uncertainty), 3.1 (bias correction), 3.2–3.3 (design storms, uncertainty), 4 (discussion), Table 1. The Supplement (Figs. S1–S3) was not read.

## What it is

The authors turn 19 years (2001–2019) of RADKLIM, the DWD reprocessed radar climatology (5 min, 1 km, adjusted to gauges at hourly scale), into design storms with return periods up to 100 years for Baden-Württemberg, Germany. Each cell's record is extended to 95 "artificial years" by pooling events from 4 nearby cells at similar altitude. A generalized Pareto distribution is then fitted. Its location parameter is bias-corrected by quantile mapping against a station-based design-storm product (BW-Stat). The result is compared with BW-Stat and with the national KOSTRA-DWD-2010R.

## Numbers we use

- **Data and season:** section 2.1. RADKLIM_YW_V2017.002, 1 km × 1 km, 5 min, 2001–2019, April–October only (to match BW-Stat and to avoid solid precipitation).
- **Durations:** section 2.3. 15, 60, 360 and 1440 min, from running sums of the 5 min data (Eq. 1), each processed separately, with no interpolation between durations.
- **Events:** section 2.3.1, Eq. (2). The 350 largest independent events per cell and duration, with independence defined as at least 48 h between events for every duration.
- **Regional pooling:** section 2.3.2, Table 1. Four extra cells per cell of interest give 5 × 19 = 95 years. The sampling probability combines distance (normal, mean 9 km, standard deviation 6 km, maximum 25 km) and altitude difference (mean = altitude of the cell, standard deviation 50 m). Only cells with probability above 0.8 can be drawn, and after each draw the cells within 4 km are excluded. Above 1150 m (about 70 cells) the altitude mean is fixed at 1150 m. The draw is repeated 10 times and the 5 draws with the fewest duplicate cells are kept (Eq. 5).
- **Extreme value fit:** section 2.3.3, Eq. (6). Peaks over a threshold, set per cell at the 1-year return level with plotting positions. L = e × 95 ≈ 258 events are kept. A three-parameter generalized Pareto distribution is fitted with L-moments per cell, duration and ensemble member. There is no wet-day or wet-pixel threshold in the method: the sample is the largest events only.
- **Quantile-mapping set-up:** section 2.3.4, Eq. (7). This is an empirical QM, x̂ = F_stat⁻¹(F_rad(x)), but it is applied to the *spatial* distribution of the fitted location parameter (a proxy for the 1-year design storm), not to rain rates. For each BW-Stat station the location parameter of the 4 nearest radar cells is taken. The station and radar distributions are built over all stations. The transfer function uses 100 discrete bins and is then applied to every radar cell, separately for each duration and ensemble member.
- **What is not corrected:** section 2.3.5. Scale and shape are left as fitted on the radar data, "to keep the consistency within the data". The reason given for correcting only the location parameter is that the station records are short (BW-Stat: 4–55 years, 90 % of stations with 18 years or fewer; section 2.2.2), so only the location parameter is robust in both datasets (section 2.3.4).
- **Reference caveat:** section 2.2.2. BW-Stat is itself an interpolated product whose values below the 5th and above the 95th spatial percentile were set to those percentiles. KOSTRA is a two-parameter GEV on 1951–2010 at about 8.2 km, with only 56 stations covering the whole period (section 2.2.1).
- **Result of the correction:** section 3.1, Fig. 3. Before correction, the radar clearly underestimates the 1-year design storm. After QM it matches the station data almost exactly at station cells (by construction). Because the location parameter shifts all events by the same amount, the relative effect shrinks for longer return periods (Fig. 5, RAD against RAD-BC).
- **Remaining bias:** section 3.2, Fig. 5. Except at the very high and low percentiles, the ensemble-mean 20- and 100-year design storms are about 5–15 mm lower than BW-Stat.
- **Uncertainty:** section 3.3. The confidence band of the spatial distribution is about 5 mm for 20-year storms and about 10 mm for 100-year storms. The local range is 15–20 % for 60 min and 10–15 % for 1440 min. Most of it comes from the choice of pooled cells, not from the parameter fit.
- **Spatial pattern:** section 3.2. The correlation of the 100-year storms with the April–October mean rainfall (REGNIE) rises from r = 0.25 at 15 min to r = 0.75 at 1440 min. In BW-Stat it stays below 0.6.
- **Warning on multiplicative corrections:** section 4 (p. 5080). The location correction works additively, so it lifts frequent events relatively more than rare ones. The alternative is a grid-cell multiplication factor from the uncorrected and corrected 1-year storms, which would raise rare events much more while keeping the radar's spatial pattern. The authors warn that such a factor is "disrupting the homogeneity of the sampled events", because it adds far more to the intense events than to the weaker ones. They also doubt that a factor derived from 1-year events can be applied to much rarer ones.
- **Warning on the reference:** section 4 (p. 5081). Using BW-Stat's scale and shape as the QM target would impose BW-Stat's regional heterogeneity on the radar data, which comes from pooling over sparse stations.
- **Why the radar tail is low:** section 4. The authors blame a fixed Z–R relation that misses the change in drop size at high intensity. They cite Kreklow et al. (2020): RADKLIM detects fewer heavy-rain days than gauges, but the mean amount on a heavy-rain day (> 20 mm) is almost identical.

## Relevance to DECADE

H3 (#20), calibration across the ODYSSEY → CIRRUS change.

- **Distribution mapping versus one factor.** The paper is a worked case of the choice we face between seasonal factors and quantile mapping. Its correction is a static transfer function, built once from archives and applied to every cell. This is compatible with our real-time constraint. It also shows the cost of each choice. A shift fitted on frequent quantiles barely touches the tail. A multiplicative factor fitted on frequent quantiles inflates the tail, and nothing guarantees that it is right there.
- **Correct where the reference is robust.** The authors correct only the part of the distribution that both datasets estimate reliably (the 1-year level) and leave the tail as the radar sees it. For H3 this argues for building the transfer from the well-sampled body of the distribution (seasonal quantiles after wet-frequency matching). The upper tail, which 4 days of overlap and a short CIRRUS archive cannot constrain, should be handled with an explicit and documented rule rather than an extrapolated factor.
- **Homogeneity.** Their warning concerns the relative size of events within one pooled sample. The same logic applies to our series. If ODYSSEY and CIRRUS were corrected with factors that treat intense and weak rain differently, an apparent change in extremes could appear at 7/2024 that comes from the correction and not from the weather. Any H3 variant should therefore be checked on the upper quantiles on both sides of the switch.
- **The bridge's own heterogeneity.** The remark that a gauge-based reference carries its own spatial structure applies to a national bridge (RADCLIM, VMM radar). Whatever spatial pattern the bridge has will be imprinted on both products.
- **Season split.** Restricting the analysis to April–October to avoid solid precipitation is consistent with treating the cold season separately.

## Limits

- The QM here maps the spatial distribution of a fitted extreme-value parameter against an interpolated design-storm product. It is not a QM of rain-rate or reflectivity distributions in time, so neither the method nor its numbers carry over directly to the matching of ODYSSEY and CIRRUS distributions.
- The reference is gauge-based design storms, not another radar product. There is no product change in the radar record: RADKLIM is a homogeneous reprocessing, which is exactly what we lack.
- Only April–October, one German state with complex orography (90–1495 m), 1 km RADKLIM. ODYSSEY is 2 km / 15 min maximum reflectivity over flat Belgium.
- No wet threshold or wet-frequency step: the method works on the largest events only.
- The "homogeneity" warning is qualitative. The Supplement figure (S3) showing the multiplicative variant was not read.
