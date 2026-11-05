# Climatological characterization of three-dimensional storm structure from operational radar and rain gauge data

- **Authors, year, venue:** M. Steiner, R. A. Houze Jr., S. E. Yuter, 1995,
  *Journal of Applied Meteorology* 34, 1978–2007
- **Link:** https://doi.org/10.1175/1520-0450(1995)034<1978:CCOTDS>2.0.CO;2
- **Access:** paywalled (© American Meteorological Society); PDF obtained
  through the university
- **Read:** full text of sections 1, 4, 5 and 6 (pp. 1978–1988), from a scanned
  PDF; sections 7–11 (vertical structure, rain rates, gauge adjustment) not
  read. Py-ART values below are from its documentation, not from the paper.

## What it is

The standard convective/stratiform separation for gridded radar reflectivity.
One month of data (Darwin, Australia, February 1988, 106 volume scans) from a
single radar, gridded to 2 km horizontal / 1.5 km vertical; the separation is
applied to the reflectivity at 3 km altitude. Convective centres are found by
intensity or by peakedness above a background; an area around each centre is
added; every other echo is stratiform.

## Numbers we use

- **Intensity: ≥ 40 dBZ** makes a grid point a convective centre, "since rain
  of this intensity could practically never be stratiform" (section 6c,
  p. 1985). Py-ART's `steiner_conv_strat` uses 42 dBZ by default.
- **Background:** linear mean in Z (mm⁶ m⁻³) of the non-zero echoes within an
  **11 km radius** (about 400 km²; 388 km² on the 2 km grid) (section 6c,
  p. 1985; section 6d, p. 1988).
- **Peakedness:** a point is also a centre if it exceeds the background by ΔZ
  (dB), with background Z_bg in dBZ (Eq. 2 and Fig. 7, p. 1986):
  ΔZ = 10 for Z_bg < 0; ΔZ = 10 − Z_bg²/180 for 0 ≤ Z_bg < 42.43;
  ΔZ = 0 for Z_bg ≥ 42.43. Tuned by eye against vertical cross sections and
  the bright band in 18 of the 106 volumes.
- **Convective radius** around each centre, growing with Z_bg (Fig. 6b,
  "medium" curve, read from the figure): 1 km below 25 dBZ, then 2, 3, 4 km in
  steps of 5 dBZ, 5 km from 40 dBZ.
- **Result with these settings** (case 2d: 2 km grid, 11 km background,
  medium radius): convective = 12% of the echo area and 59% of the monthly
  rain volume (Table 3, p. 1988). Only the centre pixels (no radius): 3% and
  38%; the large radius: 16% and 62%.

## Relevance to DECADE

Pixel classification for H1 (scores split on convective and stratiform pixels)
and, through the area of convective pixels, the event label for D3. It needs
only a 2D reflectivity field, so it fits the pan-European constraint, and its
design grid (2 km) is the ODYSSEY resolution.

## Limits

- **Grid resolution matters:** run on a finer grid than it was designed for,
  the method "identifies too much area as convective", and vice versa
  (section 6d, p. 1988). On CIRRUS at 1 km it should be applied after
  degrading to 2 km, or retuned.
- **Retuning:** the intensity and peakedness criteria may need changes for
  another climate or radar; the convective radius depends mainly on the grid
  resolution (p. 1987).
- **Height:** applied at a fixed 3 km altitude to stay below the tropical 0 °C
  level and avoid the bright band. OPERA `DBZH` is a maximum-reflectivity
  composite, not a constant-altitude field; in mid-latitudes the bright band can
  exceed 40 dBZ and be labelled convective, mostly in the cold season. The
  paper uses the bright band only as a check, not as a criterion (p. 1985).
- Tropical, single-radar, one-month tuning.
