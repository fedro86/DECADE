# Data

Verified facts about the input data: what exists, where, in which format, and
the known problems. How the data are processed is in [method.md](method.md);
how to download them is in [usage.md](usage.md).

Facts verified in October 2026 unless stated otherwise. If the data contradict
this page, fix the page in the same pull request as the code.

## OPERA public archive (ORD bucket)

`https://s3.waw3-1.cloudferro.com/openradar-archive/`, CC BY 4.0 (EUMETNET), no
credentials. Keys:
`YYYY/MM/DD/OPERA/COMP/OPERA@YYYYMMDDTHHMM@0@<product>.{h5,tiff}`.

The archive up to 31/12/2025 was uploaded in February 2026 (HDF5 + GeoTIFF).
**Since 1/1/2026 the bucket is updated almost in real time, but with HDF5
only** (GeoTIFFs only on 19/5 and 26/10/2026, partial). Some days are missing,
e.g. 1/10/2012 and 15/10/2024; CIRRUS is missing from 7 to 17/10/2024 (only
NIMBUS exists), and on 13–15/5/2025 there is no product at all.

| product | file | grid | step | period in the bucket |
|---|---|---|---|---|
| ODYSSEY max reflectivity | `DBZH_QIND.h5` | 1900 × 2200, 2 km | 15 min | 4/9/2012 → 5/7/2024 05:45 |
| ODYSSEY rain rate | `QIND_RATE.h5` | 1900 × 2200, 2 km | 15 min | same |
| ODYSSEY 1 h accumulation | `ACRR_QIND.h5` | 1900 × 2200, 2 km | 15 min | same |
| CIRRUS max reflectivity | `DBZH.h5` | 3800 × 4400, 1 km | 5 min | from 1/7/2024 |
| NIMBUS rain rate | `RATE.h5` | 1900 × 2200, 2 km | 15 min | from 5/7/2024 06:00 |
| NIMBUS 1 h accumulation | `ACRR.h5` | 1900 × 2200, 2 km | 15 min | same |

### Overlap between products

- Reflectivity: only 1–5/7/2024, and on those days only ODYSSEY exists at the
  quarter hours (CIRRUS at :00, :15, :30, :45 is missing).
- Rain: **no overlap** between ODYSSEY and NIMBUS.
- ODYSSEY was produced until 30/10/2024, but the public archive stops at
  5/7/2024.

### Grid

All products share projection and corners:
`+proj=laea +lat_0=55.0 +lon_0=10.0 +x_0=1950000.0 +y_0=-2100000.0 +units=m +ellps=WGS84`,
upper-left corner at −39.536°, 67.023°. Row 0 is north (verified: correlation
0.88 against 0.39 with the flipped field). CIRRUS has exactly twice the
resolution of ODYSSEY: each 2 km pixel covers 2 × 2 pixels at 1 km.

### Encoding (HDF5, ODIM)

- float64, `gain` 1, `offset` 0, `nodata` −9999000, `undetect` −8888000.
- ODYSSEY is ODIM 2.0, with `quantity` in `datasetN/what`; CIRRUS and NIMBUS
  are ODIM 2.4, with `quantity` in `datasetN/dataN/what`.
- CIRRUS has values down to −32 dBZ.
- ODYSSEY `ACRR`: dry areas are 0, `undetect` is not used. NIMBUS uses
  `undetect`.
- NIMBUS declares Marshall-Palmer in the files (`zr_a` = 200, `zr_b` = 1.6) and
  has a quality field `quality1`.

### Time windows for the label NT

| product | window |
|---|---|
| ODYSSEY `DBZH`, `RATE` | [NT−10, NT+5], e.g. 11:50–12:05 for 12:00 |
| CIRRUS `DBZH` | (NT−10, NT], e.g. 11:55:01–12:05 for 12:05 |
| NIMBUS `RATE` | instantaneous at NT |
| ODYSSEY `ACRR` | NT−55 → NT+5 |
| NIMBUS `ACRR` | NT−60 → NT |

For the same label, ODYSSEY reflectivity therefore "sees" about 2.5 min later
than CIRRUS.

### Quality fields

- ODYSSEY `DBZH_QIND` has `QIND` in `dataset2`: 0–1 in steps of 0.1, `nodata`
  where there is no echo. On the echoes over Belgium + 350 km the median is
  0.1–0.3.
- CIRRUS has `dataset1/data1/quality1` (`pl.imgw.quality.qi_total`), almost
  binary: about 90% of European echoes are 0, about 8% are 1. Its meaning is not
  clear yet, so it must not be used as a mask.
- In the GeoTIFFs the quality is band 2, pixel-interleaved, in the same tiles.

### GeoTIFFs next to the HDF5 files

