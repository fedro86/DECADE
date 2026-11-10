# Ground clutter as a monitor of radar stability at Kwajalein, RMI

- **Authors, year, venue:** D. S. Silberstein, D. B. Wolff, D. A. Marks,
  D. Atlas, J. L. Pippitt, 2008, *Journal of Atmospheric and Oceanic
  Technology* 25(11), 2037–2045
- **Link:** https://doi.org/10.1175/2008JTECHA1063.1 · NASA NTRS copy (the
  one read): https://ntrs.nasa.gov/citations/20080045517
- **Access:** the copy read is the manuscript submitted to the journal in
  September 2007, on NASA NTRS ("public use permitted"); the published version
  is free to read on the AMS site, but the site blocked automated access, so
  the numbers below come from the manuscript and may differ slightly from the
  published text.
- **Read:** full text of the manuscript (abstract, sections 1–3 and 5–8,
  figure and table captions). One manuscript page is missing from the NTRS
  file: the end of section 3 and the start of section 4 (range effects); the
  values of Tables 2 and 4 did not come through. Page numbers below are pages
  of the NTRS PDF.

## What it is

The original paper of the Relative Calibration Adjustment (RCA) method. NASA's
TRMM ground-validation team follows the calibration of the KPOL S-band radar
(Kwajalein atoll, tropical Pacific) day by day with the reflectivity of fixed
ground targets (buildings, towers) at the lowest elevation. A shift in the
daily distribution of clutter reflectivity is read as a change in radar
sensitivity. The record (August 1999–2007) is used to correct 7.5 years of
radar data.

## Numbers we use

- **Stability of the targets:** clutter echoes at the lowest elevation are
  stable "within better than ±1 dB" from hour to hour, day to day and month to
  month; they change only after hardware changes, failures or unknown causes
  (abstract, p. 3).
- **Selection of the targets** (section 3, p. 9–10): a clutter map of cells
  with a high probability of echo in the absence of rain, 1323 range-azimuth
  pairs of 1° × 1 km; about 5000 gate values per sweep (gates of 264 m, 200 m
  from March 2005), up to 240 sweeps per day (volume every ~6 min), over 10^6
  values per day. 77% of the clutter points are within 5 km of the radar,
  almost 90% within 10 km (section 2, p. 9).
- **Statistic** (section 3, p. 11): one cumulative distribution (CDF) per day
  of all reflectivities in the clutter map, rain included (no rain-free
  selection). The 95th percentile of the daily CDF is the reference; chosen
  empirically, because rain at Kwajalein rarely exceeds 45 dBZ, so the upper
  tail is set by clutter.
- **Calibration value** (section 3, p. 12): baseline fixed when the absolute
  calibration was known (August 1999, radar 6 dB low by comparison with the
  TRMM Precipitation Radar): 95th percentile of 1 August 1999 = 44 dBZ, plus
  6 dB, baseline = 50 dBZ. RCA = baseline − daily 95th percentile (dB).
- **Accuracy:** RCA follows the independent University of Washington offsets
  within 1–2 dB (section 3, p. 13); a deliberate ±2 dB change of the
  calibration offset in February 2007 is found again as about ±2 dB in the
  daily RCA (section 6, p. 15–16).
- **Size of real changes:** step of about 8 dB between two consecutive days
  (7–8 May 2004, directional coupler; section 5, p. 14); hardware events of
  −2 to −4.5 dB in 2000–2001 (Table 3); the shift seen in the clutter is also
  seen over the whole radar image (Fig. 10).
- **Pointing:** +0.1° of elevation raises the RCA by about 1 dB; during
  pointing errors the RCA must not be applied to rain (section 7, p. 16–17).
- **Range:** the day-to-day changes of RCA differ only slightly when the
  clutter is limited to 1, 5 or 10 km, so the whole clutter field is used
  (section 4, p. 14).
- **Anomalous propagation:** no significant effect found, probably because of
  the oceanic tropical setting (section 2, p. 9).

## Relevance to DECADE

Primary source for the later option asked by the reviewer for H2: follow the
calibration of a single radar over 2012–2024 with stable fixed points. In
DECADE the candidate targets are the fixed points above 70 dBZ that come back
every month at the same pixel; the daily or monthly 95th percentile (or
another high percentile) of their reflectivity, read where only one radar
covers the pixel, would play the role of the RCA, and a step or a slow decline
would flag a loss of sensitivity before the radar is switched off. The paper
gives the order of magnitude to expect: targets stable within about 1 dB, real
hardware changes of 2–8 dB.

Our data are a composite, not single-radar volumes: the maximum-reflectivity
rule, the projection to 2 km and the clutter filtering of each national
service sit between the radar and our pixel, and the elevation that sees a
target is not known. The method holds only if those steps stay fixed over
time.

## Limits

One S-band radar on a flat tropical atoll, targets mostly within 10 km;
Belgian radars are C-band, in a continental setting with anomalous
propagation and vegetation. The method needs radar data without Doppler
clutter filtering (section 8, p. 19), whereas the composite has already been
filtered: the fixed points left in it are clutter residues, and a change of
the filter (or of the scan strategy) would look like a calibration change.
Rain at Belgian latitudes can exceed 45 dBZ, so a 95th percentile may need
rain-free days or a higher threshold. RCA gives relative calibration only;
the absolute level needs another reference.
