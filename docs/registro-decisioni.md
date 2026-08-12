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

**Ultimo aggiornamento:** 2026-08-11

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

### D-010 — Impianto sperimentale: confronto controllato DCGAN → CAN
**Data:** 2026-08-02, riaperta il 2026-08-03, **ratificata dall'autore il 2026-08-03**
**Stato:** attiva · **Approfondimento:** [ADR-0003](decisions/0003-impianto-sperimentale.md)

> **Nota sul percorso, da conservare.** La prima stesura di questa decisione è stata
> formulata dall'assistente a partire da un'indicazione di massima dell'autore, e
> scritta come se fosse già una decisione presa. Non lo era. È stata riaperta,
> discussa e poi ratificata con tre precisazioni che nella prima stesura mancavano.

**Precisazioni emerse dalla discussione del 2026-08-03:**

1. **Taglio espositivo.** Il contributo è il *delta*: quali modifiche servono per
   passare da una GAN a una CAN, e che effetto hanno. Non «quale delle due vince».
2. **Riaddestramento da zero per entrambe le condizioni**, non fine-tuning. La
   formulazione iniziale («poi da lì le modifiche») era ambigua fra le due cose.
   Proseguire dai pesi della GAN avrebbe dato alla CAN il doppio delle epoche
   totali, confondendo l'effetto del meccanismo con l'effetto di aver addestrato di più.
3. **Tre seed per condizione**, sei run in totale. Un run per condizione non dà
   stima della varianza, e le GAN oscillano molto fra seed: senza repliche, una
   differenza osservata potrebbe essere rumore. È l'obiezione più prevedibile e più
   economica da neutralizzare (stimate ~4 ore di GPU aggiuntive, pochi euro).

Due addestramenti in sequenza sullo stesso dataset, con generatore identico, backbone
del discriminatore identica, stessi iperparametri, stesso seed, stesso numero di
epoche. **L'unica variabile indipendente è la funzione di perdita.**

**Alternative scartate:** replica integrale della CAN a 256×256 (fuori budget
temporale); variante architetturale originale (rischio di risultato non significativo
con un solo tentativo disponibile); esperimento puramente illustrativo a supporto
dell'analisi etica (rischio di leggerezza tecnica per una LM-32).

**Motivazione:** con una sola variabile indipendente, qualunque differenza osservata
è attribuibile al meccanismo di ambiguità stilistica e a nient'altro. Il contributo
non è inventare un'architettura ma isolarne rigorosamente l'effetto e misurare la
distanza fra ciò che produce e ciò che la letteratura afferma che produca.

**Conseguenza vincolante sul codice:** DCGAN e CAN **non** sono due implementazioni.
Sono la stessa classe con un parametro booleano (`style_head`). Se fossero separate,
ogni differenza nei risultati sarebbe confusa con differenze di implementazione.
L'invariante è verificato automaticamente da `tests/test_impianto.py`: se quei test
falliscono, non è un bug, è il confronto che non è più valido.

**Percorso decisionale:** la scelta è stata presa senza il relatore, in agosto, per
non perdere le uniche settimane utili. Va portata al primo ricevimento e verbalizzata
in `docs/meetings/`. Se il relatore la rovescia, ADR-0003 si marca `superato`.

---

### D-011 — Dataset: sottoinsieme bilanciato di WikiArt
**Data:** 2026-08-02, riaperta e ridiscussa il 2026-08-03
**Stato:** attiva **nel criterio**, 🔶 **aperta nella lista esatta degli stili** · **Approfondimento:** [ADR-0004](decisions/0004-dataset.md)

> **Superata il 2026-08-03 da D-014.** WikiArt è stato abbandonato in favore di
> ArtBench-10. Questa voce resta perché il criterio di selezione degli stili che vi
> era stato definito è sopravvissuto al cambio di dataset, e perché il confronto fra
> i due dataset è materiale per il capitolo di metodologia.

**Deciso il 2026-08-03 — il criterio di selezione degli stili.** Gli stili si
scelgono per **due** requisiti congiunti, non uno solo:

1. **Massima distanza visiva** fra loro, perché a 64×64 su un dominio troppo
   eterogeneo entrambe le condizioni producono immagini indistinguibili e non
   resta niente da confrontare.
2. **Opere di pubblico dominio**, cioè movimenti pre-Novecento con autori morti da
   oltre settant'anni. Esclude cubismo, surrealismo e pop art, che sono i più
   vistosi ma anche i più problematici.

Il secondo requisito non era nella prima stesura ed è il guadagno principale della
ridiscussione: scioglie gran parte del nodo etico **senza costare nulla** sul piano
sperimentale, perché ukiyo-e, barocco, rinascimento e impressionismo sono già fra
loro lontanissimi.

**Ancora da decidere: la lista.** Dipende dai conteggi reali, perché in un
sottoinsieme bilanciato **la classe meno popolata determina la dimensione di tutte
le altre**. Stime da campione troncato al 2%, da non usare per nessun altro scopo:
impressionismo ~8.000, barocco ~3.600, rinascimento nordico ~1.400, ukiyo-e ~650,
puntinismo ~200. Se reggono, il puntinismo è fuori e l'ukiyo-e fa da tetto attorno
alle 900 opere per classe.

I numeri veri si ottengono con `python -m tesi_gan.data.inventory`, che scarica i
soli indici CSV (~5 MB, nessuna immagine) e produce la tabella esatta.

**Conseguenza da tenere presente:** con 4.000-7.000 immagini si entra nel regime
«GAN con pochi dati», che è un tema metodologico riconosciuto e non un intoppo.
`karras2020training` è già in bibliografia ed è il riferimento su quel punto.

Da 5 a 10 stili ben popolati, bilanciati, a 64×64. Nessuna ridistribuzione di dati
né di pesi.

**Alternative scartate:** The Met Open Access (licenza CC0 inequivocabile, ma privo
di etichette di stile art-storico, che la CAN richiede); Art Institute of Chicago
(copertura parziale delle etichette); dataset costruito ad hoc (proibitivo nei tempi).

**Motivazione:** il vincolo dominante è che ADR-0003 richiede etichette di stile,
senza le quali la testa di classificazione non è addestrabile.

**La conseguenza più importante non è tecnica.** La tensione fra «il dataset standard
del settore è WikiArt» e «WikiArt contiene opere sotto copyright» va **dichiarata
nella tesi**, non aggirata. Una tesi che discute le implicazioni etiche dei modelli
generativi addestrati su opere d'arte, e che tace sulla licenza del proprio dataset,
perde credibilità sull'intera componente etica. Rilevare che Elgammal et al. hanno
usato WikiArt senza discuterne i termini è un contributo critico originale a costo
zero di calcolo.

---

### D-012 — Studio percettivo leggero, campione di convenienza
**Data:** 2026-08-02 · **Stato:** 🔶 **RIAPERTA il 2026-08-03** — proposta non ratificata

Questionario online su poche decine di rispondenti, con consenso informato.

**Alternative scartate:** nessuno studio umano (lascerebbe la valutazione alle sole
metriche automatiche, che per ammissione della tesi stessa non misurano creatività);
replica del protocollo di Elgammal (mesi di lavoro, non compatibile con il tempo a disposizione).

**Motivazione:** serve almeno un giudizio umano perché il capitolo dei risultati non
poggi interamente su FID e IS, di cui la tesi dichiara i limiti.

**Limite da dichiarare senza attenuanti:** campione di convenienza, non
rappresentativo, numerosità bassa. I risultati vanno presentati come **indicativi**,
mai come statisticamente significativi. Presentare un campione di convenienza come
evidenza forte è un errore che la commissione rileva immediatamente; dichiararlo come
esplorativo è invece perfettamente difendibile.

---

### D-014 — Dataset: ArtBench-10, sei stili
**Data:** 2026-08-03 · **Stato:** attiva · **Supera:** D-011 · **Approfondimento:** [ADR-0004](decisions/0004-dataset.md)

**ArtBench-10** ristretto a `ukiyo_e`, `renaissance`, `baroque`, `romanticism`,
`realism`, `impressionism`. Trentamila immagini di training, cinquemila per stile.

**Alternative scartate:** sottoinsieme di WikiArt (D-011); The Met Open Access e
Rijksmuseum (licenza limpida ma senza etichette di stile art-storico, quindi la CAN
non sarebbe addestrabile); Art500k, OmniArt, Painter by Numbers (sbilanciati).

**Motivazione.** ArtBench è **bilanciato per costruzione**, il che elimina il
problema che con WikiArt si stava cercando di aggirare a mano: lì la classe meno
popolata avrebbe determinato la dimensione di tutte le altre, portando a circa 4.500
immagini contro le 30.000 di ora. In più ha annotazioni pulite, formato ImageFolder
già compatibile col codice esistente, e **benchmark pubblicati sullo stesso
dataset**: questo permette di confrontare il proprio FID con un valore di
letteratura invece di riportarlo isolato.

**Perché questi sei.** Il criterio di D-011 sopravvive: pubblico dominio più
distanza visiva. Dei dieci stili di ArtBench il solo Surrealismo è ancora sotto
copyright ed è escluso. La sequenza Rinascimento → Barocco → Romanticismo →
Realismo → Impressionismo è la cronologia canonica della pittura occidentale, con
l'Ukiyo-e come contrappunto non occidentale — e con il legame storico del
giapponismo, che lo lega agli impressionisti invece di lasciarlo isolato.

**Limite dichiarato.** Barocco, Romanticismo e Realismo sono tutti pittura a olio
scura: il discriminatore farà più fatica a separarli. È il costo della coerenza
cronologica, ed è misurabile — va prodotta la **matrice di confusione della testa di
stile** e commentata, perché l'entropia della posterior va letta alla luce di quali
classi vengono effettivamente confuse.

**Conseguenza sul codice.** `data.download` ha ora la selezione **esplicita** degli
stili (`--stili`): con un dataset bilanciato «prendi i più popolati» non seleziona
nulla di sensato, sono tutti uguali, e la scelta ricadrebbe sull'ordine alfabetico.
Il bilanciamento viene inoltre forzato sul minimo effettivo, non sul valore
richiesto.

---

### D-013 — Servizio di calcolo: RunPod con RTX 4090
**Data:** 2026-08-03 · **Stato:** attiva

**Alternative scartate:** Colab Pro (~10 $/mese: azzera il setup ma è notebook-first
e costa più dell'intero conto di calcolo); Vast.ai (il più economico ma marketplace
peer-to-peer con macchine interrompibili e host di qualità variabile); Lambda Labs
(A100 e H100 con SLA: ferro sovradimensionato per questo carico).

**Motivazione.** Il carico è piccolo: una DCGAN a 64×64 su qualche migliaio di
immagini non richiede A100 né H100, una RTX 4090 avanza. RunPod fattura al secondo,
offre volumi persistenti su cui mettere il dataset una volta sola, e sposa la
struttura script-first che clona da GitHub decisa in D-006.

**Ordine di grandezza:** ~1 ora di GPU per run stimata, sei run, quindi **l'intera
parte sperimentale costa fra i 2 e i 4 dollari**. La stima va sostituita col tempo
reale misurato sul primo run. I listini cambiano di continuo: vanno ricontrollati
prima di impegnarsi.

**Da annotare quando disponibile:** modello di GPU effettivamente usato, ore
consumate e costo totale. Vanno nell'appendice sulla riproducibilità.

---

