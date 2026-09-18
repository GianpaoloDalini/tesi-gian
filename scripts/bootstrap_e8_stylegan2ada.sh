#!/usr/bin/env bash
# ============================================================================
#  E8 — Pilota StyleGAN2-ADA in transfer learning (ADR-0006, D-027).
#
#  ILLUSTRATIVO, fuori da ADR-0003: non tocca l'impianto DCGAN/CAN, non ne
#  condivide il codice (tesi_gan). Usa il repository ufficiale NVlabs.
#
#  Uso su un pod RunPod (RTX 4090), dentro il Network Volume (di norma
#  montato su /workspace, vedi data/README.md):
#
#      git clone https://github.com/<utente>/tesi-gian.git   # se non gia' clonato
#      bash tesi-gian/scripts/bootstrap_e8_stylegan2ada.sh
#
#  QUESTO SCRIPT NON ADDESTRA A PIENA SCALA. Fa tre cose, in ordine, e si
#  ferma dopo ciascuna finche' non confermi di voler proseguire (nessun
#  euro speso senza controllo):
#
#    1. prepara l'ambiente e clona stylegan2-ada-pytorch (repo ufficiale);
#    2. DIAGNOSTICA: misura la risoluzione reale delle immagini sorgente
#       disponibili -- e' il controllo che risolve V-011, non un dettaglio.
#       Se la sorgente non regge il target dichiarato (1024x1024), lo dice
#       qui, PRIMA di spendere GPU, invece di scoprirlo a fine pilota.
#       ArtBench-10 offre anche una versione "original size" (LSUN, per
#       stile) via Google Drive, oltre al pacchetto a 256x256 usato finora
#       (vedi ADR-0006, aggiornamento 2026-09-14) -- e' la prima fonte da
#       provare, la diagnostica dice se regge davvero il target.
#    3. lancia un pilota breve (poche centinaia di kimg) per misurare
#       tempo/costo REALI -- non si stima a tavolino (CLAUDE.md).
#
#  Dopo il pilota: registra i numeri in experiments/registry.md (sezione
#  "Esperimento E8"), NON in questo script e NON a memoria.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="${WORKSPACE:-/workspace}"
SG2ADA_DIR="${SG2ADA_DIR:-$WORKSPACE/stylegan2-ada-pytorch}"
SG2ADA_COMMIT="${SG2ADA_COMMIT:-}"   # vuoto = HEAD del default branch, poi si stampa l'hash risolto

# Stile scelto per il pilota. ukiyo_e e' il candidato naturale (vedi ADR-0006:
# precedente diretto nel progetto pubblico "ukiyo-e-faces" di Justin Pinkney),
# ma resta una scelta di Gian, non imposta da questo script.
STILE="${STILE:-ukiyo_e}"

# Sorgente delle immagini per il pilota. Tre opzioni possibili, in ordine di
# preferenza (vedi ADR-0006/V-011):
#   (1) ArtBench-10 "original size" (LSUN, per stile) -- STEP 1B qui sotto la
#       scarica ed estrae in $WORKSPACE/artbench-original/$STILE; se esiste
#       gia', il default la usa automaticamente.
#   (2) il pacchetto ArtBench-10 a 256x256 gia' preparato per il progetto
#       (ADR-0004) -- fallback se (1) non e' stata preparata o non regge.
#   (3) un sottoinsieme dedicato ad alta risoluzione con licenza di pubblico
#       dominio VERIFICATA (stesso standard di V-007) -- passa SOURCE_DIR a
#       quella cartella esplicitamente.
_ARTBENCH_ORIGINAL="$WORKSPACE/artbench-original/$STILE"
_ARTBENCH_256="$REPO_ROOT/data/raw/artbench-10-imagefolder-split/train/$STILE"
if [[ -z "${SOURCE_DIR:-}" ]]; then
  if [[ -d "$_ARTBENCH_ORIGINAL" ]]; then
    SOURCE_DIR="$_ARTBENCH_ORIGINAL"
  else
    SOURCE_DIR="$_ARTBENCH_256"
    echo "!!! Uso il pacchetto a 256x256 (fallback): $_ARTBENCH_ORIGINAL non trovata."
    echo "!!! Vedi STEP 1B qui sotto per scaricare la versione 'original size'"
    echo "!!! PRIMA di fidarti di questa diagnostica -- e' la fonte da preferire."
  fi
fi

