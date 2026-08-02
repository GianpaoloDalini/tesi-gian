# ADR-0004 — Dataset

- **Data:** 2026-08-02, riscritta il 2026-08-03
- **Stato:** **Decisa**
- **Decisore:** Gian
- **Dipende da:** [ADR-0003](0003-impianto-sperimentale.md)

## Contesto

ADR-0003 impone un vincolo non negoziabile: **il dataset deve esporre etichette di
stile**. Senza, la testa di classificazione della CAN non è addestrabile e l'intero
esperimento comparativo cade. Questo esclude a priori le collezioni di sole immagini
senza metadati art-storici.

Il secondo vincolo emerge dall'impianto: il sottoinsieme dev'essere **bilanciato**.
Con classi sbilanciate la testa di stile impara la distribuzione a priori invece
dello stile, e l'entropia della posterior — la metrica su cui si regge il confronto
fra le due condizioni — diventa ininterpretabile.

Il terzo vincolo è di coerenza. Una tesi che discute le implicazioni etiche
dell'addestramento di modelli generativi su opere d'arte non può usare un dataset
senza averne esaminato i termini.

## Alternative valutate

| Opzione | Etichette di stile | Bilanciamento | Termini dichiarati |
|---|---|---|---|
| **ArtBench-10** | 10 stili | **bilanciato per costruzione**, 5.000 train + 1.000 test per stile | *Fair Use* (autodichiarazione) |
| WikiArt / ArtGAN refined | 27 stili | fortemente sbilanciato, coda lunga | «non-commercial research purpose» + ToU di WikiArt.org |
| `huggan/wikiart` su Hugging Face | 27 stili | sbilanciato | `unknown`, «Data files © Original Authors» |
| The Met Open Access | **no** — ha *culture*, *period*, *classification* | — | CC0, inequivocabile |
| Art Institute of Chicago | parziale | — | mista |
| Art500k, OmniArt, Painter by Numbers | sì | sbilanciati | non verificati |

## Decisione

**ArtBench-10**, ristretto a **sei stili**:

`ukiyo_e`, `renaissance`, `baroque`, `romanticism`, `realism`, `impressionism`

Versione ImageFolder a 256×256, ridimensionata a 64×64 in fase di caricamento.
Dimensione risultante: **30.000 immagini di training**, 5.000 per stile, bilanciate
senza bisogno di sottocampionare.

### Perché ArtBench e non WikiArt

1. **Bilanciato per costruzione.** Con WikiArt la classe meno popolata avrebbe
   determinato la dimensione di tutte le altre: bilanciando su Ukiyo-e si sarebbe
   scesi attorno alle 4.500 immagini totali. Con ArtBench se ne hanno 30.000.
2. **Annotazioni pulite e procedura standardizzata.** Le etichette di WikiArt sono
   notoriamente rumorose, e sarebbe stato un limite da dichiarare.
3. **Esistono benchmark pubblicati sullo stesso dataset.** Gli autori riportano FID,
   IS, precision, recall e KID per GAN, VAE e modelli di diffusione. Questo
   trasforma «il mio FID vale X» in «il mio FID vale X contro Y riportato in
   letteratura sullo stesso dataset», che in una tesi vale molto di più.
4. **Formato già compatibile.** ImageFolder di torchvision, che è ciò che
   `tesi_gan.data.dataset` usa già.

### Perché questi sei stili

Due criteri congiunti.

**Pubblico dominio.** Tutti e sei appartengono a movimenti i cui autori sono morti
da oltre settant'anni. Dei dieci stili di ArtBench l'unico ancora sotto copyright è
il **Surrealismo** (Dalí 1989, Magritte 1967, Ernst 1976), ed è escluso.
*Questa valutazione è basata sulle date di morte tipiche degli autori di ciascun
movimento e non è una verifica legale.*

**Coerenza art-storica.** Renaissance → Baroque → Romanticism → Realism →
Impressionism è la sequenza cronologica canonica della pittura occidentale;
l'Ukiyo-e fa da contrappunto non occidentale. Non è un insieme arbitrario da
giustificare, è un arco — e l'Ukiyo-e ha influenzato direttamente gli impressionisti
attraverso il giapponismo, il che lega il contrappunto al resto della sequenza
invece di lasciarlo appeso.

### Limite noto di questa selezione

