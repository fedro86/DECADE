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

CIRRUS `DBZH` in 2025 (checked over the whole year with the Belgian crop):
1,329 of the 105,120 time steps at 5 min are missing from the bucket. A row
gives the first and the last missing time step, not a continuous gap: the
first row spans 389 time steps, of which 243 are missing; the other rows are
continuous.

| from | to | missing |
|---|---|---:|
| 1/1/2025 06:50 | 2/1/2025 15:10 | 243 |
| 18/2/2025 22:20 | 19/2/2025 06:55 | 104 |
| 13/5/2025 00:00 | 16/5/2025 01:55 | 888 |
| 14/8/2025 09:00 | 14/8/2025 09:55 | 12 |
| isolated, on 22 other days | | 82 |

| product | file | grid | step | period in the bucket |
|---|---|---|---|---|
| ODYSSEY max reflectivity | `DBZH_QIND.h5` | 1900 × 2200, 2 km | 15 min | 4/9/2012 → 5/7/2024 06:00 |
| ODYSSEY rain rate | `QIND_RATE.h5` | 1900 × 2200, 2 km | 15 min | same |
| ODYSSEY 1 h accumulation | `ACRR_QIND.h5` | 1900 × 2200, 2 km | 15 min | same |
| CIRRUS max reflectivity | `DBZH.h5` | 3800 × 4400, 1 km | 5 min | from 1/7/2024 |
| NIMBUS rain rate | `RATE.h5` | 1900 × 2200, 2 km | 15 min | from 5/7/2024 06:15 |
| NIMBUS 1 h accumulation | `ACRR.h5` | 1900 × 2200, 2 km | 15 min | same |

The switch on 5/7/2024, from a listing of the bucket (h5 and tiff alike):

| product | 05:15 | 05:30 | 05:45 | 06:00 | 06:15 |
|---|---|---|---|---|---|
| ODYSSEY `DBZH_QIND`, `QIND_RATE`, `ACRR_QIND` | yes | — | yes | yes | — |
| NIMBUS `RATE`, `ACRR` | — | yes | — | — | yes |
| CIRRUS `DBZH` | — | yes | — | — | yes |

So the last ODYSSEY time step is 06:00 and NIMBUS runs continuously from 06:15;
05:30 is a single NIMBUS and CIRRUS time step where all three ODYSSEY products
are missing.

ODYSSEY `DBZH_QIND` in 2023 (checked over the whole year with the Belgian
crop): 632 of the 35,040 time steps at 15 min are missing from the bucket. A
row gives the first and the last missing time step, not a continuous gap: the
30/10/2023 row spans 47 time steps, of which 21 are missing; the other rows are
continuous.

| from | to | missing |
|---|---|---:|
| 6/7/2023 07:30 | 6/7/2023 07:45 | 2 |
| 30/10/2023 00:15 | 30/10/2023 11:45 | 21 |
| 4/11/2023 00:00 | 10/11/2023 06:45 | 604 |
| isolated: 9/3 19:15, 6/7 08:30, 20/7 08:30, 1/8 11:45, 24/8 12:30 | | 5 |

### Overlap between products

- Reflectivity: only 1–5/7/2024, and on those days only ODYSSEY exists at the
  quarter hours (CIRRUS at :00, :15, :30, :45 is missing), except 5/7/2024
  05:30, where CIRRUS exists and ODYSSEY does not.
- Rain: **no overlap** between ODYSSEY and NIMBUS: no time step has both. They
  are consecutive: ODYSSEY ends at 5/7/2024 06:00 and NIMBUS runs from 06:15,
  the next time step; the only earlier NIMBUS time step, 05:30, has no ODYSSEY.
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

The reflectivity windows are the ones each file declares in
`dataset1/what` (`startdate`, `starttime`, `enddate`, `endtime`), checked on
8,415 ODYSSEY files (one in 50 of the Belgian crops, 2012–2024, and all of
1–5/7/2024) and 5,758 CIRRUS files (one in 50 of the Belgian crops, 7/2024–
1/2026, and all of 1–5/7/2024), with no exception. CIRRUS starts at
NT−9:59. They agree with the text of the OPERA note on CIRRUS and ODYSSEY
([summary](sources/2024%20-%20Radojevic%20-%20Maximum%20Reflectivity%20Composite%20Configuration%20of%20CIRRUS%20relative%20to%20ODYSSEY.md));
its Table 3 gives "NT−9 to NT+9" for ODYSSEY, which the files do not show.

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

### Single-radar files of the coastal radars

The bucket also holds the single-radar files that the countries send to OPERA
(`YYYY/MM/DD/<country>/<node>/PVOL|SCAN/…`), from 2024 and not every day.
Next to the filtered `DBZH` they carry the unfiltered `TH`. Asked in the review
of #74 (H2, #19), to see how much sea and land clutter is removed before
OPERA.

**What was compared:**
- **Files:** downloaded into `data/opera_single/` (exploration code, not in the repository yet).
  - Belgium: the PVOL of the task starting at 0.3°, with `DBZH` and `TH` in
    separate files.
  - Netherlands: PVOL with `DBZH`, `TH` and `VRADH` in one file.
  - France: the SCAN at 0.4°, with the three quantities in one file.