# Target dichiarato (ADR-0006). Lo step 2 puo' suggerire di rivederlo: non
# lo fa da solo, la decisione resta a Gian dopo aver visto il numero.
TARGET_RES="${TARGET_RES:-1024}"

echo "==> Repository tesi: $REPO_ROOT"
echo "==> Commit tesi:     $(cd "$REPO_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo 'non disponibile')"
echo "==> Workspace:       $WORKSPACE"
echo "==> Stile pilota:    $STILE"
echo "==> Sorgente immagini: $SOURCE_DIR"
echo "==> Target dichiarato: ${TARGET_RES}x${TARGET_RES}"
echo

# ----------------------------------------------------------------------------
# STEP 1 — ambiente + clone del repository ufficiale
# ----------------------------------------------------------------------------
echo "=========================================================================="
echo " STEP 1/3 — Ambiente e repository ufficiale"
echo "=========================================================================="

mkdir -p "$WORKSPACE"

python3 -c "import torch; print(f'torch {torch.__version__} | CUDA disponibile: {torch.cuda.is_available()}')" \
  || { echo "!!! torch non disponibile in questo ambiente. Installalo prima di continuare."; exit 1; }

if ! command -v nvcc >/dev/null 2>&1; then
  echo "!!! nvcc non trovato. stylegan2-ada-pytorch compila operatori CUDA custom"
  echo "!!! al primo uso (torch_utils/ops): senza un compilatore CUDA/gcc coerente"
  echo "!!! con la versione di torch installata, il training fallisce alla prima"
  echo "!!! iterazione, non all'avvio. Verifica la toolchain PRIMA di lanciare il"
  echo "!!! pilota (README/FAQ del repo ufficiale hanno la matrice di versioni"
  echo "!!! compatibili) -- non e' un problema che si risolve a tentativi."
fi

if [[ ! -d "$SG2ADA_DIR" ]]; then
  echo "==> Clono NVlabs/stylegan2-ada-pytorch in $SG2ADA_DIR"
  git clone https://github.com/NVlabs/stylegan2-ada-pytorch.git "$SG2ADA_DIR"
else
  echo "==> Repository gia' presente in $SG2ADA_DIR, non lo ri-clono"
fi

if [[ -n "$SG2ADA_COMMIT" ]]; then
  (cd "$SG2ADA_DIR" && git checkout "$SG2ADA_COMMIT")
fi
RESOLVED_COMMIT="$(cd "$SG2ADA_DIR" && git rev-parse --short HEAD)"
echo "==> Commit stylegan2-ada-pytorch effettivo: $RESOLVED_COMMIT"
echo "!!! Registra questo hash in experiments/registry.md insieme al run_id:"
echo "!!! senza, il run non e' piu' riproducibile fra tre mesi (CLAUDE.md §6)."

echo
echo "==> URL dei checkpoint pretrained ufficiali, letti dal README del repo appena"
echo "==> clonato (non incollati a mano in questo script, per non rischiare un URL"
echo "==> sbagliato o non piu' valido):"
grep -oE 'https://[^ )]+\.pkl' "$SG2ADA_DIR/README.md" | sort -u || true
echo
echo "==> Scegli il checkpoint di partenza (env PRETRAINED_URL) in base al target"
echo "==> deciso allo STEP 2 sotto: se resti a 1024x1024, il candidato e' quello"
echo "==> che contiene 'ffhq' e '1024' nel nome; se il target scende (es. 512),"
echo "==> valuta un checkpoint gia' a quella risoluzione (es. afhq, 'wild'/'cat'/'dog')"
echo "==> invece di ffhq-1024 -- risparmia una fase di adattamento della risoluzione."

# ----------------------------------------------------------------------------
# STEP 1B — ArtBench-10 "original size" (LSUN, per stile): prima fonte da
# provare (ADR-0006, aggiornamento 2026-09-14). MANUALE apposta: e' il punto
# esatto in cui V-011 va verificato, non assunto -- niente da automatizzare
# ciecamente qui.
# ----------------------------------------------------------------------------
echo
echo "=========================================================================="
echo " STEP 1B — ArtBench-10 'original size' (facoltativo ma consigliato)"
echo "=========================================================================="

if [[ -d "$_ARTBENCH_ORIGINAL" ]]; then
  echo "==> Gia' presente in $_ARTBENCH_ORIGINAL, salto il download."
