# Radar-based assessment of hail frequency in Europe

- **Authors, year, venue:** Fluck, E., Kunz, M., Geissbuehler, P., Ritz, S. P., 2021. Natural Hazards and Earth System Sciences 21, 683–701.
- **Link:** [10.5194/nhess-21-683-2021](https://doi.org/10.5194/nhess-21-683-2021)
- **Access:** open access, CC BY 4.0.
- **Read:** full text; sections 2.1.1–2.1.4 (data), 3.1 (correction of erroneous signals), 3.2 (lightning filter), 3.3 / Table 1 (tracking thresholds).

## What it is

A 10-year (2005–2014) hail-track climatology for Germany, France, Belgium and Luxembourg. It is built from 2D national reflectivity composites at 1 km and 5 min: the Météo-France mosaic (which also covers a large part of Belgium) and the DWD RX composite, which takes the maximum of the lowest elevations. Before tracking cells, the authors clean the composites with a fixed value window, a neighbour-difference filter, a single-scan spike test and a lightning filter.

## Numbers we use

- **> 70 dBZ set to missing:** section 3.1 (p. 687). The authors say the remaining errors are mostly single pixels much stronger than their surroundings, "e.g. more than 70 dBZ". To avoid this problem they set to missing every reflectivity above 70 dBZ, and also every value below 35 dBZ. This is a plain discard: the pixels are removed, not capped.
- **Z > 45 dBZ and ΔZ > 5 dBZ to the neighbours:** section 3.1, Eq. (1). The pixel is replaced by the mean of its 8 neighbours. This step follows Puskeiler et al. (2016).
- **Spike test:** section 3.1 (pp. 687–688). If a pixel is at least twice its 8 neighbours and is absent in the scans just before and after, it is called an artifact and set to zero.
- **≥ 55 dBZ with no lightning within 10 km in 24 h:** section 3.2. The pixel is set to zero. Distances of 5, 15 and 20 km were also tested.
- **55 dBZ:** Table 1. This is the minimum reflectivity of a reflectivity core, i.e. the hail criterion (Mason 1971). It is a detection threshold, not a QC threshold.
- **0.5–1 dBZ:** section 2.1.3. The French mosaic reads lower than the DWD composite in the border region (personal communication cited in the paper).

## Relevance to DECADE

H2 (#19), impossible values: this is the closest analogue we have. A peer-reviewed study cleans 2D, 1 km / 5 min maximum-type reflectivity composites over an area that includes Belgium, and it discards values above 70 dBZ. It supports a discard threshold of 70 dBZ for a 2D composite. It also shows the threshold used together with spatial and temporal spike tests and a lightning check, kept separate from any rain-rate cap.

## Limits

- The 70 dBZ value is stated without any justification or sensitivity test. The paper gives no physical argument and no count of the pixels removed.
- The lower bound (35 dBZ) and the 55 dBZ lightning rule are specific to hail tracking and must not be carried over to rainfall.
- The input data are national composites (Météo-France, DWD), not the OPERA ODYSSEY 2 km / 15 min product, and the period is 2005–2014.
- Because a hail study wants the strongest real echoes, 70 dBZ is meant as a conservative ceiling for genuine hail cores. That is a different goal from rain estimation.
