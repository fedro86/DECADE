# Three-dimensional convective–stratiform echo-type classification and convectivity retrieval from radar reflectivity

- **Authors, year, venue:** M. Dixon, U. Romatschke (NCAR), 2022,
  *Journal of Atmospheric and Oceanic Technology* 39, 1685–1704
- **Link:** https://doi.org/10.1175/JTECH-D-22-0018.1 · public copy on OSTI:
  https://www.osti.gov/pages/servlets/purl/1897074
- **Access:** free full text on OSTI (public access copy); © 2022 American
  Meteorological Society, reuse under the AMS copyright policy
- **Read:** full text of sections 1, 2, 3a–c, 3f, 4a, 5c and 6; the rest
  (subclassification, PECAN validation details, appendices) skimmed.

## What it is

The ECCO algorithm (Echo Classification from COnvectivity) separates
convective and stratiform radar echo from reflectivity texture: on each
horizontal plane, the standard deviation of the squared reflectivity within a
circle, after removing the local linear gradient. Texture is mapped to a
"convectivity" between 0 (stratiform) and 1 (convective). Built on Steiner et
al. (1995), but without their intensity rule. Validated in 3D on PECAN (U.S.
Great Plains) against lightning and GPM; also run on grids of the U.S., the
UAE, Australia and, in 2D, on the OPERA mosaic over Europe.

## Numbers we use

- **Texture:** TDBZ = √stdev(DBZ_adj²) over a circle (Eq. 4), with
  DBZ_adj = reflectivity − linear plane fit + kernel mean − DBZbase (Eqs. 1–3),
  negative DBZ_adj set to 0; DBZbase = 0 dBZ for S-, C- and X-band radars
  (section 3a). The plane fit is done only if at least 0.67 of the circle has
  valid (non-missing) reflectivity; a point is processed ("active") if it has
  valid reflectivity and at least 0.25 of the circle has.
- **Convectivity:** TDBZ ≤ 0 → 0, TDBZ ≥ 30 → 1, linear in between
  (section 3b, Fig. 3); TDBZ 15 corresponds to convectivity 0.5.
- **Classes:** convectivity < 0.4 stratiform, 0.4–0.5 mixed, > 0.5 convective
  (section 3c).
- **Texture radius:** 7 km on a 1 km grid; **8.5 km on the 2 km OPERA grid**
  (section 5c). On coarser grids TDBZ decreases, and the radius is increased
  (7 to 12.5 km from 1 to 5 km) to keep the convective fraction about constant
  (section 3f, Table 1).
- **Intensity check:** of the PECAN echo ≥ 42 dBZ (threshold of Powell et al.
  2016), 91.4% is convective, 7.5% mixed, 1.0% stratiform for ECCO (section 4a).

## Relevance to DECADE

The only source found that runs a convective/stratiform separation on the 2D
OPERA mosaic, i.e. a column-maximum reflectivity at 2 km like ODYSSEY and
CIRRUS degraded to 2 km. Its point for the bright-band question (H1, January
check): ECCO separates by horizontal texture, not by intensity, and the bright
band, smooth and planar, gets low convectivity even where reflectivity is high
(section 3b, Fig. 2; over the Gulf, bright band up to 40 dBZ classified
stratiform, section 5b). A texture measure is therefore a published way to
tell whether high-reflectivity pixels sit in smooth, widespread echo.

## Limits

- The OPERA test is qualitative and in summer only (14/7/2021, section 5c): no
  winter case and no score in 2D. The authors expect, without measuring, that
  skill persists in 2D because texture is computed on horizontal planes.
- The conclusions report cases where "the bright band itself is identified as
  convective" (section 6), left unsolved.
- Texture thresholds were set experimentally on U.S. data (section 3b).