else
  echo "==> Non ancora scaricata. Verificato il 2026-09-14 (non assunto): la"
  echo "==> cartella Google Drive ufficiale 'lsun' (linkata dal README di"
  echo "==> https://github.com/liaopeiyuan/artbench) contiene UN FILE .tar PER"
  echo "==> STILE (non tante immagini singole). Per '$STILE' il file si chiama"
  echo "==> '${STILE}_lmdb.tar' -- dimensione osservata per i sei stili del"
  echo "==> progetto: ukiyo_e 8,16 GB, renaissance 10,06 GB, baroque 8,89 GB,"
  echo "==> art_nouveau 7,85 GB, expressionism 2,54 GB, impressionism 2,87 GB."
  echo "==> Con ~6.000 immagini/stile fa circa 1-1,7 MB/immagine in media --"
  echo "==> molto sopra i 20-50 KB tipici di un JPEG a 256x256: segnale forte"
  echo "==> ma NON una misura (dipende anche dalla compressione), vedi V-011."
  echo
  echo "!!! NON eseguito automaticamente: apri la cartella 'lsun' su Google"
  echo "!!! Drive, click destro su '${STILE}_lmdb.tar' -> 'Copia link', poi:"
  echo
  echo "    pip install gdown lmdb opencv-python-headless"
  echo
  echo "    # 1. scarica il .tar dello stile scelto (usa l'ID dal link copiato:"
  echo "    #    drive.google.com/file/d/<ID>/view -> --id <ID>)"
  echo "    mkdir -p \"$WORKSPACE/artbench-original-raw\""
  echo "    gdown --id <ID_DEL_FILE> -O \"$WORKSPACE/artbench-original-raw/${STILE}_lmdb.tar\""
  echo "    tar -xf \"$WORKSPACE/artbench-original-raw/${STILE}_lmdb.tar\" -C \"$WORKSPACE/artbench-original-raw/\""
  echo
  echo "    # 2. PRIMA un campione piccolo (verifica che l'estrazione funzioni"
  echo "    #    e che le immagini abbiano senso, prima di lanciarla su tutto):"
  echo "    python3 scripts/lsun_export_reference.py \\"
  echo "        --source \"$WORKSPACE/artbench-original-raw/<cartella lmdb estratta>\" \\"
  echo "        --dest   \"$_ARTBENCH_ORIGINAL\" --limit 20"
  echo "    # ispeziona a occhio le 20 immagini in $_ARTBENCH_ORIGINAL, poi"
  echo "    # ripeti senza --limit per esportarle tutte."
fi

# ----------------------------------------------------------------------------
# STEP 2 — DIAGNOSTICA: la sorgente regge davvero il target? (risolve V-011)
# ----------------------------------------------------------------------------
echo
echo "=========================================================================="
echo " STEP 2/3 — Diagnostica risoluzione sorgente (V-011, ADR-0006)"
echo "=========================================================================="

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "!!! $SOURCE_DIR non esiste."
  echo "!!! Se e' il sottoinsieme ArtBench-10, preparalo prima come da"
  echo "!!! data/README.md. Se e' un sottoinsieme dedicato ad alta risoluzione,"
  echo "!!! ricorda: fonte di pubblico dominio VERIFICATA prima di scaricare"
  echo "!!! qualunque cosa (stesso standard di V-007/ADR-0004), non improvvisata."
  exit 1
fi

python3 - "$SOURCE_DIR" "$TARGET_RES" << 'PYEOF'
import sys, os
from pathlib import Path
try:
    from PIL import Image
except ImportError:
    print("!!! Pillow non installato: pip install pillow"); sys.exit(1)

