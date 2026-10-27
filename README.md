# Dataset radar paneuropeo da OPERA

Strumenti per costruire, a partire dall'archivio pubblico EUMETNET OPERA, dati
radar omogenei per tutta l'Europa, usando il Belgio come banco di prova. Due linee
di prodotto:

- **dati per nowcasting ML a 1 km / 5 min**: CIRRUS (dal 7/2024) per rifinitura e
  test, ODYSSEY (2012–2024, 2 km / 15 min) interpolato a 1 km / 5 min per il
  pre-addestramento;
- **archivio di pioggia a 2 km / 15 min**: ODYSSEY più NIMBUS, sulla stessa
  griglia.

Obiettivo, piano ed esperimento sono descritti in `HANDOFF_PROMPT.md`; i fatti
verificati sui prodotti OPERA (griglie, codifiche, finestre temporali, periodi
disponibili) sono in `CLAUDE.md`.

## Metodo di downscaling (ODYSSEY → 1 km / 5 min)

**Griglie.** CIRRUS usa lo stesso dominio e la stessa proiezione LAEA di ODYSSEY,
a risoluzione doppia (3800×4400 contro 1900×2200): ogni pixel a 2 km corrisponde
a 2×2 pixel a 1 km. Il pixel fine `j` si trova alla coordinata `(j+0.5)/2 − 0.5`
della griglia grossolana (centri allineati). La validazione controlla
l'allineamento dai metadati `where` e lo scrive in `grid_check.txt`.

**Moto (Lucas-Kanade, a 2 km).** Stesso schema di `pysteps.motion.lucaskanade`:
feature di Shi-Tomasi → LK piramidale → controllo forward-backward → rimozione
outlier locali → declustering → interpolazione IDW + smoothing. I vettori di
ogni coppia vengono riusati per le coppie adiacenti (contesto di ±1 coppia).
Due differenze rispetto ai default di pysteps, entrambe emerse dai test:

- LK lavora su un campo **passa-alto** (σ = 15 px): la crescita/decadimento delle
  celle non viene scambiata per moto. Sul caso sintetico l'errore medio sul moto
  scende da 5,1 a 2,0 px/15 min.
- 5000 feature invece di 1000, pensate per il dominio europeo intero.

Il backend `pysteps` resta disponibile (`"lk": {"backend": "pysteps"}`).

**Interpolazione temporale.** Per una frazione `a` dell'intervallo:

```
F(x, t0 + a·15') = (1−a) · F0(x − a·V) + a · F1(x + (1−a)·V)
```

Le traiettorie vengono integrate col metodo del punto medio sul campo stazionario
a 2 km. I valori si campionano **una sola volta** dal campo a 2 km nei punti di
partenza dei pixel a 1 km, quindi upscaling e avvezione sono un'unica
interpolazione bilineare. Ad `a = 0` il metodo si riduce al semplice upscaling.

**Conservazione della massa (default).** Due scelte, valutate in R con
Marshall-Palmer (Z = 200 R^1,6):

- **Upscaling conservativo** (`mass_correction=True`). Interpolare in dBZ perde
  pioggia, perché R è convessa in dBZ. Per ogni pixel a 2 km si calcola una
  correzione in dB che rende la media in R dei suoi 4 sottopixel uguale a R del
  pixel ODYSSEY; la correzione segue i valori anche lungo le traiettorie.
- **Blending in R** (`blend_space="R"`). La media tra F0 e F1 avvettati si fa in
  R. Un pixel asciutto pesa 0, quindi i bordi delle celle non scendono sotto
  soglia come succede mediando in dB. Mediando in Z, invece, si aggiunge pioggia
  dove F0 e F1 avvettati non coincidono, perché R è concava in Z.

Sui 4 giorni reali (Belgio, 380 coppie) il volume dell'output rispetto a
(1−a)·V(F0) + a·V(F1):

