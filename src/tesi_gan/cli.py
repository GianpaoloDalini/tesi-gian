"""Punto di ingresso unico degli esperimenti.

    python -m tesi_gan.cli train experiment=<nome>
    python -m tesi_gan.cli evaluate run_id=<id>
    python -m tesi_gan.cli export-figures

Ogni comando legge la configurazione da configs/ tramite Hydra: nessun
iperparametro va passato modificando il codice sorgente.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tesi-gan", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_train = sub.add_parser("train", help="Addestra un modello")
    p_train.add_argument("--allow-dirty", action="store_true",
                         help="Consente il training con modifiche non committate (sconsigliato)")

    sub.add_parser("evaluate", help="Calcola le metriche su un run esistente")
    sub.add_parser("export-figures", help="Rigenera le figure della tesi")

    args, overrides = parser.parse_known_args(argv)

    if args.command == "train":
        raise NotImplementedError(
            "Da implementare dopo aver deciso l'impianto sperimentale "
            "(vedi docs/decisions/0003-impianto-sperimentale.md)."
        )
    if args.command == "evaluate":
        raise NotImplementedError("Da implementare insieme alle metriche scelte.")
    if args.command == "export-figures":
        raise NotImplementedError("Da implementare quando esisteranno i primi risultati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
