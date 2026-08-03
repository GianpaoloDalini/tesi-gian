# ADR-0005 — Come si misura l'ambiguità stilistica

- **Data:** 2026-08-03
- **Stato:** **Decisa**
- **Decisore:** Gian
- **Dipende da:** [ADR-0003](0003-impianto-sperimentale.md), [ADR-0004](0004-dataset.md)
- **Registro:** D-015

## Contesto

ADR-0003 fonda l'impianto su un confronto controllato fra due condizioni, DCGAN e CAN,
identiche in tutto tranne che nella funzione di perdita. L'ipotesi da verificare è che
il meccanismo di ambiguità stilistica della CAN produca immagini **meno attribuibili a
uno stile storico** rispetto alla baseline.

Perché quel confronto esista serve una misura di attribuibilità che sia calcolabile
**allo stesso modo nelle due condizioni**. Fino al 2026-08-03 non c'era.

## Il problema, trovato rileggendo il codice prima di affittare la GPU

La funzione `metrics.style_ambiguity` calcolava l'entropia della posterior di stile
prodotta dalla **testa di stile del discriminatore**. Due difetti, entrambi fatali per
il confronto:

1. **Non è calcolabile sulla DCGAN.** La condizione di controllo non ha testa di stile:
   la funzione restituisce `None`. La metrica esisteva solo per una delle due
   condizioni, quindi non era una metrica di confronto.
2. **Non è indipendente.** Quel discriminatore si è addestrato *contro* quel
   generatore, in un gioco a somma variabile in cui l'ambiguità è precisamente ciò che
   il generatore cerca di infliggergli. Chiedergli quanto è confuso è chiedere a una
   parte in causa di arbitrare la propria partita.

**Conseguenza se non corretto:** i sei run previsti da D-010 avrebbero prodotto FID e
Inception Score — due metriche che, come documentato in `metrics.py`, penalizzano la
CAN *per costruzione*, perché un'immagine stilisticamente ambigua si allontana dalla
distribuzione dei dati reali — e nessuna misura dell'effetto che la tesi vuole
mostrare. Si sarebbero spese ore di GPU per ottenere solo la metà sfavorevole
dell'evidenza.

## Alternative valutate

| Opzione | Confrontabile fra condizioni | Indipendente | Coerente con la critica a FID/IS |
|---|---|---|---|
| **Classificatore terzo addestrato da zero** | sì | sì | sì |
| Testa di stile del discriminatore (stato precedente) | **no** | **no** | — |
| ResNet-18 pre-addestrata su ImageNet | sì | sì | **no** |
| Giudice riaddestrato per ogni run | no | sì | sì |

**Perché non ImageNet.** `metrics.py` critica FID e IS proprio perché poggiano su
feature di una rete addestrata su fotografie, il cui spazio non è costruito per
rappresentare la pittura. Adottare un giudice con lo stesso vizio significherebbe
muovere un'obiezione e poi commetterla — un'incoerenza che in sede di discussione si
paga cara. Con sei classi e migliaia di immagini per classe, l'addestramento da zero è
ampiamente sufficiente.

**Perché non riaddestrarlo per ogni run.** Introdurrebbe una variabile nascosta:
entropie prodotte da giudici diversi non sono confrontabili, che è esattamente il
difetto da eliminare.

## Decisione

Un **classificatore di stile addestrato una volta sola sui soli dati reali e poi
congelato**, riusato identico per tutte le condizioni e tutti i seed.

Modulo: `src/tesi_gan/evaluation/style_classifier.py`
Comando: `python -m tesi_gan.cli train-style-classifier`

### Scelte di dettaglio

- **Architettura**: stessa famiglia della backbone del discriminatore (blocchi
  Conv-BatchNorm-LeakyReLU con stride 2). Un giudice molto più capace misurerebbe
  un'ambiguità che nel gioco avversario non ha mai avuto un ruolo; molto meno capace,
  misurerebbe la propria incompetenza.
- **Ingresso in `[-1, 1]`**, la stessa scala del dataloader e dell'uscita `tanh` del
  generatore: nessuna conversione ai bordi, nessun rischio di valutare i due domini su
  scale diverse.
