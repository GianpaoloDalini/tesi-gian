# ADR-0003 — Impianto sperimentale

- **Data:** 2026-08-02
- **Stato:** **Decisa** — da ratificare col relatore al primo ricevimento utile
- **Decisore:** Gian
- **Supera:** lo stato «aperta» del 2026-07-31

## Contesto

L'impianto determina dataset, architettura, metriche, fabbisogno di calcolo e durata
del lavoro. Restava aperto in attesa di due informazioni, entrambe ora acquisite:

- **Sessione di laurea:** autunnale, discussione magistrale **2 ottobre 2026**,
  caricamento dell'elaborato entro il **21 settembre 2026** (vedi V-006). Restano
  circa sette settimane, di cui agosto con relatore e segreteria poco raggiungibili.
- **Calcolo:** GPU a pagamento su servizio online.

Il vincolo temporale è la variabile dominante: esclude qualunque impianto che
richieda più di due addestramenti o una risoluzione superiore a 64×64.

## Alternative valutate

| Opzione | Vantaggi | Svantaggi |
|---|---|---|
| A — Replica della CAN di Elgammal et al. (2017) su WikiArt | Riferimento solido, risultato atteso noto | Contributo originale scarso se ci si ferma alla replica |
| B — Baseline DCGAN + variante originale | Contributo proprio, calcolo contenuto | Rischio di risultato negativo o non significativo |
| C — Esperimento come caso di studio a supporto dell'analisi etica | Calcolo minimo, coerente con l'area del relatore | Rischio di giudizio di leggerezza tecnica per una LM-32 |

## Decisione

**Esperimento comparativo controllato a due condizioni: DCGAN → CAN.**

Si addestrano due modelli in sequenza sullo stesso dataset, con lo stesso generatore,
la stessa backbone di discriminatore, gli stessi iperparametri di ottimizzazione, lo
stesso seed e lo stesso numero di epoche. **L'unica variabile indipendente è la
funzione di perdita.**

| | DCGAN (condizione di controllo) | CAN (condizione sperimentale) |
|---|---|---|
| Generatore | identico | identico |
| Backbone del discriminatore | identica | identica |
| Testa reale/falso | sì | sì |
| Testa di classificazione dello stile | **assente** | **presente**, K classi |
| Loss del discriminatore | avversaria | avversaria + cross-entropy sullo stile (solo immagini reali) |
| Loss del generatore | avversaria | avversaria + termine di ambiguità stilistica |

Non è né la pura opzione A né la pura B: è una **replica ridotta con disegno
sperimentale esplicito**. Il contributo non sta nell'inventare un'architettura, sta
nell'isolare rigorosamente l'effetto del meccanismo di ambiguità stilistica e nel
misurare la distanza tra ciò che quel meccanismo produce e ciò che la letteratura
afferma che produca.

### Perché questa e non le altre

- **Rispetto ad A pura:** la replica integrale della CAN richiederebbe risoluzione
  256×256 e giorni di GPU. Ridurre a 64×64 e dichiararlo è onesto; fingere una
  replica fedele non lo sarebbe.
- **Rispetto a B:** una variante architetturale originale, con sette settimane e un
  solo tentativo disponibile, ha alta probabilità di produrre un risultato non
  significativo, e un risultato non significativo su una variante propria è molto più
  difficile da difendere di una replica ben eseguita.
- **Rispetto a C:** l'esperimento resta tecnicamente sostanziale, ma la componente
  etica non viene sacrificata: entra nel capitolo di discussione con materiale
  empirico proprio invece che come commento generico.

### Il punto di forza metodologico

Una sola variabile indipendente. Qualunque differenza osservata tra le due condizioni
è attribuibile al meccanismo di ambiguità stilistica e a nient'altro. È il motivo per
cui i due modelli **devono** condividere il codice: se DCGAN e CAN fossero due
implementazioni separate, ogni differenza sarebbe confusa con differenze di
implementazione. Questa considerazione vincola l'architettura del codice, non solo
l'esperimento.

## Conseguenze

### Sul codice

- Un solo generatore, un solo discriminatore parametrico (`style_head: bool`).
- Un solo training loop; la loss è selezionata dalla configurazione.
- Il dataset **deve** esporre le etichette di stile: senza, la CAN non è addestrabile.

### Sulle metriche

Tre livelli, con dichiarazione esplicita di cosa ciascuno misura e cosa **non** misura:

| Metrica | Cosa misura | Cosa NON misura |
|---|---|---|
| FID | distanza tra le distribuzioni di feature di reali e generati | creatività, novità, valore estetico |
| Inception Score | fedeltà e varietà secondo un classificatore ImageNet | creatività; per giunta su un classificatore addestrato su fotografie, non su dipinti |
| Entropia della posterior di stile | quanto l'output è stilisticamente ambiguo per il discriminatore | se l'ambiguità sia percepita come tale da un umano |
| Studio percettivo leggero | giudizio umano su gradevolezza e attribuzione | rappresentatività statistica (campione di convenienza) |

**L'ipotesi attesa è che la CAN peggiori il FID e aumenti l'entropia di stile.** Se
si verifica, non è un fallimento: è la dimostrazione empirica che le metriche di
fedeltà e l'obiettivo di creatività sono in tensione, che è esattamente l'argomento
del capitolo di discussione.

### Sulla pianificazione

Vedi `docs/project-plan.md` §8. In sintesi: pipeline e primo run entro il 9 agosto,
due run definitivi entro il 23 agosto, studio percettivo entro il 6 settembre,
stesura fino al 21 settembre.

## Questioni che restano aperte

- **Q4 — dataset e licenza.** Vedi ADR-0004.
- **Q3 — peso relativo tecnica/etica.** Da concordare col relatore; l'impianto scelto
  è compatibile con entrambi gli sbilanciamenti.
- **Ratifica del relatore.** Questa decisione è stata presa senza di lui per non
  bloccare il lavoro durante agosto. Va portata al primo ricevimento e verbalizzata
  in `docs/meetings/`. Se il relatore la rovescia, questo ADR va marcato `superato`,
  non riscritto.
