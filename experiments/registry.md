# Registro degli esperimenti

Ogni run che produce un numero o una figura citati nella tesi va registrato qui.
È il ponte tra `experiments/` (ignorato da git) e il testo dell'elaborato: senza,
tra tre mesi non saprai da quale run proviene la Figura 6.2.

## Revisione del criterio di selezione del checkpoint — 2026-08-03, sera

> **Questa sezione documenta un cambio di criterio avvenuto dopo aver visto dei
> risultati.** È esattamente la situazione in cui una revisione può diventare
> disonesta, quindi va scritta per intero: cosa era stato dichiarato prima, cosa è
> emerso, perché il criterio è cambiato e come è stato reso non arbitrario.

### Cosa era stato dichiarato

Prima di lanciare l'impianto a 64px: **si riporta l'epoca 100 per tutti i run**,
senza selezione a posteriori del checkpoint migliore, che sarebbe stata selezione del
modello sulla metrica di valutazione.

### Cosa è emerso

Osservando i campioni per epoca dei run a **128px**, `dcgan-seed1` mostra:

- **epoca 90 e 97:** immagini di qualità nettamente superiore a qualunque risultato a
  64px — figure riconoscibili, paesaggi, materia pittorica;
- **epoca 98:** collasso completo in un motivo a scacchiera ripetuto, la firma tipica
  degli artefatti di `ConvTranspose2d` quando l'addestramento diverge;
- **epoca 100:** stato degenerato, ed è il checkpoint che il criterio pre-registrato
  avrebbe imposto di riportare.

Il criterio non prevedeva che il collasso potesse arrivare **a fine corsa**. Applicarlo
alla lettera significherebbe presentare come risultato un modello degenerato mentre
otto epoche prima era il miglior esito dell'intero progetto.

### Il criterio nuovo

**Si valutano tutti i checkpoint salvati di ogni run, si pubblica la traiettoria
completa, e il numero di sintesi è quello del checkpoint con FID minimo.**

Tre condizioni lo rendono difendibile, e vanno tutte soddisfatte:

1. **La regola è identica** per ogni run e per entrambe le condizioni.
2. **La traiettoria completa è pubblicata**, non solo il punto scelto: si vede quando e
   come ciascun run migliora o degenera.
3. **L'adozione è datata e motivata**, cioè questa sezione.

**La selezione avviene sul FID, non sull'ambiguità**, ed è il punto metodologico
centrale. Selezionare sull'ambiguità significherebbe scegliere il checkpoint che
favorisce l'ipotesi: sarebbe circolare. Il FID è indipendente da ciò che si vuole
dimostrare, e semmai *sfavorevole* all'ipotesi — ci si attendeva che l'ambiguità
crescesse al peggiorare della fedeltà, quindi scegliere il punto di fedeltà massima
tende a selezionare il punto di ambiguità **minima**.

### Cosa resta valido del criterio vecchio

I risultati a 64px restano riportati anche all'epoca 100, come pre-registrato. Il
confronto fra i due criteri sullo stesso impianto è a sua volta informativo: se
coincidono, la revisione non ha spostato nulla; se divergono, la differenza va
discussa.

### Conseguenza operativa emersa

Con `checkpoint_every: 10` l'epoca 97 **non è stata salvata**: su disco esistono solo
90 e 100. Le immagini che hanno rivelato il collasso vengono da W&B, che registra ogni
epoca. Per impianti futuri conviene una cadenza più fitta nelle ultime epoche, oppure
salvare anche il checkpoint con la metrica migliore mentre il training procede.

---

## Impianto principale — 2026-08-03

Commit `b207c045` · 100 epoche · batch 128 · label smoothing 0,1 · ArtBench-10 sei
stili a 64×64 · valutazione su 2.048 campioni, identica per tutti i run · giudice di
stile J2 congelato (accuratezza 0,578, entropia sui reali 0,531).

**Criterio dichiarato prima di leggere i risultati:** si riporta **l'epoca 100** per
tutti i run. Nessuna selezione a posteriori del checkpoint migliore, che sarebbe
selezione del modello sulla metrica di valutazione.

