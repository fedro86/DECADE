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
| `05-mr-artefacts.ipynb` | H2: artefacts in ODYSSEY; section 1 checks how much rain the Gabella filter removes at 2 km on convective days |

Add a line here when you add a notebook. Name: `NN-<initials>-<topic>.ipynb`.
