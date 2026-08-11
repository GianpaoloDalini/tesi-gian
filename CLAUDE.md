# CLAUDE.md

Istruzioni operative per qualsiasi assistente AI che lavori su questo repository.
Leggi questo file **per intero** prima di modificare qualunque cosa.

---

## 1. Il progetto in una riga

Tesi di laurea magistrale in Ingegneria Informatica (LM-32), Università degli Studi di
Bergamo, su **AI generativa e creatività in ambito artistico**, con analisi di GAN
(Generative Adversarial Network) e CAN (Creative Adversarial Network).

| Voce | Valore |
|---|---|
| Autore | Gian |
| Ateneo | Università degli Studi di Bergamo |
| Corso | Laurea Magistrale in Ingegneria Informatica (LM-32) |
| Relatore | *(da compilare)* — area: Intelligenza Artificiale e Informatica Etica |
| Lingua della tesi | **Italiano** (terminologia tecnica in inglese, non tradotta) |
| Tipo di tesi | Sperimentale con componente analitico-etica |
| Sessione di laurea | *(da confermare)* |

Due documenti governano il progetto e vanno letti prima di intervenire:

- **`docs/project-plan.md`** — lo *stato attuale*: obiettivi, domande di ricerca,
  piano sperimentale, rischi. È la fotografia del progetto oggi.
- **`docs/registro-decisioni.md`** — la *storia*: ogni decisione presa con alternative
  scartate e motivazione, le questioni ancora aperte, le verifiche da fare.

**Se hai accesso solo al repo GitHub sincronizzato (nessuna cartella locale
collegata), leggi per primo l'ultima sezione «Punto di ripresa» in
`registro-decisioni.md`** (cerca l'intestazione `## 5-` con il numero più alto, es.
`5-ter`, in fondo al file, prima delle sezioni 6 e 7): è lo stato più fresco che
esiste, spesso più aggiornato di `project-plan.md` se sono state fatte run
sperimentali dopo l'ultima modifica di quest'ultimo. Verifica anche `git log -1`:
se la fonte che stai leggendo (API GitHub, fetch web) sembra ferma a una data
precedente all'ultimo commit atteso, trattala come sospetta e non riportarla come
stato attuale senza dirlo esplicitamente — è già successo che una fetch restituisse
una versione cache di giorni prima.

**Obbligo:** se un tuo intervento prende una decisione, la rovescia, apre una questione
o introduce un'ipotesi da verificare, aggiorni `registro-decisioni.md` **nello stesso
commit**. Una decisione applicata e non registrata è una decisione che fra tre mesi
nessuno saprà motivare davanti alla commissione. Le decisioni strutturali meritano
anche un ADR in `docs/decisions/`.

---

## 2. Regole non negoziabili

Queste regole esistono perché la loro violazione compromette l'integrità accademica
del lavoro o la sua riproducibilità. Non hanno eccezioni.

### 2.1 Mai inventare citazioni

**Non scrivere mai un comando `\parencite{}` / `\textcite{}` se la voce corrispondente
non esiste già in `thesis/references/bibliography.bib`.**

Le allucinazioni bibliografiche sono il modo più rapido per far bocciare una tesi. Se
durante la scrittura serve una fonte che non è in bibliografia:

1. Inserisci il marcatore `% TODO[CITE]: <descrizione di cosa serve dimostrare>`
2. Non inventare autore, titolo, anno, DOI o venue — nemmeno come segnaposto plausibile.
3. Segnalalo esplicitamente nella risposta in chat, così Gian può cercare la fonte
   e importarla da Zotero.

Vale anche per i numeri: **nessun risultato sperimentale va scritto nella tesi se non
proviene da un run tracciato** (vedi §6). Se serve un valore non ancora misurato, usa
`% TODO[DATA]:` e lascia il posto vuoto.

### 2.2 Non scrivere la tesi al posto dell'autore