| | α = 0 | α = 1/3 |
|---|---|---|
| bilineare, blending in Z (default precedente) | 0,918 | 0,959 |
| correzione + blending in Z | 0,999 | 1,065 |
| **correzione + blending in R (default)** | **0,999** | **1,011** |

Rispetto a CIRRUS la correzione raddoppia l'energia a piccola scala (da 0,17 a
0,33) e riduce l'RMSE degli accumuli orari a 25 km (da 1,12 a 1,07 mm), con un
RMSE in dBZ leggermente più alto (12,90 contro 12,79 a metà intervallo). Sul caso
sintetico il blending in R ha RMSE in dBZ più alto di quello in Z a metà
intervallo (3,7 contro 2,9) ma CSI migliore. Le varianti restano selezionabili
come metodi `lk:Z` e `lk:dB`, o con `mass_correction=false` nella configurazione.

**Copertura radar.** La copertura non viene avvettata. Dove un'eco entra da fuori
copertura si usa la sola sorgente valida, o in mancanza di entrambe
l'interpolazione euleriana.

## Validazione

Il confronto è con CIRRUS, nei soli giorni in cui i due prodotti coesistono
nell'archivio pubblico (1–5/7/2024), per tre metodi:

| metodo | cosa fa |
|---|---|
| `nearest` | frame ODYSSEY più vicino, upscalato (persistenza) |
| `linear` | media euleriana di F0 e F1 |
| `lk` | interpolazione advettiva (varianti `lk:Z`, `lk:dB`) |

Le metriche sono stratificate per `alpha`, cioè la posizione nell'intervallo di
15 min. **L'errore ad `alpha = 0` è il "pavimento"**: lì non c'è interpolazione
temporale, quindi misura upscaling e differenze tra i prodotti. Quello che conta
per l'interpolazione temporale è l'errore *in più* agli altri istanti.

File prodotti:

- `summary.csv`: bias, MAE, RMSE e correlazione in dBZ sui pixel bagnati;
  POD/FAR/CSI/frequency bias a 10/20/30/40 dBZ; FSS a 20/30 dBZ; rapporto di
  energia alle piccole scale; rapporto dei volumi e errori di R (mm/h) a 1, 2, 5,
  10 e 25 km (colonne `r*`);
- `mass_internal.csv`: conservazione rispetto a ODYSSEY stesso, senza le
  differenze tra prodotti (volume dell'output contro (1−a)·V(F0) + a·V(F1), e
  media dei blocchi 2×2 ad `a = 0`);
- `accum_1h.csv`: accumuli orari contro CIRRUS sugli istanti disponibili, per
  scala;
- `per_time.csv`, `qq.json`, `grid_check.txt` e i grafici.

R si ottiene con Marshall-Palmer (Z = 200 R^1,6), limitando i dBZ a 55.

**Sfasamento temporale.** ODYSSEY usa la finestra [NT−10, NT+5], CIRRUS
(NT−10, NT]: a parità di etichetta, ODYSSEY "vede" circa 2,5 min più tardi.
`--shifts` prova più sfasamenti e `time_shift.png` mostra quale minimizza
l'errore.

## Uso

Dipendenze gestite con `uv` (`pyproject.toml`): `uv sync`, poi sempre
`uv run python ...`.

