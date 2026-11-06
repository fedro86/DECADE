# Maximum Reflectivity Composite: Configuration of CIRRUS relative to ODYSSEY

- **Authors, year, venue:** M. Radojevic (Météo-France) on behalf of OPERA,
  technical specification as of 25 June 2024, EUMETNET OPERA, edition 2.0
- **Link:** [OPERA5_Report_Cirrus-vs-Odyssey_Ed-2.0.pdf](https://eumetnet.eu/wp-content/uploads/2024/06/OPERA5_Report_Cirrus-vs-Odyssey_Ed-2.0.pdf)
- **Access:** open (no licence stated)
- **Read:** full text (3 pages)

## What it is

A short note comparing the two OPERA maximum reflectivity composites produced
at Météo-France: CIRRUS (1 km, every 5 min) and the older ODYSSEY line (2 km,
every 15 min). It lists domain, update cycle, availability, time window, radar
database, production software and compositing method.

## Numbers we use

- **Time window** (section *Reference period*): CIRRUS uses the scans in
  (NT−10, NT], ODYSSEY those in [NT−10, NT+5]. Both agree with the windows
  declared in the files ([data.md](../data.md), *Time windows for the label
  NT*).
- **Table 3** gives as "selection criterion for scanning interval" NT−10 to NT
  for CIRRUS and **NT−9 to NT+9** for ODYSSEY. The ODYSSEY value disagrees with
  the text and with every ODYSSEY file checked; the note does not explain it.
- **Compositing** (section *Compositing method*): the same maximum-value method
  for both; each Cartesian pixel takes the maximum of all contributing polar
  pixels, with its quality index. The note refers to Saltikoff et al. (2019) for
  details, and neither says whether several volumes of one radar inside the
  window contribute.
- **Spanish radars** (Table 2): data every 10 min, extrapolated forward in time
  with pysteps optical flow in CIRRUS.
- **Software** (Table 3): CIRRUS uses BALTRAD 2022 and a 2023 satellite filter;
  ODYSSEY uses BALTRAD 2013 and a 2018 satellite filter. ODYSSEY has not been
  updated since December 2022 (Table 1 caption).

## Relevance to DECADE

The source of the time windows in [data.md](../data.md), and therefore of the
offset between ODYSSEY and CIRRUS labels handled in H6. It also shows that the
two products differ in pre-processing and radar list, not only in resolution.

## Limits

A configuration note, not a method description. Table 3 contradicts the text on
the ODYSSEY window; we follow the text because the file metadata agree with it.