**Barocco, Romanticismo e Realismo condividono la stessa famiglia visiva:** pittura
a olio a dominante scura. Il discriminatore farà più fatica a separarli di quanta ne
farebbe con stili più lontani, e questo comprime la componente di ambiguità
attribuibile a quelle tre classi.

Non è un errore ma un costo consapevole della coerenza cronologica, e **si misura**:
la matrice di confusione della testa di stile sui dati reali mostra esattamente quali
classi vengono confuse. Va prodotta e commentata, non nascosta. Se il Barocco viene
sistematicamente scambiato per Realismo, l'entropia della posterior va letta alla
luce di quel fatto.

## Sui termini d'uso

ArtBench dichiara una **«Fair Use license»**. È bene essere precisi su cosa significhi,
perché è materiale per il capitolo di discussione: *fair use* è un'eccezione del
diritto d'autore statunitense che si valuta caso per caso, non un permesso concesso
da un titolare. Gli autori del dataset stanno **affermando una posizione giuridica**,
non trasmettendo una licenza.

Il quadro complessivo emerso dalla ricognizione è di per sé un risultato da riportare:

| Fonte | Cosa dichiara sullo stesso materiale |
|---|---|
| ArtBench-10 | «Fair Use license» |
| WikiArt refined (ArtGAN) | «can be used only for non-commercial research purpose» |
| `huggan/wikiart` (Hugging Face) | `license: unknown`, «Data files © Original Authors» |

Tre fonti autorevoli danno tre qualificazioni giuridiche diverse a materiale in larga
parte sovrapposto. **I dataset con licenza limpida (Met, Rijksmuseum) non hanno le
etichette di stile; quelli con le etichette di stile non hanno licenza limpida.** Non
è una coincidenza: è la struttura del campo, e spiega perché la ricerca in creatività
computazionale poggi su fondamenta giuridiche fragili. Rilevarlo, con l'evidenza
documentale, è un contributo critico originale che non costa un'ora di GPU.

Rileva inoltre, per una tesi italiana:

- **Direttiva UE 2019/790, art. 14:** le riproduzioni fedeli di opere d'arte visiva
  di pubblico dominio non sono a loro volta protette. Rafforza la scelta dei sei
  stili.
- **Codice dei beni culturali, artt. 107-108:** prevede canoni per la riproduzione di
  beni culturali italiani, in tensione con la direttiva. È una peculiarità nazionale
  dibattuta e per questa tesi è merito, non ostacolo.

*Nessuno dei due punti è consulenza legale: vanno verificati con una fonte competente
prima di affermarli in tesi.*

## Conseguenze

- `configs/data/artbench.yaml` diventa la configurazione di riferimento.
  `configs/data/wikiart.yaml` resta come documentazione dell'alternativa scartata.
- `model.num_styles` vale **6**; l'entropia della posterior si normalizza su log(6).
  Il codice ricava comunque il numero dai dati e rifiuta configurazioni incoerenti.
- Le immagini non entrano nel repository (CLAUDE.md §2.5) e non vengono
  ridistribuite, né come dati né dentro i checkpoint.
- Va prodotta la **matrice di confusione della testa di stile** sui dati reali, per
  quantificare il limite dichiarato sopra.
- Provenienza esatta, versione scaricata, data e conteggi vanno in `data/README.md` e
  nell'appendice sulla riproducibilità.

## Percorso decisionale

La prima stesura di questo ADR sceglieva un sottoinsieme di WikiArt. È stata
rovesciata il 2026-08-03 dopo aver individuato ArtBench-10, che risolve il problema
del bilanciamento che si stava tentando di aggirare a mano. La strada scartata resta
documentata qui e in `src/tesi_gan/data/inventory.py`, che serviva a misurare lo
sbilanciamento di WikiArt: **il confronto fra i due dataset è materiale per il
capitolo di metodologia**, non lavoro sprecato.

## Citazione

```
Liao, Li, Liu, Keutzer — The ArtBench Dataset: Benchmarking Generative Models
with Artworks. arXiv:2206.11404, 2022. github.com/liaopeiyuan/artbench
```

% TODO[CITE]: importare `liao2022artbench` in Zotero e riesportare
`bibliography.bib`. Finché la voce non esiste, non usare `\parencite{}` per ArtBench
nel testo (CLAUDE.md §2.1).
