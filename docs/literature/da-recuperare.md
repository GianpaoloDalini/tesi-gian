# Paper da recuperare in Zotero

> **Cos'è questo file.** Elenco dei paper emersi durante le sessioni di definizione
> dell'idea di tesi (dialogo aperto con Gian), non ancora importati in Zotero e non
> ancora presenti in `thesis/references/bibliography.bib` (che resta generato solo
> da Zotero, non va editato a mano). Una volta importato un paper, va tolto da qui e
> aggiunta la relativa scheda in `docs/literature/` seguendo `_template.md`.
>
> **Perché esiste.** `bibliography.bib` non si modifica a mano, quindi i paper
> trovati in una sessione di ricerca andrebbero persi se non registrati da qualche
> parte prima di essere importati in Zotero.
>
> **Aggiornamento 2026-09-14.** Questo file era disallineato: molti dei paper
> elencati sotto come "da recuperare" erano in realtà già stati recuperati e
> vivono come PDF in `~/Desktop/esami/TESI/` (libreria organizzata per temi,
> non collegata a questo repository). Le voci confermate presenti sono state
> tolte dall'elenco qui sotto — restano solo i paper ancora effettivamente
> mancanti. Nessuna scheda in `docs/literature/` è stata ancora compilata per
> nessuno dei paper recuperati: è il prossimo passo se si vuole seguire il
> workflow descritto nel README di questa cartella.
>
> **Paper tolti da questo elenco perché già recuperati** (con cartella in
> `TESI/`): Qi (2019) → `03_Condizioni_di_creativita_(CUORE)`; Langer, *Feeling
> and Form* (1953) → `00_Teorie...(CRITERI)` (resta da recuperare solo
> *Problems of Art*, 1957, vedi sotto); Berryman (2024) → `02_CAN...`;
> Coeckelbergh (2017) → `03_Condizioni...`; McCormack, Gifford & Hutchings
> (2019) → `03_Condizioni...`; Colton, Pease & Saunders (2018) →
> `00_Teorie...`; Hertzmann (2020) → `04_Estetica...`; Epstein, Levine, Rand &
> Rahwan (2020) → `05_Esperimenti_percettivi`; Cintas, Das, Speakman &
> Akinwande (2021) → `02_CAN...` (verificato: non ridondante con la metrica di
> entropia di stile già usata, propone un approccio diverso — scanning nello
> spazio delle attivazioni — utile come letteratura correlata); Franceschelli &
> Musolesi — **attenzione alla citazione**: nel PDF recuperato risulta
> pubblicato come *Creativity and Machine Learning: A Survey*, ACM Computing
> Surveys 56(11), art. 283, giugno 2024 (non solo il preprint arXiv 2104.02726
> del 2021) — usare la citazione 2024 su rivista, molto più forte per
> rispondere alla critica di "letteratura datata".
>
> **Aggiornamento 2026-09-17.** Hereu & Hu (2024), *Creative Portraiture* — recuperato, letto per intero e **scartato**: nessuna sede di pubblicazione/peer review rintracciabile (solo arXiv, email istituzionali da studenti, nessuna citazione rintracciabile), il tipo di fonte poco rigorosa contestato dal relatore. Vedi `docs/sinossi.md`, sezione Fase 1/materiale trasversale. Rimosso dalla tabella “filone tecnico GAN alta risoluzione vs Nano Banana” qui sotto, che di conseguenza è stata eliminata (era l'unica voce).

## Dal filone "creatività claim vs. casualità / estetica simbolica" — 2026-08-11

| Titolo | Autori (anno) | Venue | Perché | Accesso |
|---|---|---|---|---|
| Philosophy of Symbolic Forms | Cassirer (1923-1929) | libro | Precursore di Langer; fonda l'arte come "funzione simbolica" dell'uomo. Solo se serve la genealogia del concetto, non essenziale al primo giro. | da reperire |
| Problems of Art | Langer (1957) | libro | Seconda fonte primaria di Langer (la prima, *Feeling and Form* 1953, è già stata recuperata). Da leggere solo se l'argomento estetico richiede di andare oltre quanto già coperto da *Feeling and Form*. | da reperire (biblioteca/Zotero) |
| Generative AI doesn't "democratize creativity" | Furze (2024) | blog (leonfurze.com) | Contro-narrativa alla "democratizzazione". **Non è peer-reviewed** — dato il nuovo standard di rigore chiesto dal relatore, valutare se vale la pena recuperarlo o se è meglio ometterlo del tutto, sostituendolo con una fonte accademica equivalente. | Open web |

## Dal filone "locus della creativita': algoritmo vs uso umano" — 2026-08-11

| Titolo | Autori (anno) | Venue | Perché | Accesso |
|---|---|---|---|---|
| Artistic Autonomy in AI Art | Issak, Varshney (2022) | ICCC 2022 (arXiv 2111.04437) | Discute le GAN come sistemi "black box" che limitano l'autonomia artistica; propone un framework (Self-Determination Theory + Fundamental Limits of Creativity) secondo cui il valore deve venire dall'autonomia "recuperata" dall'artista, non dalla capacità della macchina. Sostituisce Haase/Pokutta (2024, giudicato fuori tema: nessun legame con l'arte, solo matematica/LLM). Background: Coordinated Science Laboratory, University of Illinois Urbana-Champaign (ingegneria/informatica, Varshney noto per ricerca su creatività computazionale). | **Recuperato 2026-09-18** → `fase-2-locus-della-creativita/` |
| Introducing a Scale for AI's Artistic Autonomy | Lamers (2025) | capitolo Springer, DOI 10.1007/978-981-95-4409-7_2 | Tassonomia a 5 livelli di autonomia artistica automatizzata, definiti da chi (artista umano o macchina) è responsabile di ciascuna fase del processo creativo — equivalente "in salsa arte" della tassonomia di Haase/Pokutta. Non cita esplicitamente GAN/CAN nei riferimenti verificati finora. Background: Creative Intelligence Lab, LIACS (Leiden Institute of Advanced Computer Science), Università di Leiden — informatico puro. | **Accesso chiuso** (Springer, verificato 2026-09-18): nessuna copia open access nel repository di Leiden (`scholarlypublications.universiteitleiden.nl/handle/1887/4282531` ha solo la scheda, non il PDF). Serve accesso istituzionale/biblioteca. [Springer](https://link.springer.com/chapter/10.1007/978-981-95-4409-7_2) |
| Co-creating art with generative artificial intelligence: Implications for artworks and artists | Messer (2024) | *Computers in Human Behavior: Artificial Humans* 2(1), art. 100056, Elsevier | 3 esperimenti, 560 soggetti: l'arte co-creata con AI è percepita come meno autentica, soprattutto se l'AI interviene nell'implementazione e non nell'ideazione. Verificato 2026-09-16: autore Uwe Messer, professore di Marketing, Universität der Bundeswehr München — background economico/marketing, non informatico, ma impianto empirico solido (stesso ruolo di Bellaiche/Chamberlain/Ragot nella bibliografia). | **Recuperato 2026-09-18** → `fase-2-locus-della-creativita/` |

