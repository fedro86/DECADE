# IRENE: A Convolutional GRU Ensemble Model for Radar Precipitation Nowcasting over Italy

- **Authors, year, venue:** A. Camilletti, G. Franch, E. Tomasi,
  M. Cristoforetti (FBK), 2026, arXiv preprint 2609.17175v1 (15/9/2026)
- **Link:** https://arxiv.org/abs/2609.17175 · model weights:
  https://huggingface.co/it4lia/irene
- **Access:** open, CC BY-SA 4.0 (arXiv page); code announced under BSD 2-Clause
  (Code and Data Availability, p. 17)
- **Read:** full text of sections 3 (dataset, cleaning, importance sampling),
  5.5 (benchmarks), 6 (opening and 6.1 case study) and 7 (conclusions); the
  architecture and loss sections skimmed. The HuggingFace model card was also
  checked: it has no test set or event list.

## What it is

The paper of the model DECADE uses. A multi-scale ConvGRU ensemble trained on
the Italian DPC SRI composite (1 km, 5 min), 1/1/2021 to 11/12/2025, with 6
input frames (30 min) and 12 target frames (60 min), rolled out to 120 min.
Compared with pysteps STEPS (Lucas-Kanade motion) and pre-trained DGMR.

## Numbers we use

- **No event-based test set.** The test set is the last 5% of a sequential
  90/5/5 split of importance-sampled space-time cubes: 359,000 cubes, of which
  17,950 for test (section 3.3, p. 5). All scores are computed on this test set
  (section 6, p. 10).
- **Importance sampling** (adapted from Ravuri et al. 2021): a 24 × 256 × 256
  cube is kept with probability q = min(1, q_min + c·R̄), where R̄ is the space-
  and time-mean of 1 − exp(−R/s); q_min = 10⁻⁴, c = 0.1, s = 1 mm/h
  (section 3.3, eq. 6, p. 5).
- **Data cleaning** before sampling: candidates every 15 min and every 16 km;
  all 24 frames present; at most 10⁴ missing pixels per cube (< 1%). The authors
  note this under-samples the edges of radar coverage (section 3.2, p. 5).
- **Value range:** Z = 200 R^1.6, clipped to 0–60 dBZ (0.037 to about
  205 mm/h); losses and verification are blind outside this range
  (section 3.1, p. 4–5).
- **Case study:** one event, "selected among the test-period cases for its high
  total precipitation": Genoa low over the Ligurian Sea, input from
  2025-11-02 18:10 UTC, core above 20 mm/h (section 6.1 and Fig. 3, p. 11–12).
  No rule beyond "high total precipitation" is given.
- **STEPS baseline settings:** Lucas-Kanade, 6 cascade levels, AR(2), 10
  members, CDF matching, incremental mask below 5 dBZ (section 5.5.1, p. 9–10).
- **Stated gaps** (section 7, p. 16): skill on intense, hydrologically relevant
  rain-rate thresholds and on accumulations was not assessed.

## Relevance to DECADE (D3)

IRENE gives no event-selection rule that D3 can copy: its test set is a time
block of rain-weighted samples, plus one case chosen for high total rain. The
authors themselves list threshold and accumulation verification as open work,
which is exactly what D3 and V5 add. The importance-sampling formula is a
documented, reusable way to rank candidate windows by mean rain. The 0–60 dBZ
range bounds which intensities can be verified at all.

## Limits

Preprint, not peer reviewed. Italian DPC composite, not OPERA. The test set
mixes all weather types; nothing is said about convective versus stratiform
cases.
