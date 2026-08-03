# Giudice di stile — cronologia delle iterazioni

Registro delle versioni del classificatore terzo (D-015, [ADR-0005](../docs/decisions/0005-giudice-ambiguita.md)),
la cui entropia sostiene l'intero confronto fra DCGAN e CAN.

> **Perché questo file esiste.** Nessuna di queste iterazioni ha raggiunto la soglia
> di affidabilità che ci si era dati. Cancellarle e mostrare solo la versione finale
> darebbe l'impressione di una scelta ovvia presa al primo colpo: non lo è stata, e
> il percorso è a suo modo un risultato. Documenta che il limite è stato **misurato**
> e non subito, e alimenta direttamente il capitolo di metodologia e la sezione sui
> limiti. `CLAUDE.md` §6: un esperimento fallito si documenta, non si cancella.

**Costante in tutte le iterazioni:** 30.000 immagini di addestramento, 6.000 di
validazione sullo split `test` ufficiale di ArtBench, 64×64, 15 epoche, batch 64,
Adam lr 2e-4, seed 1234, architettura da zero (nessun pre-addestramento).
Soglia di affidabilità dichiarata: **0,60**.

---

## Sintesi

| Iter. | Risoluzione | Stili | Accuratezza | Entropia sui reali (norm.) | Esito |
|---|---|---|---|---|---|
| **J1** | 64px | ukiyo_e, renaissance, baroque, **romanticism**, **realism**, impressionism | 0,527 | 0,811 nats (**0,452**) | sotto soglia |
| **J2** | 64px | ukiyo_e, renaissance, baroque, **art_nouveau**, **expressionism**, impressionism | 0,578 | 0,951 nats (**0,531**) | sotto soglia |
| **J3** | **128px** | stessi sei di J2 | 0,623 | 0,719 nats (**0,401**) | sotto soglia, ma pavimento molto migliore |

Soffitto teorico in tutte: `log(6)` = 1,792 nats.

**Il dato che conta non è l'accuratezza.** J2 migliora di 5 punti percentuali ma
**peggiora il pavimento dell'entropia**, che è la grandezza da cui dipende la
sensibilità della metrica: se il giudice è già incerto sull'arte vera, resta poco
spazio per mostrare che le immagini della CAN sono *più* ambigue. J2 è quindi un
miglioramento apparente e un peggioramento sostanziale.

---

## J1 — insieme cronologico

**Criterio di selezione:** arco cronologico della pittura occidentale
(Rinascimento → Barocco → Romanticismo → Realismo → Impressionismo) con l'Ukiyo-e
come contrappunto non occidentale, legato agli impressionisti dal giapponismo.
Tutti gli stili di pubblico dominio.

**Accuratezza 0,527** · **entropia sui reali 0,811 nats (0,452 normalizzata)**

Matrice di confusione, percentuali di riga (riga = vero, colonna = predetto):

```
                  baroq  impre  reali  renai  roman  ukiyo
baroque        |    65%     4%     8%    11%    10%     2%   (65% corrette)
impressionism  |     7%    59%    15%     7%     8%     4%   (59% corrette)
realism        |    17%    28%    30%     9%    14%     2%   (30% corrette)
renaissance    |    33%     8%     6%    45%     6%     3%   (45% corrette)
romanticism    |    23%    20%    18%    10%    26%     4%   (26% corrette)
ukiyo_e        |     2%     3%     2%     1%     1%    91%   (91% corrette)
```

Confusioni più frequenti: `renaissance`→`baroque` 329, `realism`→`impressionism` 276,
`romanticism`→`baroque` 229, `romanticism`→`impressionism` 195,
`romanticism`→`realism` 180.

**Lettura.** Il Romanticismo al 26% contro un caso puro del 16,7% è appena 1,6 volte
il caso, e i suoi errori **non si concentrano su un vicino**: si distribuiscono su
quattro classi. Non è confusione fra stili adiacenti ma assenza di identità visiva a
questa risoluzione — coerente col fatto che il Romanticismo è definito più da
soggetto e atmosfera che da una tecnica riconoscibile. Il Realismo scambiato per
Impressionismo nel 28% dei casi non era stato previsto.

**Conclusione:** rimossi i due stili più opachi (D-017).

