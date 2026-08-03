#!/usr/bin/env bash
# ============================================================================
#  Valuta TUTTI i checkpoint salvati di ogni run, non solo l'ultimo.
#
#      RES=128 bash scripts/valuta_traiettoria.sh
#
#  ## Perche' esiste
#
#  Il criterio pre-registrato era di riportare l'epoca 100 per tutti i run, per
#  evitare di scegliere il checkpoint migliore dopo aver visto i risultati.
#  L'osservazione dei campioni a 128px ha pero' mostrato un caso che quel criterio
#  non prevedeva: `dcgan-seed1` produce immagini di ottima qualita' all'epoca 97 e
#  **collassa completamente all'epoca 98**, con gli artefatti a scacchiera tipici di
#  ConvTranspose2d in divergenza. Riportare l'epoca 100 significherebbe presentare
#  come risultato un modello degenerato, mentre otto epoche prima era il miglior
#  esito dell'intero progetto.
#
#  ## Perche' non e' cherry-picking
#
#  Tre condizioni, tutte necessarie:
#
#  1. **La regola e' identica per tutti i run** e per entrambe le condizioni.
#  2. **La traiettoria completa viene pubblicata**, non solo il punto scelto: il
#     lettore vede quando e come ciascun run e' migliorato o degenerato.
#  3. **L'adozione del criterio e' datata e motivata** in experiments/registry.md,
#     dichiarando che e' successiva all'osservazione del collasso.
#
#  Il punto (3) e' quello che distingue una revisione onesta da una mascherata: il
#  criterio e' cambiato perche' e' emerso un fenomeno che non era stato previsto,
#  non perche' i numeri non piacevano.
#
#  ## Nota sui costi
#
#  Undici checkpoint per sei run fanno 66 valutazioni. Con lo stesso --n-samples di
#  tutte le altre misure — che non si tocca, perche' il FID e' sensibile alla
#  numerosita' del campione — sono circa 40 minuti.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SEEDS="${SEEDS:-1 2 3}"
N_SAMPLES="${N_SAMPLES:-2048}"
RES="${RES:-64}"
FAST_DIR="${FAST_DIR:-/dev/shm}"

case "$RES" in
  64)  COPPIE="e1-dcgan-baseline:dcgan e2-can-confronto:can"
       TRAIN_DIR="$FAST_DIR/processed";     SRC_TRAIN="data/processed"
       REF_DIR="$FAST_DIR/processed_test";  SRC_REF="data/processed_test" ;;
  128) COPPIE="e3-dcgan-128:dcgan e4-can-128:can"
       TRAIN_DIR="$FAST_DIR/processed_128";    SRC_TRAIN="data/processed_128"
       REF_DIR="$FAST_DIR/processed_test_128"; SRC_REF="data/processed_test_128" ;;
  *)   echo "!!! RES=$RES non prevista."; exit 1 ;;
esac

[[ -d "$TRAIN_DIR" ]] || { TRAIN_DIR="$SRC_TRAIN"; REF_DIR="$SRC_REF"; }

RESULTS_DIR="${RESULTS_DIR:-experiments/traiettoria-$RES}"
mkdir -p "$RESULTS_DIR"

echo "==> Traiettoria a ${RES}px — tutti i checkpoint, --n-samples $N_SAMPLES"
echo "==> Risultati in $RESULTS_DIR/"

TOTALE=0
INIZIO=$(date +%s)

for seed in $SEEDS; do
  for coppia in $COPPIE; do
    esperimento="${coppia%%:*}"
    condizione="${coppia##*:}"
    cartella="experiments/checkpoints/${condizione}-${RES}-seed${seed}"

    [[ -d "$cartella" ]] || { echo "!!! Manca $cartella — salto."; continue; }

    # `latest.pt` si escl: e' un duplicato dell'ultima epoca gia' coperta da
    # final.pt, e valutarlo due volte sporcherebbe la curva con un punto doppio.
    for checkpoint in "$cartella"/epoch_*.pt "$cartella/final.pt"; do
      [[ -f "$checkpoint" ]] || continue

      nome="$(basename "$checkpoint" .pt)"
      uscita="$RESULTS_DIR/${condizione}-seed${seed}-${nome}.json"

      if [[ -f "$uscita" ]]; then
        echo "  gia' valutato: $uscita"
        continue
      fi

      echo
      echo "--- $condizione seed $seed — $nome ---"
      python -m tesi_gan.cli evaluate \
        --checkpoint "$checkpoint" \
        --n-samples "$N_SAMPLES" \
        --output "$uscita" \
        "experiment=$esperimento" \
        "seed=$seed" \
        "data.root=$TRAIN_DIR" \
        "data.reference_root=$REF_DIR" \
        > /dev/null
      TOTALE=$((TOTALE + 1))
    done
  done
done

DURATA=$(( $(date +%s) - INIZIO ))
echo
echo "==> $TOTALE checkpoint valutati in $((DURATA / 60)) minuti."
echo "==> Curva e selezione con:"
echo "        python scripts/traiettoria.py --results-dir $RESULTS_DIR"