| Run | run_id W&B | Commit | FID ↓ | IS ↑ | Ambiguità | Copertura | Note |
|---|---|---|---|---|---|---|---|
| `dcgan-seed1` | `fjnrok9x` | `b207c045` | 114,1 | 4,39 | 0,698 | 0,963 | |
| `dcgan-seed2` | `py2pdu4d` | `b207c045` | 106,5 | 4,09 | 0,674 | 0,968 | |
| `dcgan-seed3` | `uzzts94t` | `b207c045` | 102,3 | 3,86 | 0,673 | 0,966 | |
| `dcgan-seed4` | `j8pv11cf` | `cebbf574` | | | | | replica aggiuntiva |
| `can-seed1` | `39p77bfu` | `b207c045` | 395,4 | 1,12 | 0,794 | 0,190 | **collassato**, escluso dalle medie |
| `can-seed2` | `0w895qua` | `b207c045` | 111,3 | 3,99 | 0,740 | 0,953 | |
| `can-seed3` | `dx3j6xf4` | `b207c045` | 103,3 | 4,11 | 0,759 | 0,982 | |
| `can-seed4` | `pq4wsp6y` | `cebbf574` | | | | | replica aggiuntiva |

Run accessori, **non citabili** e tenuti solo per tracciabilità:

| Run | run_id | Commit | Scopo |
|---|---|---|---|
| `dcgan-seed99` | `nzwype85` | `026d1ddf` | 2 epoche, misura dello speedup da `/dev/shm` |

### Sulla differenza di commit fra seed 1-3 e seed 4

I seed 1-3 girano su `b207c045`, il seed 4 su `cebbf574`. **La differenza non tocca
l'addestramento**, ed è stato verificato invece che assunto:

```bash
git diff --stat b207c045 cebbf574 -- src/tesi_gan/models src/tesi_gan/training \
    src/tesi_gan/data configs/model configs/experiment configs/data
# output vuoto
```

Le modifiche fra i due commit riguardano `evaluation/`, `scripts/`, `tests/` e la
documentazione: metrica di copertura, figure e strumenti di lettura dei risultati.
Modelli, funzioni di perdita, ciclo di addestramento, dataloader e configurazioni
degli esperimenti sono identici, quindi le otto repliche sono confrontabili.

**Se un giorno un commit toccasse `models/` o `training/` fra due repliche della
stessa condizione, quelle repliche non sarebbero più confrontabili** e andrebbero
rifatte. È il motivo per cui il commit sta in tabella accanto al `run_id`.

### Confronto fra le condizioni

| Metrica | DCGAN (n=3) | CAN (n=2) | Atteso | Esito |
|---|---|---|---|---|
| FID ↓ | 107,7 ± 6,0 | 107,3 ± 5,7 | CAN peggiore | **ipotesi falsificata** |
| Inception Score ↑ | 4,11 ± 0,27 | 4,05 ± 0,09 | incerto | nessuna differenza |
| **Ambiguità (giudice terzo)** | **0,682 ± 0,014** | **0,750 ± 0,013** | CAN alta | **confermato** |
| Copertura degli stili | 0,966 ± 0,003 | 0,967 ± 0,020 | controllo | nessuna differenza |

Riferimenti di lettura: arte reale 0,531 · soffitto `log(6)` = 1,000.

### Come vanno letti

**L'ambiguità sale e nient'altro cambia.** I due gruppi non si sovrappongono — DCGAN
fra 0,673 e 0,698, CAN fra 0,740 e 0,759 — e la differenza di 0,068 vale circa cinque
volte la dispersione interna alle condizioni. Con n piccolo non si fanno test
statistici: si riportano media e intervallo.

