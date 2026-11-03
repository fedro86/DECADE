# Roadmap

The project specification: goals, plan, what is done and what is left, and the
decisions taken or still open. This is the only place for status. How the
built parts work is in [method.md](method.md); facts about the data are in
[data.md](data.md).

Update this page in the same pull request that completes or changes a task.

## Goal

DECADE (DEep-learning nowCasting from A harmonised DEcade of radar data),
HydroScan with the University of Basilicata, compute on Leonardo Booster. The
motivation is in the [README](../README.md).

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

- **Only pan-European sources in the method** (OPERA, EURADCLIM, ERA5-Land), so
  that it scales to the whole OPERA domain. National products only as validation,
  unless the level correction decides otherwise (*Open decisions*, bridge).
- **Belgium is the pilot.** The harmonised archive is produced and released for
  Belgium + 350 km; the European extension comes later and needs pan-European
  references. Validation references: VMM and RADCLIM ([data.md](data.md),
  *Inventory of sources and licences*). Validation against private Belgian
  archives is run by their owners through the injectable `reader`.
- **Production runs on Leonardo Booster** (EuroHPC, CINECA) as Slurm batch
  jobs, without notebooks. Compute nodes have no internet access and a job lasts
  at most 24 hours, so long runs save partial results and resume
  ([usage.md](usage.md), *Running on Leonardo Booster*).
- **All inputs and outputs in Zarr** (crops, archive, training stores), with
  chunks, compression, data type and sharding chosen for GPU data loading and
  parallel reads, and to keep the size down.
- The harmonised archive and the code are released openly.

## Team and timeline

- **Federico Conticello** (HydroScan): code and method; writes the tickets and
  the emails to data providers.
- **Marìca Rondinone** (PhD student, University of Basilicata): notebooks and
  exploration; full time on the project from 3/11/2026 to 28/2/2027, renewable
  by 3 months if needed.
- **Vito Telesca** (University of Basilicata): review at the gates and periodic
  reviews, as available.

The **intensive phase** runs from 3/11/2026 to 28/2/2027. Leonardo access is
12 months from 16/11/2026 if the call is won (result expected around
15/11/2026): 4500 node-hours on nodes with 4 GPUs. If it is lost, the work runs
on a workstation with one RTX 4090 and a request for a smaller HPC allocation
is written (P1).

| gate | date | condition | review |
|---|---|---|---|
| G1 | 6/12/2026 | method frozen: cleaning, level-correction bridge, time shift | Vito |
| G2 | 20/12/2026 | archive v1 and training stores ready | Vito |
| G3 | 28/2/2027 | archive tested with IRENE (phase 1), technical report | Vito |

Tickets below carry an id, an owner (F Federico, M Marìca, F+M both, M→F
explored by Marìca and coded by Federico) and the planned dates; dates after
February are indicative. Each phase of WP3 starts only if the compute budget
left allows it.

## Work packages and status

### Setup

- [ ] **S0** Reproduction on Marìca's Windows machine, with growing data: synthetic
  test, then 1–6/7/2024 whole files and `validate` (results must match
  `docs/figures/summary.csv`), then crops for a few years. Long runs on the
  workstation (M, 3–15/11).
- [ ] **S6** SSH access to the Windows workstation, for development with VS Code
  and Claude Code; remote desktop works meanwhile (F, 3–22/11).
- [ ] **S4** Email to VMM: licence of the radar rasters, token, gauge adjustment
  of the intensity, start date (F, 3–15/11).
- [ ] **S5** Period of the team's RADCLIM copy, one file read and compared with
  the OPERA grid (M, 3–22/11).
- [ ] **S7** Pan-European bridge data: whether EURADCLIM is extended to 2024–2025
  (KNMI), ERA5-Land over the Belgian domain (F, 3–22/11).
- [ ] **S1** Python environment on the CINECA modules: choose the modules
  (Python, CUDA, MPI, PyTorch from `cineca-ai`), pin the versions of
  `pyproject.toml` to what they provide, add our packages on top (e.g. a
  virtual environment with `--system-site-packages`); synthetic test in a job
  (F, 18–29/11, if the call is won).
