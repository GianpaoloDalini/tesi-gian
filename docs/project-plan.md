# Piano di progetto — Tesi magistrale

> **Documento vivo.** È la fonte di verità del progetto. Ogni decisione presa va
> registrata qui nello stesso commit in cui viene applicata. Le voci marcate
> `DA DEFINIRE` sono i vuoti aperti: nessuno va riempito con un'ipotesi
> plausibile, si riempiono solo con decisioni effettivamente prese.

**Ultimo aggiornamento:** 2026-08-11 · **Stato:** impianto sperimentale eseguito a
64px e 128px (14 run); prima bozza dell'idea di base e di RQ1 formulata (D-023),
in attesa del relatore e della revisione della letteratura per consolidarla

---

## 0. Anagrafica

| Voce | Valore |
|---|---|
| Autore | Gian |
| Corso | Laurea Magistrale in Ingegneria Informatica, LM-32 |
| Ateneo | Università degli Studi di Bergamo |
| Relatore | `DA DEFINIRE` (nome) — area: IA e informatica etica |
| Correlatore | `DA DEFINIRE` |
| Tipo di tesi | Sperimentale con componente analitico-etica |
| Sessione di laurea | Autunnale — gestita autonomamente da Gian, non tracciata qui |
| Lingua | Italiano |

---

## 1. Contesto

- **Area di ricerca:** intelligenza artificiale generativa applicata alla produzione
  artistica; intersezione tra machine learning, creatività computazionale ed etica.
