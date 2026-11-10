# General application of the relative calibration adjustment (RCA) technique for monitoring and correcting radar reflectivity calibration

- **Authors, year, venue:** D. B. Wolff, D. A. Marks, W. A. Petersen, 2015,
  *Journal of Atmospheric and Oceanic Technology* 32(3), 496–506
- **Link:** https://doi.org/10.1175/JTECH-D-13-00185.1
- **Access:** published version, downloaded by the user from the AMS site (the
  site blocks automatic download). The PDF carries no licence or copyright
  line, only the AMS download stamp on each page.
- **Read:** full text (abstract, sections 1–6, Tables 1–5, figure captions).
  Page numbers below are journal pages.

## What it is

The follow-up of Silberstein et al. (2008) by the same NASA team. The RCA
method (daily 95th percentile of the reflectivity of fixed clutter targets,
compared with a baseline) is moved from the KPOL radar on Kwajalein to NASA's
transportable S-band polarimetric radar NPOL, in north-eastern Iowa during the
IFloodS field campaign (1 May–15 June 2013), a continental site with strong
clutter, hail and intense anomalous propagation (AP). The paper writes the
method as a general recipe: how to build the clutter map, how to set the
baseline, how to tie it to an absolute calibration, and how to read changes.
Two new KPOL cases show an elevation change and a hardware failure.

## Numbers we use

- **Clutter map** (section 2a, p. 497–498): one precipitation-free day
  (2 June 2013); fixed polar grid of 1 km × 1°; only ranges 1–5 km from the
  radar, to avoid sidelobe and beam-propagation effects; a cell is flagged in
  a scan if at least one gate exceeds 55 dBZ; "percent on" = share of the
  day's scans in which the cell is flagged; the clutter map is the cells with
  percent on ≥ 50%.
- **Threshold choice** (section 2a, p. 498): the threshold must be above most
  rain reflectivities of the regime but below the usual reflectivity of
  nearby clutter; 50 dBZ suits Kwajalein, 55 dBZ Iowa, where hail is more
  common. The authors call the 55 dBZ value "somewhat arbitrary".
- **Elevation** (section 3, p. 499): only the lowest sweep of the PPI scans is
  used; the angle of that sweep is not given.
- **Daily statistic** (section 2b, p. 499): all clutter-area reflectivities of
  the day, rain included, give a PDF and a CDF; the 95th percentile is read
  from the CDF. RCA = dBZ95(baseline) − dBZ95(daily), in dB; positive means
  the radar runs low. On a rainy day (4 May 2013) the hourly distributions
  differ in the lower part but converge at the 95th percentile (Fig. 2b,
  p. 500).
- **Baseline** (sections 2b and 3, p. 499): the 95th percentile of a day
  without precipitation or AP (2 June 2013); it is a benchmark, not an
  absolute calibration.
- **Stability** (section 3, p. 499 and 501): daily RCA over IFloodS has a
  standard deviation of 0.13 dB (Fig. 3); May 2013 mean dBZ95 = 60.59 dBZ,
  hourly and daily standard deviations 0.18 and 0.12 dB; hourly standard
  deviations ≤ 0.3 dB also for NPOL in MC3E (2011) and IPHEx (2014) and for
  KPOL.
- **Choice of the clutter-map day** (section 3, Tables 3–4, p. 501–503): maps
  built from a light-rain day (2 May), an extreme-AP day (16 May) and three
  other days give daily RCA series with mean between −0.13 and +0.14 dB and
  standard deviation 0.13–0.14 dB; the method is largely insensitive to the
  day chosen, as long as the map stays within 1–5 km.
- **Operational rule** (section 4, p. 501): day-to-day changes within ±0.5 dB
  are not corrected (inherent uncertainty); a jump larger than ±0.5 dB thought
  to come from calibration is investigated and then corrected by hand.
  Abstract: relative calibration uncertainty ±0.5 dB or better; section 6
  (p. 506): ±0.5–1.0 dB or better.
