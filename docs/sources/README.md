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
| 1993 - Rosenfeld | level correction: probability matching of radar reflectivity to gauge rain, wet fraction matched first | [10.1175/1520-0450(1993)032<0050:GPMRBR>2.0.CO;2](https://doi.org/10.1175/1520-0450(1993)032%3C0050:GPMRBR%3E2.0.CO;2) | to download (AMS, blocked for automatic download); summary from the full text (scanned) |
| 1995 - Steiner | convective / stratiform classification | [10.1175/1520-0450(1995)034<1978:CCOTDS>2.0.CO;2](https://doi.org/10.1175/1520-0450(1995)034%3C1978:CCOTDS%3E2.0.CO;2) | to download (paywall); summary from the full text (sections 1, 4–6) |
| 2002 - Gabella | cleaning: original of the Gabella texture filter | [ERAD 2002, 305–311](https://web.archive.org/web/20170809110607/https://www.copernicus.org/erad/online/erad-305.pdf) | free copy via the Internet Archive (the ERAD address is dead); summary from the full text |
| 2002 - Peura | cleaning: image-processing detectors (speckle, emitters, sun, ships, birds) | [ERAD 2002, 312–317](https://web.archive.org/web/2023/https://www.copernicus.org/erad/online/erad-312.pdf) | free copy via the Internet Archive (the ERAD address is dead); summary from the full text |
| 2005 - Charba | cleaning: discard of reflectivity ≥ 75 dBZ without lightning (NOAA LAMP) | [NOAA VLab](https://vlab.noaa.gov/documents/6609493/36173392/LAMP_radqc_paper_AMS2005_final.pdf) | free copy, no licence stated; summary from the full text |
| 2006 - Bøvith | cleaning: clutter on a radar composite with the NWC SAF precipitating-clouds product (DMI) | [author copy, DTU](https://www2.imm.dtu.dk/pubdb/edoc/imm4661.pdf) | free copy, no licence stated; summary from the full text |
| 2008 - Silberstein | calibration: stable ground-clutter targets to monitor radar calibration (relative calibration adjustment) | [10.1175/2008JTECHA1063.1](https://doi.org/10.1175/2008JTECHA1063.1) | submitted manuscript on [NASA NTRS](https://ntrs.nasa.gov/citations/20080045517), public use permitted (the AMS site blocks automatic download); summary from the manuscript, one page missing |
| 2009 - Goudenhoofdt | level correction: radar–gauge merging in Belgium (mean-field bias to kriging with external drift) | [10.5194/hess-13-195-2009](https://doi.org/10.5194/hess-13-195-2009) | open (CC BY 3.0); summary from the full text |
| 2011 - Blair | cleaning: physical maximum of reflectivity in giant hail | [EJSSM 6(7)](https://ejssm.org/archives/wp-content/uploads/2021/09/vol6-7.pdf) | open e-journal; summary from the full text |
| 2012 - Gudmundsson | level correction: quantile mapping methods compared, dry days, extrapolation | [10.5194/hess-16-3383-2012](https://doi.org/10.5194/hess-16-3383-2012) | open (CC BY 3.0); summary from the full text |
| 2012 - Themeßl | level correction: empirical quantile mapping with frequency adaptation, 31-day windows, new extremes | [10.1007/s10584-011-0224-4](https://doi.org/10.1007/s10584-011-0224-4) | free PDF on SpringerLink (no open licence); summary from the full text |
| 2012 - Venema | bridge homogeneity: benchmark of homogenisation methods for monthly series, relative series, size of real breaks | [10.5194/cp-8-89-2012](https://doi.org/10.5194/cp-8-89-2012) | open (CC BY 3.0); summary from the full text |
| 2012 - Wagner | cleaning: fixed clutter and spokes from long-term frequency maps | [10.5194/hess-16-4101-2012](https://doi.org/10.5194/hess-16-4101-2012) | open, CC BY 3.0; summary from the full text |
| 2013 - Goudenhoofdt | convective / stratiform classification | [10.1175/JAMC-D-12-079.1](https://doi.org/10.1175/JAMC-D-12-079.1) | to download (paywall); summary from the full text (sections 1–3, 4c) |
| 2013 - Heistermann | cleaning: wradlib, software of the Gabella and `histo_cut` filters | [10.5194/hess-17-863-2013](https://doi.org/10.5194/hess-17-863-2013) | open, CC BY 3.0; summary from the full text and the wradlib documentation (9/11/2026) |
| 2013 - Maraun | level correction: quantile mapping across a scale gap inflates extremes and changes trends; correct the level or add a stochastic step | [10.1175/JCLI-D-12-00821.1](https://doi.org/10.1175/JCLI-D-12-00821.1) | free PDF on [GEOMAR OceanRep](https://oceanrep.geomar.de/id/eprint/21175) (no open licence); summary from the full text |
| 2013 - Scovell | cleaning: quality control of the OPERA data centre (ODYSSEY) | [AMS poster](https://ams.confex.com/ams/34Radar/webprogram/Manuscript/Paper155995/OPERA_QC_v1.pdf) | free copy, no licence stated; summary from the full text |
| 2014 - Delobbe | sea clutter at Jabbeke, polarimetric filtering at RMI (ERAD 2014 poster) | [RMI](https://meteo.be/uploads/media/60ddc37432cab/poster-delo-goud-erad-2014.pdf) | free copy, no licence stated; summary from the poster and the short abstract |
| 2014 - Ośródka | cleaning: RADVOL-QC algorithms of 2014 (spikes, speckle, beam blockage, quality index) | [10.1002/met.1323](https://doi.org/10.1002/met.1323) | to download (paywall); summary from the full text |
| 2015 - Wolff | calibration: relative calibration adjustment generalised from KPOL to the NPOL S-band radar (Iowa, intense anomalous propagation) | [10.1175/JTECH-D-13-00185.1](https://doi.org/10.1175/JTECH-D-13-00185.1) | to download (blocked for automatic download); summary from the full text |
| 2016 - Foresti | nowcasting verification in the Benelux | [10.5194/hess-20-505-2016](https://doi.org/10.5194/hess-20-505-2016) | open ([PDF](https://hess.copernicus.org/articles/20/505/2016/hess-20-505-2016.pdf)); summary from the full text |
| 2016 - Leijnse | Doppler and statistical clutter removal at KNMI, sea clutter (TR-355) | [KNMI](https://cdn.knmi.nl/knmi/pdf/bibliotheek/knmipubTR/TR355.pdf) | free copy, no licence stated; summary from the full text |
| 2016 - Ribeiro | bridge homogeneity: review of homogenisation tests (t-test, Wilcoxon–Mann–Whitney, SNHT, Pettitt) | [10.1016/j.pce.2015.08.007](https://doi.org/10.1016/j.pce.2015.08.007) | paywalled; accepted manuscript open in the [NOVA University Lisbon repository](https://run.unl.pt/handle/10362/76624) (CC BY-NC-ND 4.0); summary from part of the text |
| 2016 - Saltikoff | cleaning: interference from wireless devices (RLAN) | [10.1175/BAMS-D-15-00048.1](https://doi.org/10.1175/BAMS-D-15-00048.1) | free copy in the [NOAA repository](https://repository.library.noaa.gov/view/noaa/15308); summary from the full text |
| 2016 - Vaccarono | calibration: clutter, Sun and self-consistency monitoring of two operational C-band radars | [10.5194/amt-9-5367-2016](https://doi.org/10.5194/amt-9-5367-2016) | open, CC BY 3.0; summary from the full text |
| 2017 - Volosciuk | level correction: bias correction at the grid scale, then a separate stochastic step to the point scale | [10.5194/hess-21-1693-2017](https://doi.org/10.5194/hess-21-1693-2017) | open (CC BY 3.0); summary from the abstract, part of the introduction and part of the conclusions |
| 2018 - Poelman | convective / stratiform classification | [EUMETNET report](https://www.eumetnet.eu/wp-content/uploads/2019/01/Daily_convective_precipitation_Maps_OPERA.pdf) | open; summary from the full text |
| 2018 - VMM | bridge homogeneity: how VMM adjusted the radar to its gauges in 2018 (amqsf, 43 gauges, every 15 min) | [Flemish Government repository](https://themis-test.vlaanderen.be/files/1c4fe652-d653-11e9-99f3-0242ac1b0003/download) | open; summary from the VMM part in full |
| 2019 - Saltikoff | OPERA composites: compositing rule, central quality control | [10.3390/atmos10060320](https://doi.org/10.3390/atmos10060320) | open, CC BY 4.0 (blocked for automatic download); summary from the full text |
| 2020 - Hersbach | bridge homogeneity: ERA5 observing system by date (all-sky microwave imagers, US Stage IV), production streams, ERA5T | [10.1002/qj.3803](https://doi.org/10.1002/qj.3803) | open (CC BY), blocked for automatic download, downloaded by hand; summary from the full text |
| 2020 - Imhoff | nowcasting verification in the Benelux | [10.1029/2019WR026723](https://doi.org/10.1029/2019WR026723) | to download (blocked for automatic download; open access, CC BY); summary from the full text (sections 1, 2.2, 3.2) |
| 2020 - RMI | bridge homogeneity: published precipitation trends at Uccle, 1981–2019 | [Klimaatrapport 2020](https://www.meteo.be/resources/misc/climate_report/KlimaatRapport-2020.pdf) | open; summary from chapter 1.1 |
| 2020 - WMO | bridge homogeneity: guidelines; t-test for a break at a known date, ratio series for precipitation | [WMO-No. 1245](https://library.wmo.int/idurl/4/57130) | free; blocked for automatic download, copy from a public mirror; summary from chapters 2, 3 and 5 |
| 2021 - Fluck | cleaning: values above 70 dBZ discarded in French and German composites | [10.5194/nhess-21-683-2021](https://doi.org/10.5194/nhess-21-683-2021) | open, CC BY 4.0; summary from the full text |
| 2021 - Imhoff | level correction: climatological day-of-year radar adjustment factors (CARROTS, Netherlands) | [10.5194/hess-25-4061-2021](https://doi.org/10.5194/hess-25-4061-2021) | open (CC BY 4.0); summary from the full text |
| 2021 - Muñoz-Sabater | level correction: ERA5-Land, how its precipitation is made, accumulation convention | [10.5194/essd-13-4349-2021](https://doi.org/10.5194/essd-13-4349-2021) | open (CC BY 4.0); summary from the full text |
| 2022 - Dixon | convective / stratiform classification; bright band; test on the 2D OPERA mosaic | [10.1175/JTECH-D-22-0018.1](https://doi.org/10.1175/JTECH-D-22-0018.1) | open copy on [OSTI](https://www.osti.gov/pages/servlets/purl/1897074); summary from the full text (sections 1–3c, 3f, 4a, 5c, 6) |
| 2022 - Grosemans | bridge homogeneity: VMM radars and gauges (parliamentary answer, 2022) | [Flemish Parliament](https://docs.vlaamsparlement.be/files/pfile?id=1810499) | open; summary from the full text |
| 2022 - Hänsler | level correction: quantile mapping of radar extremes (RADKLIM) to station statistics | [10.5194/hess-26-5069-2022](https://doi.org/10.5194/hess-26-5069-2022) | open (CC BY 4.0); summary from the full text |
| 2022 - Lavers | level correction: ERA5 daily precipitation against 5,637 gauges, wet bias, extremes, seasons | [10.1002/qj.4351](https://doi.org/10.1002/qj.4351) | open (CC BY-NC-ND 4.0), blocked for automatic download; summary from the full text |
| 2022 - Ośródka | cleaning: RADVOL-QC algorithms on single-radar volumes (spikes, clutter, non-meteorological echoes) | [10.5194/amt-15-261-2022](https://doi.org/10.5194/amt-15-261-2022) | open, CC BY 4.0; summary from the full text |
| 2022 - VMM | VMM raster service: series, units, radars of the composite | [waterinfo.be manual 02/2022](https://waterinfo.vlaanderen.be/download/9f5ee0c9-dafa-46de-958b-7cac46eb8c23?dl=0) | open; summary from the full text |
| 2023 - Overeem | cleaning of the OPERA composite (EURADCLIM): Gabella, satellite mask, static clutter | [10.5194/essd-15-1441-2023](https://doi.org/10.5194/essd-15-1441-2023) | open, CC BY 4.0; summary from the full text |
| 2023 - Perschke | convective / stratiform classification | [10.5194/egusphere-2023-1907](https://doi.org/10.5194/egusphere-2023-1907) | open, CC BY 4.0; summary from the full text |
| 2023 - RMI | RADCLIM product: radars, gauges, compositing, time convention, grid | [user guide, version 2](https://opendata.meteo.be/cases/202107/radclim_userguide.pdf) | open; summary from the full text |
| 2023 - van Dorland | bridge homogeneity: observed precipitation change in the Netherlands (KNMI'23) | [KNMI report WR23-02](https://www.knmi.nl/research/publications/knmi-national-climate-scenarios-2023-for-the-netherlands) | open; summary from section 3.2.2 only |
| 2024 - EUMETNET | OPERA CIRRUS product: compositing rule, time window | [product sheet 2.0](https://eumetnet.eu/wp-content/uploads/2024/06/OPERA_Max-Reflectivity_Product-Sheet_Ed-2.0.pdf) | open; summary from the full text |
| 2024 - Lussana | bridge homogeneity: drift of ERA5 annual precipitation against homogenised gauge grids (Alps, Italy) | [10.1002/asl.1239](https://doi.org/10.1002/asl.1239) | open (CC BY), blocked for automatic download, copy from the [University of Milan repository](https://hdl.handle.net/2434/1048648); summary from the full text |
| 2024 - Radojevic | OPERA CIRRUS and ODYSSEY: time windows, configuration | [OPERA note, ed. 2.0](https://eumetnet.eu/wp-content/uploads/2024/06/OPERA5_Report_Cirrus-vs-Odyssey_Ed-2.0.pdf) | open; summary from the full text |
| 2024 - Soci | bridge homogeneity: ERA5 observing system over time, production streams, precipitation | [10.1002/qj.4803](https://doi.org/10.1002/qj.4803) | open (CC BY), blocked for automatic download, copy from the [NOAA repository](https://repository.library.noaa.gov/view/noaa/68132); summary from the parts on observations and precipitation |
| 2025 - OPERA | #88: release 2025b of 18/11/2025, CIRRUS 1.5.0 (compositing search distance, satellite filter) | [opera-releases](https://github.com/opera-radar/opera-releases/tree/main/release-notes) | public GitHub repository, no licence stated; summary from the full text |
| 2025 - Overeem | bridge homogeneity: KNMI gauge-adjusted radar product and its use of the Belgian radars (dated changes) | [10.5194/essd-17-4715-2025](https://doi.org/10.5194/essd-17-4715-2025) | open, CC BY 4.0; summary from the full text |
| 2025 - Wood | level correction: ERA5, ERA5-Land, CERRA-Land and CHELSA precipitation against gauges | [10.5194/hess-29-4153-2025](https://doi.org/10.5194/hess-29-4153-2025) | open (CC BY 4.0); summary from the full text |
| 2026 - Camilletti | IRENE: training cubes, normalisation, model, afCRPS loss, verification | [10.48550/arXiv.2609.17175](https://doi.org/10.48550/arXiv.2609.17175) | open, CC BY-SA 4.0; summary from the full text |
| 2026 - ECMWF | bridge homogeneity: ERA5 and ERA5-Land production experiments and known issues, 2012–2026 | [ERA5 data documentation](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation) and pages listed in the summary | open web pages, read on 11/11/2026 |
| 2026 - OPERA | #88: release 2026b of 2/11/2026, Belgian Doppler-filtered DBZH no longer delivered | [opera-releases](https://github.com/opera-radar/opera-releases/tree/main/release-notes) | public GitHub repository, no licence stated; summary from the full text |
| 2026 - RMI | bridge homogeneity: Uccle and Belgian precipitation, yearly 2012–2025 and summer months 2023–2026 | [RMI climatological overviews](https://www.meteo.be/nl/klimaat/klimaat-van-belgie/klimatologisch-overzicht) | open; summary from the overviews listed in it |
| 2026 - RMI and VMM | bridge homogeneity: dated changes of the Belgian radars and of the VMM series, 2016–2026 | URLs per row in the summary | open web pages and PDFs; read on 11/11/2026 |
| 2026 - wradlib | clutter from satellite cloud type (`classify.filter_cloudtype`) | [wradlib documentation](https://docs.wradlib.org/en/latest/notebooks/classify/clutter/clutter_cloud.html) | open, CC BY-SA 4.0 (code MIT); summary from the notebook and the code |

When a PDF marked "to download" is added, rewrite its summary from the full
text and update its row.
