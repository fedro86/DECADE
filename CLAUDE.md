# CLAUDE.md

Dataset radar paneuropeo da OPERA: pioggia a 2 km / 15 min e dati per nowcasting
ML a 1 km / 5 min. Obiettivo, piano e stato sono in `HANDOFF_PROMPT.md`; qui ci
sono fatti verificati sui dati, comandi e convenzioni. Rispondi in italiano.

## Vincoli del progetto

- **Solo fonti paneuropee** (OPERA, ECA&D, EURADCLIM). Gli archivi nazionali non
  entrano nel metodo: al più come validazione facoltativa.
- **Il Belgio è il banco di prova.** L'archivio belga dell'utente è privato: la
  validazione su di esso la esegue l'utente, tramite un `reader` iniettabile.
- **Credenziali in `.env`** (`ARCODATAHUB_USERNAME`, `ARCODATAHUB_ACCESS_KEY`,
  `METEOGATE_USERNAME`, `METEOGATE_ACCESS_KEY`). Leggile da script, non stamparle
  mai: per mostrare il file usa `sed -E 's/=.*/=<…>/' .env`.

## Comandi

```bash
uv sync                                                    # ambiente (Python 3.12, vedi pyproject.toml)
uv run python tests/test_synthetic.py <cartella>           # deve stampare TUTTI I TEST SUPERATI
uv run python scripts/fetch_ord_archive.py --product DBZH_QIND --start 2024-07-01 --end 2024-07-06 --out data/odyssey
uv run python scripts/make_region_mask.py --ref <file CIRRUS .h5> --country BEL --out data/mask_BEL_1km.npy
```

Validazione sul Belgio (circa 21 min con 12 processi per 4 giorni):

```bash
uv run python scripts/opera_ds_cli.py validate \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" --cirrus-glob "data/cirrus/*@DBZH.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --start 2024-07-01 --end 2024-07-06 \
  --bbox 2.5 49.45 6.45 51.55 --buffer-km 200 --region-mask data/mask_BEL_1km.npy \
  --shifts 0 -2.5 -5 2.5 --methods nearest linear lk lk:dB \
  --pair-stride 1 --workers 12 --out <cartella nuova>
```

- Usa sempre `uv run python`, mai `python`.
- `ls` è un alias di `eza` e ne cambia l'output: negli script usa `find`.
- Download grandi e run lunghi: stima tempo e spazio, poi chiedi conferma.

## Codice

| file | contenuto |
|---|---|
| `opera_ds/odim_io.py` | `read_odim_composite(path, quantity, extent=None)`, ritaglio (`bbox_extent`, `extent_window`, `crop_where`), scrittura ODIM, `index_files` |
| `opera_ds/motion.py` | LK su OpenCV (schema pysteps), passa-alto, cache dei vettori sparsi |
| `opera_ds/interp.py` | `PairInterpolator.get(alpha, method)`; metodi `nearest`, `linear`, `lk`, con suffisso `:Z` o `:dB` |
| `opera_ds/pipeline.py` | `FrameSource`, `run_downscaling`, `run_downscaling_parallel` (accetta `reader`) |
| `opera_ds/validate.py` | metriche in dBZ, in R per scala, conservazione interna, accumuli orari |
| `opera_ds/windows.py` | finestre per il ML: `Window`, `make_window`, `WindowStore` (Zarr in formato IRENE), `dbz_to_rr` |
| `opera_ds/sampling.py` | scelta delle finestre su ODYSSEY a 2 km: `SamplerConfig`, `sample_block`, `block_times` |
| `scripts/opera_ds_cli.py` | sottocomandi `downscale`, `validate`, `sample` e `windows`; `--bbox`/`--buffer-km` ritagliano in lettura e ritagliano anche `--region-mask` |
| `scripts/fetch_ord_archive.py` | download dal bucket pubblico ORD |
| `scripts/fetch_cog_crop.py` | download di un'area sola: legge a pezzi i GeoTIFF (o, se mancano, scarica l'HDF5 intero e lo ritaglia in memoria) e scrive HDF5 ritagliati con l'offset in `where` |
| `scripts/make_region_mask.py` | maschera di un paese (Natural Earth 1:10m) sulla griglia di un file ODIM |

- `reader(path, quantity) -> Frame` è iniettabile ovunque; con il ritaglio si usa
  `functools.partial(read_odim_composite, extent=...)`, che è serializzabile per
  il multiprocessing.
- Il ritaglio va espresso in metri dall'angolo UL e allineato a 2000 m, così
  resta 2:1 tra le griglie a 2 km e a 1 km.
- Output della validazione: `summary.csv` (dBZ e colonne `r*` in R per scala),
  `per_time.csv`, `mass_internal.csv`, `accum_1h.csv`, `qq.json`, `grid_check.txt`
  e i grafici.
- Gli accumuli orari richiedono `--pair-stride 1`.
- `pipeline.output_times(t0, cfg, shift)` è l'unica regola tra etichette di
  output e `alpha`. Con shift 0 (default) α = 0, 1/3, 2/3; con −2,5 (convenzione
  CIRRUS) α = 1/6, 1/2, 5/6 e nessun frame è un ODYSSEY vero.