- [ ] **S2** Copy the inputs to the cluster via the data movers. Whole files are
  about 0.4 TB of ODYSSEY `DBZH_QIND` and 0.6 TB of CIRRUS `DBZH`, the Belgian
  crops about 95 GB, the archive about 0.5 TB, against 1 TB of default `$WORK`
  quota: copy the crops in Zarr (D7) (F, 23/11–6/12, if the call is won).
- [ ] **S3** Slurm job scripts for production and training, chained so that each
  job resumes from the previous one (F, 30/11–20/12, if the call is won).
- [ ] **P1** Request for a smaller HPC allocation, which also prepares later
  requests (F+M, 23/11–20/12, if the call is lost).

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
- [ ] **H1** Interpolation on degraded CIRRUS: CIRRUS averaged in Z to 2 km,
  one frame every 15 min with the ODYSSEY time-window offset, interpolated and
  compared with the real 5 min frames over months of data. Measures the whole
  2 km / 15 min → 1 km / 5 min chain without the product difference (M,
  16–29/11).
- [ ] **H2** Cleaning of outliers and artefacts: catalogue of the artefacts over
  Belgium (outliers, clutter, radial spikes from 5 GHz interference, blocked
  sectors, isolated echoes, echoes without clouds), then a known method for each
  (thresholds and persistent-point masks on the model of EURADCLIM, spike
  filters, despeckling, `QIND`, satellite cloud mask) ([data.md](data.md),
  *Known problems*) (M→F, 16–29/11).
- [ ] **H3** Level correction ODYSSEY → CIRRUS through a bridge dataset that is
  stable across the change of product in 7/2024: ODYSSEY is calibrated on the
  bridge before, CIRRUS after. Seasonal, wet-pixel frequency matched first.
  Three variants: pan-European bridge (EURADCLIM if extended, otherwise
  ERA5-Land), national bridge (VMM or RADCLIM), plain seasonal quantile mapping.
  Each comparison uses the bridge's quantity and resolution; the bridge sets the
  level, CIRRUS the shape at 1 km / 5 min. Needed because the IRENE input
  normalisation is fixed (R → dBZ with Marshall-Palmer, clipped to [0, 60],
  scaled to [−1, 1]): a level gap between products ([data.md](data.md),
  *Known problems*) is not absorbed by the model. Variant chosen at G1 (M→F,
  16/11–6/12).
- [ ] **H6** Time shift in production (see *Open decisions*) (F+M, 30/11–6/12).
- [ ] **H5** Validation over Belgium: intensity fields against VMM (bias, QQ,
  FSS, power spectra), accumulations against RADCLIM; baselines are plain
  regridding and linear time interpolation. A dataset used as bridge is no
  longer independent (M, 7–24/1).
- [ ] **H4** Consistency over 2012–2024: rain-rate distributions, wet-pixel
  frequency and accumulation maps year by year; break-point tests on monthly
  accumulations against EURADCLIM 3.0 (F, 3–4/2027).
- [ ] **H8** Archive v1.1 with the corrections from H4 and H5 (F, 4–5/2027).
- [ ] **H7** GPU implementation in PyTorch: gradients and local least squares as
  convolutions, warping with `grid_sample`, many pairs per batch. Must match the
  CPU version on the synthetic test. Optional for DECADE, needed for Europe (F,
  5–7/2027).

### WP2 – Archive and training data in IRENE format

- [x] Window sampler on ODYSSEY at 2 km (`sample`).
- [x] Zarr store of interpolated windows in IRENE format (`windows`).
- [ ] **D7** Zarr for all inputs and outputs: convert the crops (about 640,000
  one-frame HDF5 files), choose chunks (e.g. 24 × 256 × 256), compression, data
  type and sharding by measuring size and read speed. If the archive chunks
  align with the windows, store C can be a list of windows read directly from
  the archive (F, 16–29/11).
