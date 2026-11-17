# Description of differences between NIMBUS and ODYSSEY composite production

- **Authors, year, venue:** L. Bouilloud, G. Haase, M. Koutek, B. Lankamp,
  H. Leijnse, A. von Lerber, V. Meyer, M. Radojevic, K. Stephan, EUMETNET OPERA
  note "NIMBUS vs. ODYSSEY", version 1.0, 13/06/2024
- **Link:** [eumetnet.eu](https://www.eumetnet.eu/wp-content/uploads/2024/06/NIMBUS_composite_vs_ODYSSEY_1.0_19062024.pdf)
- **Access:** open (no licence stated)
- **Read:** full text (8 pages)

## What it is

A comparison of the ODYSSEY rain-rate and accumulation composites (2 km,
15 min, 01/2011–06/2024) with their NIMBUS successors, including the
configuration tables and the central QC filters. It is the most detailed
description of the ODYSSEY filters found.

## Numbers we use

- **Which filters, for which radar** (section 8, page 5): ODYSSEY applies the
  BALTRAD toolbox modules `hac`, `bropo`, `beamb`, `satfilter` and `qi-total`;
  each data provider chooses which of them are applied to its radars.
- **Configuration** (section 5, page 2): the ODYSSEY configuration tables were
  last updated in December 2022; several countries have since asked that some
  filters no longer be applied to their data (in NIMBUS, not in ODYSSEY).
- **Software** (Table 1, page 3): ODYSSEY pre-processing is BALTRAD version
  2013 (rave, bropo, beamb) plus satellite filter version 2018; maintained by
  Météo-France only after 2019.
- **Hit-accumulation filter** (section 8, page 6): monthly normalised echo count,
  threshold typically 0.6; a hit is any pixel that is not undetect or nodata;
  hit-accumulation files older than 63 days are erased; if the scan geometry
  (bins or rays) does not match the file, the scan is not filtered and the radar
  is not composited until the file is erased. It gives no quality index.
- **Satellite filter** (section 8, page 6): NWC SAF Precipitating Clouds,
  maximum over the 49 surrounding satellite pixels; **if the probability of
  precipitation is 0–5 %** the reflectivity is set to undetect (Saltikoff et
  al. 2019 say 0). The PC quality index is not used in the ODYSSEY filtering.
- **Beam blockage** (section 8, page 6): GTOPO30, partial blockage up to 70 %
  corrected, above 70 % set to nodata.
- **Time window** (section 3, page 2): ODYSSEY uses data valid between −10 and
  +5 min of the composite time, never older than 18 min.

## Relevance to DECADE

PR #96: the filters are per radar and chosen by the provider, so the QC
history of the Belgian radars cannot be read from the OPERA-wide dates alone.
The "2018" of the satellite filter is a version label in a 2024 software table,
not a start date.

## Limits

Written for the rain-rate products, but the pre-processing is shared with the
maximum reflectivity composite (Radojevic 2024, Table 3). It gives no dates for
when each filter or version entered production, and no per-radar filter list.
