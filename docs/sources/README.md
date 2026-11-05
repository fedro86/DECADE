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

| topic | summaries |
|---|---|
| convective / stratiform classification | Steiner 1995, Goudenhoofdt 2013, Poelman 2018, Perschke 2023 |
| nowcasting verification in the Benelux | Foresti 2016, Imhoff 2020 |