src, target = Path(sys.argv[1]), int(sys.argv[2])
files = [p for p in src.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
if not files:
    print(f"!!! Nessuna immagine trovata in {src}"); sys.exit(1)

sides = []
for p in files[:500]:  # campione, non serve leggerle tutte per la diagnosi
    try:
        with Image.open(p) as im:
            sides.append(min(im.size))
    except Exception:
        pass

sides.sort()
n = len(sides)
mediana = sides[n // 2]
sotto_target = sum(1 for s in sides if s < target)

print(f"==> Campione: {n} immagini su {len(files)} totali in {src}")
print(f"==> Lato corto minimo: {sides[0]}px · mediana: {mediana}px · massimo: {sides[-1]}px")
print(f"==> Immagini sotto il target {target}px: {sotto_target}/{n} ({100*sotto_target/n:.0f}%)")
print()
if mediana < target:
    print(f"!!! ATTENZIONE (V-011): la mediana ({mediana}px) e' SOTTO il target")
    print(f"!!! dichiarato ({target}px). Addestrare a {target}px da questa sorgente")
    print(f"!!! significa upscalare: la rete impara a riprodurre dettaglio che non")
    print(f"!!! e' mai stato nella sorgente. Non e' un errore dello script, e' il")
    print(f"!!! rischio metodologico che ADR-0006/V-011 chiedevano di controllare")
    print(f"!!! PRIMA del run completo.")
    print()
    print(f"!!! Due strade, entrambe legittime se dichiarate (vedi ADR-0006):")
    print(f"!!!   (a) abbassa TARGET_RES a un valore che questa sorgente regge")
    print(f"!!!       davvero (es. {mediana}px o la potenza di 2 piu' vicina sotto),")
    print(f"!!!       e usa un checkpoint pretrained a quella risoluzione;")
    print(f"!!!   (b) usa SOURCE_DIR per puntare a un sottoinsieme dedicato ad alta")
    print(f"!!!       risoluzione, con licenza pubblico-dominio VERIFICATA.")
else:
    print(f"==> La sorgente regge il target dichiarato ({target}px). Si puo' procedere.")
PYEOF

echo
read -r -p "Procedere allo STEP 3 (pilota, consuma GPU reale)? [s/N] " CONFERMA
if [[ "${CONFERMA,,}" != "s" ]]; then
  echo "==> Fermato qui su richiesta. Nessun costo GPU sostenuto oltre a questa diagnosi."
  exit 0
fi

# ----------------------------------------------------------------------------
# STEP 3 — pilota breve: tempo/costo REALI, non stimati
# ----------------------------------------------------------------------------
echo
echo "=========================================================================="
echo " STEP 3/3 — Pilota (kimg ridotto, per misurare tempo/costo reali)"
echo "=========================================================================="

PRETRAINED_URL="${PRETRAINED_URL:?Imposta PRETRAINED_URL con uno degli URL stampati allo STEP 1}"
DATASET_ZIP="$WORKSPACE/e8-${STILE}-${TARGET_RES}.zip"
OUTDIR="$REPO_ROOT/experiments/e8-stylegan2ada-pilota"
PILOT_KIMG="${PILOT_KIMG:-200}"   # breve apposta: e' un pilota, non il run finale

mkdir -p "$OUTDIR"

echo "==> Preparazione dataset in formato stylegan2-ada (dataset_tool.py)"
python3 "$SG2ADA_DIR/dataset_tool.py" \
  --source="$SOURCE_DIR" \
  --dest="$DATASET_ZIP" \
  --width="$TARGET_RES" --height="$TARGET_RES"

echo "==> Lancio pilota: kimg=$PILOT_KIMG, cfg=auto (si adatta a una singola GPU),"
echo "==> aug=ada, mirror=1, resume dal checkpoint pretrained scelto"
echo "==> Comando eseguito (annotalo nel run_id/registry.md):"
set -x
python3 "$SG2ADA_DIR/train.py" \
  --outdir="$OUTDIR" \
  --data="$DATASET_ZIP" \
  --gpus=1 \
  --cfg=auto \
  --resume="$PRETRAINED_URL" \
  --aug=ada \
  --mirror=1 \
  --kimg="$PILOT_KIMG" \
  --snap=4
set +x

echo
echo "=========================================================================="
echo " Pilota lanciato. Al termine:"
echo "=========================================================================="
echo "  1. leggi $OUTDIR/<run>/log.txt per il kimg/sec reale e stima il costo"
echo "     dell'eventuale run completo moltiplicando per il prezzo/ora del pod;"
echo "  2. guarda le griglie fakes*.png: e' qui che si vede se l'upscaling"
echo "     dalla sorgente (STEP 2) produce dettaglio reale o solo sfocatura;"
echo "  3. registra run_id, commit ($RESOLVED_COMMIT), checkpoint di partenza,"
echo "     target di risoluzione EFFETTIVO, kimg, tempo e costo in"
echo "     experiments/registry.md, sezione 'Esperimento E8' -- sostituendo i"
echo "     TODO, non aggiungendo un'altra tabella;"
echo "  4. decidi go/no-go per il run completo sulla base di 1 e 2, non prima."