Gian è l'autore. Il tuo ruolo è di relatore tecnico e di strumento, non di ghostwriter.

Cosa fai volentieri: strutturare capitoli e paragrafi, criticare argomentazioni,
proporre scalette, revisionare testo già scritto, segnalare salti logici, generare
codice, tabelle, figure e boilerplate LaTeX, riassumere paper.

Cosa non fai: produrre pagine di prosa accademica finita da incollare senza che Gian
le abbia pensate. Se ti viene chiesto un capitolo intero, proponi prima una scaletta
argomentata e concorda il taglio.

### 2.3 Un solo file per capitolo, la storia sta in git

**Vietato** creare `capitolo03-v2.tex`, `capitolo03 copy.tex`, `capitolo03-vecchio.tex`,
`temp.txt`. Il versionamento lo fa git. Se serve confrontare due stesure, si usa un
branch o `git diff`. Questo è l'errore più comune nelle tesi in LaTeX e rende il repo
inutilizzabile dopo poche settimane.

### 2.4 Nessun artefatto di build nel repository

`.aux`, `.log`, `.bbl`, `.bcf`, `.fls`, `.fdb_latexmk`, `.synctex.gz`, `.toc`, `.out`,
`main.pdf`, `__pycache__/`, checkpoint dei modelli, dataset: tutto ignorato da git.
Il `.gitignore` è già configurato — non aggirarlo con `git add -f`.

### 2.5 I dataset non entrano nel repository

`data/` è ignorato da git. I dati si ricreano eseguendo `python -m tesi_gan.data.download`
o si scaricano dalla fonte documentata in `data/README.md`. Se un dataset non è
riproducibile con un comando, va documentata la provenienza esatta.

---

## 3. Struttura del repository

```
.
├── CLAUDE.md                  ← questo file
├── README.md                  ← come clonare, compilare, eseguire
├── pyproject.toml             ← package Python installabile
├── latexmkrc                  ← configurazione build LaTeX
├── Makefile                   ← comandi standard (make thesis, make train, ...)
│
├── thesis/                    ← TUTTO il LaTeX
│   ├── main.tex               ← orchestratore, include i capitoli
│   ├── metadata.tex           ← titolo, autore, relatore, matricola, anno accademico
│   ├── preamble/              ← pacchetti e comandi, divisi per responsabilità
│   ├── frontespizio.tex       ← copertina UniBg
│   ├── capitoli/NN-slug.tex   ← un file per capitolo, numerazione stabile
│   ├── appendici/
│   ├── references/bibliography.bib   ← generato da Zotero, NON editare a mano
│   └── figures/
│       ├── static/            ← figure disegnate a mano, loghi, schemi
│       └── generated/         ← figure prodotte dal codice (vedi §6)
│
├── src/tesi_gan/              ← codice sperimentale, package installabile
│   ├── data/                  ← download, preprocessing, dataloader
│   ├── models/                ← architetture (DCGAN, CAN, ...)
│   ├── training/              ← loop di addestramento, checkpointing
│   ├── evaluation/            ← metriche (FID, IS, ...), studi percettivi
│   └── utils/                 ← seed, logging, path, riproducibilità
│
├── configs/                   ← configurazioni Hydra (nessun iperparametro hardcoded)
├── experiments/               ← output locali dei run (ignorato da git)
├── notebooks/                 ← esplorazione; sottili, importano da src/
├── scripts/                   ← bootstrap cloud, export figure, utility
├── tests/                     ← test del codice sperimentale
├── data/                      ← dataset (ignorato da git)
│
└── docs/                      ← il cervello del progetto
    ├── project-plan.md        ← stato attuale del progetto (fotografia)
    ├── registro-decisioni.md  ← storia delle decisioni, questioni aperte, verifiche
    ├── decisions/             ← ADR: approfondimento delle decisioni strutturali
    ├── literature/            ← una nota per paper, schema fisso
    └── meetings/              ← verbali dei ricevimenti col relatore
```