### D-015 — Classificatore di stile terzo come giudice dell'ambiguità
**Data:** 2026-08-03 · **Stato:** attiva · **Approfondimento:** [ADR-0005](decisions/0005-giudice-ambiguita.md)

L'ambiguità stilistica si misura con un **classificatore di stile addestrato una volta
sola sui soli dati reali e poi congelato**, non con la testa di stile del
discriminatore. Lo stesso identico giudice valuta entrambe le condizioni e tutti i
seed. Modulo: `src/tesi_gan/evaluation/style_classifier.py`.

**Il problema che risolve.** La metrica precedente aveva due difetti che la rendevano
inservibile per il confronto di D-010:

1. **Non calcolabile sulla DCGAN**, che la testa di stile non ce l'ha. La condizione di
   controllo sarebbe rimasta senza misura, e il confronto non sarebbe esistito.
2. **Non indipendente**: quel discriminatore si è addestrato *contro* quel generatore.
   Chiedergli se il generatore lo confonde è chiedere a una parte in causa di arbitrare
   la propria partita.

Senza questa correzione i sei run avrebbero prodotto FID e IS — due metriche che per
costruzione penalizzano la CAN — e nessuna misura dell'effetto cercato. La lacuna è
stata trovata rileggendo il codice prima di affittare la GPU.

**Alternative scartate:**

| Alternativa | Perché no |
|---|---|
| Tenere solo la testa di stile del discriminatore | Non confrontabile, non indipendente: è il difetto da correggere |
| ResNet-18 pre-addestrata su ImageNet | Erediterebbe il bias fotografico che la tesi contesta a FID e IS: si muoverebbe un'obiezione e poi la si commetterebbe |
| Un giudice riaddestrato per ogni run | Introdurrebbe una variabile nascosta e renderebbe le entropie non confrontabili |

**Scelte di dettaglio, tutte motivate dalla validità del confronto:**

- **Stessa famiglia architetturale della backbone del discriminatore.** Un giudice
  molto più capace misurerebbe un'ambiguità che nel gioco avversario non ha mai avuto
  un ruolo; molto meno capace, misurerebbe la propria incompetenza.
- **Addestrato da zero**, non pre-addestrato (vedi tabella sopra).
- **Split stratificato e seedato**, con accuratezza di validazione registrata. Sotto
  `MIN_VAL_ACCURACY = 0.60` il modulo avvisa: l'incertezza di un giudice incapace non è
  informativa.
- **Seed proprio** (`style_judge.seed`), indipendente dai tre seed dei run: il giudice
  non fa parte delle ripetizioni dell'impianto.
- **Si addestra una volta sola.** Il comando rifiuta di sovrascriverne uno esistente
  senza `--force`, perché riaddestrarlo invaliderebbe i run già valutati.
- **Il caricamento verifica le classi**: un giudice addestrato su altri stili produce
  numeri privi di significato, e il fallimento deve essere rumoroso.

**Confondimento da dichiarare in tesi, non aggirabile con il codice.** Un'entropia alta
significa «il classificatore non sa attribuire uno stile», e ci sono **due** ragioni
perché accada: l'immagine è pittoricamente sensata ma stilisticamente ibrida (l'effetto
cercato), oppure è rumore informe (un generatore collassato). **Un generatore fallito
ottiene ambiguità massima.** L'entropia va quindi sempre letta accanto al FID e alla
griglia di campioni: alta con FID basso è l'esito interessante, alta con FID pessimo è
un modello che non ha imparato a dipingere. Il codice emette un avviso quando ricorre
il secondo caso, ma la dichiarazione in tesi resta obbligatoria.

**Ancore di lettura, calcolate e salvate insieme al giudice:** entropia sulle immagini
**reali** di validazione (il pavimento) e `log(K)` (il soffitto). Un'entropia
normalizzata senza il confronto col pavimento è un numero che sembra significare
qualcosa e non significa niente. Accuratezza ed entropia sui reali vanno in appendice.

---

### D-016 — Figure dei campioni generate dal codice
**Data:** 2026-08-03 · **Stato:** attiva

Quattro figure prodotte automaticamente, modulo `src/tesi_gan/evaluation/campioni.py`:
griglia per epoca (con condizione, seed ed epoca nel nome del file), **griglia
annotata dal giudice terzo**, evoluzione a rumore fisso ricostruita dai checkpoint,
griglia di riferimento degli stili reali.

**Vincolo concettuale.** Il generatore è **incondizionato**: un'immagine generata non
ha uno stile vero da stampare in didascalia. L'unica etichetta legittima è la
*predizione* del giudice, ed è un'affermazione su come un classificatore legge
l'immagine, non sulla sua natura. Scrivere «Barocco» sotto un campione generato
sarebbe un errore concettuale — in una tesi su questo tema, non una sfumatura. La
funzione `didascalia_griglia_annotata()` genera il testo corretto.

**Correzione collaterale:** il nome del run W&B non conteneva il seed, quindi i tre run
per condizione (D-010) sarebbero stati indistinguibili nella dashboard. È lo stesso
errore già corretto sui percorsi dei checkpoint, ricomparso altrove.

---

### D-017 — Selezione degli stili rivista sulla base della matrice di confusione
**Data:** 2026-08-03 · **Stato:** attiva · **Modifica:** D-014

Fuori `romanticism` e `realism`, dentro `art_nouveau` ed `expressionism`.
Insieme finale: **ukiyo_e, renaissance, baroque, art_nouveau, expressionism,
impressionism**.

**Perché.** Il giudice di stile (D-015), addestrato sui sei stili originali e
validato sullo split `test` ufficiale, si è fermato al **52,7%** di accuratezza. La
matrice di confusione ha mostrato che il problema non era distribuito:

| Stile | Corrette | Caso puro = 16,7% |
|---|---|---|
| `ukiyo_e` | 91% | separabile nettamente |
| `baroque` | 65% | accettabile |
| `impressionism` | 59% | accettabile |
| `renaissance` | 45% | confuso col Barocco (33%) |
| `realism` | 30% | disperso |
| `romanticism` | **26%** | 1,6× il caso: praticamente non riconosciuto |

Il Romanticismo non sbagliava verso un vicino ma si spargeva su quattro classi
(23% Barocco, 20% Impressionismo, 18% Realismo). Non è confusione fra stili
adiacenti: **a 64×64 non ha un'identità visiva propria**, essendo definito più da
soggetto e atmosfera che da una tecnica riconoscibile. Il Realismo veniva scambiato
per Impressionismo nel 28% dei casi, confusione che non era stata prevista.

**Perché contava e non era solo estetica.** L'entropia sui reali si assestava a
0,811 nats, cioè **0,45 normalizzata su un massimo di 1**. Quel pavimento alto
derivava in buona parte dalle tre classi opache: il giudice era incerto già
sull'arte vera. Poiché l'effetto della CAN si misura come innalzamento
dell'entropia, un pavimento a 0,45 comprime lo spazio in cui l'effetto può
manifestarsi. Rimuovere le classi opache non è un ritocco cosmetico: **allarga la
dinamica della metrica su cui si regge l'intero confronto**.

**Costo accettato:** si perde l'arco cronologico Rinascimento → Barocco →
Romanticismo → Realismo → Impressionismo che aveva motivato la selezione originale,
con l'Ukiyo-e come contrappunto e il legame storico del giapponismo. Era una
narrazione elegante; è stata scambiata con la misurabilità.

**Alternative scartate:** tenere i sei originali dichiarando il limite (metrica
debole); ridurre a quattro stili (confronto meno ricco, e `renaissance` resta
impigliato col `baroque`); migliorare il giudice prima di toccare gli stili
(l'ipotesi era che il 52,7% fosse debolezza del classificatore, ma la dispersione
degli errori del Romanticismo indica sovrapposizione reale, non incapacità).

**La matrice di confusione resta un risultato da riportare in tesi**, non solo un
passaggio diagnostico: che il Romanticismo non sia una categoria visivamente
coerente a bassa risoluzione è un'osservazione difendibile e non banale.

**Conseguenza operativa:** vanno rifatte la preparazione dei dati (train e
riferimento) e l'addestramento del giudice. I run precedenti al 2026-08-03 non sono
confrontabili con quelli successivi.

---

### D-018 — Impianto a 128px affiancato a quello a 64px
**Data:** 2026-08-03 · **Stato:** attiva · **Modifica:** D-010 (che resta valida a 64px)

Il confronto DCGAN/CAN viene replicato a **128×128**, senza sostituire l'impianto a
64px: i due convivono, con dati, giudice, checkpoint e risultati separati.

**Perché.** Tre iterazioni del giudice di stile (`experiments/giudice-stile.md`)
avevano isolato la risoluzione come fattore limitante: due insiemi di stili scelti con
criteri opposti si erano fermati entrambi fra il 52% e il 58% di accuratezza. A 128px
il giudice J3 raggiunge 0,623, ma soprattutto **abbassa l'entropia sui reali da 0,531
a 0,401**, allargando del 28% lo spazio in cui l'effetto della CAN può manifestarsi.

**Nota su un errore di impostazione.** La soglia dichiarata prima della verifica era
sull'**accuratezza** (sopra 0,70 si procede). Il guadagno si è invece manifestato sul
**pavimento dell'entropia**, che è la grandezza da cui dipende la sensibilità della
metrica. La soglia era sulla variabile sbagliata: va riportato, perché mostra che la
metrica di controllo va motivata quanto quella di risultato.

**Conseguenze sul codice:**

- Le architetture derivano il numero di stadi da `data.image_size` invece di averlo
  cablato. **Non è una seconda coppia di classi:** quella avrebbe distrutto
  l'invariante di ADR-0003. A 64px l'architettura risultante è identica a prima, quindi
  i checkpoint esistenti restano caricabili.
- I test dell'impianto sono parametrizzati su `[64, 128]`: l'invariante è verificato a
  ogni risoluzione.
- **Tutti i percorsi di output includono la risoluzione.** Senza, il 128 avrebbe
  sovrascritto il 64 in silenzio.
- `build_generator(cfg)` è l'unico modo di costruire un generatore da configurazione,
  dopo che lo stesso errore — dimenticare `image_size` — si è presentato tre volte in
  punti diversi.

**I due impianti non sono confrontabili nella stessa tabella:** cambiano rete, dati,
giudice e riferimenti di entropia. Il loro confronto riguarda l'effetto della
risoluzione sulla misurabilità dello stile, non l'effetto della CAN.

---

### D-019 — Criterio di selezione del checkpoint: FID minimo
**Data:** 2026-08-03, sera · **Stato:** attiva · **Sostituisce:** il criterio
pre-registrato «epoca 100 per tutti»
**Approfondimento:** `experiments/registry.md`, sezione sulla revisione del criterio

Si valutano **tutti** i checkpoint salvati di ogni run, si pubblica la traiettoria
completa, e il numero di sintesi è quello del checkpoint con **FID minimo**.

**Perché il criterio è cambiato.** A 128px `dcgan-seed1` produce immagini di ottima
qualità all'epoca 97 e **collassa all'epoca 98**, con gli artefatti a scacchiera tipici
di `ConvTranspose2d` in divergenza. Il criterio pre-registrato avrebbe imposto di
riportare l'epoca 100, cioè un modello degenerato, mentre otto epoche prima era il
miglior esito del progetto. Il criterio non prevedeva che il collasso potesse arrivare
a fine corsa.

