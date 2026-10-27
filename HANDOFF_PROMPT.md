# Handoff: dataset radar paneuropeo per pioggia e nowcasting ML

> Incolla questo testo come primo messaggio di una nuova sessione di Claude Code
> aperta nella radice del repo. I fatti verificati sui dati, i comandi e le
> convenzioni stanno in `CLAUDE.md`, che viene letto automaticamente: qui ci sono
> obiettivo, piano e stato. Rispondi in italiano.

---

## Ruolo e contesto

Riprendi un progetto avviato. Il codice di lettura ODIM, ritaglio, downscaling
(LK + interpolazione advettiva) e validazione esiste ed è testato su dati
sintetici e su 4 giorni reali (1–5/7/2024, Belgio). Il tuo compito è portarlo
verso l'obiettivo descritto sotto, in modo incrementale, senza riscrivere il codice.

**Prima di modificare qualsiasi cosa:**
1. Leggi `CLAUDE.md`, `README.md` e i moduli in `opera_ds/`.
2. Esegui `uv run python tests/test_synthetic.py <cartella>`: deve stampare
   `TUTTI I TEST SUPERATI`.
3. Riassumimi in 5–10 righe cosa hai capito e cosa intendi fare.

## Domanda di ricerca

Come passare da un luogo ben strumentato come il **Belgio** a **tutta l'Europa**
con un budget limitato. Il metodo deve usare **solo fonti paneuropee**: archivio
pubblico OPERA (ODYSSEY, CIRRUS, NIMBUS), pluviometri ECA&D, EURADCLIM. Non si
contattano i singoli servizi meteorologici nazionali: il metodo non scalerebbe.

Il **Belgio è il banco di prova**. L'utente ha un archivio storico belga che non
condivide: la validazione contro quell'archivio la esegue l'utente in locale. Il
codice di valutazione deve quindi accettare un dataset di riferimento esterno
tramite un `reader` iniettabile (il meccanismo esiste già in `run_validation`).

## Due linee di prodotto

### A. Dati per nowcasting ML, 1 km / 5 min (priorità)

Modello di riferimento: **IRENE** (FBK, arXiv 2609.17175, HuggingFace
`it4lia/irene`). Input: pioggia in mm/h a 1 km / 5 min, 6 frame passati, 12
futuri. Normalizzazione **fissa**: R → dBZ con Marshall-Palmer, taglio a
[0, 60] dBZ, scala lineare a [−1, 1]. Uno scarto di livello tra prodotti quindi
non viene assorbito.

- **Rifinitura e test:** CIRRUS DBZH, 1 km / 5 min, dal 7/2024 (circa 2,3 anni a
  fine 2026), convertito in R con lo stesso Marshall-Palmer di IRENE.
- **Pre-addestramento:** ODYSSEY DBZH 2012–7/2024 interpolato a 1 km / 5 min con
  `opera_ds`, così il modello resta identico tra le due fasi. Il
  pre-addestramento si fa comunque; l'esperimento sotto stabilisce **quanti anni**
  usare.

### B. Archivio di pioggia, 2 km / 15 min

ODYSSEY `RATE`/`ACRR` (2012 → 5/7/2024) più NIMBUS `RATE`/`ACRR` (5/7/2024 → oggi),
sulla stessa griglia. Non serve downscaling. Serve:
- pulizia dei punti anomali (vedi `CLAUDE.md`), sul modello di EURADCLIM;
- omogeneizzazione tra i due periodi **senza sovrapposizione**, ancorata ai
  pluviometri ECA&D;
- gestione delle finestre temporali diverse (vedi `CLAUDE.md`).

## Esperimento: curva di apprendimento sul pre-addestramento ODYSSEY

- **B0, riferimento:** solo CIRRUS, per lo stesso numero totale di passi delle
  altre varianti (stesso calcolo).
