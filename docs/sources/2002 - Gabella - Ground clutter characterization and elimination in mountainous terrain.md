# Ground clutter characterization and elimination in mountainous terrain

- **Authors, year, venue:** M. Gabella, R. Notarpietro, 2002, *Proceedings of ERAD 2002*, 305–311 (Copernicus GmbH)
- **Link:** [Internet Archive snapshot (9 Aug 2017)](https://web.archive.org/web/20170809110607/https://www.copernicus.org/erad/online/erad-305.pdf); original URL, now dead: https://www.copernicus.org/erad/online/erad-305.pdf
- **Access:** free copy via the Internet Archive; no licence stated
- **Read:** full text (7 pages)

## What it is

A short conference paper that proposes a simple texture-based filter to remove *residual* ground clutter and anomalous-propagation (anaprop) echoes from reflectivity maps. The filter is run after another clutter removal method (a static clutter map, or the MeteoSwiss Doppler decision tree) and works on polar or Cartesian data. It has two steps: a spatial-continuity test in a moving window, and a compactness test (area/perimeter) on connected echo groups. This is the method behind wradlib `classify.filter_gabella`.

## Numbers we use

**Test 1: spatial-continuity ("texture") test (Sect. 2)**

- 5 × 5 pixel window around each pixel (or bin, for polar data). The authors call it a compromise; they say a "3×3 window is too selective while a larger one would filter too weakly".
- Rule: the pixel is kept as weather when its difference to *np* surrounding pixels in the window is below a threshold (called *trvar* and *tr1* in the text). Otherwise it is flagged as clutter. The text does not say whether *np* means "at least np" or "exactly np" neighbours.
- tr1 ≈ 6 dB: not stated as a single explicit choice. The paper justifies it from Germann and Joss (2001): at about 1 km lag, even an Alpine mesoscale convective system shows an average variance of no more than 6 "dBZ" (unit as written in the paper).
- np: **no single chosen value is stated.** The value np = 8 appears only in the description of the Germann and Joss study (the 8 neighbours at ~1 km distance), not as the filter setting.
- "Acceptable" ranges: 3 dBZ ≤ tr1 ≤ 9 dBZ and 6 ≤ np ≤ 10. The authors say results do not change drastically inside these ranges. No sensitivity numbers are shown.

**Test 2: compactness (area/perimeter) test (Sect. 2)**

- Connected groups of non-zero pixels, 8-connectivity (diagonals included).
- R = (number of pixels in the group) / (number of boundary pixels of the group).
- Residual clutter groups often have R close to 1 ("verified in a number of radar maps"; no count given).
- tr2 = 1.3: groups with R below this are removed. The paper states that this implies the smallest accepted "compact" group has more than 11 pixels. The derivation is not shown, and the exact definition of a boundary pixel is not given.
- Known side effect: very small thunderstorm cells (lifetime about 30 min, a few km²) can be removed (Sect. 2).

**Data the method was developed and tested on (Sects. 3–4)**

- Two non-collocated C-band radars in NW Italy / southern Switzerland, mountainous terrain.
- Bric della Croce (710 m a.s.l., near Turin): non-Doppler, 1.54° beam, four 250 m bins averaged, resampled to a Cartesian 1 km grid. Clutter pre-removed with a static map (threshold = median daily cross-section).
- Monte Lema (1625 m a.s.l.): Doppler, 1° beam, 20 elevations in 5 min, 83 m raw gates, clutter pre-removed with the Joss and Lee (1995) decision tree (JL95), resampled to a Cartesian grid.
- Input to the filter: **single-radar** 5-min **maximum-reflectivity** (column-max) Cartesian maps, in dBZ. The authors note that the method is meant for constant-altitude data but still works on maximum-reflectivity maps.
- Test area: 180 × 150 km² (27 000 km², 180 × 150 pixels, so about 1 km pixels).
- Test days: clear sky 28 September 1996 (288 maps per radar, refractivity gradient −50 N units/km, slightly super-standard); rain 29 June 1997; rain 14 October 2000 (Lema with the modified algorithm GJ2002).

**Validation numbers (Sect. 5, Table 1; clear sky only)**

Metric: share of area with clutter giving an "equivalent" daily rain amount above a threshold.

| Clutter removal | Bric > 1 mm/day | Lema > 1 mm/day | Bric > 600 mm/day | Lema > 600 mm/day |
|---|---|---|---|---|
| None | 48% | 50% | 9.0% | 2.3% |
| Operational (static map / JL95) | 38% | 39% | 3.3% | 0.01% |
| Operational + texture | 14% | 0.3% | no pixel | no pixel |

- For Lema, after texture filtering no pixel exceeds 6 mm/day (Sect. 7).
- Inconsistency: for Bric, the Sect. 5 text gives the 14% for "> 6 mm/day", while Table 1 and Sect. 7 give it for "> 1 mm/day". Sect. 7 also calls the Bric radar "the non-Doppler radar" in a bullet about JL95, which is the Lema (Doppler) radar. These look like typos.
- Rainy days (Sect. 6, Fig. 4): qualitative only. The texture filter removed more residual clutter after the static map than after JL95, and less after GJ2002. No numbers.
- No measure of rain wrongly removed (false alarms), no rain-gauge comparison, no hit/miss statistics.

**Artefact types targeted**

- Residual ground clutter (non-stationary, spatially decorrelated) and anaprop echoes. Both tests rely on clutter being more spatially variable and less compact than rain.

## Relevance to DECADE

Ticket **H2 (#19)**: this is the primary source for the Gabella filter that EURADCLIM (Overeem et al. 2023) ran on the ODYSSEY composite via wradlib. It informs these H2 artefact types:

- **Fixed clutter**: yes, residual clutter is the stated target. The paper's design (run *after* another clutter removal) matches our case: ODYSSEY data were already quality-controlled by national services and OPERA.
- **Isolated echoes (speckle)**: yes, in practice. Small groups fail the compactness test (R < 1.3) and isolated pixels fail the continuity test. The paper does not name speckle explicitly.
- **Echoes without rain (anaprop)**: yes, anaprop is named as a target.
- **Interference spikes (RLAN/5 GHz), blocked sectors, impossible values**: not addressed by the paper.

**Paper vs wradlib defaults**

- Window 5 × 5: **same** as the paper.
- tr1 = 6 dB: **consistent** with the paper's reasoning (6 from Germann and Joss 2001), but the paper does not state 6 as an explicit setting; it gives the range 3–9.
- n_p = 6: **not stated in the paper.** It is the lower end of the paper's range 6–10. The paper's only np = 8 refers to the Germann and Joss study.
- tr2 = 1.3: **same** as the paper.

**Things to keep in mind on a 2 km multi-radar composite**

- Pixel size: tr1 was justified at ~1 km lag. On a 2 km grid the 5 × 5 window spans 10 × 10 km and neighbours are 2–4+ km away. Rain varies more over larger lags, so the same tr1 will flag more true rain edges and convective cells. To check on our data.
- Compactness: "more than 11 pixels" means more than ~11 km² at 1 km but more than ~44 km² at 2 km. Small convective cells are at greater risk than in the paper. The paper already warns about cells of a few km².
- Composite vs single radar: the paper used single-radar column-max maps. A multi-radar max composite adds seams between radar domains and mixed heights. The filter may flag pixels along seams as "texture". To check.
- Units: tr1 is in dB, so it fits our dBZ maximum-reflectivity composite. EURADCLIM converted its rain rates back to Z with Z = 200 R^1.6 before the filter (Overeem et al. 2023, section 3.1).
- No-data handling: the paper does not say how missing pixels, QIND-flagged pixels, or pixels outside radar coverage enter the window counts. This must be decided and documented for our run.
- wradlib semantics, checked in the source of version 2.9.8: test 1 counts the neighbours in the window that are less than `tr1` *below* the centre (higher neighbours always count as similar) and flags the pixel when the count is below `n_p`; `cartesian=True` is needed for a Cartesian grid. How test 2 counts boundary pixels was not checked.

## Limits

- Developed on two C-band radars, about 1 km Cartesian single-radar column-max maps, in Alpine terrain, 1996–2000. Our data: 2 km, 15 min, multi-radar OPERA composite, mostly flat Belgium, 2012–2024.
- Parameter values are justified by one external study (Germann and Joss 2001) and by visual checks, not by an optimisation. No sensitivity numbers for the stated ranges.
- Validation covers only clear-sky clutter reduction (Table 1) on one day per radar. Rainy days are qualitative only. Loss of real rain is not measured.
- Some inconsistencies in the text (6 vs 1 mm/day for Bric; radar names in Sect. 7) and an unstated np value.
- Does not handle RLAN spikes, beam blockage, or physically impossible values. Other methods are needed for those H2 types.
- Static/permanent clutter in a long time series is not its focus; the paper treats it as post-processing after a static or Doppler filter.
