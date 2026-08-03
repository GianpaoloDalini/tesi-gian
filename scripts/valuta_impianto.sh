#!/usr/bin/env bash
# ============================================================================
#  Valutazione dei sei run dell'impianto (ADR-0003, D-010).
#
#      bash scripts/valuta_impianto.sh
#
#  **Tutti i checkpoint vengono valutati con lo stesso `--n-samples`.** Il FID
#  e' notoriamente sensibile alla numerosita' del campione: confrontare un FID
#  su 2048 campioni con uno su 10000 non significa nulla. Per questo il valore
#  e' una variabile dello script e non un argomento da ricordarsi ogni volta.
#
#  Lo stesso vale per il giudice di stile: e' uno solo, congelato, e valuta
#  tutte le condizioni e tutti i seed (ADR-0005).
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SEEDS="${SEEDS:-1 2 3}"
N_SAMPLES="${N_SAMPLES:-2048}"
RES="${RES:-64}"
RESULTS_DIR="${RESULTS_DIR:-experiments/results-$RES}"
FAST_DIR="${FAST_DIR:-/dev/shm}"

case "$RES" in
  64)  COPPIE="e1-dcgan-baseline:dcgan e2-can-confronto:can"
       TRAIN_DIR="$FAST_DIR/processed"
       REF_DIR="$FAST_DIR/processed_test"
       SRC_TRAIN="data/processed"; SRC_REF="data/processed_test" ;;
  128) COPPIE="e3-dcgan-128:dcgan e4-can-128:can"
       TRAIN_DIR="$FAST_DIR/processed_128"
       REF_DIR="$FAST_DIR/processed_test_128"
       SRC_TRAIN="data/processed_128"; SRC_REF="data/processed_test_128" ;;
  *)   echo "!!! RES=$RES non prevista. Valori ammessi: 64, 128."; exit 1 ;;
esac

# Se il disco veloce e' stato svuotato (il pod e' stato riavviato), si ricade
# sul volume persistente: piu' lento ma corretto.
if [[ ! -d "$TRAIN_DIR" ]]; then
  echo "==> $TRAIN_DIR assente, uso il volume persistente"
  TRAIN_DIR="$SRC_TRAIN"
  REF_DIR="$SRC_REF"
fi

mkdir -p "$RESULTS_DIR"

echo "==> Risoluzione: ${RES}px"
echo "==> Valutazione con --n-samples $N_SAMPLES (identico per tutti i run)"
echo "==> Giudice: experiments/style_judge-$RES"
echo "==> Risultati: $RESULTS_DIR"

for seed in $SEEDS; do
  for coppia in $COPPIE; do
    esperimento="${coppia%%:*}"
    condizione="${coppia##*:}"
    checkpoint="experiments/checkpoints/${condizione}-${RES}-seed${seed}/final.pt"

    if [[ ! -f "$checkpoint" ]]; then
      echo "!!! Manca $checkpoint — run non eseguito? Salto."
      continue
    fi

    echo
    echo "--- $condizione seed $seed ---"
    python -m tesi_gan.cli evaluate \
      --checkpoint "$checkpoint" \
      --n-samples "$N_SAMPLES" \
      --output "$RESULTS_DIR/${condizione}-seed${seed}.json" \
      "experiment=$esperimento" \
      "seed=$seed" \
      "data.root=$TRAIN_DIR" \
      "data.reference_root=$REF_DIR"
  done
done

echo
echo "==> Risultati in $RESULTS_DIR/"
echo "==> Rigenera le figure della tesi con:"
echo "        python -m tesi_gan.cli export-figures"