---

## J2 — insieme a massima distanza visiva

**Criterio di selezione:** distanza visiva anziché coerenza storica. Fuori
`romanticism` e `realism`, dentro `art_nouveau` (linea decorativa, campiture piatte)
ed `expressionism` (colore violento, forme distorte).

**Ipotesi:** i due stili nuovi si sarebbero comportati come `ukiyo_e` (91% in J1),
alzando l'accuratezza e **abbassando** il pavimento dell'entropia.

**Accuratezza 0,578** · **entropia sui reali 0,951 nats (0,531 normalizzata)**

```
                  art_n  baroq  expre  impre  renai  ukiyo
art_nouveau    |    42%     4%    23%    12%    15%     5%   (42% corrette)
baroque        |     3%    68%     4%     5%    18%     2%   (68% corrette)
expressionism  |    19%     6%    42%    15%    13%     5%   (42% corrette)
impressionism  |     9%    11%    13%    54%    10%     3%   (54% corrette)
renaissance    |     7%    25%     7%     4%    55%     1%   (55% corrette)
ukiyo_e        |     5%     1%     5%     1%     2%    87%   (87% corrette)
```

Confusioni più frequenti: `renaissance`→`baroque` 249,
`art_nouveau`→`expressionism` 227, `expressionism`→`art_nouveau` 187,
`baroque`→`renaissance` 182, `expressionism`→`impressionism` 151.

**L'ipotesi è stata falsificata.** I due stili nuovi si fermano al 42% ciascuno — meglio
dei due rimossi, molto peggio di `ukiyo_e` — e **si confondono reciprocamente**
(227 e 187 scambi). A 64 pixel «linea decorativa e campiture piatte» e «colore
violento e forme distorte» collassano entrambi in «immagine chiara, piatta, non
fotografica». La distanza visiva che li rendeva promettenti esiste alla risoluzione
originale, non a quella di addestramento.

**L'effetto collaterale è più grave del guadagno.** Entropia e accuratezza misurano
cose diverse: il classificatore di J2 indovina più spesso ma è meno sicuro anche
quando ha ragione. Il pavimento sale da 0,452 a 0,531, cioè lo spazio utile per
misurare l'ambiguità della CAN si **restringe** invece di allargarsi.

**Costo collaterale:** perduto l'arco cronologico che motivava J1, e introdotto uno
stile non integralmente di pubblico dominio (V-008).

---

## Ciò che le prime due iterazioni dimostrano insieme

Due insiemi di stili scelti con criteri **opposti** — coerenza storica in J1, massima
distanza visiva in J2 — si assestano entrambi fra il 52% e il 58%. Il fattore
limitante non è quindi la selezione degli stili. L'ipotesi che restava era **la
risoluzione**: lo stile pittorico è in larga parte texture e trattamento della
superficie, e a 64×64 la texture non sopravvive.

---

## J3 — stessi stili di J2, a 128×128

**Ipotesi sotto verifica:** se il limite è la risoluzione, raddoppiarla deve
migliorare il giudice in modo netto.

**Soglia dichiarata in anticipo:** accuratezza sopra 0,70 → si procede;
intorno a 0,60 → il problema è altrove.

**Accuratezza 0,623** · **entropia sui reali 0,719 nats (0,401 normalizzata)**
Commit `e834314` · 15 epoche · batch 64 · seed 1234 · validazione sullo split esterno.

### Esito ambivalente, e la soglia era sulla metrica sbagliata

L'accuratezza sale di 4,5 punti, da 0,578 a 0,623: un miglioramento reale ma lontano
dai dodici punti che la soglia richiedeva. Per il criterio dichiarato ci si
fermerebbe.

**Ma l'accuratezza non era la grandezza giusta da mettere a soglia.** Ciò da cui
dipende la sensibilità della metrica è il **pavimento dell'entropia**, cioè quanto il
giudice è già incerto sull'arte vera:

| | J2 (64px) | J3 (128px) | variazione |
|---|---|---|---|
| Accuratezza | 0,578 | 0,623 | +0,045 |
| Entropia sui reali (norm.) | 0,531 | **0,401** | **−0,130** |
| Spazio utile fino al soffitto | 0,469 | **0,599** | **+28%** |

