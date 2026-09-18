# ADR-0006 — Esperimento E8: transfer learning StyleGAN2-ADA per il restyling ad alta risoluzione

- **Data:** 2026-09-14
- **Stato:** **Accettata** (esperimento pianificato — pilota da lanciare, nessun run ancora eseguito)
- **Decisore:** Gian, in risposta all'esito del primo ricevimento col relatore (Domenico Fabio Savo, 2026-09-14)
- **Dipende da:** ricerca esplorativa in `ricerca-restyling-gan-alta-risoluzione-vs-nano-banana.md`
  (progetto Claude "Tesi", 2026-09-14). **Non sostituisce** [ADR-0003](0003-impianto-sperimentale.md)/[ADR-0004](0004-dataset.md):
  il confronto controllato DCGAN→CAN resta il nucleo sperimentale quantitativo della tesi.

## Contesto

Il relatore ha bocciato la parte sperimentale della tesi: i risultati visivi (DCGAN/CAN
su ArtBench-10, 64px/128px) sono giudicati troppo scarsi se confrontati con quello che
oggi ottengono strumenti industriali come Nano Banana (Gemini 2.5/3 Pro Image). La
ricerca esplorativa ha valutato le opzioni GAN recenti/rilevanti a risoluzione minima
1080×1080 (StyleGAN2/3, StyleGAN-XL, GigaGAN, R3GAN) e la loro fattibilità di replica
col budget attuale (RunPod/RTX 4090, ordine di pochi $).

**Vincolo di inquadramento, non negoziabile:** questo esperimento è **illustrativo**,
sullo stesso piano di E5 (D-022) — dimostra la fattibilità di un risultato ad alta
qualità con risorse accademiche, **non** sostituisce né estende il confronto
quantitativo DCGAN/CAN sull'ambiguità di stile (RQ1/D-026). Le due cose restano
separate nel testo della tesi.

## Alternative valutate

| Opzione | Vantaggi | Svantaggi |
|---|---|---|
| **StyleGAN2-ADA, transfer learning** | Pensato apposta per dataset piccoli; pesi pretrained ufficiali documentati (`NVlabs/stylegan2-ada-pytorch`); precedenti pubblici di fine-tuning su arte a 512-1024px (`stylegan2-FineArt`, tutorial "Creating Abstract Art with StyleGAN2 ADA"); rischio implementativo basso | Resta un'architettura del 2020 — non risolve da sola la critica di "tesi vecchia" sul piano teorico |
| R3GAN esteso oltre FFHQ-256 | Paper più recente (2024), utile per lo "svecchiamento" della bibliografia | Mai testato dagli autori oltre 256×256: adattarlo a 1024px ha lo stesso costo di ripartire da zero, senza il vantaggio del transfer learning |
| GigaGAN | Arriva a 16 megapixel, il più veloce in inferenza | **Nessun codice/peso ufficiale rilasciato da Adobe**: replicare un risultato non verificabile indipendentemente è un rischio metodologico da evitare in un lavoro accademico |
| Training da zero a 1024px+ | Nessun compromesso sulla purezza del setup | Costo intrattabile: il paper originale StyleGAN2 ha richiesto giorni su cluster multi-GPU, non ore su un singolo RTX 4090 |

## Decisione

**StyleGAN2-ADA in transfer learning, checkpoint pretrained ufficiale come punto di
partenza (candidato principale: FFHQ, 1024×1024), target dichiarato 1024×1024,
eseguito su RunPod/RTX 4090.** ADA (Adaptive Discriminator Augmentation) è pensato
apposta per il caso "dataset piccolo + poco budget": il fine-tuning riusa la capacità
già appresa dal modello pretrained e deve solo spostarne lo stile verso la pittura,
molto più economico di un training da zero.

### Rischio metodologico centrale, da risolvere PRIMA del run completo — vedi V-011

**ArtBench-10, così come usato in questo progetto, è distribuito a 256×256**
(`data/README.md`, ADR-0004). Un transfer learning verso un target di 1024×1024
partendo da immagini sorgente a 256×256 upscalate non aggiunge dettaglio reale: la
rete imparerebbe a riprodurre texture sfocate, vanificando proprio l'obiettivo che
ha motivato l'esperimento (la qualità visiva). Questo non è un dettaglio tecnico
secondario, è la stessa logica che ha già portato a scartare GigaGAN per un motivo
diverso ma imparentato: **un esperimento che non regge a un controllo elementare non
va lanciato solo perché la pipeline gira**.