**Perché non è cherry-picking.** Tre condizioni, tutte necessarie e tutte soddisfatte:
la regola è identica per ogni run e per entrambe le condizioni; la traiettoria completa
viene pubblicata; l'adozione è datata e motivata invece che silenziosa.

**Il punto metodologico centrale: si seleziona sul FID, non sull'ambiguità.**
Selezionare sull'ambiguità significherebbe scegliere il punto che favorisce l'ipotesi,
ed è circolare. Il FID è indipendente da ciò che si vuole dimostrare, e semmai
sfavorevole: se fedeltà e ambiguità sono in tensione come atteso, prendere il punto di
fedeltà massima tende a prendere quello di ambiguità **minima**.

**I risultati a 64px restano riportati anche all'epoca 100**, come pre-registrato. Il
confronto fra i due criteri sullo stesso impianto è a sua volta informativo.

---

### D-020 — Criterio di esclusione dei run degenerati: IS < 2,0
**Data:** 2026-08-03, sera · **Stato:** attiva

Un run con **Inception Score inferiore a 2,0** è marcato degenerato ed escluso dalle
medie. Resta in tabella, marcato, e il criterio è stampato sotto ogni riassunto.

**Perché serviva.** Con `can-seed1` (IS 1,12) e `can-seed4` (1,77) a 64px, escludere
«i run che non funzionano» a occhio sarebbe stata selezione mascherata. Serviva una
soglia dichiarata e applicata identicamente alle due condizioni.

**Perché 2,0 e perché l'IS.** L'Inception Score misura **diversità**, e vale 1,0 quando
tutti i campioni sono identici — il minimo assoluto, la firma del mode collapse. I run
sani stanno sopra 4,0. Una soglia a 2,0 separa nettamente le due popolazioni e non
tocca run semplicemente mediocri: `dcgan-seed4`, degradato con FID 203, ha IS 3,04 e
**resta incluso**. È una soglia di diversità minima, non di qualità: escludere sul FID
significherebbe escludere i run che generano peggio, che è cosa diversa dall'escludere
quelli che non generano affatto.

**Il tasso di degenerazione è a sua volta un risultato**, non solo un problema di
igiene: a 64px due run su quattro della CAN degenerano contro uno su quattro della
DCGAN. Il meccanismo di ambiguità rende l'addestramento fragile, e la letteratura sulle
CAN non è generosa su questo punto.

---

### D-021 — Figure di confronto generate alla stessa epoca per tutti i run
**Data:** 2026-08-03, sera · **Stato:** attiva

Le figure di confronto reali/generate si producono con `scripts/figure_confronti.sh`,
che impone **la stessa epoca a tutti i run** di una condizione.

**Motivazione:** figure prodotte da epoche diverse non sono confrontabili fra loro, e
sceglierla run per run — magari quella che rende meglio — sarebbe selezione mascherata
sul materiale visivo, meno visibile di quella sui numeri e altrettanto scorretta.
L'epoca usata va dichiarata nella didascalia.

A 128px si usa l'**epoca 90** e non `final`, perché almeno un run è collassato nelle
ultime epoche (D-019).

**Vincolo concettuale, già in D-016 e qui riaffermato:** il generatore è
incondizionato, quindi un'immagine generata non ha uno stile vero. Nelle figure di
confronto è il **giudice terzo** a smistare i campioni per stile predetto, e la
didascalia deve dire che si tratta di una predizione, non di una proprietà
dell'immagine.

---

### D-022 — Esperimento illustrativo condizionato per stile (E5), esplicitamente fuori da ADR-0003
**Data:** 2026-08-11 · **Stato:** implementato, non ancora eseguito

Su richiesta di Gian, ispirato al condizionamento categorico di ArtGAN (Tan, Chan,
Aguirre & Tanaka) e in particolare al progetto studentesco non ufficiale
`github.com/sebastienmeyer2/image-synthesis-artgan`, la cui galleria di immagini
sembrava visivamente superiore a quanto prodotto finora dall'impianto DCGAN/CAN.

**Obiettivo dichiarato: solo figure piu' convincenti per la tesi, non un confronto
quantitativo.** Prima di implementare e' stata fatta un'obiezione esplicita
sull'idea di "replicare i loro risultati": non pubblicano FID/IS, solo una galleria
curata di immagini scelte, su compiti diversi (volti di politici francesi, WikiArt
per singolo artista o genere, CIFAR-10) — non un termine di paragone omogeneo con
sei stili art-storici. Gian ha confermato che l'obiettivo e' comunque la resa
visiva, non la dimostrazione di un risultato.

**Perche' e' fuori dall'impianto comparativo.** ADR-0003 vale perche' DCGAN e CAN
condividono lo stesso generatore e la stessa backbone del discriminatore, con
un'unica variabile indipendente (la loss). Un generatore condizionato per stile
prende in ingresso anche l'etichetta: e' un'architettura diversa per costruzione,
non una terza condizione dello stesso confronto. Aggiungerlo al registro come "E5"
comparabile a E1/E2 sarebbe stato un errore metodologico.

**Cosa e' stato implementato**, in moduli **separati** che non toccano nulla
dell'impianto D-010 (`networks.py`, `losses.py`, `trainer.py` restano invariati):

