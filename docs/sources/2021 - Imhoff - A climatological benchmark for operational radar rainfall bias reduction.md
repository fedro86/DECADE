# A climatological benchmark for operational radar rainfall bias reduction

- **Authors, year, venue:** Imhoff, R., Brauer, C., van Heeringen, K.-J., Leijnse, H., Overeem, A., Weerts, A., Uijlenhoet, R., 2021. Hydrology and Earth System Sciences 25, 4061–4080.
- **Link:** [10.5194/hess-25-4061-2021](https://doi.org/10.5194/hess-25-4061-2021)
- **Access:** open access, CC BY 4.0.
- **Read:** full text; sections 2.1 (radar and reference data), 2.2.1 (mean field bias), 2.2.2 (CARROTS), 2.4 and 3.4 (sensitivity), 3.1–3.3 (results), 4 (discussion), Tables 1, 2 and A1. The hydrological model set-up (2.3) was read but is not used here.

## What it is

CARROTS ("Climatology-based Adjustments for Radar Rainfall in an OperaTional Setting") is a fixed set of multiplicative correction factors, one per 1 km grid cell and per day of the year, for the KNMI two-radar composite of the Netherlands (pseudo-CAPPI at 1500 m, Z = 200R^1.6, 5 min). The factors are the ratio of a gauge-adjusted reference to the unadjusted radar over 10 years (2009–2018). They are compared with the operational hourly mean field bias (MFB) adjustment on country-average rainfall, on annual sums for 12 basins and on simulated discharge.

## Numbers we use

- **Size of the bias:** section 2.2 (p. 4064). The unadjusted radar (RU) underestimates the reference by 55 % on average over the Dutch land area, 65 % in winter and 50–55 % in the other seasons. In Table 1 (fit through the origin between RA and RU, daily country averages) the slope is 0.35 in DJF, 0.48 in MAM, 0.50 in JJA, 0.45 in SON and 0.45 overall, with R² = 0.79 overall.
- **Reference dataset (RA):** section 2.1 (pp. 4063–4064). The same radar product, adjusted with an hourly MFB from 32 automatic gauges and a daily spatial adjustment from 319 manual gauges (Barnes-type weights, smoothness 12 km; Eqs. 4–5, section 2.2.3). It is available only with a delay of 1–2 months, which is why it can serve offline but not in real time. RA and RU share the 1 km / 5 min grid.
- **Years used:** 2009–2018 (section 2.2.2). The year 2008 is left out because RU behaved differently, often overestimating in the first half of the year (section 2.1, p. 4064). Leap days are left out.
- **How a factor is built:** section 2.2.2, Eq. (3) (p. 4065). (1) For each day of 2009–2018, sum all 5 min values of RU and of RA over a 31-day moving window (the day plus 15 days on each side). (2) For each day of the year, average these 31-day sums over the 10 years. (3) The factor is F_clim(i, j) = RA(i, j) / RU(i, j), per grid cell. So it is a ratio of long sums, not a mean of daily ratios, and it is applied unchanged to every 5 min field of that day.
- **MFB for comparison:** section 2.2.1, Eq. (2). The ratio of hourly gauge sums to radar sums at the 32 automatic gauges. It is computed only when both sums are at least 1.0 mm, otherwise the factor is 1.0.
- **Values of the factors:** section 3.1 (p. 4067), Figs. 3–4. In January the catchment-averaged factors range from 2.1 (Beemster) to 3.2 (Hupsel Brook). In June they range from 1.3 (Grote Waterleiding) to 1.6 (Roggelsebeek). From December to March the factors in the south and east are more than twice those in the centre and north-west. The minimum falls between April and June (Fig. 4 caption).
- **Why winter is worse:** section 3.1. With a wet-adiabatic lapse rate of 5.5 K km⁻¹ applied to ground temperatures, the 1500 m pseudo-CAPPI lies above the 0 °C level from December to March (Fig. 4b–c), so the radar often samples snow above the melting layer.
- **Country-average result:** section 3.2, Table 2. The remaining underestimation is 10 % with MFB and 8 % with CARROTS (fit slopes 0.90 and 0.92 overall). CARROTS has a wider spread (R² 0.85 against 0.98 for MFB) and a higher hourly fractional standard error in every year (Table A1; e.g. DJF 2009: RU 1.10, MFB 0.49, CARROTS 0.74).
- **Basin result:** section 3.2, Fig. 6. CARROTS gives annual sums closer to the reference than MFB in 9 of 12 basins. Far from the radars, MFB still underestimates by 20 % on the Aa (610 against 761 mm per year) and by 13 % on the Regge (673 against 776 mm), while CARROTS stays within about 5 %.
- **Discharge:** section 3.3. CARROTS input gives better discharge than MFB in 11 of 12 basins. The exception is Beemster, with a KGE of 0.92 (CARROTS) against 0.96 (MFB).
- **Window length:** sections 2.4 and 3.4, Fig. 8 (pp. 4070–4071). Windows of 1 day, 1 week, 2 weeks, 31 days, 6 weeks and 2 months were tested. From 2 weeks upwards the factors hardly change. A 1-day window fluctuates strongly from day to day and a 1-week window still follows single events. The authors expect a 3-month window to behave like the 31-day one but smoother, and windows of half a year or more to lose the seasonal cycle.
- **Archive length:** section 3.4 (p. 4071). Leaving one year out of the 10 changes the factors little (vertical bars in Fig. 4c), so 10 years were enough. The minimum number of years is left open (section 4, p. 4074).
- **Extremes:** section 4 (p. 4074). For the 10 highest daily sums in the Aa and Hupsel Brook, both methods are off by about 20 % on average, against 50–60 % without correction. CARROTS overestimates in 25 % of these cases and MFB in 15 %. Single events can still be off by 48 % (CARROTS) and 64 % (MFB). The authors suggest rain-type-dependent Z–R or dBZ-dependent factors derived in the same way.
- **Validation is not independent:** section 2.3 (p. 4066). The same 10 years and the same reference serve both to derive and to validate the factors; the leave-one-year-out test is the only check.

## Relevance to DECADE

H3 (#20), calibration across the ODYSSEY → CIRRUS change.

- **Climatological factors computed beforehand.** This is the published model for a correction that satisfies our real-time constraint. The factors come from an offline reference and an archive, and they are then applied with no same-day gauges. The authors name this independence from the timeliness of gauges as the main advantage (sections 4–5).
- **Seasonal resolution is enough.** The window test shows that any window of 2 weeks or more gives nearly the same factors, and that a 3-month (seasonal) window is expected to be close to the 31-day one. This supports seasonal factors for H3, provided the window is not stretched to half a year or more.
- **Every product change needs its own factors.** The paper states that the factors must be recalculated after any change in radars, calibration, post-processing or compositing (section 4, p. 4073; section 5). The ODYSSEY → CIRRUS switch is such a change. So each product needs its own factors against the same stable reference, which is the logic of the bridge variants. RADCLIM, a merged radar–gauge product available offline, plays the role that RA plays here.
- **What a ratio of sums cannot do.** The factor is one multiplicative number per cell and day. It corrects the mean but cannot change the wet-pixel frequency or the shape of the intensity distribution, which is why we match the wet frequency first. The authors' remark on extremes (dBZ-dependent factors) points in the direction of distribution (quantile) mapping, which our third variant tests.
- **Benchmark role.** The paper frames CARROTS as the minimum a more elaborate adjustment should beat. That is a useful way to rank our three variants: plain seasonal factors should be the baseline.

## Limits

- One national composite of 2 radars (Den Helder and De Bilt, later Herwijnen) at a constant-altitude pseudo-CAPPI. It is not a pan-European maximum-reflectivity composite, so the factors fold together Z–R, vertical-profile and range effects that differ in OPERA.
- The bias here is 55 % (a factor of about 2.2) and mostly from the melting layer in winter. The ODYSSEY–CIRRUS gap is a difference between two composites, not between radar and ground; only the method transfers, not the values.
- 10 years of archive for each product. CIRRUS starts in 7/2024, so its archive is far shorter, and the paper does not say how short an archive can be.
- The radar replacement of 2016–2017 had little effect only because dual-polarisation was not yet used; this is no guarantee for other product changes.
- Training and validation use the same data and the same reference.
- Daily factors are applied to 5 min fields, so intensity-dependent errors remain, especially for extremes.
