# Registro delle decisioni

> **Cos'è questo file.** Il verbale cumulativo di ogni decisione presa sul progetto:
> cosa è stato deciso, quando, perché, quali alternative sono state scartate e cosa
> resta aperto. Non si riscrive: si aggiunge in fondo.
>
> **Perché esiste.** Alla discussione la commissione chiede *perché* hai fatto una
> scelta, non solo *cosa* hai fatto. Fra sei mesi non ricorderai le alternative che
> avevi valutato. Questo file le conserva, e alimenta direttamente il capitolo di
> metodologia e l'appendice sulla riproducibilità.
>
> **Rapporto con gli altri documenti:**
> - `docs/project-plan.md` → stato *attuale* del progetto (fotografia)
> - `docs/registro-decisioni.md` → *storia* delle decisioni (film) ← questo file
> - `docs/decisions/NNNN-*.md` → approfondimento di una singola decisione strutturale
> - `experiments/registry.md` → tracciabilità dei run sperimentali
>
> **Regola d'uso:** ogni volta che una decisione viene presa o rovesciata, si aggiunge
> una riga qui nello stesso commit che la applica. Una decisione superata non si
> cancella: si marca `superata` e si indica da cosa.

**Ultimo aggiornamento:** 2026-07-31

---

## 1. Dati raccolti

Informazioni acquisite in fase di intervista. Le voci `DA CONFERMARE` non sono state
verificate: non vanno usate come se fossero certe.

| Voce | Valore | Fonte | Stato |
|---|---|---|---|
| Autore | Gian | dichiarato | confermato |
| Corso di laurea | Laurea Magistrale in Ingegneria Informatica | dichiarato | confermato |
| Classe | LM-32 | dichiarato | confermato |
| Ateneo | Università degli Studi di Bergamo | dichiarato | confermato |
| Dipartimento | `DA CONFERMARE` (ipotesi: DIGIP) | inferito dal template | **non verificato** |
| Relatore — nome | `DA DEFINIRE` | — | mancante |
| Relatore — area | Intelligenza Artificiale e Informatica Etica | dichiarato | confermato |
| Correlatore | `DA DEFINIRE` | — | mancante |
| Matricola | `DA DEFINIRE` | — | mancante |
| Argomento | IA generativa e creatività in ambito artistico; analisi di GAN e CAN | dichiarato | confermato |
| Tipo di tesi | Sperimentale con componente analitico-etica | dichiarato | confermato |
| Sessione di laurea | Settembre — poi dichiarata non vincolante | dichiarato | **ambiguo, vedi Q1** |
| Esami mancanti | `DA DEFINIRE` | — | mancante |
| Ore/settimana disponibili | `DA DEFINIRE` | — | mancante |
| Anno accademico | 2025/2026 `DA CONFERMARE` | ipotesi | **non verificato** |

### Informazioni chieste e non ancora fornite

Restano aperte dal blocco di intervista iniziale. Non sono state riempite con ipotesi.

- Numero di esami mancanti e ore settimanali realisticamente disponibili
- Nome del relatore, sue preferenze metodologiche, tipo di tesi che si attende
- Criteri di valutazione adottati dalla commissione
- Regolamento UniBg: lunghezza attesa, frontespizio ufficiale per la magistrale,
  scadenze di consegna
- Esistenza di lavoro già prodotto (bibliografia, codice, pagine scritte)
- Livello di innovazione desiderato
- Budget di calcolo disponibile
- Competenze pregresse su PyTorch, LaTeX, git

---

## 2. Decisioni prese

### D-001 — Monorepo unico per tesi e codice
**Data:** 2026-07-31 · **Stato:** attiva · **Approfondimento:** [ADR-0001](decisions/0001-monorepo.md)

Tesi LaTeX, codice sperimentale, configurazioni e documentazione nello stesso repository.

**Alternative scartate:** due repository separati; repo tesi con il codice come git submodule.

**Motivazione:** un solo commit lega testo, codice e figura, quindi ogni numero della
tesi è riconducibile allo stato esatto del codice che l'ha prodotto.

**Nota sul percorso decisionale:** la scelta iniziale era il *submodule*. È stata
contestata e poi rovesciata: il submodule richiede un doppio commit (codice, poi
puntatore nel repo padre) e il suo fallimento silenzioso — dimenticare di aggiornare
il puntatore — produce esattamente la perdita di tracciabilità che si voleva evitare.
Il submodule si giustifica quando il codice ha un ciclo di rilascio autonomo o è
condiviso tra progetti: non è il caso di una tesi individuale.

**Conseguenza operativa:** se dopo la discussione servirà un repository pubblico del
solo codice, si estrarrà con `git subtree split` preservando la storia.

---

### D-002 — Lingua della tesi: italiano
**Data:** 2026-07-31 · **Stato:** attiva

