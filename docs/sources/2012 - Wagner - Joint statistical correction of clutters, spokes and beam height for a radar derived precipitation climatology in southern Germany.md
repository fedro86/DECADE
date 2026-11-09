# Joint statistical correction of clutters, spokes and beam height for a radar derived precipitation climatology in southern Germany

- **Authors, year, venue:** A. Wagner, J. Seltmann, H. Kunstmann, 2012, *Hydrology and Earth System Sciences* 16, 4101–4117
- **Link:** [10.5194/hess-16-4101-2012](https://doi.org/10.5194/hess-16-4101-2012)
- **Access:** open, CC BY 3.0
- **Read:** full text

## What it is

The paper builds a statistical post-correction for a radar climatology of the single DWD C-band radar at Munich (100 km radius), using seven years (2000–2006) of 5-min near-surface scans. All corrections work on per-pixel frequency-of-occurrence maps of six reflectivity classes (PX product, 1 × 1 km), not on single images. Three modules follow: an altitude (beam-height) correction, a correction of clutter and spokes, and a mean adjustment to rain gauges. Validation uses annual rain totals at gauges (2004–2006 calibration, 2007–2009 validation).

## Numbers we use

- **Basic input statistic (Sect. 3, p. 4103; Table 1, p. 4104):** for every pixel, count how often each reflectivity class occurs over the archive. PX classes: 7 dBZ (1 dBZ in winter) to 18.9, 19–27.9, 28–36.9, 37–45.9, 46–54.9, ≥ 55 dBZ. About 2.4 × 10^10 pixel measurements in 7 years (Sect. 2). Core assumption: averaged over many years, frequencies at the same height should be about equal, so abrupt spatial jumps mean errors (Sect. 3).
- **Fixed clutter ("city clutter" and "mountain clutter"), detection (Sect. 3, p. 4104; Sect. 5.2, p. 4111):** artefact = clutter remnants (too many echoes) and filter "holes" (too few echoes, from clutter suppression in the signal processor, Sect. 4.2.2). Steps: an area around each clutter source is drawn by hand once; inside it, frequency thresholds flag the obvious bad pixels; a 2 km buffer is added around them; the rest are checked with a histogram, and the 95 % interval of the empirical frequency distribution marks the clean pixels. The threshold values are not given as numbers. Sect. 3 says the classification for all classes uses class 1; Sect. 5.2 says separation is done per class, with the class 4 mask reused for classes 5–6. This is not fully consistent in the paper. Input: long series of frequency maps (one 2D map per class), plus manual work.
- **Fixed clutter, correction (Sect. 5.2, p. 4111):** flagged pixels are replaced by interpolation from the frequencies of clean pixels in the surroundings (10 to 20 km). The interpolation method is not specified further. Effects differ by class: city clutter mainly lowers class 1 frequencies; mountain clutter lowers class 1 and raises class 5 (Figs. 7–8, Sect. 4.2). Input: long-series frequency maps only (no polar geometry).
- **Blocked sectors (beam blockage / shading spokes), detection (Sect. 3, p. 4104):** pixels are grouped by 1° azimuth from the radar. For each azimuth, the median frequency of all pixels (clutter pixels excluded) is computed; thresholds flag obvious spokes; a change of more than 10 % between medians of adjacent azimuths marks a spoke edge, checked visually. Ten spokes found (Fig. 2, Fig. 9). Input: long-series frequency maps plus radar position (to compute azimuth).
- **Blocked sectors, correction (Sect. 5.2, pp. 4111–4112):** spoke pixels keep their pattern and are scaled by one factor per azimuth and class: median of clean pixels in the adjacent 20–30 azimuths divided by the spoke median. Factors range 1.1–1.5. Blockage reduces class 2–4 frequencies more than class 1 (Sect. 4.2.3). Input: as above. The authors note the spoke correction had to be updated after the 2006 change of elevation angles (Sect. 3, p. 4105).
- **Echoes without rain (aircraft):** spoke #10 (east-north-east) shows more echoes, not fewer; the cause is aircraft near Munich airport (Sect. 4.2.3, p. 4109). The two aircraft spokes east of the radar are fully interpolated, not scaled (Sect. 5.2, p. 4112). Input: long-series frequency maps plus azimuth.
- **Interference spikes (RLAN/5 GHz):** not treated. The paper only mentions that single images can show positive spokes from jamming transmitters or the sun (Sect. 4.2.3), and says that in a climatology most spokes come from beam blockage.
- **Impossible values, isolated echoes (speckle):** not treated by the paper's scheme. Noise thresholding and a speckle remover are applied earlier, inside the signal processor (Sect. 1, p. 4102).
- **Beam height / range effect (module 1, Sect. 4.1 and 5.1, pp. 4105–4110, Eqs. 1–5):** not one of our artefact names; it removes the drop of echo frequency with beam height. Above 1 km, frequency falls by 12.9 % per km for class 1 and 20.3 % per km for classes 2–5 (Sect. 4.1, Sect. 7). Correction: Y0 = Y (h · fcor + 1) (Eq. 5), with fcor = −0.203 (moderate/heavy) and −0.129 (light). Heights binned in 100 m classes; six beam-elevation classes (0.8° to 2.1°). Behaviour below 1 km is ignored. The shape varies by month because of the bright band (Figs. 5–6). It inflates frequencies, so it must be followed by module 3 (Sect. 5.1, 6.1). Input: beam height per pixel (radar position, elevation per azimuth, polar geometry) plus long-series frequency maps.
- **Gauge adjustment (module 3, Sect. 5.3, p. 4112):** one mean factor from annual totals at 33 gauges 30–60 km from the radar (3 × 3 pixel value), DX product, three-part Z/R (Table 2: a = 125/200/77, b = 1.4/1.6/1.9 for < 36.5, 36.5–44, > 44 dBZ). Factor 0.94 (uncorrected) and 1.26 (corrected). A locally varying factor was rejected because it would distort the rain pattern. Input: rain gauges.
- **Overall effect (Table 3, p. 4114; Table 4, p. 4115):** RMSE of annual totals vs. gauges falls from 262 mm to 118 mm (76 gauges, 2004–2006) and from 322 mm to 174 mm (91 gauges, 2007–2009). Within each 20 km range class, the median radar-gauge difference goes from −40 % to +2 % before to −5 % to +5 % after (Sect. 6.1).
- **Stability rule (Sect. 3, p. 4105):** corrections can be transferred between periods only if calibration or scan strategy did not change, or the change is analysed with at least one year of data.

## Relevance to DECADE

This informs H2 (#19), the cleaning of the OPERA composite archive. The main idea transfers directly: build per-pixel frequency-of-occurrence maps per reflectivity class over many years and treat abrupt spatial anomalies as artefacts.

Steps that could run on our long 2D composite archive (accumulation/frequency maps only):
- fixed clutter detection (thresholds, 2 km buffer, 95 % interval of the frequency distribution) and replacement by interpolation from clean pixels 10–20 km around;
- the per-class view, which separates clutter remnants (excess) from suppression holes (deficit).

Steps that need more than the composite:
- spoke detection and scaling need the radar position to compute azimuth. Positions are known, so this is possible on the composite. But overlapping radars may hide or mix spokes; the paper does not cover this case (one radar only);
- the beam-height correction needs beam height per pixel, so it needs single-radar polar geometry and scan elevations. The composite does not carry this. Whether QIND could be a proxy is our open question, not something the paper says;
- the gauge adjustment needs rain gauges and concerns rainfall bias, not artefact masking.

The stability rule means we should compute frequency maps in time blocks and recompute after known radar or scan changes in 2012–2024.

## Limits

- One radar (Munich, DWD C-band), 100 km radius, Alpine terrain with terrain-following elevations. Not a multi-radar composite.
- Period 2000–2006 for the analysis, 2004–2009 for gauge checks. Hardware (2004) and scan (2006) changes affected the results.
- Product: PX with only six classes at 1 × 1 km and 5 min; DX at 1° × 1 km. Our data are a 2 km / 15 min composite with a QIND field; class limits and resolution differ.
- Method made for climatologies of one year or longer. The authors say modules 2 and 3 might also suit shorter scales, but they do not test this.
- Several steps are manual (drawing clutter areas, visual spoke check). Frequency thresholds are not given as numbers, so they cannot be copied.
- No step for RLAN interference, speckle, impossible values, or non-rain echoes other than aircraft spokes. No bright-band correction per image.
- Validation is only on annual totals at gauges, not on artefact detection skill.