- **Split stratificato e seedato**, con accuratezza di validazione registrata nei
  metadati. Sotto `MIN_VAL_ACCURACY = 0.60` il modulo avvisa esplicitamente.
- **Seed proprio** (`style_judge.seed = 1234`), indipendente dai tre seed dei run: il
  giudice non fa parte delle ripetizioni dell'impianto.
- **Si tiene l'epoca migliore**, non l'ultima: continuare oltre il massimo peggiorerebbe
  il giudice per overfitting senza che se ne accorga nessuno.
- **Rifiuto di sovrascrivere** senza `--force`: riaddestrarlo invaliderebbe i run già
  valutati, che sono stati misurati da un giudice diverso.
- **Verifica delle classi al caricamento**: valutare con un giudice addestrato su altri
  stili produrrebbe numeri privi di significato, e il fallimento dev'essere rumoroso.
- **`evaluate` senza giudice fallisce** con un messaggio esplicito, salvo
  `--allow-no-judge` per i controlli rapidi.

## Conseguenze

### Positive

- L'ambiguità diventa confrontabile fra DCGAN e CAN: il confronto di ADR-0003 esiste.
- Il giudice non sa quale condizione ha prodotto le immagini — è il punto.
- Le entropie sono confrontabili anche fra seed, quindi ha senso riportare media e
  dispersione sulle tre ripetizioni.
- Rende possibile la figura annotata di D-016, che mostra l'effetto senza tabelle.

### Negative e da dichiarare

- **Un passo in più prima dei run.** Il giudice va addestrato per primo. Se lo si
  dimentica, `evaluate` si rifiuta di procedere — deliberatamente.
- **Il giudice non è infallibile.** La sua accuratezza è un limite superiore alla
  fiducia riponibile nelle entropie, e va riportata in appendice accanto ai risultati.
- **Barocco, Romanticismo e Realismo sono visivamente vicini** (nota già in ADR-0004):
  il giudice li confonderà anche su immagini reali. La matrice di confusione va
  riportata, perché una parte dell'entropia misurata sui generati è attribuibile a
  questa vicinanza e non all'ambiguità prodotta dal modello.

### Il confondimento centrale, non risolvibile con il codice

Un'entropia alta significa «il classificatore non sa attribuire uno stile». Ci sono
**due** ragioni perché accada:

- l'immagine è pittoricamente sensata ma stilisticamente ibrida — l'effetto cercato;
- l'immagine è rumore informe — non c'è nulla da classificare.

**Un generatore collassato ottiene ambiguità massima.** La metrica da sola non
distingue i due casi. Perciò l'entropia non va **mai** riportata isolata: si legge
accanto al FID e alla griglia di campioni. Entropia alta *e* FID basso è l'esito
interessante; entropia alta *e* FID pessimo è un modello che non ha imparato a
dipingere. Il codice emette un avviso quando ricorre il secondo caso, ma la
dichiarazione esplicita in tesi resta obbligatoria: è il rilievo più facile e più
meritato che la commissione possa muovere.

### Ancore di lettura

Le entropie assolute non dicono nulla senza due riferimenti, entrambi calcolati e
salvati insieme al giudice:

- `entropy_real` — entropia sulle immagini **reali** di validazione: il pavimento,
  quanto il giudice è sicuro su arte vera e attribuibile;
- `log(K)` — il soffitto teorico, raggiunto dalla posterior uniforme.

Un valore normalizzato in `[0, 1]` senza il confronto col pavimento è un numero che
sembra significare qualcosa e non significa niente.

## Cosa resta aperto

- La soglia `MIN_VAL_ACCURACY = 0.60` è un valore di buon senso, non derivato dalla
  letteratura. Se il giudice si assesta molto sopra o molto sotto, va rivista e la
  scelta motivata.
- Il giudice misura l'attribuibilità secondo un classificatore, **non** la percezione
  umana. Non sostituisce lo studio percettivo di D-012: lo rende confrontabile con una
  misura automatica, che è cosa diversa.
