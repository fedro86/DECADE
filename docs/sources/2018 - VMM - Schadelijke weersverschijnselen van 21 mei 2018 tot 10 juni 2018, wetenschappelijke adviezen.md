# Schadelijke weersverschijnselen van 21 mei 2018 tot 10 juni 2018 – Wetenschappelijke adviezen

- **Authors, year, venue:** Vlaamse Milieumaatschappij (VMM, Afdeling Operationeel Waterbeheer, Dienst Hoogwaterbeheer) and Royal Meteorological Institute (RMI), 2018. Compiled scientific advice for the Flemish Government (calamity fund): VMM reports of 6 June and 31 August 2018 ("Stormperiode 22 mei - 1 juni 2018" and its follow-up), RMI letters of 7 June and 18 September 2018.
- **Link:** [themis-test.vlaanderen.be file 1c4fe652](https://themis-test.vlaanderen.be/files/1c4fe652-d653-11e9-99f3-0242ac1b0003/download) (document repository of the Flemish Government)
- **Access:** open; no licence stated.
- **Read:** the VMM part in full for the radar method (sections 1, 3, 5 and Bijlage I of the first VMM report; section 3 of the follow-up); the RMI letters and the municipality tables only skimmed.

## What it is

Two VMM reports that decide which Flemish municipalities passed the calamity thresholds (30 mm/h, 65 mm/24 h at the time) during the convective storms of 22 May – 9 June 2018, from VMM gauges and radar. Bijlage I is the only public text found that names the method VMM used to adjust radar images to its gauges. Note that in 2018 the radar images are said to come from the RMI ("bron: KMI"), not from a VMM composite.

## Numbers we use

All page numbers are those of the first VMM report ("Stormperiode 22 mei - 1 juni 2018"); read on 11/11/2026.

- Radar source: "radarbeelden (bron: KMI)", recalibrated with the VMM gauge network (section 3, p. 4); in Bijlage I, "radarcomposietbeelden met een temporele resolutie van 5 minuten (bron: KMI)" that combine several radars (p. 14). The radars are not named.
- Adjustment: 5-min radar images first aggregated to 15 min, then "geherkalibreerd" against the gauges with the **adaptive multiquadric surface fitting** algorithm; 1 h and 24 h sums then built with a 15-min sliding window (Bijlage I, p. 14). This is very likely the method behind the `*_amqsf` series of the VMM raster service (see `2026 - RMI and VMM - Belgian radar network changes 2016–2026.md`); the report does not use that name.
- Gauges: 15-min series of the VMM network of 43 gauges; only the 41 with at most 5% missing values in the period are used (Bijlage I, p. 14; conclusion p. 13).
- Measurement height "ca. 1500 m" for the radar data; reflectivity-to-rain conversion called uncertain, no Z–R relation given (Bijlage I, p. 14).
- Grid: 529 m × 529 m cells (~28 ha) (footnote 1, section 4, p. 7).
- Known bias: the adjusted images "zeer waarschijnlijk" overestimate rain in the cores of intense summer storms (e.g. 159.2 mm/h at Kalmthout), which the gauges cannot correct because none lay in the cores (section 4, p. 7).
- Radar–gauge check per event: linear regression of radar against gauge accumulations with a 95% interval, used to class municipalities as "waarschijnlijk", "vermoedelijk" or "weinig waarschijnlijk" (Bijlage I, figure 7).

## Relevance to DECADE

H3 (#20), whether VMM is homogeneous across 7/2024: this is the baseline description of VMM's gauge adjustment in 2018 (RMI radar images, 15-min AMQSF recalibration, 43 gauges). It applies to the accumulations, not to the radar-only 5-min intensity `SRI_1km_cappi` that the project uses. It shows that the processing chain changed at least once before our VMM period: in 2018 the input was an RMI composite on a 529 m grid, while the 2022 service documentation describes a VMM composite of Helchteren, Jabbeke and Herwijnen at 1 km height (`2022 - VMM - Open punt- en rasterdata voor waterinfo.be.md`). The date of that switch is not given anywhere we read.

## Limits

- A calamity-fund report, not a product description: no Z–R relation, clutter filter, radar list or software version.
- Describes the 2018 analysis method; whether the same AMQSF settings were used operationally, and until when, is not stated.
- Radar-only intensity (what the project reads) is not discussed.
