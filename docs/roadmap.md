# Roadmap

The project specification: goals, plan, what is done and what is left, and the
decisions taken or still open. This is the only place for status. How the
built parts work is in [method.md](method.md); facts about the data are in
[data.md](data.md).

Update this page in the same pull request that completes or changes a task.

## Goal

DECADE (DEep-learning nowCasting from A harmonised DEcade of radar data),
12 months from 16/11/2026, HydroScan with the University of Basilicata, compute
on Leonardo Booster. The motivation is in the [README](../README.md).

### Research questions

1. **Harmonisation.** Can ODYSSEY be brought to 1 km / 5 min, by optical-flow
   interpolation plus a statistical correction, consistently with the current
   products, accurately enough for training and fast enough for the whole
   continent?
2. **Value of the data.** How much does pre-training on the legacy decade
   improve a model trained on the current products alone, and how much of the
   gain comes from harmonisation rather than from data volume?
3. **Hydrological value.** Does the best configuration improve rainfall
   accumulations and the detection of intense-rain thresholds on Belgian
   convective events, compared with STEPS and the Lucas-Kanade nowcast of
   Flood4Cast?

### Constraints

- **Only pan-European sources in the method** (OPERA, ECA&D, EURADCLIM), so that
  it scales to the whole OPERA domain. National products only as validation.
- **Belgium is the pilot.** Validation reference: open VMM radar products
  ([data.md](data.md), *Other sources*). Validation against private Belgian archives is run
  by their owners through the injectable `reader`.
- **Production runs on Leonardo Booster** (EuroHPC, CINECA) as Slurm batch
  jobs, without notebooks. Compute nodes have no internet access: all input
  data are copied to the cluster storage first ([usage.md](usage.md), *Running
  on Leonardo Booster*).
- The harmonised archive and the code are released openly.

## Work packages and status

### Setup on Leonardo Booster

- [ ] Copy the inputs to the cluster. Whole files: about 0.4 TB of ODYSSEY
  `DBZH_QIND` and 0.6 TB of CIRRUS `DBZH` (estimated from file counts and sizes
  in [data.md](data.md)), as much as the default `$WORK` quota; the Belgian
  crops are about 95 GB. Decide what to copy and where (`$WORK`, `$FAST`,
  quota extension).
- [ ] Python environment on Leonardo, built on the CINECA modules
  ([usage.md](usage.md), *Running on Leonardo Booster*): choose the modules
  (Python, CUDA, MPI, PyTorch from `cineca-ai`), pin the versions of
  `pyproject.toml` to what they provide, and add our packages on top (e.g. a
  virtual environment with `--system-site-packages`). Needed at the latest for
  the GPU version (WP1) and for training (WP3), which rely on the cluster's
  CUDA and interconnect libraries.
- [ ] Slurm job scripts for `downscale`, `sample` and `windows`, then for
  training (WP3).

### WP1 – Harmonisation of ODYSSEY

- [x] Reading of ODYSSEY (ODIM 2.0) and CIRRUS (ODIM 2.4), crops aligned to
  2 km, Belgium mask, download from the public bucket.
- [x] LK optical-flow interpolation to 1 km / 5 min with mass conservation
  (CPU, OpenCV).
- [x] Validation against CIRRUS on the only overlap, 1–5/7/2024
  ([method.md](method.md), *Results*).
- [x] Synthetic end-to-end test, run by CI.
- [x] Crops of Belgium + 350 km: ODYSSEY 2012–2024 and CIRRUS 2024–2026
  ([data.md](data.md), *Derived datasets*).
- [ ] Validation of the interpolation on CIRRUS alone: subsample CIRRUS to
  15 min, interpolate, compare with the real 5 min frames. Removes the product
  difference from the score and is not limited to 4 days.
- [ ] GPU implementation in PyTorch: gradients and local least squares as
  convolutions, warping with `grid_sample`, many pairs per batch. Must match the
  CPU version on the synthetic test.
- [ ] Outlier cleaning of ODYSSEY: threshold plus mask of persistent points
  ([data.md](data.md), *Known problems*), on the model of EURADCLIM.
- [ ] Statistical correction ODYSSEY → CIRRUS: seasonal quantile mapping of
  rain rates, wet-pixel frequency matched first. Estimated on matching seasons
  of different years, since the products do not overlap. Needed because the
  IRENE input normalisation is fixed (R → dBZ with Marshall-Palmer, clipped to
  [0, 60], scaled to [−1, 1]): a level gap between products
  ([data.md](data.md), *Known problems*) is not absorbed by the model.
- [ ] Consistency over 2012–2024: rain-rate distributions, wet-pixel frequency
  and accumulation maps year by year; break-point tests on monthly
  accumulations.
- [ ] Validation over Belgium against VMM: bias, QQ, FSS, power
  spectra, accumulations; baselines are plain regridding and linear time
  interpolation.
- [ ] Apply the time shift in production (see *Open decisions*).

### WP2 – Training data in IRENE format

- [x] Window sampler on ODYSSEY at 2 km (`sample`).
- [x] Zarr store of interpolated windows in IRENE format (`windows`).
- [ ] Group windows by time in production, so that each ODYSSEY frame is read
  and each motion field estimated once (today each window rereads all its
  ODYSSEY files, see [usage.md](usage.md), *Measured costs*).
