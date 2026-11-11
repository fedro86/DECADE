# The Dutch real-time gauge-adjusted radar precipitation product

- **Authors, year, venue:** Aart Overeem, Hidde Leijnse, Mats Veldhuizen, Bastiaan Anker (KNMI), 2025. Earth System Science Data 17, 4715–4736.
- **Link:** [10.5194/essd-17-4715-2025](https://doi.org/10.5194/essd-17-4715-2025)
- **Access:** open, CC BY 4.0.
- **Read:** full text; sections 2.1, 3.1–3.2, 4.1 and 7.2 in detail for the Belgian radars.

## What it is

Description and evaluation of KNMI's real-time 5-min gauge-adjusted radar QPE (1 km, Netherlands and surroundings), comparing the last year of the old product (31/1/2022–31/1/2023) with the first year of the renewed one (31/1/2023–31/1/2024). The product ingests volume data from Dutch, German and Belgian radars; VMM, RMI and DWD are thanked for radar data. It is not the VMM product, but it is the only peer-reviewed source found that dates changes in how data of the Belgian radars (Jabbeke and Wideumont by name; the VMM radar presumably, since VMM is thanked for radar data) are used by a neighbouring service in 2022–2025.

## Numbers we use

Page numbers are those of the journal; read on 11/11/2026.

- Product renewal on 31/1/2023: polarimetric fuzzy-logic clutter removal, rain-induced attenuation correction, VPR correction, quality-based compositing, and spatially variable instead of mean-field-bias gauge adjustment (abstract; section 1, p. 4716).
- Up to 7 C-band polarimetric radars: 2 in the Netherlands, 2 in Germany, **3 in Belgium**; Neuheilenbach (Germany) added on 9/9/2024 (section 2.1, p. 4717). The Belgian radars are not all named in the text; Jabbeke and Wideumont are.
- **Wideumont "started contributing in August 2023"**, and longer-range scan data from **Jabbeke** were added in the renewed product (section 2.1, p. 4717).
- Belgian radar data lack the clutter-phase-alignment variable; their fuzzy-logic clutter removal uses only ZDR texture (0.5), PhiDP texture (0.3) and RHOHV (0.2), threshold 0.3 (Dutch radars: 0.6) (section 3.2, p. 4718; Appendix A).
- Z = 200 R^1.6 (Marshall–Palmer) for all radars in this product (section 1, p. 4716).
- Radial patterns over the North Sea and the Channel pointing to **Jabbeke**, at ≥ 0.01 mm/h, attributed to **interference**, remain in the renewed product (section 4.1, p. 4722).
- After the evaluation period (section 7.2, p. 4729): **9/9/2024**, data from almost twice as many elevation scans added for Jabbeke and the German radars; **5/11/2024**, a few more scans for all Belgian and German radars; 5/11/2024, down-weighting of the beam-blocked eastern sector of Herwijnen in the two lowest scans.

## Relevance to DECADE

H3 (#20), VMM across 7/2024:

- **Herwijnen**, one of the three VMM radars, has a severe beam blockage to the east (a line of trees; section 4.2) that KNMI only mitigates in its own processing from 5/11/2024. The paper documents no hardware change of Herwijnen in 2022–2025.
- **Jabbeke:** KNMI changed which Jabbeke scans it ingests on 9/9/2024. This is KNMI processing, not VMM's, but it falls in the same month as the `*_BEJAB0924issue` series that VMM has served since 1/10/2024 (`docs/data.md`). A change in the Jabbeke scan strategy or data delivery around September 2024 would explain both; neither source says so. Both dates are after the ODYSSEY–CIRRUS switch of July 2024, so they matter for the CIRRUS side of the bridge, not for the overlap itself.
- **Wideumont** entered the KNMI product in August 2023, after its replacement in 2022; Wideumont is not part of the VMM composite.
- Product-level lesson: a neighbouring national product changed its whole processing chain on one date (31/1/2023) and kept changing in 2024–2025. The same could happen to VMM without peer-reviewed documentation.

## Limits

- Describes KNMI's product and KNMI's use of Belgian radar data; it does not describe VMM's processing.
- Dates of changes at the Belgian radar sites themselves (scan strategy, calibration, software) are not given.
- Evaluation period ends 31/1/2024, before July 2024.
