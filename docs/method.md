# Method

How the processing works and why it is designed this way, with the evidence
behind each choice. Facts about the input data are in [data.md](data.md);
commands and output files are in [usage.md](usage.md); what is planned but not
built yet is in [roadmap.md](roadmap.md).

## Conventions

- Reflectivity in dBZ, rain rate R in mm/h.
- Z–R: Marshall-Palmer, Z = 200 R^1.6, the same as NIMBUS and IRENE.
- Every conversion to R caps dBZ at 55, because of the outliers in ODYSSEY
  (see [data.md](data.md), *Known problems*).

## Temporal super-resolution of ODYSSEY (2 km / 15 min → 1 km / 5 min)

### Grids

The fine pixel `j` lies at coordinate `(j+0.5)/2 − 0.5` of the coarse grid
(aligned centres). Crops are expressed in metres from the upper-left corner and
aligned to 2000 m, so the 2 km and 1 km grids stay 2:1. Validation checks the
alignment from the `where` metadata and writes it to `grid_check.txt`.

### Motion (Lucas-Kanade, at 2 km)

Same scheme as `pysteps.motion.lucaskanade`: Shi-Tomasi features → pyramidal LK
→ forward-backward check → local outlier removal → declustering → IDW
interpolation and smoothing. The sparse vectors of each pair are reused for the
adjacent pairs (context of ±1 pair). Two differences from the pysteps defaults,
both found in testing:

- LK runs on a **high-pass** field (σ = 15 px), so that growth and decay of
  cells are not mistaken for motion. On the synthetic case the mean motion error
  drops from 5.1 to 2.0 px / 15 min.
- 5000 features instead of 1000, meant for the whole European domain.

The `pysteps` backend remains available (`"lk": {"backend": "pysteps"}`).

### Interpolation

For a fraction `a` (`alpha`) of the 15 min interval:

```
F(x, t0 + a·15') = (1−a) · F0(x − a·V) + a · F1(x + (1−a)·V)
```

Trajectories are integrated with the midpoint method in the stationary field V
at 2 km. Values are sampled **once** from the 2 km field at the departure
points of the 1 km pixels, so upscaling and advection are a single bilinear
interpolation. At `a = 0` the method reduces to plain upscaling.

Radar coverage is not advected. Where an echo enters from outside coverage, the
only valid source is used, or, if neither is valid, the Eulerian interpolation.

### Mass conservation (default)