- [ ] Window budget: tune `m`, `q_min`, `step_px`, `step_t` (the IRENE
  parameters give far too many windows, see [usage.md](usage.md), *Measured
  costs*).
- [ ] CIRRUS data for fine-tuning and test: conversion to R, same store format,
  split in alternating monthly blocks (e.g. one month in four for test, one for
  validation) with a few days of margin, so that the test covers all seasons.
- [ ] Raw ODYSSEY windows for configuration B (regridded only, 15 min steps).

### WP3 – IRENE training (configurations A, B, C)

IRENE architecture trained from scratch, evaluated on the same held-out Belgian
convective events from the current products:

| configuration | pre-training | fine-tuning | measures |
|---|---|---|---|
| A | none | current OPERA (from 7/2024) | baseline, about two years of data |
| B | raw ODYSSEY 2012–2024, regridded, 15 min | current OPERA | value of the legacy data without harmonisation |
| C | ODYSSEY interpolated to 1 km / 5 min and corrected | current OPERA | value of harmonisation |

A vs C is the value of the unlocked archive; B vs C isolates harmonisation.

**Learning curve on the years of pre-training (extension of C).** Variants of C
pre-trained on the last k years of harmonised ODYSSEY (years added backwards
from 2024), each with the same fine-tuning and the same total number of
training steps, so that the curve measures data diversity, not compute. A is
the point k = 0 and C the point k = 12. A non-stationarity control compares two
variants with the same number of years, old (2013–2014) against recent
(2022–2023). Each variant is scored before fine-tuning (distance between the
ODYSSEY and CIRRUS domains) and after (the number that decides). It shows how
many years are worth harmonising, which sets the cost of the European
extension (WP5).

The work runs in phases; each phase starts only if the compute budget left
allows it:

| phase | trainings | seeds | runs |
|---|---|---|---|
| 1 | A, B, C | 3 | 9 |
| 2 | C with k = 2 and k = 4, old/recent control | 1 | 3 |
| 3 | C with k = 1, 2, 4, 8, old/recent control | 3 | 15 (12 more than phase 2) |

- [ ] Data loader from the stores of WP2 into the IRENE code (ConvGRU-Ensemble).
- [ ] Multi-node data-parallel training on Leonardo Booster.
- [ ] Small run first, to measure the time and cost of one training and decide
  how many phases fit in the budget.
- [ ] Phase 1.
- [ ] Phase 2.
- [ ] Phase 3.

### WP4 – Verification

- [ ] STEPS and Flood4Cast LK nowcasts on the same events.
- [ ] Scores: CRPS, CSI and FSS in mm/h by lead time, volume bias, rainfall
  accumulations, intense-rain thresholds.
- [ ] Selection of Belgian convective events for the test set.

### WP5 – Costs and scaling

- [ ] Measured costs of harmonisation and training on Leonardo Booster, for a
  Regular Access proposal covering the whole OPERA domain. Current CPU costs are
  in [usage.md](usage.md).

## Decisions taken

- **Variable:** DBZH (maximum reflectivity) for both ODYSSEY and CIRRUS,
  converted to R with Marshall-Palmer.
- **Interpolated frames are flagged** with `alpha` (0 = real ODYSSEY frame).
- **Windows are chosen on ODYSSEY at 2 km**, and only the chosen windows are
  interpolated.
- **Output labels stay on ODYSSEY times** (shift 0), so that real frames remain
  real.
- **WP3 runs in phases** (A/B/C, then a reduced learning curve, then the full
  one), as far as the compute budget allows (decided 3/11/2026).

## Open decisions

- **Loss only on real frames?** The earlier plan computed the loss only on
  frames with `alpha = 0`. Configuration C is meant to test the interpolated
  5 min sequences: decide whether the loss includes interpolated frames.
- **Whole archive or selected windows?** The proposal releases a harmonised
  archive from 2012; the current pipeline interpolates only the sampled
  windows.
- **Time shift in production:** with shift 0 the labels keep the offset between
  the products' time windows ([data.md](data.md), *Time windows*).
- **Quality fields:** redo the Belgian crops with quality bands, at the same
  network cost?
- **Rain archive at 2 km / 15 min** (ODYSSEY `RATE`/`ACRR` plus NIMBUS, outlier
  cleaning, homogenisation of the two periods anchored to ECA&D gauges). Planned
  before DECADE, not in the proposal: parked unless decided otherwise.

## Open questions (external)

- How much does IRENE degrade with fewer years of data? Asked to the authors,
  answer unknown.
- Are there parallel ODYSSEY/NIMBUS or ODYSSEY/CIRRUS data beyond the 4 days in
  the public archive? To ask support.opera@eumetnet.eu.
- Which radars does CIRRUS extrapolate with LK (`how/comment`)? Presumably
  Spain, not verified.

## References

- IRENE: Camilletti et al., 2026, arXiv 2609.17175; model on HuggingFace
  `it4lia/irene`; code ConvGRU-Ensemble (FBK, IT4LIA AI Factory).
- Pulkkinen et al., EGU 2026: convolutional nowcasting on OPERA at
  2 km / 15 min.
