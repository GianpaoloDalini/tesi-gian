#!/usr/bin/env bash
# ============================================================================
#  Preparazione dell'ambiente su un servizio di training remoto che clona
#  il repository da GitHub (Colab, Kaggle, Lightning AI, RunPod, ...).
#
#  Uso tipico in una cella di notebook:
#     !git clone https://github.com/<utente>/<repo>.git && \
#      bash <repo>/scripts/bootstrap_remote.sh
#
#  L'API key di Weights & Biases NON va scritta qui: si passa come variabile
#  d'ambiente WANDB_API_KEY, oppure tramite i secrets del servizio.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Repository: $REPO_ROOT"
echo "==> Commit:     $(git rev-parse --short HEAD 2>/dev/null || echo 'non disponibile')"

echo "==> Installazione del package in editable mode"
pip install -q -e .

if [[ -f requirements-lock.txt ]]; then
  echo "==> Applicazione delle versioni bloccate"
  pip install -q -r requirements-lock.txt
fi

if [[ -z "${WANDB_API_KEY:-}" ]]; then
  echo "!!! WANDB_API_KEY non impostata: il run non verra' tracciato."
  echo "!!! Impostala prima di lanciare il training, altrimenti i risultati"
  echo "!!! non saranno riconducibili a un esperimento registrato."
fi

echo "==> Ambiente:"
python -c "import torch; print(f'  torch {torch.__version__} | CUDA disponibile: {torch.cuda.is_available()}')"

echo "==> Pronto. Lancia il training con:"
echo "    python -m tesi_gan.cli train experiment=<nome>"
