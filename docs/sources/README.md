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
| 2013 - Goudenhoofdt | convective / stratiform classification | [10.1175/JAMC-D-12-079.1](https://doi.org/10.1175/JAMC-D-12-079.1) | to download (paywall); summary from the full text (sections 1–3, 4c) |
| 2016 - Foresti | nowcasting verification in the Benelux | [10.5194/hess-20-505-2016](https://doi.org/10.5194/hess-20-505-2016) | open ([PDF](https://hess.copernicus.org/articles/20/505/2016/hess-20-505-2016.pdf)); summary from the full text |
| 2018 - Poelman | convective / stratiform classification | [EUMETNET report](https://www.eumetnet.eu/wp-content/uploads/2019/01/Daily_convective_precipitation_Maps_OPERA.pdf) | open; summary from the full text |
| 2020 - Imhoff | nowcasting verification in the Benelux | [10.1029/2019WR026723](https://doi.org/10.1029/2019WR026723) | to download (blocked for automatic download; open access, CC BY); summary from the full text (sections 1, 2.2, 3.2) |
| 2022 - Dixon | convective / stratiform classification; bright band; test on the 2D OPERA mosaic | [10.1175/JTECH-D-22-0018.1](https://doi.org/10.1175/JTECH-D-22-0018.1) | open copy on [OSTI](https://www.osti.gov/pages/servlets/purl/1897074); summary from the full text (sections 1–3c, 3f, 4a, 5c, 6) |
| 2024 - EUMETNET | OPERA CIRRUS product: compositing rule, time window | [product sheet 2.0](https://eumetnet.eu/wp-content/uploads/2024/06/OPERA_Max-Reflectivity_Product-Sheet_Ed-2.0.pdf) | open; summary from the full text |
| 2023 - Perschke | convective / stratiform classification | [10.5194/egusphere-2023-1907](https://doi.org/10.5194/egusphere-2023-1907) | open, CC BY 4.0; summary from the full text |

When a PDF marked "to download" is added, rewrite its summary from the full
text and update its row.
