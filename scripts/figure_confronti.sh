#!/usr/bin/env bash
# ============================================================================
#  Figure di confronto reali/generate per tutti i run di una condizione.
#
#      RES=128 EPOCA=0090 bash scripts/figure_confronti.sh
#      RES=128 EPOCA=final CONDIZIONI=can bash scripts/figure_confronti.sh
#
#  **L'epoca e' la stessa per tutti i run**, ed e' il punto che conta: figure
#  generate da epoche diverse non sono confrontabili fra loro, e sceglierla run per
#  run — magari quella che rende meglio — sarebbe selezione mascherata sul materiale
#  visivo. L'epoca usata va dichiarata nella didascalia.
#
#  A 128px `final` contiene un modello collassato per almeno un run (dcgan-seed1
#  degenera fra l'epoca 97 e la 98), quindi EPOCA=0090 e' il valore sensato.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RES="${RES:-128}"
EPOCA="${EPOCA:-0090}"
SEEDS="${SEEDS:-1 2 3}"
CONDIZIONI="${CONDIZIONI:-dcgan can}"
FAST_DIR="${FAST_DIR:-/dev/shm}"

case "$RES" in
  64)  DATI="processed";     RIF="processed_test"
       ESP_dcgan="e1-dcgan-baseline"; ESP_can="e2-can-confronto" ;;
  128) DATI="processed_128"; RIF="processed_test_128"
       ESP_dcgan="e3-dcgan-128";      ESP_can="e4-can-128" ;;
  *)   echo "!!! RES=$RES non prevista."; exit 1 ;;
esac

TRAIN_DIR="$FAST_DIR/$DATI"
REF_DIR="$FAST_DIR/$RIF"
[[ -d "$TRAIN_DIR" ]] || { TRAIN_DIR="data/$DATI"; REF_DIR="data/$RIF"; }

echo "==> Figure a ${RES}px, epoca $EPOCA per tutti i run"
echo "==> Dati: $TRAIN_DIR"

PRODOTTE=0
for condizione in $CONDIZIONI; do
  case "$condizione" in
    dcgan) esperimento="$ESP_dcgan" ;;
    can)   esperimento="$ESP_can" ;;
    *)     echo "!!! Condizione sconosciuta: $condizione"; exit 1 ;;
  esac

  for seed in $SEEDS; do
    cartella="experiments/checkpoints/${condizione}-${RES}-seed${seed}"
    if [[ "$EPOCA" == "final" ]]; then
      checkpoint="$cartella/final.pt"
    else
      checkpoint="$cartella/epoch_${EPOCA}.pt"
    fi

    if [[ ! -f "$checkpoint" ]]; then
      echo "  manca $checkpoint — salto"
      continue
    fi

    echo
    echo "--- $condizione seed $seed ---"
    python -m tesi_gan.cli export-figures \
      --checkpoint "$checkpoint" \
      "experiment=$esperimento" \
      "seed=$seed" \
      "data.root=$TRAIN_DIR" \
      "data.reference_root=$REF_DIR" 2>&1 | grep -E "Confronto|Figura annotata" || true
    PRODOTTE=$((PRODOTTE + 1))
  done
done

echo
echo "==> $PRODOTTE run elaborati. Figure in thesis/figures/generated/"
echo "==> Per scaricarle:"
echo "        mkdir -p /workspace/figure && cp thesis/figures/generated/*.png /workspace/figure/"
