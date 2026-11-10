# Quality control of gridded national radar reflectivity data

- **Authors, year, venue:** Charba, J. P., Liang, F., 2005. AMS conference preprint, paper 6A.5. The paper does not print the conference name; the file name says "AMS2005".
- **Link:** [vlab.noaa.gov PDF](https://vlab.noaa.gov/documents/6609493/36173392/LAMP_radqc_paper_AMS2005_final.pdf)
- **Access:** free copy on NOAA VLab; no licence stated.
- **Read:** full text; sections 2 (data, Table 1), 3.1–3.3 (false echoes, Table 3), 4.1 (decision-tree QC, Table 4).

## What it is

NOAA/MDL quality control of two US national reflectivity mosaics used for the LAMP thunderstorm guidance:

- the WSI 2 km mosaic, aggregated to 10 km boxes by taking the highest value;
- the RCM 10 km mosaic, whose top category is ≥ 55 dBZ.

The authors find intense false echoes (radar test patterns, sudden jumps that look like anomalous propagation (AP), and single-box spikes), mostly at ≥ 75 dBZ in WSI. They correct them with a decision tree that tests lightning together with spatial and temporal continuity.

## Numbers we use

- **≥ 75 dBZ:** the top WSI category (category 15, Table 1). It was the search key for false-echo cases (section 3.2).
- **1,270 cases ≥ 75 dBZ, i.e. 0.0005 % of the ≥ 5 dBZ cases:** Table 3, WSI, warm seasons 1997–2001, nominal time :30. By comparison, 70–74 dBZ has 2,731 cases (0.0012 %).
- **Lightning relative frequency:** Fig. 2 and section 3.1. It rises with reflectivity up to 64 dBZ and then drops steeply, which suggests the highest values are often not precipitation.
- **Decision tree, Table 4(a), for WSI:**
  - ≥ 75 dBZ test pattern with no lightning: set to missing.
  - ≥ 75 dBZ single-box spike with no lightning: set to 0.
  - ≥ 75 dBZ echo with intense lightning: no change.
  - ≥ 65 dBZ echo with lightning: no change, or lowered slightly according to lightning intensity.
  - ≥ 50 dBZ with no lightning: lowered or removed according to spatial and temporal continuity.
- **50 dBZ:** the lower limit of all the checks (section 4.1). The ≥ 50 dBZ values checked were 0.29 % of warm-season samples, and 5.5 % of them (WSI) were changed.

## Relevance to DECADE

H2 (#19), impossible values. This is the NOAA source behind the "≥ 75 dBZ without lightning" lead, now checked against the text. It shows that a national 2D mosaic built by taking maxima contains spikes and test patterns at ≥ 75 dBZ. It supports treating ≥ 75 dBZ as suspect, but only together with a context test, not as an unconditional discard.

## Limits

- 75 dBZ is a category boundary of the WSI product, not a tuned threshold. Echoes ≥ 75 dBZ that come with intense lightning are kept on purpose.
- The products are a US commercial (WSI) mosaic and a categorical RCM grid at 10 km, from S-band WSR-88D radars. This is not ODIM/OPERA C-band, and the values are categorical rather than continuous dBZ.
- The rule needs lightning data. Without them, the paper gives no unconditional upper cut-off.