- **Absolute baseline** (section 4, p. 503–504): the baseline is shifted once
  an independent absolute calibration is known (example: baseline 50 dBZ and
  a −2 dB bias give a new baseline of 52 dBZ). For IFloodS: KDP
  self-consistency over 30–48 dBZ, iterated to 0.1 dB, and four 2D video
  disdrometers at 15–69 km compared with NPOL at 0.9° elevation (2DVD − NPOL
  = +1.80 to +2.61 dB, combined +2.15 dB, Table 5). Decision: NPOL low by
  2.0 dB from 1 May to 6 June and by 2.2 dB from 7 to 15 June 2013.
- **Changes detected** (sections 4–5, p. 504–505): a step of about 0.2 dB
  after 6 June 2013 at NPOL, tied to the polarization switches; at KPOL an
  elevation-offset change of 0.05° (February 2014) gave an RCA drop of
  0.49 dB, in line with ~1 dB per 0.1° from Silberstein et al. (2008), and
  is not a calibration change; a modulator failure on 31 December 2013 (less
  pulse width and power) gave an RCA jump of about +4 dB, back to normal after
  the replacement the next week.
- **Radars tested** (sections 3–4 and 6): NPOL (IFloodS, MC3E, IPHEx) and
  KPOL (16-plus years corrected, Marks et al. 2009). No WSR-88D or other
  operational network radar is tested; extension to "other S-band
  surveillance ground-based radars (that do not filter ground clutter)" is
  given as feasible only (section 6, p. 506).
- **Doppler filter** (Table 2, p. 497; section 6, p. 506): NPOL records both
  total (unfiltered) and filtered reflectivity; the method is meant for radars
  that do not filter ground clutter. The text does not say explicitly which
  of the two fields fed the RCA.

## What it adds to Silberstein et al. (2008)

- A written recipe for the clutter map (1 km × 1° cells, fixed threshold,
  percent on ≥ 50% on one dry day) instead of a map described only in outline.
- The clutter field limited to 1–5 km, whereas the 2008 paper used the whole
  clutter field.
- Proof that the method works in a continental setting with hail and intense
  AP, and that the result hardly depends on the day used for the map.
- Smaller uncertainty: daily standard deviation about 0.13 dB and an
  operational ±0.5 dB rule, against agreement within 1–2 dB in 2008.
- A clear procedure for tying the relative baseline to an absolute
  calibration (self-consistency, disdrometers) and correcting past data.

## Relevance to DECADE

Second primary source, after Silberstein et al. (2008), for the later H2
option "calibration drift": following a radar's calibration over 2012–2024
with stable fixed points. What transfers: the way the map is built (cells
where a high threshold is exceeded in at least half of the scans of a dry day)
is the same idea as our fixed points above 70 dBZ that come back at the same
pixel; the threshold must sit above the local rain regime, and hail in Belgium
argues for a high one; a daily 95th percentile against a dry-day baseline,
with steps above about 0.5 dB as candidate changes; the reminder that an
elevation change of 0.1° moves the statistic by about 1 dB, so a change of
scan strategy looks like a calibration change; and an absolute level needs a
separate reference.

What does not transfer directly: our data are a 2D maximum-reflectivity
composite at 2 km, not single-radar volumes. The 1–5 km ring around a radar
covers only a few composite pixels, the elevation behind each pixel is
unknown, the maximum rule may pick another radar where coverages overlap, and
the national clutter filters have already removed most clutter. The fixed
points left in the composite are filter residues, and the method holds only
if the filters and the compositing stay fixed over time.

## Limits

Only S-band radars (NPOL, KPOL); Belgian radars are C-band. The IFloodS test
covers six weeks of spring 2013 on a research radar operated for a field
campaign, not an operational network. The method needs reflectivity without
Doppler clutter filtering, which the composite does not offer. The 55 dBZ
threshold is admitted to be partly arbitrary. RCA follows relative
calibration only and cannot tell a power change from a pointing change
without engineering information.
