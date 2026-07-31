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

| Nome | Fonte | Licenza | Comando di download | Note |
|---|---|---|---|---|
| *(da definire)* | | | | vedi `docs/decisions/0003-impianto-sperimentale.md` |

## Attenzione al copyright

I dataset di opere d'arte (WikiArt e simili) hanno vincoli di licenza non banali.
Dato che la tesi tratta anche le implicazioni etiche dell'IA generativa, usare un
dataset senza verificarne i termini sarebbe un'incoerenza che la commissione
potrebbe legittimamente rilevare. Verificare **prima** di scaricare.