- **Conservative upscaling** (`mass_correction=True`). Interpolating in dBZ
  loses rain, because R is convex in dBZ (Jensen's inequality). For each 2 km
  pixel a correction in dB makes the mean R of its 4 sub-pixels equal to the R
  of the ODYSSEY pixel; the correction follows the values along the
  trajectories.
- **Blending in R** (`blend_space="R"`). The average of the advected F0 and F1
  is taken in R. A dry pixel weighs 0, so cell edges do not drop below threshold
  as they do when averaging in dB. Averaging in Z instead adds rain where the
  advected F0 and F1 do not coincide, because R is concave in Z.

Evidence on the 4 real days (Belgium, 380 pairs): volume of the output relative
to (1−a)·V(F0) + a·V(F1).

| | α = 0 | α = 1/3 |
|---|---|---|
| bilinear, blending in Z (previous default) | 0.918 | 0.959 |
| correction + blending in Z | 0.999 | 1.065 |
| **correction + blending in R (default)** | **0.999** | **1.011** |

Against CIRRUS the correction doubles the small-scale energy (from 0.17 to
0.33 of CIRRUS) and lowers the RMSE of hourly accumulations at 25 km (from 1.12
to 1.07 mm), with a slightly higher RMSE in dBZ (12.90 against 12.79
mid-interval). On the synthetic case blending in R has a higher dBZ RMSE than
blending in Z mid-interval (3.7 against 2.9) but a better CSI. The variants
remain available as methods `lk:Z` and `lk:dB`, or with `mass_correction=false`.

### Output labels and `alpha`

Every produced frame carries `alpha`: 0 is a real ODYSSEY frame, 1/3 and 2/3
are interpolated. By default the output labels are the ODYSSEY times. A time
shift of −2.5 min moves them to the CIRRUS convention (see [data.md](data.md),
*Time windows*), but then every frame is interpolated (α = 1/6, 1/2, 5/6). Which
convention is used for training is a decision recorded in
[roadmap.md](roadmap.md).

## Validation against CIRRUS

Compared methods:

| method | what it does |
|---|---|
| `nearest` | nearest ODYSSEY frame, upscaled (persistence) |
| `linear` | Eulerian average of F0 and F1 |
| `lk` | advection-based interpolation above (variants `lk:Z`, `lk:dB`) |

Metrics are stratified by `alpha`. **The error at `alpha = 0` is the floor**:
there is no temporal interpolation there, so it measures upscaling and the
differences between products. What matters for temporal interpolation is the
*extra* error at the other times. Scores: bias, MAE, RMSE and correlation in
dBZ on wet pixels; POD/FAR/CSI/frequency bias at 10/20/30/40 dBZ; FSS at
20/30 dBZ; small-scale energy ratio; volumes and R errors at 1–25 km; hourly
accumulations; internal conservation against ODYSSEY itself. Several time
shifts are tried to find the one that minimises the error.

### Results on 1–5/7/2024, Belgium (current defaults)

- With the current defaults the volume stays within 1% of ODYSSEY at every
  `alpha` (bilinear upscaling in dBZ lost about 8%).
- Hourly accumulations: the methods are almost equivalent.
- Instantaneous fields mid-interval: LK beats `nearest` (RMSE 12.9 against
  13.8 dBZ).
- The interpolated field has about a third of the small-scale energy of CIRRUS.
- The ODYSSEY/CIRRUS level difference (see [data.md](data.md)) dominates the
  floor error; it is a product difference, not an interpolation error.

![Validation overview, 1–5/7/2024, Belgium](figures/validation_overview.png)

### Degraded CIRRUS as a stand-in for ODYSSEY

To measure the interpolation error over months with a known truth (H1),
CIRRUS is degraded to the ODYSSEY grid (`opera_ds.validate.degrade_frame`) and
kept every 15 min; the degraded frames are interpolated back to 5 min and scored
against the real CIRRUS (`notebooks/02-mr-degraded-cirrus.ipynb`). The
degradation should look like real ODYSSEY, otherwise it measures the error on an
input that is easier or harder to interpolate.

Three degradations of each 2 × 2 block were compared with real ODYSSEY on
1–5/7/2024: mean in linear Z (`zmean`), maximum (`max`) and the upper-left pixel
(`sample`). ODYSSEY at NT is paired with CIRRUS at NT+5, the closest window
([data.md](data.md), *Time windows*); 382 pairs, values capped at 60 dBZ against
the ODYSSEY outliers. Distributions of wet pixels (≥ 10 dBZ) are compared by
shape, after removing the median offset, since the products differ in level;
small-scale energy is the high-pass energy (Gaussian, σ = 2 px) relative to
ODYSSEY.

| area | variant | median offset to ODYSSEY [dB] | QQ shape RMS [dB] | small-scale energy / ODYSSEY |
|---|---|---:|---:|---:|
| Belgium + 200 km | `zmean` | −0.04 | 0.39 | 1.39 |
| | `max` | 0.70 | 0.78 | 1.64 |
| | `sample` | −0.20 | 0.43 | 1.53 |
| Belgium | `zmean` | 1.30 | 0.67 | 2.14 |
| | `max` | 2.61 | 1.21 | 2.52 |
| | `sample` | 0.86 | 0.63 | 2.26 |

- `zmean` is the closest to ODYSSEY: lowest small-scale energy everywhere, best
  or tied distribution shape. It is the degradation used in H1.
- No degradation is smoother than ODYSSEY: real ODYSSEY has 1.4–2.1 times less
  small-scale energy than CIRRUS degraded by `zmean`. Degraded CIRRUS is
  therefore a rougher, not an easier, input than ODYSSEY.

### Synthetic test

`tests/test_synthetic.py` builds a multiscale field with known motion
(translation and rotation, about 60 km/h) and growth/decay, degrades it to
"ODYSSEY" (2 km, 15 min, shifted by +2.5 min) and uses it as "CIRRUS" at
1 km / 5 min. It requires that the estimated shift is −2.5 min, that LK beats
`nearest` and `linear` in RMSE at every interpolated time and `linear` in CSI at
30 dBZ, that the volume stays within 2% of "ODYSSEY" at every `alpha` and the
2 × 2 block error at `alpha = 0` is below 1%, and that the sampler and the
window store behave as specified below.

## Training windows

### Sampling on ODYSSEY at 2 km

Same scheme as IRENE's `importance_sampler`, but on the ODYSSEY files at 2 km,
so that only the selected windows are interpolated. A window of T frames at
5 min needs ⌊(T−1)·5/15⌋ + 2 consecutive ODYSSEY frames (9 for T = 24): if one
is missing the window is discarded. It is also discarded if the fraction
outside coverage exceeds `max_nan_frac` (default 0.64%, as IRENE), and accepted
with probability q = min(1, q_min + m · mean(1 − e^(−R/s))).

The seed generates an independent generator per block (`SeedSequence.spawn`),
so results do not depend on how the period is split. (In the IRENE code, with a
fixed seed, every window would receive the same random number.)

### Window content

Windows are T × H × W (24 × 256 × 256 as IRENE) in R (mm/h), with dBZ clipped
to [0, 60] as in IRENE, NaN outside coverage, and `alpha` for every frame.
Motion is estimated on a crop larger than the window (`context_km` on each
side). Windows with missing ODYSSEY frames are discarded.

## Limitations

- **Detail below 2 km is not created.** Recovering that variability would need
  a stochastic (e.g. RainFARM) or learned downscaling.
- **The dynamics within the 15 min are synthetic**: two frames out of three are
  combinations of real ones.
- **The ODYSSEY/CIRRUS overlap is only 4 summer days** in the public archive,
  without CIRRUS at the quarter hours; for rain it is zero.
- **Motion is stationary within the interval.** With very fast systems (above
  about 120 km/h) LK can lock onto a wrong match.
- **The time shift is not yet applied in production.**
