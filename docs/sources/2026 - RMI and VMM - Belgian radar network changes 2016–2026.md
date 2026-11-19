# Belgian radar network and VMM radar product: dated changes 2016–2026

- **Authors, year, venue:** compiled from public web pages and documents of the RMI (meteo.be), VMM (vmm.vlaanderen.be, waterinfo.be, the VMM KiWIS raster service), KNMI, and the Flemish Government document repository; all read on 11/11/2026.
- **Link:** URLs per row in the table below.
- **Access:** open web pages and PDFs; no licence stated except for the VMM data (`docs/data.md`, VMM row).
- **Read:** every page and document in the table in full, except the calamity-fund advices (only the radar paragraphs). Documents with their own summary: `2018 - VMM - Schadelijke weersverschijnselen van 21 mei 2018 tot 10 juni 2018, wetenschappelijke adviezen.md`, `2022 - Grosemans - Overstromingen juli 2021 Limburg - Netwerk pluviometers - Dossiers.md`, `2022 - VMM - Open punt- en rasterdata voor waterinfo.be.md`, `2025 - Overeem - The Dutch real-time gauge-adjusted radar precipitation product.md`.

## What it is

A dated list of everything public that we found on the radars behind the VMM composite (Helchteren, Jabbeke, Herwijnen) and on the rest of the Belgian network (Wideumont, Zaventem), and on changes to VMM's radar processing, to judge whether VMM can be a stable bridge across July 2024. Searches covered meteo.be news, newsletters and FAQ; VMM press, product and service pages; waterinfo.be; the Flemish Parliament and Government repositories; KNMI news; ESSD/HESS and general web search for papers on the VMM radar product.

## Numbers we use

Dated events. "KiWIS" = the series list of the VMM raster service, `request=getTimeseriesList&station_name=Vlaanderen_VMM` with `returnfields=ts_id,ts_name,ts_path,coverage` (declared first and last data, read 11/11/2026). Series names are VMM's; their meaning is our reading and is not documented by VMM.

