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
   products, accurately enough for training and with a cost per year of data
   that makes the whole OPERA domain feasible (measured on Belgium,
   extrapolated in C1)?
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
- **Only real-time inputs in the operational chain** (decided 9/11/2026, review
  of #74). The pipeline is fed by real-time CIRRUS, so every step that CIRRUS
  goes through uses only data available in real time: the composite itself,
  and masks or statistics computed beforehand from past composites. Satellite
  products, gauges and national products serve only to validate, or to make
  ODYSSEY look like CIRRUS. Cleaning ODYSSEY aims to match CIRRUS, not to be
  cleaner than it.
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
| G4 | 15/11/2027 (indicative) | final archive and results: archive v1.1 and code released, research questions answered, costs extrapolated to Europe; end of Leonardo access | — |

Tickets below carry an id, an owner (F Federico, M Marìca, F+M both, M→F
explored by Marìca and coded by Federico) and the planned dates; dates after
February are indicative. Each id links to its GitHub issue, which holds the
goal, scope, data and compute, how to verify and the acceptance criteria; a
ticket is ticked here when its issue is closed. Each phase of WP3 starts only if the compute budget
left allows it.

## Work packages and status

### Setup

- [x] [**S0**](https://github.com/fedro86/DECADE/issues/9) Reproduce the
  existing pipeline on Marìca's Windows machine (M, 3–15/11).
- [ ] [**S6**](https://github.com/fedro86/DECADE/issues/10) Set up SSH access to
  the Windows workstation (F, 3–22/11).
- [x] [**S4**](https://github.com/fedro86/DECADE/issues/11) Ask VMM about
  licence, access token, gauge adjustment and start date (F, 3–15/11).
- [x] [**S5**](https://github.com/fedro86/DECADE/issues/12) Check the period of
  the RADCLIM copy and read it on the OPERA grid (M, 3–22/11).
- [ ] [**S7**](https://github.com/fedro86/DECADE/issues/13) Get EURADCLIM and
  ERA5-Land over the Belgian domain (F, 3–22/11).
- [ ] [**S1**](https://github.com/fedro86/DECADE/issues/14) Build the Python
  environment on the CINECA modules (F, 18–29/11, if the call is won).
- [ ] [**S2**](https://github.com/fedro86/DECADE/issues/15) Copy the inputs to
  Leonardo via the data movers (F, 23/11–6/12, if the call is won).
- [ ] [**S3**](https://github.com/fedro86/DECADE/issues/16) Write chained,
  resumable Slurm job scripts (F, 30/11–20/12, if the call is won).
- [ ] [**P1**](https://github.com/fedro86/DECADE/issues/17) Write a request for
  a smaller HPC allocation (F+M, 23/11–20/12, if the call is lost).

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
- [x] [**H1**](https://github.com/fedro86/DECADE/issues/18) Measure
  interpolation error on degraded CIRRUS (M, 16–29/11).
- [ ] [**H2**](https://github.com/fedro86/DECADE/issues/19) Clean outliers and
  radar artefacts from ODYSSEY (M→F, 16–29/11).
- [ ] [**H3**](https://github.com/fedro86/DECADE/issues/20) Correct the ODYSSEY
  → CIRRUS level difference through a bridge dataset (M→F, 16/11–6/12).
- [ ] [**H6**](https://github.com/fedro86/DECADE/issues/21) Decide the time
  shift used in production (F+M, 30/11–6/12).
- [ ] [**H5**](https://github.com/fedro86/DECADE/issues/22) Validate archive v1
  over Belgium against VMM and RADCLIM (M, 7–24/1).
- [ ] [**H4**](https://github.com/fedro86/DECADE/issues/23) Check the
  consistency of the archive over 2012–2024 (F, 3–4/2027).
- [ ] [**H8**](https://github.com/fedro86/DECADE/issues/24) Produce archive v1.1
  with the validation corrections (F, 4–5/2027).
- [ ] [**H7**](https://github.com/fedro86/DECADE/issues/25) Port the
  interpolation to GPU with PyTorch (F, 5–7/2027).

### WP2 – Archive and training data in IRENE format

- [x] Window sampler on ODYSSEY at 2 km (`sample`).
- [x] Zarr store of interpolated windows in IRENE format (`windows`).
- [ ] [**D7**](https://github.com/fedro86/DECADE/issues/26) Move all inputs and
  outputs to Zarr (F, 16–29/11).
- [ ] [**D3**](https://github.com/fedro86/DECADE/issues/27) Choose the Belgian
  convective test events (M, 3–29/11).
- [ ] [**D1**](https://github.com/fedro86/DECADE/issues/28) Produce the archive
  by time, with resume (F, 30/11–13/12).
- [ ] [**D2**](https://github.com/fedro86/DECADE/issues/29) Set the window
  budget (M, 30/11–13/12).
- [ ] [**D4**](https://github.com/fedro86/DECADE/issues/30) Build the CIRRUS
  store with train, validation and test splits (F, 7–20/12).
- [ ] [**D6**](https://github.com/fedro86/DECADE/issues/31) Produce harmonised
  archive v1 and store C (F, 7–20/12).
- [ ] [**D5**](https://github.com/fedro86/DECADE/issues/32) Build the raw
  ODYSSEY store for configuration B (F, 21/12–10/1).
- [ ] [**R1**](https://github.com/fedro86/DECADE/issues/33) Release archive v1
  for Belgium (F, 1–21/2).

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

- [ ] [**T0**](https://github.com/fedro86/DECADE/issues/34) Run IRENE on the
  4090 with fake data (F, 3–22/11).
- [ ] [**T2**](https://github.com/fedro86/DECADE/issues/35) Decide the loss and
  the time step of configuration B (F+M, 23/11–6/12).
- [ ] [**T7**](https://github.com/fedro86/DECADE/issues/36) Train on 4 GPUs with
  data parallelism (F, 23/11–13/12).
- [ ] [**T1**](https://github.com/fedro86/DECADE/issues/37) Write the IRENE data
  loader, with checkpoint and resume (F, 7–20/12).
- [ ] [**T3**](https://github.com/fedro86/DECADE/issues/38) Run a small training
  and measure the cost (F, 14–20/12).
- [ ] [**T4**](https://github.com/fedro86/DECADE/issues/39) Train phase 1:
  configurations A, B and C (F, 21/12–31/1).
- [ ] [**T5**](https://github.com/fedro86/DECADE/issues/40) Train phase 2:
  configuration C with 2 and 4 years (F, 3–4/2027).
- [ ] [**T6**](https://github.com/fedro86/DECADE/issues/41) Train phase 3: the
  full learning curve (F, 5–8/2027).

### WP4 – Verification

- [ ] [**V5**](https://github.com/fedro86/DECADE/issues/42) Agree basins and
  thresholds for research question 3 with Vito (F+M, 14–20/12).
- [ ] [**V1**](https://github.com/fedro86/DECADE/issues/43) Produce the STEPS
  and Lucas-Kanade reference nowcasts (F+M, 7–31/1).
- [ ] [**V2**](https://github.com/fedro86/DECADE/issues/44) Compute verification
  scores with pysteps (F+M, 7–31/1).
- [ ] [**V3**](https://github.com/fedro86/DECADE/issues/45) Analyse
  configurations A, B and C (M, 1–21/2).
- [ ] [**V4**](https://github.com/fedro86/DECADE/issues/46) Verify all trained
  models (F, 5–9/2027).

### WP5 – Costs, release and publications

- [ ] [**C5**](https://github.com/fedro86/DECADE/issues/47) Submit the EGU 2027
  abstract (F+M, 7–12/1).
- [ ] [**R2**](https://github.com/fedro86/DECADE/issues/48) Write the technical
  report of the intensive phase (F+M, 8–28/2).
- [ ] [**C6**](https://github.com/fedro86/DECADE/issues/49) Write the data paper
  on the Belgian archive (F+M, 3–5/2027).
- [ ] [**C4**](https://github.com/fedro86/DECADE/issues/50) Write the paper on
  the results (F, 6–10/2027).
- [ ] [**C1**](https://github.com/fedro86/DECADE/issues/51) Measure costs and
  extrapolate them to Europe (F, 8–9/2027).
- [ ] [**C2**](https://github.com/fedro86/DECADE/issues/52) Write the EuroHPC
  Regular Access proposal (F, 9–10/2027).
- [ ] [**C3**](https://github.com/fedro86/DECADE/issues/53) Release archive v1.1
  and the code (F, by 15/11/2027).

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
  G1. With similar results the pan-European bridge is preferred, because the
  method must apply to the whole OPERA domain. If a national bridge is chosen,
  the decision states what would replace it in the other countries.
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
