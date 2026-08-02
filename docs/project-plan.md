# Piano di progetto — Tesi magistrale

> **Documento vivo.** È la fonte di verità del progetto. Ogni decisione presa va
> registrata qui nello stesso commit in cui viene applicata. Le voci marcate
> `DA DEFINIRE` sono i vuoti aperti: nessuno va riempito con un'ipotesi
> plausibile, si riempiono solo con decisioni effettivamente prese.

**Ultimo aggiornamento:** 2026-07-31 · **Stato:** impostazione dell'infrastruttura

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
| Sessione di laurea | `DA DEFINIRE` — vedi §8, il vincolo temporale è aperto |
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
- **Dataset:** sottoinsieme bilanciato di WikiArt, 5-10 stili, 64×64.
  Vedi ADR-0004 e D-011. **Subordinato a V-007** (verifica della licenza).
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

| ID | Obiettivo | Variabile indipendente | Dataset | Metriche | Stato |
|---|---|---|---|---|---|
| E0 | Smoke test della pipeline su dati sintetici, CPU | — | sintetico | nessuna | ✅ pipeline implementata |
| E1 | Condizione di **controllo**: DCGAN | loss avversaria pura | WikiArt ridotto | FID, IS | non avviato |
| E2 | Condizione **sperimentale**: CAN | + classificazione stile (D) e ambiguità (G) | WikiArt ridotto | FID, IS, entropia di stile | non avviato |
| E3 | Ablazione: CAN con `style_ambiguity_weight=0` | peso dell'ambiguità | WikiArt ridotto | FID, IS | opzionale, se avanza tempo |
| E4 | Studio percettivo leggero sui campioni di E1 ed E2 | condizione mostrata | — | giudizio umano | non avviato |

Tutto ciò che non è la variabile indicata resta **identico** fra E1 ed E2: generatore,
backbone del discriminatore, iperparametri, seed, epoche, numero di campioni per la
valutazione. È l'unica cosa che rende il confronto interpretabile.

E3 non è un esperimento ma un controllo di sanità: con peso nullo la CAN deve
riprodurre la DCGAN. Se non accade, l'implementazione condivisa introduce differenze
spurie e E1/E2 non sono confrontabili.

## 8. Pianificazione

> **Vincolo chiuso e stretto.** Sessione autunnale: caricamento dell'elaborato entro
> il **21 settembre 2026**, discussione il **2 ottobre 2026**. L'avviso della Scuola
> di Ingegneria specifica che non sono ammesse deroghe. Vedi V-006 nel registro delle
> decisioni per il calendario completo degli adempimenti.
>
> **Il rischio principale non è tecnico ma amministrativo:** la Fase 1 della domanda
> di laurea scade il **14 agosto** e richiede il nominativo del relatore, tuttora
> `DA DEFINIRE`, che deve poi approvare online entro il 17 agosto.

| Milestone | Descrizione | Scadenza | Stato |
|---|---|---|---|
| M0 | Infrastruttura del repository | 2026-07-31 | ✅ fatto |
| M-A1 | **Fase 1: deposito titolo e relatore** | **2026-08-14** | 🔴 da fare |
| M-A2 | **Fase 3: domanda definitiva + AlmaLaurea** | **2026-08-18** | 🔴 da fare |
| M3a | Pipeline sperimentale implementata e testata | 2026-08-02 | ✅ fatto |
| M3b | Dataset preparato (dopo V-007) e smoke test superato | 2026-08-09 | ⬜ |
| M4 | Run E1 ed E2 conclusi e registrati | 2026-08-23 | ⬜ |
| M4b | Metriche calcolate, figure esportate | 2026-08-30 | ⬜ |
| M1 | Revisione della letteratura, gap definito | 2026-09-06 | ⬜ in parallelo |
| M2 | Domande di ricerca approvate dal relatore | 2026-09-06 | ⬜ |
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
| D-011 | 2026-08-02 | Dataset: sottoinsieme bilanciato di WikiArt (con riserva) | ADR-0004 |
| D-012 | 2026-08-02 | Studio percettivo leggero, campione di convenienza | — |

## Prossime decisioni da prendere

Dettaglio e criticità in [`docs/registro-decisioni.md` §3](registro-decisioni.md#3-questioni-aperte).

Chiuse dal 2026-08-02: **Q1** (sessione: discussione 02/10/2026), **Q2** (impianto →
D-010), **Q4** (dataset → D-011), **Q6** (studio percettivo → D-012), **Q7**
(calcolo). Restano:

1. **Relatore** 🔴 nominativo necessario per la Fase 1 entro il **14 agosto**. Non è
   una questione metodologica ma è il singolo punto di fallimento del progetto.
2. **Titolo della tesi** 🔴 richiesto in italiano e inglese entro il 14 agosto.
3. **V-007 — verifica della licenza del dataset** 🔴 blocca il download.
4. **Q8 — Domande di ricerca** 🔴 servono almeno in bozza per scegliere il titolo.
5. **Q3 — Peso relativo tra componente tecnica ed etica**, da concordare col relatore.
6. **Q5 — formulazione esatta della penalità di ambiguità**, da verificare sul paper
   di Elgammal: il codice ne implementa due varianti non equivalenti.
