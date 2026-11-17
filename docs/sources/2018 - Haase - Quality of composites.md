# Quality of composites

- **Authors, year, venue:** G. Haase and D. Johnson (SMHI) on behalf of
  EUMETNET OPERA, OPERA 4 work package OD12, dated 15 May 2018 (cover sheet
  12/10/2018), posted by EUMETNET in January 2019
- **Link:** [eumetnet.eu](https://www.eumetnet.eu/wp-content/uploads/2019/01/Quality_of_composites_OPERA.pdf)
- **Access:** open (no licence stated)
- **Read:** full text (12 numbered pages after two cover sheets). The appendix
  with the monthly maps is not in the PDF: the report says it is available at
  SMHI on request (page 12).

## What it is

A monitoring study of the ODYSSEY precipitation-intensity composites (2 km,
15 min) for 2015–2017: monthly hit fractions, an automatic clutter
classification from the distribution of hit fractions, and a daily comparison
with the MESAN analysis (gauges plus model, no radar). It looks for jumps in the
monthly series that point to changes in the ODYSSEY processing.

## Numbers we use

- **QC in the composites** (section 2.1, pages 1–2): the composites are
  corrected for beam blockage with BALTRAD `beamb` and clutter-filtered with
  BALTRAD `bropo` and satellite imagery. No start dates are given here.
- **Change at the end of 2015** (section 3.1, page 5, Fig. 6): the monthly
  clutter fraction (pixels > 0.0 mm/h) drops by more than 10 % at the beginning
  of 2016, after a temporary minimum in December 2015; the authors tie it to "a
  new clutter removal and beam blockage correction in Odyssey". The fraction
  rises slightly in 2017. For pixels > 0.1 mm/h the clutter fraction is low and
  stable, so most of the clutter removed was ≤ 0.1 mm/h.
- **No effect on the bias** (section 3.2, page 8, Fig. 8): the end-2015 change
  did not change the OPERA−MESAN bias, probably because the clutter removed was
  weak.
- **Other dated events** (section 3.2, pages 7–8): artefact circles around the
  Danish radars Stevns (gone 9/2017) and Sindal (gone 5/2017); possible
  over-correction of beam blockage at Bømlo, Norway (2017). Nothing is reported
  for Belgium.
- **Not dated here:** the satellite filter, the hit-accumulation filter, bRopo,
  the 3/2017 input change, and anything in 2018 (the series ends in 12/2017).

## Relevance to DECADE

PR #96 (QC changes in ODYSSEY): independent evidence, from the composites
themselves, of a processing change at the turn of 2015–2016 that mainly removed
weak echoes. This matches our step at 12/2015 in timing; it was seen as a
drop in weak-echo frequency, not as a change of the rain amount.

## Limits

Statistics over the whole OPERA domain, rain-rate product only (not the
maximum reflectivity we use), 2015–2017 only. It does not say which of the two
new methods (satellite filter or beam blockage) caused the drop; the text says
"new clutter removal", which Saltikoff et al. (2019) identify as the satellite
filter.
