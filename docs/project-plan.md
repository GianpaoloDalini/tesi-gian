# Piano di progetto — Tesi magistrale

> **Documento vivo.** È la fonte di verità del progetto. Ogni decisione presa va
> registrata qui nello stesso commit in cui viene applicata. Le voci marcate
> `DA DEFINIRE` sono i vuoti aperti: nessuno va riempito con un'ipotesi
> plausibile, si riempiono solo con decisioni effettivamente prese.

**Ultimo aggiornamento:** 2026-08-11 · **Stato:** impianto sperimentale eseguito a
64px e 128px (14 run), in attesa del relatore e delle domande di ricerca

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
| Sessione di laurea | Autunnale — discussione **2026-10-02**, elaborato entro **2026-09-21** (V-006) |
| Lingua | Italiano |

---

## 1. Contesto

- **Area di ricerca:** intelligenza artificiale generativa applicata alla produzione
  artistica; intersezione tra machine learning, creatività computazionale ed etica.
- **Motivazione:** `DA DEFINIRE` — perché *ora*, perché *questo* taglio.
- **Contesto applicativo:** `DA DEFINIRE`.
- **Stakeholder:** artisti, ricercatori in creatività computazionale, chi si occupa
  di policy sul diritto d'autore, comunità ML. `DA RESTRINGERE`.

## 2. Definizione del problema

- **Problema reale:** `DA DEFINIRE`
- **Limiti delle soluzioni esistenti:** `DA DEFINIRE` (esito della revisione, §4)
- **Opportunità di ricerca:** `DA DEFINIRE`

> Nota metodologica: questa sezione non si può compilare prima di aver fatto la
> revisione della letteratura. Un problema definito prima di conoscere lo stato
> dell'arte è quasi sempre già risolto, oppure mal posto.

## 3. Obiettivi

- **Obiettivo generale:** `DA DEFINIRE`
- **Obiettivi specifici:** `DA DEFINIRE`
- **Deliverable concreti:**
  1. Elaborato di tesi (PDF).
  2. Repository riproducibile con codice e configurazioni.
  3. Risultati sperimentali tracciati su W&B.
  4. `DA DEFINIRE` — eventuale dataset o artefatto rilasciato.

### Domande di ricerca

| ID | Domanda | Come viene risposta | Stato |
|---|---|---|---|
| RQ1 | `DA DEFINIRE` | | aperta |

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

| ID | Obiettivo | Variabile indipendente | Run | Metriche | Stato |
|---|---|---|---|---|---|
| E0 | Smoke test della pipeline su dati sintetici, CPU | — | 1 | nessuna | ✅ fatto |
| E1 | Condizione di **controllo**: DCGAN, 64px | loss avversaria pura | 4 (seed 1-4) | FID, IS, ambiguità (giudice terzo), copertura | ✅ **concluso 2026-08-03** |
| E2 | Condizione **sperimentale**: CAN, 64px | + classificazione stile (D) e ambiguità (G) | 4 (seed 1-4) | idem | ✅ **concluso 2026-08-03** — 1 run collassato (`can-seed1`), escluso dalle medie |
| E1b/E2b | Stesso confronto a **128px** | idem | 3+3 (seed 1-3) | idem | ✅ **concluso 2026-08-04** — vedi esito sotto |
| E3 | Ablazione: CAN con `style_ambiguity_weight=0` | peso dell'ambiguità | 1 | FID, IS | non avviato |
| E4 | Studio percettivo leggero sui campioni generati | condizione mostrata | — | giudizio umano | non avviato |

Dataset per E1-E3: ArtBench-10, sei stili (D-017: `ukiyo_e`, `renaissance`,
`baroque`, `art_nouveau`, `expressionism`, `impressionism`), 30.000 immagini.

