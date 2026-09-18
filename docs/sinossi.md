# Sinossi — evoluzione dell'argomentazione critica

> File di lavoro, non testo di tesi. Elenco delle tematiche discusse passo
> passo, con lo stato di ciascuna. Confluisce nello scheletro del capitolo 3
> (`thesis/capitoli/03-evoluzione-argomentazione-critica.tex`) e nella
> discussione (cap. 4). Si aggiorna a ogni sessione di brainstorming; non
> sostituisce il registro decisioni (`docs/registro-decisioni.md`), che resta
> la fonte delle decisioni formali (D-NNN, ADR).

## Legenda stato
🔲 da sviluppare · 🟡 impostato/abbozzato · 🟢 solido, pronto per la stesura

## Mappa cronologica (bozza di Gian, 2026-09-14)

> **Nota strutturale (2026-09-18, decisione di Gian).** Nel capitolo di tesi
> vero e proprio ci saranno **4 fasi argomentative**, non 5: "Fase 4 — oggi"
> non ha senso scorporata come tappa a se stante nell'argomentazione (lo ha
> confermato anche nella bozza di mail al relatore, che elenca 4 punti). Un
> articolo recente che si collega tematicamente a una fase precedente va
> discusso li, non isolato in una quinta fase cronologica fittizia.
> **A livello di cartelle in `TESI/` la sistemazione resta invariata (5
> cartelle, `fase-0-...` → `fase-4-oggi/`)**: `fase-4-oggi/` resta la casa
> pratica per le fonti più recenti non ancora ricollegate a una fase
> precedente. Quando si scrive il capitolo, ogni fonte li dentro
> (Franceschelli/Musolesi, Calvo, Pearson/Dennis/Cheong) va assegnata al
> punto argomentativo a cui appartiene tematicamente (es. Calvo e Placani
> sono chiaramente lo stesso filone etico/Fase 3 anche se in cartelle
> diverse), non introdotta come "quinta fase".

### Fase 0 — le GAN aprono il dibattito 🟡
- Le GAN (Goodfellow et al., 2014) sono stato dell'arte per un periodo breve;
  con loro si apre il dibattito su "AI art" e creatività artificiale.
