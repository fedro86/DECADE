# Technical Note: Downscaling RCM precipitation to the station scale using statistical transformations – a comparison of methods

- **Authors, year, venue:** Gudmundsson, L., Bremnes, J. B., Haugen, J. E., Engen-Skaugen, T., 2012. Hydrology and Earth System Sciences 16, 3383–3390.
- **Link:** [10.5194/hess-16-3383-2012](https://doi.org/10.5194/hess-16-3383-2012)
- **Access:** open access, CC Attribution 3.0.
- **Read:** full text; sections 2.1–2.3 (the three classes of transformation, dry-day handling, extrapolation), 3 (data), 4.1–4.2 (scores, cross-validation, ranking), 5 (performance), 6 (limits), Appendix A (terminology).

## What it is

A short comparison of statistical transformations ("quantile mapping" in the broad sense) that map modelled daily precipitation onto the observed distribution. The model is HIRHAM at 25 km forced by ERA-40; the reference is 82 Norwegian stations, 1960–2000. Eleven transformations in three classes are scored with 10-fold cross-validation on the mean absolute error between the observed and the corrected empirical CDF, overall and per decile of probability. The methods are released in the R package `qmap`.

## Numbers we use

- **Three classes of method:** section 2. (1) *Distribution derived* (section 2.1): Eq. (2), `Po = Fo⁻¹(Fm(Pm))`, with a Bernoulli mixture for occurrence and a Gamma, Weibull, log-normal or exponential law for amounts; the two distributions are fitted separately to `Po` and `Pm` by maximum likelihood. (2) *Parametric* (section 2.2): the quantile–quantile relation is fitted directly, Eqs. (3)–(7): `b·Pm`, `a + b·Pm`, `b·Pm^c`, `b·(Pm − x)^c`, `(a + b·Pm)(1 − e^(−(Pm − x)/τ))`. (3) *Nonparametric* (section 2.3): empirical quantiles (QUANT) and a cubic smoothing spline (SSPLIN, smoothing parameter by generalised cross-validation).
- **Best methods: QUANT and SSPLINE:** section 5 and Fig. 4. The two nonparametric methods have the best mean relative error, including the extreme percentiles; Fig. 4 lists QUANT first and SSPLINE second. Parametric forms with three or more free parameters (Eqs. 6 and 7) come close; the simple scaling `b·Pm` (Eq. 3) is clearly worse.
- **Distribution derived methods rank lowest:** section 5. Bernoulli–Weibull is the best of them, Bernoulli–log-normal is the worst of all methods and gives no visible improvement (Fig. 2). Bernoulli–exponential and Bernoulli–log-normal increase the error at the most extreme values (Fig. 3). The authors attribute this to fitting `Fo` and `Fm` separately, which does not optimise the transformation itself.
- **Dry days, parametric and spline methods:** sections 2.2 and 2.3.2. The transformation is fitted only on the part of the CDF that corresponds to observed wet days (`Po > 0`), by least squares; modelled values that fall in the dry part of the observed empirical CDF are set to zero. This handles the usual case of a model with too many wet days; the paper does not treat a model that is drier than the observations.
- **0.1 mm/day:** section 2.2. The observations have a resolution of 0.1 mm/day, which in practice sets the wet-day threshold to 0.1 mm/day. No other threshold is introduced.
- **QUANT implementation:** section 2.3.1. Following Boé et al. (2007), each empirical CDF is stored as a table of empirical percentiles, with linear interpolation between them. The paper does not state the percentile step.
- **Out of range, QUANT:** section 2.3.1. A new model value larger than every training value receives the correction of the highest training quantile (constant extrapolation, as in Boé et al. 2007 and Themeßl et al. 2012).
- **10-fold cross-validation in contiguous blocks:** section 4.1. The 1960–2000 series is cut into 10 continuous time intervals; each is predicted with a transformation calibrated on the other nine, and the mean of the 10 errors is reported. This is how the transfer function is tested out of sample.
- **MAE₀.₁ … MAE₁.₀:** section 4.1. Mean absolute error between observed and corrected empirical CDF within 0.1-wide probability intervals of the observed CDF; MAE₀.₁ reflects the number of wet days, MAE₁.₀ the most extreme events, and their mean equals the total MAE.
- **Relative error ranking:** section 4.2, following Reichler and Kim (2008). Each score is divided by the score of the uncorrected model (values below 1 mean improvement) and the relative errors are averaged per method.
- **Overfitting warning:** section 5. Nonparametric transformations may overfit "if calibrated using small data samples, i.e. time series that cover only a short period".

## Relevance to DECADE

H3 (#20), harmonisation of ODYSSEY and CIRRUS through a bridge dataset.

- **Choice of transformation:** for every H3 variant (pan-European bridge, national bridge, plain seasonal quantile mapping) the paper supports an empirical, nonparametric transfer (a percentile table with linear interpolation) over a fitted distribution or a single scaling factor. A single factor, the equivalent of one dB offset for the whole distribution, is the class that performs worst here (Eq. 3).
- **Real-time constraint:** QUANT is a lookup table of percentiles computed beforehand, applied by interpolation. It needs no data from the time of application, so it satisfies the real-time requirement.
- **Wet-pixel frequency first:** the paper's handling of zeros (fit only the wet part of the reference CDF, set to zero what maps into the dry part) is the published form of matching the wet frequency before mapping intensities, for the case where the product to correct has too many wet pixels. The opposite case is not covered here; see Themeßl et al. (2012), frequency adaptation.
- **Extremes:** the constant correction of the highest training quantile is the reference rule for radar values above the calibration range.
- **Validation:** the contiguous-block cross-validation and the per-decile MAE give a ready protocol to compare the three H3 variants out of sample, and to see separately whether they fix the wet fraction (MAE₀.₁) and the tail (MAE₁.₀).

## Limits

- Daily station totals against a 25 km model, not 5 min or 15 min radar reflectivity composites at 1–2 km compared on a 5.5–9 km bridge grid. Spatial and temporal aggregation change the wet fraction and the tails, so the ranking is not guaranteed to hold for our data.
- Calibration uses 41 years with full overlap between model and observations. In H3 each product is calibrated against the bridge separately, and CIRRUS has only the period since 7/2024; the direct ODYSSEY–CIRRUS overlap is 4 days. The paper itself warns that nonparametric methods may overfit short samples.
- The paper does not say whether the transformations were fitted per season or month, so it gives no guidance on the length of the seasonal windows.
- The wet-day threshold (0.1 mm/day) comes from the gauge resolution, not from a sensitivity study; it does not transfer to radar rain rates.
- Only one region (Norway), one model and one variable; the stationarity of the correction is assumed, not shown (section 6).
