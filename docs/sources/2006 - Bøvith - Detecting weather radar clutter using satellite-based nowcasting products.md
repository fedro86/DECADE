# Detecting weather radar clutter using satellite-based nowcasting products

- **Authors, year, venue:** T. Bøvith (DMI and DTU-IMM), R. S. Gill (DMI), S. Overgaard (DMI), L. K. Hansen (DTU), A. A. Nielsen (DTU), 2006. Proceedings of the Fourth European Conference on Radar in Meteorology and Hydrology (ERAD 2006), Barcelona, 18–22 September 2006, pp. 153–156.
- **Link:** author copy: [DTU IMM pubdb imm4661.pdf](https://www2.imm.dtu.dk/pubdb/edoc/imm4661.pdf); record: [pubdb 4661](https://www2.imm.dtu.dk/pubdb/pubs/4661-full.html). Also indexed on CORE (core.ac.uk/download/13700643.pdf), which refused automated download. No DOI.
- **Access:** free author copy on the DTU repository; no licence stated.
- **Read:** full text (4 pages); the figure (radar, IR, PC and classification maps for three cases) from its caption only.
- **Identification note:** the URL given by the reviewer (copernicus.org/erad/online/erad-312.pdf) is Peura (2002, FMI), already read. This ERAD 2006 paper is the only DMI paper at an ERAD we found that uses the NWC SAF "Precipitating Clouds" product for clutter detection, so we take it to be the intended lead. A companion paper with the same authors uses the same data plus NWP temperature: Bøvith et al. (2006), "Detecting Weather Radar Clutter by Information Fusion With Satellite Images and Numerical Weather Prediction Model Output", IGARSS 2006, Denver, pp. 511–514 (free copy: [imm4482.pdf](https://www2.imm.dtu.dk/pubdb/edoc/imm4482.pdf), not downloaded or read here). The method was later extended in Bøvith's 2008 DTU PhD thesis "Detection of Weather Radar Clutter" (not read).

## What it is

A short conference paper from DMI and DTU showing first results of clutter detection on the DMI radar mosaic by fusing it, pixel by pixel, with the NWC SAF Precipitating Clouds (PC) product from Meteosat-8, then classifying echoes as clutter or rain with a supervised scale-space ensemble classifier trained on samples chosen by a radar expert. Three cases are shown: anaprop clutter without rain, clutter with rain, rain without clutter.

## Numbers we use

- 3 of DMI's 4 radars used: Sindal, Rømø, Stevns, all C-band Doppler (Sect. 2.1).
- Radar input = composite: volumes reduced to 2-D with a DMI in-house algorithm and mosaicked; 1 km grid, 10 min (Sect. 2.1).
- PC product: probabilities for 3 classes (heavy, light-to-moderate, no precipitation) per Meteosat-8 pixel, from a linear combination of SEVIRI bands plus NWP surface temperature (NWCSAF/PGE04); 3 km at nadir, about 5 km at Scandinavian latitudes, every 15 min (Sect. 2.2).
- Fusion: both data sets resampled to a 1 km stereographic grid; nearest satellite slot in time, so at most 5 min mismatch, i.e. about 3 km (3 pixels) displacement for clouds moving at 10 m/s (Sect. 3.1).
- Gaussian smoothing of inputs at several scales (scale-space) reduces the effect of misalignment (Sect. 3.2).
- Classification error / total error (Table 1): Case I (sea + land clutter, no rain, 2006-05-05 20:10 UTC) 0.00 % / 0.00 %; Case II (sea clutter + rain, 2005-09-25 20:00 UTC) 1.37 % / 8.01 %; Case III (convective rain, no clutter, 2006-05-19 10:40 UTC) 0.94 % / 3.26 %. "Classification error" is on held-out training samples; "total error" uses all pixels of the scene (Sect. 4).
- Case I: anaprop lasted more than a week from about 5 May 2006 under high pressure; pronounced sea clutter over much of the Baltic Sea and moderate sea clutter over the North Sea (Sect. 4, Case I).

## Relevance to DECADE

H2 (#19), sea clutter and anomalous propagation:

- **Works on a composite:** unlike the RMI and KNMI methods, this one is applied to a 2-D radar mosaic, not to polar volumes. The only inputs are the mosaic reflectivity and a collocated satellite product, so it is in principle transferable to the OPERA ODYSSEY composite over Belgium and the North Sea.
- **Physics of the problem:** the authors note that Doppler filtering handles stationary land clutter but sea clutter and moving targets are hard to detect with single-pol data alone (Sect. 1), which agrees with KNMI TR-355. They report anaprop as frequent in Denmark in spring, summer and autumn, linked to warm moist air over a colder sea (Sect. 4, Case I); a similar mechanism is plausible over the southern North Sea, but the paper does not study it.
- **Strength:** widespread sea clutter in clear-sky anaprop is detected with high accuracy when no rain is nearby (Case I, zero error).
- **Weakness:** the PC product overestimates precipitating cloud, so clutter under or near clouds is labelled rain; rain at the edges of fronts can be labelled clutter; rain in areas of low PC probability (central Jutland, Case III) was labelled clutter (Sect. 4, 5). The authors sum it up as detecting clutter well "at the expense of some misclassification of precipitation" (Sect. 5).
- **Input needed:** radar composite; NWC SAF PC (or another Meteosat precipitation/cloud product) at 15 min; training samples labelled by an expert; reprojection to a common grid.

## Limits

- Only 3 hand-picked cases, errors measured on expert-chosen samples; no long-term statistics and no estimate of rain lost over a season.
- Supervised classifier trained per case; the paper does not give a ready-to-use rule or thresholds, nor details of the ensemble models.
- Danish radars and Baltic/North Sea around Denmark; nothing on Belgium or Jabbeke.
- Meteosat-8 PC product of 2005–2006; the NWC SAF product family has changed since (later versions and newer satellites), so a 2012–2024 reprocessing would need the PC (or successor) archive for the whole period, which this paper does not address.
- The satellite product is derived from cloud-top radiation while the radar sees the precipitation itself, so the two fields do not match even when perfectly aligned in time (Sect. 3.1).
- Our composite is a 15-min maximum-reflectivity product at 2 km; the 5-min/3-km mismatch figure would need to be recomputed for our time steps.