- **Pk, pre-addestramento:** ultimi k anni di ODYSSEY (k = 1, 2, 4, 8, 12, aggiunti
  all'indietro dal 2024), poi rifinitura sullo stesso insieme CIRRUS con lo stesso
  budget per tutti.
- **Controllo non stazionarietà:** una variante di pari dimensione presa dagli
  anni più vecchi (ad es. 2 anni 2013–2014 contro 2 anni 2022–2023).
- **Semi:** almeno 3 per variante.
- **Due misure per ogni k:** il modello pre-addestrato prima della rifinitura,
  valutato su CIRRUS (distanza tra domini), e quello dopo la rifinitura (il
  numero che decide). Ci si ferma quando la curva smette di salire o scende sotto
  B0 (trasferimento negativo).
- **Metriche:** CRPS, CSI e FSS in mm/h per lead time, bias di volume; poi la
  validazione sul Belgio, eseguita dall'utente.
- **Suddivisione CIRRUS:** blocchi mensili alternati (ad es. un mese su quattro
  per il test, uno per la validazione), con qualche giorno di margine tra i
  blocchi, così il test copre tutte le stagioni.

Scelte già fissate:
- **Variabile:** DBZH per entrambi i prodotti (riflettività massima), convertita
  in R con Marshall-Palmer.
- **Frame interpolati:** marcati con `alpha` (0 = frame ODYSSEY vero). In
  pre-addestramento entrano come input, ma la loss si calcola solo sui frame veri.
- **Campionamento:** finestre alla maniera di IRENE (24 × 256 × 256, scartate se
  hanno buchi temporali, campionamento per importanza verso la pioggia), scelte
  **su ODYSSEY a 2 km**. Si interpolano solo le finestre scelte, non tutto
  l'archivio.

Varianti da valutare dopo, non di default:
- quantile mapping climatologica ODYSSEY → CIRRUS prima del pre-addestramento
  (scarto osservato 3,5–5 dB), stimata su stagioni corrispondenti di anni diversi;
- ODYSSEY nativo a 2 km / 15 min come controllo del formato.

## Stato

**Fatto e verificato**
- Lettura reale di ODYSSEY (ODIM 2.0) e CIRRUS (ODIM 2.4): codifica, finestre,
  orientamento e griglie come atteso (dettagli in `CLAUDE.md`).
- Ritaglio in lettura allineato a 2 km (`--bbox`, `--buffer-km`), maschera del
  Belgio da Natural Earth, download dal bucket pubblico.
- Metriche di massa: controlli interni contro ODYSSEY, volumi e accumuli orari in
  R contro CIRRUS, errori per scala.
- Validazione 1–5/7/2024 sul Belgio (`out_val_2024-07_BEL_mass/`), con questi
  risultati:
  - ODYSSEY ha circa **metà del volume** di CIRRUS (scarto di 3,5–5 dB) e POD a
    10 dBZ di circa 0,69: è una differenza tra prodotti, già presente al pavimento;
  - **l'upscaling bilineare in dBZ perdeva circa l'8% del volume** rispetto a
    ODYSSEY (disuguaglianza di Jensen), e il blending in Z ne aggiungeva circa il
    6%. Ora i default sono upscaling conservativo + blending in R, che conservano
    il volume entro l'1% a ogni `alpha` (`out_val_mc_off/` contro `out_val_mc_on/`);
  - negli accumuli orari i metodi sono quasi equivalenti; negli istantanei a metà
    intervallo LK batte `nearest` (RMSE 12,7 contro 13,6 dBZ);
  - il campo interpolato ha circa un terzo dell'energia a piccola scala di CIRRUS
    (era il 18% prima della correzione di massa).

- Archivi ritagliati sul Belgio + 350 km dal bucket pubblico (lettura a pezzi
  dei GeoTIFF): ODYSSEY `DBZH_QIND` 9/2012–7/2024 in `data/odyssey_bel/`, CIRRUS
  `DBZH` 7/2024–10/2026 in `data/cirrus_bel/`.

**Non ancora fatto**
- Pipeline di addestramento e valutazione IRENE.
- Linea B: pulizia, omogeneizzazione, confronto con ECA&D.

## Prossimi passi (in quest'ordine)

1. ~~**Upscaling conservativo.**~~ Fatto: default `mass_correction=True`,
   `blend_space="R"`.
2. ~~**Output per il ML.**~~ Fatto: `alpha` nei metadati, `time_shift_min`
   (default 0 = etichette ODYSSEY, così α = 0 resta un frame vero), sottocomando
   `windows` con store Zarr in formato IRENE (`RR` mm/h float16).
3. ~~**Campionatore su ODYSSEY.**~~ Fatto: sottocomando `sample` → CSV per
   `windows`. Da decidere il budget di finestre (con i parametri di IRENE
   sarebbero circa 50 milioni su 12 anni) e, per la produzione, raggruppare le
   finestre per tempo per leggere ogni frame una volta sola.
4. **Dati CIRRUS per la rifinitura.** Scarico, conversione in R, suddivisione a
   blocchi mensili, stesso formato Zarr.
5. **Esperimento della curva di apprendimento.** Prima una prova piccola (k = 1,
   un seme) per stimare tempi e costi, poi la serie completa.
6. **Linea B.** Pulizia dei punti anomali, omogeneizzazione con ECA&D, confronto
   con EURADCLIM dove si sovrappone.

## Regole di lavoro

- **Dopo ogni modifica** riesegui il test sintetico.
- **Per ogni cambio di default** mostra il confronto delle metriche prima/dopo in
  una tabella stratificata per `alpha`.
- **Non sovrascrivere** output o archivi esistenti senza chiedere.
- **Run lunghi e download grandi:** stima tempo e spazio su disco e chiedi
  conferma prima di lanciarli.
- **Ambiguità sui dati:** se i dati reali contraddicono quanto scritto qui o in
  `CLAUDE.md`, fermati e dimmelo prima di adattare il codice.
- **Fonti:** mai proporre archivi nazionali come input del metodo; al più come
  validazione facoltativa.

## Domande aperte

- Quanto peggiora IRENE togliendo anni di dati (domanda posta agli autori nel
  webinar, risposta non nota).
- Esistono dati paralleli ODYSSEY/NIMBUS o ODYSSEY/CIRRUS oltre i 4 giorni
  dell'archivio pubblico? Andrebbe chiesto a support.opera@eumetnet.eu.
- Da quali radar provengono i volumi che CIRRUS estrapola con LK (commento nei
  file `how/comment`)? Si presume Spagna, non verificato.
