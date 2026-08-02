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

| Nome | Fonte | Licenza | Comando di preparazione | Note |
|---|---|---|---|---|
| WikiArt (sottoinsieme bilanciato) | `DA COMPILARE`: URL esatto e data di download | `DA VERIFICARE` — vedi V-007 | vedi sotto | 5-10 stili, 64×64, vedi [ADR-0004](../docs/decisions/0004-dataset.md) |

### Preparazione

I dati grezzi vanno messi in `data/raw/`, **una sottocartella per stile**:

```
data/raw/
├── baroque/
│   ├── 0001.jpg
│   └── ...
└── impressionism/
    └── ...
```

Poi:

```bash
# 1. ispeziona cosa c'e', senza copiare nulla
python -m tesi_gan.data.download --ispeziona

# 2. costruisci il sottoinsieme bilanciato (solo dopo aver chiuso V-007)
python -m tesi_gan.data.download \
    --num-styles 8 --per-style 2000 --seed 42 --licenza-verificata
```

Il comando scrive `data/processed/manifest.json` con stili, conteggi, seed e data:
**quei numeri vanno riportati in questa tabella e nell'appendice sulla
riproducibilità.** Il campionamento è seedato, quindi lo stesso seed ricostruisce lo
stesso sottoinsieme.

Il flag `--licenza-verificata` è obbligatorio e il comando si rifiuta di girare
senza. Non è un fastidio da aggirare: è il presidio di V-007.

### Perché il bilanciamento

Con classi sbilanciate la testa di stile del discriminatore impara la distribuzione a
priori invece dello stile, e l'entropia della posterior — la metrica su cui si regge
il confronto DCGAN/CAN — diventa ininterpretabile.

## Attenzione al copyright

I dataset di opere d'arte (WikiArt e simili) hanno vincoli di licenza non banali.
Dato che la tesi tratta anche le implicazioni etiche dell'IA generativa, usare un
dataset senza verificarne i termini sarebbe un'incoerenza che la commissione
potrebbe legittimamente rilevare. Verificare **prima** di scaricare.
