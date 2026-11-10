# Precipitation Nowcasting with Orographic Enhanced Stacked Generalization: Improving Deep Learning Predictions on Extreme Events

- **Authors, year, venue:** G. Franch, D. Nerini, M. Pendesini, L. Coviello,
  G. Jurman, C. Furlanello, 2020, *Atmosphere* 11, 267
- **Link:** https://doi.org/10.3390/atmos11030267 · copy used: University of
  Trento repository (https://iris.unitn.it/handle/11572/254258)
- **Access:** open, CC BY 4.0 (p. 19)
- **Read:** sections 1, 2.1–2.4 (data, splits, test set), 3 (results, CSI table)
  and 5 (conclusions); model details skimmed.

## What it is

FBK work (the IRENE group) on the TAASRAD19 archive of the Mt. Macaion radar
(Trentino, 500 m, 5 min, 2010–2019). An ensemble of TrajGRU models plus a
stacked model with orographic features, aimed at extreme rain rates, compared
with S-PROG.

## Numbers we use

- **Split by time** (section 2.1, p. 4): 2010–2016 for the ensemble, 2017–July
  2019 for the stacked model.
- **Test set chosen by impact list** (section 2.4, p. 8): 30 days drawn from
  "the list of days with extreme events" for 2017–2019 compiled by
  Meteotrentino (the regional weather service): 6,840 sequences, 9% of the
  data. The selection of the 30 days within the list is a sample; no further
  rule is given.
- **Sequences:** daily chunks of at least 25 frames (2 h) with precipitation
  (section 2.1, p. 4).
- **Rain-rate classes** used to describe the data (Fig. 6, p. 8): below 0.5,
  0.5–2, 2–5, 5–10, 10–30 and at least 30 mm/h, named hardly noticeable, light,
  light to moderate, moderate, heavy, extreme. Each class from 5 mm/h upwards is below 1% of
  pixels in each of the three sets.
- **CSI thresholds** up to 20 and 30 mm/h for "very heavy rain rates"
  (Table 2 and section 3, p. 12).
- Data capped at 52.5 dBZ, about 70 mm/h with Marshall-Palmer (section 2.1).

## Relevance to DECADE (D3)

A precedent, from the IRENE group, for choosing test days from an official
list of extreme-weather days kept by the national or regional weather service.
For D3 the Belgian analogue would be RMI warnings or reports. The 10 and
30 mm/h class limits give literature-backed intensity classes.

## Limits

Single mountain radar, not a composite. The Meteotrentino list is not public in
the paper and its criteria are not given.
