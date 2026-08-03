#!/usr/bin/env bash
# ============================================================================
#  Impianto sperimentale completo: sei run (ADR-0003, D-010).
#
#      bash scripts/run_impianto.sh
#
#  Due condizioni — DCGAN di controllo e CAN sperimentale — per tre seed.
#  Le condizioni si alternano seed per seed invece di eseguire prima tutte le
#  DCGAN: se la sessione remota cade a meta', restano coppie complete e
#  confrontabili invece di tre run di una sola condizione.
#
#  I dati vengono letti dal disco locale, non dal volume di rete: misurato il
#  2026-08-03, 3,6 s per epoca contro 44 s, cioe' dodici volte piu' veloce.
#  Il collo di bottiglia sono i 30.000 file piccoli serviti a ogni epoca, non
#  la GPU.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SEEDS="${SEEDS:-1 2 3}"
FAST_DIR="${FAST_DIR:-/dev/shm}"
TRAIN_SRC="${TRAIN_SRC:-data/processed}"
REF_SRC="${REF_SRC:-data/processed_test}"

TRAIN_DIR="$FAST_DIR/$(basename "$TRAIN_SRC")"
REF_DIR="$FAST_DIR/$(basename "$REF_SRC")"

echo "==> Repository: $REPO_ROOT"
echo "==> Commit:     $(git rev-parse --short HEAD)"

# Un working tree sporco fa fallire il primo `train` per via di
# assert_clean_tree. Meglio accorgersene subito che dopo mezz'ora di attesa.
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo "!!! Working tree sporco: committa prima di lanciare l'impianto."
  echo "!!! Un run non riconducibile a un commit non e' citabile in tesi."
  exit 1
fi

# --- Dati sul disco veloce --------------------------------------------------
# `/dev/shm` e' un disco in RAM: si svuota allo spegnimento del pod, quindi la
# copia va rifatta a ogni sessione. E' una copia, non uno spostamento.
for pair in "$TRAIN_SRC:$TRAIN_DIR" "$REF_SRC:$REF_DIR"; do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if [[ -d "$dst" ]]; then
    echo "==> Gia' presente: $dst"
  else
    echo "==> Copia $src -> $dst (qualche minuto: sono decine di migliaia di file)"
    cp -r "$src" "$dst"
  fi
done

echo "==> Immagini di addestramento: $(find "$TRAIN_DIR" -name '*.jpg' | wc -l)"
echo "==> Immagini di riferimento:   $(find "$REF_DIR" -name '*.jpg' | wc -l)"

if [[ -z "${WANDB_API_KEY:-}" ]]; then
  echo "!!! WANDB_API_KEY non impostata: i run NON saranno tracciati e i loro"
  echo "!!! numeri non sono citabili in tesi (CLAUDE.md §6). Interrompo."
  exit 1
fi

OVERRIDES=(
  "data.root=$TRAIN_DIR"
  "data.reference_root=$REF_DIR"
)

# --- I sei run --------------------------------------------------------------
INIZIO=$(date +%s)

for seed in $SEEDS; do
  for esperimento in e1-dcgan-baseline e2-can-confronto; do
    echo
    echo "============================================================"
    echo "  $esperimento — seed $seed"
    echo "============================================================"
    python -m tesi_gan.cli train \
      "experiment=$esperimento" \
      "seed=$seed" \
      "${OVERRIDES[@]}"
  done
done

DURATA=$(( $(date +%s) - INIZIO ))
echo
echo "==> Sei run completati in $((DURATA / 60)) minuti."
echo "==> Ora valuta i checkpoint con lo STESSO --n-samples per tutti:"
echo "        bash scripts/valuta_impianto.sh"
echo "==> E registra i run_id in experiments/registry.md."
