# Improvement in algorithms for quality control of weather radar data (RADVOL-QC system)

- **Authors, year, venue:** Ośródka, K. and Szturc, J., 2022, Atmospheric Measurement Techniques, 15, 261–277
- **Link:** [10.5194/amt-15-261-2022](https://doi.org/10.5194/amt-15-261-2022)
- **Access:** open, CC BY 4.0
- **Read:** full text

## What it is

The paper updates RADVOL-QC, the operational quality-control chain of the Polish C-band network POLRAD (8 Doppler radars, 3 dual-polarisation; 1° beam, 1 km bins, 360 azimuths, 10 elevations, 250 km range, 10 min; Table 1). It details only the algorithms added since Ośródka et al. (2014): two polarimetric clutter detectors (DP.TURBINE, DP.NMET), a static clutter mask (TURBINE), new geometric RLAN spike detectors (SPIKE), and the replacement step (INTERP). All work on single-radar 3-D polar volumes; examples and checks use 2018–2019 data, mostly the Ramża, Legionowo, Pastewnik, Świdwin and Gdańsk radars, and are assessed with monthly accumulations and visual inspection.

## Numbers we use

Algorithms are listed in processing order (Table 2, p. 264). Only the new ones get parameters in this paper; the rest are named with a one-line task and refer back to Ośródka et al. (2014).

- **DP.TURBINE (Sect. 3.2, Eqs. 1–3, Fig. 4, Table 3).** (a) Fixed clutter, mainly wind turbines, also masts, chimneys, urban side-lobe echoes; it also weakens RLAN spikes. (b) Fuzzy logic on ρHV, SD(ZDR) and SD(ΦDP); the SDs are computed in 3 × 3 bin windows; weights 1.0 / 0.5 / 1.0; the class with the larger weighted sum wins. Membership functions are shown only as a figure (Fig. 4), not as numbers. Not applied within 25 km of the radar. Effectiveness, defined as 1 − (R_after − R_bg)/(R_raw − R_bg) on monthly 0.5° accumulations, averages 0.82 for turbines at Ramża (range 0.58–0.93; other obstacles 0.68–0.96; Table 3, Sept 2018). Raw monthly totals at turbines often exceed 1000 mm. QI = 0.75 for flagged bins (Eq. 3). (c) Needs a single-radar polar volume with polarimetric variables.
- **DP.NMET (Sect. 3.3, Eq. 4, Fig. 6).** (a) Echoes without rain: anomalous propagation, biological targets, also turbines, side-lobe clutter near the radar, and RLAN spikes. (b) Decision tree adapted from Seo et al. (2015): non-meteorological if [(Z ≥ 35 dBZ and ρHV < 0.95) or (Z < 35 dBZ and ρHV < 0.80)] and SD(ΦDP) ≥ 10°. SD(ZDR) was dropped as weakly informative. Thresholds tuned for POLRAD. Not applied within 25 km. QI = 0.75 (Eq. 5). (c) Single-radar polar volume with polarimetric variables.
- **TURBINE (Sect. 3.4, Eq. 6, Figs. 8–9).** (a) Fixed clutter (wind farms, residential and industrial buildings). (b) Static mask, built semi-automatically: accumulate precipitation fields from non-rainy time steps (rainy-bin count below a threshold) at the lowest elevations over a few months; flag bins above a radar-specific threshold; then edit by hand to drop mountain echoes. Threshold values are not given. Masks need regular updates. QI = 0.75 inside the mask. (c) Long series of the lowest-elevation field; method itself is a per-pixel accumulation and threshold, applied in polar coordinates in the paper.
- **SPIKE (Sect. 3.5, Eqs. 7–14, Figs. 10–11).** (a) Interference spikes (RLAN at C-band, and the sun); the "inverse" sub-type targets blocked sectors not explained by the terrain map. (b) Five sub-algorithms plus a verification step:
  - "wide": high reflectivity variance across the beam, low along it; used only when echo coverage of the elevation is below a pre-set threshold (value not given; details in the 2014 paper).
  - "narrow": spikes up to 5° wide; checks that bins at the same range on either side are weak.
  - "discontinuous" (new): per azimuth, count echo bins along the ray, n; p = max difference to neighbouring azimuths; P = mean of p over ±4 minus mean over ±40 azimuths; potential spike if P > 7.0 or (P > 2.0 and p > 215), and both neighbouring azimuths must also be potential. Bins are then confirmed if across-beam variance > 80 dBZ² and < 6 (mm⁶ m⁻³)² (Eq. 11). For the lowest elevation the candidate azimuths come from the next elevation up.
  - "shorter longitudinal" (new, aggressive, lowest elevation only, only for very affected radars): with a 7.0 dBZ threshold, run length along the beam > 110 bins and across < 8 bins (Eq. 12).
  - "inverse": bin at least 6.0 dBZ weaker than bins d = 1–2 azimuths away on both sides (Eq. 13); two lowest elevations only.
  - Verification: a spike is confirmed if the number of potential bins in an azimuth exceeds a pre-set threshold (value not given).
  - QI from 0.2 ("wide" bin) to 0.9 (Eq. 14).
  (c) Single-radar polar volume (azimuth/range geometry; "discontinuous" also uses the next elevation). No polarimetry needed, so it runs on the 5 single-pol radars too.
- **INTERP (Sect. 4).** (a) Replacement step, not a detector. (b) Spikes: average of the nearest unflagged bins left and right at the same range; "no echo" if either side is "no echo". DP.TURBINE / DP.NMET / TURBINE flags: clusters split at 720 bins; small clusters take the higher-elevation value shifted by the difference between the surrounding mean and the higher-elevation mean (Eqs. 15–16); large clusters take min(higher elevation, current) (Eq. 17); flagged echoes at the top elevation are removed. (c) Polar volume with several elevations.
- **NMET (Table 2 only).** (a) Echoes without rain (biological, anomalous propagation). (b) Uses echo altitude and intensity; no thresholds here. (c) Polar volume (needs height).
- **SPECK (Table 2 only; one sub-algorithm mentioned in Sect. 3.3).** (a) Isolated echoes (speckle). (b) Analysis of a bin's neighbourhood and of the spatial intensity pattern; no thresholds here. Within 25 km one sub-algorithm replaces the lowest elevation with the next one up. (c) Mostly a neighbourhood test; the near-radar part needs a polar volume.
- **BLOCK (Table 2 only).** (a) Blocked sectors (partial or total beam blockage); also flags ground clutter. (b) No numbers here. (c) Beam geometry plus a digital terrain map.
- **BROAD (Table 2 only).** (a) Not an artefact remover; QI drop with beam broadening. (c) Beam geometry.
- **MHV (Table 2 only).** (a) Underestimation with range (vertical profile). (c) Polar volume.
- **DP.ATT / ATT (Table 2 only).** (a) Attenuation in rain. (c) Dual-pol variables, or along-beam path analysis.
- **Total QI (Sect. 2.2).** Product of the individual QIs, from 0 (bad) to 1 (perfect). Individual QI values are set empirically or by expert judgement.
- **Evaluation metric (Sect. 5, Fig. 13).** Monthly count of exceedances of 1 mm per 10 min per bin; bins with more than 200 per month were attributed to permanent non-precipitation echoes (mountains, cities, RLAN, wind farms).
- **"No echo" coding (Sect. 3.3).** −32 dBZ in the Rainbow system of Leonardo radars.

Not covered: impossible values (no range check is described) and sea clutter.

## Relevance to DECADE

This paper informs H2 (#19), the cleaning of the OPERA ODYSSEY composite for Belgium. It gives a catalogue of artefact types and of the thresholds used by one OPERA member service. It also gives a test we can apply to the composite: a monthly per-pixel count of exceedances of a rain threshold, which shows permanent clutter.

What could run on a 2D composite without polar data:
- The TURBINE idea: accumulate echoes over dry time steps across a long series, threshold per pixel, check by hand. This needs only a long series of 2D fields. The paper does it in polar coordinates per radar and gives no threshold values, so the thresholds would have to come from our own data or from other literature.
- The exceedance count (1 mm / 10 min, more than 200 per month) as a diagnostic map. On a 15 min composite the rate threshold would need rescaling; the paper does not discuss this.
- The QI product approach, to be compared with the QIND field we already have.
- SPECK, as a neighbourhood test, might apply, but this paper gives no parameters.

What cannot run on our composite as written:
- DP.TURBINE and DP.NMET: they need ρHV, ZDR and ΦDP, which the composite does not carry.
- SPIKE: every sub-algorithm works along and across rays in azimuth/range bins, and "discontinuous" uses a second elevation. On a composite, spikes from different radars overlap. Applying it would need re-gridding around each known radar site; the paper does not test this, so it is our assumption, not its result. The thresholds (e.g. 110 bins along at 1 km bins) are tied to POLRAD geometry and would not carry over to 2 km pixels.
- INTERP, NMET, MHV, BLOCK, BROAD, ATT: they need higher elevations, echo height, beam geometry or along-beam paths.

The authors also say analysis of "raw 3-D radar data are still an indispensable element" (Sect. 6). This supports the view that the composite can only be partly cleaned after the fact.

## Limits

- Polish POLRAD network only: 8 C-band Leonardo/Gematronik radars, 3 dual-pol, Rainbow software. Thresholds are tuned to these radars and to local clutter (e.g. Upper Silesia, Warsaw).
- All methods run on single-radar polar volumes at 1° × 1 km and 10 min. Our data are a 2 km, 15 min multi-radar Cartesian composite with no polar or polarimetric data.
- Validation is mostly visual, plus monthly accumulations at a few radars for 2018–2019 (Table 3 covers one radar and one month). There is no gauge-based or long-term skill score, and no study of Belgian radars or of the OPERA composite.
- Several key thresholds are "pre-set" but not stated (wide-spike coverage, spike verification count, TURBINE mask threshold, rainy-bin threshold), and the DP.TURBINE membership functions appear only as a figure.
- Older algorithms (NMET, SPECK, BLOCK, etc.) are only named; their details are in Ośródka et al. (2014), which we have not read here.
- The software is IMGW property and not public (Code availability).
