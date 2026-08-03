#!/usr/bin/env python3
"""Raccoglie gli identificativi dei run da Weights & Biases.

    python scripts/raccogli_run_id.py
    python scripts/raccogli_run_id.py --markdown

**A cosa serve.** `CLAUDE.md` §6 impone che ogni numero riportato in tesi sia
rintracciabile a un `run_id`, e che la corrispondenza viva in
`experiments/registry.md`. Senza, la catena `commit → run → checkpoint → figura →
numero in tesi` si interrompe proprio nell'anello che la commissione puo' chiedere
di verificare.

Gli identificativi vengono stampati a fine training, ma finiscono nello scrollback
del terminale e si perdono. Questo script li ripesca dal servizio, insieme al commit
con cui ciascun run e' stato lanciato.

`--markdown` produce direttamente le righe da incollare nel registro.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="tesi-gan-creativita")
    parser.add_argument("--entity", default=None,
                        help="Se omesso, usa quella predefinita della API key")
    parser.add_argument("--markdown", action="store_true",
                        help="Stampa righe di tabella pronte per experiments/registry.md")
    args = parser.parse_args()

    try:
        import wandb
    except ImportError:
        print("wandb non installato: pip install wandb")
        return 1

    api = wandb.Api()
    percorso = f"{args.entity}/{args.project}" if args.entity else args.project

    try:
        runs = list(api.runs(percorso))
    except Exception as exc:  # noqa: BLE001
        print(f"Impossibile leggere il progetto {percorso!r}: {exc}")
        print("Verifica WANDB_API_KEY, oppure passa --entity esplicitamente.")
        return 1

    if not runs:
        print(f"Nessun run in {percorso!r}.")
        return 1

    def chiave(r):
        cfg = r.config or {}
        modello = (cfg.get("model") or {}).get("name", "?")
        return (str(modello), cfg.get("seed", 0))

    runs.sort(key=chiave)

    if args.markdown:
        print("| Run | run_id W&B | Commit | Stato | Epoche |")
        print("|---|---|---|---|---|")
        for r in runs:
            cfg = r.config or {}
            modello = (cfg.get("model") or {}).get("name", "?")
            commit = (cfg.get("provenance") or {}).get("commit", "")[:8]
            epoche = (r.summary or {}).get("epoch", "")
            print(
                f"| `{modello}-seed{cfg.get('seed', '?')}` | `{r.id}` | "
                f"`{commit}` | {r.state} | {epoche} |"
            )
    else:
        print(f"\nProgetto: {percorso}   ({len(runs)} run)\n")
        print(f"{'nome':<30}{'run_id':<12}{'commit':<11}{'stato':<10}{'epoche':>7}")
        print("-" * 72)
        for r in runs:
            cfg = r.config or {}
            commit = (cfg.get("provenance") or {}).get("commit", "")[:8]
            epoche = (r.summary or {}).get("epoch", "")
            print(f"{r.name:<30}{r.id:<12}{commit:<11}{r.state:<10}{str(epoche):>7}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
