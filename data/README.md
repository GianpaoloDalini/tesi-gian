# Dati

**Questa cartella non e' versionata.** I dataset si ricreano, non si committano.

```
data/
├── raw/         dati scaricati, mai modificati a mano
├── processed/   output del preprocessing, rigenerabile da raw/
└── external/    risorse di terze parti (es. pesi preaddestrati)
```

## Regola

Ogni dataset usato nella tesi deve essere ottenibile con un comando documentato
qui sotto. Se un dato non e' riproducibile, vanno registrate provenienza esatta,
data di acquisizione e licenza — la commissione puo' chiederle, e la sezione
sulla riproducibilita' della tesi le richiede.

## Dataset del progetto

| Nome | Fonte | Licenza dichiarata | Note |
|---|---|---|---|
| **ArtBench-10**, sei stili | [artbench.eecs.berkeley.edu](https://artbench.eecs.berkeley.edu/files/artbench-10-imagefolder-split.tar) — data di download `DA COMPILARE` | «Fair Use» (autodichiarazione, vedi V-007) | 5.000 immagini per stile, 64×64, vedi [ADR-0004](../docs/decisions/0004-dataset.md) |
| WikiArt | *alternativa scartata* | «non-commercial research» | tenuta come confronto metodologico |

Stili selezionati: `ukiyo_e`, `renaissance`, `baroque`, `romanticism`, `realism`,
`impressionism`. Tutti di pubblico dominio; escluso il Surrealismo, l'unico dei
dieci ancora sotto copyright.

### Dove si scarica

**Sul pod RunPod, dentro un Network Volume**, non in locale. Il volume sopravvive
alla distruzione del pod e si riattacca a pod nuovi: il dataset si scarica **una
volta sola** e lo riusano il classificatore di stile e tutti e sei i run.

La rete di un datacenter scarica in minuti quello che una linea domestica impiega
un'ora, e il costo del pod acceso durante il download è nell'ordine dei centesimi.

### Preparazione

Dal pod, con il Network Volume montato (per convenzione su `/workspace`):

```bash
cd /workspace

# 1. scarica ArtBench nella versione ImageFolder con split (256x256)
curl -O https://artbench.eecs.berkeley.edu/files/artbench-10-imagefolder-split.tar
mkdir -p data/raw && tar -xf artbench-10-imagefolder-split.tar -C data/raw/

# 2. ispeziona cosa c'e', senza copiare nulla e senza bisogno di --licenza-verificata
python -m tesi_gan.data.download --ispeziona --raw data/raw

# 3. costruisci il sottoinsieme (solo dopo aver chiuso V-007)
python -m tesi_gan.data.download \
    --stili ukiyo_e renaissance baroque romanticism realism impressionism \
    --per-style 5000 --resize 64 --seed 42 --licenza-verificata
```

**`--resize 64` non è opzionale nella pratica.** ArtBench è distribuito a 256×256 e
l'esperimento gira a 64×64: senza, il dataloader decodifica un JPEG a 256px a ogni
accesso per scartarne il 94% dei pixel, su sei run da un centinaio di epoche. Con il
ridimensionamento `data/processed` scende sotto i 100 MB, contro alcuni GB.

Il ritaglio applicato qui (resize del lato corto + ritaglio centrale) è **lo stesso**
di `build_transform` in `src/tesi_gan/data/dataset.py`. Se uno dei due cambia va
cambiato anche l'altro, altrimenti l'inquadratura diventa una variabile non
dichiarata.

**La risoluzione finisce nel manifest.** Un `data/processed` a 64px e uno a 256px sono
indistinguibili a occhio ma producono run non confrontabili.

La struttura attesa in `data/raw/` è una sottocartella per stile:

```
data/raw/
├── ukiyo_e/
│   ├── 0001.jpg
│   └── ...
└── renaissance/
    └── ...
```

Il comando scrive `data/processed/manifest.json` con stili, conteggi, seed e data:
**quei numeri vanno riportati qui e nell'appendice sulla riproducibilità.** Il
campionamento è seedato, quindi lo stesso seed ricostruisce lo stesso sottoinsieme.

Il flag `--licenza-verificata` è obbligatorio e il comando si rifiuta di girare
senza. Non è un fastidio da aggirare: è il presidio di V-007.

### Perché la selezione è esplicita e non «i più popolati»

ArtBench è bilanciato per costruzione: tutti gli stili hanno 5.000 immagini. Chiedere
«i sei più popolati» non selezionerebbe nulla di sensato — la scelta ricadrebbe
sull'ordine alfabetico invece che su un criterio dichiarato. `--stili` rende la
selezione esplicita e quindi giustificabile.

### Perché il bilanciamento

Con classi sbilanciate la testa di stile del discriminatore impara la distribuzione a
priori invece dello stile, e l'entropia della posterior — la metrica su cui si regge
il confronto DCGAN/CAN — diventa ininterpretabile. Per questo `prepare` forza il
numero di immagini al minimo effettivo fra le classi selezionate, anche se ne è stato
richiesto uno più alto.

### Il dataset alternativo

`python -m tesi_gan.data.inventory` misura lo sbilanciamento di WikiArt scaricando i
soli indici CSV (~5 MB, nessuna immagine). Non serve più alla strada principale, ma
documenta perché WikiArt è stato scartato — ed è materiale per il capitolo di
metodologia.

## Attenzione al copyright

I dataset di opere d'arte (WikiArt e simili) hanno vincoli di licenza non banali.
Dato che la tesi tratta anche le implicazioni etiche dell'IA generativa, usare un
dataset senza verificarne i termini sarebbe un'incoerenza che la commissione
potrebbe legittimamente rilevare. Verificare **prima** di scaricare.
