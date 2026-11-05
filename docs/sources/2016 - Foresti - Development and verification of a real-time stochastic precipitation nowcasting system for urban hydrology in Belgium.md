# Development and verification of a real-time stochastic precipitation nowcasting system for urban hydrology in Belgium

- **Authors, year, venue:** L. Foresti, M. Reyniers, A. Seed, L. Delobbe (RMI),
  2016, *Hydrology and Earth System Sciences* 20, 505–527
- **Link:** https://doi.org/10.5194/hess-20-505-2016
- **Access:** open, CC BY 3.0
- **Read:** full text

## What it is

STEPS-BE, the RMI implementation of STEPS: 20-member ensemble nowcasts at 1 km
and 5 min up to 2 h, from a composite of the Wideumont, Zaventem, Jabbeke and
Avesnois C-band radars (Marshall-Palmer Z = 200 R^1.6), for sewer models in
Ghent and Leuven. Verified on four events that caused sewer overflow (table 1).

## Numbers we use

- **Event labels:** the four events are labelled stratiform (Ghent, 10/11/2013
  and 3/1/2014) or convective (Leuven, 9–10/6/2014 and 19–20/7/2014) by their
  character and season, not by a quantitative rule (section 2).
- **Verification thresholds:** 0.5 and 5.0 mm/h (on 30 min accumulations).
  Probabilistic nowcasts are reliable up to about 2 h above 0.5 mm/h, only up
  to about 30 min above 5 mm/h.
- RMSE of the 0–30 min nowcast above 10 mm/h over Leuven in the convective case,
  below 2 mm/h over Ghent in the winter case.

## Relevance to DECADE

The Belgian STEPS reference for V1 and V2 (thresholds, lead times). Shows that
RMI case studies label events qualitatively; it does not give a classification
rule for H1 or D3. It also notes that the operational composite of that time
had no bright-band correction.

## Limits

Four events only; national composite of 2013–2014.
