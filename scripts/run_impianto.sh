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

# --- Controlli preliminari --------------------------------------------------
# TUTTI i controlli stanno prima della copia dei dati, che dura minuti. Un
# controllo che costa un millisecondo non deve mai stare dopo un'operazione che
# costa minuti: la prima versione di questo script verificava la chiave W&B dopo
# la copia, e falliva quando l'attesa era gia' stata pagata.

if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo "!!! Working tree sporco: committa prima di lanciare l'impianto."
  echo "!!! Un run non riconducibile a un commit non e' citabile in tesi."
  exit 1
fi

if [[ -z "${WANDB_API_KEY:-}" ]]; then
  echo "!!! WANDB_API_KEY non impostata: i run NON sarebbero tracciati e i loro"
  echo "!!! numeri non sono citabili in tesi (CLAUDE.md §6)."
  echo "!!!"
  echo "!!!   export WANDB_API_KEY=<chiave da wandb.ai/authorize>"
  echo "!!!"
  echo "!!! Per non ripeterlo a ogni sessione, aggiungila alle variabili"
  echo "!!! d'ambiente del pod nella configurazione RunPod."
  exit 1
fi

for sorgente in "$TRAIN_SRC" "$REF_SRC"; do
  if [[ ! -d "$sorgente" ]]; then
    echo "!!! Dati assenti: $sorgente"
    echo "!!! Preparali con python -m tesi_gan.data.download (vedi data/README.md)."
    exit 1
  fi
done

if [[ ! -f experiments/style_judge/style_classifier.pt ]]; then
  echo "!!! Giudice di stile assente: senza, l'ambiguita' non e' confrontabile"
  echo "!!! fra DCGAN e CAN (ADR-0005). Addestralo con:"
  echo "!!!   python -m tesi_gan.cli train-style-classifier data=artbench"
  exit 1
fi

# --- Dati sul disco veloce --------------------------------------------------
# `/dev/shm` e' un disco in RAM: si svuota allo spegnimento del pod, quindi la
# copia va rifatta a ogni sessione. E' una copia, non uno spostamento.
#
# **La copia viene verificata, non data per fatta.** Interrompere un `cp -r` a
# meta' lascia una cartella che *esiste* ma e' incompleta: uno script che si
# limitasse a controllarne la presenza addestrerebbe su un dataset parziale
# senza alcun errore visibile, e i risultati sarebbero sbagliati in un modo
# impossibile da notare a posteriori. Si contano i file e si confrontano con
# l'originale.
copia_verificata() {
  local src="$1" dst="$2" attese effettive

  attese=$(find "$src" -name '*.jpg' | wc -l)

  if [[ -d "$dst" ]]; then
    effettive=$(find "$dst" -name '*.jpg' | wc -l)
    if [[ "$effettive" -eq "$attese" ]]; then
      echo "==> $dst gia' completo ($effettive immagini)"
      return 0
    fi
    echo "==> $dst incompleto ($effettive su $attese): lo rifaccio da capo"
    rm -rf "$dst"
  fi

  echo "==> Copia $src -> $dst ($attese file, qualche minuto)"
  cp -r "$src" "$dst"

  effettive=$(find "$dst" -name '*.jpg' | wc -l)
  if [[ "$effettive" -ne "$attese" ]]; then
    echo "!!! Copia incompleta: $effettive su $attese. Interrompo."
    exit 1
  fi
  echo "==> Copiate $effettive immagini"
}

copia_verificata "$TRAIN_SRC" "$TRAIN_DIR"
copia_verificata "$REF_SRC" "$REF_DIR"

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
