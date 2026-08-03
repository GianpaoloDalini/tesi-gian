# Registro degli esperimenti

Ogni run che produce un numero o una figura citati nella tesi va registrato qui.
È il ponte tra `experiments/` (ignorato da git) e il testo dell'elaborato: senza,
tra tre mesi non saprai da quale run proviene la Figura 6.2.

| ID run (W&B) | Data | Commit | Config | Esito | Usato in | Note |
|---|---|---|---|---|---|---|
| | | `experiment=e1-dcgan-baseline` | | | | condizione di **controllo** |
| | | `experiment=e2-can-confronto` | | | | condizione **sperimentale** |

## Confronto E1 / E2

Tabella da compilare dopo `python -m tesi_gan.cli evaluate`. I due run vanno valutati
con **lo stesso `--n-samples`**: il FID è sensibile alla numerosità del campione e
confrontare un FID su 2048 campioni con uno su 10000 non significa nulla.

| Metrica | E1 — DCGAN | E2 — CAN | Direzione attesa |
|---|---|---|---|
| FID ↓ | | | CAN peggiore |
| Inception Score ↑ | | | incerta |
| Entropia di stile normalizzata | — (assente per costruzione) | | CAN alta |
| Studio percettivo | | | esplorativo |

Il trattino nella riga dell'entropia **non è un dato mancante**: la DCGAN non ha testa
di stile, quindi la metrica non è definita per quella condizione. Va detto nella
caption della tabella in tesi, altrimenti sembra un buco nei risultati.

## Registri collegati

- [`giudice-stile.md`](giudice-stile.md) — iterazioni del classificatore terzo
  (D-015). Nessuna ha raggiunto la soglia dichiarata: il percorso è documentato
  perché mostra che il limite è stato misurato, non subito, ed è materiale per il
  capitolo di metodologia e per la sezione sui limiti.

## Regole

1. **Nessun run senza commit.** Il working tree dev'essere pulito prima del training
   (`tesi_gan.utils.provenance.assert_clean_tree`).
2. **I run falliti si registrano**, non si cancellano. Un fallimento documentato è
   materiale per la sezione sui limiti; un fallimento rimosso è tempo perso due volte.
3. La colonna *Usato in* indica figura, tabella o sezione della tesi. Se resta vuota
   a lungo, o il run era inutile o la tesi sta ignorando un risultato.
