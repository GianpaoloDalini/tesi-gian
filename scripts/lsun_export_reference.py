#!/usr/bin/env python3
# ============================================================================
#  Esportazione di riferimento: da database LSUN (lmdb) a cartella di JPEG.
#
#  Contesto: ArtBench-10 offre una versione "original size, per stile" in
#  formato LSUN (vedi ADR-0006, aggiornamento 2026-09-14, e V-011 in
#  docs/registro-decisioni.md). Questo script implementa lo schema standard
#  di esportazione LSUN (ogni voce del database e' una coppia chiave/bytes
#  JPEG) -- e' il formato usato dal toolkit ufficiale di LSUN (fyu/lsun).
#
#  NON ANCORA VERIFICATO contro i file reali scaricati da ArtBench: prima di
#  lanciarlo su uno stile intero, provalo su un campione piccolo e controlla
#  a occhio che le immagini esportate abbiano senso (sono davvero dipinti
#  dello stile atteso, non rumore o errori di decodifica).
#
#  Uso:
#      pip install lmdb opencv-python-headless
#      python3 scripts/lsun_export_reference.py \
#          --source /workspace/artbench-original-raw/ukiyo_e \
#          --dest   /workspace/artbench-original/ukiyo_e \
#          --limit  50   # per il campione di prova; ometti per esportare tutto
# ============================================================================
import argparse
import os
import sys

import cv2
import lmdb
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="cartella del database lmdb scaricato")
    parser.add_argument("--dest", required=True, help="cartella di destinazione per i JPEG")
    parser.add_argument("--limit", type=int, default=None, help="numero massimo di immagini (per un campione di prova)")
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        sys.exit(f"!!! {args.source} non esiste o non e' una cartella")

    os.makedirs(args.dest, exist_ok=True)

    env = lmdb.open(args.source, readonly=True, lock=False, readahead=False, max_readers=1)
    esportate = 0
    saltate = 0
    with env.begin() as txn:
        cursor = txn.cursor()
        for i, (key, val) in enumerate(cursor):
            if args.limit is not None and i >= args.limit:
                break
            img = cv2.imdecode(np.frombuffer(val, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                saltate += 1
                continue
            out_path = os.path.join(args.dest, f"{i:06d}.jpg")
            cv2.imwrite(out_path, img)
            esportate += 1

    print(f"Esportate {esportate} immagini in {args.dest} ({saltate} voci non decodificabili come JPEG, da investigare se molte)")
    if esportate == 0:
        print("!!! Nessuna immagine esportata: il formato del database potrebbe differire "
              "da quello atteso. Ispeziona una voce a mano (chiave/valore) prima di insistere.")


if __name__ == "__main__":
    main()
