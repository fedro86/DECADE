# The threat to weather radars by wireless technology

- **Authors, year, venue:** Saltikoff, E., Cho, J. Y. N., Tristant, P., Huuskonen, A., Allmon, L., Cook, R., Becker, E. and Joe, P. (2016), Bulletin of the American Meteorological Society, 97(7), 1159–1167
- **Link:** [10.1175/BAMS-D-15-00048.1](https://doi.org/10.1175/BAMS-D-15-00048.1)
- **Access:** free copy in the NOAA repository (https://repository.library.noaa.gov/view/noaa/15308); publisher terms apply
- **Read:** full text

## What it is

A short review article on how wireless devices (Wi-Fi/RLAN and similar, called WDs in the paper) interfere with weather radars, mostly at C band near 5.6 GHz. It describes what the interference looks like, gives cases from the USA, Europe (OPERA), South Africa, Canada, Australia and Japan, and reviews mitigation: regulation (dynamic frequency selection, DFS), signal processing, image processing and changes of band. Its main message is that removing the interference after the fact is not a lasting solution; keeping devices off radar frequencies is.

## Numbers we use

- Look of the artefact: interference shows up as "dots, spokes, or stripes" in the radar image (p. 1159, introduction).
- Geometry: a continuous-wave emitter gives a line pointing radially to the radar centre (p. 1160, Fig. 1). An emitter close to the radar can affect a sector up to several tens of degrees wide (p. 1160, section "Deteriorating quality of radar images").
- Intensity: some interference echoes are stronger than the strongest typical weather echoes (Fig. 1 caption, p. 1160; Fig. 2 caption, p. 1161). So a simple reflectivity threshold cannot separate them from storms.
- Persistence: in two images 10 min apart (Argentina) the interference changes from image to image, so blocking fixed radials does not work (Fig. 2, p. 1161). Mobile emitters (ships, planes, trains) give intermittent interference (p. 1162).
- Duration per event: a device that detects the radar still finishes its packet sequence, which takes tens to hundreds of milliseconds, and can interfere over several degrees of azimuth and elevation meanwhile (p. 1164, section "Attempts to share frequencies and mitigate disturbances").
- Canadian tests: interference can also appear as a raised noise level, i.e. a loss of sensitivity, not only as visible strobes; mitigation would need a noise filter that changes from ray to ray (p. 1164).
- Frequency: C-band weather radars at 5.60–5.65 GHz (TDWR band, and the band protected by the 10-min channel check in ETSI EN 301 893). RLANs were allowed in 5.150–5.350 and 5.470–5.725 GHz by WRC-03, on condition of using DFS (initial channel check 60 s) (p. 1163). Most reported cases are C band, with a growing number at S band (p. 1159).
- OPERA: 175 C-band and 31 S-band radars (OPERA website, Dec 2014) (p. 1162). Most OPERA members have seen growing RLAN interference on C-band radars since 2006 (p. 1162).
- European case counts: ECC Report 192 (2014) analysed more than 200 interference cases reported in 2012. Almost all came from illegal use or non-compliant equipment, and over 50% of 5-GHz RLANs on the European market were non-compliant (pp. 1162–1163). No per-country breakdown is given; Belgium is not mentioned.
- Detection/removal methods mentioned, with the input each needs:
  - Dual-polarization identification of RLAN signals from polarization properties (Keränen et al. 2013; Husnoo and Sugier 2014) (p. 1160). Needs dual-pol moments at the single radar.
  - Image processing on the "unnatural" shape of the signal (Peura 2002); a bad radial is removed and weather is interpolated from neighbouring radials, losing the weather inside it (p. 1160). Works on single-radar polar data (radials). The paper does not describe it for composites.
  - Signal-processing filters at the receiver (p. 1160); single-pulse filters like the TDWR one do not work against high-duty-cycle devices (Cho 2011) (p. 1163). Needs raw radar signal.
  - South Africa: a software filter removed most interference but also removed weather echoes; Fig. 3 shows precipitation lost even when no interference was present (p. 1161, p. 1164). The service moved to S band in 2011.
  - Non-processing options: DFS/regulation, X-band gap-fillers for a permanently affected sector, band changes (pp. 1163–1166).
- Limit of removal: when many emitters are present, too few clean radials remain for interpolation (p. 1160, Fig. 2). The conclusions say processing helps with one or a few disturbances but is not a permanent fix (p. 1166).

## Relevance to DECADE

H2 (#19), artefact type "radial spikes from 5 GHz interference". The paper confirms this artefact is real and widespread in the OPERA C-band network from 2006 onwards, with >200 cases reported in Europe in 2012, which falls inside our 2012–2024 period. It tells us what to look for: narrow lines or wider sectors along a radial from a radar site, which change between scans and can be as strong as heavy convection. In a composite these would appear as straight lines radiating from the position of one contributing radar; this is our inference, the paper does not discuss composites. It does not give a removal method usable on a 2D composite: all methods cited need polar data, dual-pol variables or the raw signal. The one image-processing route (Peura 2002) is described per radial, so it would have to be adapted to a composite grid by us, and that adaptation would need its own support from the literature or from Federico. The paper also warns that filters can remove real precipitation (Fig. 3), so any cleaning step should be checked for loss of weather echoes. It says nothing about the QIND quality field.

## Limits

- Review and policy paper: no algorithm, thresholds or validation scores for detection.
- All cited removal methods work on single-radar polar data or signal level; none on a composite. The OPERA ODYSSEY composite is not discussed.
- No Belgium-specific information and no per-country or per-year counts beyond the 2012 ECC figure.
- Examples are from TDWR (USA), Argentina and South Africa, not from OPERA radars.
- It is unclear from the text whether compositing (e.g. overlap with other radars) hides or keeps such spikes; the paper does not address this.
- The persistence information is qualitative (one 10-min image pair); no statistics on how long spikes last.
