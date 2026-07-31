# ADR-0002 — Toolchain: LaTeX, bibliografia, tracciamento esperimenti

- **Data:** 2026-07-31
- **Stato:** Accettata
- **Decisore:** Gian

## Contesto

Vanno fissati gli strumenti di base prima di iniziare a scrivere e sperimentare.
Cambiarli a metà lavoro costa molto più che sceglierli bene all'inizio.

## Decisioni

**LaTeX con `latexmk` + `biblatex`/`biber`, stile `authoryear`.**
`authoryear` produce `(Elgammal et al., 2017)`: in una tesi che discute criticamente
i lavori altrui e intreccia argomentazione tecnica ed etica, il lettore riconosce
l'autore senza saltare in bibliografia. Lo stile numerico IEEE è più compatto ma
rende la discussione meno scorrevole. Lo stile è isolato in una sola riga di
`preamble/packages.tex`: il cambio resta reversibile a costo nullo.

**Zotero + Better BibTeX come unica fonte della bibliografia.**
Il file `bibliography.bib` diventa un artefatto generato. Evita il disallineamento
tra ciò che si è letto e ciò che si cita, ed elimina gli errori di trascrizione dei
metadati — che nelle tesi sono una fonte ricorrente di rilievi.

**Weights & Biases per il tracciamento.**
Gratuito per uso accademico, funziona bene con i servizi di training remoto che
clonano il codice da GitHub (nessuno stato da mantenere in locale), e conserva
automaticamente iperparametri, curve e campioni generati. L'alternativa
TensorBoard + CSV è più povera nel confronto tra run; MLflow richiede infrastruttura.

**Hydra per le configurazioni.**
Nessun iperparametro nel codice: un esperimento è definito da un file di
configurazione versionato, quindi citabile e riproducibile.

## Conseguenze

- Serve un account W&B e la variabile d'ambiente `WANDB_API_KEY` sui servizi remoti.
- `bibliography.bib` non va più editato a mano.
- Il codice sperimentale va scritto config-driven fin dall'inizio.

## Impatto sulla tesi

Capitolo di implementazione (`sec:infrastruttura`) e appendice sulla riproducibilità.
