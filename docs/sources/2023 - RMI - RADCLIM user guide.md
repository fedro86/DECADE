# RADCLIM User Guide

- **Authors, year, venue:** Royal Meteorological Institute of Belgium (RMI), last
  edited by E. Goudenhoofdt; version 2, web page printed to PDF on 13/4/2023
  (date of the PDF; the page itself carries no date)
- **Link:** https://opendata.meteo.be/cases/202107/radclim_userguide.pdf
- **Access:** open (no licence stated in the guide; the dataset record gives
  CC BY 4.0, `docs/data.md`)
- **Read:** full text (3 pages)

## What it is

The user description of RADCLIM: radar precipitation for Belgium and its
surroundings from four radars, quality-controlled and merged every 5 min with
about 150 automatic rain gauges by kriging with external drift. 1 km grid in
Belgian Lambert 2008, UTC.

## Numbers we use

- **Radars:** Wideumont (RMI, since 2001), Avesnois (Météo-France, since 2005),
  Jabbeke (RMI, since 2013), Helchteren (VMM, 2016); Wideumont dual-pol since
  2022 (*Weather radar measurements*).
- **Gauges:** 91 SPW, 42 VMM, 19 WL, weighing gauges at 5 min (*Rain gauge
  measurements*).
- **Compositing:** maximum of the 3 closest radars within 180 km; the text
  continues "For other months" with a distance-weighted composite, so a
  seasonal condition is missing from the sentence (*Compositing, accumulation
  and radar-gauge merging*, item 1).
- **Accumulations:** 5 min and 1 h, made from the 5 min rain rates with
  optical flow; kriging is done on the 1 h accumulation every 5 min and its
  correction factor applied to the 5 min accumulation (items 2–4).
- **Time:** "the timestamp corresponds to the end of the accumulation period"
  (*Temporal resolution*).
- **Grid:** 1 km, each value the mean precipitation over its 1 km square;
  0.3° W–9.7° E, 47.4–53.7° N; quality decreases outside Belgium (*Spatial
  resolution*).
- **Formats:** GeoTIFF int16 scaled by 100 (1 = 0.01 mm); HDF5 ODIM float32;
  `UL_x`, `UL_y` are the native coordinates of the upper-left corner of the
  upper-left pixel, specific to RMI (*Data format*, *Quick guide to ODIM*).

## Relevance to DECADE

S5 (#12): grid, projection, radars and the time convention used to sum the
5 min files of the project's copy into hours that match the ODYSSEY `ACRR`
window (`notebooks/04-mr-radclim.ipynb`). Background for RADCLIM as a bridge
(H3) and accumulation reference (H5).

## Limits

The guide describes 5 min and 1 h *accumulations*; the project's copy holds
only 5 min files with quantity `RATE` (mm/h according to the download page),
and each file declares a 20 s window ending about 33 s before its label, not a
5 min period (`docs/data.md`, RADCLIM row). The guide gives no version history
of the processing, so it does not say which steps applied in which years.