**Esito E1/E2 a 64px** (`experiments/registry.md`): l'ambiguità di stile sale come
atteso (0,682 → 0,750, gruppi non sovrapposti), ma **il FID non peggiora** (107,7 vs
107,3, indistinguibili) — l'ipotesi che la CAN costasse fedeltà è **falsificata** a
questa risoluzione. Un run CAN (`can-seed1`) è mode-collapsed (copertura 0,190),
escluso dalle medie con motivazione esplicita.

**Esito E1b/E2b a 128px:** qui l'ipotesi **non è più falsificata** — FID 183,4 (CAN)
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

E3 non è un esperimento ma un controllo di sanità, ancora da eseguire: con peso nullo
la CAN deve riprodurre la DCGAN.

**Nodo ancora aperto (Q2, punto 3):** per costruzione la CAN tende a peggiorare il
FID. Non è ancora stato deciso, prima di scrivere le conclusioni, quale esito si
considera "informativo" — va chiuso prima della stesura del capitolo dei risultati.

## 8. Pianificazione

> Le scadenze amministrative della sessione (Fase 1-4, calendario completo) sono in
> V-006 nel registro delle decisioni. Gian le gestisce autonomamente; questo piano
> non le ripete né le segnala come rischio.

| Milestone | Descrizione | Scadenza | Stato |
|---|---|---|---|
| M0 | Infrastruttura del repository | 2026-07-31 | ✅ fatto |
| M-A1 | Fase 1: deposito titolo e relatore | vedi V-006 | ⬜ |
| M-A2 | Fase 3: domanda definitiva + AlmaLaurea | vedi V-006 | ⬜ |
| M3a | Pipeline sperimentale implementata e testata | 2026-08-02 | ✅ fatto |
| M3b | Dataset preparato e smoke test superato | 2026-08-03 | ✅ fatto |
| M4 | Run E1 ed E2 conclusi e registrati (64px) | 2026-08-03 | ✅ fatto |
| M4b | Metriche calcolate, figure esportate (64px) | 2026-08-03 | ✅ fatto |
| M4c | Impianto replicato a 128px, traiettoria valutata | 2026-08-04 | ✅ fatto — V-009 aperta (ispezione visiva mancante) |
| M1 | Revisione della letteratura, gap definito | 2026-09-06 | ⬜ in parallelo |
| M2 | Domande di ricerca approvate dal relatore | 2026-09-06 | ⬜ vedi Q8 |
| M-E4 | Studio percettivo concluso | 2026-09-06 | ⬜ |
| M5 | Prima stesura completa | 2026-09-14 | ⬜ |
| M6 | **Caricamento dell'elaborato (Fase 4)** | **2026-09-21** | ⬜ |
| M7 | Discussione | 2026-10-02 | — |

**Margine reale:** nullo. Ogni slittamento di M4 si scarica interamente sulla stesura.
Per questo E1 ed E2 hanno un budget di epoche fisso e un checkpoint ripristinabile: se
la qualità a 100 epoche non è quella sperata, si scrive la tesi su quello che c'è e si
discute il limite, invece di rilanciare il training a due settimane dalla consegna.

## 9. Rischi

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| Sessione di laurea troppo ravvicinata per un impianto sperimentale serio | alta | alto | Decidere presto la sessione; predisporre uno scope minimo difendibile |
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

## Prossime decisioni da prendere

Dettaglio e criticità in [`docs/registro-decisioni.md` §3](registro-decisioni.md#3-questioni-aperte).

Chiuse: **Q1** (sessione: discussione 02/10/2026), **Q2** (impianto → D-010, ma vedi
punto sotto), **Q4** (dataset → D-014), **Q7** (calcolo → D-013). **Q6** riaperta
(vedi sotto). Restano:

- **Relatore e titolo della tesi** — nominativo e titolo (IT/EN) da depositare nelle
  fasi amministrative descritte in V-006. Gestione di Gian.
- **Q8 — Domande di ricerca** ancora non formulate; servono per il titolo e a monte
  della revisione della letteratura.
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
