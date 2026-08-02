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

### Preparazione

```bash
# 1. scarica ArtBench nella versione ImageFolder con split
curl -O https://artbench.eecs.berkeley.edu/files/artbench-10-imagefolder-split.tar
tar -xf artbench-10-imagefolder-split.tar -C data/raw/

# 2. ispeziona cosa c'e', senza copiare nulla
python -m tesi_gan.data.download --ispeziona

# 3. costruisci il sottoinsieme (solo dopo aver chiuso V-007)
python -m tesi_gan.data.download \
    --stili ukiyo_e renaissance baroque romanticism realism impressionism \
    --per-style 5000 --seed 42 --licenza-verificata
```

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
