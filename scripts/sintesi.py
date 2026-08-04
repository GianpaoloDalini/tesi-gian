#!/usr/bin/env python3
"""Sintesi compatta dei risultati, in una schermata, più un grafico per la tesi.

    python scripts/sintesi.py experiments/traiettoria-128
    python scripts/sintesi.py experiments/traiettoria-128 --escludi can-seed1
    python scripts/sintesi.py experiments/results-64 --no-grafico

Sostituisce la lettura a scorrimento di `traiettoria.py`, che stampa tutto e
costringe a cercare i numeri. Qui restano solo le tre cose che servono per
decidere: una riga per run, le medie per condizione con la dispersione, e i
riferimenti di lettura.

Funziona sia su una cartella di **traiettorie** (più checkpoint per run) sia su una
di **risultati singoli**. Nel primo caso seleziona per ciascun run il checkpoint con
**FID minimo**, regola identica per tutti — vedi la motivazione in
`experiments/registry.md`, sezione sulla revisione del criterio.

Produce anche `traiettoria-{res}.png`: FID e ambiguità in funzione dell'epoca, una
curva per run, colorate per condizione. È la figura che rende visibile in un colpo
d'occhio sia l'effetto sia le degenerazioni, ed è direttamente utilizzabile nel
capitolo dei risultati.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics as st
from pathlib import Path

CAMPI = (
    ("fid", "FID", 1, "↓"),
    ("inception_score_mean", "IS", 2, "↑"),
    ("judge_entropy_normalized", "ambiguità", 3, "↑"),
    ("style_coverage_entropy_normalized", "copertura", 3, "—"),
)


def carica(directory: Path) -> dict[str, list[dict]]:
    per_run: dict[str, list[dict]] = {}
    for percorso in sorted(directory.glob("*.json")):
        try:
            d = json.loads(percorso.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        trovato = re.search(r"epoch_(\d+)", percorso.stem)
        d["_epoca"] = int(trovato.group(1)) if trovato else int(d.get("epoca", 0))
        per_run.setdefault(f"{d['condizione']}-seed{d['seed']}", []).append(d)
    for punti in per_run.values():
        punti.sort(key=lambda x: x["_epoca"])
    return per_run


def seleziona(punti: list[dict]) -> dict:
    """Checkpoint con FID minimo. Un solo punto: nessuna scelta da fare."""
    return min(punti, key=lambda d: d.get("fid") if d.get("fid") is not None else float("inf"))


def _val(d: dict, chiave: str, dec: int, larghezza: int) -> str:
    v = d.get(chiave)
    return f"{'—':>{larghezza}}" if v is None else f"{v:>{larghezza}.{dec}f}"


def stampa(per_run: dict[str, list[dict]], esclusi: set[str], titolo: str) -> None:
    print(f"\n{titolo}")
    print("=" * 62)

    multipunto = any(len(p) > 1 for p in per_run.values())
    intestazione = f"{'run':<15}" + ("epoca".rjust(6) if multipunto else "")
    intestazione += "".join(f"{n:>11}" for _, n, _, _ in CAMPI)
    print(intestazione)
    print("-" * 62)

    scelti: dict[str, list[dict]] = {}
    for nome in sorted(per_run):
        d = seleziona(per_run[nome])
        riga = f"{nome:<15}" + (f"{d['_epoca']:>6}" if multipunto else "")
        riga += "".join(_val(d, c, dec, 11) for c, _, dec, _ in CAMPI)

        degenerato = (d.get("inception_score_mean") or 9) < 2.0
        if degenerato:
            riga += "  degenerato"
        elif nome in esclusi:
            riga += "  escluso"
        print(riga)

        if nome not in esclusi and not degenerato:
            scelti.setdefault(d["condizione"], []).append(d)

    print("-" * 62)
    for condizione in ("dcgan", "can"):
        gruppo = scelti.get(condizione, [])
        if not gruppo:
            continue
        riga = f"{condizione.upper():<15}" + ("".rjust(6) if multipunto else "")
        for chiave, _, dec, _ in CAMPI:
            valori = [d[chiave] for d in gruppo if d.get(chiave) is not None]
            if not valori:
                riga += f"{'—':>11}"
            elif len(valori) > 1:
                riga += f"{st.mean(valori):>7.{dec}f}±{st.stdev(valori):<3.{dec}f}"
            else:
                riga += f"{st.mean(valori):>11.{dec}f}"
        print(riga + f"  (n={len(gruppo)})")

    campione = next(iter(next(iter(per_run.values()))))
    reali = campione.get("judge_entropy_real_normalized")
    if reali is not None:
        print(
            f"\nambiguità: reali {reali:.3f} · soffitto 1.000 · "
            f"giudice accurato al {campione.get('judge_val_accuracy', 0):.1%}"
        )
    print("i run con IS < 2,0 sono esclusi dalle medie: criterio dichiarato, "
          "applicato a entrambe le condizioni\n")


def grafico(per_run: dict[str, list[dict]], destinazione: Path) -> Path | None:
    """FID e ambiguità in funzione dell'epoca, una curva per run."""
    if not any(len(p) > 1 for p in per_run.values()):
        return None
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    colori = {"dcgan": "#4c72b0", "can": "#dd8452"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

    for nome, punti in sorted(per_run.items()):
        condizione = punti[0]["condizione"]
        epoche = [d["_epoca"] for d in punti]
        colore = colori.get(condizione, "gray")
        ax1.plot(epoche, [d.get("fid") for d in punti], "o-", ms=3,
                 color=colore, alpha=0.75, label=nome)
        ax2.plot(epoche, [d.get("judge_entropy_normalized") for d in punti], "o-",
                 ms=3, color=colore, alpha=0.75)

    reali = next(iter(next(iter(per_run.values())))).get("judge_entropy_real_normalized")
    if reali is not None:
        ax2.axhline(reali, ls="--", c="gray", lw=1)
        ax2.text(ax2.get_xlim()[1], reali, " arte reale", va="center", fontsize=8, c="gray")

    ax1.set_yscale("log")
    ax1.set_xlabel("epoca"); ax1.set_ylabel("FID (scala log)")
    ax1.set_title("Fedeltà — più basso è meglio")
    ax2.set_xlabel("epoca"); ax2.set_ylabel("entropia / log K")
    ax2.set_title("Ambiguità secondo il giudice terzo")

    # Una voce per condizione, non per run: sei etichette renderebbero la
    # legenda più grande del grafico.
    from matplotlib.lines import Line2D
    ax1.legend(handles=[Line2D([], [], color=c, label=n.upper())
                        for n, c in colori.items()], fontsize=8)

    fig.tight_layout()
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destinazione, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return destinazione


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--escludi", nargs="*", default=[])
    parser.add_argument("--no-grafico", action="store_true")
    parser.add_argument("--figure-dir", type=Path, default=Path("thesis/figures/generated"))
    args = parser.parse_args()

    per_run = carica(args.results_dir)
    if not per_run:
        print(f"Nessun risultato in {args.results_dir}")
        return 1

    risoluzione = re.search(r"(\d+)$", args.results_dir.name)
    etichetta = f"{risoluzione.group(1)}px" if risoluzione else args.results_dir.name
    stampa(per_run, set(args.escludi), f"IMPIANTO {etichetta} — {len(per_run)} run")

    if not args.no_grafico:
        prodotto = grafico(per_run, args.figure_dir / f"traiettoria-{etichetta}.png")
        if prodotto:
            print(f"grafico: {prodotto}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