```bash
# dati dal bucket pubblico ORD
uv run python scripts/fetch_ord_archive.py --product DBZH_QIND \
  --start 2024-07-01 --end 2024-07-06 --out data/odyssey
uv run python scripts/fetch_ord_archive.py --product DBZH \
  --start 2024-07-01 --end 2024-07-06 --out data/cirrus

# maschera del Belgio sulla griglia CIRRUS a 1 km
uv run python scripts/make_region_mask.py --ref "data/cirrus/OPERA@20240702T1205@0@DBZH.h5" \
  --country BEL --out data/mask_BEL_1km.npy

# validazione, con ritaglio in lettura (Belgio + 200 km)
uv run python scripts/opera_ds_cli.py validate \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" --cirrus-glob "data/cirrus/*@DBZH.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --start 2024-07-01 --end 2024-07-06 \
  --bbox 2.5 49.45 6.45 51.55 --buffer-km 200 --region-mask data/mask_BEL_1km.npy \
  --shifts 0 -2.5 -5 2.5 --methods nearest linear lk lk:dB \
  --pair-stride 1 --workers 12 --out out_val

# produzione
uv run python scripts/opera_ds_cli.py downscale \
  --odyssey-glob "data/odyssey/*@DBZH_QIND.h5" \
  --time-regex "@(\d{8}T\d{4})@" --time-format "%Y%m%dT%H%M" \
  --start 2024-07-01 --end 2024-07-02 \
  --bbox 2.5 49.45 6.45 51.55 --buffer-km 200 --workers 8 --out out_ds
```

- `--time-regex` deve catturare il timestamp nel nome del file; se lo si omette,
  il tempo viene letto dagli attributi ODIM, più lentamente.
- `--bbox` e `--buffer-km` ritagliano in lettura una finestra allineata a 2 km,
  identica per le due griglie. Se `--region-mask` è sulla griglia intera, viene
  ritagliata allo stesso modo.
- `--config config_example.json` cambia i parametri di `DownscaleConfig` e di LK.
- Gli accumuli orari della validazione richiedono `--pair-stride 1`.

Output della produzione: ODIM HDF5 2.4, DBZH uint16 (gain 0.01, offset −50),
gzip.

## Test

`uv run python tests/test_synthetic.py out_test/` genera un campo multiscala con
moto noto (traslazione + rotazione, ~60 km/h) e crescita/decadimento. Lo degrada a
"ODYSSEY" (2 km, 15 min, sfasato di +2,5 min) e lo usa come "CIRRUS" a 1 km /
5 min. Il test verifica che:

- lo sfasamento stimato sia −2,5 min;
- LK batta `nearest` e `linear` in RMSE a tutti gli istanti interpolati;
- LK batta `linear` in CSI a 30 dBZ;
- con i default il volume di pioggia resti entro il 2% di quello di "ODYSSEY" a
  ogni `alpha`, e l'errore sui blocchi 2×2 ad `alpha = 0` sia sotto l'1%.

## Risultati sui dati reali (1–5/7/2024, Belgio)

- ODYSSEY ha circa **metà del volume di pioggia** di CIRRUS (scarto di 3,5–5 dB su
  tutti i quantili, POD a 10 dBZ circa 0,69). È una differenza tra prodotti, già
  presente al pavimento.
- L'upscaling bilineare in dBZ perdeva circa l'**8% del volume** rispetto a
  ODYSSEY; con i default attuali la perdita è sotto l'1% (vedi sopra).
- Negli accumuli orari i metodi sono quasi equivalenti; negli istantanei a metà
  intervallo LK batte `nearest` (RMSE 12,9 contro 13,8 dBZ con i default).
- Il campo interpolato ha circa un terzo dell'energia a piccola scala di CIRRUS.
- ODYSSEY DBZH contiene punti anomali fino a 128 dBZ (clutter): ogni conversione
  in R va limitata, la validazione usa 55 dBZ.

## Limiti

- **Il dettaglio sotto i 2 km non viene creato.** Per recuperare la variabilità
  servirebbe un downscaling stocastico (es. RainFARM) o appreso.
- **La dinamica dentro i 15 min è sintetica**: due frame su tre sono combinazioni
  di quelli veri. Per il ML vanno marcati e la loss va calcolata sui frame veri.
- **La sovrapposizione ODYSSEY/CIRRUS è di soli 4 giorni estivi** nell'archivio
  pubblico, senza i CIRRUS ai quarti d'ora; per la pioggia è nulla.
- **Il moto è stazionario nell'intervallo.** Con sistemi molto veloci (oltre
  ~120 km/h) LK può agganciarsi a un match sbagliato.
- **Lo sfasamento non è ancora applicato in produzione.**
