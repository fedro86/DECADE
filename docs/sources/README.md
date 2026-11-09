# Sources

Literature behind the choices of the project: one summary per article, report
or dataset paper.

- **Every method choice that rests on a number** (a threshold, a parameter, a
  classification rule) starts with a literature search. `docs/method.md` cites
  the summaries here, so that no number in the method is unexplained.
- **File names:** `YEAR - AUTHOR - TITLE`, with the surname of the first author
  and the title as published, without characters that Windows does not accept
  in file names (`: / \ ? * " < > |`). Example:
  `2013 - Goudenhoofdt - Statistical characteristics of convective storms in Belgium derived from volumetric weather radar observations.md`.
- **The articles are not shared.** Put the PDF next to its summary with the
  same name; git ignores every file in this folder except the `.md` files, so
  each person keeps their own copy.
- **Paywalled articles:** if an article cannot be downloaded automatically,
  download it yourself into this folder under any name; the summary step
  renames it.
- **The summaries are shared.** Write them in your own words, with at most a
  few short quotes, and say whether the full text or only the abstract was read.

## Template

```markdown
# <Title>

- **Authors, year, venue:** <…>
- **Link:** <DOI or URL>
- **Access:** open / paywalled; licence if stated
- **Read:** full text / abstract only (and where the rest comes from)

## What it is

Two or three sentences: data, region, period, method.

## Numbers we use

- <value>: <what it means, where in the paper (section, table, page)>

## Relevance to DECADE

Which ticket or decision it informs, and how.

## Limits

What does not transfer to our data (region, product, resolution, period).
```

## Index

Every person keeps their own PDFs, so the list says where each one comes from.
**Open** articles can be downloaded directly; **to download** ones are
paywalled or blocked for automatic download: get them through your institution
and put them in this folder with the name of their summary.

| summary | topic | DOI or link | PDF |
|---|---|---|---|
| 1995 - Steiner | convective / stratiform classification | [10.1175/1520-0450(1995)034<1978:CCOTDS>2.0.CO;2](https://doi.org/10.1175/1520-0450(1995)034%3C1978:CCOTDS%3E2.0.CO;2) | to download (paywall); summary from the full text (sections 1, 4–6) |
| 2002 - Gabella | cleaning: original of the Gabella texture filter | [ERAD 2002, 305–311](https://web.archive.org/web/20170809110607/https://www.copernicus.org/erad/online/erad-305.pdf) | free copy via the Internet Archive (the ERAD address is dead); summary from the full text |
| 2002 - Peura | cleaning: image-processing detectors (speckle, emitters, sun, ships, birds) | [ERAD 2002, 312–317](https://web.archive.org/web/2023/https://www.copernicus.org/erad/online/erad-312.pdf) | free copy via the Internet Archive (the ERAD address is dead); summary from the full text |
| 2012 - Wagner | cleaning: fixed clutter and spokes from long-term frequency maps | [10.5194/hess-16-4101-2012](https://doi.org/10.5194/hess-16-4101-2012) | open, CC BY 3.0; summary from the full text |
| 2013 - Goudenhoofdt | convective / stratiform classification | [10.1175/JAMC-D-12-079.1](https://doi.org/10.1175/JAMC-D-12-079.1) | to download (paywall); summary from the full text (sections 1–3, 4c) |
| 2013 - Heistermann | cleaning: wradlib, software of the Gabella and `histo_cut` filters | [10.5194/hess-17-863-2013](https://doi.org/10.5194/hess-17-863-2013) | open, CC BY 3.0; summary from the full text and the wradlib documentation (9/11/2026) |
| 2016 - Foresti | nowcasting verification in the Benelux | [10.5194/hess-20-505-2016](https://doi.org/10.5194/hess-20-505-2016) | open ([PDF](https://hess.copernicus.org/articles/20/505/2016/hess-20-505-2016.pdf)); summary from the full text |
| 2016 - Saltikoff | cleaning: interference from wireless devices (RLAN) | [10.1175/BAMS-D-15-00048.1](https://doi.org/10.1175/BAMS-D-15-00048.1) | free copy in the [NOAA repository](https://repository.library.noaa.gov/view/noaa/15308); summary from the full text |
| 2018 - Poelman | convective / stratiform classification | [EUMETNET report](https://www.eumetnet.eu/wp-content/uploads/2019/01/Daily_convective_precipitation_Maps_OPERA.pdf) | open; summary from the full text |
| 2019 - Saltikoff | OPERA composites: compositing rule, central quality control | [10.3390/atmos10060320](https://doi.org/10.3390/atmos10060320) | open, CC BY 4.0 (blocked for automatic download); summary from the full text |
| 2020 - Imhoff | nowcasting verification in the Benelux | [10.1029/2019WR026723](https://doi.org/10.1029/2019WR026723) | to download (blocked for automatic download; open access, CC BY); summary from the full text (sections 1, 2.2, 3.2) |
| 2022 - Dixon | convective / stratiform classification; bright band; test on the 2D OPERA mosaic | [10.1175/JTECH-D-22-0018.1](https://doi.org/10.1175/JTECH-D-22-0018.1) | open copy on [OSTI](https://www.osti.gov/pages/servlets/purl/1897074); summary from the full text (sections 1–3c, 3f, 4a, 5c, 6) |
| 2022 - Ośródka | cleaning: RADVOL-QC algorithms on single-radar volumes (spikes, clutter, non-meteorological echoes) | [10.5194/amt-15-261-2022](https://doi.org/10.5194/amt-15-261-2022) | open, CC BY 4.0; summary from the full text |
| 2023 - Overeem | cleaning of the OPERA composite (EURADCLIM): Gabella, satellite mask, static clutter | [10.5194/essd-15-1441-2023](https://doi.org/10.5194/essd-15-1441-2023) | open, CC BY 4.0; summary from the full text |
| 2023 - Perschke | convective / stratiform classification | [10.5194/egusphere-2023-1907](https://doi.org/10.5194/egusphere-2023-1907) | open, CC BY 4.0; summary from the full text |
| 2023 - RMI | RADCLIM product: radars, gauges, compositing, time convention, grid | [user guide, version 2](https://opendata.meteo.be/cases/202107/radclim_userguide.pdf) | open; summary from the full text |
| 2024 - EUMETNET | OPERA CIRRUS product: compositing rule, time window | [product sheet 2.0](https://eumetnet.eu/wp-content/uploads/2024/06/OPERA_Max-Reflectivity_Product-Sheet_Ed-2.0.pdf) | open; summary from the full text |
| 2024 - Radojevic | OPERA CIRRUS and ODYSSEY: time windows, configuration | [OPERA note, ed. 2.0](https://eumetnet.eu/wp-content/uploads/2024/06/OPERA5_Report_Cirrus-vs-Odyssey_Ed-2.0.pdf) | open; summary from the full text |

When a PDF marked "to download" is added, rewrite its summary from the full
text and update its row.