## Dal filone "falsa rivendicazione di creativita' come problema etico" — 2026-08-11

**Aggiornamento 2026-09-18.** Tutte e quattro le fonti di questo filone sono state scaricate da Gian e spostate in `TESI/`: **Placani (2024)** → `fase-3-ondata-etica/`; **Calvo (2026)** e **Pearson, Dennis, Cheong (2026)** → `fase-4-oggi/` (rafforzano la fase più debole, entrambe recentissime — gennaio/2026); **Horton Jr, White, Iyengar (2023)** → `fase-2-locus-della-creativita/` (letteratura sul bias percettivo, in continuità con Chamberlain/Bellaiche). Background autori già verificati (vedi tabella sotto e `docs/sinossi.md`): Placani e Calvo umanistici puri (filosofia/etica dell'AI); Pearson e Dennis filosofi, Cheong tecnico/informatico (team bilanciato); Horton/White/Iyengar tutti Columbia Business School (psicologia del consumatore/marketing).

## Dal filone "training = ispirazione umana? l'obiezione della componente emotiva" — 2026-08-11

| Titolo | Autori (anno) | Venue | Perché | Accesso |
|---|---|---|---|---|
| Comparing AI Training to Human Learning Is Cartoonishly Absurd | | Copyright Alliance | Posizione critica sull'analogia training/ispirazione umana — di parte (lobby del copyright) ma riassume bene gli argomenti tecnici (scala, memorizzazione) da verificare con fonti più neutre. | Open web |
| Generative AI Training and Copyright Law | Dornis, Stober (2025) | arXiv 2502.15858 | Rassegna più equilibrata del dibattito giuridico, incluse le sentenze USA che si contraddicono sull'analogia con la lettura umana — fonte primaria per V-007. Verificato 2026-09-17: Tim Dornis, Professore, Institute of Legal Informatics, Leibniz Universität Hannover (giurista); Sebastian Stober, Professore, Faculty of Computer Science, Univ. Magdeburg (informatico). **Deciso 2026-09-17 (Gian): fuori tema** rispetto al nucleo creatività/GAN — appartiene al filone copyright, non prioritario per la tesi. Deprioritizzato, non recuperare per ora. | Open access |
| Copyright Office Weighs In on AI Training and Fair Use | Levi, Ghaemmaghami (2025) | Skadden (studio legale) | Sintesi dello stato dell'arte legale USA post-report dell'US Copyright Office. Non un paper accademico ma un "client alert" legale. Verificato 2026-09-17: Stuart D. Levi, Mana Ghaemmaghami — avvocati, Skadden Arps — pratica legale, non ricerca accademica. **Deciso 2026-09-17 (Gian): fuori tema**, stesso motivo della voce sopra. Deprioritizzato. | Open web |
| Toward Affective Interactions: E-Motions and Embodied Artificial Cognitive Systems | Scarinzi, Cañamero (2022) | *Frontiers in Psychology* 13:768416 | Fonda filosoficamente la distinzione proposta da Gian: "problema del symbol grounding", assenza di un soggetto per cui l'esperienza conti. Aggancio diretto a D-024. Verificato 2026-09-18: **è la stessa fonte discussa in precedenza come "Scarinzi-Cañamero"** (raccomandazione precedente: tenerla, mai confermata da Gian — risolto qui). Alfonsina Scarinzi, CY AS Institute for Advanced Studies (CY Cergy Paris Université) + Univ. Göttingen — filosofa/estetica, umanistico; Lola Cañamero, ETIS Lab (CY Cergy Paris Université) — robotica affettiva/sistemi cognitivi artificiali, tecnico. Team bilanciato, stesso profilo di Pearson/Dennis/Cheong. | Open access — [Frontiers](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.768416/full) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/35496207/) |

## Dal filone "Fase 0 - le GAN aprono il dibattito / caso Belamy" - 2026-09-16

**Aggiornamento 2026-09-18.** *Who is Edmond de Belamy?* — recuperato e spostato in `fase-0-gan-aprono-il-dibattito/`. Autore verificato: **Mikel Arbiza Goenaga**, Sinnergiak Social Innovation Center + Galapagos Studio (Donostia-San Sebastián) — background creative industries/innovazione sociale, non tecnico.

| Titolo | Autori (anno) | Venue | Perche' | Accesso |
|---|---|---|---|---|
| A Survey on Generative Adversarial Networks: Variants, Applications, and Training | Jabbar, Li, Omar (2021) | ACM Computing Surveys 54(8), art. 157, DOI 10.1145/3463475 | Introduzione tecnica a come funzionano le GAN, venue molto citata/autorevole - copre il bisogno di una fonte tecnica introduttiva per la Fase 0, complementare a Elgammal (2017) che presuppone gia' il funzionamento base. Autori verificati 2026-09-18 aprendo il PDF: College of Computer Science and Technology, Zhejiang University (Cina) — tecnico/informatico puro. | **Recuperato 2026-09-18** → `fase-0-gan-aprono-il-dibattito/` |

## Note

- **Aggiornamento 2026-09-18.** Tutte le fonti di questo elenco che erano
  state effettivamente decise (Placani, Calvo, Pearson/Dennis/Cheong,
  Horton/White/Iyengar, Arbiza-Goenaga, Messer, Issak-Varshney, Jabbar/Li/Omar)
  sono state recuperate e spostate nelle cartelle di fase — vedi
  `docs/sinossi.md` per note narrative e tabella background. Scarinzi &
  Cañamero (2022, "Toward Affective Interactions") è risultato essere la
  fonte già in elenco: stessa raccomandazione di tenerla, ora con autori
  verificati.
  **Resta aperto solo Lamers (2025)** — accesso chiuso (Springer, nessuna
  copia OA reperibile), Gian ha deciso 2026-09-18 di lasciarlo in sospeso
  per ora (non prioritario, non cita esplicitamente GAN/CAN).
- Furze (2024), il post del Copyright Alliance, Cassirer e Langer (1957) sono
  fonti secondarie/deboli o non essenziali al primo giro: valutare se
  recuperarle affatto o ometterle, invece di trattarle come "da recuperare"
  alla pari delle altre.
- Dornis-Stober (2025) e Levi-Ghaemmaghami (2025) restano deprioritizzati
  (fuori tema, decisione di Gian del 2026-09-17) — non recuperare per ora.