- [ ] **D3** Belgian convective test events 2024–2026, excluded from training
  and validation (M, 3–29/11).
- [ ] **D1** Production by time: each ODYSSEY frame read and each motion field
  estimated once, archive chunks written directly, finished chunks skipped so
  that an interrupted job resumes; identical to the current output on the same
  dates; cost per year measured (today each window rereads its 9–11 ODYSSEY
  files, see [usage.md](usage.md), *Measured costs*) (F, 30/11–13/12).
- [ ] **D2** Window budget: tune `m`, `q_min`, `step_px`, `step_t` to what
  training can use within the compute budget (the IRENE parameters give about
  50 million windows) (M, 30/11–13/12).
- [ ] **D4** CIRRUS store for fine-tuning and test: conversion to R, split in
  alternating monthly blocks (e.g. one month in four for test, one for
  validation) with a few days of margin, test events excluded (F, 7–20/12).
- [ ] **D6** Harmonised archive v1 over Belgium + 350 km (reflectivity, `alpha`
  on every frame, about 1.2 million frames, about 0.5 TB) and store C cut from
  it. If D1 shows the whole archive does not fit in two weeks, windows first
  and the archive in January (F, 7–20/12).
- [ ] **D5** Raw ODYSSEY store for configuration B (regridded only; time step
  as decided in T2), same windows and splits as C (F, 21/12–10/1).
- [ ] **R1** Release of archive v1 with a version and a data sheet (content,
  method, limits, licence, citation), in a repository that accepts about
  0.5 TB (F, 1–21/2).

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
allows it. Planning estimate: 10% of the 4500 node-hours in reserve, the rest
over 24 runs, about 169 node-hours per run (about 7 days on one node, so a
chain of about 7 jobs of 24 hours), to be replaced by the cost measured in T3.

| phase | trainings | seeds | runs | estimate |
|---|---|---|---|---|
| 1 | A, B, C | 3 | 9 | about 1520 node-hours; on 2 nodes, 5 rounds of a week from 21/12, B last |
| 2 | C with k = 2 and k = 4, old/recent control | 1 | 3 | about 505 node-hours |
| 3 | C with k = 1, 2, 4, 8, old/recent control | 3 | 15 (12 more than phase 2) | about 2025 node-hours, Leonardo only |

On the RTX 4090 alone (about 1/5 of a node, to be measured) phase 1 by the end
of January is possible only with 1 seed and runs at about 40% of the planned
size.

- [ ] **T0** IRENE (ConvGRU-Ensemble) on the workstation with fake data shaped
  like the stores; native Windows or WSL2 (F, 3–22/11).
- [ ] **T2** Two method decisions (see *Open decisions*): loss on all frames or
  only on real ones, and the time step of B (F+M, 23/11–6/12).
- [ ] **T7** Data-parallel training on the 4 GPUs of a node (PyTorch DDP),
  tried on the 4090 first (F, 23/11–13/12).
- [ ] **T1** Data loader from the Zarr stores into the IRENE code, with
  checkpoint and resume (weights, optimiser, random state, position in the
  data) (F, 7–20/12).
- [ ] **T3** Small run: measure the cost of a run, check that a run interrupted
  and resumed matches a continuous one, decide phases and seeds (F, 14–20/12).
- [ ] **T4** Phase 1 (F, 21/12–31/1).
- [ ] **T5** Phase 2, if the budget allows (F, 3–4/2027).
- [ ] **T6** Phase 3, Leonardo only (F, 5–8/2027).

### WP4 – Verification

- [ ] **V5** Basins and thresholds for question 3, to discuss with Vito:
  accumulations over the Belgian basins hit by the test events, boundaries from
  a pan-European source (EU-Hydro or HydroSHEDS); thresholds such as 10 and
  20 mm/h and 1 h accumulations (F+M, 14–20/12).
- [ ] **V1** STEPS and Flood4Cast LK nowcasts on the test events, same start
  times, lead times and grid as IRENE (F+M, 7–31/1).
