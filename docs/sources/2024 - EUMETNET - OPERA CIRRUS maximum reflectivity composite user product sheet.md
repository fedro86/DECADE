# OPERA CIRRUS maximum reflectivity composite (1 km; 5 min), user product sheet

- **Authors, year, venue:** EUMETNET OPERA, production centre Météo-France;
  product sheet version 2.0, 25/6/2024
- **Link:** https://eumetnet.eu/wp-content/uploads/2024/06/OPERA_Max-Reflectivity_Product-Sheet_Ed-2.0.pdf
- **Access:** open (no licence stated)
- **Read:** full text (3 pages)

## What it is

The user description of the CIRRUS maximum reflectivity composite: pan-European,
1 km, every 5 min, made at Météo-France with BALTRAD pre-processing and an
updated version of the ODYSSEY compositing software, in ODIM HDF5 2.4.

## Numbers we use

- **Compositing rule:** the value of a pixel is the maximum of all contributing
  single-scan reflectivity pixels (page 3, *Production method*).
- **Time window:** (NT − 10 min, NT], updated every 5 min, 288 times a day
  (page 2, section 4, where it is written [NT − 10 min, NT]; the files declare
  a start at NT − 9:59, `docs/data.md`, *Time windows for the label NT*).
- **Grid:** 4400 × 3800 pixels at 1 km (page 2, section 4).
- **Spain:** Spanish data come every 10 min and are extrapolated forward with
  Lucas–Kanade to 5 min (page 2, section 3).
- **Pre-processing** (anomaly removal, occurrence filtering, beam-blockage
  correction, satellite filter) is chosen by each national producer and not
  applied to all radars (page 2, section 3; page 3); a threshold of 0.12619 dBZ
  (0.01 mm/h) is suggested against noise (page 3).
- Only C- and S-band radars enter the product (page 3).

## Relevance to DECADE

Source for the compositing rule when comparing degradations of CIRRUS with
ODYSSEY (H1, `docs/method.md`, *Degraded CIRRUS as a stand-in for ODYSSEY*): a
column maximum over radars and scans is closer to the `max` degradation than to
`zmean`. Also confirms the CIRRUS time window and the Spanish extrapolation.

## Limits

It describes CIRRUS, not the 2 km ODYSSEY legacy product; for ODYSSEY it only
says that CIRRUS uses an updated version of the ODYSSEY software. It does not
say how overlapping radars are weighted beyond taking the maximum, nor which
radar gives the value of a pixel.
