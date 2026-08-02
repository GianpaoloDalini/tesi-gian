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

**Ultimo aggiornamento:** 2026-08-03

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
replica del protocollo di Elgammal (mesi di lavoro, incompatibile con la scadenza).

**Motivazione:** serve almeno un giudizio umano perché il capitolo dei risultati non
poggi interamente su FID e IS, di cui la tesi dichiara i limiti.

**Limite da dichiarare senza attenuanti:** campione di convenienza, non
rappresentativo, numerosità bassa. I risultati vanno presentati come **indicativi**,
mai come statisticamente significativi. Presentare un campione di convenienza come
evidenza forte è un errore che la commissione rileva immediatamente; dichiararlo come
esplorativo è invece perfettamente difendibile.

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

## 3. Questioni aperte

Ordinate per criticità. Le questioni chiuse restano elencate con il rimando alla
decisione che le ha risolte: cancellarle farebbe perdere la traccia del percorso.

### Q1 — Sessione di laurea ✅ chiusa
**Stato:** risolta il 2026-08-02 · **Verifica:** V-006

Sessione autunnale, **discussione magistrale 2 ottobre 2026**. Le date non sono più
un'ipotesi: sono state lette sull'avviso ufficiale della Scuola di Ingegneria, che
riporta testualmente «non sono ammesse deroghe rispetto alle scadenze indicate».

L'obiezione del 31 luglio era fondata e la risposta «non preoccuparti delle scadenze»
era basata su un'informazione sbagliata: **la Fase 1 scade il 14 agosto 2026**, non a
settembre. Vedi V-006 per il calendario completo.

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

### Q4 — Dataset 🔶 chiusa nel criterio, aperta nella lista
**Stato:** criterio deciso il 2026-08-03 → **D-011**, [ADR-0004](decisions/0004-dataset.md) · **Riserva:** V-007

Deciso: WikiArt, pochi stili scelti per distanza visiva **e** appartenenza al
pubblico dominio. Da decidere: quali cinque (o quattro), sui conteggi reali prodotti
da `python -m tesi_gan.data.inventory`.

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

### Q6 — Studio percettivo con soggetti umani 🔶 riaperta
**Stato:** **di nuovo aperta dal 2026-08-03** · **Proposta:** D-012

Sì, versione leggera con campione di convenienza. Limiti da dichiarare senza
attenuanti.

### Q7 — Servizio di calcolo e budget ✅ chiusa
**Stato:** chiusa il 2026-08-03 → **D-013**

RunPod con RTX 4090. Dimensionamento: 64×64, sei run (due condizioni × tre seed) da
circa 100 epoche su un sottoinsieme di alcune migliaia di immagini. Ore consumate e
costo effettivo vanno annotati qui man mano, per l'appendice sulla riproducibilità.

### Q8 — Domande di ricerca 🔴 ora la più urgente
**Stato:** aperta

Non ancora formulate. Con Q2 chiusa non dipendono più dall'impianto, ma restano
subordinate alla revisione della letteratura: formulare domande di ricerca prima di
conoscere lo stato dell'arte produce quasi sempre domande già risolte o mal poste.

**Vincolo nuovo:** la Fase 1 della domanda di laurea richiede il **titolo della tesi
entro il 14 agosto 2026** (V-006). Un titolo si può cambiare, ma sceglierlo senza
avere almeno una domanda di ricerca abbozzata significa sceglierlo a caso.

Direzione compatibile con D-010, da affinare dopo la revisione:
*che cosa misura effettivamente il meccanismo di ambiguità stilistica di una CAN, e
in che rapporto sta con le metriche con cui la letteratura ne valuta il risultato.*

---

## 4. Verifiche da fare

Punti su cui è stata fatta un'ipotesi o un adattamento che va confermato da una fonte
autorevole prima della consegna.

