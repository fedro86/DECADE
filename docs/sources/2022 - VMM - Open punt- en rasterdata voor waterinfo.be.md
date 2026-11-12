# Open punt- en rasterdata voor waterinfo.be

- **Authors, year, venue:** Vlaamse Milieumaatschappij (VMM) with the Hydrological Information Centre (MOW-HIC), user manual of the waterinfo.be web services, version 02/2022 (13 pages).
- **Link:** [waterinfo.vlaanderen.be download 9f5ee0c9](https://waterinfo.vlaanderen.be/download/9f5ee0c9-dafa-46de-958b-7cac46eb8c23?dl=0); the same file is also served as [download e402c149](https://waterinfo.vlaanderen.be/download/e402c149-17da-49db-adb8-de688fe4a394?dl=0) (byte-identical, checked 11/11/2026).
- **Access:** open; the data fall under the Flemish free-reuse licence recorded in `docs/data.md` (VMM row).
- **Read:** full text; section 2.5 (raster data) in detail.

## What it is

The manual of the KiWIS web services behind waterinfo.be: point data (gauges) and raster data (radar). Section 2.5 is the only VMM text found that describes the radar composite. `docs/data.md` already uses it for the service URL, the series names and the radar list; this summary records only what that row does not.

## Numbers we use

Read on 11/11/2026.

- Composite of 3 radars: Helchteren (VMM), Jabbeke (RMI), Herwijnen (KNMI); all images at 1 km height, 5-min resolution (section 2.5, p. 9). Already in `docs/data.md`.
- "De data werden afgetoetst en verbeterd met de 43 pluviografen die VMM beheert" (section 2.5, p. 9). The sentence covers all images served, including the intensity; it does not say whether the 5-min intensity itself is adjusted. `docs/data.md` notes that no gauge-adjusted intensity is listed, and VMM's own series names (`SRI_1km_cappi` without `_adj`) agree.
- Table 3 (p. 10) lists `ts_id` 911010 as **`DPSRI_1km_cappi`**, while the GetRasterFile example on p. 11 and today's series list use `SRI_1km_cappi` for the intensity. The manual does not explain the prefix; "DP" could stand for dual polarisation, but this is not stated.
- Reliability series: for the 1 h and 24 h adjusted sums VMM publishes NSE (Nash–Sutcliffe efficiency) and RMSE against its 43 gauges, `ts_id` 6790010, 6791010 (1 h) and 6792010, 6793010 (24 h) (section 2.5.4, Table 4, p. 12). On 11/11/2026 the service declares these four series only from 6/6/2018 to 12/10/2019, so this quality check cannot be used for 2021–2026.
- Raster responses to `getRasterTimeseriesValues` are "HDF5 Opera" files (section 2.5.1, p. 10).

## Relevance to DECADE

H3 (#20): the service manual is the primary VMM description of the product the project uses. It says nothing about processing changes or versions. The NSE/RMSE series would have been a direct homogeneity diagnostic, but they stop in October 2019. The `DPSRI` → `SRI` naming difference shows that series names have changed at least once without a change of `ts_id`; whether the processing changed with the name is unknown.

## Limits

- A data-access manual: no Z–R relation, clutter filter, compositing rule, gauge-adjustment method or version history.
- Version 02/2022: it describes the service at that date only. The 2022 parliamentary answer names only Jabbeke and Helchteren for VMM (`2022 - Grosemans - Overstromingen juli 2021 Limburg - Netwerk pluviometers - Dossiers.md`).