- **Measure:** at the lowest elevation, the bins with `TH` ≥ 10 dBZ, and the
  share of them that `DBZH` removes (undetect, nodata or below 10 dBZ). Sea and
  land are told apart by the Natural Earth countries, with ranges flat in an
  azimuthal equidistant projection.
- **Cases:** a dry hour, 20/6/2025 06:00–06:55, and a rainy day, 5/1/2025, the
  day with most wet pixels in the H1 months. No day of anomalous propagation
  has been found yet.

| radar | processing declared in `how` (lowest elevation) | dry hour: sea bins, removed | dry hour: land bins, removed | rainy day: sea, removed | rainy day: land, removed |
|---|---|---:|---:|---:|---:|
| bejab (Jabbeke) | Rainbow 5.59, `Dclutter` DFT, FFT, Speckle; `SQI` 0.3, `CSR` 30, `LOG` 2; `BBC` and `VPRCorr` False | 54,973, 93.7% | 185,588, 97.4% | 8.2 M, 4.0% | 17.4 M, 10.8% |
| behel (Helchteren) | Rainbow 5.59, `Dclutter` DFT, FFT, Spatial, Speckle; `SQI` 0.3, `CSR` 30, `LOG` 2 | 324, 86.1% | 620,953, 97.2% | 2.8 M, 3.3% | 53.6 M, 7.0% |
| bewid (Wideumont) | Rainbow 5.59, `Dclutter` DFT, FFT, Speckle; `SQI` 0.3, `CSR` 30, `LOG` 2 | 21, 61.9% | 235,824, 98.8% | 0.06 M, 11.3% | 43.7 M, 5.8% |
| nldhl (Den Helder) | `SQI` 0.3, `CSR` 30, `LOG` 0.5; no clutter filter named | 84,648, 58.3% | 153,814, 60.8% | 14.0 M, 11.2% | 13.4 M, 15.1% |
| nlhrw (Herwijnen) | `SQI` 0.3, `CSR` 30, `LOG` 0.5; no clutter filter named | 2,248, 77.4% | 202,829, 70.8% | 5.8 M, 11.5% | 27.4 M, 11.3% |
| frabb (Abbeville) | SERVAL; no processing declared | 6,958, 94.3% | 109,930, 97.5% | 2.5 M, 1.8% | 8.3 M, 25.9% |
| frave (Avesnois) | SERVAL; no processing declared | 66, 97.0% | 94,986, 99.9% | 0.9 M, 1.3% | 12.4 M, 14.0% |

**How to read it:**
- **The removed share mixes two things.** `TH` ≥ 10 dBZ includes rain as well
  as clutter, and rain is rightly kept.
  - In the dry hour almost every strong echo is clutter, and the Belgian and
    French radars remove 94–100% of it over land and over the sea near them.
    The lower Dutch shares (58–77%) were checked over the 12 volumes of the
    hour. About a third of what `DBZH` keeps stays in place in all 12 volumes,
    mostly near the radar (median range 18 km at Den Helder, 3 km at
    Herwijnen); the rest moves. None of the fixed bins reaches the CIRRUS
    composite at 10 dBZ or more at more than 5 of the 12 times of the hour,
    so OPERA removes them before compositing.
  - On the rainy day the shares are low because most echoes are rain.
- **Only from 2024.** Single-radar files are not in the bucket before 2024, so
  the processing of 2012–2023 cannot be checked this way.

### Radars in the ODYSSEY composites (`how/nodes`)

Each composite lists the radars it was made from in `how/nodes`, and so do
our crops. ODYSSEY writes `NOD:bewid,...` and CIRRUS writes `bewid, ...`.

I read this attribute in all 400,337 ODYSSEY crops on 10/11/2026 (results in
`results/h2_artefacts/nodes_odyssey.csv`, not in git). A radar counts as
listed on a day when it is in at least half of that day's composites. Days
with no composite are left out, so a gap in the archive is not counted as an
absence.

The radar positions come from the OPERA radar database of EUMETNET
(*Inventory of sources and licences*). Both of its files are used:
- `OPERA_RADARS_DB.json`, the active radars;
- `OPERA_RADARS_ARH_DB.json`, the archived ones.

They were downloaded on 10/11/2026 into `data/opera_radars/`.
- **Matching.** Each code of `how/nodes` is matched with the `odimcode` of
  the database. When a code is in both files (several German radars renewed
  on almost the same site), the active row is used.
- **Coverage.** All the ODYSSEY codes of the domain are in the database
  except `deflg`. The other missing codes are Spanish and old Estonian,
  Croatian and Icelandic radars.
- **Check.** For the 47 radars that also have a 2025 single-radar file, the
  database position matches the one in the file within 0.0003°.

The table lists the 56 radars of `how/nodes` that lie within 100 km of the
Belgian crop, plus `deflg`, which has no position. The column *in the crop*
says whether the radar itself is inside the crop.

The archive becomes regular only in April 2013 (*Known problems*). So a
"first day" before that date is the start of the readable archive, not
necessarily the radar's.