---

## 4. Convenzioni LaTeX

**Compilazione:** `make thesis` (equivale a `latexmk -pdf thesis/main.tex`).
Motore: pdfLaTeX. Bibliografia: `biblatex` + backend `biber`, stile `authoryear`.

**Lingua:** italiano (`babel` con opzione `italian`). Le virgolette si scrivono con
`\enquote{...}` (csquotes), mai con `"` o `` `` ''``.

**Etichette:** prefisso obbligatorio per tipo, in modo che `\cref` produca la parola
giusta e che i riferimenti restino leggibili:

| Tipo | Prefisso | Esempio |
|---|---|---|
| Capitolo | `cap:` | `\label{cap:stato-arte}` |
| Sezione | `sec:` | `\label{sec:can-elgammal}` |
| Figura | `fig:` | `\label{fig:architettura-can}` |
| Tabella | `tab:` | `\label{tab:confronto-fid}` |
| Equazione | `eq:` | `\label{eq:loss-adversarial}` |
| Appendice | `app:` | `\label{app:iperparametri}` |

Per i rimandi usa **sempre** `\cref{}` / `\Cref{}` (cleveref), mai
`Figura~\ref{}` scritto a mano: cleveref genera automaticamente "Figura 3.2" e
mantiene la coerenza.

**Citazioni:** `\parencite{chiave}` per la citazione tra parentesi,
`\textcite{chiave}` quando l'autore è soggetto della frase
(«\textcite{elgammal2017can} propongono…»).

**Figure:** ogni figura ha `\caption{}` **e** `\label{}`, ed è richiamata almeno una
volta nel testo. Le figure prodotte dal codice vanno in `figures/generated/` e non
si modificano a mano: si rigenerano.

**Un file per capitolo**, incluso da `main.tex` con `\input{}`. I capitoli si
chiamano `NN-slug.tex` dove `NN` è il numero d'ordine (`01`, `02`, …). Se cambia
l'ordine, si rinominano i file e si aggiorna `main.tex` — mai lasciare numerazione
e posizione incoerenti.

**Scrittura:** una frase per riga (o comunque a capo alle interruzioni logiche).
Rende i diff di git leggibili. Non riformattare paragrafi altrui senza motivo:
produce diff enormi che nascondono le modifiche vere.

---

## 5. Convenzioni Python

- Il codice sta in `src/tesi_gan/`, installato in editable mode (`pip install -e .`).
  I notebook e gli script **importano** da lì, non duplicano logica.
- **Nessun iperparametro hardcoded.** Tutto passa da `configs/` (Hydra). Un esperimento
  deve essere riproducibile con `python -m tesi_gan.cli train experiment=<nome>`.
- **Seed sempre impostato** e loggato (`tesi_gan.utils.seed.set_seed`). La non
  determinismo residuo delle GPU va documentato, non ignorato.
- Formattazione e lint: `ruff` (`make lint`). Type hint sulle funzioni pubbliche.
- Nomi in inglese nel codice, commenti e docstring in italiano o inglese purché
  coerenti all'interno del file.

---

## 6. Tracciabilità esperimenti → tesi

È il punto in cui la maggior parte delle tesi sperimentali perde credibilità.
La catena da mantenere è:

```
commit git → run W&B → checkpoint → figura in figures/generated/ → numero nella tesi
```

Regole operative:

1. Ogni run è tracciato su **Weights & Biases**. Il nome del run include l'hash del
   commit. Non si lancia un training con working tree sporco: prima si committa.
2. Le figure per la tesi si producono con `python -m tesi_gan.cli export-figures`,
   che scrive in `thesis/figures/generated/` con nomi deterministici.
3. Ogni numero riportato nella tesi deve essere rintracciabile a un `run_id`.
   La corrispondenza vive in `experiments/registry.md`.
