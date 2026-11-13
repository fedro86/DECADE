# CERRA-Land surface reanalysis: Data User Guide

- **Authors, year, venue:** Copernicus Climate Change Service (C3S) and ECMWF, Copernicus Knowledge Base (ECMWF Confluence); last modified 26/02/2026 (the *Known issues* section added on 25/02/2026).
- **Link:** <https://confluence.ecmwf.int/spaces/CKB/pages/278548151/CERRA-Land+surface+reanalysis+Data+User+Guide>
- **Access:** open web page; the data are CC BY 4.0
- **Read:** full text of the web page, read on 13/11/2026

## What it is

The user guide of the CERRA-Land dataset in the Climate Data Store: grid,
variables, conventions and known issues.

## Numbers we use

- **Precipitation convention:** total precipitation exists only in the 06 UTC
  analysis and is the amount of the 24 h from 06 UTC of the previous day to
  06 UTC of the stated day; the date is the end of the accumulation.
- **Method:** optimal interpolation between a first guess from CERRA forecast
  precipitation and daily rain gauges (Soci et al., 2016).
- **Known issue, 12-bit packing:** the data of 1/5/2021–31/7/2025 were
  converted from netCDF to GRIB2 with 12 bits per value instead of 24, by
  mistake; snow depth and snow water equivalent are named as the most
  affected; precipitation is not mentioned; data with 24 bits announced for
  July 2026.
- **Coastal cells:** aggregated values on coastal cells can be biased, because
  the sea fraction is not taken into account.

## Relevance to DECADE

H3b (#82): it fixes the 06–06 UTC day used to sum ODYSSEY, CIRRUS and
ERA5-Land (`opera_ds/bridge.py`). The 12-bit packing falls inside our period
(5/2021–7/2025) and its effect on precipitation is not documented: it has to be
checked on the data (the step of a 12-bit value and whether small daily
amounts are rounded). The coastal cells of Belgium may need to be left out or
checked apart.

## Limits

- The page still gives 9/1984 → 4/2021 as the period, while the catalogue now
  reaches 12/2025; it says nothing on how the continuation is produced.
