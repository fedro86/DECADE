# Skilful precipitation nowcasting using deep generative models of radar

- **Authors, year, venue:** S. Ravuri, K. Lenc, M. Willson, D. Kangin,
  R. Lam, P. Mirowski, M. Fitzsimons, M. Athanassiadou, S. Kashem, S. Madge,
  R. Prudden, A. Mandhane, A. Clark, A. Brock, K. Simonyan, R. Hadsell,
  N. Robinson, E. Clancy, A. Arribas, S. Mohamed, 2021, *Nature* 597, 672–677
- **Link:** https://doi.org/10.1038/s41586-021-03854-z · Supplementary
  Information from the same page
- **Access:** open, CC BY 4.0 (article, p. 677)
- **Read:** main text, Methods (Datasets, Training set preparation, Expert
  meteorologist study, Quantitative evaluation), Extended Data captions;
  Supplementary Information sections A.1 (importance sampling, Table 1) and C.1
  (evaluation by precipitation type). Architecture sections skimmed.

## What it is

DGMR, a GAN nowcasting model trained on the UK Met Office RadarNet composite
(1 km, 5 min, 2016–2018) and tested on 2019, with a US (MRMS) check. Verified
with CSI, CRPS, economic value, spectra and a study with 56 Met Office
forecasters.

## Numbers we use

- **Test set = a whole held-out year:** 2019, after training on 2016–2018
  (first day of each month as validation). Chosen to prevent leakage and test
  out-of-distribution generalisation (Methods, Datasets, PDF p. 7).
- **Rarity of heavy rain:** about 89% of UK grid cells have no rain; rain above
  4 mm/h is below 0.4% of grid cells (Methods, Training set preparation, p. 7).
- **Importance sampling** (SI A.1, eq. 6, Table 1): crop kept with probability
  q = min(1, q_min + m·mean(1 − exp(−R/s))). Training: s = 1 mm/h, m = 0.1,
  q_min = 2 × 10⁻⁴. Test: s = 10 mm/h, m = 1.0, q_min = 2 × 10⁻⁵, 512 × 512
  crops at 64-cell offsets; metrics on the central 64 × 64 cells and weighted
  back with importance weights. Test set: 66,851 crops (Methods, Quantitative
  evaluation, p. 9).
- **Significance:** every other week of the test year used as independent units
  (n = 26 weeks), paired permutation test (Methods, p. 9).
- **Intensity classes for the forecaster study:** "medium" rain above 5 mm/h and
  "heavy" rain above 10 mm/h (main text p. 675; Methods p. 9). The chief
  meteorologist picked 141 days of 2019 with medium-to-heavy rain; within them
  the 256 km crop with the largest fraction of cells above 5 or 10 mm/h was
  chosen automatically, excluding a 192 km border (Methods, p. 9).
- **Case studies:** three events "chosen by the chief meteorologist" as
  difficult for nowcasting: convective cells over eastern Scotland
  (24/6/2019), an intense front with decay (24/7/2019) and a slow cyclonic
  circulation (30/7/2019) (Methods p. 9; Fig. 1, Extended Data Figs. 2–3).
- **Verification thresholds:** CSI at 1, 4 and 8 mm/h (Fig. 2).
- **Rain-type labels** (SI C.1): test examples labelled by hand as frontal /
  non-frontal / mixed, coherent / non-coherent motion, scattered /
  non-scattered, then checked by a Met Office forecaster.

## Relevance to DECADE (D3)

Two models for D3. (1) An objective route: a full held-out period, with
rain-weighted sampling and fixed intensity thresholds (5 and 10 mm/h). (2) A
case-study route: a few events picked by an operational forecaster as
difficult, including at least one convective case. The 5 / 10 mm/h classes and
the 1 / 4 / 8 mm/h CSI thresholds are ready candidates for D3 intensity
criteria. The hand-made rain-type labels show that even DGMR did not classify
events objectively.

## Limits

UK composite, gauge-adjusted, rain rates capped at 128 mm/h. Case studies and
the 141 days rest on expert choice, not a written rule.
