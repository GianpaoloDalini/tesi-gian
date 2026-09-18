# Capitoli sospesi (non cancellati)

Questi file erano `thesis/capitoli/04-metodologia.tex`, `05-implementazione.tex`,
`06-risultati.tex` e `thesis/appendici/A-iperparametri.tex`, `B-riproducibilita.tex`.

Con il passaggio a una tesi espositiva (**ADR-0007**, 2026-09-14, supera **ADR-0003**),
il confronto sperimentale DCGAN/CAN non fa più parte del documento consegnato: questi
capitoli sono stati **spostati qui con `mv`, non cancellati**, e tolti da
`thesis/main.tex`.

Il codice, le configurazioni e i risultati tracciati (`src/`, `configs/`,
`experiments/registry.md`) restano intatti e non sono toccati da questa decisione:
il lavoro DCGAN/CAN (E1-E6) e il restyling E8 continuano come binario personale di
Gian, in parallelo alla stesura della tesi (vedi D-028 in `docs/registro-decisioni.md`).

Se il lavoro su E8 produce un risultato che convince il relatore a riaprire una
componente sperimentale, questi file tornano il punto di partenza per riscrivere i
capitoli corrispondenti — non si ripartirebbe da zero. Se questo accade, ADR-0007 va
marcata `superata`, non riscritta (stessa regola già applicata ad ADR-0003).
