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

# Risoluzione dell'impianto. I due impianti convivono: percorsi, dati e giudice
# sono separati, quindi lanciare il 128 non tocca nulla del 64.
#   RES=64  -> e1-dcgan-baseline / e2-can-confronto
#   RES=128 -> e3-dcgan-128      / e4-can-128
RES="${RES:-64}"

case "$RES" in
  64)  ESPERIMENTI="e1-dcgan-baseline e2-can-confronto"
       TRAIN_SRC="${TRAIN_SRC:-data/processed}"
       REF_SRC="${REF_SRC:-data/processed_test}" ;;
  128) ESPERIMENTI="e3-dcgan-128 e4-can-128"
       TRAIN_SRC="${TRAIN_SRC:-data/processed_128}"
       REF_SRC="${REF_SRC:-data/processed_test_128}" ;;
  *)   echo "!!! RES=$RES non prevista. Valori ammessi: 64, 128."; exit 1 ;;
esac

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

# --- Spazio su disco ---------------------------------------------------------
# Un checkpoint salva generatore, discriminatore E lo stato dei due ottimizzatori
# Adam, che triplica lo spazio dei soli pesi. A 128px le reti hanno quattro volte i
# parametri di 64px, quindi un checkpoint passa da ~80 MB a ~290 MB e i sei run
# dell'impianto da ~11 GB a ~22 GB.
#
# Questo controllo esiste perche' il 2026-08-03 il volume si e' riempito a meta'
# dell'impianto a 128: un run completo, uno troncato, quattro mai partiti. Il
# fabbisogno era stato calcolato sui numeri di 64px e non ricalcolato al cambio di
# risoluzione. Meglio saperlo adesso che dopo venti minuti di GPU.
if [[ "$RES" == "128" ]]; then
  RICHIESTI_GB=24
else
  RICHIESTI_GB=12
fi

DISPONIBILI_GB=$(df -BG --output=avail . 2>/dev/null | tail -1 | tr -dc '0-9')
if [[ -n "$DISPONIBILI_GB" && "$DISPONIBILI_GB" -lt "$RICHIESTI_GB" ]]; then
  echo "!!! Spazio insufficiente: ${DISPONIBILI_GB} GB liberi, ne servono ~${RICHIESTI_GB}"
  echo "!!! per i checkpoint dei sei run a ${RES}px."
  echo "!!!"
  echo "!!! Ingrandisci il Network Volume, oppure libera spazio: il tar di ArtBench e"
  echo "!!! data/raw non servono piu' una volta preparati i dati."
  echo "!!! Per procedere comunque: SALTA_CONTROLLO_DISCO=1"
  [[ "${SALTA_CONTROLLO_DISCO:-0}" == "1" ]] || exit 1
fi
echo "==> Spazio disponibile: ${DISPONIBILI_GB:-?} GB (stimati necessari: ${RICHIESTI_GB} GB)"

GIUDICE="experiments/style_judge-$RES/style_classifier.pt"
if [[ ! -f "$GIUDICE" ]]; then
  echo "!!! Giudice di stile assente per $RES px: $GIUDICE"
  echo "!!! Senza, l'ambiguita' non e' confrontabile fra DCGAN e CAN (ADR-0005)."
  echo "!!! Ogni risoluzione ha il suo giudice: entropie prodotte da classificatori"
  echo "!!! diversi non vanno nella stessa tabella. Addestralo con:"
  if [[ "$RES" == "64" ]]; then
    echo "!!!   python -m tesi_gan.cli train-style-classifier data=artbench"
  else
    echo "!!!   python -m tesi_gan.cli train-style-classifier data=artbench$RES"
  fi
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
  for esperimento in $ESPERIMENTI; do
    # La condizione si ricava dal nome dell'esperimento: e1/e3 sono DCGAN, e2/e4 CAN.
    case "$esperimento" in
      *dcgan*) condizione="dcgan" ;;
      *can*)   condizione="can" ;;
      *)       echo "!!! Esperimento non riconosciuto: $esperimento"; exit 1 ;;
    esac
    cartella="experiments/checkpoints/${condizione}-${RES}-seed${seed}"

    # Un run gia' concluso non si rifa'. Serve a riprendere un impianto interrotto
    # — per disco pieno, sessione caduta, GPU riassegnata — senza buttare le ore
    # gia' spese. `final.pt` esiste solo a training concluso, quindi un run
    # troncato viene correttamente rilanciato.
    if [[ -f "$cartella/final.pt" && "${FORZA:-0}" != "1" ]]; then
      echo
      echo "==> $esperimento seed $seed gia' completo, salto. (FORZA=1 per rifarlo)"
      continue
    fi

    echo
    echo "============================================================"
    echo "  $esperimento — seed $seed — ${RES}px"
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
