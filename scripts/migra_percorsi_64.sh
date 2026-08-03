#!/usr/bin/env bash
# ============================================================================
#  Migrazione una tantum dei percorsi dell'impianto a 64px.
#
#      bash scripts/migra_percorsi_64.sh          # mostra cosa farebbe
#      bash scripts/migra_percorsi_64.sh --esegui # rinomina davvero
#
#  I percorsi di output ora includono la risoluzione, perche' senza un impianto a
#  128 sovrascriverebbe quello a 64 in silenzio. Gli artefatti gia' prodotti usano
#  ancora il vecchio schema e non verrebbero piu' trovati:
#
#      experiments/checkpoints/dcgan-seed1  ->  dcgan-64-seed1
#      experiments/samples/can-seed3        ->  can-64-seed3
#      experiments/style_judge              ->  style_judge-64
#      experiments/results                  ->  results-64
#
#  Si rinomina, non si copia: gli artefatti sono grandi e i checkpoint sono
#  l'unica copia esistente dei run gia' eseguiti.
#
#  Di default lo script **non fa nulla** e si limita a elencare le operazioni.
#  Serve `--esegui` per applicarle: un rinomina sbagliato su questi file
#  costerebbe le ore di calcolo che li hanno prodotti.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ESEGUI=0
[[ "${1:-}" == "--esegui" ]] && ESEGUI=1

if [[ $ESEGUI -eq 0 ]]; then
  echo "=== SIMULAZIONE — nessuna modifica. Usa --esegui per applicare. ==="
fi
echo

rinomina() {
  local da="$1" a="$2"

  if [[ ! -e "$da" ]]; then
    return 0
  fi
  if [[ -e "$a" ]]; then
    echo "  SALTO   $da  ->  $a   (destinazione gia' esistente)"
    return 0
  fi

  echo "  rinomina $da  ->  $a"
  if [[ $ESEGUI -eq 1 ]]; then
    mv "$da" "$a"
  fi
}

echo "Checkpoint e campioni:"
for tipo in checkpoints samples; do
  for condizione in dcgan can; do
    for vecchia in "experiments/$tipo/$condizione"-seed*; do
      [[ -e "$vecchia" ]] || continue
      # Salta quelle gia' migrate, che contengono gia' la risoluzione.
      [[ "$vecchia" == *"-64-seed"* || "$vecchia" == *"-128-seed"* ]] && continue
      seed="${vecchia##*-seed}"
      rinomina "$vecchia" "experiments/$tipo/$condizione-64-seed$seed"
    done
  done
done

echo
echo "Giudice di stile e risultati:"
rinomina "experiments/style_judge" "experiments/style_judge-64"
rinomina "experiments/results" "experiments/results-64"

echo
if [[ $ESEGUI -eq 1 ]]; then
  echo "==> Fatto. Verifica con:"
  echo "        ls experiments/checkpoints/ experiments/style_judge-64/"
  echo "==> I risultati vanno rivalutati solo se cambiano le metriche, non i"
  echo "    percorsi: i JSON gia' prodotti restano validi in results-64/."
else
  echo "==> Nessuna modifica applicata. Rilancia con --esegui quando l'elenco torna."
fi
