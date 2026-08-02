# ADR-0004 — Dataset

- **Data:** 2026-08-02
- **Stato:** Criterio deciso il 2026-08-03; 🔶 lista degli stili ancora aperta; subordinata a V-007
- **Decisore:** Gian
- **Dipende da:** [ADR-0003](0003-impianto-sperimentale.md)

## Contesto

ADR-0003 impone un vincolo non negoziabile: **il dataset deve esporre etichette di
stile**. Senza di esse la testa di classificazione della CAN non è addestrabile e
l'intero esperimento comparativo cade. Questo esclude a priori qualunque collezione
di sole immagini senza metadati art-storici.

Il secondo vincolo è temporale: sette settimane. Costruire un dataset da zero
(scraping, pulizia, etichettatura) consumerebbe da solo il tempo disponibile.

Il terzo vincolo è di coerenza. Una tesi che discute le implicazioni etiche
dell'addestramento di modelli generativi su opere d'arte non può usare un dataset
senza averne verificato i termini. Sarebbe il rilievo più facile che la commissione
possa muovere, e sarebbe meritato.

## Alternative valutate

| Opzione | Etichette di stile | Licenza | Costo di preparazione |
|---|---|---|---|
| **WikiArt** (sottoinsieme) | 27 classi di stile art-storico | ambigua: opere in gran parte sotto copyright, ToS del sito restrittive sulla ridistribuzione | basso |
| **The Met Open Access** | no — ha *culture*, *period*, *classification*, non lo stile art-storico | CC0, inequivocabile | medio, ma le etichette non sono quelle che serve |
| **Art Institute of Chicago API** | parziale, tramite *style_title* su una frazione del catalogo | mista, public domain solo su parte del catalogo | alto |
| Dataset costruito ad hoc | da definire | da definire | proibitivo nei tempi |

## Decisione

**Sottoinsieme di WikiArt**, ristretto a un numero limitato di stili
(indicativamente da 5 a 10 classi ben popolate e visivamente distinte),
ridimensionato a 64×64, con queste condizioni vincolanti:

1. **Le immagini non entrano nel repository** (già imposto da CLAUDE.md §2.5). Si
   scaricano con uno script versionato e documentato.
2. **Nessuna ridistribuzione.** Né il dataset né i checkpoint che potrebbero
   contenerne traccia vengono pubblicati.
3. **Uso esclusivamente di ricerca**, dichiarato nell'elaborato.
4. **La questione della licenza viene dichiarata nella tesi**, non nascosta.

### Sul punto 4

Questa è la scelta metodologicamente più importante di questo ADR. La tensione tra
«il dataset standard del settore è WikiArt» e «WikiArt contiene opere sotto
copyright» **non è un problema da aggirare: è materiale primario per il capitolo di
discussione.**

La tesi si trova nella posizione di dover usare, per replicare un lavoro di
riferimento, esattamente il tipo di dataset le cui implicazioni etiche discute. Dirlo
esplicitamente — con l'analisi di cosa questo comporta per la riproducibilità della
ricerca in creatività computazionale — vale più di qualunque risultato numerico che
l'esperimento possa produrre. Tacerlo, invece, rende l'intera componente etica non
credibile.

Elgammal et al. hanno usato WikiArt senza discuterne i termini. Rilevarlo è un
contributo critico originale, e non costa un'ora di GPU.

## Riserva

### V-007 — Termini d'uso di WikiArt 🔴
Prima del download vanno letti i termini d'uso effettivi della fonte da cui si
scarica, e va verificato se l'uso previsto (addestramento di un modello generativo a
fini di ricerca, senza ridistribuzione di dati né di pesi) vi rientri. **Se la
verifica dà esito negativo, questa decisione decade** e si ripiega su The Met Open
Access con etichette derivate da *culture* o *period* invece che dallo stile: la
CAN resterebbe addestrabile, con una nota metodologica sul fatto che le classi non
sono stilistiche in senso art-storico.

Questa verifica la fa Gian, non l'assistente: richiede di leggere i termini alla
fonte e di assumersene la responsabilità.

## Conseguenze

- `configs/data/wikiart.yaml` sostituisce `placeholder.yaml` come configurazione di
  riferimento; `placeholder.yaml` resta come esempio minimo per gli smoke test.
- Il numero di classi di stile diventa un iperparametro condiviso tra dataset e
  modello: `model.num_styles` deve coincidere con le classi effettivamente presenti.
  Il codice lo verifica a runtime invece di fidarsi della configurazione.
- La provenienza esatta (URL, data di download, numero di immagini per classe) va
  registrata in `data/README.md` e ripresa nell'appendice sulla riproducibilità.