Il pilota (vedi `scripts/bootstrap_e8_stylegan2ada.sh`) deve quindi rispondere prima
di tutto a una domanda diagnostica, non addestrare subito a piena scala:
**il target di risoluzione realistico è quello dichiarato al relatore (1024×1024),
o va rivisto verso il basso (es. 512×512) in base alla risoluzione reale delle
immagini sorgente disponibili?** Due strade, entrambe legittime purché dichiarate:

1. **Restare su ArtBench-10** e accettare un target più realistico (es. 512×512,
   usando come sorgente pretrained AFHQ-512 invece di FFHQ-1024) — meno impressionante
   ma onesto rispetto ai dati disponibili.
2. **Assemblare un sottoinsieme ad alta risoluzione per un solo stile** (candidato
   naturale: `ukiyo_e`, già fra i sei stili del progetto — precedente diretto nel
   progetto pubblico "ukiyo-e-faces" di Justin Pinkney, che ha fatto esattamente
   questo: fine-tuning di StyleGAN2 su ritratti ukiyo-e raccolti ad alta risoluzione,
   non su un benchmark a bassa risoluzione). Questa strada richiede una fonte
   dichiarata e verificata di pubblico dominio (stesso standard di V-007/ADR-0004),
   **non va avviata scaricando immagini a caso da internet.**

**Non si decide qui quale delle due.** Si decide nel pilota, sulla base dei dati
reali disponibili — coerente con la regola del progetto di non stimare a tavolino
ciò che si può misurare.

**Aggiornamento 2026-09-14, stesso giorno — terza strada, verificata dopo la
prima stesura di questo ADR.** ArtBench-10 offre anche una versione **"original
size", per stile, formato LSUN** via Google Drive, distinta dal pacchetto a
256×256 usato finora (fonte: [README ufficiale](https://github.com/liaopeiyuan/artbench),
[paper arXiv:2206.11404](https://arxiv.org/abs/2206.11404)). Resta la stessa
fonte già verificata per licenza in ADR-0004/V-007, quindi **è la prima strada da
tentare**, prima delle due sopra: se la risoluzione reale di questi file regge il
target, si resta su ArtBench-10 senza dover riabbassare l'obiettivo né cercare
una fonte nuova. La risoluzione effettiva **non è dichiarata dal paper** (solo
citata come "filtrata sotto una soglia" nel materiale supplementare, non ancora
consultato) e va misurata scaricando un campione — è il primo controllo che fa
`scripts/bootstrap_e8_stylegan2ada.sh`. Se anche questa fonte non regge il
target, restano valide le due strade già discusse sopra. Dettaglio completo in
V-011 (`docs/registro-decisioni.md`).

## Conseguenze

- Diventa più facile mostrare al relatore un risultato visivamente competitivo in
  tempi brevi (ore, non giorni), con un rischio implementativo basso.
- Diventa più difficile mantenere il confronto "ad armi pari": va dichiarato
  esplicitamente che StyleGAN2-ADA è un'architettura del 2020 con pesi pretrained
  su un dominio diverso (volti), non un training comparabile a DCGAN/CAN.
- Si preclude, per budget e tempo, l'idea di ricostruire una CAN alla stessa
  risoluzione: il confronto quantitativo sull'ambiguità di stile resta a bassa
  risoluzione (E1-E4), e va detto esplicitamente in discussione perché i due
  risultati (fedeltà visiva alta, confronto quantitativo a bassa risoluzione) non
  si toccano.

## Impatto sulla tesi

- **Capitolo di metodologia:** giustificazione della scelta (questo ADR) e del suo
  status di esperimento illustrativo, non comparativo.
- **Capitolo dei risultati:** figure separate da quelle di E1-E6, etichettate come
  E8, con lo stesso trattamento già dato a E5 (D-022).
- **Capitolo di discussione:** il confronto onesto con strumenti come Nano Banana —
  "cosa è ragionevole ottenere con un GAN a budget accademico rispetto allo stato
  dell'arte industriale", non un confronto ad armi pari (vedi il documento di
  ricerca §1).