- **Costi misurati (16 core, disco locale):**
  - `sample` sull'intero dominio: 5 giorni in 43 s con 10 processi, quindi circa
    10 h per i 12 anni di ODYSSEY;
  - con i parametri di IRENE escono circa 56.000 finestre in 5 giorni (circa 50
    milioni su 12 anni): `m`, `q_min`, `step_px` e `step_t` vanno tarati su un
    budget;
  - `windows`: circa 8 s di CPU e 1,1–1,6 MB a finestra 24 × 256 × 256. Ogni
    finestra rilegge e decomprime per intero i suoi 9–11 file ODYSSEY: per la
    produzione conviene raggruppare le finestre per tempo e stimare il moto una
    volta sola per coppia.
- L'indice dei file arriva ai processi una volta sola (`_map` con initializer
  nella CLI).
- Il seme di `sample` genera un generatore indipendente per blocco
  (`SeedSequence.spawn`). Nel codice di IRENE, con un seme fissato, ogni
  finestra riceverebbe lo stesso numero casuale.

## Fonti dati (verificate a ottobre 2026)

### Bucket pubblico ORD

`https://s3.waw3-1.cloudferro.com/openradar-archive/` (CC BY 4.0, nessuna
credenziale). Chiavi: `AAAA/MM/GG/OPERA/COMP/OPERA@AAAAMMGGTHHMM@0@<prodotto>.{h5,tiff}`.
L'archivio fino al 31/12/2025 è stato caricato a febbraio 2026 (HDF5 + GeoTIFF);
**dal 1/1/2026 il bucket si aggiorna quasi in tempo reale ma con i soli HDF5**
(GeoTIFF presenti solo il 19/5 e il 26/10/2026, parziali). Ci sono giorni
mancanti (ad es. 1/10/2012, 15/10/2024; CIRRUS manca dal 7 al 17/10/2024, quando
c'è solo NIMBUS, e il 13–15/5/2025 non c'è nessun prodotto).

| prodotto | file | griglia | passo | periodo nel bucket |
|---|---|---|---|---|
| ODYSSEY riflettività massima | `DBZH_QIND.h5` | 1900 × 2200, 2 km | 15 min | 4/9/2012 → 5/7/2024 05:45 |
| ODYSSEY tasso di pioggia | `QIND_RATE.h5` | 1900 × 2200, 2 km | 15 min | stesso |
| ODYSSEY accumulo 1 h | `ACRR_QIND.h5` | 1900 × 2200, 2 km | 15 min | stesso |
| CIRRUS riflettività massima | `DBZH.h5` | 3800 × 4400, 1 km | 5 min | dall'1/7/2024 |
| NIMBUS tasso di pioggia | `RATE.h5` | 1900 × 2200, 2 km | 15 min | dal 5/7/2024 06:00 |
| NIMBUS accumulo 1 h | `ACRR.h5` | 1900 × 2200, 2 km | 15 min | stesso |

- **Sovrapposizione:** riflettività solo 1–5/7/2024, e in quei giorni ai quarti
  d'ora c'è solo ODYSSEY (mancano i CIRRUS delle :00, :15, :30, :45). Per la
  pioggia la sovrapposizione è **nulla**. ODYSSEY è stato prodotto fino al
  30/10/2024, ma l'archivio pubblico non lo contiene dopo il 5/7/2024.
- **Stessa proiezione e stessi angoli per tutti:**
  `+proj=laea +lat_0=55.0 +lon_0=10.0 +x_0=1950000.0 +y_0=-2100000.0 +units=m +ellps=WGS84`,
  angolo UL a −39,536°, 67,023°. Riga 0 = nord (verificato: correlazione 0,88
  contro 0,39 col campo capovolto).
- **Codifica:** float64, `gain` 1, `offset` 0, `nodata` −9999000, `undetect`
  −8888000. ODYSSEY ha `quantity` in `datasetN/what` (ODIM 2.0), CIRRUS e NIMBUS
  in `datasetN/dataN/what` (ODIM 2.4). CIRRUS ha valori fino a −32 dBZ.
- **Finestre temporali per l'etichetta NT:**
  - ODYSSEY `DBZH` e `RATE`: [NT−10, NT+5] (ad es. 11:50–12:05 per le 12:00);
  - CIRRUS `DBZH`: (NT−10, NT] (11:55:01–12:05 per le 12:05);
  - NIMBUS `RATE`: istantaneo a NT;
  - ODYSSEY `ACRR`: NT−55 → NT+5; NIMBUS `ACRR`: NT−60 → NT.
- **Pioggia ODYSSEY `ACRR`:** le zone asciutte sono 0, `undetect` non è usato.
  NIMBUS usa `undetect`.
- **NIMBUS** dichiara Marshall-Palmer nei file (`zr_a` = 200, `zr_b` = 1,6) e ha
  un campo di qualità `quality1`.
