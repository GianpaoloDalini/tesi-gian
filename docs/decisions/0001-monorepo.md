# ADR-0001 — Monorepo unico per tesi e codice

- **Data:** 2026-07-31
- **Stato:** Accettata
- **Decisore:** Gian

## Contesto

La tesi produce due artefatti che devono restare allineati: il testo LaTeX e il
codice sperimentale che genera i numeri e le figure citate nel testo. La domanda è
se tenerli nello stesso repository o separarli.

## Alternative valutate

| Opzione | Vantaggi | Svantaggi |
|---|---|---|
| Monorepo unico | Un commit lega testo, codice e figura; clone singolo; storia unica | Repo più grande; separare il codice per una pubblicazione richiede un'estrazione |
| Due repository separati | Codice pubblicabile indipendentemente | Si perde il legame diretto risultato→testo; doppia sincronizzazione manuale |
| Repo tesi + git submodule | Codice autonomo mantenendo un puntatore | Doppio commit a ogni modifica; se si dimentica di aggiornare il puntatore la tracciabilità salta, cioè fallisce proprio l'obiettivo; `--recurse-submodules` obbligatorio per chi replica |

## Decisione

**Monorepo unico.** L'opzione submodule era stata considerata e scartata: introduce
un passaggio manuale (aggiornare il puntatore) il cui fallimento silenzioso produce
esattamente la perdita di tracciabilità che si voleva evitare. Il submodule ha senso
quando il codice ha un ciclo di rilascio autonomo o è condiviso tra più progetti:
non è il caso di una tesi individuale.

## Conseguenze

- Ogni commit può essere citato come riferimento riproducibile di un risultato.
- Se dopo la discussione servirà un repository pubblico del solo codice, si estrarrà
  con `git subtree split`, preservando la storia.

## Impatto sulla tesi

Appendice sulla riproducibilità (`app:riproducibilita`).