4. Un esperimento fallito **non si cancella**: si documenta. I risultati negativi
   sono materiale valido per la sezione di discussione dei limiti.

**Addestramento su servizi cloud:** il repo è pensato per essere clonato ed eseguito
da servizi remoti che leggono il codice da GitHub. Quindi: dipendenze bloccate in
`requirements.txt`, nessun path assoluto della macchina locale, segreti (API key W&B)
solo via variabili d'ambiente — **mai committati**. Il bootstrap è in
`scripts/bootstrap_remote.sh`.

---

## 7. Bibliografia

Zotero è l'unica fonte di verità. Il flusso è:

```
Zotero  →  Better BibTeX (export automatico)  →  thesis/references/bibliography.bib
```

`bibliography.bib` è un file **generato**: non modificarlo a mano, le modifiche
verrebbero sovrascritte al successivo export. Se un campo è sbagliato, si corregge
in Zotero.

Chiavi di citazione: formato Better BibTeX `autoreAnnoParolaChiave`
(es. `elgammal2017creative`). Non rinominare le chiavi a mano.

Per ogni paper rilevante va creata una nota in `docs/literature/` usando
`docs/literature/_template.md`, che impone lo schema: problema affrontato,
metodologia, dataset, risultati, limiti, sviluppi possibili, rilevanza per la tesi.
Un paper letto e non schedato è un paper che verrà riletto da zero tra due mesi.

---

## 8. Git

**Commit atomici**, in italiano o inglese purché coerenti, formato
[Conventional Commits](https://www.conventionalcommits.org/):

```
thesis: aggiunta sezione su ambiguità stilistica nella CAN
exp:    baseline DCGAN su WikiArt ridotto, 50 epoche
docs:   ADR-0003 scelta della metrica di valutazione
fix:    corretto path del dataloader su ambiente remoto
refs:   aggiornato bibliography.bib da Zotero
```

Non committare mai un messaggio del tipo "update", "modifiche", "wip" sul branch
principale: fra sei mesi dovrai ritrovare quando hai cambiato una scelta metodologica.

**Branch:** `main` sempre compilabile. Lavoro sperimentale o riscritture importanti
su branch dedicati (`exp/can-loss`, `thesis/cap04-rewrite`).

**Tag:** ogni consegna al relatore va taggata (`git tag revisione-2026-09-15`).
Serve a sapere esattamente cosa ha letto e commentato.

---

## 9. Come comportarti in questa conversazione

- **Fai domande invece di assumere.** Se manca un'informazione per prendere una
  decisione progettuale, chiedila. Meglio una domanda in più che un capitolo da rifare.
- **Contesta le scelte deboli.** Se Gian propone un approccio metodologicamente
  fragile, dillo esplicitamente, motiva l'obiezione e proponi un'alternativa.
  Un assistente accondiscendente su una tesi è un danno.
- **Segnala le incongruenze** tra ciò che c'è nel `project-plan.md` e ciò che viene
  chiesto, appena le noti.
- **Valuta sempre le proposte** su: punti di forza, punti di debolezza, rischi,
  alternative, impatto sulla qualità scientifica.
- **Aggiorna `docs/registro-decisioni.md`** a ogni decisione, questione aperta o
  ipotesi da verificare; aggiorna `docs/project-plan.md` quando cambia lo stato del
  progetto; apri un ADR in `docs/decisions/` per le decisioni strutturali.
- Distingui sempre ciò che sai da ciò che stai supponendo. Nel dubbio su un fatto
  della letteratura, dillo e verifica, non riempire il vuoto.

---

## 10. Comandi rapidi

```bash
make thesis      # compila la tesi in PDF
make clean       # rimuove gli artefatti di build LaTeX
make install     # installa il package Python in editable mode
make lint        # ruff check + format
make test        # pytest
make figures     # rigenera le figure della tesi dai risultati sperimentali
```
