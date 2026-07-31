# ADR-0003 — Impianto sperimentale

- **Data:** —
- **Stato:** **Aperta** — decisione bloccante
- **Decisore:** Gian, con il relatore

## Contesto

L'impianto sperimentale non è ancora deciso. È la decisione che determina dataset,
architettura, metriche, fabbisogno di calcolo e durata del lavoro: finché resta
aperta, il piano di progetto non è dimensionabile.

Vincolo a monte non ancora risolto: **la sessione di laurea**. Un impianto con
studio percettivo su soggetti umani e più run comparativi richiede mesi; una replica
ridotta su dataset piccolo richiede settimane.

## Alternative da valutare

| Opzione | Vantaggi | Svantaggi |
|---|---|---|
| A — Replica della CAN di Elgammal et al. (2017) su WikiArt | Riferimento solido, risultato atteso noto, confronto con baseline immediato | Contributo originale scarso se ci si ferma alla replica; costo di calcolo non banale |
| B — Baseline DCGAN + variante originale su dominio ristretto | Contributo proprio, calcolo più contenuto | Rischio di risultato negativo o non significativo |
| C — Esperimento come caso di studio a supporto dell'analisi etica | Coerente con l'area del relatore, calcolo minimo, taglio originale | Rischio che la commissione lo giudichi tecnicamente leggero per una LM-32 |

Nota: una replica ben eseguita **con** un'analisi critica originale dei suoi limiti
(opzione A estesa) è spesso più difendibile di una variante originale mal validata.
Da discutere con il relatore.

## Domande aperte

1. Qual è il peso relativo atteso tra componente tecnica e componente etica?
2. Il relatore preferisce contributo tecnico o analisi critica?
3. Quale budget di calcolo è realisticamente disponibile?
4. È previsto uno studio con soggetti umani? Se sì, servono consenso informato e
   probabilmente un vaglio etico: va messo in conto nella pianificazione.

## Decisione

*Da prendere.*