| node | site | position | in the crop | first day | last day | days listed / days in its period | longest absence, days |
|---|---|---|---|---|---|---:|---|
| `behel` | Helchteren | 51.07 N, 5.41 E | yes | 21/3/2018 | 5/7/2024 | 1,980 / 2,293 | 258 (17/6/2020 to 1/3/2021) |
| `bejab` | Jabbeke | 51.19 N, 3.06 E | yes | 27/11/2014 | 5/7/2024 | 3,153 / 3,503 | 98 (6/11/2015 to 11/2/2016) |
| `bewid` | Wideumont | 49.91 N, 5.50 E | yes | 26/3/2013 | 5/7/2024 | 3,730 / 4,114 | 124 (8/4/2022 to 9/8/2022) |
| `chalb` | Albis | 47.28 N, 8.51 E | yes | 7/3/2017 | 5/7/2024 | 2,623 / 2,672 | 8 (21/6/2017 to 28/6/2017) |
| `chdol` | La Dole | 46.43 N, 6.10 E | yes | 29/6/2017 | 5/7/2024 | 2,532 / 2,558 | 7 (25/10/2017 to 31/10/2017) |
| `chlem` | Monte Lema | 46.04 N, 8.83 E | no | 16/9/2014 | 5/7/2024 | 3,528 / 3,575 | 11 (12/12/2020 to 22/12/2020) |
| `chppm` | Plaine Morte | 46.37 N, 7.49 E | yes | 27/2/2018 | 5/7/2024 | 2,255 / 2,315 | 23 (22/1/2019 to 13/2/2019) |
| `chwei` | Weissfluhgipfel | 46.84 N, 9.79 E | yes | 27/6/2018 | 5/7/2024 | 2,186 / 2,195 | 5 (18/7/2022 to 22/7/2022) |
| `deasb` | Isle of Borkum | 53.56 N, 6.75 E | yes | 24/4/2018 | 5/7/2024 | 2,024 / 2,259 | 170 (18/6/2018 to 4/12/2018) |
| `deboo` | Boostedt | 54.00 N, 10.05 E | yes | 28/1/2014 | 5/7/2024 | 3,722 / 3,806 | 29 (27/7/2016 to 24/8/2016) |
| `deeis` | Eisberg | 49.54 N, 12.40 E | no | 4/9/2012 | 5/7/2024 | 3,719 / 4,177 | 229 (6/6/2013 to 20/1/2014) |
| `deemd` | Emden | 53.34 N, 7.02 E | yes | 4/9/2012 | 27/2/2018 | 1,565 / 1,863 | 180 (22/7/2015 to 17/1/2016) |
| `deess` | Essen | 51.41 N, 6.97 E | yes | 27/3/2013 | 5/7/2024 | 4,032 / 4,113 | 29 (27/7/2016 to 24/8/2016) |
| `defbg` | Feldberg | 47.87 N, 8.00 E | yes | 5/2/2019 | 5/7/2024 | 1,945 / 1,972 | 5 (8/7/2023 to 12/7/2023) |
| `defld` | Flechtdorf | 51.31 N, 8.80 E | yes | 4/9/2012 | 5/7/2024 | 3,727 / 4,177 | 197 (29/4/2014 to 11/11/2014) |
| `deflg` | not in the database | — | — | 22/1/2013 | 4/2/2019 | 2,140 / 2,199 | 29 (27/7/2016 to 24/8/2016) |
| `deham` | Hamburg | 53.62 N, 10.00 E | yes | 4/9/2012 | 23/1/2014 | 366 / 367 | 1 (14/3/2013 to 14/3/2013) |
| `dehan` | Hannover | 52.46 N, 9.70 E | yes | 4/9/2012 | 22/4/2015 | 360 / 821 | 317 (26/3/2013 to 5/2/2014) |
| `dehnr` | Hannover | 52.46 N, 9.69 E | yes | 23/4/2015 | 5/7/2024 | 3,282 / 3,356 | 29 (27/7/2016 to 24/8/2016) |
| `deisn` | Isen/München | 48.17 N, 12.10 E | no | 28/1/2014 | 5/7/2024 | 3,707 / 3,806 | 30 (27/7/2016 to 25/8/2016) |
| `demem` | Memmingen | 48.04 N, 10.22 E | yes | 12/6/2013 | 5/7/2024 | 3,879 / 4,036 | 68 (14/1/2023 to 22/3/2023) |
| `demuc` | München | 48.34 N, 11.61 E | no | 26/3/2013 | 21/1/2014 | 293 / 302 | 4 (20/6/2013 to 23/6/2013) |
| `deneu` | Neuhaus | 50.50 N, 11.14 E | yes | 26/3/2013 | 5/7/2024 | 4,031 / 4,114 | 29 (27/7/2016 to 24/8/2016) |
| `denhb` | Neuheilenbach | 50.11 N, 6.55 E | yes | 4/9/2012 | 5/7/2024 | 3,750 / 4,177 | 252 (28/8/2013 to 6/5/2014) |
| `deoft` | Offenthal | 49.98 N, 8.71 E | yes | 4/9/2012 | 5/7/2024 | 4,099 / 4,177 | 30 (26/7/2016 to 24/8/2016) |
| `deros` | Rostock | 54.18 N, 12.06 E | no | 4/9/2012 | 5/7/2024 | 3,686 / 4,177 | 390 (13/6/2013 to 7/7/2014) |
| `detur` | Tuerkheim | 48.59 N, 9.78 E | yes | 4/9/2012 | 5/7/2024 | 3,717 / 4,177 | 397 (5/4/2013 to 6/5/2014) |
| `deumd` | Ummendorf | 52.16 N, 11.18 E | yes | 4/9/2012 | 3/7/2024 | 3,738 / 4,175 | 300 (14/2/2013 to 16/12/2013) |
| `dkrom` | Römö | 55.17 N, 8.55 E | no | 26/3/2013 | 5/7/2024 | 4,007 / 4,114 | 20 (24/8/2017 to 12/9/2017) |
| `dkste` | Stevns | 55.33 N, 12.45 E | no | 26/3/2013 | 5/7/2024 | 4,009 / 4,114 | 21 (6/10/2017 to 26/10/2017) |
| `frabb` | Abbeville | 50.14 N, 1.83 E | yes | 4/9/2012 | 5/7/2024 | 4,125 / 4,177 | 11 (17/3/2019 to 27/3/2019) |
| `frave` | Avesnes | 50.13 N, 3.81 E | yes | 4/9/2012 | 5/7/2024 | 4,106 / 4,177 | 25 (2/5/2020 to 26/5/2020) |
| `frbla` | Blaisy-Haut | 47.36 N, 4.78 E | yes | 4/9/2012 | 5/7/2024 | 4,120 / 4,177 | 11 (9/8/2013 to 19/8/2013) |
| `frbou` | Bourges | 47.06 N, 2.36 E | yes | 4/9/2012 | 5/7/2024 | 4,015 / 4,177 | 94 (23/4/2018 to 25/7/2018) |
| `frcae` | Falaise | 48.93 N, 0.15 W | yes | 4/9/2012 | 5/7/2024 | 3,969 / 4,177 | 122 (25/2/2014 to 26/6/2014) |
| `frche` | Cherves | 46.70 N, 0.07 E | yes | 4/9/2012 | 5/7/2024 | 4,034 / 4,177 | 17 (16/1/2022 to 1/2/2022) |
| `frgre` | Grèzes | 45.10 N, 1.37 E | no | 4/9/2012 | 5/7/2024 | 4,139 / 4,177 | 7 (17/4/2019 to 23/4/2019) |
| `frlep` | Sembadel | 45.29 N, 3.71 E | no | 4/9/2012 | 5/7/2024 | 3,889 / 4,177 | 190 (10/9/2013 to 18/3/2014) |
| `frmtc` | Montancy | 47.37 N, 7.02 E | yes | 4/9/2012 | 5/7/2024 | 3,942 / 4,177 | 73 (9/10/2019 to 20/12/2019) |
| `frnan` | Nancy | 48.72 N, 6.58 E | yes | 4/9/2012 | 5/7/2024 | 3,981 / 4,177 | 141 (16/5/2017 to 3/10/2017) |
| `frniz` | Saint Nizier | 46.07 N, 4.45 E | no | 4/9/2012 | 5/7/2024 | 3,999 / 4,177 | 155 (15/9/2015 to 16/2/2016) |
| `frtra` | Trappes | 48.77 N, 2.01 E | yes | 4/9/2012 | 5/7/2024 | 4,163 / 4,177 | 3 (7/3/2020 to 9/3/2020) |
| `frtre` | Treillères | 47.34 N, 1.66 W | yes | 4/9/2012 | 5/7/2024 | 3,949 / 4,177 | 211 (8/3/2016 to 4/10/2016) |
| `frtro` | Arcis-sur-Aube | 48.46 N, 4.31 E | yes | 4/9/2012 | 5/7/2024 | 3,939 / 4,177 | 161 (18/5/2015 to 25/10/2015) |
| `nldbl` | De Bilt | 52.10 N, 5.18 E | yes | 4/9/2012 | 19/1/2017 | 1,397 / 1,459 | 50 (29/1/2013 to 19/3/2013) |
| `nldhl` | Den Helder | 52.95 N, 4.79 E | yes | 4/9/2012 | 5/7/2024 | 3,853 / 4,177 | 113 (10/10/2016 to 30/1/2017) |
| `nlhrw` | Herwijnen | 51.84 N, 5.14 E | yes | 19/5/2017 | 5/7/2024 | 2,567 / 2,599 | 8 (21/6/2017 to 28/6/2017) |
| `ukche` | Chenies | 51.69 N, 0.53 W | yes | 4/9/2012 | 5/7/2024 | 3,956 / 4,177 | 57 (22/1/2013 to 19/3/2013) |
| `ukcle` | Clee Hill | 52.40 N, 2.60 W | yes | 4/9/2012 | 3/7/2024 | 3,775 / 4,175 | 222 (23/2/2015 to 2/10/2015) |
| `ukcob` | Cobbacombe Cross | 50.96 N, 3.45 W | no | 4/9/2012 | 5/7/2024 | 3,782 / 4,177 | 134 (25/12/2013 to 7/5/2014) |
| `ukcyg` | Crug y Gorllwyn | 51.98 N, 4.44 W | no | 4/9/2012 | 5/7/2024 | 3,805 / 4,177 | 295 (14/9/2015 to 4/7/2016) |
| `ukdea` | Dean Hill | 51.03 N, 1.65 W | yes | 4/9/2012 | 5/7/2024 | 3,799 / 4,177 | 219 (17/10/2016 to 23/5/2017) |
| `ukham` | Hameldon Hill | 53.75 N, 2.29 W | yes | 4/9/2012 | 5/7/2024 | 3,688 / 4,177 | 318 (3/3/2014 to 14/1/2015) |
| `ukhmy` | High Moorsley | 54.80 N, 1.47 W | no | 4/9/2012 | 5/7/2024 | 3,874 / 4,177 | 170 (23/5/2016 to 8/11/2016) |
| `uking` | Ingham | 53.33 N, 0.56 W | yes | 4/9/2012 | 5/7/2024 | 3,793 / 4,177 | 255 (1/9/2014 to 13/5/2015) |
| `ukjer` | Jersey | 49.18 N, 2.22 W | yes | 4/9/2012 | 5/7/2024 | 3,984 / 4,177 | 99 (1/6/2016 to 7/9/2016) |
| `ukthu` | Thurnham | 51.29 N, 0.60 E | yes | 26/3/2013 | 5/7/2024 | 3,703 / 4,114 | 202 (28/5/2013 to 15/12/2013) |