- `src/tesi_gan/models/conditional.py` — `ConditionalGenerator` (concatena
  l'etichetta di stile in one-hot al vettore latente) e `ConditionalDiscriminator`
  (testa ausiliaria di classificazione su reali **e** generate, logica AC-GAN).
- `src/tesi_gan/training/conditional_losses.py` — loss dove il generatore e'
  premiato per farsi classificare **come lo stile richiesto**: l'esatto opposto
  della penalita' di ambiguita' della CAN.
- `src/tesi_gan/training/conditional_trainer.py` — `ConditionalTrainer`, ciclo
  separato da `Trainer`, con griglia a rumore ed etichette fisse (una riga per
  stile) per seguire se il condizionamento funziona.
- `src/tesi_gan/evaluation/conditional_figures.py` — unica figura prodotta:
  griglia stile-per-riga, con didascalia che dichiara i limiti (vedi sotto).
- `configs/model/conditional_artgan.yaml`, `configs/experiment/e5-illustrativo-64.yaml`
  e `...-128.yaml` — entrambe le risoluzioni, perche' il budget di calcolo
  disponibile lo permette. Un solo seed: non e' un confronto statistico.
- `tests/test_conditional.py` — verifica che il condizionamento non sia un
  ingresso morto (etichette diverse -> immagini diverse), le forme alle due
  risoluzioni, e che nessuna importazione tocchi le classi di ADR-0003.

**Limite dichiarato, da riportare in tesi se le figure vengono usate:** nessun
numero (FID/IS) e' comparabile con la fonte di ispirazione, che non ne pubblica.
La figura mostra qualita' visiva ottenuta con un'architettura diversa, non un
risultato che confermi o smentisca l'ipotesi della CAN.

**Citazione bloccata.** Il paper di Tan, Chan, Aguirre & Tanaka non e' ancora in
`thesis/references/bibliography.bib` — marcato `% TODO[CITE]` nei file di codice.
Va importato in Zotero prima di qualunque `\parencite` in tesi (CLAUDE.md §2.1).

**Test eseguiti il 2026-08-11 sul Mac locale (venv, non nel sandbox di sviluppo,
dove non e' stato possibile installare `torch` per spazio disco e proxy):
92 test verdi (78 dell'impianto D-010, invariati, + 14 nuovi di
`test_conditional.py`).** Il codice e' verificato su CPU: forme, differenziabilita',
condizionamento non banale (etichette diverse -> immagini diverse), round-trip dei
checkpoint. Resta da fare la prova vera, su GPU con dati reali: i test su dati
sintetici non dicono nulla sulla qualita' visiva o sulla stabilita' del training,
solo che il codice non esplode.

### D-023 — Bozza dell'idea di base e di RQ1: rivendicazione di creatività della CAN come antropomorfizzazione
**Data:** 2026-08-11 · **Stato:** bozza confermata da Gian, da consolidare con la revisione della letteratura (M1)

Emersa da un dialogo aperto (domande una alla volta, risposte verificate contro
fonti reali di volta in volta invece che assunte) — non dalla revisione
sistematica della letteratura, che resta da fare. Registrata qui perché è la prima
risposta concreta a Q8, ferma dal 31/07.

**Il percorso.** Punto di partenza di Gian: l'AI generativa interessa come
strumento per superare lacune tecniche ed esprimere qualcosa attraverso l'arte
visiva, ma la "creatività claim" di alcuni algoritmi non convince. Prima
formulazione: "non c'è creatività, è casualità, soprattutto rifacendosi
all'estetismo simbolico". Verificato che:

1. La letteratura sulla creatività computazionale (Boden, già in bibliografia)
   definisce la creatività **in opposizione** alla pura casualità — un campionamento
   casuale nello spazio latente non garantisce di per sé valore, novità o coerenza.
   La critica di Gian, precisata, non è "è casuale" ma "manca l'emozione/intenzione".
2. "Estetismo simbolico" → **estetica simbolica di Susanne K. Langer** (sviluppa la
   semiotica di Cassirer): un'opera d'arte richiede "illusione artistica" imbevuta
   di emozione per essere arte. Qi (2019) applica questa teoria esattamente al CAN e
   conclude che manca l'input emotivo — non è ancora arte secondo questo criterio.
   Fonte trovata solo dopo una seconda ricerca mirata (il riferimento era in un
   paper scartato come "troppo corto" al primo giro): vedi
   `docs/literature/da-recuperare.md`.
3. Gian: la CAN non può esprimere emozione, l'uso umano dell'arte generativa sì.
   Confermato dalla letteratura su co-creatività uomo-AI: l'agentività è distribuita
   lungo un continuum, l'accoglienza di un'opera dipende dall'intenzione dichiarata
   dall'artista umano, non dallo strumento.
4. Ponte fra parte teorica e impianto sperimentale (che Gian giudica, allo stato
   attuale, "un eccesso di zelo" rispetto a ciò che gli interessa davvero — la
   parte espositiva): l'impianto non serve a stabilire *se* la CAN è creativa
   (già escluso teoricamente), ma a mostrare *come si comporta* un sistema che
   rivendica una creatività che non ha. La testa di stile del discriminatore della
   CAN si autovaluta 0,28 (immagini facilmente attribuibili), il giudice terzo
   indipendente dà 0,75 sugli stessi campioni (`experiments/registry.md`) — la
   stessa divergenza fra creatività rivendicata e creatività misurata che Colton
   (2008, già in bibliografia) descrive in astratto.
5. Gian: rivendicare falsamente creatività è di per sé un problema etico — non un
   filone a parte rispetto al vincolo analitico-etico del corso (Q3), la stessa
   linea di ragionamento. Confermato: la letteratura di etica dell'AI tratta
   l'attribuzione di creatività a un sistema come **antropomorfizzazione**, una
   fallacia che distorce il giudizio morale, con conseguenze concrete documentate
   (svalutazione del lavoro artistico umano, inganno del pubblico).

**La frase, confermata da Gian con una correzione (il dato 0,28 vs 0,75 va tenuto
come preliminare, non come risultato consolidato — mancano ancora verifiche/
esperimenti dedicati):**

> Le CAN rivendicano "creatività" tramite una metrica autoreferenziale (il proprio
> discriminatore) che diverge nettamente da una misura indipendente sugli stessi
> dati (0,28 contro 0,75 a 64px — **dato preliminare**, non ancora confermato da un
> esperimento dedicato); questa rivendicazione non regge nemmeno sul piano teorico,
> perché per l'estetica simbolica di Langer l'arte richiede emozione, che
> l'algoritmo non ha e che semmai risiede nell'uso umano dello strumento;
> etichettare comunque il sistema come "creativo" è un caso di antropomorfizzazione
> che la letteratura di etica dell'AI classifica come fallacia, con conseguenze
> reali su artisti e pubblico.

**Cosa resta aperto, esplicitamente non deciso qui:**

- ~~Il tema dell'accessibilità (AI come strumento per chi ha lacune tecniche, da
  cui Gian era partito) non è ancora ricollegato a questo nucleo~~ — **ricollegato
  da D-024.**
- **La divergenza 0,28 vs 0,75** è preliminare: va capito se serve un esperimento
  dedicato (non solo un sottoprodotto di D-010/D-015) prima di poterla usare come
  risultato in tesi.
- **Rapporto con l'impianto sperimentale esistente (D-010, ADR-0003):** questa
  bozza lo riqualifica da "confronto che stabilisce se la CAN è più/meno fedele"
  a "caso di studio a supporto della critica" — implicazioni su §5 e §7 del
  piano di progetto (metodologia, piano sperimentale) non ancora tratte.
- **Non sostituisce la revisione sistematica della letteratura (M1).** Le fonti
  citate qui sono state trovate e verificate una a una in risposta a affermazioni
  specifiche di Gian, non tramite una ricerca sistematica sullo stato dell'arte.
- **Q8 resta aperta**, ma con una prima direzione difendibile invece che vuota.

---

### D-024 — Accessibilità e training: due tesi che coesistono senza elidersi (completa D-023)
**Data:** 2026-08-11 · **Stato:** confermata da Gian, chiude il punto aperto in D-023 sull'accessibilità

Riprende il punto di partenza di Gian (D-023, primo passo del dialogo): l'AI
generativa come strumento di accessibilità per chi ha lacune tecniche, per
esprimere qualcosa attraverso l'arte visiva. Restava da capire come si collega al
nucleo critico (D-023): se fosse la controparte costruttiva della critica, o se il
fatto che il training "ruba" da altri artisti (V-007) la rimettesse in discussione.

**Obiezione posta e verificata prima di accettare la posizione di Gian.** Prima
formulazione di Gian: il training è paragonabile all'ispirazione umana, perché
anche la creazione umana nasce dall'osservazione di natura, realtà e opere altrui,
e gli stili artistici lo dimostrano. Verificato che questa equiparazione è tra le
più contestate in letteratura — non ci sono solo tesi accademiche discordanti, ci
sono **sentenze di tribunali americani che si contraddicono direttamente** su
questo stesso punto: una motiva un giudizio con l'analogia alla lettura umana
("un LLM allenato su un'opera non per sostituirla, ma per prendere una svolta e
crearne un'altra"), un'altra la respinge esplicitamente ("non è così che un umano
legge un libro" — il testo viene ingerito, spezzettato, ricombinato miliardi di
volte, un processo meccanico senza equivalente nella lettura umana).

**Il criterio che ha sciolto la tensione, proposto da Gian stesso:** la differenza
non sta nella scala né nella tecnica, ma nella **componente emotiva**, sempre
presente nello studio di un artista umano, assente nell'addestramento di un
modello. Coerente con D-023 (l'algoritmo non ha emozione) invece di essere in
tensione con esso: **l'assenza di emozione non riguarda solo l'output della CAN,
riguarda anche il training di qualunque modello generativo**, quindi l'analogia
con l'ispirazione umana perde il fondamento che la renderebbe una difesa valida.
Aggancio trovato in filosofia della mente: il "problema del symbol grounding" —
una semantica puramente relazionale (pesi, gradienti) non produce significato
vissuto, perché non c'è un soggetto per cui l'esperienza conti qualcosa.

**Decisione:** l'accessibilità (l'uso umano dello strumento per esprimersi,
nonostante lacune tecniche) resta un beneficio genuino, **indipendente** dalla
legittimità del processo con cui il modello sottostante è stato addestrato. Le due
valutazioni **coesistono senza elidersi a vicenda**: uno strumento può fare del
bene a chi lo usa e restare, allo stesso tempo, costruito in un modo eticamente
problematico (V-007). La tesi non deve scegliere fra le due, deve tenerle insieme
e distinte.

**Conseguenza per la struttura della tesi:** il capitolo di discussione ha ora due
argomenti distinti da tenere separati esplicitamente, non fusi in uno solo —
altrimenti si rischia di usare il beneficio dell'uno per attenuare il problema
dell'altro, esattamente l'errore che l'obiezione qui sopra ha escluso. Dettaglio di
merito e struttura da definire dopo M1.

---

### D-025 — Due figure aggiuntive per l'esperimento illustrativo E5 (colonna reale + progressione per epoca)
**Data:** 2026-08-12 · **Stato:** implementate, in attesa di verifica coi test da parte di Gian

Su richiesta di Gian, due estensioni a `evaluation/conditional_figures.py`, entrambe
fuori da ADR-0003 come il resto di E5 (D-022):

**1. Colonna reale opzionale in `save_conditional_grid`.** Nuovo parametro
`reference_dataset`: se passato, la prima colonna di ogni riga mostra un'immagine
reale di quello stile accanto ai campioni generati.

- l'immagine reale proviene dallo split di **riferimento** (`data.reference_root`),
  non da quello di training, cosi' l'esemplare mostrato non e' un'immagine che il
  generatore ha gia' visto in addestramento;
- e' **un singolo esemplare scelto a caso** (seed dedicato, `reference_seed`), non
  una media ne' un prototipo statistico dello stile — va dichiarato in didascalia,
  esattamente come per l'assenza di un confronto quantitativo (gia' vincolante da
  D-022);
- retrocompatibile: senza `reference_dataset` (default `None`) la figura resta
  identica a prima;
- `cmd_sample_conditional` in `cli.py` costruisce ora anche il dataset di
  riferimento via `build_reference_dataset` e lo passa alla figura, con
  `assert_same_classes` a guardia di un possibile disallineamento fra le classi dei
  due split.

**2. Nuova funzione `save_progression_grid`** (+ comando
`sample-conditional-progression`): griglia stile × epoca, una riga per stile e una
colonna per checkpoint, costruita dai checkpoint periodici `epoch_NNNN.pt` che
`ConditionalTrainer` gia' scrive ogni `training.checkpoint_every` epoche (10 nei
config e5-illustrativo-*). Non e' la vista automatica gia' loggata su W&B a ogni
epoca (quella resta invariata, non richiedeva codice nuovo): qui l'obiettivo e' una
sola immagine statica che mostri l'evoluzione nel tempo per ciascuno dei sei stili,
affiancati.

- **stesso rumore fisso per tutte le colonne** di una riga: la differenza visibile
  fra una colonna e la successiva e' quindi imputabile solo all'evoluzione dei pesi,
  non a un campione diverso;
- il generatore passato viene **mutato** (i pesi vengono ricaricati a ogni colonna):
  documentato esplicitamente nel docstring perche' e' un comportamento diverso da
  `save_conditional_grid`, che non tocca lo stato del generatore oltre `.eval()`;
- guardie esplicite: rifiuta checkpoint senza flag `"conditional"` o con un numero
  di stili diverso da quello atteso, per non mescolare in una figura epoche di run
  incompatibili tra loro;
- il comando CLI legge `--checkpoint-dir`, ordina i file per numero di epoca dal
  nome (`epoch_NNNN.pt`) e si rifiuta di procedere se non ne trova nessuno —
  `latest.pt`/`final.pt` non bastano perche' non portano il numero di epoca nel
  nome.

Aggiunti 8 test in `tests/test_conditional.py` in totale fra le due figure
(selezione dell'immagine reale deterministica e con stile assente, entrambe le
figure con e senza gli argomenti opzionali, i due casi di rifiuto per checkpoint
incoerenti). Non ancora eseguiti da Gian — nessun numero da questa modifica entra
nell'impianto comparativo, quindi non blocca i run E5/E6 già in corso su RunPod.

---

## 3. Questioni aperte

Ordinate per criticità. Le questioni chiuse restano elencate con il rimando alla
decisione che le ha risolte: cancellarle farebbe perdere la traccia del percorso.

### Q1 — Sessione di laurea ✅ chiusa
**Stato:** risolta il 2026-08-02 · **Verifica:** V-006

Sessione autunnale confermata sull'avviso ufficiale della Scuola di Ingegneria. Le
date amministrative sono gestite da Gian autonomamente, fuori da questo repository,
per scelta esplicita — non vengono più registrate qui.

### Q2 — Impianto sperimentale ✅ chiusa dall'autore
**Stato:** chiusa il 2026-08-03 → **D-010**, [ADR-0003](decisions/0003-impianto-sperimentale.md)

Riaperta e ridiscussa perché la prima chiusura era dell'assistente. I quattro nodi
sollevati nella revisione sono stati sciolti così:

1. **Riaddestramento da zero**, non fine-tuning → D-010, punto 2.
2. **Rischio di risultato nullo** → mitigato restringendo il dominio a pochi stili
   molto distinti → D-011.
3. **Cosa conta come successo** → 🔶 **ancora aperto.** È l'unico nodo non sciolto:
   per costruzione la CAN peggiora il FID, e va deciso *prima* dei run quale esito
   si considera informativo. Da riprendere.
4. **Varianza fra seed** → tre seed per condizione → D-010, punto 3.

### Q3 — Peso relativo tra componente tecnica ed etica 🟠 alta
**Stato:** aperta

Determina quale capitolo porta il contributo principale. Da concordare col relatore,
la cui area include l'informatica etica. L'impianto scelto (D-010) è compatibile con
entrambi gli sbilanciamenti, quindi questa questione non blocca più il lavoro
sperimentale — ma blocca ancora la stesura del capitolo di discussione.

### Q4 — Dataset ✅ chiusa
**Stato:** chiusa il 2026-08-03 → **D-014**, [ADR-0004](decisions/0004-dataset.md)

ArtBench-10, sei stili di pubblico dominio, 30.000 immagini bilanciate. Il criterio
di selezione (pubblico dominio + distanza visiva) è quello fissato in D-011; il
dataset no.

Percorso: WikiArt → misurazione dello sbilanciamento → scoperta di ArtBench →
ArtBench. La strada scartata resta documentata perché il confronto fra i due dataset
è materiale per il capitolo di metodologia.

Sottoinsieme bilanciato di WikiArt. La verifica della licenza resta da fare **prima**
del download, ed è bloccante: lo script di preparazione dei dati si rifiuta di girare
senza il flag `--licenza-verificata`.

### Q5 — Metriche di valutazione 🟡 chiusa nella scelta, aperta nella formulazione
**Stato:** metriche scelte, una formulazione da verificare

Adottate: FID, Inception Score, entropia della posterior di stile, studio percettivo
leggero. Ciascuna è accompagnata dalla dichiarazione esplicita di cosa **non** misura
(vedi la tabella in ADR-0003 e la nota in `src/tesi_gan/evaluation/metrics.py`).

**Resta aperto:** la forma esatta della penalità di ambiguità stilistica in Elgammal
et al. Il codice implementa due varianti — entropia incrociata rispetto all'uniforme
e opposto dell'entropia — che **non sono equivalenti**. Vanno confrontate col paper
originale prima di dichiarare in tesi quale è stata usata.

