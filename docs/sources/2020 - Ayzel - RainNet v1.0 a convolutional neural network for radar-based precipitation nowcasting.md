# RainNet v1.0: a convolutional neural network for radar-based precipitation nowcasting

- **Authors, year, venue:** G. Ayzel, T. Scheffer, M. Heistermann, 2020,
  *Geoscientific Model Development* 13, 2631–2644
- **Link:** https://doi.org/10.5194/gmd-13-2631-2020
- **Access:** open, CC BY 4.0 (p. 2631)
- **Read:** full text of sections 3 (data and setup), 4 (results) and 5
  (conclusions); architecture section skimmed. The event list is in Ayzel et
  al. 2019 (rainymotion), summarised separately.

## What it is

A U-Net-type CNN trained on the DWD RY composite (1 km, 5 min, Germany),
predicting 5 min ahead and applied recursively to 60 min. Compared with
Eulerian persistence and the rainymotion Dense optical-flow model.

## Numbers we use

- **Split by years** (section 3.1, p. 2635): 2006–2013 training, 2014–2015
  validation, 2016–2017 verification.
- **Training filter** (section 3.1, p. 2635): only May–September, and only
  time steps where rain above 0.125 mm/h covers at least 10% of the domain.
- **Test events** (section 3.3, p. 2636): 11 summer events from 2016–2017,
  "selected for covering a range of event characteristics with different
  rainfall intensity, spatial coverage, and duration"; the list is in Ayzel et
  al. (2019).
- **Verification thresholds:** CSI at 0.125, 1, 5, 10 and 15 mm/h; FSS with
  windows of 1, 5, 10 and 20 km (Figs. 3 and 6). Above 10 mm/h no method
  exceeds CSI 0.31 (section 4, p. 2637).

## Relevance to DECADE (D3)

Closest DL precedent for D3: a fixed set of about ten events, taken only from
the held-out period, chosen to span intensity, extent and duration. The three
axes match the D3 criteria. It also shows a simple objective pre-filter
(rain-covered fraction of the domain) and the threshold ladder up to 15 mm/h.

## Limits

The selection is described in words only, without numeric bounds. German
national composite; deterministic model.