- **Radars that start or stop within the period:**
  - `bejab` starts on 27/11/2014 and `behel` on 21/3/2018.
  - `nlhrw` starts on 19/5/2017, four months after the last day of `nldbl`
    (19/1/2017).
  - In Germany, `deboo` starts on 28/1/2014, five days after the last day of
    `deham`. `dehnr` starts on 23/4/2015, the day after the last day of
    `dehan`. `deasb` starts on 24/4/2018, after `deemd` ends on 27/2/2018.
    `defbg` starts on 5/2/2019, the day after the last day of `deflg`.
- **Long absences.** Several radars are missing for months, for example:
  - `behel` 258 days (2020–2021);
  - `bewid` 124 days (2022);
  - `deros` 390 days (2013–2014).
- **A common absence.** From 28/7 to 23/8/2016 no German radar is listed in
  any composite. The German radars of the table are missing from 26–27/7 to
  24–25/8/2016.

## Known problems

- **Outliers in ODYSSEY.** For example on 3/7/2024 12:00 a group of 4 pixels
  reaches 75,000 mm/h at row 1444, column 899 of the 2 km grid, inside the
  Belgian working crop; the same point is **128 dBZ** in `DBZH_QIND`. Over the
  whole domain there are often from 4 to more than 100 pixels ≥ 100 dBZ. They
  need a threshold plus a mask of persistent points. Every conversion to R must
  be capped (55 dBZ, as in Imhoff et al. 2020, section 2.2.1), otherwise these
  pixels dominate the volumes. The cap limits the rain rate; removing values
  such as 128 dBZ is a separate threshold (H2, #19).
- **ODYSSEY has about half the rain volume of CIRRUS** over Belgium on
  1–5/7/2024: a gap of 3.5–5 dB at all quantiles, POD at 10 dBZ about 0.69. It
  is a difference between products, present even without interpolation.
- **Incomplete CIRRUS days**, e.g. 192 frames out of 288 on 2/7/2024.
- **ODYSSEY before April 2013 is sparse** (`DBZH_QIND`, crop download of
  9/11/2026, `data/odyssey_bel/failed.txt`):
  - 2012 has only 576 readable frames, 4–9/9/2012.
  - From 10/9 to 22/11/2012, the 3,338 files in the bucket cannot be read:
    `fetch_cog_crop.py` fails with "Unable to synchronously open object
    (object 'what' doesn't exist)".
  - December 2012 has no file.
  - January 2013 has files only from 22/1 (900 frames), and March 2013 has
    2,286 of 2,976.
  - 32 more files fail with the same error on 17/5/2013, 16:00–23:45.
  - In all, 3,370 files cannot be read. The 400,337 frames of the crops
    (*Derived datasets*) do not include them.
  - So yearly statistics start in 2013, and 2013 lacks most of January and
    part of March.

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
- `data/radclim/`: RADCLIM zips from the project's internal copy, unpacked in place
  (`manifest.json` and `kmi-radclim/YYYY/MM/*.hdf`); for now 14/7/2021 only
  (289 files, 67 MB).
- `data/odyssey_acrr/`: whole ODYSSEY `ACRR_QIND` files downloaded by
  `opera_ds.ord.download` (one for now, 14/7/2021 21:00).
- `data/era5land_bel/`: ERA5-Land hourly `tp`, 1/2012–10/2026, made with
  `fetch_cds.py` over 55.0–45.6 N, 3.9 W–11.8 E (95 × 158 cells). 178 monthly
  netCDF files, 2.9 GB (8–24 MB a month).
- `data/cerraland_bel/`: CERRA-Land daily precipitation, 1/2012–12/2025, made
  with `fetch_cds.py` (window of 204 × 224 cells of the CERRA grid, about
  4 MB a month); download in progress, newest year first (23 months on
  11/11/2026), completed in S8.

## Inventory of sources and licences

Every source we know of, used or not; which ones enter the method is decided
in [roadmap.md](roadmap.md) (*Constraints*). Licences checked on 3/11/2026 on
the pages linked; "not stated" means no licence was found in the provider's
own documentation.

| source | content | period | licence | notes |
|---|---|---|---|---|
| OPERA ORD bucket (EUMETNET) | ODYSSEY, CIRRUS, NIMBUS composites | 2012 → now | CC BY 4.0 | see *OPERA public archive* above |
| [OPERA radar database](https://eumetnet.eu/wp-content/themes/aeron-child/observations-programme/current-activities/opera/database/OPERA_Database) (EUMETNET) | ODIM code, site, coordinates, band, start and end year of each OPERA radar; active radars (`OPERA_RADARS_DB.json`) and archived ones (`OPERA_RADARS_ARH_DB.json`), also as CSV and XLSX | the database as published (downloaded 10/11/2026) | not stated | positions of the radars of `how/nodes` (*Radars in the ODYSSEY composites*); local copy in `data/opera_radars/` |
| MeteoGate ORD API (`https://api.meteogate.eu/eu-eumetnet-weather-radar`, OGC EDR) | the same OPERA products | **last 24 hours only** | CC BY 4.0 (OPERA data) | also with a key (which raises the limit to 2000 requests/hour). Useful for recent CIRRUS metadata, not for history. Credentials in `.env` |
| [EURADCLIM 3.0](https://dataplatform.knmi.nl/dataset/rad-opera-24h-rainfall-accumulation-euradclim-3-0) (KNMI Data Platform) | OPERA rain accumulations adjusted with rain gauges, 1 h and 24 h, 2 km | 2013–2023 | CC BY 4.0 | versions 1.0 and 2.0 are deprecated. The dataset page expects a yearly rerun that adds one year, but no version after 3.0 is published (KNMI Open Data API, 10/11/2026). Version 4, 2013–2024, is announced for the KNMI platform and the Copernicus Climate Data Store, without a date ([EMS2026-403](https://meetingorganizer.copernicus.org/EMS2026/EMS2026-403.html)); like 3.0 it is built on the OPERA composites, so it carries the ODYSSEY → CIRRUS change of July 2024 and cannot be the bridge of H3. Monthly zips of the whole of Europe, with no cut on the server: 132 files and 129.9 GB for 1 h, 132 files and 384.3 GB for 24 h (file listing of the KNMI Open Data API, 10/11/2026). The Open Data API needs a key; the shared anonymous one of the [developer portal](https://developer.dataplatform.knmi.nl/open-data-api) is often rate-limited. Download left to H4 (#23) |
| [ECA&D](https://www.ecad.eu) (KNMI) | daily station series, including precipitation | from the 19th century, varies by station | **non-commercial research and education only**; results must be published in the open literature | about 85% of the series can be downloaded; E-OBS (gridded) has the [same terms](https://ewds.climate.copernicus.eu/licences/licence-to-use-E-OBS-products) |
| [RODEO-ML](https://github.com/ecmwf/rodeo-ai-static-datasets) (`s3://ecmwf-rodeo-benchmark`, ECMWF) | OPERA precipitation accumulations, 1 h and 6 h; ECA&D-based verification data | 2013–2023 | per dataset, not stated in the repository ("open data licenses where applicable") | accumulations only |
| ArcoDataHub `opera-plus-it-vmi.zarr` (FBK) | VMI in dBZ, 1 km / 5 min, OPERA plus Italian DPC radars | from 1/7/2024 | CC BY-SA 4.0 | in **EPSG:3035**, 3819 × 4411, not the native OPERA grid. `_FillValue` −9999, `undetect` −9998. One chunk is a whole frame (about 100–130 MB compressed, about 45 s per frame): reading only Belgium costs as much as reading Europe. Credentials in `.env` |
| [RADCLIM](https://publish.geo.be/geonetwork/srv/api/records/RMI_DATASET_RADCLIM?language=all) (RMI) | radar rainfall for Belgium and surroundings merged with rain gauges (kriging with external drift), 1 km, 700 × 700, Belgian Lambert 2008 (EPSG:3812). The product has 5 min and 1 h accumulations in ODIM HDF5 and GeoTIFF; **the project's copy** (an internal copy of the project, login needed, still to be verified; downloaded as a zip per period) has only 5 min files, most likely of the gauge-merged rate: the file names end in `rate.qpe_edk.hdf` and `dataset1/what` declares `product` `QPE_EDK`, and EDK is the kriging with external drift of the user guide (evidence from the names only, not checked against gauges). The files are ODIM_H5 2.2, `dataset1/data1` quantity `RATE`, float32, mm/h (download page; the file has no unit attribute; maximum 85.7 on 14/7/2021), NaN outside the coverage (34% of the grid), no `gain`, `offset`, `nodata` or `undetect`. Each file declares in `dataset1/what` a 20 s window ending 32–34 s before its label; the user guide says the label is the end of the accumulation period. 76.3 GB for the whole copy as stored (about 105 kB per file; 233 kB on the rainy 14/7/2021) | 2017–2022 (metadata record); **the project's copy: 1/1/2017 00:05 → 30/11/2023 23:55 UTC**, 726,325 files, 874 of 727,199 time steps missing in 12 gaps: three whole days, 19/5, 4/6 and 20/6/2023 (00:05–23:55, 287 each), 30/11/2018 13:20–13:40 (5), and 9 single time steps on 6/5/2020 and 9–10/9/2020 (download page, *Largest gaps*, 9/11/2026; its *From* is the first missing label, *To* the next one present). No time in common with CIRRUS (from 1/7/2024) | CC BY 4.0 | radars Wideumont, Jabbeke (RMI), Helchteren (VMM), Avesnois (Météo-France), as in `what/source` of the files; gauges of SPW, VMM and WL; quality decreases outside Belgium ([user guide](https://opendata.meteo.be/cases/202107/radclim_userguide.pdf), [summary](sources/2023%20-%20RMI%20-%20RADCLIM%20user%20guide.md)); read with `read_odim_composite(path, "RATE")`; one hour beside ODYSSEY in `notebooks/04-mr-radclim.ipynb`; a public version with mean-field bias correction is in the MLCast catalogue (row below) |
| [MLCast catalogue](https://github.com/mlcast-community/mlcast-datasets) (MLCast community; data on the ECMWF object store, `s3://mlcast-source-datasets/`, endpoint `https://object-store.os-api.cci2.ecmwf.int`) | national radar precipitation datasets converted to Zarr for machine learning, one Zarr store per dataset, read with `intake` or directly with xarray; besides the rows below, DMI reflectivity (2016–2025, 10 min), RADKLIM (DWD) and the Italian DPC rain rate | per dataset | per dataset (code: Apache 2.0 or BSD 3-Clause) | anonymous access, no account. One chunk is one whole frame, so reading Belgium costs as much as reading the whole grid. New datasets are proposed through an issue template of the repository: a possible home for the DECADE archive (R1). Read on 10/11/2026 |
| RADCLIM with mean-field bias correction (RMI, in the [MLCast catalogue](https://github.com/mlcast-community/mlcast-datasets), `be_rmi_radclim_mfb_5min`) | radar rain rate merged with rain gauges by **mean-field bias** correction (`rate_qpe_mfb`), not by the kriging with external drift of the project's copy (`QPE_EDK`); 5 min, 1 km, 700 × 700, Belgian Lambert 2008, mm/h | 1/1/2017 00:00 → 30/11/2023 23:55, 868 missing time steps | CC BY 4.0 | marked as a pre-release that can contain errors. No time in common with CIRRUS |
| Météo-France radar rainfall (in the [MLCast catalogue](https://github.com/mlcast-community/mlcast-datasets), `fr_mf_prate_5min`) | rain rate from the 1 km rainfall amounts of Météo-France, 1536 × 1536, polar stereographic, 5 min, mm/h; whether it is adjusted with gauges is not stated in the catalogue | 1/1/2020 → 31/12/2024, 389 missing time steps | CC BY 4.0 | covers northern France, part of the Belgian domain, and **both sides of the ODYSSEY → CIRRUS change of July 2024**: a candidate national bridge or reference for H3 (#20) |
| Met Office C-band rain radar 1 km composite (in the [MLCast catalogue](https://github.com/mlcast-community/mlcast-datasets), `uk_metoffice_5min`) | rain rate, 1 km, 2175 × 1725, British National Grid (EPSG:27700), 5 min, mm/h | 5/7/2005 → 31/12/2025, 100,404 missing time steps | Open Government Licence v3.0 | covers south-east England, the west of the Belgian domain, and **both sides of July 2024**: a candidate national bridge or reference for H3 (#20) |
| RADKLIM (DWD, in the [MLCast catalogue](https://github.com/mlcast-community/mlcast-datasets), `radklim_5_minutes`, `radklim_hourly`) | radar precipitation climatology of Germany, 1 km, 1100 × 900, 5 min and 1 h ([10.5676/DWD/RADKLIM_YW_V2017.002](https://doi.org/10.5676/DWD/RADKLIM_YW_V2017.002)) | 2001–2023 | CC BY 4.0 | covers western Germany, the east of the Belgian domain; no time in common with CIRRUS |
| RMI open data (`opendata.meteo.be`, WMS `radar:belgian_rainfall_composite`) | Belgian composite, 5 min | last ~13 hours only | CC BY 4.0 for RMI open data services (radar layer not checked) | |
| VMM raster service (KiWIS, `https://hydro.vmm.be/grid/kiwis/KiWIS`, `datasource=10`) | composite of Helchteren (VMM), Jabbeke (RMI) and Herwijnen (KNMI), CAPPI at 1 km height, 5 min: rain intensity `SRI_1km_cappi` (`ts_id` 911010, mm/h; radar only, no gauge-adjusted variant of the intensity is listed; this is what the project uses); 15 min, 1 h and 24 h accumulations adjusted with VMM gauges (`PAC_15m_1km_cappi_adj`, `PAC_1h_1km_cappi_adj`, `PAC_24h_1km_cappi_adj`). Since 1/10/2024 the service also lists `*_BEJAB0924issue` versions of the intensity and of the accumulations, whose name points to a problem of the Jabbeke radar in September 2024 (not checked) | **the API serves about the last six months only** (on 6/11/2026 a raster for 1/5/2026 was returned, none for 1/6/2025), although the series list declares `SRI_1km_cappi` from 9/9/2017 and the 1 h and 24 h accumulations from 6/6/2018; older data come only from the project's copy, which has scattered data in 2021 and 2022 and is almost continuous from 2023 | [Modellicentie voor gratis hergebruik v1.0](https://data.vlaanderen.be/id/licentie/modellicentie-gratis-hergebruik/v1.0) (free reuse with attribution), as in the VMM catalogue record [Meetreeksen – neerslag](https://www.vlaanderen.be/datavindplaats/catalogus/meetreeksen-neerslag) (high-value dataset, keywords including radar data; checked on 6/11/2026) | rasters with `request=getRasterTimeseriesValues`, `ts_id` and `format=hdf5`, without a token; the list of series and their declared period with `request=getTimeseriesList&station_name=Vlaanderen_VMM` (read on 6/11/2026). [Service documentation](https://waterinfo.vlaanderen.be/download/9f5ee0c9-dafa-46de-958b-7cac46eb8c23?dl=0), version 02/2022 |
| [CLAAS-3](https://doi.org/10.5676/EUM_SAF_CM/CLAAS/V003) (EUMETSAT CM SAF) | cloud properties from MSG SEVIRI, level 2 every 15 min on the full SEVIRI disk (3712 × 3712, about 3 km at nadir), NetCDF-4, in three files per slot: cloud mask (`cma`), cloud top (CTX) and cloud physical properties (CPP, with an extended cloud phase: liquid, supercooled, opaque ice, cirrus, overlap, overshooting). **No cloud type** like the NWC SAF one of CLAAS-2, which EURADCLIM used ([user manual 3.1](https://www.cmsaf.eu/SharedDocs/Literatur/document/2022/saf_cm_knmi_pum_sev_cld_3_1_final_pdf.pdf?__blob=publicationFile), section 7.1.3) | 2004/01 → 2020/12 as climate data record, then extended to the present as an interim record (10-day latency); CLAAS-2.1, with the cloud type, ends on 31/12/2017 | CC BY 4.0 | candidate for the satellite mask of H2. Ordered through the CM SAF web interface, free, registration required; the order site offers reprojection and a sub-domain cut. The climate data record is 78.3 TiB in all; no size per file is documented (pages read on 9/11/2026) |
| [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) (Copernicus Climate Data Store) | reanalysis, hourly precipitation among other variables, 0.1° (about 9 km). Total precipitation `tp` (m) is accumulated from 00 UTC: the value at 00 UTC is the total of the previous day, and hourly amounts are differences of consecutive hours (checked on 1/7/2024: the domain mean grows through the day and drops at 01 UTC) | 1950 → now (to 4/11/2026 on 10/11/2026, CDS catalogue) | CC BY 4.0 | candidate pan-European bridge for the level correction, for levels and seasonal frequencies only ([roadmap.md](roadmap.md), H3); independent of OPERA. Downloaded with `scripts/fetch_cds.py` (*Derived datasets*); the CDS token goes in `.env` (`COPERNICUS_CDS_API_KEY`), and the dataset licence must be accepted once on the CDS website by the account |
| [CERRA-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-cerra-land) (Copernicus Climate Data Store) | regional land reanalysis for Europe, 5.5 km, Lambert conformal grid of 1069 × 1069. Total precipitation only as a daily analysis: the 24 h from 06 UTC of the previous day to 06 UTC of the stated day, by optimal interpolation of CERRA forecast precipitation and daily rain gauges ([data user guide](https://confluence.ecmwf.int/spaces/CKB/pages/278548151/CERRA-Land+surface+reanalysis+Data+User+Guide)); surface observations from ECA&D, MARS and national databases ([EMS2026-139](https://meetingorganizer.copernicus.org/EMS2026/EMS2026-139.html)) | 1/9/1984 → 31/12/2025 (CDS catalogue, 10/11/2026), extended twice a year (June and December). The original production ended in June 2021; the continuation to near real time comes from a new C3S contract, and whether it is homogeneous with the earlier part is not documented (EMS2026-139) | CC BY 4.0 | candidate pan-European bridge for H3, daily only; independent of OPERA. Known issue: 1/5/2021–31/7/2025 were packed with 12 instead of 24 bits per value (mostly snow variables; effect on precipitation not checked; 24-bit data announced for July 2026; data user guide, *Known issues*). The CDS cannot cut this grid, so `scripts/fetch_cds.py` downloads it whole (netCDF, about 160 MB a month) and keeps the window of cells that covers the domain. It is read from the ECMWF MARS archive, which runs one request per user and had 1181–1371 requests queued for 65 slots on 11/11/2026 (request status page of the CDS), so the script asks for a whole year at a time, newest year first, and picks up a request already queued instead of sending it again |
| [EMO-1](https://data.europa.eu/data/datasets/0bd84be4-cec8-4180-97a6-8b3adaac4d26?locale=en) (JRC, Copernicus Emergency Management Service) | gridded station observations for Europe by angular distance weighting, 1 arcmin (about 1.8 km); precipitation daily and 6-hourly, among other variables; no radar input | v3.0.0: 1990–2023 (EU data portal record, 10/11/2026). A version to 2024 is described in the preprint [essd-2025-723](https://essd.copernicus.org/preprints/essd-2025-723/), not yet in the catalogue | CC BY 4.0 (EMO-1 distribution) | a pan-European bridge independent of OPERA once 2024 is published; files on the [JRC FTP](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-EFAS/meteorological_forcings/) |
| [Natural Earth](https://www.naturalearthdata.com) 1:10m | country borders for the region masks | | public domain | |
