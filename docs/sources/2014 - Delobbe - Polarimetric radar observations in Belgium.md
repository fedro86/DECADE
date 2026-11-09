# Polarimetric radar observations in Belgium

- **Authors, year, venue:** Laurent Delobbe and Edouard Goudenhoofdt (RMI), 2014. Poster NET.P03, 8th European Conference on Radar in Meteorology and Hydrology (ERAD 2014), Garmisch-Partenkirchen, 1–5 September 2014 (short abstract #063).
- **Link:** poster: [meteo.be PDF](https://meteo.be/uploads/media/60ddc37432cab/poster-delo-goud-erad-2014.pdf); short abstract: [ERAD 2014 ShortAbstracts/063_short.pdf](https://www.pa.op.dlr.de/erad2014/programme/ShortAbstracts/063_short.pdf); programme entry: [ERAD 2014 abstracts page](https://www.pa.op.dlr.de/erad2014/programme/abstracts.html). No extended abstract is listed for #063.
- **Access:** free copy on the RMI website and on the ERAD 2014 (DLR) site; no licence stated.
- **Read:** poster (one page, text and figures, figures inspected visually) plus the short abstract.

## What it is

A one-page poster on the first year of the dual-polarisation C-band radar at Jabbeke (Selex, installed 2012, near the Belgian coast). It checks the quality of the polarimetric data, shows how the Selex Rainbow 5 fuzzy-logic clutter module removes sea and land clutter in a strong anaprop case, and tests a Z–KDP rain-rate relation. The sea clutter part is a qualitative demonstration with one case, not a verification study.

## Numbers we use

- 2012: year the Jabbeke dual-pol radar entered the network (map panel; short abstract says "installed in 2012 ... near the coast").
- 3 C-band Doppler radars in the Belgian network at the time: Jabbeke (RMI, 2-pol, 2012), Wideumont (RMI, 1-pol, 2001), Zaventem (Belgocontrol, 1-pol, 2003); Houthalen-Helchteren (VMM, 2-pol) shown as being installed in 2015 (panel "Operational weather radars in Belgium").
- ~40 km: distance of an offshore wind farm from Jabbeke that shows RHOHV around 0.5 at the 0.3° elevation (panel "Quality assessment", right figure; the photo inset is labelled Thornton Bank in the text layer).
- RHOHV > 0.99: mean RHOHV at short range in rain in all directions except clutter-contaminated sectors (same panel, 1.5° PPI).
- 6: stratiform precipitation episodes used for the quality check, following OPERA (2012) deliverable 2012-03 (same panel).
- 7 input variables of the Rainbow 5 fuzzy-logic clutter classifier, with a discrimination score tested in strong anaprop: Z (−), texture of Z (−), vertical gradient of Z (−), radial velocity Vr (−), texture of ZDR (++), texture of PhiDP (+++), RHOHV (+). Texture = standard deviation along range. The poster states that discrimination comes mainly from the polarimetric variables (panel "Clutter removal using polarimetric data", box "Data types used in the fuzzy logic algorithm").
- Anaprop case shown: 22 July 2013, 22:00 (5-min rain rate, product SRI, 240 km range, 0.5 km/pixel), and 24-h accumulation ending 23 July 2013 06:00 (product PAC), before and after clutter removal (figure labels read from the image). Before filtering the 24-h map shows straight lines of spurious accumulation over the North Sea along shipping lanes towards Rotterdam (arrow "Rotterdam" on the figure); after filtering these mostly disappear.
- ZDR azimuthal variation of 0.2–0.3 dB at 1.5°, 5–20 km, ZH 12–14 dBZ, RHOHV > 0.99, partly due to radome cables (azimuthal ZDR panel; not about clutter).
- R = 33.5 KDP^0.83 if Z > 38 dBZ and KDP > 0.15 °/km, else Z = 200 R^1.6 (rain-rate panel; not about clutter).

## Relevance to DECADE

H2 (#19), sea clutter and anomalous propagation:

- **Upstream removal (RMI):** confirms that Jabbeke raw reflectivity is heavily contaminated by sea clutter over the North Sea, and that offshore wind farms and dense ship traffic produce clutter even without anaprop ("even in non-anaprop conditions"). By the time of the poster (2014) RMI used the Selex Rainbow 5 polarimetric fuzzy-logic filter operationally at the radar, which was installed in 2012. The poster does not say when the filter started, so the first years of Jabbeke data may be unfiltered; nor does it say which fields reach OPERA.
- **Expected residuals on the composite:** fixed points (wind farms, ~40 km offshore) and linear tracks along shipping lanes to Rotterdam and the Scheldt; in anaprop nights (the example is a summer night) widespread speckle over the sea and along the coast. These are the patterns to look for in our 2012–2024 composite over the Belgian coast and sea.
- **Input needed:** the method needs single-radar polarimetric moments (ZDR, PhiDP, RHOHV) and Doppler velocity in polar coordinates. None of these is in the OPERA ODYSSEY maximum-reflectivity composite, so this method cannot be re-run by us; it only tells us what was done upstream.
- **No satellite or composite method** is discussed.

## Limits

- Poster only: one case, no statistics on detection rate or on how much rain was lost; the "+/−" scores are qualitative.
- Applies to Jabbeke only (the only dual-pol radar at the time). Wideumont and Zaventem were single-pol, so their clutter handling is not covered.
- The filter acts on polar volume data at the radar; it does not transfer to a 2 km / 15 min maximum-reflectivity composite, where polarimetric and Doppler information is gone.
- Start date of operational use is not given (the case is July 2013, the poster is September 2014); the early part of our 2012–2024 period may be unfiltered for Jabbeke. To be checked with RMI or OPERA metadata.