Elaborato interamente in italiano, senza abstract in inglese. La terminologia tecnica
resta in inglese e non viene tradotta.

**Alternative scartate:** italiano con abstract inglese; tesi interamente in inglese.

**Motivazione:** scelta dell'autore.

**Conseguenza:** `babel` configurato su `italian`, `cleveref` con opzione `italian`.
Riusare i capitoli per una pubblicazione internazionale richiederà una traduzione:
è un costo differito, non eliminato.

---

### D-003 — Stile bibliografico authoryear
**Data:** 2026-07-31 · **Stato:** attiva · **Approfondimento:** [ADR-0002](decisions/0002-toolchain.md)

`biblatex` con stile `authoryear`: nel testo compare `(Elgammal et al., 2017)`.

**Alternativa scartata:** stile numerico IEEE, usato nel template di riferimento.

**Motivazione:** in una tesi che discute criticamente i lavori altrui e intreccia
argomentazione tecnica ed etica, il lettore riconosce l'autore senza saltare in
bibliografia. Il numerico è più compatto ma rende la discussione meno scorrevole.

**Reversibilità:** alta. Lo stile è isolato in una sola riga di
`thesis/preamble/packages.tex`; il cambio costa una compilazione.

---

### D-004 — Weights & Biases per il tracciamento degli esperimenti
**Data:** 2026-07-31 · **Stato:** attiva · **Approfondimento:** [ADR-0002](decisions/0002-toolchain.md)

**Alternative scartate:** TensorBoard + CSV locali; MLflow self-hosted.

**Motivazione:** gratuito per uso accademico; non richiede stato locale, quindi
funziona con i servizi di training remoto che clonano il codice da GitHub (vedi D-006);
conserva automaticamente iperparametri, curve e campioni generati.

**Conseguenza operativa:** serve un account W&B e la variabile d'ambiente
`WANDB_API_KEY`. La chiave non va mai committata.

---

### D-005 — Zotero + Better BibTeX come unica fonte della bibliografia
**Data:** 2026-07-31 · **Stato:** attiva · **Approfondimento:** [ADR-0002](decisions/0002-toolchain.md)

`thesis/references/bibliography.bib` diventa un file **generato** da Zotero via export
automatico. I PDF dei paper restano fuori dal repository.

**Alternative scartate:** `.bib` gestito a mano; PDF dei paper dentro il repo.

**Motivazione:** elimina gli errori di trascrizione dei metadati, che nelle tesi sono
una fonte ricorrente di rilievi. Tenere i PDF nel repo lo appesantirebbe e porrebbe un
problema di ridistribuzione di materiale sotto copyright.

**Conseguenza operativa:** il `.bib` non si modifica più a mano; le correzioni si fanno
in Zotero e si riesporta. Ogni paper letto va schedato in `docs/literature/`.

---

### D-006 — Addestramento su servizi remoti che clonano il codice da GitHub
**Data:** 2026-07-31 · **Stato:** attiva

Il training non avviene su hardware locale ma su servizi online che leggono il codice
direttamente dal repository GitHub.

**Motivazione:** dichiarata dall'autore.

**Conseguenze vincolanti sull'architettura del codice:**

- Struttura **script-first**, non notebook-first: i notebook restano sottili e importano
  da `src/`.
- Package Python installabile (`pip install -e .`), nessun path assoluto della macchina locale.
- Dipendenze bloccabili (`make freeze` → `requirements-lock.txt`).
- Segreti solo via variabili d'ambiente.
- Bootstrap automatizzato in `scripts/bootstrap_remote.sh`.
- **Le sessioni remote sono effimere:** il checkpointing frequente su storage
  persistente non è un optional, è una condizione per non perdere giorni di training.

---

### D-007 — Configurazioni via Hydra, nessun iperparametro nel codice
**Data:** 2026-07-31 · **Stato:** attiva · **Approfondimento:** [ADR-0002](decisions/0002-toolchain.md)

Un esperimento è definito da un file di configurazione versionato in `configs/`,
lanciabile con `python -m tesi_gan.cli train experiment=<nome>`.

**Motivazione:** un iperparametro scritto nel codice rende l'esperimento non citabile:
non si può indicare *quale* configurazione ha prodotto un risultato.

---

### D-008 — Il template di riferimento si segue nella struttura, non nelle pratiche git
**Data:** 2026-07-31 · **Stato:** attiva

Dal repository `phd-thesis-tex` (tesi di dottorato in elettronica, UniBg) sono stati
ripresi: orchestratore `main.tex`, split in `capitoli/`, `references/` per i `.bib`,
cartella per le figure, `biblatex` + `biber`, build con `latexmk`, frontespizio UniBg
con logo vettoriale.