**La copertura identica esclude la spiegazione alternativa.** Un'entropia per immagine
alta potrebbe derivare da fusione stilistica (l'effetto cercato) oppure da collasso su
una zona generica che il classificatore non sa attribuire. La marginale delle classi
predette è però la stessa nelle due condizioni: la CAN mantiene la copertura degli
stili **e** aumenta l'incertezza per immagine. L'alternativa è esclusa da una misura,
non da un argomento.

**Due ipotesi pre-registrate sono state falsificate**, e vanno riportate come tali:
che la CAN peggiorasse il FID (non è successo), e la previsione che l'ambiguità della
DCGAN scendesse con l'addestramento (è salita, da 0,601 a 20 epoche a 0,682 a 100).
La seconda ha una lettura: una GAN incondizionata addestrata su sei stili modella la
*miscela*, quindi più impara più produce immagini stilisticamente ibride.
**L'ambiguità della CAN è una spinta ulteriore sopra quella che una GAN produce già
da sola** — lettura più sottile e più difendibile di «la CAN rende ambiguo, la GAN no».

**Le due misure di ambiguità si contraddicono sullo stesso modello.** La testa di
stile del discriminatore della CAN dà 0,28, cioè «immagini facilmente attribuibili»;
il giudice indipendente dà 0,75. È la dimostrazione empirica del motivo per cui il
giudice terzo esiste (ADR-0005): non più un argomento teorico ma un numero.

### Il run collassato

`can-seed1` produce sessantaquattro campioni visivamente identici. FID 395,4,
Inception Score 1,12 (con 1,0 come minimo assoluto), copertura 0,190 con l'89,3% delle
attribuzioni su un solo stile. È mode collapse conclamato, riconoscibile da tre
metriche indipendenti e dall'ispezione visiva.

**Non si cancella e non si sostituisce in silenzio.** Resta in tabella, escluso dalle
medie con motivazione esplicita. Vale anche come dato in sé: **un run su tre della CAN
è collassato, zero su tre della DCGAN.** La differenza di stabilità fra le due
condizioni è un risultato, e con più seed diventerebbe quantificabile.

**È anche la giustificazione a posteriori di D-010 punto 3.** Con un solo seed per
condizione, se fosse capitato quello, la conclusione sarebbe stata che la CAN è una
catastrofe. Le repliche non erano una precauzione formale.

### Estensione a quattro seed

Escludendo il run collassato la CAN si regge su due seed, e una deviazione standard
calcolata su due valori è poco più che decorativa. Si aggiunge il **seed 4 a entrambe
le condizioni**, non solo alla CAN: aggiungere repliche solo alla condizione che ha
avuto il problema significherebbe trattare le due in modo diverso, ed è esattamente
l'asimmetria che verrebbe contestata in discussione.

## Impianto 128px — 2026-08-04

Risoluzione 128×128 · ArtBench-10 sei stili (D-014/D-017) · valutazione su 2.048
campioni, identica per tutti i run · giudice di stile J3 congelato (accuratezza
0,623, entropia sui reali 0,401 — **giudice e riferimento diversi da quelli usati a
64px** (0,531): i due impianti non sono confrontabili sulla scala assoluta di
ambiguità, solo sull'effetto relativo CAN−DCGAN, vedi D-018).

**Criterio di selezione: FID minimo su tutta la traiettoria** (D-019), non l'epoca
100 fissa. Traiettoria completa in `experiments/traiettoria-128/` (66 checkpoint
valutati, 11 per run), script `scripts/traiettoria.py` e `scripts/sintesi.py`.

TODO[DATA]: commit hash e run_id W&B dei sei run — recuperarli dalla dashboard W&B
del pod RunPod e completare la tabella prima di citare questi numeri in tesi.

| Run | run_id W&B | Commit | Epoca selezionata | FID ↓ | IS ↑ | Ambiguità | Copertura | Note |
|---|---|---|---|---|---|---|---|---|
| `can-seed1` | TODO | TODO | 20 | 171,4 | 3,05 | 0,625 | 0,680 | picco poi degrado fino a FID 305,7 a epoca 100 |
| `can-seed2` | TODO | TODO | 20 | 201,4 | 3,27 | 0,633 | 0,851 | picco poi degrado fino a FID 268,0 a epoca 100 |
| `can-seed3` | TODO | TODO | 20 | 177,5 | 3,02 | 0,650 | 0,896 | picco poi degrado fino a FID 305,2 a epoca 100 |
| `dcgan-seed1` | TODO | TODO | 80 | 109,9 | 3,57 | 0,544 | 0,898 | collassa a epoca 100 (FID 248,3): stesso fenomeno a scacchiera che ha motivato D-019 |
| `dcgan-seed2` | TODO | TODO | 100 | 117,6 | 3,73 | 0,528 | 0,911 | |
| `dcgan-seed3` | TODO | TODO | 90 | 126,0 | 3,87 | 0,570 | 0,964 | |

Nessuno dei sei checkpoint selezionati ha IS < 2,0: il criterio D-020 non esclude
alcun run da questo impianto.

### Confronto fra le condizioni

| Metrica | DCGAN (n=3) | CAN (n=3) | Atteso | Esito |
|---|---|---|---|---|
| FID ↓ | 117,8 ± 8,0 | 183,4 ± 15,8 | CAN peggiore o pari | **CAN nettamente peggiore (+55%)** |
| Inception Score ↑ | 3,72 ± 0,15 | 3,12 ± 0,14 | incerto | DCGAN migliore |
| Ambiguità (giudice terzo) | 0,547 ± 0,021 | 0,636 ± 0,013 | CAN alta | confermato |
| Copertura degli stili | 0,924 ± 0,035 | 0,809 ± 0,114 | controllo | CAN più bassa e più dispersa |

Riferimenti di lettura: arte reale 0,401 · soffitto `log(6)` = 1,000 · accuratezza
del giudice 0,623.

### Osservazione da verificare: collasso sistematico del CAN dopo l'epoca 20

**I tre seed CAN raggiungono il FID minimo tutti alla stessa epoca (20 su 100), poi
degradano quasi monotonicamente per il resto del training:** `can-seed1` 171,4 →
305,7, `can-seed3` 177,5 → 305,2, `can-seed2` 201,4 → 268,0. Non è il collasso
isolato di un singolo run come `dcgan-seed1` (che degrada solo nell'ultimo tratto,
epoca 90→100): qui il fenomeno è **sistematico su tutti e tre i seed CAN**, e
comincia presto — al 20% del training.

**Non sembra lo stesso fenomeno del mode collapse osservato a 64px** (`can-seed1` a
64px: copertura 0,190, 89,3% delle attribuzioni su un solo stile — vedi sopra). Qui
la copertura oscilla ma non crolla in modo pulito: il minimo di `can-seed1` a 128px
è 0,603 all'epoca 100, mai vicino a 0,19. **Da verificare con ispezione visiva dei
campioni a epoca 20 vs epoca 100 per i tre seed CAN** prima di scrivere in tesi che
«il CAN collassa» a 128px — potrebbe essere degrado generico di qualità (rumore,
artefatti) piuttosto che collasso di modo su un singolo stile. Vedi V-008 in
`docs/registro-decisioni.md`.

**Confronto con l'impianto a 64px.** Lì il vantaggio di ambiguità del CAN non
costava nulla in fedeltà (FID 107,3 vs 107,7, indistinguibili). Qui il vantaggio di
ambiguità è di entità simile (+0,089 vs +0,068 a 64px) ma costa un FID nettamente
peggiore. Se confermata dall'ispezione visiva, l'ipotesi che **l'instabilità del CAN
scali con la risoluzione** è il risultato più rilevante di questo impianto — ma è
un'ipotesi emersa dai dati, non pre-registrata, e va trattata con la stessa cautela
metodologica già applicata alla revisione del criterio di selezione (D-019).

---

## Registri collegati

- [`giudice-stile.md`](giudice-stile.md) — iterazioni del classificatore terzo
  (D-015). Nessuna ha raggiunto la soglia dichiarata: il percorso è documentato
  perché mostra che il limite è stato misurato, non subito, ed è materiale per il
  capitolo di metodologia e per la sezione sui limiti.

## Regole

1. **Nessun run senza commit.** Il working tree dev'essere pulito prima del training
   (`tesi_gan.utils.provenance.assert_clean_tree`).
2. **I run falliti si registrano**, non si cancellano. Un fallimento documentato è
   materiale per la sezione sui limiti; un fallimento rimosso è tempo perso due volte.
3. La colonna *Usato in* indica figura, tabella o sezione della tesi. Se resta vuota
   a lungo, o il run era inutile o la tesi sta ignorando un risultato.