### V-006 — Scadenze della sessione autunnale ✅ verificata, con adempimenti aperti
**Verificata il:** 2026-08-02
**Fonte:** [Avviso Lauree Settembre 2026 — Scuola di Ingegneria UniBg](https://www.unibg.it/sites/default/files/media/documents/2026-07-03/Avviso%20Lauree%20Settembre%202026.pdf)

L'avviso riporta: «**NON SONO AMMESSE DEROGHE RISPETTO ALLE SCADENZE INDICATE**».

| Adempimento | Scadenza | Stato |
|---|---|---|
| Fase 1 — deposito titolo tesi (IT + EN) e nominativo relatore | **ven 14/08/2026** | ⬜ da fare |
| Fase 2 — approvazione online del relatore | lun 17/08/2026 | ⬜ dipende dal relatore |
| Fase 3 — domanda definitiva + questionario AlmaLaurea + € 32 | mar 18/08/2026 | ⬜ da fare |
| Termine registrazione esami | sab 12/09/2026 | ⬜ da verificare |
| Fase 4 — caricamento dell'elaborato | ven 11/09 – lun 21/09/2026 | ⬜ |
| Discussione e proclamazione (magistrali) | **ven 02/10/2026** | — |

**Conseguenze immediate.** La Fase 1 richiede il nominativo del relatore, che è
tuttora `DA DEFINIRE` (§1) e che deve poi approvare online entro il 17 agosto, in
pieno agosto. Questo, non il training, è il rischio principale del progetto: nessun
risultato sperimentale compensa una domanda non presentata.

Il tempo effettivo per la parte sperimentale e la stesura è **fino al 21 settembre**,
cioè circa sette settimane da oggi.

### V-007 — Termini d'uso del dataset 🟠 in parte chiarita
**Stato:** parzialmente verificata il 2026-08-03; resta da leggere i ToU della fonte
**Riferimento:** [ADR-0004](decisions/0004-dataset.md)

**Novità del 2026-08-03.** La situazione è migliore di come era stata registrata.
Il dataset non ha licenza «ignota»: il README del WikiArt refined di ArtGAN
([cs-chan/ArtGAN](https://github.com/cs-chan/ArtGAN/blob/master/WikiArt%20Dataset/README.md))
dichiara testualmente *«The WikiArt dataset can be used only for non-commercial
research purpose»*, e rimanda ai termini di WikiArt.org. Una tesi magistrale è
ricerca non commerciale, quindi rientra nella condizione dichiarata.

Su Hugging Face lo stesso materiale è invece etichettato `license: unknown` con la
nota *«Data files © Original Authors»*: le due fonti dicono cose diverse sullo
stesso dataset, ed è di per sé un'osservazione da riportare in tesi.

**Resta da fare:** leggere i termini d'uso di WikiArt.org e verificare che l'uso
previsto vi rientri. Questa verifica la fa Gian, non l'assistente.

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

Ordinati per **scadenza**, non per dipendenza logica: da oggi il calendario comanda.

### Entro il 14 agosto — amministrativo, non rinviabile

1. **Contattare il relatore.** Il suo nominativo serve in Fase 1 e la sua approvazione
   online in Fase 2 entro il 17 agosto. È il singolo punto di fallimento del progetto.
2. **Scegliere il titolo della tesi** (italiano e inglese) anche in forma provvisoria.
3. **Fase 1** entro venerdì 14/08, **Fase 3** entro martedì 18/08, con questionario
   AlmaLaurea e pagamento.
4. **V-007:** verificare i termini d'uso del dataset e sbloccare il download.

### Entro fine agosto — sperimentale

5. Preparare il sottoinsieme del dataset e lanciare lo smoke test su dati sintetici.
6. **Run E1 (DCGAN)** e **run E2 (CAN)**, registrandoli in `experiments/registry.md`.
7. Valutazione con metriche identiche sulle due condizioni; export delle figure.

### Entro il 6 settembre — studio percettivo

8. Predisporre questionario e consenso informato; raccogliere le risposte mentre
   procede la stesura.

### Fino al 21 settembre — stesura

9. Revisione della letteratura e schede in `docs/literature/` (in parallelo, non dopo).
10. Formulare le domande di ricerca (Q8) e farle approvare.
11. Stesura dei capitoli; V-001…V-005 chiuse prima della consegna.

**Ordine da non invertire.** La revisione della letteratura sarebbe metodologicamente
dovuta *prima* dell'esperimento. Con sette settimane e agosto di mezzo, si fa in
parallelo: è una deviazione consapevole dal metodo, imposta dal calendario, e come
tale va dichiarata invece che nascosta. L'esperimento è deciso e implementato; se la
revisione ne rivelasse l'inadeguatezza, resterebbe comunque materiale per la
discussione dei limiti.

---

## 7. Cronologia delle sessioni

| Data | Attività | Esito |
|---|---|---|
| 2026-07-31 | Intervista iniziale; analisi del template `phd-thesis-tex`; impostazione del monorepo | D-001…D-009 decise; Q1…Q8 aperte; infrastruttura verificata |
| 2026-08-03 | Ripianificazione: impianto ridiscusso e ratificato, dataset e servizio di calcolo decisi | D-010 ratificata con tre precisazioni; D-011 chiusa nel criterio; D-013 RunPod; V-007 chiarita; modulo di inventario del dataset |
| 2026-08-02 | Verifica delle scadenze ufficiali; chiusura dell'impianto sperimentale; implementazione della pipeline | V-006 verificata (Fase 1 il 14/08, discussione il 02/10); D-010…D-012 decise; Q1, Q2, Q4, Q6, Q7 chiuse; codice sperimentale implementato e testato |
