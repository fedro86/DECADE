# OPERA the Radar Project

- **Authors, year, venue:** E. Saltikoff, G. Haase, L. Delobbe, N. Gaussiat,
  M. Martet, D. Idziorek, H. Leijnse, P. Novák, M. Lukach, K. Stephan, 2019,
  *Atmosphere* 10, 320
- **Link:** [10.3390/atmos10060320](https://doi.org/10.3390/atmos10060320)
- **Access:** open, CC BY 4.0
- **Read:** full text (13 pages)

## What it is

An overview of OPERA, written by people from the national services and from
the data centre: the radar network in 2019, the central processing of the OPERA
data centre (Odyssey), the quality of the composites seen from long-term
statistics and from a comparison with the MESAN analysis, the ODIM data model,
and the users. It describes the ODYSSEY composites (2 km, every 15 min), not
CIRRUS, which came later.

## Numbers we use

- **Compositing rule** (section 2.2): for each composite pixel, all single-scan
  pixels in the vertical column above it contribute. In the maximum
  reflectivity composite the value is the maximum of the contributing pixels,
  and the quality index is their maximum quality index. In the rain-rate
  composite it is the quality-weighted mean reflectivity, converted with
  Marshall–Palmer (a = 200, b = 1.6). The hourly accumulation integrates the
  last four 15 min rain-rate products.
- **Timing** (sections 1, 3.3): composites on the hour and at 15, 30 and
  45 minutes past, issued about 15 min after the start of data acquisition.
  The paper does not give the window of scans used for one composite, and does
  not say whether several volumes of the same radar within that window
  contribute.
- **Central quality control** (section 2.2): an anomaly-removal module; a
  monthly hit-accumulation clutter filter (threshold typically 0.6); since late
  2015 a beam-blockage correction, with blockage above 70% set to nodata; a
  satellite filter (NWC SAF precipitating clouds), which sets echoes with zero
  probability of precipitation to undetect. The quality index is the minimum of
  the three, weighted by distance from the radar and beam height.
- **Not implemented** (section 4): a vertical profile of reflectivity
  correction, and a Z–R relation that depends on the phase (rain or snow).
- **Bias** (section 3.1): against MESAN, OPERA underestimates by typically
  1–3 mm/day (2015–2017), more in winter because of beam overshooting.
- **Input data** (section 4): since March 2017 the members send their best
  processed data, documenting the processing, and the unfiltered reflectivity
  as a separate quantity; the change was introduced gradually.

## Relevance to DECADE

- **H6 (time alignment of ODYSSEY and CIRRUS):** it confirms the maximum over
  the vertical column, but it does not settle the time window. That remains as
  in the 2024 OPERA comparison of CIRRUS and ODYSSEY, whose text
  ([NT−10, NT+5]) and Table 3 (NT−9 to NT+9) disagree.
- **H1 (convective/stratiform classes):** without a vertical-profile correction,
  a bright band can reach the composite as high reflectivity. This supports
  checking whether the January Steiner intensity centres are bright band.
- **Archive homogeneity:** processing changed in December 2015 and from March
  2017, so the archive is not homogeneous in time (the authors warn about
  climate studies).

## Limits

An overview, not a technical specification: the compositing is described in a
few sentences and refers to other reports. It describes ODYSSEY as of 2019; the
CIRRUS line and the later ODYSSEY settings are in the 2024 OPERA documents.