- Tiled 512 × 512, deflate, float32, with overviews. Values identical to the
  HDF5 (verified on ODYSSEY 2013, 2018, 2024 and CIRRUS 1/7/2024); `undetect`
  becomes NaN.
- The georeferencing is shifted by half a pixel (origin −1000/+1000 m at 2 km,
  −500/+500 m at 1 km): take the grid from the HDF5 and read by indices.
- CIRRUS tags have no `quantity`.
- Reading only Belgium + 350 km in pieces costs 140–280 kB of network per
  ODYSSEY frame, against about 950 kB for the whole HDF5.

### Whole CIRRUS HDF5 files

About 2.2–2.8 MB, chunks 760 × 880 gzip 9 (the Belgian area touches 6 chunks
out of 30). Reading pieces through HTTP ranges gives identical values but is
slow in parallel with `urllib` (1.2 files/s); downloading whole files runs at
16–20 files/s (about 40 MB/s).

### CIRRUS `how/comment`

Some radar volumes are extrapolated with LK by Météo-France (pysteps). The
files do not say which radars.

## Known problems

- **Outliers in ODYSSEY.** For example on 3/7/2024 12:00 a group of 4 pixels
  reaches 75,000 mm/h at row 1444, column 899 of the 2 km grid, inside the
  Belgian working crop; the same point is **128 dBZ** in `DBZH_QIND`. Over the
  whole domain there are often from 4 to more than 100 pixels ≥ 100 dBZ. They
  need a threshold plus a mask of persistent points. Every conversion to R must
  be capped (55 dBZ is used), otherwise these pixels dominate the volumes.
- **ODYSSEY has about half the rain volume of CIRRUS** over Belgium on
  1–5/7/2024: a gap of 3.5–5 dB at all quantiles, POD at 10 dBZ about 0.69. It
  is a difference between products, present even without interpolation.
- **Incomplete CIRRUS days**, e.g. 192 frames out of 288 on 2/7/2024.

## Derived datasets on the project machine

Crops of Belgium + 350 km, aligned to 2 km, made with `fetch_cog_crop.py`. They
are not in git; ask for a copy. They are read with `read_odim_composite` like
whole files, also with `extent` as long as the extent is inside the crop.

| folder | content | crop | size |
|---|---|---|---|
| `data/odyssey_bel/` | ODYSSEY `DBZH_QIND` 9/2012–7/2024 | rows 1053–1531, cols 528–1027 at 2 km | 400,337 frames, 37 GB (about 100 kB/frame) |
| `data/cirrus_bel/` | CIRRUS `DBZH` 7/2024–10/2026 | rows 2106–3062, cols 1056–2054 at 1 km | 238,863 frames, 58 GB (about 380 kB/frame), on 27/10/2026 |

- `cirrus_bel` comes from the GeoTIFFs up to 12/2025 and from whole HDF5 files
  in 2026 (crops verified identical to the GeoTIFF ones on two times in 2025).
  Coverage 97.7%: 14 days missing (7–17/10/2024, 13–15/5/2025). To extend it,
  rerun `fetch_cog_crop.py` with a later end date.
- **The crops hold reflectivity only.** Quality fields would require redoing
  them, with the same network traffic.
- `data/mask_BEL_1km.npy`: Belgium mask on the full CIRRUS grid (Natural Earth
  1:10m), made with `make_region_mask.py`.

## Other sources

| source | what | notes |
|---|---|---|
| MeteoGate ORD API (`https://api.meteogate.eu/eu-eumetnet-weather-radar`, OGC EDR) | OPERA products | **last 24 hours only**, also with a key (which raises the limit to 2000 requests/hour). Useful for recent CIRRUS metadata, not for history. Credentials in `.env` |
| ArcoDataHub `opera-plus-it-vmi.zarr` (FBK, CC BY-SA 4.0) | VMI in dBZ, 1 km / 5 min from 1/7/2024, OPERA plus Italian DPC radars | in **EPSG:3035**, 3819 × 4411, not the native OPERA grid. `_FillValue` −9999, `undetect` −9998. One chunk is a whole frame (about 100–130 MB compressed, about 45 s per frame): reading only Belgium costs as much as reading Europe. Credentials in `.env` |
| RODEO-ML (`s3://ecmwf-rodeo-benchmark`, ECMWF) | precipitation accumulations, 1 h and 6 h, 2013–2023 | accumulations only |
| RMI open data (`opendata.meteo.be`, WMS `radar:belgian_rainfall_composite`) | Belgian composite, 5 min | only the last ~13 hours; national, so outside the method |
| VMM (Flemish Environment Agency) | open radar products from the same radars, from June 2021 | validation reference for Belgium (see [roadmap.md](roadmap.md)); not yet examined here |