**Sono stati invece corretti quattro difetti del template:**

| Difetto nel template | Correzione adottata |
|---|---|
| Nessun `.gitignore`: `.aux`, `.log`, `.fls`, `.bbl` e `main.pdf` versionati | `.gitignore` completo; artefatti isolati in `thesis/build/` via `latexmkrc` |
| Versionamento per duplicazione: `capitolo04-tot copy.tex`, `v1-capitolo02-28nm.tex`, `temp.txt` | Un solo file per capitolo; la storia la fa git. Regola scritta in `CLAUDE.md` §2.3 |
| `.bib` frammentati tra `capitoli/` e `references/` | Un unico `references/bibliography.bib` generato da Zotero |
| Naming ambiguo: `capitolo01.tex`, `capitolo01-sensori.tex`, `capitolo01-progetti.tex` sono tre capitoli distinti | Schema `NN-slug.tex` con numerazione stabile |

**Nota:** il template è una tesi di **dottorato**. Il frontespizio è stato riadattato
ma va verificato contro il modello ufficiale per la laurea magistrale (vedi V-001).

---

### D-009 — Struttura dell'elaborato in 8 capitoli + 2 appendici
**Data:** 2026-07-31 · **Stato:** **provvisoria** — da validare con il relatore

Introduzione · Fondamenti teorici · Stato dell'arte · Metodologia · Implementazione ·
Risultati · Discussione · Conclusioni. Appendici: iperparametri, riproducibilità.

**Scelte di impianto degne di nota:**

- **Risultati e Discussione separati.** Il capitolo dei risultati riporta, quello di
  discussione interpreta. Mescolarli è il difetto più comune nelle tesi sperimentali e
  rende impossibile distinguere il dato dall'opinione.
- **Il capitolo di discussione è la sede in cui la componente etica si salda alla
  sperimentale.** È il punto di maggior valore aggiunto, data l'area del relatore.
- **La sezione sui limiti è obbligatoria**, non opzionale: un capitolo senza limiti
  dichiarati è il primo bersaglio della commissione.
- **Lo stato dell'arte ha una sezione sulla metodologia della revisione** (database,
  stringhe di ricerca, criteri di inclusione): rende la rassegna riproducibile e
  difendibile invece che aneddotica.

---

## 3. Questioni aperte

Ordinate per criticità. Le prime due bloccano il dimensionamento dell'intero progetto.

### Q1 — Sessione di laurea 🔴 bloccante
**Stato:** ambiguo

Inizialmente indicata come settembre. Alla mia obiezione — al 31 luglio 2026 restano
4-6 settimane utili, con agosto in cui relatore e segreteria sono di fatto
irraggiungibili, il che non basta per un impianto sperimentale su GAN partendo da zero
— la risposta è stata di non preoccuparsi delle scadenze. **Non è chiaro se questo
significhi che la sessione è stata spostata o che l'obiezione è stata accantonata.**

Da questa dipende tutto: un impianto con studio percettivo su soggetti umani richiede
mesi, una replica ridotta su dataset piccolo richiede settimane.

### Q2 — Impianto sperimentale 🔴 bloccante
**Stato:** aperta · **Approfondimento:** [ADR-0003](decisions/0003-impianto-sperimentale.md)

Dichiarato «non ancora deciso». Tre alternative sul tavolo:

| Opzione | Vantaggi | Rischi |
|---|---|---|
| A — Replica della CAN su WikiArt | Riferimento solido, confronto immediato con baseline | Contributo originale scarso se ci si ferma alla replica |
| B — Baseline DCGAN + variante originale | Contributo proprio, calcolo contenuto | Risultato negativo o non significativo |
| C — Esperimento come caso di studio a supporto dell'analisi etica | Coerente con l'area del relatore, calcolo minimo | Possibile giudizio di leggerezza tecnica per una LM-32 |

Osservazione: una replica ben eseguita **accompagnata da un'analisi critica originale
dei suoi limiti** è spesso più difendibile di una variante originale mal validata.

L'architettura del codice è stata predisposta agnostica rispetto a questa scelta:
`configs/` contiene sia `dcgan.yaml` sia `can.yaml`, entrambi parametrici.

### Q3 — Peso relativo tra componente tecnica ed etica 🟠 alta
Determina quale capitolo porta il contributo principale. Da concordare col relatore,
la cui area include l'informatica etica.

### Q4 — Dataset 🟠 alta
Non scelto. Va verificata la licenza **prima** del download: usare un dataset di opere
d'arte senza verificarne i termini sarebbe un'incoerenza che una tesi la quale discute
le implicazioni etiche dell'IA generativa non può permettersi.

