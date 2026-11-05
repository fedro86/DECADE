# Climatological characterization of three-dimensional storm structure from operational radar and rain gauge data

- **Authors, year, venue:** M. Steiner, R. A. Houze Jr., S. E. Yuter, 1995,
  *Journal of Applied Meteorology* 34, 1978–2007
- **Link:** https://doi.org/10.1175/1520-0450(1995)034<1978:CCOTDS>2.0.CO;2
- **Access:** paywalled
- **Read:** not the full text. Parameters from the Py-ART implementation
  ([`steiner_conv_strat`](https://pyart.readthedocs.io/en/latest/API/generated/pyart.retrieve.steiner_conv_strat.html))
  and from later studies that apply the method. Check the original before
  quoting exact values in a paper.

## What it is

The standard convective/stratiform separation for gridded radar reflectivity,
developed on a tropical radar (Darwin, Australia) with a 2 km horizontal grid
at a fixed height. A pixel is convective if it is a convective centre (above an
intensity threshold, or "peaked" above the mean of its background), or if it
lies within a convective radius of a centre; everything else with echo is
stratiform.

## Numbers we use

- **40 dBZ:** intensity above which a pixel is a convective centre. Py-ART uses
  42 dBZ by default; other studies use 30 dBZ.
- **11 km:** radius of the background used for the peakedness test (Py-ART
  default); other studies use 21 km.
- The convective radius grows with the background reflectivity (about 1 km
  below 25 dBZ to 5 km at 40 dBZ in one implementation).
- Classification at a fixed height (Py-ART: 3 km) to avoid the bright band.

## Relevance to DECADE

Candidate pixel classification for H1 (scores split by convective and
stratiform pixels) and for D3 (area of convective pixels per event). It works
on any grid, so it fits the pan-European constraint, and its 2 km design grid
is the ODYSSEY resolution.

## Limits

Built for a reflectivity field at a fixed height. OPERA `DBZH` is not at a
fixed height (see `docs/data.md`); an intense bright band can exceed 40 dBZ and
be classified as convective, a known weakness of the threshold
([NWS review](https://www.weather.gov/owp/oh_hrl_papers_2000mou_DJ_DJ00)).
Tropical origin: thresholds may need tuning for Belgian rain.
