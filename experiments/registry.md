# Registro degli esperimenti

Ogni run che produce un numero o una figura citati nella tesi va registrato qui.
È il ponte tra `experiments/` (ignorato da git) e il testo dell'elaborato: senza,
tra tre mesi non saprai da quale run proviene la Figura 6.2.

| ID run (W&B) | Data | Commit | Config | Esito | Usato in | Note |
|---|---|---|---|---|---|---|
| | | | | | | |

## Regole

1. **Nessun run senza commit.** Il working tree dev'essere pulito prima del training
   (`tesi_gan.utils.provenance.assert_clean_tree`).
2. **I run falliti si registrano**, non si cancellano. Un fallimento documentato è
   materiale per la sezione sui limiti; un fallimento rimosso è tempo perso due volte.
3. La colonna *Usato in* indica figura, tabella o sezione della tesi. Se resta vuota
   a lungo, o il run era inutile o la tesi sta ignorando un risultato.
