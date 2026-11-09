# Recent improvements to the quality control of radar data for the OPERA data centre

- **Authors, year, venue:** Scovell, R., Gaussiat, N., Mittermaier, M., 2013. AMS Conference on Radar Meteorology, poster P361. The PDF is dated September 2013, which points to the 36th conference; the confex URL path says "34Radar".
- **Link:** [ams.confex.com PDF](https://ams.confex.com/ams/34Radar/webprogram/Manuscript/Paper155995/OPERA_QC_v1.pdf)
- **Access:** free conference manuscript; no licence stated.
- **Read:** full text, sections 1–5.
- **Supporting documents (not summarised separately):**
  - OPERA CIRRUS product sheet, Ed. 2.0 (2024): summary `2024 - EUMETNET - OPERA CIRRUS maximum reflectivity composite user product sheet.md`.
  - "Configuration of CIRRUS relative to ODYSSEY" (2024): summary `2024 - Radojevic - Maximum Reflectivity Composite Configuration of CIRRUS relative to ODYSSEY.md`.
  - Haase and Johnson, OPERA OD12 "Quality of composites" (2018), [eumetnet.eu](https://www.eumetnet.eu/wp-content/uploads/2019/01/Quality_of_composites_OPERA.pdf).

## What it is

The paper describes the quality control (QC) that the ODYSSEY (OPERA Data Centre) production line applies to each plan position indicator (PPI) scan before making the 2 km / 15 min composites. The DBZH product is the column maximum reflectivity. There are two QC steps:

- a climatological clutter filter based on monthly echo counts, introduced in 2011;
- three of the BALTRAD bRopo anomaly filters (SPECK, EMITTER, SHIP), in operation since March 2013.

## Numbers we use

- **Clutter filter:** a bin is rejected when its normalised monthly echo count exceeds a threshold (section 2). The first setting was 90 %, and 60 % was adopted as the first guess for the whole network. The UK gauge trial gave Peirce skill scores of 0.51 at 100 %, 0.59 at 90 % and 0.60 at 60 % (Table 3).
- **bRopo filters:** SPECK, EMITTER and SHIP are used (section 3). Above 2.0° elevation only SPECK runs. Each filter is set with a *minimum* dBZ and a size or shape, and none of them uses a maximum dBZ.
- **Wind-farm echoes:** these were "by choice" not removed from the PPIs received by ODYSSEY (section 4).
- **ODYSSEY vs CIRRUS (supporting sheet):** ODYSSEY pre-processes with BALTRAD 2013 (rave, bropo, beamb) plus a satellite filter (2018 version). Pre-processing is not applied to all incoming radars, and the composite pixel is the maximum over all contributing polar bins.
- **CIRRUS product sheet:** the only threshold it recommends to users is a *lower* one, 0.12619 dBZ (≈ 0.01 mm/h), to remove noise. It states no upper valid limit.

## Relevance to DECADE

H2 (#19), impossible values. None of the documented ODYSSEY QC steps tests for implausibly high reflectivity. A single bad bin from any one radar therefore passes straight into the maximum composite. This explains why values of 100 dBZ or more survive in our data, and it means the upper discard has to be added by us after the fact. No OPERA document found gives an upper valid limit for DBZH.

## Limits

- This is a 2013 snapshot of ODYSSEY QC. Later changes (for example the satellite filter, BALTRAD 2013 beamb) are known only from the 2024 configuration sheet.
- National producers may apply their own QC before sending data, and the paper does not describe it.
- The paper says nothing about how DBZH is encoded (gain, offset, maximum representable value). That has to be read from the ODIM `what` attributes of our files.
