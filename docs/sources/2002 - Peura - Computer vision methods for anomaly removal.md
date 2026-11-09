# Computer vision methods for anomaly removal

- **Authors, year, venue:** M. Peura, 2002, *Proceedings of ERAD 2002*, 312–317 (Copernicus GmbH)
- **Link:** [Internet Archive snapshot](https://web.archive.org/web/2023/https://www.copernicus.org/erad/online/erad-312.pdf) (original URL, now dead: https://www.copernicus.org/erad/online/erad-312.pdf)
- **Access:** free copy via the Internet Archive; no licence stated
- **Read:** full text (6 pages)

## What it is

A conference paper from the Finnish Meteorological Institute (FMI). It describes a set of image-processing detectors for non-precipitation echoes in single-radar data, built from generic tools (median and morphological filters, flood-fill segment size, run lengths) and soft fuzzy membership functions. Each detector writes a probability of anomaly into a common anomaly map; removal is a separate step, done by thresholding that map at a chosen level.

## Numbers we use

All detectors below work on one radar at one time. The paper calls the working image a "B-scan": the polar scan drawn as a rectangle, with beam direction on one axis and range on the other. No detector uses a time sequence. The worked example is one case: FMI Korppoo radar, 9 July 2002, 04:30 EET, lowest sweep (0.5°) (Fig. 1).

- **Fuzzy functions (Sec. 2.4, Fig. 3):** a soft peak δ(x,a) = a²/(a²+x²) and a soft threshold σ(x,a). In the extracted text σ reads x/(a+|x|), but the plot runs from 0 to 1, so the exact normalisation is unclear. The parameter *a* is a half-width (steepness). These are generic and work on any image.
- **Ship example rule (Sec. 2.4):** segment size about 8 pixels (at least 4–12) and maximum intensity above 40 dBZ means "probably a ship". It is given to motivate fuzzy logic. It is unclear whether SHIP actually uses these values.
- **Median filter (Sec. 2.1):** a generic mask operator for outliers (e.g. ships) and speckle. No window size is given. Works on any 2D image.
- **Morphology and run lengths (Sec. 2.2–2.3, Fig. 2):** erosion/dilation as the n-th value of the mask histogram; opening and closing; elongated masks give direction-weighted results. Run lengths are the horizontal or vertical length of a segment. No sizes given. Generic 2D tools; in the paper, horizontal means along the beam in the B-scan.
- **BIOMET (Sec. 3.1):** birds and insects near the radar (low, widespread, speckled). Probability = σ(f′ − f, Δf) · σ(h′ − h, Δh), with f′ = −5 dBZ, Δf = 10 dBZ, h′ = 2500 m, Δh = 500 m. Needs the beam height h at each bin, so it works on the polar scan with known radar geometry. The author presents it as a preliminary detector, not a full bird detector.
- **SPECK (Sec. 3.2):** speckle noise and isolated specks. Segment size by flood-fill; size threshold Δs = 12 pixels (bins) at 50 % anomaly probability. Applied in the B-scan in the paper, but the method itself (connected-segment area) has no polar dependence. Preferred to median filtering because it does not distort other details and gives a separate detection image.
- **EMITTER (Sec. 3.3, Fig. 4):** external emitters seen as straight radial line segments. Hypotheses: segment length at least *a* pixels along the beam, width at most *w* pixels (= degrees), and short beam-wise segments raise the probability for the whole direction. Fig. 4 shows segments of width 1°, thresholded per-beam averages, and horizontal minus vertical run lengths. Numeric values of *a* and of the per-beam threshold are not given. Needs polar (B-scan) geometry, because a radial becomes a horizontal line only there.
- **SUN (Sec. 3.3):** the sun spike. Same as EMITTER, but thicker segments are allowed and the per-beam confidence holds only a precomputed peak in the sun direction. No numbers given. Needs polar geometry, radar location and time.
- **SHIP (Sec. 3.4, Fig. 5):** ships and aircraft as small, strong, separate spots, often with sidelobes perpendicular to the beam. Steps shown: high-boost filtering for suspicious pixels, pruning of horizontal (radial) segments, matching of synthetic sidelobes. No thresholds given; the author says there is no room to explain it in detail. Runtime: under a few seconds per radar volume on a 2002 Pentium. Needs polar geometry (sidelobes defined relative to the beam).
- **VERT_GRAD (Sec. 3.5; not operational):** sea clutter and ducting/anaprop. Vertical reflectivity gradient between sweeps, weighted inversely by altitude, computed from the lowest dBZ seen so far. 50 % limits: 3500 m altitude and −10 dBZ per 1000 m. Needs a multi-elevation polar volume.
- **METEOSAT (Sec. 3.5; not operational):** echoes in areas that are too warm for precipitation. Uses satellite temperature: 50 % confidence at −5 °C, 75 % at 0 °C. Small specks are masked first because satellite resolution is too coarse. Needs external satellite data.
- **DOPPLER (Sec. 3.5; not operational):** insects, bird flocks, some sea clutter as discontinuities in radial velocity. Continuity checked in a 3×3 pixel window. Needs Doppler velocity data.
- **Removal (Sec. 4, Fig. 7):** default is to cut detected pixels. Where anomalies and rain mix, the paper suggests filling from neighbouring non-anomalous pixels with median-type filters, using filters elongated perpendicular to elongated anomalies. Fig. 7 shows all detectors combined at 75 %, 50 % and 40 % thresholds, as a POD/FAR-type trade-off chosen by the user.
- **Operational context:** FMI software, in operational use since May 2002 (Abstract). Detectors marked as under development and not operational: VERT_GRAD, METEOSAT, DOPPLER (Table 1).
- **Evaluation:** qualitative only. One case is shown (Figs. 1, 6, 7). The author judges EMITTER, SUN and SHIP satisfactory and BIOMET good at detecting presence of birds/insects (Sec. 5). No POD, FAR or other scores are reported.

## Relevance to DECADE

Informs H2 (#19), the cleaning of artefacts from the OPERA ODYSSEY 2 km / 15 min maximum-reflectivity composite. It is the paper Saltikoff et al. (2016) cite for removing interference radials by image processing; here that is the EMITTER detector.

Mapping to the H2 artefact types:
- **Isolated echoes (speckle):** SPECK (segment area, 12-pixel limit at 50 %) and median filtering.
- **Interference spikes (RLAN/emitters):** EMITTER; SUN for sun spikes.
- **Echoes without rain:** BIOMET (biological), SHIP (ships), VERT_GRAD (sea clutter, anaprop/ducting).
- **Impossible values, fixed clutter, blocked sectors:** not covered by this paper.

What could run on our 2D Cartesian multi-radar composite as written:
- SPECK (connected-segment size), median filtering, morphology, run lengths, the fuzzy functions, the probability-map-plus-threshold design, and median-type infill for removal. These are plain 2D image operations. The 12-pixel limit was set on polar bins, not on 2 km grid cells, so the right value for our grid is open.

What needs polar single-radar geometry or data we do not have:
- EMITTER, SUN and SHIP rely on the B-scan, where a beam is a row of pixels. BIOMET needs beam height per bin. VERT_GRAD needs several elevations. DOPPLER needs radial velocity. METEOSAT needs satellite data.

Adapting a polar operator to the composite (for example, re-sampling the composite into polar coordinates around each Belgian or neighbouring radar site to look for radials) would be our own assumption. The paper does not describe or test it.

The idea of storing per-detector anomaly probabilities and thresholding them later is close to how we could combine our filters with QIND. That link is ours, not the paper's.

## Limits

- Everything is designed and shown on single-radar polar data from Finland (one sweep or one volume), not on a composite.
- In a maximum-reflectivity composite, an artefact from one radar can win over rain from another, and radials from different radars overlap. The paper does not address this.
- Key thresholds for EMITTER (*a*, *w* beyond the 1° shown), SUN and SHIP are not given, so these detectors cannot be reproduced from the paper alone.
- The σ formula is ambiguous in the available text.
- Evaluation is one qualitative case, with no scores. The positive verdict is the author's own judgement.
- Parameters were tuned for Finnish conditions (2002 hardware, Baltic sea clutter, local bird seasons). They may not suit Belgium in 2012–2024 or 5 GHz RLAN interference, which the paper does not mention by name.
- Three of the eight detectors were not operational at the time.
