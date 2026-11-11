# Notebooks

Exploration and figures, built on the `opera_ds` library. They are not part of
the production pipeline: see `CONTRIBUTING.md`, *From notebook to production
code*.

| notebook | what it shows |
|---|---|
| `01-quickstart.ipynb` | download a few composites, read ODYSSEY and CIRRUS over Belgium, interpolate one pair to 5 min and compare with CIRRUS |
| `02-mr-degraded-cirrus.ipynb` | H1: degrade CIRRUS to the ODYSSEY grid, interpolate it back to 5 min and score against the real CIRRUS by `alpha`, scale and event type |
| `03-mr-cirrus-analysis.ipynb` | CIRRUS analysis: Steiner intensity centres against ECCO convectivity, January and September 2025, and maps of the January disagreements (review of #65) |
| `04-mr-radclim.ipynb` | S5: period of the RADCLIM copy, one 5 min file (grid, projection, units, time attributes), one hour on the OPERA grid beside ODYSSEY `ACRR` |
| `05-mr-artefacts.ipynb` | H2: artefacts in ODYSSEY and CIRRUS. Gabella on convective and January days (1–2), values above 55/70 dBZ (3), yearly catalogue 2013–2024 and stability of `histo_cut` (4–5), radar positions, `how/nodes` and monthly catalogue (5, 7), isolated echoes, blocked sectors, spokes, static-mask rules (8), first version on ODYSSEY 2015, 2017, 2023 (9), on CIRRUS 7–12/2024 (10) and on CIRRUS 2025 out of sample with the losses over Belgium (11), with and without Gabella |
| `06-fc-bridge-data.ipynb` | S7: July 2013 of ERA5-Land and CERRA-Land on the OPERA grid as coarse cells, beside cleaned ODYSSEY summed over the same 06–06 UTC window; level gap and cell-by-cell agreement |
| `07-mr-level-correction.ipynb` | H3: distributions of ODYSSEY and CIRRUS over Belgium per month and hour, the product gap on the overlap days 1–5/7/2024, the year-to-year spread of each month against that gap, and hourly radar rain on the ERA5-Land grid |

Add a line here when you add a notebook. Name: `NN-<initials>-<topic>.ipynb`.