- **Punto di ingresso pubblico individuato e verificato (2026-09-15):**
  *Edmond de Belamy*, opera del collettivo parigino **Obvious** (Hugo
  Caselles-Dupré, Pierre Fautrel, Gauthier Vernier), generata da una GAN
  (non una CAN) addestrata su 15.000 ritratti da WikiArt, con codice
  open-source di Robbie Barrat (allora diciannovenne), forkato da un
  repository di Soumith Chintala. Venduta da Christie's a New York il 25
  ottobre 2018 per **432.500 $** contro una stima di 7.000-10.000 $.
  Fonte: [Wikipedia, "Edmond de Belamy"](https://en.wikipedia.org/wiki/Edmond_de_Belamy).
- **Nota cronologica**: la vendita è di un anno DOPO il paper delle CAN
  (giugno 2017), non prima — sul piano tecnico-accademico l'ordine resta
  GAN (2014) → CAN (2017), ma è Belamy a portare il dibattito fuori dagli
  ambienti accademici, nel grande pubblico.
- **Controversia principale: non "è arte?" in astratto, ma attribuzione e
  autorialità.** Robbie Barrat protestò pubblicamente lo stesso giorno della
  vendita per il credito non riconosciuto; il critico Mario Klingemann
  disse che "probabilmente il 90% del lavoro vero" era di Barrat. Il critico
  Jonathan Jones mise in discussione se l'opera costituisse arte genuina.
  È un filone diverso ma collegato a quello etico (Fase 3): non la
  creatività della macchina in sé, ma chi merita il credito quando una GAN
  è nel mezzo.
- **Riferimento incrociato con la Fase 2**: McCormack, Gifford, Hutchings
  (2019), in `fase-2-locus-della-creativita/`, ha materiale primario
  aggiuntivo sul caso Belamy/Barrat (screenshot del tweet di Barrat).
- **Tenuta (2026-09-16), con una precisazione**: Hertzmann (2020), *Visual
  Indeterminacy in GAN Art* (Adobe Research; poi Leonardo/SIGGRAPH Art
  Papers), in `fase-0-gan-aprono-il-dibattito/`. Spiega tecnicamente
  l'estetica tipica delle GAN dell'epoca (2017-2019) col concetto di
  "indeterminatezza visiva" (Pepperell): immagini che sembrano coerenti ma
  non ammettono un'interpretazione spaziale stabile. Nota esplicitamente che
  *Edmond de Belamy* non ne è un buon esempio ("sembra solo sfocato").
  Propone la curva della "Uncanny Ridge": l'indeterminatezza è massima nei
  modelli "nel punto debole" (es. BigGAN) e diminuisce sia nei modelli
  peggiori sia in quelli migliori (StyleGAN sui volti) — **ipotesi del 2020
  confermata dai fatti**: oggi, con modelli indistinguibili, la previsione
  si è avverata. Non è quindi una fonte datata nel senso problematico, ma
  un ponte già pronto verso la Fase 4 (vedi sotto). Background: Aaron
  Hertzmann, ricercatore di computer graphics, Adobe Research — tecnico.
- **Tenuta (2026-09-17)**: Barale (2022), *Latent Spaces: What AI Art Can Tell Us About Aesthetic Experience* (da un talk alla conferenza “L’Expérience Esthétique”, Société Française d’Esthétique, 2021), in `fase-0-gan-aprono-il-dibattito/`. Analizza i contorni sfumati e l’incertezza oggettuale tipica delle immagini GAN come banco di prova per la teoria dell’esperienza estetica (richiama Talon-Hugon, *L’art victime de l’esthétique*); definisce l’arte GAN uno “specchio perturbante” degli sforzi classificatori umani. Collocata in Fase 0 (non in Fase 3, pur essendo del 2022) per continuità tematica con Hertzmann (indeterminatezza visiva delle GAN), non per l’ondata etica/antropomorfizzazione a cui non appartiene. Background: Alice Barale, ricercatrice presso l’Università degli Studi di Milano, settore M-FIL/04 (Estetica) — umanistico puro. Scartati nello stesso giro: Aris, Moosavand, Nosrati (2023) (troppo generico, non specifico GAN/CAN; background misto media studies/ingegneria civile) e Manovich (2018), *AI Aesthetics* (framework di “cultural AI” su scala industriale, non specifico GAN/CAN, pur con un background eccezionalmente ibrido tecnico+umanistico).
- **Tenuta (2026-09-17)**: Barale (2021), *“Who inspires who?” Aesthetics in front of AI art* (Philosophical Inquiries IX, 2), stessa autrice di *Latent Spaces*, in `fase-0-gan-aprono-il-dibattito/`. Parte anch'essa dal caso Belamy/Christie's; propone una “mossa beniaminiana” (Walter Benjamin, *L’opera d’arte nell’epoca della sua riproducibilità tecnica* — aura, riproducibilità tecnica) per spostare la domanda da “l’AI può essere creativa?” a “cosa dice l’AI sulla creatività e il suo ruolo nell’arte?”; ricostruisce anche la genesi tecnica di DeepDream (Mordvintsev, Tyka, gruppo AMI a Google) utile come sfondo storico per l'apertura del dibattito. Background: identico a Barale (2022) — umanistico puro.

### Fase 1 — 2017: le CAN e la rivendicazione esplicita 🟡
- Elgammal et al. (2017): l'ambiguità di stile come proxy di creatività,
  rivendicazione esplicita nel nome e nella funzione di perdita.
- **Prima obiezione trovata e verificata (2026-09-15), quasi immediata:**
  Ben Snell, ["A review of Creative Adversarial Networks"](https://bensnell.medium.com/a-review-of-creative-adversarial-networks-a2a5e8bf01a2),
  Medium, 7 novembre 2017 — pochi mesi dopo il preprint. Quattro obiezioni:
  1. *Interpolazione, non innovazione*: la CAN cerca "spazi non rappresentati"
     TRA gli stili esistenti, non crea davvero qualcosa di nuovo — vicino
     alla distinzione di Boden fra creatività esplorativa/combinatoria e
     quella trasformazionale (la CAN resterebbe nella prima).
  2. *Fondamento psicologico ristretto*: la CAN si basa su teorie
     dell'arousal potential (Berlyne, Wundt, Martindale) che riducono l'arte
     alla sola dimensione percettiva, ignorando quella concettuale, sociale
     ed espressiva — stesso bersaglio, angolo diverso, dell'obiezione di
     Langer già usata da Gian in `thesis/extra/proposta-relatore.tex`.
  3. *Manca la capacità concettuale*: la macchina resta confinata
     nell'"orizzonte percettivo", senza comprensione emotiva o concettuale.
  4. *Valutazione empirica debole*: pochi soggetti Mechanical Turk, rigore
     insufficiente — un parallelo diretto con quello che Gian ha già
     trovato per conto suo (D-026, giudice interno vs esterno): anche la
     critica "esterna" del 2017 puntava il dito sulla debolezza della
     valutazione empirica del paper originale.
- **Verificato (2026-09-16): nessuna risposta pubblica diretta di Elgammal a
  Snell.** Nessuna citazione nominale, nessun articolo di replica puntuale
  trovato. La difesa più vicina resta **Mazzone & Elgammal (2019)** (già
  in `fase-1-can-2017/`): affronta le stesse categorie di obiezioni
  (creatività autentica vs. imitazione, scetticismo/"technophobia" del
  pubblico, debolezza della valutazione percettiva) ma in chiave generale,
  senza mai nominare Snell o rispondere punto per punto.
- **Tenuta (2026-09-17)**: Berryman (2024), *Creativity and Style in GAN and AI Art: Some Art-historical Reflections* (Philosophy & Technology), in `fase-1-can-2017/`. Seconda critica diretta alla rivendicazione della CAN (Elgammal et al., 2017) di “creare stili artistici originali”, stavolta da prospettiva storico-artistica anziché psicologica e quasi vent'anni dopo Snell: un modello meccanico dello sviluppo artistico basato solo sull'autonomia dello stile ripristina acriticamente una visione formalista della storia dell'arte e un “modernismo storico” stile-centrico. Già in dialogo con fonti tenute altrove (cita Coeckelbergh, Hertzmann, McCormack et al., Colton, Epstein et al.). **Riferimento incrociato con la Fase 4**: pubblicato nel 2024, utile anche come voce recente nella sezione sullo stato attuale del dibattito. Background: Jim Berryman, School of Humanities, University of Glasgow — storico dell'arte (lavora su storiografia marxista dell'arte, Frederick Antal) — umanistico puro.
- **Tenuta (2026-09-17)**: Langer (1953), *Feeling and Form: A Theory of Art* [libro], in `fase-1-can-2017/` — già individuata come fonte in `02-arte.tex` (bozza/fonte superata nell'impostazione ma non nel contenuto). Teoria: l'arte come “forma imbevuta di sentimento”, un simbolo espressivo che rende percepibile la forma del sentimento umano — base per l'argomento dell'assenza di sentimento nel processo generativo come obiezione all'arte-AI. Background: Susanne K. Langer, filosofa dell'estetica e della simbolizzazione (allieva/influenzata da Ernst Cassirer) — umanistico puro.
- **Scartati (2026-09-17)**: Miller (2019), *The Artist in the Machine: The World of AI-Powered Creativity* [libro, MIT Press] e Olszewska (2020), recensione dello stesso in *Genetic Programming and Evolvable Machines*. Miller e' un libro divulgativo (raccolta di interviste a Goodfellow, Mordvintsev, Isola, Eck, collettivo Obvious, Anadol, Klingemann, con discussione di Ritchie/Wiggins/Boden) che conclude affermando una “prova” della creatività della macchina; sovrapposto in larga parte a fonti gia' tenute (DeepDream/Mordvintsev gia' coperto da Barale 2021). La stessa recensione di Olszewska ne segnala la debolezza argomentativa (e' Miller stesso a fissare i criteri di creatività usati per poi “confermarli”, circolarita'; manca una sintesi teorica delle interviste raccolte) — proprio il tipo di fonte poco rigorosa contestato dal relatore. Background: Arthur I. Miller, PhD in Fisica (MIT), poi Professore di Storia e Filosofia della Scienza, UCL — percorso misto tecnico+umanistico, ma il libro stesso e' divulgativo; Anna Olszewska, Faculty of Humanities, AGH University of Science and Technology (Cracovia) — umanistico.
- Corrisponde alla sezione 2 del capitolo 3 (già impostata).

### Fase 2 — il locus della creatività (2020-2021) 🟡
- Il dibattito si sposta da "l'algoritmo è creativo?" a "chi/cosa è creativo
  nel sistema uomo+AI?". Letteratura già individuata in
  `docs/literature/da-recuperare.md` (co-creatività uomo-AI, 2024).
- **Due fonti verificate e tenute (2026-09-16), in `fase-2-locus-della-creativita/`:**
  - Hughes, Zhu, Bednarz (2021), *GAN-Enabled Human-AI Collaborative
    Applications* (Frontiers in AI, systematic review PRISMA, 34 studi):
    le GAN come strumento di supporto collaborativo per designer
    ("human-in-the-loop"), non come sostituti automatici; nota il problema
    della fiducia utente-sistema legato alla natura "black box" dei modelli.
  - McCormack, Gifford, Hutchings (2019), *Autonomy, Authenticity,
    Authorship and Intention in Computer Generated Art* (EvoMUSART 2019):
    riparte dal caso Belamy ("Belamy's Revenge") per riesaminare mezzo
    secolo di letteratura su autonomia/autorialità/intenzione nell'arte
    computazionale (Noll, Nees, Nake, Cohen) e chiede se le tecniche
    recenti (deep learning, GAN) cambino davvero le risposte consolidate.
    **Riferimento incrociato con la Fase 0**: contiene materiale primario
    aggiuntivo sul caso Belamy/Barrat (screenshot del tweet di Barrat del
    25 ottobre 2018) utile anche per l'ancoraggio storico della Fase 0.
- **Tenuta come spunto secondario, non pilastro (2026-09-16)**: Colton,
  Pease, Saunders (2018), *Issues of Authenticity in Autonomously Creative
  Systems* (in `fase-2-locus-della-creativita/`). Non parla di GAN/CAN nello
  specifico e il tema centrale (percezione dell'opera in base a chi/cosa si
  crede l'abbia creata) e' gia' coperto dalla letteratura sul bias
  percettivo (Bellaiche, Chamberlain, Ragot). Contributo utile solo per la
  distinzione terminologica di Dutton (2003) tra autenticita' *nominale*
  (provenienza) ed *espressiva* (l'opera riflette davvero le convinzioni
  dell'autore) — da citare puntualmente se serve in fase di stesura, non da
  trattare come fonte primaria della Fase 2.
- **Tenuto come spunto secondario, non pilastro (2026-09-17)**: Arielli (2021), *Extended Aesthetics: Art and Artificial Intelligence* (Proceedings of the European Society for Aesthetics, vol. 13 — nel file sono presenti anche altri contributi del volume, non pertinenti: solo le pp. 1-13, l'articolo di Arielli, riguardano l'AI), in `fase-2-locus-della-creativita/`. Sostiene che gli sviluppi ML/AI in estetica mettano in discussione l'unicità della creatività/autorialità individuale; propone la cornice della “extended aesthetic mind” — l'AI come estensione della mente umana piuttosto che “Altro” in competizione con essa (concettualmente vicino al tema del locus della creatività di questa fase; è anche il seme del libro *Artificial Aesthetics*, scritto poi con Lev Manovich). Non specifico GAN/CAN, per questo non trattato come fonte primaria. Background: Emanuele Arielli, MA Filosofia (Univ. Statale di Milano) + PhD Psicologia e Semiotica (TU Berlin), professore IUAV Venezia — umanistico con componente empirico-psicologica, nessuna formazione tecnica.
- **Scartato per overlap (2026-09-17)**: Chamberlain, Mullin, Scheerlinck, Wagemans (2018), *Putting the Art in Artificial* (bias percettivo contro l'arte generata al computer, con effetto opposto per l'arte robotica osservata in azione). Sovrapposizione con il filone del bias percettivo già coperto da Bellaiche et al. (2023), già usato in `02-arte.tex` e più recente e specifico sull'arte generata da AI (Chamberlain 2018 è precedente alle GAN mainstream e riguarda arte computazionale/robotica in senso lato, non AI generativa specificamente). Conteggi di citazione non verificabili in modo affidabile da questo ambiente (vedi nota metodologica Fase 0); criterio di scelta usato: recenza e specificità tematica su Bellaiche. Background per completezza: Chamberlain (ora Goldsmiths, Psicologia) e Mullin (MIT CSAIL, Computational Perception and Cognition) psicologhe sperimentali; Scheerlinck e Wagemans (KU Leuven, Laboratory of Experimental Psychology) — psicologia sperimentale/scienza cognitiva, empirico-quantitativo.
- Corrisponde alla sezione 3 del capitolo 3.

### Fase 3 — l'ondata etica e l'antropomorfizzazione (2021-2024) 🟡
- Esplosione dei modelli diffusivi (DALL-E, Midjourney, Stable Diffusion) porta
  il dibattito nel mainstream. Antropomorfizzazione come fallacia; obiezione
  training-vs-ispirazione. Fonti già individuate in `da-recuperare.md`.
- Corrisponde alla sezione 4 del capitolo 3.

### Fase 4 — oggi: modelli indistinguibili, dove si è spostato il discorso 🟡
- Tesi di Gian (2026-09-14): i modelli sono migliorati fino a produrre output
  indistinguibili da lavoro umano (diffusion, Nano Banana e simili) — ma il
  seme del dibattito resta GAN/CAN. Domande aperte da sviluppare:
  - Come si è spostato il discorso, anni dopo, alla luce delle nuove tecnologie?
  - Cosa ne pensa oggi l'opinione pubblica?
  - Cosa ne pensa la comunità scientifica?
- **Prima fonte pilastro tenuta (2026-09-16)**: Franceschelli & Musolesi
  (2024), *Creativity and Machine Learning: A Survey*, ACM Computing
  Surveys (rivista molto autorevole, pubblicazione giugno 2024) — rassegna
  ampia e recente su creatività e ML, tassonomia dei modelli generativi e
  metodi di valutazione. Risponde direttamente alla critica del relatore
  sulla letteratura datata. Background: Franceschelli (Università di
  Bologna) e Musolesi (UCL + Bologna) — informatici. In `fase-4-oggi/`.
- **Riferimento incrociato con la Fase 0**: Hertzmann (2020), in
  `fase-0-gan-aprono-il-dibattito/`, aveva previsto nel 2020 che
  l'"indeterminatezza visiva" tipica delle GAN sarebbe scomparsa con il
  miglioramento dei modelli (curva "Uncanny Ridge") — previsione ora
  verificabile come confermata, utile come aggancio diretto alla domanda
  centrale di questa fase.
- Corrisponde alla sezione 5 del capitolo 3 (2025-2026) e alla discussione
  trasversale del capitolo 4. È il punto su cui manca più letteratura verificata
  ad oggi.

## Background degli autori — tracciato per bilanciare tecnico/umanistico

> Aggiunto il 2026-09-16 su richiesta del relatore: verificare per ogni
> fonte se l'autore ha formazione tecnica (informatica/ingegneria) o
> umanistica (filosofia, storia dell'arte, scienze sociali), per non
> sbilanciare la rassegna verso i soli "pensatori" senza competenza tecnica
> sul funzionamento reale dei sistemi. Aggiornare questa tabella ogni volta che si valuta una nuova fonte, PRIMA di deciderne l'inclusione.

| Fase | Autore/i | Fonte | Background | Note |
|---|---|---|---|---|
| 0 | Coeckelbergh (2017) | *Can Machines Create Art* | Filosofo — Professore di Filosofia della Tecnologia, Universita' di Vienna | Umanistico puro |
| 0 | Epstein, Levine, Rand, Rahwan (2020) | *Who Gets Credit for AI-Generated Art?* | Epstein: MIT Media Lab (interdisciplinare); Levine: psicologa cognitiva (MIT Brain and Cognitive Sciences / Harvard Psychology); Rand: scienziato cognitivo, decisione/comportamento (MIT); Rahwan: background in informatica/AI, ora scienza computazionale dei sistemi sociali (Max Planck, Center for Humans and Machines) | Team multidisciplinare, orientato a scienze cognitive/comportamentali, non ingegneria pura — ma con almeno un autore (Rahwan) di formazione informatica |
| 1 | Elgammal (2017; coautore 2019) | *CAN* / *Art, Creativity, and the Potential of AI* | Informatico — Dept. of Computer Science, Rutgers University | Tecnico, autore del sistema stesso |
| 1 | Mazzone (coautrice 2019) | *Art, Creativity, and the Potential of AI* | Storica dell'arte — Dept. of Art & Architectural History, College of Charleston | Umanistico; il paper 2019 e' gia' un lavoro misto tecnico+umanistico |
| 1 | Qi (2019) | *Research on Art of AI from the Perspective of Symbolic Aesthetics* | Communication University of China — formazione in comunicazione/studi umanistici, non tecnica | Umanistico puro |
| 1 | Snell (2017) | *A Review of "Creative Adversarial Networks"* (Medium) | Artista — B.A. Experiential Art and Design, Carnegie Mellon University; usa ML nella pratica artistica ma senza formazione tecnica formale | Non accademico, non tecnico — voce dal mondo dell'arte digitale |
| 2 | Hughes, Zhu, Bednarz (2021) | *GAN-Enabled Human-AI Collaborative Applications* | Hughes: EPICentre, Faculty of Art and Design, UNSW (misto arte/design e tecnologia); Zhu e Bednarz: CSIRO Data61 (agenzia nazionale australiana di ricerca in data science/AI) | Tecnico, systematic review con metodologia PRISMA |
| 2 | McCormack, Gifford, Hutchings (2019) | *Autonomy, Authenticity, Authorship and Intention in Computer Generated Art* | SensiLab, Faculty of Information Technology, Monash University | Tecnico/informatico puro (McCormack: noto ricercatore di computational creativity, base in informatica) |
| 2 | Colton, Pease, Saunders (2018) | *Issues of Authenticity in Autonomously Creative Systems* | MetaMakers Institute (Falmouth University) + Computational Creativity Group (Goldsmiths, University of London) + School of Computing (University of Dundee) | Tecnico/informatico puro (Colton: noto per "The Painting Fool") |
| 3 | Anscomb (2022) | *Creating Art with AI* | De Montfort University (Leicester), Faculty of Art, Design & Humanities | Filosofa dell'arte/estetica (PhD History and Philosophy of Art, University of Kent), ma con impegno tecnico diretto sul funzionamento delle GAN |
| 3 | Arriagada, Arriagada-Bruneau (2022) | *AI's Role in Creative Processes: A Functionalist Approach* | Arriagada: Faculty of Philosophy and Education (Groningen/Metropolitan Univ. of Educational Sciences); Arriagada-Bruneau: Pontificia Universidad Católica de Chile, doppia affiliazione Instituto de Éticas Aplicadas + Instituto de Matemática Computacional | Filosofi, ma con un piede in un istituto di matematica computazionale |
| 3 | Anantrasirichai, Bull (2022) | *Artificial Intelligence in the Creative Industries: A Review* | Bristol Vision Institute, University of Bristol | Tecnico puro (ingegneria/visione artificiale) |
| 0 | Hertzmann (2020) | *Visual Indeterminacy in GAN Art* | Adobe Research | Tecnico puro (ricercatore di computer graphics) |
| 0 | Barale (2022) | *Latent Spaces: What AI Art Can Tell Us About Aesthetic Experience* | Università degli Studi di Milano, settore M-FIL/04 (Estetica) | Umanistico puro (filosofa dell’estetica) |
| 0 | Barale (2021) | *“Who inspires who?” Aesthetics in front of AI art* | Università degli Studi di Milano, settore M-FIL/04 (Estetica) | Umanistico puro (filosofa dell’estetica) |
| 2 | Arielli (2021) | *Extended Aesthetics: Art and Artificial Intelligence* | IUAV Venezia (MA Filosofia Univ. Milano + PhD Psicologia e Semiotica, TU Berlin) | Umanistico con componente empirico-psicologica |
| 4 | Franceschelli, Musolesi (2024) | *Creativity and Machine Learning: A Survey* | Università di Bologna + University College London | Tecnico puro (informatici) |
| 1 | Berryman (2024) | *Creativity and Style in GAN and AI Art* | School of Humanities, University of Glasgow | Umanistico puro (storico dell'arte) |
| 1 | Langer (1953) | *Feeling and Form: A Theory of Art* | Filosofa dell'estetica (allieva/influenzata da Ernst Cassirer) | Umanistico puro |
| gen. | Boden (2004) | *The Creative Mind: Myths and Mechanisms* | Research Professor of Cognitive Science, Univ. Sussex (laurea in Scienze Mediche, Cambridge; PhD in psicologia sociale/scienze cognitive, Harvard) | Interdisciplinare (medicina→filosofia→psicologia cognitiva→informatica), non un “puro pensatore” umanistico |
| gen. | Colton (2008) | *Creativity Versus the Perception of Creativity in Computational Systems* | Department of Computing, Imperial College London | Tecnico/informatico puro |
| gen. | Wiggins (2006) | *A Preliminary Framework for Description, Analysis and Comparison of Creative Systems* | Dept. of Computing, Goldsmiths, University of London | Tecnico/informatico puro |
| gen. | Ritchie (2006) | *The Transformational Creativity Hypothesis* | Dept. of Computing Science, University of Aberdeen | Tecnico/informatico puro |
| 0 | Arbiza Goenaga (2020) | *Who is Edmond de Belamy?* | Sinnergiak Social Innovation Center + Galapagos Studio (Donostia-San Sebastián) | Creative industries/innovazione sociale, non tecnico |
| 2 | Horton Jr, White, Iyengar (2023) | *Bias against AI art can enhance perceptions of human creativity* | Columbia Business School (tutti e tre gli autori) | Psicologia del consumatore/marketing, umanistico-sociale, metodologia empirica |
| 3 | Placani (2024) | *Anthropomorphism in AI: hype and fallacy* | Institute of Philosophy (IFILNOVA), Universidade Nova de Lisboa | Umanistico puro (filosofa, etica dell'AI) |
| 4 | Calvo (2026) | *The synthetic transformation of the art world: ethical tensions* | Universitat Jaume I (Castellón) | Umanistico puro (filosofo, etica dell'AI) |
| 4 | Pearson, Dennis, Cheong (2026) | *Creativity Reconsidered: Generative AI and the Problem of Intentional Agency* | Pearson (Univ. Amsterdam/Lisbona) e Dennis (TU Eindhoven, Centro Filosofia dell'AI): filosofi; Cheong (Senior Lecturer in Digital Ethics, Melbourne, School of Computing and Information Systems + Law School): tecnico | Team bilanciato tecnico/umanistico |
| gen. | Scarinzi, Cañamero (2022) | *Toward Affective Interactions: E-Motions and Embodied Artificial Cognitive Systems* | Scarinzi: CY AS Institute for Advanced Studies + Univ. Göttingen (filosofia/estetica); Cañamero: ETIS Lab, CY Cergy Paris Université (robotica affettiva/sistemi cognitivi) | Team bilanciato umanistico/tecnico |
| 0 | Jabbar, Li, Omar (2021) | *A Survey on Generative Adversarial Networks: Variants, Applications, and Training* | College of Computer Science and Technology, Zhejiang University, Hangzhou (Cina) | Tecnico/informatico puro |

## Materiale trasversale (non specifico di una fase)

> Nuova cartella nella libreria TESI, `fondamenti-generale/` (2026-09-16):
> fonti teoriche generali sulla creativita' computazionale, utili come
> sfondo per `02-fondamenti.tex` ma non legate a una tappa cronologica
> precisa del dibattito GAN/CAN. Primo contenuto: Veale, Cardoso, Perez y
> Perez, *Systematizing Creativity: A Computational View* (2019) — capitolo
> introduttivo generale al campo della Computational Creativity, non
> specifico di GAN/CAN.
>
> **Confermate qui (2026-09-17)**: Boden (2004, 2a ed.), *The Creative Mind: Myths and Mechanisms* — testo fondativo del campo, distinzione H-creativity/P-creativity e tassonomia esplorativa/combinatoria/trasformazionale (è il riferimento diretto dietro l'obiezione di Snell del 2017, già in Fase 1); Colton (2008), *Creativity Versus the Perception of Creativity in Computational Systems*; Wiggins (2006), *A Preliminary Framework for Description, Analysis and Comparison of Creative Systems* (formalizza le nozioni di Boden). Nessuna delle tre è specifica di GAN/CAN (tutte precedenti), ma sono il vocabolario teorico su cui si appoggiano già le obiezioni citate altrove nella sinossi.
>
> **Confermato anche (2026-09-17)**: Ritchie (2006), *The Transformational Creativity Hypothesis* (Dept. of Computing Science, University of Aberdeen — tecnico puro). Prova a rendere formalizzabile e falsificabile empiricamente l'ipotesi di Boden sulla trasformazione dello spazio concettuale; conclude che i termini centrali (spazio concettuale, trasformazione) restano troppo vaghi per affermazioni falsificabili. Utile non solo come vocabolario ma come **nota critica/di cautela**: la stessa distinzione esplorativa/trasformazionale usata da Snell (Fase 1) per dire che la CAN “resta nella creatività esplorativa” poggia su un concetto che uno degli autori dello stesso campo giudica troppo vago per essere verificato rigorosamente — una sfumatura utile in sede di stesura.
>
> **Nuova cartella `fondamenti-tecnici/` (2026-09-17)**, distinta da `fondamenti-generale/`: per fonti puramente tecniche sul funzionamento delle GAN, senza contenuto rilevante per il dibattito critico. Primo contenuto: Karras et al. (2020), *Training Generative Adversarial Networks with Limited Data* (StyleGAN2-ADA, NeurIPS 2020; NVIDIA + Aalto University — tecnico puro). Nessun legame con creatività/autorialità: propone l'adaptive discriminator augmentation per stabilizzare l'addestramento GAN con pochi dati. Utile come riferimento tecnico per spiegare come le GAN moderne raggiungano output di alta qualità (utile per l'introduzione tecnica in `02-fondamenti.tex` e per il collegamento con la Fase 4, “modelli indistinguibili”).
>
> **Aggiunte (2026-09-17)**, stesso criterio puramente tecnico: Ho, Jain, Abbeel (2020), *Denoising Diffusion Probabilistic Models* (DDPM, NeurIPS 2020; UC Berkeley) — il paper fondativo dei moderni modelli di diffusione (Stable Diffusion, DALL-E derivano da qui); Dhariwal, Nichol (2021), *Diffusion Models Beat GANs on Image Synthesis* (OpenAI) — il paper che segna tecnicamente il sorpasso della diffusione sulle GAN in qualità di sintesi, aggancio diretto alla Fase 4 (perché il discorso si è spostato dalle GAN alla diffusione, perché oggi gli output sono indistinguibili). Entrambi tecnico puro, nessun contenuto sul dibattito creatività/autorialità.
>
> **Scartato (2026-09-17)**: Hereu, Hu (2024), *Creative Portraiture: Exploring Creative Adversarial Networks and Conditional Creative Adversarial Networks* (arXiv, Columbia University). Specifico sulla CAN (la riproducono e propongono un'estensione condizionata sullo stile, CCAN), ma **nessuna sede di pubblicazione/peer review rintracciabile** — sembra un lavoro di corso/progetto studentesco (solo arXiv, email istituzionali da studenti, nessuna citazione rintracciabile). Proprio il tipo di fonte “poco citata” contestato in origine dal relatore. Background: Sebastian Hereu, Qianfei Hu, Columbia University — presumibilmente studenti, non ricercatori affermati.

## Prossimi temi da discutere (coda)
- (da riempire mano a mano che procediamo)


## Audit di rilevanza e sovrapposizioni concettuali (2026-09-18)

> Fatto durante il riordino della libreria `TESI/` (Readme.docx + Spunti.docx
> per ogni cartella). Nessuna fonte attualmente in libreria e' stata giudicata
> da scartare, ma segno qui alcune osservazioni per la stesura.

**Coppie complementari da citare insieme (non ridondanti, si rinforzano a vicenda):**
- Epstein, Levine, Rand, Rahwan (2020) [Fase 0, empirico] + Placani (2024)
  [Fase 3, filosofico] — stesso fenomeno (antropomorfizzazione dell'AI e sue
  conseguenze sul giudizio morale/di merito), letto prima con dati sperimentali
  e poi con cornice etica. Buona sequenza espositiva.
- Colton (2008) [tecnico, fondamenti-generale] + Horton/White/Iyengar (2023) e
  Messer (2024) [Fase 2, empirico] — stesso tema (percezione di creativita vs.
  creativita "reale") da angolature disciplinari diverse (framework
  computazionale vs. psicologia sperimentale).

**Sovrapposizione parziale da tenere d'occhio (non richiede di scartare nulla, solo attenzione in fase di scrittura):**
- Coeckelbergh (2017) e McCormack, Gifford, Hutchings (2019) coprono entrambi,
  in modo ampio, decenni di dibattito filosofico su autonomia/autenticita/
  intenzione nell'arte generata al computer. Non sono duplicati (Coeckelbergh
  e piu propriamente filosofico/Heideggeriano; McCormack et al. e piu storico
  ed esplicitamente ancorato al caso Belamy), ma in sede di scrittura valutare
  se serve davvero spiegare entrambi per esteso o se uno dei due puo restare
  in nota a supporto dell'altro, per non appesantire l'esposizione.

**Da verificare quando si leggeranno per intero (abstract non recuperabile in automatico, solo frontespizio Odradek):**
- Anscomb (2022), Arriagada/Arriagada-Bruneau (2022) e Anantrasirichai/Bull
  (2022) sono tutti e tre del 2022 e tutti nel filone etico della Fase 3:
  stesso controllo di overlap gia fatto per Chamberlain/Bellaiche (Fase 2) va
  ripetuto qui una volta letti per intero, per assicurarsi che non dicano la
  stessa cosa con parole diverse.

**Rilevanza tematica, non da scartare ma da tenere come "di contorno":**
- ESA Proceedings vol. 13 (2021)/Arielli — gia annotato come spunto
  secondario, non un pilastro.
- Hughes, Zhu, Bednarz (2021) — sistematic review su GAN nei workflow di
  design: rilevante per il "locus della creativita" ma piu vicino al design
  industriale che al dibattito arte/creativita in senso stretto.
- Cintas, Das, Speakman, Akinwande (2021) — tecnico puro su come misurare la
  creativita nei modelli generativi: utile come nota tecnica, non come
  argomento centrale.

**Nessuna fonte risulta oggi fuori tema o da scartare** nell'insieme delle
cartelle di fase e nei due fondamenti — il lavoro di scarto (Chamberlain,
Manovich, Hereu&Hu, Miller, Olszewska, ecc., vedi `_scartati/`) e' gia stato
fatto nelle sessioni precedenti.
