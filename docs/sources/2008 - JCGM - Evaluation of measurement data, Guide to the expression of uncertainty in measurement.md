# Evaluation of measurement data – Guide to the expression of uncertainty in measurement (GUM)

- **Authors, year, venue:** Joint Committee for Guides in Metrology (JCGM WG 1), 2008; JCGM 100:2008 (GUM 1995 with minor corrections), BIPM.
- **Link:** <https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf>
- **Access:** free from the BIPM; copyright JCGM, reproduction allowed with acknowledgement (title page)
- **Read:** sections 3.2–3.3 (errors, effects, corrections), 4.3 (Type B evaluation, in particular 4.3.7), 5.1–5.2 (combined standard uncertainty, uncorrelated and correlated inputs), 6.3 (coverage factor); the annexes were not read.

## What it is

The international reference for how to state and combine uncertainties of a
measurement result, used across metrology and adopted by the WMO guide on
instruments.

## Numbers we use

- **Known systematic effects are corrected** (3.2.3–3.2.4); what is left is
  the uncertainty of the correction, not the bias. A known significant
  systematic effect should be corrected rather than covered by enlarging the
  uncertainty (6.3.1, note).
- **Bounds only, no preference inside them** (4.3.7): rectangular
  distribution, expectation at the midpoint, variance (a₊ − a₋)²/12, so a
  standard uncertainty equal to the full width over √12.
- **Uncorrelated inputs** (5.1.2): the combined variance is the sum of the
  squared contributions (addition in quadrature).
- **Fully correlated inputs** (5.2.2, note 1): with all correlation
  coefficients +1 the combined standard uncertainty is the linear sum of the
  contributions.
- **Expanded uncertainty** (6.3): U = k·u_c, with k usually 2 to 3; k = 2
  gives about 95% for a near-normal distribution.

## Relevance to DECADE

H3 (#20): the rules for the uncertainty budget of the level correction
(`docs/method.md`, *Uncertainty budget of the level correction*), asked on #96
on 16/11/2026: which terms add in quadrature, which linearly, how a choice
between two alternatives becomes a standard uncertainty, and why a known drift
of a bridge is corrected (by using the other bridge) rather than added as a
term.

## Limits

- Written for measurements of one quantity with a known model; the offsets
  of H3 are statistical estimates with structural choices (bridge, rings,
  seasons), so treating those choices as Type B rectangular terms is our
  application of 4.3.7, not something the guide prescribes.
- Nothing specific to climate data, homogenisation or bias correction.