Lo spazio in cui l'effetto della CAN può manifestarsi **cresce di oltre un quarto**.
È il guadagno che si cercava, ed è passato inosservato al criterio che ci si era dati:
un errore di impostazione da riportare, perché mostra che la scelta della metrica di
controllo va motivata quanto quella della metrica di risultato.

### Altre osservazioni

**L'overfitting resta.** La loss di addestramento scende da 1,43 a 0,58 mentre
l'accuratezza di validazione si assesta sopra l'epoca 12. Aumentare le epoche non
aiuta: se si volesse spingere oltre servirebbe augmentation o regolarizzazione, non
più tempo.

**Il costo della risoluzione è molto minore del previsto.** Quindici epoche in due
minuti, cioè 7,6 secondi per epoca a 128 pixel leggendo da `/dev/shm`. La stima
iniziale prevedeva un fattore 4-5 rispetto a 64: il fattore reale è molto più basso,
perché il collo di bottiglia resta l'accesso ai dati e non il calcolo.

### Cosa resta da misurare

Il tempo per epoca delle **GAN** a 128, che è un carico diverso da quello del giudice.
Da misurare con due epoche di `e3-dcgan-128` prima di impegnare ore:

```bash
python -m tesi_gan.cli train experiment=e3-dcgan-128 training.epochs=2 seed=99 \
  data.root=/dev/shm/processed_128 data.reference_root=/dev/shm/processed_test_128
```

Con quel numero la decisione se rifare l'impianto a 128 diventa aritmetica.

---

## Ciò che le tre iterazioni dimostrano insieme

Il fattore limitante **è** la risoluzione — l'ipotesi era corretta — ma il guadagno si
manifesta sull'incertezza del giudice più che sulla sua accuratezza. Anche a 128 pixel
il classificatore resta sotto la soglia di affidabilità che ci si era dati, e questo
non è un dettaglio implementativo: **una metrica basata su un classificatore non può
essere più fine della risoluzione a cui opera, e la classificazione di stile
pittorico è un problema difficile anche per un umano su immagini di 128 pixel.**

È l'osservazione da portare in tesi, con le tre iterazioni a supporto: due che
escludono la selezione degli stili come causa, una che quantifica l'effetto della
risoluzione.

## Verifica dell'effetto soffitto — superata

Il rischio da escludere prima di spendere il calcolo: se il giudice trovasse già
quasi massima l'entropia sulle immagini della **DCGAN**, la CAN non avrebbe spazio
per salire e le due condizioni darebbero lo stesso numero — non perché il meccanismo
non funzioni ma perché la metrica è satura.

**Misurato il 2026-08-03** con un run DCGAN di 20 epoche (`e1-dcgan-baseline`,
seed 1, commit `66f91f2`), valutato su 1.024 campioni.

| Riferimento | Entropia normalizzata |
|---|---|
| Immagini reali (split esterno) | 0,531 |
| **DCGAN, 20 epoche** | **0,601** |
| Soffitto teorico `log(6)` | 1,000 |

**La metrica non è satura.** La condizione di controllo si colloca 0,07 sopra il
pavimento dell'arte vera e 0,40 sotto il soffitto: lo spazio per osservare un
innalzamento dovuto al meccanismo di ambiguità c'è tutto.

**Il confondimento «generatore scarso = entropia massima» non morde**, ed è la
notizia migliore. Questo modello ha **FID 191,3**, cioè immagini visibilmente brutte
dopo sole 20 epoche, e il giudice le attribuisce comunque con una certa sicurezza. Se
il rumore informe bastasse a massimizzare l'entropia, qui si sarebbe visto.

**Attesa per il run completo:** a 100 epoche la DCGAN produrrà immagini più
attribuibili, quindi la sua entropia dovrebbe **scendere** verso 0,53, allargando la
forbice disponibile. Se invece salisse, andrebbe indagato.

Altre metriche del run di controllo, utili come riferimento per i run completi:
FID 191,3 · Inception Score 2,627 ± 0,175 · 1.024 campioni · FID calcolato contro lo
split esterno.

`style_entropy` risulta `null`: è la vecchia metrica basata sulla testa di stile del
discriminatore, non definita per la DCGAN. È il buco che ha motivato ADR-0005.
