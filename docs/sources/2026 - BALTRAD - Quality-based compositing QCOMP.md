# Quality-based compositing: QCOMP

- **Authors, year, venue:** BALTRAD cookbook (web page), maintained by the
  BALTRAD partnership; undated, read 17/11/2026
- **Link:** [baltrad.github.io/cookbook/cookbook_QCOMP](https://baltrad.github.io/cookbook/cookbook_QCOMP)
- **Access:** open web page, no PDF
- **Read:** full page

## What it is

The BALTRAD documentation of the quality-control modules of the toolbox and
how their quality indices combine into a total quality index for compositing.

## Numbers we use

- **Modules and status at Odyssey:** `ropo` (anomaly detection and removal)
  and `hac` (hit-accumulation clutter filtering) are both described as
  "operational at Odyssey"; `beamb` (beam-blockage analysis and correction) was
  validated in early 2012 in the trial of the BALTRAD toolbox for Odyssey.
- **Origin of `hac` in BALTRAD:** implemented in the toolbox under OPERA WP3.6
  task 4 (Michelson and Henja 2013, working document WD_2012_02p), i.e. the
  Odyssey clutter filter of 2011 (Scovell et al. 2013) was ported to BALTRAD
  in 2013.
- The page does not describe the satellite filter and gives no production
  dates.

## Relevance to DECADE

PR #96: links the module names in the OPERA documents (`hac`, `bropo`,
`beamb`) to their BALTRAD descriptions, and dates the `beamb` validation for
Odyssey to early 2012, well before its use in production at the end of 2015.

## Limits

Toolbox documentation, not a production log: "operational at Odyssey" is not
dated.
