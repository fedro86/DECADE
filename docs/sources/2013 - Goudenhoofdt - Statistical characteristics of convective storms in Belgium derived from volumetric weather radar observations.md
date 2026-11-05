# Statistical characteristics of convective storms in Belgium derived from volumetric weather radar observations

- **Authors, year, venue:** E. Goudenhoofdt, L. Delobbe (RMI), 2013,
  *Journal of Applied Meteorology and Climatology* 52, 918–934
- **Link:** https://doi.org/10.1175/JAMC-D-12-079.1 · RMI record:
  https://orfeo.belnet.be/handle/internal/8922
- **Access:** paywalled (© American Meteorological Society); PDF obtained
  through the university
- **Read:** full text of sections 1–3 and of section 4c (area-averaged storm
  activity, pp. 918–926); the rest (storm properties, tracks) skimmed.

## What it is

Ten years (2002–2011) of 5 min volumetric reflectivity from the RMI C-band
radar at Wideumont (south-east Belgium), clutter-filtered, interpolated to a
0.5 km 3D Cartesian grid and processed with the TITAN storm tracker between 20
and 180 km from the radar: more than one million storms. Climatology of storm
frequency, coverage, size, duration and motion over Belgium.

## Numbers we use

- **40 dBZ, minimum volume 10 km³:** TITAN threshold for a convective storm;
  **45 dBZ, 5 km³** as a second, stricter one. With the NEXRAD relation
  Z = 300 R^1.4 they are 12 and 28 mm/h. The 40 dBZ value is linked explicitly
  to Steiner et al. (1995) (section 2d, p. 922).
- **Cell or system:** a storm whose 40 dBZ envelope area is below **100 km²** is
  a cell, above it a convective system; a cell is isolated if no other storm is
  within **10 km**; a system is linear if the eccentricity of its fitted ellipse
  exceeds 0.95 (section 3b, p. 923).
- **How often there is convection:** at least one storm somewhere in the study
  area (about 10⁵ km²) in **15%** of the 5 min times (12–20% by year), above 20%
  from May to August, about **35% in July–August**; over a reference area of
  10⁴ km², **6%** of the times and **14% in July–August** (section 4c,
  pp. 925–926).
- Storms mostly move towards the north-east, median speed 30 km/h; simple
  tracks last 25 min on average, complex ones 70 min (abstract).

## Relevance to DECADE

The Belgian reference for what "convective" means at RMI: supports 40 dBZ as
the convective threshold in H1 and D3, and the 100 km² cell/system limit is a
candidate scale for an area-based event label. The frequencies give a check for
a classification on OPERA: with Belgium at about 3 × 10⁴ km², the share of
times with convection should fall between the two areas above (about 6–15% over
the year, 14–35% in July–August), if the definitions were comparable.

## Limits

- Single radar and 3D volumes: the volume threshold (km³) has no equivalent on
  a 2D composite such as OPERA `DBZH`, so the frequencies are only a rough check.
- Period 2002–2011, before the OPERA archive used in DECADE.
- The values 35–36 dBZ quoted earlier from the authors' conference papers
  (ECSS 2009, ERAD 2010) were not checked here; this paper uses 40 and 45 dBZ.