### Q5 — Metriche di valutazione 🟠 alta
Candidate: FID, Inception Score, studio percettivo. **Avvertenza metodologica:** FID e
IS misurano fedeltà e varietà, *non* creatività. Usarle come proxy della creatività
senza dichiararne esplicitamente il limite è un errore facilmente rilevabile in sede
di discussione.

### Q6 — Studio percettivo con soggetti umani? 🟡 media
Se incluso: consenso informato, probabile vaglio etico, tempi non comprimibili.
Va deciso presto perché cambia la pianificazione.

### Q7 — Servizio di calcolo e budget 🟡 media
Non specificato quale servizio remoto verrà usato né con quale budget. Determina
risoluzione delle immagini, dimensione del dataset e numero di run comparativi.

### Q8 — Domande di ricerca 🟠 alta
Non ancora formulate. Dipendono da Q2 e dalla revisione della letteratura: formulare
domande di ricerca prima di conoscere lo stato dell'arte produce quasi sempre domande
già risolte o mal poste.

---

## 4. Verifiche da fare

Punti su cui è stata fatta un'ipotesi o un adattamento che va confermato da una fonte
autorevole prima della consegna.

### V-001 — Frontespizio ufficiale per la laurea magistrale 🔴
Il frontespizio attuale è un adattamento di quello di una tesi di **dottorato**.
Verificare in segreteria UniBg il modello ufficiale per la LM-32.
File: `thesis/frontespizio.tex`

### V-002 — Metadati bibliografici 🟠
`thesis/references/bibliography.bib` contiene 11 lavori fondativi inseriti in forma
minimale (autori, titolo, anno, sede) proprio per limitare il rischio di dettagli
errati. **Vanno importati in Zotero e verificati alla fonte originale.** Da quel
momento il file è generato e non si tocca più a mano.

### V-003 — Dipartimento e anno accademico 🟡
`thesis/metadata.tex` riporta valori ipotizzati per dipartimento e anno accademico.
Confermarli.

### V-004 — Campi `TODO` in metadata.tex 🟠
Nome del relatore e matricola sono segnaposto letterali `TODO`: compaiono nel PDF
compilato. Vanno compilati prima di qualsiasi consegna al relatore.

### V-005 — Distribuzione LaTeX completa 🟡
La compilazione è stata verificata con successo (32 pagine, nessun warning) ma in un
ambiente privo di `biblatex` e `babel-italian`, quindi con quei due componenti
temporaneamente disattivati. Sulla macchina di lavoro serve **TeX Live completo** o
MacTeX, oppure Overleaf. Con una distribuzione minimale la build fallisce.

---

## 5. Stato dell'infrastruttura

Verificato il 2026-07-31.

| Componente | Stato | Verifica eseguita |
|---|---|---|
| Struttura del monorepo | completa | 58 file versionati, primo commit pulito |
| Documento LaTeX | compila | 32 pagine, zero warning, zero riferimenti indefiniti |
| Frontespizio UniBg | presente | logo vettoriale importato dal template |
| Elenco acronimi | funzionante | `makeglossaries` eseguito nella catena di build |
| Package Python | importabile | `import tesi_gan` OK |
| Configurazioni Hydra | valide | 4 file YAML parsati senza errori |
| Script di bootstrap | sintatticamente valido | `bash -n` OK |
| Makefile | funzionante | 9 target documentati |
| `.gitignore` | attivo | nessun artefatto di build versionato |

**Anomalia nota:** nella cartella `.git` sono rimasti file di lock (`HEAD.lock`) non
rimovibili dall'ambiente in cui ho lavorato. Bloccano i commit finché non vengono
eliminati manualmente:

```bash
cd "/Users/gian/Documents/Tesi Gian" && rm -f .git/HEAD.lock .git/index.lock
```

---

## 6. Prossimi passi

In ordine di dipendenza. Ogni passo è bloccato dal precedente.

1. **Risolvere Q1** (sessione di laurea). Senza, il piano non è dimensionabile.
2. **Incontro col relatore:** presentare l'impianto, raccogliere le sue preferenze su
   Q2 e Q3, verificare V-001 e i criteri di valutazione. Verbalizzare in
   `docs/meetings/`.
3. **Revisione della letteratura:** definire stringhe di ricerca e criteri, schedare i
   lavori in `docs/literature/`, arrivare a un gap dichiarato.
4. **Formulare le domande di ricerca** (Q8) e farle approvare.
5. **Chiudere ADR-0003** (Q2): impianto, dataset, metriche.
6. **Primo esperimento** end-to-end, anche minimale, per validare la pipeline prima di
   investire tempo di calcolo.

---

## 7. Cronologia delle sessioni

| Data | Attività | Esito |
|---|---|---|
| 2026-07-31 | Intervista iniziale; analisi del template `phd-thesis-tex`; impostazione del monorepo | D-001…D-009 decise; Q1…Q8 aperte; infrastruttura verificata |
