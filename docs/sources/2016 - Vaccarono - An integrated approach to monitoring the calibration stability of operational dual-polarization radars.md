# An integrated approach to monitoring the calibration stability of operational dual-polarization radars

- **Authors, year, venue:** M. Vaccarono, R. Bechini, C. V. Chandrasekar,
  R. Cremonini, C. Cassardo, 2016, *Atmospheric Measurement Techniques* 9,
  5367–5383
- **Link:** https://doi.org/10.5194/amt-9-5367-2016 ·
  [PDF](https://amt.copernicus.org/articles/9/5367/2016/amt-9-5367-2016.pdf)
- **Access:** open access, Creative Commons Attribution 3.0 licence (p. 5367)
- **Read:** full text; the Sun-calibration and self-consistency sections
  (3.1, 3.4, 4.1, 4.2.3) only for what they add to the clutter monitoring.

## What it is

An operational application of the Silberstein et al. (2008) clutter method in
Europe: the two C-band polarimetric radars of Arpa Piemonte (Bric della Croce
near Turin, Monte Settepani in Liguria, north-western Italy), 28 July–13
October 2014. Ground-clutter monitoring is combined with Sun monitoring, with
the comparison of the two radars in their overlap (intercalibration) and with
an absolute check from polarimetric self-consistency in heavy rain. During the
period one radar lost transmitter power, and the clutter statistic caught it.

## Numbers we use

- **Clutter statistic** (section 3.3, p. 5371–5372): daily empirical CDF of
  clutter reflectivity at low elevation; the value at the 95th percentile is
  followed in time, for both polarizations. Conditions for it to work: stable
  targets, stable elevation, and rain echoes that do not dominate the clutter.
- **Selection of the targets** (section 3.3, p. 5371–5372): a clutter mask of
  echoes that appear very often; volumes are kept only when meteorological
  echoes are < 1% and clutter echoes > 12% of all echoes (hydrometeor
  classification). Daily maps of mean clutter reflectivity and of frequency of
  occurrence, averaged with previous days to avoid sudden changes; most
  clutter at the lowest elevation has a frequency above 95% (Fig. 3); Alpine
  clutter exceeds 64–65 dBZ.
- **Threshold:** clutter echoes below 20 dBZ are removed, to steepen the CDF
  around the 95th percentile and reduce the scatter of the daily value
  (section 3.3, p. 5372).
- **Time windows** (section 3, p. 5369): clutter daily; trend reference =
  mean over the last 4 weeks in real time; weekly averages in the combined
  index; Sun over the previous 5 days.
- **Overlap comparison** (section 3.2, p. 5370–5371): pairs of bins at the
  same height (±100 m), > 100 pairs needed, rain only (ρhv > 0.95), below the
  freezing level, dry radome; fit with slope 1, the intercept is the relative
  bias (2.4 dB on 28 July 2014, uncertainty about 4 dB; p. 5375–5376).
- **Detected failure** (section 5, p. 5379–5380): Monte Settepani clutter
  95th percentile 57 dB before 12 August, 54.7 dB after a transmitter module
  failed (step between 11 and 12 August), 56 dB after the repair of
  17 September; the overlap comparison shows the same change in rain.
- **Accuracy:** anomalous propagation added about 1 dB to the clutter
  95th percentile on one occasion (section 4.2.2, p. 5376); RMSE on the stable
  radar 0.45 dB for clutter alone, 0.38 dB combined (p. 5381); detection of
  calibration changes with an accuracy of about 2 dB (abstract, conclusions).

## Relevance to DECADE

European operational example for the later H2 option of following a radar's
calibration with fixed targets: a step of about 2–3 dB from a hardware
failure is visible in the daily clutter 95th percentile within one day, and
confirmed in rain by the radar that covers the same area. Both ideas
transfer to the composite: the stable fixed points above 70 dBZ as targets
(pixels where one radar covers alone), and the comparison of overlapping
radars in rain where two cover. The 20 dBZ floor, the frequency-of-occurrence
mask and the 4-week reference are concrete choices to start from.

Our data are a composite, not single-radar volumes: we see only the maximum
over radars and elevations at 2 km, after each country's clutter filter, so
the mask and the percentile would be computed on the composite pixels and
the radar behind each pixel has to be inferred from coverage.

## Limits

Two radars, 2.5 months of data, summer and autumn only; the authors note that
winter (snow, no self-consistency, fewer usable rain cases) is a weak period
for the other methods. The clutter selection relies on a polarimetric
hydrometeor classification in the polar volumes, which the composite does
not have. Clutter monitoring sees transmitter and receiver together and cannot
tell which one changed; it gives relative, not absolute, calibration.
