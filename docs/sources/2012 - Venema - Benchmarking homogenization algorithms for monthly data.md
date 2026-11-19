# Benchmarking homogenization algorithms for monthly data

- **Authors, year, venue:** Venema, V. K. C., Mestre, O., Aguilar, E., Auer, I., Guijarro, J. A., Domonkos, P., and 31 co-authors, 2012. Climate of the Past 8, 89–115.
- **Link:** [10.5194/cp-8-89-2012](https://doi.org/10.5194/cp-8-89-2012)
- **Access:** open access, CC BY 3.0; PDF downloaded directly from the Copernicus site.
- **Read:** full text (27 pages): sections 1–8, Tables 1–4 and 9. Figures could not be rendered here: their content is known only from the captions and the text; some tables come out scrambled in the text extraction and only the values that could be read unambiguously are used below.

## What it is

The blind benchmark of the COST Action HOME: monthly temperature and precipitation networks of 5 to 15 stations over 100 years (1900–1999), built either as "surrogate" data that copy the distribution, autocorrelation and cross-correlation of real homogenised European networks, or as "synthetic" data whose candidate/reference ratio or difference is uncorrelated Gaussian white noise. Known breaks, outliers, missing periods, local trends and a network-wide trend were inserted; 25 blind and 22 late contributions from 13 algorithms (MASH, PRODIGE, USHCN, ACMANT, Craddock, SNHT, Climatol, RHtests variants) were scored against the truth with centred RMSE, trend errors and detection skill scores.

## Numbers we use

- **Relative series: ratio for precipitation, difference for temperature:** section 4 (p. 94). All relative methods compare the candidate with a reference through the difference (temperature) or the ratio (precipitation); precipitation is treated as the multiplicative case and temperature as the additive one (abstract, p. 89; section 1, p. 91). The synthetic data were built in the same way, from the ratio of each precipitation station to the network mean (section 2.3, p. 92).
- **Monthly data: annual, parallel or serial:** section 4 (p. 94). The comparison can be made on annual, seasonal or monthly values; the twelve monthly (or four seasonal) series can be tested independently "in parallel" or one after the other as a single serial series, and the parallel results then need a synthesis step. Table 1 (p. 95) lists which method uses which time step.
- **Size of the inserted precipitation breaks:** section 3 (p. 93). Break sizes are Gaussian with a standard deviation of 15 % for precipitation (0.8 °C for temperature), with a seasonal cycle of standard deviation 7.5 % (0.4 °C); breaks occur on average five times per 100 years (station rate drawn between 2 and 8 % per year).
- **Size of real precipitation breaks:** section 6.3.2 (p. 108). In the real (not simulated) precipitation networks the detected annual breaks have a standard deviation of 9.5 mm, about 10 %, against 15 mm (19 %) detected in the artificial data; the seasonal cycle of the precipitation breaks is 12 % in real data and 19 % in artificial data (p. 109). Detected breaks are rarer in real precipitation data (1.0 % per year) than in the artificial data (2.3 %) (p. 108).
- **Precipitation breaks are hard to detect even in 100-year series:** Table 9 (p. 106). For precipitation the probability of detection ranges from 0.04 (SNHT DWD) to 0.26 (MASH main) with probabilities of false detection of 0.00–0.05; detection is scored at yearly resolution, a year with a break counting as one break (section 5, p. 96). Most algorithms keep the false detection rate well below the target 5 % level (section 6.1.6, p. 103).
- **Autocorrelation makes the problem harder:** section 6.3.1 (p. 108). On 200 extra networks per section, the white-noise synthetic data were easier to homogenise than the realistic surrogate data: monthly CRMSE after homogenisation 7 % smaller and the spread of trend errors 15 % smaller, both highly significant. The authors suggest the lag-one autocorrelation of the surrogate data, or variability at all lags, or non-Gaussian distributions as possible causes, without testing them (section 7.2, p. 111).
- **Monthly precipitation ratios are noisy:** section 7.1 (p. 110). Improvements were much larger for yearly and decadal data than for monthly data, which the authors attribute mainly to the low signal-to-noise ratio of the precipitation ratio series caused by the high spatial variability of precipitation. Monthly corrections of precipitation were noisy; annual correction factors are recommended for typical precipitation networks (p. 110).
- **Only the best methods improve precipitation:** abstract (p. 90) and section 6.1.1 (pp. 99–100). Over half of the precipitation contributions did not improve the station CRMSE and none improved the network-mean CRMSE meaningfully.
- **Metadata for the dates:** section 8.1 (p. 112). Metadata are preferred to statistics for designating the dates of breaks, but statistical homogenisation should always be applied as well to find undocumented ones.

## Relevance to DECADE

H3 (#20), homogeneity of the bridge: the step of the monthly radar / ERA5-Land ratio at 7/2024 and 9/2024 (`opera_ds/homog.py`, `step`).

- **The relative series is the ratio, tested in log.** The paper confirms that precipitation is homogenised through the candidate/reference ratio (section 4, p. 94) and treated as multiplicative; working with log10 of the ratio, as `step` does, turns the multiplicative step into an additive one, which is the form the WMO guidelines describe (see the 2020 WMO summary, section 5.1, p. 41). Here the "candidate" is the radar product and the "reference" is ERA5-Land; the ratio cannot say which of the two changed.
- **Expected break sizes are of order 10–15 %.** Real precipitation breaks in station networks have a spread of about 10 % (p. 108); the benchmark used 15 % (p. 93). A step of 0.04–0.06 in log10 (about 10–15 %, computed here) is therefore the order of size a homogenisation study would care about; much smaller steps are unlikely to be detectable in 40–46 months.
- **Detection power is low for monthly precipitation ratios.** Even over 100 years, with dense networks, at most about a quarter of the inserted precipitation breaks were found (Table 9, p. 106). Our series is far shorter; a non-significant result at 7/2024 or 9/2024 will not prove that there is no step, only bound its size.
- **Known dates.** The benchmark is about undocumented breaks; it does not test a single documented date. It supports using the metadata date (p. 112), which is what H3 does with 7/2024 and 9/2024.
- **Seasonality and autocorrelation.** It shows that both monthly analysis choices exist (parallel per calendar month or serial, p. 94) and that realistic autocorrelation makes the problem harder (p. 108), but gives no recipe for correcting a test for autocorrelation.
- **Not settled:** which test statistic, the significance level for a documented date, the minimum detectable step for about 18 months on each side, and how to remove the seasonal cycle of the ratio with only three or four values per calendar month.

## Limits

- **Station networks, not gridded products:** candidate and references are rain gauges in dense European networks; our pair is a radar composite against a reanalysis over all of Belgium, with much higher correlation between the two series and different error sources.
- **Long series:** 100-year networks with about five breaks per century; nothing on series of 3–4 years.
- **Undocumented breaks:** the algorithms search for unknown dates; detection scores are computed at yearly resolution (p. 96), so they say nothing about monthly date accuracy.
- **Precipitation results rest on few contributions** (one algorithm, AnClim main, for the real-data comparison, p. 108), and the authors note that the statistical properties of precipitation breaks are less known than for temperature (p. 110).
