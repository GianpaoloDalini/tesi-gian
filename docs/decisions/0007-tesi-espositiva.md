# ADR-0007 — Tesi espositiva invece di sperimentale

- **Data:** 2026-09-14
- **Stato:** Accettata
- **Decisore:** Gian, in accordo con quanto indicato dal relatore al primo ricevimento
- **Supera:** [ADR-0003](0003-impianto-sperimentale.md) (impianto sperimentale: confronto controllato DCGAN → CAN)

## Contesto

Al primo ricevimento (2026-09-14) il relatore ha indicato che la parte sperimentale
(DCGAN/CAN, E1-E6, e il restyling E8) non è più al centro del suo interesse: vuole
una tesi che ricostruisca come si è evoluta nel tempo l'argomentazione critica
contro la rivendicazione di creatività dei sistemi di IA generativa, usando le
Creative Adversarial Networks (Elgammal et al., 2017) come caso di partenza
esemplare — non come esperimento da riprodurre.

Non è una richiesta del tutto nuova: la proposta originale al relatore
(`thesis/extra/proposta-relatore.tex`) affermava già che "l'esperimento non serve a
stabilire se questi sistemi siano creativi: a quella domanda risponde il vaglio
teorico". Il registro decisioni (D-010→D-026) aveva però progressivamente spostato
il baricentro, trattando il confronto DCGAN/CAN come "il risultato scientifico
quantitativo della tesi" — è questa cornice, non l'idea originale di Gian, ad
essere corretta dal relatore.

## Alternative valutate

| Opzione | Vantaggi | Svantaggi |
|---|---|---|
| A — Mantenere l'impianto sperimentale (ADR-0003) e aggiungere solo teoria aggiornata | Nessun lavoro già fatto va rifatto | Non risponde a quanto chiesto esplicitamente dal relatore: il centro resterebbe l'esperimento |
| B — Tesi puramente espositiva/argomentativa, CAN come caso citato dalla letteratura, DCGAN/CAN/E8 fuori dal documento | Risponde direttamente alla richiesta del relatore; recupera il baricentro della proposta originale | Nessun esperimento originale nel documento consegnato; da verificare se il regolamento del corso lo consente (V-012) |
| C — Tesi ibrida: capitolo critico centrale + capitolo sperimentale ridotto come appendice | Compromesso, mantiene visibile il lavoro tecnico | Il relatore ha detto esplicitamente che la parte sperimentale "non interessa": rischio di andare contro la sua indicazione |

## Decisione

**Tesi espositiva.** Le Creative Adversarial Networks restano il caso di partenza
— per la rivendicazione esplicita nel nome e nella funzione di perdita — ma
discusso come caso di letteratura (Elgammal et al., 2017), non riprodotto
sperimentalmente da Gian nel corpo del documento. Il nucleo della tesi diventa la
ricostruzione **cronologica** (non tematica: è la forma chiesta esplicitamente dal
relatore, "evoluta nel tempo") di come l'argomentazione critica contro la
rivendicazione di creatività si è evoluta dal 2017 a oggi (D-028).

**Il lavoro DCGAN/CAN già svolto (E1-E6, D-010→D-026) e il restyling E8 escono per
ora dal documento di tesi.** Restano nel repository come lavoro personale di Gian:
in parallelo continua a sviluppare E8 (già preparato, ADR-0006) con l'obiettivo di
mostrare al relatore un risultato visivo migliore e verificare se questo lo porta a
riconsiderare l'inclusione di una componente sperimentale. È una scommessa separata
dal documento, non una sua precondizione: la tesi espositiva è consegnabile
indipendentemente dall'esito di E8.

## Conseguenze

### Sulla struttura della tesi

- **ADR-0003 è superata**, non riscritta (per esplicita clausola della stessa ADR-0003).
- I capitoli `04-metodologia`, `05-implementazione`, `06-risultati` e le appendici
  `A-iperparametri`, `B-riproducibilita` sono spostati in `thesis/capitoli-sospesi/`
  (`mv`, non `rm` — vedi il README in quella cartella) e tolti da `thesis/main.tex`.
- `thesis/capitoli/03-stato-arte.tex` è rinominato
  `03-evoluzione-argomentazione-critica.tex` e riorganizzato cronologicamente.
- `07-discussione.tex` e `08-conclusioni.tex` rinumerati `04` e `05`.
- La domanda di ricerca (capitolo 1) è storico-critica, non più empirica.

### Sulle questioni aperte

- **Q2, Q5, Q6** (impianto sperimentale, formulazione della metrica, studio
  percettivo) non sono più applicabili nella forma attuale: non c'è più un
  esperimento nel documento a cui si riferiscano. Non si cancellano, si chiudono
  con nota in `registro-decisioni.md`.
- **Q3** (peso tecnica/etica) si scioglie di fatto verso il polo teorico/etico.
- **Nuova V-012**: verificare se il regolamento del corso LM-32 richiede una
  componente sperimentale/progettuale per la tesi magistrale anche quando il
  relatore la vuole espositiva — controllo amministrativo, da fare prima di
  consolidare la scelta.

### Sul lavoro tecnico già fatto

Codice, configurazioni ed esperimenti (`src/`, `configs/`, `experiments/`) restano
intatti nel repository: non è lavoro perso, è lavoro che non entra (per ora) nel
documento consegnato. Se E8 produce un risultato che convince il relatore a
riaprire la componente sperimentale, questa ADR va marcata `superata` a sua volta,
non riscritta.

## Questioni che restano aperte

- V-012 (sopra).
- Se e come nominare il lavoro sperimentale personale nelle conclusioni, come
  sviluppo futuro/parallelo (da decidere in fase di stesura).
- Titolo della tesi (`thesis/metadata.tex`): il titolo attuale nomina esplicitamente
  GAN e CAN come oggetto di "analisi" — da rivedere con Gian, visto che la tesi non
  le analizza più sperimentalmente ma le usa come caso di partenza storico. Non
  modificato in questa ADR.
