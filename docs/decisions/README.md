# Architecture Decision Record (ADR)

Un ADR registra **una** decisione significativa: il contesto in cui è stata presa,
le alternative valutate, la scelta e le sue conseguenze.

> **Non tutte le decisioni diventano un ADR.** L'elenco completo e cronologico di ciò
> che è stato deciso sul progetto sta in [`../registro-decisioni.md`](../registro-decisioni.md).
> Qui finiscono solo le decisioni *strutturali*, quelle che meritano una pagina di
> argomentazione perché condizionano il resto del lavoro o perché dovrai difenderle
> in sede di discussione.

## Perché serve in una tesi

Alla discussione la commissione non chiede solo *cosa* hai fatto, ma *perché* lo hai
fatto così. Sei mesi dopo aver scelto una metrica non ricorderai le alternative che
avevi scartato né il motivo. Gli ADR trasformano una scelta implicita in un'argomentazione
difendibile, e alimentano direttamente il capitolo di metodologia.

## Uso

1. Copia `_template.md` in `NNNN-titolo-breve.md` (numerazione progressiva).
2. Compilalo. Un ADR è breve: una pagina basta.
3. Gli ADR **non si cancellano**. Una decisione superata si marca `Superata da ADR-NNNN`.

## Indice

| ID | Titolo | Stato |
|---|---|---|
| 0001 | Monorepo unico per tesi e codice | Accettata |
| 0002 | Toolchain: LaTeX, bibliografia, tracciamento esperimenti | Accettata |
| 0003 | Impianto sperimentale: confronto controllato DCGAN → CAN | Accettata |
| 0004 | Dataset: ArtBench-10, sei stili di pubblico dominio | Accettata |
