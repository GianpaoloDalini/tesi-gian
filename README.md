# Tesi di Laurea Magistrale — IA generativa e creatività artistica

Analisi di Generative Adversarial Networks (GAN) e Creative Adversarial Networks (CAN)
nel contesto della produzione artistica.

Corso di Laurea Magistrale in Ingegneria Informatica (LM-32) — Università degli Studi di Bergamo.

---

## Struttura

Monorepo: la tesi e il codice sperimentale che ne produce i risultati vivono nello
stesso repository, così che ogni figura e ogni numero dell'elaborato siano
riconducibili al commit che li ha generati.

```
thesis/     elaborato LaTeX
src/        codice sperimentale (package Python installabile)
configs/    configurazioni degli esperimenti (Hydra)
docs/       piano di progetto, decisioni (ADR), schede dei paper, verbali
scripts/    bootstrap per i servizi di training remoto
tests/      test del codice
data/       dataset (non versionato)
experiments/ output dei run (non versionato, tranne il registro)
```

Il documento di riferimento sullo stato del progetto è
[`docs/project-plan.md`](docs/project-plan.md).
Le convenzioni operative sono in [`CLAUDE.md`](CLAUDE.md) — leggerlo prima di
mettere mano al repository.

## Requisiti

- **LaTeX:** distribuzione completa (TeX Live full o MacTeX) con `biber`.
  Servono `biblatex`, `cleveref`, `glossaries`, `todonotes`, `babel-italian`.
  In alternativa Overleaf, che li include tutti.
- **Python:** ≥ 3.10
- **Account** Weights & Biases (gratuito per uso accademico)
- **Zotero** con il plugin Better BibTeX

## Compilare la tesi

```bash
make thesis        # produce thesis/build/main.pdf
make watch         # ricompila a ogni salvataggio
make clean         # rimuove gli artefatti di build
```

Gli artefatti di compilazione finiscono in `thesis/build/` e non entrano in git.

## Eseguire gli esperimenti

```bash
make install                                   # pip install -e ".[dev]"
export WANDB_API_KEY=...                       # mai committare la chiave
python -m tesi_gan.cli train experiment=<nome>
```

Su un servizio di training remoto che clona il repository da GitHub:

```bash
git clone https://github.com/<utente>/<repo>.git
bash <repo>/scripts/bootstrap_remote.sh
```

## Bibliografia

`thesis/references/bibliography.bib` è **generato** da Zotero tramite Better BibTeX:
non va modificato a mano. Le correzioni si fanno in Zotero e si riesportano.

Il file attualmente presente è un *seed* con i lavori fondativi del dominio, da
importare in Zotero al primo utilizzo.

## Riproducibilità

- Nessun iperparametro nel codice: tutto in `configs/`.
- Seed fissato e registrato per ogni run.
- Un training non parte con modifiche non committate: il commit registrato deve
  corrispondere al codice eseguito.
- Ogni risultato citato nella tesi è tracciato in
  [`experiments/registry.md`](experiments/registry.md).
