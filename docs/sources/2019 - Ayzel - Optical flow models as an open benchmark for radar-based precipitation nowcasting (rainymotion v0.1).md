# Optical flow models as an open benchmark for radar-based precipitation nowcasting (rainymotion v0.1)

- **Authors, year, venue:** G. Ayzel, M. Heistermann, T. Winterrath, 2019,
  *Geoscientific Model Development* 12, 1387–1402
- **Link:** https://doi.org/10.5194/gmd-12-1387-2019
- **Access:** open, CC BY 4.0 (p. 1387)
- **Read:** sections 1, 3 (data, events, metrics) and 4 (results), Table 2;
  model descriptions skimmed.

## What it is

The rainymotion optical-flow library, benchmarked against the DWD operational
RADVOR nowcast on the DWD RY composite (1 km, 5 min). Its event set is the one
later reused to test RainNet (Ayzel et al. 2020).

## Numbers we use

- **Event set** (section 3.1 and Table 2, p. 1393): 11 events, summers 2016 and
  2017, chosen to cover a range of intensity, spatial coverage and duration.
- **Event properties in Table 2:** duration 2 to 23 h; maximum rain extent
  about 64,000 to 254,000 km²; share of the rain area above 1 mm/h 42 to 77%.
  An event is a start and end time, not a fixed window.
- **Verification thresholds:** CSI at 0.125, 0.25, 0.5, 1 and 5 mm/h,
  following Bowler et al. (2006) and Foresti et al. (2016) (section 3.2,
  p. 1394).
- **Finding:** fast loss of skill for events with high rain intensity, for all
  optical-flow models (section 6, conclusions).

## Relevance to DECADE (D3)

Gives the three properties (duration, maximum extent, share above 1 mm/h) to
tabulate for each D3 event, and shows that published event sets report them.
The ranges are for German summer events and can be used as orders of magnitude
for event extent and duration.

## Limits

No numeric selection rule; the ranges describe the chosen events, they are not
criteria. Extents are for the whole German domain, larger than Belgium.
