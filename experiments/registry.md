# Registro degli esperimenti

Ogni run che produce un numero o una figura citati nella tesi va registrato qui.
È il ponte tra `experiments/` (ignorato da git) e il testo dell'elaborato: senza,
tra tre mesi non saprai da quale run proviene la Figura 6.2.

## Impianto principale — 2026-08-03

Commit `b207c045` · 100 epoche · batch 128 · label smoothing 0,1 · ArtBench-10 sei
stili a 64×64 · valutazione su 2.048 campioni, identica per tutti i run · giudice di
stile J2 congelato (accuratezza 0,578, entropia sui reali 0,531).

**Criterio dichiarato prima di leggere i risultati:** si riporta **l'epoca 100** per
tutti i run. Nessuna selezione a posteriori del checkpoint migliore, che sarebbe
selezione del modello sulla metrica di valutazione.

| Run | FID ↓ | IS ↑ | Ambiguità | Copertura | Note |
|---|---|---|---|---|---|
| `dcgan-seed1` | 114,1 | 4,39 | 0,698 | 0,963 | |
| `dcgan-seed2` | 106,5 | 4,09 | 0,674 | 0,968 | |
| `dcgan-seed3` | 102,3 | 3,86 | 0,673 | 0,966 | |
| `can-seed1` | 395,4 | 1,12 | 0,794 | 0,190 | **collassato**, escluso dalle medie |
| `can-seed2` | 111,3 | 3,99 | 0,740 | 0,953 | |
| `can-seed3` | 103,3 | 4,11 | 0,759 | 0,982 | |

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