| date | radar / product | event | source |
|---|---|---|---|
| 11/2001 | Wideumont (RMI) | inaugurated, the first RMI radar | [meteo.be, Vervanging van de weerradar in Wideumont](https://www.meteo.be/nl/info/nieuwsoverzicht/vervanging-van-de-weerradar-in-wideumont) |
| 2012 | Jabbeke (RMI) | installed; dual-pol Doppler | [meteo.be, radar network](https://www.meteo.be/en/about-rmi/observation-network/radarnetwerk); see also `2014 - Delobbe - Polarimetric radar observations in Belgium.md` |
| 23/10/2016 | Helchteren (VMM) | press release "Nieuwe neerslagradar Houthalen-Helchteren operationeel" (dated 23 Oct 2016 in the PDF, 22-10-2016 on the web page); 65 m tower, 4.2 m antenna, accurate measurement up to 120 km, one image every 5 min; "together with the RMI radar in Jabbeke" covers all of Flanders; 43 VMM gauges "immediately combined" with the radar images | [VMM press release, PDF](https://vmm.vlaanderen.be/pers/persbericht_neerslagradarhouthalen-helchteren_tw.pdf/@@download/file); [Engineeringnet, 25/10/2016](https://engineeringnet.be/nl/nieuws/item/11728/vmm-heeft-neerslagradar-in-houthalen-helchteren-in-gebruik-genomen); [integraalwaterbeleid.be, "Dec. 2016 – ingehuldigd"](https://www.integraalwaterbeleid.be/nl/bekkens/maasbekken/in-de-kijker/neerslagradartoren-in-houthalen-helchteren-ingehuldigd) |
| 25/2/2017, 1/3/2017 | VMM product | first data of `PAC_1h_1km_cappi_amqsf` and `PAC_15m_1km_cappi_amqsf` | KiWIS |
| 12/5/2017 | Herwijnen (KNMI) | officially opened; replaces De Bilt, whose view was blocked by tall buildings | [KNMI news, 12/5/2017](https://knmi.nl/over-het-knmi/nieuws/knmi-opent-neerslagradar-in-herwijnen) |
| 9/9/2017 | VMM product | first declared data of the radar-only intensity `SRI_1km_cappi` (`ts_id` 911010) and of the generic raster series 6490010 | KiWIS (already in `docs/data.md`) |
| 6/6/2018 | VMM product | first data of `PAC_1h_1km_cappi_adj`, `PAC_24h_1km_cappi_adj`, of the NSE/RMSE reliability series and of `PAC_1h_1km_cappi_adj-Storm` | KiWIS |
| 5–6/2018 | VMM analysis | storm analysis uses radar images "bron: KMI", 529 m grid, recalibrated at 15 min with adaptive multiquadric surface fitting (AMQSF) against 43 VMM gauges | `2018 - VMM - …` summary |
| 12/10/2019 | VMM product | last data of the four NSE/RMSE series | KiWIS |
| early 6/2021 and early 9/2021 | Jabbeke | radome cleaned (dirt "can have a negative influence on the measurements"); radome panel seals renewed because water was leaking in | [meteo.be newsletter 2021](https://www.meteo.be/nl/info/nieuwsbrief/artikels-2021/spectaculaire-onderhoud-van-kmi-weerradar-in-jabbeke) (year from the newsletter section) |
| 16/7/2021 | VMM product | last data of `PAC_1h_1km_cappi_adj-Storm` | KiWIS |
| 2021 | VMM analysis | July 2021 report uses "aan het VMM-pluviometernetwerk geassimileerde neerslagradarbeelden", 1 h and 24 h, sliding window of 5 min (15 min in 2018) | [VMM (2021), Uitzonderlijke neerslag 14 tot 16 juli 2021](https://themis-test.vlaanderen.be/files/61b85cb6d129f6000c000ee6/download), section 2 |
| 30/9/2021 | RMI composite | RMI composite for the calamity fund made of Jabbeke, Wideumont, Zaventem, Helchteren and Avesnois, combined with gauges | [RMI advice of 30/9/2021](https://themis-test.vlaanderen.be/files/61b85cc0d129f6000c000ef4/download), p. 2 |
| 24/1/2022 | VMM product | last data of `PAC_1h_1km_cappi_amqsf` | KiWIS |
| early 2022 | VMM product | VMM uses Jabbeke and Helchteren; RMI uses five radars; VMM radar serviced twice a year by the manufacturer; 52 VMM gauges | `2022 - Grosemans - …` summary |
| 02/2022 | VMM product | service manual: composite of Helchteren, Jabbeke, Herwijnen at 1 km height; `ts_id` 911010 listed as `DPSRI_1km_cappi` | `2022 - VMM - Open punt- en rasterdata voor waterinfo.be.md` |
| 7/4/2022 | Wideumont | last images of the old single-pol radar, "after more than 26 million rotations" | [meteo.be newsletter 2022](https://www.meteo.be/nl/info/nieuwsbrief/artikels-2022/een-nieuwe-hoogtechnologische-radar-in-wideumont) |
| 13–14/4/2022 | Wideumont | new transmitter/receiver, antenna and radome hoisted onto the existing tower; during the works the RMI composite used Jabbeke, Zaventem, Helchteren and Neuheilenbach (Germany) | [meteo.be news, 14/4/2022](https://www.meteo.be/nl/info/nieuwsoverzicht/vervanging-van-de-weerradar-in-wideumont); [French version](https://www.meteo.be/fr/infos/actualite/remplacement-du-radar-de-wideumont) |
| 11/5/2022 21:25 UTC | Wideumont | first precipitation image of the new dual-pol radar; maximum range 250 km; data then integrated into RMI products "in de weken erop" (no date) | [meteo.be news](https://www.meteo.be/nl/info/nieuwsoverzicht/de-eerste-beelden-van-de-vernieuwde-weerradar-in-wideumont); newsletter 2022 above |
| 19/9/2022 | VMM product | first data of `PAC_15m_1km_cappi_adj` | KiWIS |
| 10/4/2023, 18/4/2023 | VMM product | first data of the "widget" 24 h and 1 h series | KiWIS |
| 8/2023 | Wideumont | starts contributing to the KNMI real-time product | `2025 - Overeem - …` summary |
| 9/9/2024 | Jabbeke | KNMI ingests almost twice as many Jabbeke elevation scans | `2025 - Overeem - …` summary |
| 1/10/2024 | VMM product | first data of `SRI_1km_cappi_BEJAB0924issue` and the three `PAC_*_BEJAB0924issue` series | KiWIS (already in `docs/data.md`) |
| 5/11/2024 | Belgian radars | KNMI ingests a few more scans of all Belgian radars | `2025 - Overeem - …` summary |
| 20/3/2025 | VMM product | last data of `PAC_15m_1km_cappi_amqsf` | KiWIS |
| 24/3/2025 | VMM product | first data of `PAC_1d_1km_cappi_adj_new` (a `PAC_1d_1km_cappi_adj_old` series exists with no data) | KiWIS |
| 1/1/2026 | VMM product | first data of `PAC_24h_1km_cappi_adj_1d` (daily) | KiWIS |
| undated (read 11/11/2026) | Zaventem | single-pol; "a new dual-polarization is foreseen in the near future"; operated by Skeyes "since 2013" | [meteo.be, Weather radars](https://www.meteo.be/en/instruments) |
| undated (read 11/11/2026) | Helchteren | VMM page: dual-pol; with Jabbeke, images every 5 min "accurate to 500 m"; accurate up to 120 km; part of OPERA | [VMM, Hoe werkt een neerslagradar?](https://vmm.vlaanderen.be/feiten-cijfers/water/overstromingen/overstromingen-voorspellen-hoe-doe-je-dat/hoe-werkt-een-neerslagradar) |

Other facts:

- Rasters served today: HDF5 with `what/object` `COMP` and `what/source` `CTY:227`, no list of contributing radars and no processing attributes; grid 900 × 780 at 500 m in an azimuthal equidistant projection (raster of `SRI_1km_cappi` and `PAC_1h_1km_cappi_adj` for 10/11/2026 11:00 UTC, read 11/11/2026). So the served files cannot tell which radars contributed. The `BEJAB0924issue` raster for the same time was refused ("does not exist or is not available for access").
- RMI calamity-fund advices for summer 2024 storms still use Jabbeke, Wideumont and Zaventem for hail probability ([RMI advice, VR 2025 1403 DOC.0133/11](https://themis.vlaanderen.be/files/31320500-fd99-11ef-92ee-a9f77261d5d4/download), section 2).

## Relevance to DECADE

H3 (#20), is VMM homogeneous across 7/2024?

- **Radars of the VMM composite:** no public source documents a hardware change, replacement, dual-pol upgrade or long outage of **Helchteren** (since 10/2016), **Jabbeke** (since 2012; only the 2021 radome cleaning and seal repair) or **Herwijnen** (since 5/2017) in 2023–2026. Wideumont (replaced 4–5/2022) and Zaventem are not in the VMM composite according to both 2022 VMM-side sources.
- **VMM processing:** no public source documents a change of Z–R relation, clutter filtering, compositing or CAPPI height of `SRI_1km_cappi`, in any year. No change is documented for 2023–2026. The only public hints of change are series names: an AMQSF family that ends between 1/2022 and 3/2025, new 15-min and daily series (9/2022, 3/2025, 1/2026), and the `BEJAB0924issue` family from 1/10/2024. None starts or ends in July 2024. The `BEJAB0924issue` family points to a Jabbeke problem from September 2024; the KNMI paper dates a change in the Jabbeke data it receives to 9/9/2024. Both are after the ODYSSEY → CIRRUS switch, so they affect the CIRRUS side of the bridge: CIRRUS months from 9/2024 should be compared with VMM with care, or checked separately.
- **Composite membership is uncertain:** Herwijnen is in the 02/2022 manual but not in the early-2022 parliamentary answer nor on today's VMM radar page. When Herwijnen entered, and whether it is still used, must be asked to VMM.
- **The earliest VMM data differ:** in 2018 VMM's analyses used RMI radar images on a 529 m grid; today's composite is VMM's own. This matters only if VMM data before 2021 are ever used.
- Absence of documentation is not proof of homogeneity: Helchteren is serviced twice a year by the manufacturer, and any recalibration would not be public. A data check (VMM against gauges or RADCLIM, before and after 7/2024 and 9/2024) is still needed.

## Limits

- Mostly press and web pages: they give hardware dates, not processing details.
- KiWIS coverage dates are what the service declares today; they say nothing about gaps, and series names are not documented.
- The Jabbeke problem behind `BEJAB0924issue` is not described anywhere we found. Questions that only VMM can answer: the radars in the composite and since when (Herwijnen); the Z–R relation, clutter filter and CAPPI method of `SRI_1km_cappi` and any change since 2017; what `DPSRI`, `amqsf`, `_new`/`_old` and `BEJAB0924issue` mean and which periods they cover; Helchteren calibration and maintenance log, especially around 7/2024 and 9/2024.
