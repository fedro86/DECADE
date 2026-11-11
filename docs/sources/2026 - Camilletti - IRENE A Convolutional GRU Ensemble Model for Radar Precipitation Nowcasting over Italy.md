# IRENE: A Convolutional GRU Ensemble Model for Radar Precipitation Nowcasting over Italy

- **Authors, year, venue:** A. Camilletti, G. Franch, E. Tomasi, M.
  Cristoforetti (Fondazione Bruno Kessler), 2026, arXiv preprint 2609.17175v1
  (15/9/2026)
- **Link:** [10.48550/arXiv.2609.17175](https://doi.org/10.48550/arXiv.2609.17175)
- **Access:** open, CC BY-SA 4.0
- **Read:** full text (17 pages, sections 1–7); the code checked against it is
  [DSIP-FBK/IT4LIA-FBK-Seminar](https://github.com/DSIP-FBK/IT4LIA-FBK-Seminar),
  `module2-irene-nowcasting`, commit `676ffe7`

## What it is

IRENE is the probabilistic nowcasting model that DECADE trains. It reads 6
radar frames (30 min) and produces an ensemble of the next 12 (60 min; 24 in
verification), at 1 km / 5 min. It is trained on the Italian DPC rain-rate
composite (IT-DPC-SRI), 1/1/2021–11/12/2025, and compared with STEPS and a
pre-trained DGMR on the 5% of the cubes that come last in time.

## Numbers we use

- **Training cubes** (sections 3.2–3.3):
  - candidates of 24 × 256 × 256 on a stride of 3 frames (15 min) and
    16 pixels;
  - discarded when a frame is missing or when more than 10⁴ pixels are NaN
    ("less than 1%"; 10⁴ / 1.57·10⁶ = 0.64%); the remaining NaN become the
    no-rain value;
  - kept with probability q = min(1, q_min + c · R̄), R̄ the cube mean of
    1 − e^(−R/s); q_min = 10⁻⁴, c = 0.1, s = 1 mm/h. The scheme is adapted
    from Ravuri et al. (2021, DGMR); the paper gives no reason for these
    values beyond giving dry cubes "a small but non-zero chance";
  - 359,000 cubes kept, split in time order 90/5/5: 323,100 / 17,950 /
    17,950. The number of candidates before and after the NaN filter is not
    given.
- **Augmentation** (section 3.4): one of the 8 symmetries of the square, and
  a random 18-frame run inside the 24 frames (7 positions): up to 56 views
  per cube.
- **Normalisation** (section 3.1): Z = 200 R^1.6 in dBZ, clipped to
  [0, 60] dBZ (0.037–205 mm/h), rescaled to [−1, 1]. The loss is computed in
  this space, so an error weighs the same at low and high rain rates.
- **Model** (section 2, Table 1): ConvGRU encoder–forecaster on 6 levels
  (1, 2, 4, 8, 16, 32 km; channels 1 to 1024, ×4 at each PixelUnshuffle),
  3 × 3 convolutions, 6.4·10⁷ parameters (encoder 3.8·10⁶). Members differ by
  Gaussian noise fed to the 32 km decoder block, drawn anew at every lead
  time. The predicted frame is not fed back; the rollout runs on the hidden
  states. No layer has a fixed size, so the weights trained on 256 × 256
  apply to the whole grid (padded to a multiple of 32), without tiles
  (section 6).
- **Loss** (section 4.1): afCRPS with α = 0.95 (after Lang et al., 2026) on
  K = 10 members, plus 0.01 × the mean step between consecutive frames.
- **Training** (section 4.4, Table 2): Adam, learning rate 10⁻⁴, batch 32
  (16 for IRENE-GAN), K = 10, one GPU, stopped when the validation loss
  stops improving. Steps, epochs and GPU hours are not given.
- **GAN variants** (sections 4.2–4.3): 3-D PatchGAN discriminator (5.2·10⁵
  parameters), hinge loss, adaptive weight (Esser et al., 2021) times
  w_D = 0.04, switched on after 4·10⁵ steps; IRENE-GAN-RAPSD adds a spectral
  penalty (64 × 64 windows, w_S = 0.02) and is fine-tuned from IRENE-GAN.
  Section 4.2 sets the temporal penalty to 0 for the GAN, Table 2 to 0.01.
- **Results at 120 min** (section 6): CRPS 0.548 (IRENE), 0.549 (GAN), 0.553
  (GAN-RAPSD) against 0.64 mm/h for STEPS; all IRENE versions beat STEPS and
  DGMR at every lead time. IRENE has the lowest MAE up to about 85 min. The
  rank-histogram deviation of IRENE stays below 0.015. IRENE loses power at
  small scales (about −12 dB at 16 km by 120 min); the GAN versions reach
  about +10 dB at 4 km.

## Relevance to DECADE

- **T0, T2, T4:** the code's defaults (CRPS on 2 members, batch 16) are not
  the paper's configuration (afCRPS on 10 members, batch 32). T0 measured the
  defaults; memory with 10 training members on the RTX 4090 is still to be
  measured, and T2 has to choose which configuration to reproduce. The code
  already has an afCRPS class.
- **Training windows (D-tickets):** `opera_ds.sampling` uses the same filter
  and acceptance rule; the paper confirms the values and the 90/5/5 split in
  time order.
- **H3:** the fixed normalisation passes any level gap between ODYSSEY and
  CIRRUS to the model unchanged.
- **V-tickets:** the paper reports no threshold (CSI) or neighbourhood (FSS)
  scores and no accumulations; it names them as limits. DECADE needs both
  for the intense-rain thresholds and the basins (V2, V5).

## Limits

- Italian radar network and climate; DECADE trains on OPERA over Belgium +
  350 km.
- Instantaneous rain rate only, 5-min archive since 2021; ODYSSEY is 15 min
  and needs the interpolation of WP1 first.
- The cleaning keeps cubes from the well-covered interior, so behaviour near
  the edge of the radar coverage is under-represented (section 3.2).
- DGMR is used without retraining and only to 90 min; it is not a comparison
  of architectures (section 5.5.2).