**Ipotesi attesa, da dichiarare prima di vedere i risultati:** la CAN peggiora il FID
e aumenta l'entropia di stile. Se accade, non è un fallimento ma la dimostrazione
empirica che fedeltà e ambiguità stilistica sono obiettivi in tensione.

**Esito del 2026-08-03 — l'ipotesi è stata FALSIFICATA a metà.** L'ambiguità sale come
previsto (0,682 → 0,750, gruppi non sovrapposti), ma **il FID non peggiora**: 107,7
contro 107,3, indistinguibili. Fedeltà e ambiguità stilistica non risultano in tensione
a questa scala. Un'ipotesi pre-registrata e smentita vale più di una confermata, e va
riportata come tale.

**Seconda previsione smentita:** era stato scritto che l'ambiguità della DCGAN sarebbe
scesa proseguendo l'addestramento. È salita, da 0,601 a 20 epoche a 0,682 a 100. La
lettura: **una GAN incondizionata addestrata su sei stili modella la miscela**, quindi
più impara più produce immagini stilisticamente ibride. L'ambiguità della CAN è una
spinta *ulteriore* sopra quella che una GAN produce già da sola — più sottile e più
difendibile di «la CAN rende ambiguo, la GAN no».

**Metrica aggiunta strada facendo:** la *copertura degli stili*, cioè la distribuzione
marginale delle classi predette. Serve a distinguere la fusione stilistica (marginale
piatta, l'effetto cercato) dal collasso su una zona generica (marginale concentrata),
che l'entropia per immagine da sola non separa. È risultata identica nelle due
condizioni (0,966 contro 0,967), il che **esclude la spiegazione alternativa** con una
misura invece che con un argomento.

**Aggiornamento del 2026-08-03 — lacuna trovata e chiusa.** L'entropia della posterior
di stile era calcolabile **solo sulla CAN**, perché prodotta dalla testa di stile del
discriminatore, che la DCGAN non ha. La metrica su cui si regge il confronto non era
quindi confrontabile: i sei run avrebbero prodotto FID e IS — due metriche che per
costruzione penalizzano la CAN — e nessuna misura dell'effetto cercato. Risolta con
**D-015** (giudice terzo). La vecchia metrica resta come diagnostica interna.

**Esito del 2026-08-04 — impianto 128px (D-018), criterio FID minimo (D-019).**
A questa risoluzione l'ipotesi **non è più falsificata**: FID 183,4 (CAN) contro
117,8 (DCGAN), +55%, con ambiguità che sale di un'entità simile a quella osservata a
64px (+0,089 contro +0,068). A 64px fedeltà e ambiguità non risultavano in tensione;
a 128px lo sono. Il dettaglio non è solo quantitativo: i tre seed CAN raggiungono
tutti il loro FID minimo alla stessa epoca (20 su 100) e poi degradano quasi
monotonicamente, mentre i tre DCGAN raggiungono il minimo fra le epoche 80 e 100.
Non è uno squilibrio del criterio di selezione — la regola è identica per entrambe
le condizioni (D-019) — è la traiettoria stessa del CAN a esaurirsi presto. Dettagli
e tabella completa in `experiments/registry.md`, sezione «Impianto 128px».
**Resta da stabilire se questo sia lo stesso tipo di instabilità del mode collapse
già visto a 64px o un fenomeno diverso**: vedi V-008.

### Q6 — Studio percettivo con soggetti umani 🔶 riaperta
**Stato:** **di nuovo aperta dal 2026-08-03** · **Proposta:** D-012

Sì, versione leggera con campione di convenienza. Limiti da dichiarare senza
attenuanti.

### Q7 — Servizio di calcolo e budget ✅ chiusa
**Stato:** chiusa il 2026-08-03 → **D-013**

RunPod con RTX 4090. Dimensionamento: 64×64, sei run (due condizioni × tre seed) da
circa 100 epoche su un sottoinsieme di alcune migliaia di immagini. Ore consumate e
costo effettivo vanno annotati qui man mano, per l'appendice sulla riproducibilità.

### Q8 — Domande di ricerca 🟡 bozza formulata, da consolidare
**Stato:** aperta, con una prima direzione → **D-023**, completata da **D-024**

Prima bozza: la rivendicazione di creatività della CAN come antropomorfizzazione
(D-023), con l'accessibilità riconosciuta come beneficio indipendente dalla
legittimità del training (D-024) — due argomenti da tenere distinti nel capitolo
di discussione, non fusi. Emersa da dialogo aperto, non dalla revisione
sistematica della letteratura — resta subordinata a quella (M1): formulare domande
di ricerca prima di conoscere lo stato dell'arte produce quasi sempre domande già
risolte o mal poste, e questa bozza va trattata come tale finché la revisione non
la conferma o la corregge.

**Vincolo:** la domanda di laurea richiede il titolo della tesi in una delle prime
fasi amministrative (gestite da Gian, non tracciate qui). Un titolo si può cambiare,
ma sceglierlo senza avere almeno una domanda di ricerca abbozzata significa
sceglierlo a caso.

Direzione compatibile con D-010, da affinare dopo la revisione:
*che cosa misura effettivamente il meccanismo di ambiguità stilistica di una CAN, e
in che rapporto sta con le metriche con cui la letteratura ne valuta il risultato.*

---

## 4. Verifiche da fare

Punti su cui è stata fatta un'ipotesi o un adattamento che va confermato da una fonte
autorevole prima della consegna.

### V-006 — Scadenze della sessione autunnale ✅ verificata

Fonte ufficiale della Scuola di Ingegneria consultata. Il calendario e le singole
scadenze sono gestiti da Gian autonomamente e **non vengono più tracciati in questo
repository**, per scelta esplicita.

**Unica dipendenza rilevante per il progetto:** una delle prime fasi amministrative
richiede il nominativo del relatore, tuttora `DA DEFINIRE` (§1), che deve poi dare
un'approvazione. Questo, non il training, è il rischio principale del progetto:
nessun risultato sperimentale compensa una domanda non presentata.

### V-007 — Termini d'uso del dataset 🟠 in parte chiarita
**Stato:** ricognizione fatta il 2026-08-03; resta la lettura diretta dei termini
**Riferimento:** [ADR-0004](decisions/0004-dataset.md)

**Ricognizione del 2026-08-03.** Tre fonti autorevoli danno tre qualificazioni
giuridiche diverse a materiale in larga parte sovrapposto:

| Fonte | Dichiarazione |
|---|---|
| **ArtBench-10** (dataset scelto) | «Fair Use license» |
| WikiArt refined ([cs-chan/ArtGAN](https://github.com/cs-chan/ArtGAN/blob/master/WikiArt%20Dataset/README.md)) | «can be used only for non-commercial research purpose» + ToU di WikiArt.org |
| [`huggan/wikiart`](https://huggingface.co/datasets/huggan/wikiart) | `license: unknown`, «Data files © Original Authors» |

**Il punto da capire su ArtBench:** *fair use* è un'eccezione del diritto d'autore
statunitense valutata caso per caso, **non un permesso concesso da un titolare**.
Gli autori stanno affermando una posizione giuridica, non trasmettendo una licenza.
Non è un difetto da nascondere: è l'esempio migliore che la tesi possa avere per
mostrare su che fondamenta poggia la ricerca in creatività computazionale.

**L'osservazione strutturale**, da riportare in tesi: i dataset con licenza limpida
(Met, Rijksmuseum, CC0) non hanno etichette di stile art-storico; quelli con le
etichette non hanno licenza limpida. Non è una coincidenza.

**Mitigazione già applicata:** i sei stili scelti in D-014 sono tutti di pubblico
dominio, il che riduce molto l'esposizione a prescindere da come si qualifichi la
licenza del dataset.

---

### Lettura diretta delle fonti — 2026-08-03

Testo verificato alla fonte, non parafrasato. Restano da **valutare**, non più da
reperire: la responsabilità della dichiarazione è di Gian.

**1. `LICENSE` del repository ArtBench** ([liaopeiyuan/artbench](https://github.com/liaopeiyuan/artbench/blob/main/LICENSE)), testualmente:

> The data sources of ArtBench-10 is released under a Fair Use license, as requested
> by WikiArt, Ukiyo-e.org database and The Surrealism Website. […] Other artifacts
> are released under a MIT license.

Quindi: **codice MIT, immagini «fair use»**, con rinvio a tre fonti a monte.

**2. WikiArt, *Terms and conditions*** (ultimo aggiornamento 5 ottobre 2016), sezione
*Copyright Policy*. WikiArt dichiara di ospitare sia opere di pubblico dominio sia
opere protette, e che **le seconde** sono esposte in base al principio di fair use in
quanto storicamente significative, usate a fini informativi ed educativi, già
ampiamente disponibili in rete e in copie a bassa risoluzione inadatte all'uso
commerciale.

Tre osservazioni che contano:

- La distinzione è esplicita fra **opere di pubblico dominio** e **opere protette**:
  il fair use è invocato solo per le seconde. I sei stili di D-014 ricadono nelle
  prime.
- I termini regolano l'uso **del sito** («the Service»), non la costituzione di
  dataset né l'addestramento di modelli. Non autorizzano e non vietano: **non
  prevedono il caso**.
- Legge applicabile dichiarata: **Ucraina**. Non è un dettaglio da ignorare quando si
  ragiona di eccezioni al diritto d'autore.

**3. Ukiyo-e.org, pagina *About*.** Non contiene alcuna clausola di licenza: descrive
un database aggregato da oltre 24 istituzioni (musei, università, biblioteche, case
d'asta). I termini effettivi sono quindi **quelli delle singole istituzioni a monte**,
non del sito aggregatore. Chi volesse risalire deve passare da `ukiyo-e.org/sources`.

**4. The Surrealism Website.** Non consultata, e **irrilevante**: il Surrealismo è
l'unico dei dieci stili di ArtBench escluso da D-014, ed è anche l'unico ancora sotto
copyright. La fonte più problematica delle tre non tocca il sottoinsieme scelto.

### Cosa cambia rispetto a stamattina

Il quadro è più solido di quanto la sola dicitura «fair use» lasciasse pensare:

- la catena delle dichiarazioni è ora **tracciata fino alla fonte primaria** e
  citabile in tesi con testo verificato;
- l'unica fonte con un problema di copyright conclamato riguarda uno stile escluso;
- WikiArt distingue esplicitamente pubblico dominio e opere protette, e il
  sottoinsieme scelto sta dalla parte non problematica.

### Cosa resta aperto, e non è un cavillo

**«Fair use» è dottrina statunitense.** Gian scrive una tesi in Italia. La
qualificazione rilevante nell'ordinamento europeo è un'altra, e va verificata con una
fonte competente — quanto segue è **informazione, non consulenza legale**:

- **Direttiva UE 2019/790, art. 3** — eccezione per il *text and data mining* a fini
  di **ricerca scientifica** da parte di organismi di ricerca. È la disposizione che
  più direttamente riguarda una tesi universitaria, e non prevede opt-out del titolare
  (a differenza dell'art. 4, di portata generale).
- **Direttiva UE 2019/790, art. 14** — le riproduzioni di opere d'arte visiva il cui
  termine di protezione è scaduto non sono a loro volta protette, salvo originalità
  propria. Toglie l'obiezione «la fotografia del quadro è comunque protetta».
- **Codice dei beni culturali, artt. 107-108** — canoni per la riproduzione di beni
  culturali italiani. Peculiarità nazionale molto discussa: per questa tesi è
  materiale di merito, non un ostacolo.

**Verifica suggerita:** una domanda al relatore, la cui area include l'informatica
etica, o all'ufficio competente dell'ateneo. Un paragrafo di tesi che cita la
direttiva e distingue fair use da eccezione TDM vale più di uno che dice «licenza
fair use» e passa oltre.

**Uso previsto da dichiarare:** addestramento di modelli generativi a fini di ricerca
accademica, **senza ridistribuzione** né delle immagini né dei pesi, su un
sottoinsieme di sole opere di pubblico dominio.

Due elementi giuridici da approfondire, **non sono consulenza legale** e vanno
verificati con una fonte competente:

- **Direttiva UE 2019/790, art. 14:** le riproduzioni di opere d'arte visiva il cui
  termine di protezione è scaduto non sono a loro volta protette, salvo originalità
  propria. Rileva perché il criterio di D-011 seleziona già solo opere di pubblico
  dominio.
- **Codice dei beni culturali italiano, artt. 107-108:** prevede canoni per la
  riproduzione di beni culturali italiani. È una peculiarità nazionale molto
  discussa e, per una tesi italiana su IA ed etica dell'arte, materiale di merito
  più che un ostacolo.

Il blocco operativo resta: `python -m tesi_gan.data.download` non gira senza
`--licenza-verificata`. Non è invece bloccato
`python -m tesi_gan.data.inventory`, che scarica i soli indici CSV e nessuna
immagine: contare non è riprodurre.

`python -m tesi_gan.data.download` **si rifiuta di girare** finché non si passa
`--licenza-verificata`. Il blocco è deliberato. Esito negativo → si ripiega su The
Met Open Access con etichette derivate da *culture* o *period*.

Questa verifica non la può fare un assistente: richiede di leggere i termini alla
fonte e di assumersene la responsabilità.

### V-008 — L'espressionismo non è integralmente in pubblico dominio 🟠
**Stato:** aperta, aperta consapevolmente il 2026-08-03 · **Origine:** D-017

D-014 aveva selezionato gli stili anche in base al criterio che fossero **tutti di
pubblico dominio**, e quella è oggi la mitigazione principale rispetto a V-007.
D-017 introduce `expressionism`, che nell'analisi dei dieci stili di ArtBench era
classificato «in gran parte sì», **non** «sì».

È primo Novecento: Munch (†1944) e Kandinsky (†1944) sono liberi, ma Nolde (†1956)
e altri espressionisti ricadono ancora nei settant'anni di protezione. Il dataset li
include sulla base della stessa posizione di *fair use* dichiarata dalla fonte.

**Scelta consapevole**, non svista: la distanza visiva dell'espressionismo è ciò che
serve alla metrica, e l'alternativa pienamente in pubblico dominio
(`post_impressionism`) avrebbe ricreato il problema di sovrapposizione che D-017
esiste per risolvere.

**Da fare:** dichiararlo esplicitamente in tesi, dove si descrive il dataset e dove
si discutono le implicazioni etiche. Scrivere «tutti gli stili sono di pubblico
dominio» sarebbe ora **falso**, e la formula va corretta ovunque compaia. Cinque
stili su sei lo sono; il sesto è incluso con la stessa qualificazione giuridica che
la tesi analizza criticamente — il che, dichiarato, è materiale di merito più che un
difetto.

### V-009 — Natura del degrado del CAN dopo l'epoca 20 a 128px 🟠
**Stato:** aperta, emersa il 2026-08-04 · **Origine:** impianto 128px, `experiments/registry.md`

I tre seed CAN a 128px toccano il FID minimo tutti all'epoca 20 e poi degradano
quasi monotonicamente fino a fine training (dettagli e tabella in
`experiments/registry.md`, sezione «Impianto 128px»). La copertura degli stili non
crolla come nel mode collapse già documentato a 64px (`can-seed1`, copertura 0,190):
qui resta nell'intervallo 0,6-0,9, quindi non è chiaramente lo stesso fenomeno.

**Da fare prima di scrivere il risultato in tesi:** ispezionare visivamente i
campioni salvati (o quelli su W&B) dei tre seed CAN a epoca 20 e a epoca 100, per
stabilire se il degrado è mode collapse su un sottoinsieme ristretto di output,
artefatti tipo checkerboard (come `dcgan-seed1`, D-019), o un peggioramento diffuso
della qualità senza una firma riconoscibile. La caratterizzazione cambia cosa si può
affermare: «il CAN collassa a 128px» è una frase diversa da «il CAN degrada
progressivamente a 128px», e solo l'ispezione visiva permette di scegliere quella
corretta.

**Perché conta.** Se confermato, è il contrasto più forte con l'impianto a 64px
(dove il vantaggio di ambiguità del CAN non costava nulla in fedeltà) e il
candidato più solido per il capitolo di discussione: l'instabilità del meccanismo
di ambiguità sembra scalare con la risoluzione.

### V-010 — L'ablazione E6 (peso ambiguità zero) non replica i numeri di DCGAN 🟠
**Stato:** aperta, emersa il 2026-08-12 · **Origine:** `experiments/registry.md`,
sezione «Ablazione di controllo (E6)»

Il config `e6-ablazione-can-peso-zero.yaml` dichiara: se FID/IS del run risultassero
sistematicamente diversi da `e1-dcgan-baseline seed=1`, sarebbe un bug
nell'implementazione condivisa. Il run (seed=1, epoca 100) da':

- FID 91,7 — sotto tutti e tre i seed DCGAN a 64px (102,3–114,1);
- IS 4,10 ± 0,20 — indistinguibile dalla media DCGAN (4,11 ± 0,27);
- ambiguità (giudice terzo) 0,652 — sotto il minimo dei tre seed DCGAN (0,673).

Non è mode collapse (copertura 0,991) né un run degenerato (IS ben sopra soglia
D-020). **Non sembra un bug di implementazione**: più probabile un'ipotesi
strutturale. La CAN, anche a peso di ambiguità zero, mantiene nel discriminatore una
testa di classificazione stilistica addestrata sulle immagini reali — quella parte
della loss non dipende da `style_ambiguity_weight`, che pesa solo il termine
sul generatore (`training/losses.py`). ADR-0003 dichiara che DCGAN e CAN
«differiscono solo per `style_head: bool`»: è tecnicamente vero (stesso backbone),
ma la *presenza* della testa di stile nel discriminatore — non il suo peso nella
loss del generatore — resta una differenza architetturale rispetto a DCGAN, e questo
run suggerisce che possa comportarsi da compito ausiliario regolarizzante,
cambiando la dinamica avversaria anche quando il generatore non riceve mai il
segnale di ambiguità.

**Da fare prima di scrivere qualunque cosa in tesi su questo:**

1. Un solo seed non distingue «effetto reale della testa ausiliaria» da «varianza
   fra run»: il range dei tre seed DCGAN (102,3–114,1 di FID) è già ampio quanto la
   differenza osservata. Servirebbe la stessa ripetizione a più seed già fatta per
   E1/E2 prima di trarre conclusioni.
2. Un'ablazione più fine isolerebbe la causa: testa di stile presente nel
   discriminatore ma NON addestrata (nessun gradiente dalla CE sui reali),
   confrontata con questa (testa presente e addestrata, weight=0 solo sul
   generatore).
3. Ispezione visiva dei campioni, come già richiesto per V-009.

**Perché conta.** Il confronto principale E1/E2 resta valido come esperimento (ogni
condizione è consistente con se stessa, e il confronto è comunque DCGAN-senza-testa
contro CAN-con-testa-e-peso-pieno, esattamente ciò che ADR-0003 dichiara di
misurare). Quello che questo run mette in discussione è una lettura più fine:
D-010/ADR-0003 descrivono la differenza fra le due condizioni come «un solo termine
di loss» (il peso di ambiguità). Questo risultato suggerisce che una parte
dell'effetto osservato in E1/E2 — FID comparabile, ambiguità più alta nella CAN —
potrebbe derivare dalla *presenza* della testa di classificazione nel discriminatore
in sé, non (solo) dal termine di ambiguità che agisce sul generatore. Se confermato
con più seed, è materiale per la sezione sui limiti metodologici: non toglie valore
al risultato principale, ma va dichiarato che «un solo termine di loss» è una
semplificazione della differenza architetturale reale fra le due condizioni.

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

**Anomalia ricorrente:** nella cartella `.git` compaiono file di lock (`HEAD.lock`,
`index.lock`) che bloccano i commit finché non vengono eliminati:

```bash
cd "/Users/gian/Documents/Tesi Gian" && rm -f .git/HEAD.lock .git/index.lock
```

Si è ripresentata il 2026-08-03, insieme alla comparsa di un ADR-0005 duplicato
(`0005-giudice-stile.md`, poi eliminato) scritto nello stesso minuto di quello
prodotto in sessione. **Ipotesi:** due sessioni assistite aperte contemporaneamente
sulla stessa cartella. Conviene tenerne aperta una sola per volta.

**Ambiente Python:** virtualenv in `.venv/` (ignorato da git). Prima di qualsiasi
comando: `source .venv/bin/activate`.

---

## 5-quinquies. Punto di ripresa — 2026-08-12

**Sostituisce 5-quater** (lasciato sotto per la cronologia).

### Stato dell'intera parte sperimentale, in un colpo d'occhio

| Traccia | Stato |
|---|---|
| Impianto comparativo D-010 a 64px (E1/E2) | ✅ completo — 8 run, a registro |
| Impianto comparativo D-010 a 128px (E1b/E2b) | ✅ completo — 6 run, V-009 aperta |
| E5 — illustrativo condizionato per stile (D-022) | ✅ **train-conditional a 64px concluso**, valutato; 128px non ancora lanciato |
| E6 — ablazione di controllo (peso ambiguità = 0) | ✅ **eseguito e valutato** (seed 1, 64px) — risultato sorprendente, V-010 aperta |
| E7 — studio percettivo leggero | ⬜ non eseguito |

### Cosa è successo in questa sessione (2026-08-12)

1. **Risolto un conflitto di merge** in `registro-decisioni.md` dopo che una
   sessione parallela (D-023, D-024 sul nucleo teorico della tesi) aveva pushato
   mentre questa sessione lavorava in locale. Merge fatto a mano, entrambe le
   parti preservate. Push riuscito (`6f83c92`).
2. **Lanciati E5-64 ed E6 su RunPod.** Dataset già pronto su `/workspace/tesi-gian`
   da una sessione precedente (4 agosto) — trovato dopo un giro a vuoto perché il
   pod era clonato in `/tesi-gian`, non su `/workspace`.
3. **Bug di percorso trovato e corretto in `e6-ablazione-can-peso-zero.yaml`**:
   senza override esplicito di `paths.checkpoints`, l'ablazione scriveva nella
   stessa cartella di `can-64-seed1` (E2 reale) — verificato che l'E2 originale
   sul volume non è stato toccato (i due run erano su filesystem diversi), ma il
   bug era reale e ora è corretto per sempre.
4. **Backup su `/workspace`**: i checkpoint di E5/E6, nati sul filesystem effimero
   del container (`/tesi-gian`), sono stati copiati sul Network Volume prima che
   andassero persi con la distruzione del pod.
5. **E6 valutato — risultato che apre V-010.** Il run non replica i numeri di
   DCGAN come il config si aspettava di dover verificare: FID 91,7 (sotto tutti e
   tre i seed DCGAN, 102,3–114,1), IS comparabile (4,10 vs 4,11), ambiguità 0,652
   (sotto il minimo DCGAN, 0,673). Non è un bug né mode collapse. Ipotesi aperta:
   la testa di classificazione di stile nel discriminatore, addestrata sui reali
   indipendentemente dal peso di ambiguità sul generatore, potrebbe già avere un
   effetto regolarizzante da sola. Serve più di un seed prima di scrivere
   qualunque cosa in tesi — vedi V-010 per il dettaglio completo.
6. **Due nuove figure per E5** su richiesta di Gian:
   `save_conditional_grid` accetta ora una colonna reale opzionale (un esemplare
   dallo split di riferimento accanto ai generati); nuova funzione
   `save_progression_grid` + comando `sample-conditional-progression` per una
   griglia stile × epoca dai checkpoint periodici. D-025. **Non ancora pushato.**
7. Task ancora aperto: generare le due figure di E5-64 con i comandi CLI (non
   ancora lanciati), poi lanciare E5-128.

### Il prossimo comando, letteralmente il primo da lanciare

Sul Mac, prima di tutto: pushare il lavoro di D-025 (colonna reale + progressione),
la correzione del bug di E6, e questo aggiornamento al registro — vedi il messaggio
di chat per i comandi esatti (`git add -A && git commit && git push`).

Sul pod, dopo il pull: generare le figure di E5-64 (`sample-conditional`,
`sample-conditional-progression`) e poi lanciare
`train-conditional experiment=e5-illustrativo-128` — vedi il messaggio di chat per
i comandi con i percorsi dati già verificati in questa sessione
(`/workspace/tesi-gian/data/processed_128`, ecc.).

### Cosa NON è ancora deciso, in ordine di peso

1. **V-010** — se l'ablazione a peso zero non replica DCGAN per varianza fra seed
   o per un effetto reale della testa di stile. Richiede più seed o
   un'ablazione più fine, non ancora pianificata.
2. **V-009** — natura del degrado del CAN a 128px dopo l'epoca 20: ispezione
   visiva mai fatta.
3. **Q2, punto 3** — cosa conta come esito "informativo" per D-010. Mai chiuso.
4. **Q8**, le domande di ricerca — resta in sospeso su richiesta di Gian.
5. Relatore, titolo, questioni amministrative — fuori dal perimetro di queste
   sessioni per esplicita richiesta di Gian.

---

## 5-quater. Punto di ripresa — 2026-08-11

**Sostituisce i punti di ripresa precedenti** (5-ter, 5-bis, lasciati sotto per la
cronologia). Se apri una chat nuova su questo progetto e hai solo l'accesso
sincronizzato da GitHub (nessuna cartella locale collegata), **leggi prima questa
sezione** — vedi anche la nota in cima a `CLAUDE.md`.

### Stato dell'intera parte sperimentale, in un colpo d'occhio

| Traccia | Stato |
|---|---|
| Impianto comparativo D-010 a 64px (E1/E2) | ✅ completo — 8 run, risultati a registro, ambiguità confermata (0,682→0,750), FID indistinguibile |
| Impianto comparativo D-010 a 128px (E1b/E2b) | ✅ completo — 6 run, FID CAN +55%, causa non confermata (V-009 aperta) |
| E6 — ablazione di controllo (peso ambiguità = 0) | ⬜ **non eseguito** — prossimo esperimento comparativo in coda, config pronta |
| E7 — studio percettivo leggero | ⬜ non eseguito |
| E5 — illustrativo condizionato per stile (D-022, fuori da ADR-0003) | codice scritto **e testato** (92 test verdi, 2026-08-11), **nessun run lanciato** |

### Cosa è successo in questa sessione (2026-08-11)

1. **Corretta una falsa partenza.** A inizio sessione ho letto lo stato del
   progetto da una fetch del repo GitHub che si è rivelata ferma al primo commit
   (31 luglio), mentre il repo vero era già a metà agosto. Non era un problema dei
   documenti — erano già ottimi — ma di una lettura stale. Aggiunta nota in
   `CLAUDE.md` §1 per non ripetere l'errore: chi ha solo l'accesso sincronizzato
   deve diffidare di una fetch che sembra ferma e controllare `git log -1`.
2. **`project-plan.md` riallineato**: era rimasto indietro rispetto al registro
   (diceva ancora "E1/E2 non avviato" quando erano già conclusi da una settimana).
   Ora riflette impianto 64px e 128px conclusi, D-015→D-021 nell'indice.
3. **Deciso e implementato E5** (D-022): generatore condizionato per stile,
   ispirato al condizionamento categorico di ArtGAN, **esplicitamente fuori** dal
   confronto comparativo — solo per ottenere figure più nitide, nessuna pretesa
   quantitativa. Codice in moduli separati che non toccano l'impianto D-010:
   `models/conditional.py`, `training/conditional_{losses,trainer}.py`,
   `evaluation/conditional_figures.py`, config `e5-illustrativo-{64,128}.yaml`.
4. **Testato**: 92 test verdi sul Mac locale (i 78 di D-010, invariati, più 14
   nuovi). Verificato solo su CPU e dati sintetici: non dice nulla sulla qualità
   visiva o la stabilità del training vero.
5. Due commit pushati: `3dc124f` (allineamento documenti) e `1602d88` (E5).

### Il prossimo comando, letteralmente il primo da lanciare

Nessun run di E5 è partito. Sul pod RunPod:

```bash
cd /workspace/tesi-gian && git pull
bash scripts/bootstrap_remote.sh        # solo se e' un pod nuovo
python -m tesi_gan.cli train-conditional experiment=e5-illustrativo-64
# poi, se il primo va bene:
python -m tesi_gan.cli train-conditional experiment=e5-illustrativo-128
```

Dopo E5 (o anche prima/in parallelo, non c'e' una dipendenza tecnica fra i due),
il prossimo esperimento pianificato è **E6**, l'ablazione di controllo:
`style_ambiguity_weight=0` deve far degenerare la CAN esattamente nella DCGAN.
Config pronta: `configs/experiment/e6-ablazione-can-peso-zero.yaml` (override di
`can` con `model.style_ambiguity_weight: 0.0`, per il resto identica a
`e2-can-confronto`).

```bash
python -m tesi_gan.cli train experiment=e6-ablazione-can-peso-zero
```

**Nota sulla numerazione (2026-08-11):** l'ablazione era chiamata "E3" nel piano,
ma quel nome era già preso da `e3-dcgan-128.yaml` (128px). Rinominata **E6** per
coincidere col nome del file di config. Lo studio percettivo, non ancora
implementato, è **E7**. Vedi `docs/project-plan.md` §7 per la tabella corretta.

### Cosa NON è ancora deciso, in ordine di peso

1. Se dopo il run E5 mostrerà risultati visivamente validi o servirà tuning
   (`classification_weight`, epoche, batch) — nessun run reale eseguito finora.
2. **Q2, punto 3** — cosa conta come esito "informativo" per D-010, dato che la
   CAN tende strutturalmente a peggiorare il FID. Mai chiuso.
3. **V-009** — natura del degrado del CAN a 128px dopo l'epoca 20: serve
   ispezione visiva dei campioni, mai fatta.
4. **Q8, le domande di ricerca** — lasciate esplicitamente in sospeso su
   richiesta di Gian in questa sessione. Non toccarle finché non lo chiede lui.
5. Relatore, titolo della tesi, questioni amministrative — **fuori dal perimetro
   di queste sessioni per esplicita richiesta di Gian**: non vanno sollevate né
   usate per stabilire urgenza. Sono affari suoi.

---

## 5-ter. Punto di ripresa — 2026-08-04

Sostituisce i punti di ripresa precedenti.

### Stato

| | |
|---|---|
| Impianto a 64px | **completo**: 8 run, valutati, a registro con `run_id` |
| Risultato principale a 64px | ambiguità 0,682 → 0,750 senza variazione di FID, IS o copertura |
| Impianto a 128px | **6 run completati, traiettoria valutata**: FID 183,4 (CAN) vs 117,8 (DCGAN), +55% — vedi V-009 |
| Giudice | tre iterazioni documentate in `experiments/giudice-stile.md` (J1, J2 a 64px; J3 a 128px) |
| Figure | prodotte per `dcgan-128-seed1` all'epoca 90 |
| Test | 78 superati, invariante di ADR-0003 verificato a 64 e 128 |
| Volume | ampliato a 60 GB dopo il riempimento a metà impianto |

### Il prossimo comando, letteralmente il primo da lanciare

Il commit di questa sessione (registro esperimenti 128px + apertura V-009) è
**bloccato**: `.git/index.lock` non si rimuove da sessione assistita remota
("Operation not permitted" anche da proprietario del file — variante nuova
dell'anomalia già nota in §5). Le modifiche sono su disco (staging fatto), manca
solo il commit. Sul Mac, in locale:

```bash
cd "/Users/gian/Documents/Tesi Gian"
rm -f .git/index.lock .git/HEAD.lock
git status   # tre file già in staging: registro-decisioni.md, registry.md, traiettoria-128px.png
git commit -m "docs: impianto 128px a registro, apre V-009 sul degrado del CAN dopo l'epoca 20"
```

### Cosa è successo in questa sessione (2026-08-04, sera)

I 66 JSON di `experiments/traiettoria-128/` sono stati recuperati dal pod RunPod
via `runpodctl send`/`receive` e analizzati con `traiettoria.py`/`sintesi.py`.
Risultato: i **tre seed CAN toccano il FID minimo tutti all'epoca 20** (171-201) e
degradano quasi monotonicamente fino a fine corsa (FID 268-306 a epoca 100); i tre
DCGAN toccano il minimo fra le epoche 80 e 100. Confronto fra condizioni:
FID 183,4 (CAN) contro 117,8 (DCGAN), +55% — a differenza di 64px, dove la stessa
ipotesi era stata falsificata (FID indistinguibile). Tabella completa e
osservazione in `experiments/registry.md`, sezione «Impianto 128px». Aperta
**V-009**: non è chiaro se il degrado del CAN sia lo stesso mode collapse già
visto a 64px (`can-seed1`, copertura crollata a 0,190) — qui la copertura non
crolla in modo pulito — o un fenomeno diverso. Serve ispezione visiva dei campioni.

**Incoerenza trovata, da correggere prima di generare altre figure:** D-021 fissa
l'epoca 90 per le figure di confronto reali/generate a 128px (decisa per il
collasso tardivo di `dcgan-seed1`), ma quella decisione precede la scoperta che il
CAN tocca il suo picco all'epoca 20. Usare l'epoca 90 per il CAN mostrerebbe
campioni già degradati mentre per il DCGAN è vicina all'ottimo — un'asimmetria non
decisa deliberatamente. Da risolvere: epoca del FID minimo per condizione (stessa
regola di D-019) oppure striscia multi-epoca che renda visibile il degrado.

### I prossimi comandi, dopo lo sblocco di git

```bash
cd /workspace/tesi-gian && git pull

# ispezione visiva V-009: campioni CAN a epoca 20 vs epoca 100, tre seed —
# guardare quelli salvati su disco o su W&B, non rigenerarli dai checkpoint
# se già presenti

# quando risolta l'incoerenza sull'epoca delle figure (vedi sopra):
# CONDIZIONI=can RES=128 EPOCA=0020 bash scripts/figure_confronti.sh
```

### Strumenti disponibili

| Script | A cosa serve |
|---|---|
| `run_impianto.sh` | i sei run; `RES=64\|128`; salta quelli già conclusi |
| `valuta_impianto.sh` | valuta i soli `final.pt` |
| `valuta_traiettoria.sh` | valuta **tutti** i checkpoint |
| `sintesi.py` | riassunto compatto + grafico delle traiettorie |
| `figure_confronti.sh` | confronto reali/generate per tutti i run |
| `raccogli_run_id.py` | recupera gli identificativi W&B per il registro |
| `migra_percorsi_64.sh` | migrazione una tantum dei percorsi (già eseguita) |

### Avvertenze operative apprese

- **Il terminale web di RunPod cade spesso.** Ogni comando lungo va lanciato con
  `nohup ... > log 2>&1 &`. `nohup` restituisce subito il prompt: sembra che il
  comando sia terminato, ma sta girando in background.
- **Ogni pod nuovo richiede** `bootstrap_remote.sh`, `pip install -e ".[dev]"
  "torchmetrics[image]"` e la ricopia dei dati in `/dev/shm`. Solo il volume
  sopravvive.
- **`WANDB_API_KEY` non sta sul volume:** va nella configurazione del pod, o
  riesportata a ogni terminale.
- **Leggere i dati da `/dev/shm` invece che dal volume** porta un'epoca da 44 a 3,6
  secondi a 64px. Non è un'ottimizzazione facoltativa.
- **`rm -rf` su cartelle di `data/` cancella i `.gitkeep` tracciati** e sporca il
  working tree, bloccando i training. Si ripristina con `git restore`.
- **Il fabbisogno di disco va ricalcolato al cambio di risoluzione:** a 128px un
  checkpoint pesa ~290 MB contro ~80 MB, e i sei run passano da 11 a 22 GB.

### Avvertenze operative apprese oggi

- **Il terminale web di RunPod cade spesso.** Ogni comando lungo va lanciato con
  `nohup ... > log 2>&1 &`, altrimenti la disconnessione uccide il processo. In
  alternativa `tmux`, che conserva anche le barre di avanzamento.
- **Il riavvio del pod non è garantito** su questo tipo di macchina: se la GPU è stata
  presa, si crea un pod nuovo agganciando lo stesso volume e si rifà solo il
  bootstrap.
- **Le variabili d'ambiente non stanno sul volume.** `WANDB_API_KEY` va reimpostata a
  ogni pod nuovo, e `export` va rifatto a ogni terminale nuovo.
- **`/dev/shm` si svuota** allo spegnimento: i dati vanno ricopiati, e lo script lo fa
  da solo verificando il conteggio dei file.

### Decisioni ancora aperte

1. **Se rifare l'impianto a 128.** Dipende dal tempo per epoca, ancora da misurare.
2. **Criterio di esclusione dei run degenerati.** Serve una soglia dichiarata e
   applicata identicamente alle due condizioni: il candidato è Inception Score < 2,0,
   che cattura `can-seed1` (1,12) e `can-seed4` (1,77) senza toccare `dcgan-seed4`
   (3,04). Escludere a occhio i run che disturbano sarebbe selezione mascherata.
3. **Q8, le domande di ricerca.** Restano non formulate, ed è la cosa che dovrebbe
   stare a monte di tutto il resto: determina quali risultati servono e quante
   repliche.
4. **V-008**, l'espressionismo non integralmente di pubblico dominio.
5. **V-009**, natura del degrado del CAN dopo l'epoca 20 a 128px — richiede ispezione
   visiva dei campioni prima di poter scrivere il risultato in tesi.
6. **Epoca delle figure di confronto CAN a 128px.** D-021 fissa l'epoca 90 per
   l'intero impianto 128px, ma il CAN tocca il suo picco all'epoca 20: da
   ridecidere prima di lanciare `figure_confronti.sh` sul CAN, altrimenti le
   figure mostrano il CAN già degradato accanto a un DCGAN vicino al suo ottimo.

---

## 5-bis. Punto di ripresa — 2026-08-03, sessione interrotta

Stato esatto al momento dell'interruzione, per non doverlo ricostruire a memoria.

### Pronto e verificato

| Componente | Stato |
|---|---|
| Pod RunPod | `tesi-gan`, RTX 4090, EU-RO-1, Network Volume `tesi-gan` 30 GB su `/workspace` — **fermato** |
| Repository sul pod | `/workspace/tesi-gian`, allineato a `f19e368` |
| Dataset | `data/processed` 30.000 img · `data/processed_test` 6.000 · sei stili · 64px |
| Giudice di stile | `experiments/style_judge/` — J2, accuratezza 0,578, entropia reali 0,531 |
| W&B | funzionante, entity di ateneo ricavata in automatico con `entity: null` |
| Test superati | 45 in locale + smoke test su GPU |

### Il prossimo comando

```bash
# sul pod, dopo averlo riavviato
cd /workspace/tesi-gian && git pull
bash scripts/run_impianto.sh        # ~40 minuti
bash scripts/valuta_impianto.sh     # poi la valutazione
```

`/dev/shm` sarà vuoto dopo il riavvio: lo script ricopia da solo. Se il pod non
ripartisse (Community Cloud non garantisce la disponibilità della GPU), se ne crea
uno nuovo agganciando lo stesso volume: va rifatto solo `bootstrap_remote.sh`.

### Decisione da prendere prima di leggere i risultati

**Quale epoca riportare in tesi.** Con `checkpoint_every: 10` su 100 epoche ci saranno
dieci checkpoint per run. Le GAN non migliorano in modo monotono: la tentazione, a
risultati visti, sarà di riportare per ciascuna condizione l'epoca col FID migliore.
È model selection sulla metrica di valutazione, ed è un rilievo facile in discussione.

Va fissato **prima**: o si riporta l'epoca 100 per entrambe mostrando la curva
completa, o si dichiara un criterio di selezione stabilito in anticipo e applicato
identicamente alle due condizioni. Non è ancora stato deciso.

### Aperto e non risolto

- **V-008** — l'espressionismo non è integralmente di pubblico dominio: da dichiarare
  in tesi, e la formula «tutti gli stili sono di pubblico dominio» va corretta ovunque.
- **Giudice sotto soglia** — 0,578 contro lo 0,60 dichiarato. Due iterazioni con
  criteri opposti danno lo stesso esito: il limite è la risoluzione, non la scelta
  degli stili. Documentato in `experiments/giudice-stile.md`, da riportare in tesi come
  limite misurato.
- **Q8** — le domande di ricerca non sono ancora formulate.
- **Q3** — peso fra componente tecnica ed etica, dipende dal relatore.

---

## 6. Prossimi passi

Ordinati per dipendenza logica, non per scadenza (le scadenze amministrative sono
gestite da Gian fuori da questo repository).

### Amministrativo

1. **Contattare il relatore.** Il suo nominativo e la sua approvazione sono il
   singolo punto di fallimento del progetto: senza, nessuna fase amministrativa
   successiva può procedere.
2. **Scegliere il titolo della tesi** (italiano e inglese) anche in forma provvisoria.
3. **V-007:** verificare i termini d'uso del dataset e sbloccare il download.

### Sperimentale

4. Preparare il sottoinsieme del dataset e lanciare lo smoke test su dati sintetici.
5. **Run E1 (DCGAN)** e **run E2 (CAN)**, registrandoli in `experiments/registry.md`.
6. Valutazione con metriche identiche sulle due condizioni; export delle figure.

### Studio percettivo

7. Predisporre questionario e consenso informato; raccogliere le risposte mentre
   procede la stesura.

### Stesura

8. Revisione della letteratura e schede in `docs/literature/` (in parallelo, non dopo).
9. Formulare le domande di ricerca (Q8) e farle approvare.
10. Stesura dei capitoli; V-001…V-005 chiuse prima della consegna.

**Ordine da non invertire.** La revisione della letteratura sarebbe metodologicamente
dovuta *prima* dell'esperimento. Farla in parallelo è una deviazione consapevole dal
metodo, e come tale va dichiarata invece che nascosta. L'esperimento è deciso e
implementato; se la revisione ne rivelasse l'inadeguatezza, resterebbe comunque
materiale per la discussione dei limiti.

---

## 7. Cronologia delle sessioni

| Data | Attività | Esito |
|---|---|---|
| 2026-07-31 | Intervista iniziale; analisi del template `phd-thesis-tex`; impostazione del monorepo | D-001…D-009 decise; Q1…Q8 aperte; infrastruttura verificata |
| 2026-08-03 | Ripianificazione: impianto ridiscusso e ratificato; ricognizione dei dataset artistici; dataset e servizio di calcolo decisi | D-010 ratificata con tre precisazioni; D-013 RunPod; D-014 ArtBench-10 supera D-011; Q2, Q4, Q7 chiuse; V-007 documentata; pipeline adattata |
| 2026-08-02 | Verifica delle scadenze ufficiali; chiusura dell'impianto sperimentale; implementazione della pipeline | V-006 verificata (date amministrative non tracciate qui); D-010…D-012 decise; Q1, Q2, Q4, Q6, Q7 chiuse; codice sperimentale implementato e testato |
| 2026-08-03 (2ª sessione) | Avvio della configurazione RunPod, sospeso; revisione del codice sperimentale prima di spendere GPU | Trovata e chiusa la lacuna sulla metrica di ambiguità (**D-015**, ADR-0005); figure dei campioni automatizzate (**D-016**); corretto il nome dei run W&B, privo del seed; `entity` W&B compilata; virtualenv `.venv` creato e dipendenze installate. **45 test superati**, zero falliti |
| 2026-08-03 (3ª sessione) | Infrastruttura RunPod completata; impianto a 64px eseguito e valutato; estensione a 128px | Dataset preparato (D-017 stili rivisti); giudici J1-J3; **8 run a 64px** con ambiguità 0,682 → 0,750 a parità di FID, IS e copertura; due ipotesi pre-registrate falsificate; **D-018** impianto a 128px; **D-019** criterio del FID minimo dopo aver osservato il collasso a fine corsa; **D-020** soglia IS < 2,0 per i run degenerati; **D-021** figure alla stessa epoca; **V-008** aperta. 78 test superati |
| 2026-08-11 | Corretta una lettura stale del repo (fetch GitHub ferma al 31/07); riallineati `project-plan.md` e `CLAUDE.md`; deciso e implementato **E5**, esperimento illustrativo condizionato per stile, esplicitamente fuori da ADR-0003 | **D-022**; codice in moduli separati (`models/conditional.py`, `training/conditional_*`, `evaluation/conditional_figures.py`); **92 test superati** (78 invariati + 14 nuovi); nessun run E5 ancora lanciato; rinominate E3→E6 (ablazione) ed E4→E7 (studio percettivo) per non collidere con `e3-dcgan-128`/`e4-can-128`; config `e6-ablazione-can-peso-zero.yaml` pronta, non avviato; Q8 lasciata sospesa su richiesta esplicita |
| 2026-08-11 (2ª sessione) | Rimosse tutte le scadenze/date amministrative dai file (richiesta esplicita e ripetuta di Gian) e aggiunta regola permanente in `CLAUDE.md` §0; dialogo aperto guidato da domande per costruire l'idea di base della tesi, con verifica di ogni affermazione contro fonti reali | Q8 con prima bozza di direzione → **D-023**; ricollegato il tema dell'accessibilità e chiarito il rapporto col problema del training → **D-024**; creato `docs/literature/da-recuperare.md` per tracciare i paper trovati non ancora in Zotero; sessione chiusa su richiesta di Gian |
