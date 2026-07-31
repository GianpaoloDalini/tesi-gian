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

- **Impianto:** `DA DEFINIRE` — vedi ADR-0003.
- **Dataset:** `DA DEFINIRE`
- **Baseline:** `DA DEFINIRE`
- **Metriche:** `DA DEFINIRE` — candidate: FID, Inception Score, studio percettivo.
  Attenzione: FID e IS misurano fedeltà e varietà, **non** creatività. Usarle come
  proxy della creatività senza dichiararne il limite è un errore che la commissione
  può rilevare facilmente.
- **Validazione:** `DA DEFINIRE`

## 6. Architettura

Definita, vedi `README.md` e `CLAUDE.md`.
Monorepo: `thesis/` (LaTeX) + `src/` (codice) + `configs/` + `docs/`.
Tracciamento su Weights & Biases; configurazioni via Hydra; bibliografia via Zotero.

## 7. Piano sperimentale

| ID | Obiettivo | Variabili | Dataset | Baseline | Metriche | Stato |
|---|---|---|---|---|---|---|
| E1 | `DA DEFINIRE` | | | | | non avviato |

## 8. Pianificazione

> **Vincolo aperto.** La sessione di laurea non è ancora confermata. Da questa
> dipende l'intero dimensionamento: un impianto sperimentale con studio percettivo
> su soggetti umani richiede mesi, una replica ridotta su dataset piccolo richiede
> settimane. La scelta va fatta *prima* di definire l'impianto, non dopo.

| Milestone | Descrizione | Scadenza | Stato |
|---|---|---|---|
| M0 | Infrastruttura del repository | 2026-07-31 | ✅ fatto |
| M1 | Revisione della letteratura, gap definito | `DA DEFINIRE` | |
| M2 | Domande di ricerca approvate dal relatore | `DA DEFINIRE` | |
| M3 | Pipeline dati + baseline funzionante | `DA DEFINIRE` | |
| M4 | Esperimenti principali conclusi | `DA DEFINIRE` | |
| M5 | Prima stesura completa | `DA DEFINIRE` | |
| M6 | Consegna | `DA DEFINIRE` | |

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

| Data | Decisione | Motivazione | ADR |
|---|---|---|---|
| 2026-07-31 | Monorepo unico invece di submodule | Tracciabilità diretta risultato→testo, minor attrito operativo per un lavoro individuale | ADR-0001 |
| 2026-07-31 | Bibliografia `authoryear` invece di IEEE numerico | Leggibilità nella discussione critica, coerente con il taglio etico-filosofico | ADR-0002 |
| 2026-07-31 | Tesi in italiano | Scelta dell'autore | — |
| 2026-07-31 | W&B come sistema di tracciamento | Gratuito per uso accademico, adatto a run su servizi remoti | ADR-0002 |

## Prossime decisioni da prendere

1. **Sessione di laurea** — blocca tutto il resto della pianificazione.
2. **Tipo di contributo:** replica della CAN, variante originale, o caso di studio
   a supporto dell'analisi etica. Determina l'intero impianto (ADR-0003).
3. **Dataset**, con verifica della licenza.
4. **Servizio di calcolo** e budget disponibile.
5. **Metriche** e se includere o meno uno studio percettivo con soggetti umani
   (che comporta questioni di consenso informato e forse approvazione etica).
