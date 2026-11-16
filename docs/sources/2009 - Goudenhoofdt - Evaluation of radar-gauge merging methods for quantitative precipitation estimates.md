# Evaluation of radar-gauge merging methods for quantitative precipitation estimates

- **Authors, year, venue:** Goudenhoofdt, E., Delobbe, L., 2009. Hydrology and Earth System Sciences 13, 195–203.
- **Link:** [10.5194/hess-13-195-2009](https://doi.org/10.5194/hess-13-195-2009) (the PDF prints only the address www.hydrol-earth-syst-sci.net/13/195/2009/; the DOI follows the journal's standard pattern and was not printed in the text)
- **Access:** open access, CC BY 3.0.
- **Read:** full text; sections 2 (radar and gauges), 3.1–3.7 (methods), 4.1–4.4 (verification, seasonal and range dependence), 5 (gauge density), Table 1.

## What it is

RMI compares eight daily rainfall estimates for Wallonia, using the single-polarisation C-band radar at Wideumont and the SPW telemetric gauges for adjustment. The estimates are the raw radar, five radar–gauge adjustments or merges of increasing complexity, and gauge-only ordinary kriging. They are verified over 2005–2008 against an independent network of manual RMI climatological gauges. The paper also tests seasonal and range dependence, and how each method degrades when gauges are removed.

## Numbers we use

- **Radar processing:** section 2. Wideumont radar at 592 m, 5 elevations every 5 min, Doppler and static clutter filtering. A pseudo-CAPPI at 1500 m on a 600 m × 600 m grid, Z = 200R^1.6, 24 h sums from 08:00 local time.
- **Adjustment network:** section 2. 90 SPW telemetric gauges (one per 135 km²), mostly hourly tipping buckets, reduced to 74 within the 120 km maximum range.
- **Verification network:** sections 2 and 4.1. 270 manual RMI stations (daily, 08–08 LT, available late, strictly quality-controlled). This becomes 110 after removing stations with gaps, then 75 after removing those within 2 km of an SPW gauge. The test covers 612 valid days in 2005–2008.
- **Pairing rules:** section 3. The radar value at a gauge is the mean of the 9 pixels around it. A pair is valid only if both radar and gauge exceed 1 mm, and a day is valid only with at least 10 valid pairs. The scores use pairs above 1 mm for all methods (section 4.1).
- **Methods:** section 3.
  - **MFB (Eq. 1):** one daily factor, the sum of gauges over the sum of radar.
  - **RDA (Eq. 2):** a range-dependent factor; log(R/G) is fitted as a second-order polynomial of range (BALTEX method).
  - **SRD (section 3.3, Fig. 3):** a *static local bias* correction followed by RDA. Daily radar sums are first MFB-corrected. The residual bias at each climatological gauge is then averaged over one year and kriged into a field. The field from one year is applied to the next year to mimic operations. The fields for 2004–2007 are "very similar", and the 2005 field spans about ±2 dB.
  - **BRA (Eqs. 3–4):** Brandes adjustment, i.e. Barnes interpolation of gauge/radar ratios, with a smoothing parameter tied to the gauge density.
  - **KRI (Eq. 5):** ordinary kriging of gauges only, with the 20 nearest gauges and a linear isotropic variogram. More complex variograms gave no gain.
  - **KRE:** kriging with radar-based error correction ("conditional merging").
  - **KED (Eq. 6):** kriging with external drift, with radar as the drift and a linear variogram; the most expensive method.
- **Scores (MAE and scatter, 2005–2008):** Table 1 and Figs. 5–7. The pdftotext layout of the table is scrambled; the values below follow the column order and agree with the ratios in section 4.2.

  | | ORI | MFB | RDA | SRD | BRA | KRI | KRE | KED |
  |---|---|---|---|---|---|---|---|---|
  | MAE (mm) | 2.410 | 1.812 | 1.735 | 1.652 | 1.592 | 1.685 | 1.517 | 1.485 |
  | Scatter (dB) | 2.236 | 1.520 | 1.480 | 1.378 | 1.240 | 1.380 | 1.209 | 1.186 |

- **Error reduction:** section 4.2. MFB cuts the MAE by about 25 % and KED by almost 40 % compared with the raw radar. RDA adds a little to MFB, and SRD a little more. The methods with a daily spatial correction from radar and gauges (BRA, KRE, KED) do clearly better on scatter. The ranking is the same in each of the four years (Fig. 4).
- **Raw radar bias:** section 4.2, Fig. 6. The raw radar has a mean bias of −1.2 dB (radar/gauge total, i.e. about 24 % too little rain). Table 1 lists −0.998 dB for ORI on the common pair set. After any adjustment, the mean bias stays within about ±0.15 dB (Table 1). MFB removes the overall bias but not the spread.
- **Seasonal dependence:** section 4.3, Fig. 8 (MAE per month divided by the raw-radar MAE). In summer, gauge-only kriging is worse than plain MFB. In winter it is nearly as good as KED. KED is the best method in every month. The radar adds most when convection dominates (summer) and little in widespread stratiform rain (winter).
- **Range dependence:** section 4.4, Fig. 9 (six 20 km bins up to 120 km). The radar adds little below 20 km (bright band) and above 100 km. RDA beats MFB only beyond 80 km, and KED is best at every range. The seasonal variation of the range effect was not robust from year to year.
- **Gauge density:** section 5, Figs. 10–11. Gauges are removed one at a time, each time dropping the one with the largest sum of inverse distances to its 4 nearest neighbours, from 74 gauges (one per 135 km²) down to 20 (one per 500 km²). MFB is hardly sensitive to density. KRI is the most sensitive, and BRA, KRE and KED are moderately sensitive. KED stays best at all densities. At one gauge per 500 km², SRD (static local bias + RDA) is as good as KRE and KED (section 5.2; section 6).

## Relevance to DECADE

H3 (#20), calibration across the ODYSSEY → CIRRUS change.

- **The national bridge is a KED merge.** RADCLIM merges radar and gauges by kriging with external drift (`2023 - RMI - RADCLIM user guide.md`). This paper is the RMI evaluation behind that choice: KED was the best of eight methods in every season, at every range and at every gauge density. That supports RADCLIM as the most accurate national reference for the bridge.
- **What the bridge is made of changes with the season.** In winter, gauge-only kriging is almost as good as KED, so a KED field then leans on gauges; in summer it leans on the radar pattern. A bridge built on RADCLIM is therefore more gauge-like in winter and more radar-like in summer. This is one more reason to calibrate per season rather than with one annual factor.
- **Climatological spatial factor, computed beforehand.** SRD is the closest precedent in Belgium to what our real-time chain can use. It is a spatial correction field estimated from one year of gauges and applied unchanged the following year. The fields were stable over 2004–2007, and with sparse gauges SRD matched KED. MFB, BRA, KRE and KED all need same-day gauges and cannot run in our chain; SRD-type and RDA-type fields can.
- **Range and bright band.** The radar–gauge error depends on range, with poor estimates below 20 km and beyond 100 km. A spatially uniform seasonal factor between ODYSSEY and CIRRUS will not capture such structure if the two composites weight the radars differently.
- **Wet threshold.** The 1 mm threshold on both radar and gauge (daily) is a precedent for excluding near-dry values before computing ratios. It is a daily value and does not transfer as such to 15 min rates.

## Limits

- Single radar (Wideumont), 2005–2008, daily accumulations only, Wallonia, up to 120 km. It is not RADCLIM (four radars, about 150 gauges, kriging of hourly sums every 5 min) and not a composite.
- Verification is at gauge points only. Its sensitivity to sub-daily intensities and to extremes is unknown.
- The raw-radar bias (−1.0 to −1.2 dB) is that of one radar in 2005–2008. It is a radar-against-ground bias, not the ODYSSEY–CIRRUS difference.
- The kriging choices (20 nearest gauges, linear variogram) and the Brandes smoothing tuned on 2006 are specific to this network.
- Table 1 had to be read from a scrambled text layout; the MAE and scatter values were checked against the percentages in section 4.2, the mean-bias column only against the qualitative text.