- **Motivazione (bozza, D-023):** le rivendicazioni di "creatività" nei sistemi
  generativi (in particolare la CAN) guidano adozione, mercato e percezione
  pubblica senza un vaglio commisurato — né empirico (si autovalutano con metriche
  autoreferenziali) né teorico (non reggono a un confronto con criteri filosofici
  consolidati di cosa sia l'arte). L'etichetta "creativo" non è neutra: ha
  conseguenze su come pubblico e artisti percepiscono e valutano questi sistemi e
  il lavoro umano.
- **Contesto applicativo (bozza):** uso e presentazione pubblica/commerciale di
  sistemi generativi (in particolare CAN) come agenti "creativi" nella produzione
  artistica.
- **Due tesi che coesistono (D-024):** l'accessibilità che questi strumenti offrono
  a chi ha lacune tecniche è un beneficio genuino, **indipendente** dalla
  legittimità del processo con cui il modello sottostante è stato addestrato
  (V-007) — l'emozione che manca nel training di qualunque modello generativo
  (D-023, D-024) non è la stessa cosa dell'emozione che l'utente umano porta
  nell'uso dello strumento. Le due valutazioni vanno tenute distinte nel capitolo
  di discussione, non fuse: l'una non attenua l'altra.
- **Stakeholder:** artisti (sia chi usa questi strumenti per esprimersi, sia chi ha
  visto le proprie opere usate per l'addestramento senza consenso — due posizioni
  distinte, non sovrapponibili), ricercatori in creatività computazionale, chi si
  occupa di policy sul diritto d'autore, comunità ML. `DA RESTRINGERE`.

## 2. Definizione del problema

> Bozza del 2026-08-11 (D-023), emersa da un dialogo aperto e verificata contro
> fonti reali punto per punto — non dalla revisione sistematica della letteratura,
> che resta da fare (M1) e che può confermarla, correggerla o sostituirla.
> Fino ad allora va trattata come direzione di lavoro, non come conclusione.

- **Problema reale:** la rivendicazione di creatività della CAN (Elgammal et al.,
  2017) si basa su una metrica autoreferenziale — la testa di stile del proprio
  discriminatore, allenata insieme al generatore che valuta — non su una misura
  indipendente né su un criterio filosofico condiviso di cosa costituisca
  creatività o arte.
- **Limiti delle soluzioni esistenti:** `DA DEFINIRE` (esito della revisione, §4)
- **Opportunità di ricerca:** verificare quanto la rivendicazione di creatività
  della CAN regge a un confronto con una misura indipendente sugli stessi campioni
  (dato preliminare già raccolto, 0,28 contro 0,75 a 64px — non ancora confermato
  da un esperimento dedicato, vedi D-023) e con un criterio teorico esplicito
  (estetica simbolica di Langer: l'arte richiede emozione), per poi discutere le
  conseguenze etiche di una rivendicazione che non regge, in linea con la critica
  dell'antropomorfizzazione nella letteratura di etica dell'AI.

> Nota metodologica originale, ancora valida: questa sezione non si considera
> davvero chiusa prima di aver fatto la revisione della letteratura. Un problema
> definito prima di conoscere lo stato dell'arte è quasi sempre già risolto, oppure
> mal posto — per questo la bozza sopra resta marcata come tale.

## 3. Obiettivi

- **Obiettivo generale (bozza, D-023):** verificare se e quanto la rivendicazione
  di "creatività" della CAN regge a un confronto empirico indipendente e a un
  vaglio teorico esplicito, e discuterne le implicazioni etiche quando non regge.
- **Obiettivi specifici:** `DA DEFINIRE`
- **Deliverable concreti:**
  1. Elaborato di tesi (PDF).
  2. Repository riproducibile con codice e configurazioni.
  3. Risultati sperimentali tracciati su W&B.
  4. `DA DEFINIRE` — eventuale dataset o artefatto rilasciato.

### Domande di ricerca

| ID | Domanda | Come viene risposta | Stato |
|---|---|---|---|
| RQ1 | In che misura la creatività rivendicata dalla CAN (misurata dalla propria testa di stile) diverge da una misura indipendente sugli stessi campioni, e quali conseguenze etiche comporta presentare come "creativo" un sistema la cui creatività non è, in questo senso, affidabile né teoricamente fondata? | Confronto autovalutazione vs. giudice terzo (dato preliminare in `experiments/registry.md`, da consolidare); vaglio teorico via estetica simbolica di Langer e letteratura su antropomorfizzazione in etica dell'AI | bozza (D-023) — da affinare dopo M1 |

## 4. Stato dell'arte

- **Keyword:** `generative adversarial network`, `creative adversarial network`,
  `computational creativity`, `machine creativity`, `AI art`, `generative art`,
  `authorship AI`, `style ambiguity`. `DA AFFINARE`
- **Database:** Scopus, IEEE Xplore, ACM Digital Library, arXiv, Google Scholar,
  atti dell'ICCC (International Conference on Computational Creativity).
- **Criteri di inclusione/esclusione:** `DA DEFINIRE`
- **Lavori fondativi identificati:** vedi `thesis/references/bibliography.bib`
  (seed) e le schede in `docs/literature/`.
- **Gap individuato:** `DA DEFINIRE`

## 5. Metodologia

- **Impianto:** confronto controllato a due condizioni, **DCGAN → CAN**, a variabile
  indipendente singola (la funzione di perdita). Vedi ADR-0003 e D-010.
  Da ratificare col relatore.
- **Dataset:** **ArtBench-10**, sei stili di pubblico dominio (`ukiyo_e`,
  `renaissance`, `baroque`, `romanticism`, `realism`, `impressionism`), 64×64,
  30.000 immagini bilanciate. Vedi ADR-0004 e D-014.
- **Baseline:** DCGAN (Radford et al., 2016) come condizione di controllo, con
  generatore e backbone di discriminatore *identici* a quelli della CAN.
- **Metriche:** FID, Inception Score, entropia della posterior di stile, studio
  percettivo leggero. Ciascuna accompagnata dalla dichiarazione esplicita di cosa
  **non** misura: FID e IS misurano fedeltà e varietà, non creatività, e poggiano su
  una Inception addestrata su fotografie, non su dipinti.
- **Validazione:** stesso seed, stessi batch, stesso numero di epoche e stesso numero
  di campioni per la valutazione nelle due condizioni. Gli invarianti del disegno
  sperimentale sono verificati automaticamente da `tests/test_impianto.py`.
- **Ipotesi dichiarata a priori:** la CAN peggiora il FID e aumenta l'entropia di
  stile. Se si verifica, dimostra che fedeltà e ambiguità stilistica sono obiettivi
  in tensione — che è l'argomento del capitolo di discussione, non un fallimento.

## 6. Architettura

Definita, vedi `README.md` e `CLAUDE.md`.
Monorepo: `thesis/` (LaTeX) + `src/` (codice) + `configs/` + `docs/`.
Tracciamento su Weights & Biases; configurazioni via Hydra; bibliografia via Zotero.

## 7. Piano sperimentale

Configurazioni in `configs/experiment/`. I due run definitivi differiscono per **una
sola riga**: `override /model`.

**Nota sulla numerazione (corretta il 2026-08-11):** gli ID qui sotto ora
coincidono esattamente con i nomi dei file in `configs/experiment/`. Prima E3/E4
indicavano nel piano l'ablazione e lo studio percettivo, ma `e3-dcgan-128.yaml` ed
`e4-can-128.yaml` esistevano già con un altro significato (il confronto a 128px):
un'incoerenza che avrebbe confuso chiunque cercasse "E3" nel repo. L'ablazione e lo
studio percettivo sono ora **E6** ed **E7**.

| ID | File config | Obiettivo | Variabile indipendente | Run | Metriche | Stato |
|---|---|---|---|---|---|---|
| E0 | `e0-smoke` | Smoke test della pipeline su dati sintetici, CPU | — | 1 | nessuna | ✅ fatto |
| E1 | `e1-dcgan-baseline` | Condizione di **controllo**: DCGAN, 64px | loss avversaria pura | 4 (seed 1-4) | FID, IS, ambiguità (giudice terzo), copertura | ✅ **concluso 2026-08-03** |
| E2 | `e2-can-confronto` | Condizione **sperimentale**: CAN, 64px | + classificazione stile (D) e ambiguità (G) | 4 (seed 1-4) | idem | ✅ **concluso 2026-08-03** — 1 run collassato (`can-seed1`), escluso dalle medie |
| E3 | `e3-dcgan-128` | Condizione di controllo, **128px** | idem | 3 (seed 1-3) | idem | ✅ **concluso 2026-08-04** — vedi esito sotto |
| E4 | `e4-can-128` | Condizione sperimentale, **128px** | idem | 3 (seed 1-3) | idem | ✅ **concluso 2026-08-04** — vedi esito sotto |
| E5 | `e5-illustrativo-{64,128}` | **Illustrativo**, generatore condizionato per stile | — (fuori dal confronto) | 1+1 | nessuna (solo qualità visiva) | 64px concluso e valutato (2026-08-12); 128px in coda |
| E6 | `e6-ablazione-can-peso-zero` | Ablazione: CAN con `style_ambiguity_weight=0` | peso dell'ambiguità | 1 | FID, IS | concluso e valutato (2026-08-12) — risultato non atteso, vedi V-010 |
| E7 | — (non ancora creato) | Studio percettivo leggero sui campioni generati | condizione mostrata | — | giudizio umano | non avviato |

**E5 non fa parte del confronto comparativo E1-E4** (ADR-0003): architettura
diversa (il generatore riceve anche l'etichetta di stile), obiettivo diverso
(fedeltà allo stile richiesto invece di ambiguità), nessuna metrica quantitativa —
serve solo a produrre figure più nitide da mostrare come contrasto visivo. Dettagli
in D-022.

Dataset per E1-E4 ed E6: ArtBench-10, sei stili (D-017: `ukiyo_e`, `renaissance`,
`baroque`, `art_nouveau`, `expressionism`, `impressionism`), 30.000 immagini.

**Esito E1/E2 a 64px** (`experiments/registry.md`): l'ambiguità di stile sale come
atteso (0,682 → 0,750, gruppi non sovrapposti), ma **il FID non peggiora** (107,7 vs
107,3, indistinguibili) — l'ipotesi che la CAN costasse fedeltà è **falsificata** a
questa risoluzione. Un run CAN (`can-seed1`) è mode-collapsed (copertura 0,190),
escluso dalle medie con motivazione esplicita.

**Esito E3/E4 a 128px:** qui l'ipotesi **non è più falsificata** — FID 183,4 (CAN)
contro 117,8 (DCGAN), +55%, con ambiguità che sale di entità simile a 64px. I tre
seed CAN toccano il FID minimo tutti alla stessa epoca (20 su 100) e poi degradano
quasi monotonicamente: possibile instabilità del meccanismo di ambiguità che scala
con la risoluzione, ma **non ancora confermato** — serve l'ispezione visiva dei
campioni (V-009 in `docs/registro-decisioni.md`) prima di scriverlo in tesi.

**E1 ed E2 usano gli stessi seed**: a parità di seed le due condizioni partono
dagli stessi pesi e vedono gli stessi batch nello stesso ordine, quindi la
differenza nei risultati non è imputabile né all'inizializzazione né all'ordine dei
dati.

Tutto ciò che non è la variabile indicata resta **identico** fra E1 ed E2: generatore,
backbone del discriminatore, iperparametri, seed, epoche, numero di campioni per la
valutazione — verificato automaticamente da `tests/test_impianto.py` (78 test verdi).

E6 non è un esperimento ma un controllo di sanità, ancora da eseguire: con peso nullo
la CAN deve riprodurre la DCGAN.

**Nodo ancora aperto (Q2, punto 3):** per costruzione la CAN tende a peggiorare il
FID. Non è ancora stato deciso, prima di scrivere le conclusioni, quale esito si
considera "informativo" — va chiuso prima della stesura del capitolo dei risultati.

## 8. Pianificazione

> Le scadenze amministrative della sessione sono gestite autonomamente da Gian fuori
> da questo repository e non vengono tracciate qui, per scelta esplicita.

| Milestone | Descrizione | Stato |
|---|---|---|
| M0 | Infrastruttura del repository | ✅ fatto |
| M-A1 | Deposito titolo e relatore | ⬜ |
| M-A2 | Domanda definitiva | ⬜ |
| M3a | Pipeline sperimentale implementata e testata | ✅ fatto |
| M3b | Dataset preparato e smoke test superato | ✅ fatto |
| M4 | Run E1 ed E2 conclusi e registrati (64px) | ✅ fatto |
| M4b | Metriche calcolate, figure esportate (64px) | ✅ fatto |
| M4c | Impianto replicato a 128px, traiettoria valutata | ✅ fatto — V-009 aperta (ispezione visiva mancante) |
| M1 | Revisione della letteratura, gap definito | ⬜ in parallelo |
| M2 | Domande di ricerca approvate dal relatore | ⬜ vedi Q8 |
| M-E4 | Studio percettivo concluso | ⬜ |
| M5 | Prima stesura completa | ⬜ |
| M6 | Caricamento dell'elaborato | ⬜ |
| M7 | Discussione | — |

E1 ed E2 hanno un budget di epoche fisso e un checkpoint ripristinabile: se la qualità
a 100 epoche non è quella sperata, si scrive la tesi su quello che c'è e si discute il
limite, invece di rilanciare il training.

## 9. Rischi

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| Le metriche automatiche non misurano ciò che la tesi afferma di misurare | alta | alto | Dichiarare esplicitamente i limiti; affiancare valutazione qualitativa |
| Costi o quote di calcolo insufficienti per il training | media | alto | Risoluzione ridotta, dataset ristretto, checkpointing aggressivo |
| Sessioni cloud effimere che interrompono il training | alta | medio | Checkpoint frequenti su storage persistente |
| Licenza del dataset artistico incompatibile con l'uso o la pubblicazione | media | alto | Verificare i termini prima del download |
| Deriva del progetto verso la sola parte tecnica, perdendo il taglio etico | media | medio | Il capitolo di discussione è vincolante, non opzionale |
| Perdita di tracciabilità tra risultati e testo | media | alto | `experiments/registry.md` + regola del working tree pulito |

## 10. Struttura della tesi

Vedi `thesis/capitoli/`. Struttura provvisoria in 8 capitoli, da rivedere con il
relatore dopo M2.

---

## Registro delle decisioni

Il verbale completo — decisione, alternative scartate, motivazione, conseguenze — vive
in **[`docs/registro-decisioni.md`](registro-decisioni.md)**, insieme all'elenco delle
questioni aperte e delle verifiche da fare. Qui sotto solo l'indice.

| ID | Data | Decisione | ADR |
|---|---|---|---|
| D-001 | 2026-07-31 | Monorepo unico invece di submodule | ADR-0001 |
| D-002 | 2026-07-31 | Tesi in italiano | — |
| D-003 | 2026-07-31 | Bibliografia `authoryear` invece di IEEE numerico | ADR-0002 |
| D-004 | 2026-07-31 | W&B come sistema di tracciamento | ADR-0002 |
| D-005 | 2026-07-31 | Zotero + Better BibTeX come unica fonte bibliografica | ADR-0002 |
| D-006 | 2026-07-31 | Training su servizi remoti che clonano da GitHub → codice script-first | — |
| D-007 | 2026-07-31 | Configurazioni via Hydra, nessun iperparametro nel codice | ADR-0002 |
| D-008 | 2026-07-31 | Template seguito nella struttura, non nelle pratiche git | — |
| D-009 | 2026-07-31 | Struttura in 8 capitoli + 2 appendici (provvisoria) | — |
| D-010 | 2026-08-02 | Impianto: confronto controllato DCGAN → CAN | ADR-0003 |
| D-011 | 2026-08-02 | Dataset: sottoinsieme di WikiArt — **superata da D-014** | ADR-0004 |
| D-012 | 2026-08-02 | Studio percettivo leggero, campione di convenienza (riaperta) | — |
| D-013 | 2026-08-03 | Servizio di calcolo: RunPod con RTX 4090 | — |
| D-014 | 2026-08-03 | Dataset: ArtBench-10, sei stili di pubblico dominio | ADR-0004 |
| D-015 | 2026-08-03 | Classificatore di stile terzo come giudice dell'ambiguità (indipendente dal discriminatore) | ADR-0005 |
| D-016 | 2026-08-03 | Figure dei campioni generate dal codice, etichettate solo con la predizione del giudice | — |
| D-017 | 2026-08-03 | Stili rivisti su base della matrice di confusione: fuori `romanticism`/`realism`, dentro `art_nouveau`/`expressionism` | modifica D-014 |
| D-018 | 2026-08-03 | Impianto a 128px affiancato (non sostitutivo) a quello a 64px | modifica D-010 |
| D-019 | 2026-08-03 | Criterio di selezione del checkpoint: FID minimo su tutta la traiettoria, non epoca 100 fissa | — |
| D-020 | 2026-08-03 | Criterio di esclusione dei run degenerati: Inception Score < 2,0 | — |
| D-021 | 2026-08-03 | Figure di confronto alla stessa epoca per tutti i run di una condizione | — |
| D-022 | 2026-08-11 | Esperimento illustrativo E5 condizionato per stile, fuori da ADR-0003 | — |
| D-023 | 2026-08-11 | Bozza dell'idea di base e di RQ1: rivendicazione di creatività della CAN come antropomorfizzazione | — |
| D-024 | 2026-08-11 | Accessibilità e training: due tesi che coesistono senza elidersi | completa D-023 |

## Prossime decisioni da prendere

Dettaglio e criticità in [`docs/registro-decisioni.md` §3](registro-decisioni.md#3-questioni-aperte).

Chiuse: **Q1** (sessione confermata), **Q2** (impianto → D-010, ma vedi
punto sotto), **Q4** (dataset → D-014), **Q7** (calcolo → D-013). **Q6** riaperta
(vedi sotto). Restano:

- **Relatore e titolo della tesi** — nominativo e titolo (IT/EN) da depositare nelle
  fasi amministrative descritte in V-006. Gestione di Gian.
- **Q8 — Domande di ricerca**: prima bozza formulata (D-023, RQ1 in §3), completata
  dal collegamento fra accessibilità e problema del training (D-024). Non ancora
  consolidata dalla revisione della letteratura. Resta da: decidere se serve un
  esperimento dedicato per la divergenza autovalutazione/giudice terzo (0,28 vs
  0,75) prima di usarla in tesi; rivedere §5 e §7 alla luce del nuovo ruolo
  dell'impianto sperimentale (caso di studio a supporto della critica, non più
  confronto che stabilisce "chi vince"); strutturare il capitolo di discussione
  tenendo distinti i due argomenti di D-024 invece di fonderli.
- **Q2, punto 3 — cosa conta come successo** la CAN per costruzione tende a
  peggiorare il FID; non è ancora deciso quale esito, prima di vederlo, si considera
  un risultato informativo per la tesi.
- **V-007 — verifica dei termini d'uso del dataset** in parte chiarita (ArtBench
  dichiara «fair use» US, rintracciato fino alla fonte), ma manca ancora la lettura
  della disciplina UE applicabile (direttiva 2019/790). Blocca `data.download`
  finché non passato `--licenza-verificata`.
- **V-008 — l'espressionismo non è integralmente di pubblico dominio** va
  dichiarato esplicitamente in tesi, la formula "tutti gli stili sono di pubblico
  dominio" va corretta.
- **V-009 — natura del degrado del CAN dopo l'epoca 20 a 128px** richiede
  ispezione visiva dei campioni prima di poter scrivere il risultato in tesi.
- **Q3 — Peso relativo tra componente tecnica ed etica**, da concordare col relatore.
- **Q5 — formulazione esatta della penalità di ambiguità**, da verificare sul paper
  di Elgammal: il codice ne implementa due varianti non equivalenti.
- **Q6 — studio percettivo** riaperta il 2026-08-03, proposta (D-012) non
  ancora ratificata.