- [ ] **V2** Scores with pysteps (CRPS, CSI, FSS by lead time) plus volume bias,
  basin accumulations and thresholds; truth is CIRRUS, accumulations also
  checked against RADCLIM and intensity against VMM (F+M, 7–31/1).
- [ ] **V3** Analysis of A/B/C, first answer to question 2 (M, 1–21/2).
- [ ] **V4** Full verification of all phases, answers to questions 2 and 3 (F,
  5–9/2027).

### WP5 – Costs, release and publications

- [ ] **C5** EGU 2027 abstract (deadline usually mid-January, to check) (F+M,
  7–12/1).
- [ ] **R2** Technical report of the intensive phase, written in `docs/` and
  exported to PDF (F+M, 8–28/2).
- [ ] **C6** Data paper on the Belgian archive (e.g. Earth System Science Data)
  (F+M, 3–5/2027).
- [ ] **C4** Paper on the results (F, 6–10/2027).
- [ ] **C1** Measured costs of harmonisation and training on Leonardo Booster,
  extrapolated to the whole OPERA domain. Current CPU costs are in
  [usage.md](usage.md) (F, 8–9/2027).
- [ ] **C2** Regular Access proposal for the whole OPERA domain (F, 9–10/2027).
- [ ] **C3** Release of archive v1.1 and of the code (F, by 15/11/2027).

## Decisions taken

- **Variable:** DBZH (maximum reflectivity) for both ODYSSEY and CIRRUS,
  converted to R with Marshall-Palmer.
- **Interpolated frames are flagged** with `alpha` (0 = real ODYSSEY frame).
- **Windows are chosen on ODYSSEY at 2 km** and cut from the harmonised archive.
- **Output labels stay on ODYSSEY times** (shift 0), so that real frames remain
  real.
- **WP3 runs in phases** (A/B/C, then a reduced learning curve, then the full
  one), as far as the compute budget allows (decided 3/11/2026).
- **No ECA&D in DECADE.** The correction is anchored to CIRRUS through a
  bridge, the Belgian validation to VMM and RADCLIM, the consistency check to
  EURADCLIM (CC BY 4.0); so the non-commercial ECA&D terms do not touch the
  release (decided 3/11/2026). ECA&D returns only with the parked rain archive.
- **The whole archive is harmonised and released for Belgium + 350 km**, not
  only the training windows; Europe follows when the method is fast enough (H7)
  and pan-European references exist (decided 3/11/2026).
- **Zarr for every input and output** (decided 3/11/2026).

## Open decisions

- **Level-correction bridge (H3):** pan-European, national or none; decided at
  G1.
- **Loss and time step of B (T2):** the earlier plan computed the loss only on
  frames with `alpha = 0`, but configuration C is meant to test the
  interpolated 5 min sequences. B is at 15 min: 15 min steps in pre-training
  and 5 min in fine-tuning, plain linear interpolation to 5 min, or each frame
  repeated three times; the choice changes what B vs C measures.
- **Time shift in production (H6):** with shift 0 the labels keep the offset
  between the products' time windows ([data.md](data.md), *Time windows*).
- **Quality fields (H2):** redo the Belgian crops with quality bands, at the
  same network cost?
- **Basins and thresholds (V5).**
- **Rain archive at 2 km / 15 min** (ODYSSEY `RATE`/`ACRR` plus NIMBUS, outlier
  cleaning, homogenisation of the two periods anchored to ECA&D gauges). Planned
  before DECADE, not in the proposal: parked unless decided otherwise.

## Open questions (external)

- **Licence of the VMM radar rasters** (not stated by waterinfo.be), whether the
  intensity product is gauge-adjusted, and since when the rasters exist (June
  2021 or earlier). To ask hydrometrie@waterinfo.be, together with a token.
- **Period of the RADCLIM copy available to the project:** about 2018–2024
  according to the team, 2017–2022 in the metadata record. To check.
- **EURADCLIM after 2023:** is a version covering 2024–2025 available or
  planned? To ask KNMI.

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