- **Punti anomali in ODYSSEY:** ad es. il 3/7/2024 alle 12:00 c'è un gruppo di 4
  pixel fino a 75.000 mm/h, alla riga 1444 e colonna 899 della griglia a 2 km,
  dentro il ritaglio di lavoro del Belgio. Lo stesso punto vale **128 dBZ** in
  `DBZH_QIND`; sul dominio intero si trovano spesso da 4 a oltre 100 pixel
  ≥ 100 dBZ. Serve una soglia più una maschera dei punti persistenti. Qualsiasi
  conversione in R va limitata (si usa 55 dBZ), altrimenti questi pixel dominano
  i volumi.
- **GeoTIFF (`.tiff`) accanto agli HDF5:** tiled 512 × 512, deflate, float32,
  con overview. Valori identici agli HDF5 (verificato su ODYSSEY 2013, 2018, 2024
  e su CIRRUS 1/7/2024), `undetect` → NaN. La georeferenziazione è sfasata di
  mezzo pixel (origine −1000/+1000 m a 2 km, −500/+500 a 1 km): la griglia si
  prende dall'HDF5 e si legge per indici. I tag CIRRUS non hanno `quantity`.
  Leggere a pezzi solo l'area del Belgio + 350 km costa 140–280 kB di rete a
  frame ODYSSEY contro circa 950 kB dell'HDF5 intero.
- **Archivi ritagliati locali (Belgio + 350 km, allineati a 2 km):**
  `data/odyssey_bel/` (righe 1053–1531, colonne 528–1027 a 2 km, circa 100 kB a
  frame) e `data/cirrus_bel/` (2106–3062, 1056–2054 a 1 km, circa 380 kB a
  frame). Si leggono con `read_odim_composite` come i file interi, anche con
  `extent`, purché l'estensione stia dentro il ritaglio. CIRRUS ha giorni
  incompleti (ad es. 192 frame su 288 il 2/7/2024). `cirrus_bel` contiene
  7/2024–12/2025 dai GeoTIFF (152.975 frame, 39 GB); il 2026 dagli HDF5 interi
  (ritagli verificati identici a quelli da GeoTIFF su due istanti del 2025).
- **HDF5 CIRRUS interi:** circa 2,2–2,8 MB, chunk 760 × 880 gzip 9 (l'area del
  Belgio tocca 6 chunk su 30). Lettura a pezzi via HTTP range verificata
  identica, ma con `urllib` lenta in parallelo (1,2 file/s); il download intero
  va a 16–20 file/s (circa 40 MB/s).
- **CIRRUS `how/comment`:** alcuni volumi sono estrapolati con LK da Météo-France
  (pysteps). Non è indicato quali radar.

### Altre fonti

- **API ORD su MeteoGate** (`https://api.meteogate.eu/eu-eumetnet-weather-radar`,
  OGC EDR): solo le **ultime 24 ore**, anche con la chiave (che alza il limite a
  2000 richieste l'ora). Utile per i metadati CIRRUS recenti, non per lo storico.
- **ArcoDataHub `opera-plus-it-vmi.zarr`** (FBK, CC BY-SA 4.0): VMI in dBZ, 1 km /
  5 min dall'1/7/2024, OPERA più radar DPC, in **EPSG:3035** 3819 × 4411 (non
  la griglia OPERA nativa). `_FillValue` −9999, `undetect` −9998. Un chunk è un
  frame intero (circa 100–130 MB compressi, circa 45 s a frame): leggere il solo
  Belgio costa come leggere tutta Europa.
- **RODEO-ML** (`s3://ecmwf-rodeo-benchmark`, object store ECMWF): solo accumuli
  di precipitazione a 1 h e 6 h, 2013–2023.
- **Open data RMI** (`opendata.meteo.be`, WMS `radar:belgian_rainfall_composite`):
  5 min, ma solo le ultime circa 13 ore. È un archivio nazionale: fuori dal metodo.
- **IRENE** (FBK): arXiv 2609.17175, HuggingFace `it4lia/irene`. Materiali del
  webinar in `/home/fedro/Code/personal/webinar-forecast-ai`.

## Convenzioni di metodo

- **Conversione in R:** Marshall-Palmer Z = 200 R^1,6, la stessa di NIMBUS e di
  IRENE. Nelle metriche in R i dBZ sono limitati a 55 (`r_cap_dbz`).
- **Conservazione della massa (default):** `mass_correction=True` (upscaling che
  preserva in R la media dei blocchi 2×2) e `blend_space="R"`. Sui 4 giorni il
  volume resta entro l'1% di quello ODYSSEY a ogni `alpha`; il blending in Z
  aggiunge circa il 6% e l'upscaling bilineare senza correzione ne toglie l'8%.
  Le varianti restano come metodi `lk:Z`, `lk:dB`.
- **Shift temporale:** ODYSSEY "vede" circa 2,5 min più tardi di CIRRUS a parità
  di etichetta. Sui 4 giorni gli accumuli sono poco sensibili allo shift.
