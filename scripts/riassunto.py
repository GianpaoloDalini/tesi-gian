#!/usr/bin/env python3
"""Riassunto leggibile dei risultati dell'impianto.

    python scripts/riassunto.py
    python scripts/riassunto.py --escludi can-seed1

Legge i JSON prodotti da `tesi_gan.cli evaluate` e stampa le tre cose che servono
per leggere l'esperimento:

1. **Le metriche per run**, per vedere subito quali sono anomali.
2. **Media e dispersione per condizione**, che e' la forma in cui i numeri vanno in
   tesi. Con tre seed non si fanno test statistici seri, ma media e intervallo sono
   lo standard onesto in letteratura.
3. **La distribuzione degli stili predetti**, che distingue la fusione stilistica
   dal collasso su una zona generica — due situazioni che l'entropia per immagine
   non separa.

`--escludi` toglie un run dalle medie **senza cancellarlo**: resta stampato e
marcato. Un run collassato si documenta, non si nasconde (CLAUDE.md §6).
"""

from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path


def carica(directory: Path) -> list[dict]:
    risultati = []
    for percorso in sorted(directory.glob("*.json")):
        try:
            risultati.append(json.loads(percorso.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            print(f"!!! File illeggibile, ignorato: {percorso}")
    return risultati


def etichetta(r: dict) -> str:
    return f"{r['condizione']}-seed{r['seed']}"


def _fmt(valore, decimali=3, larghezza=9) -> str:
    return f"{'—':>{larghezza}}" if valore is None else f"{valore:>{larghezza}.{decimali}f}"


def tabella_run(risultati: list[dict], esclusi: set[str]) -> None:
    print(f"\n{'run':<16}{'FID':>9}{'IS':>7}{'ambiguita':>11}{'copertura':>11}   nota")
    print("-" * 70)
    for r in sorted(risultati, key=lambda x: (x["condizione"], x["seed"])):
        nome = etichetta(r)
        nota = "ESCLUSO dalle medie" if nome in esclusi else ""
        print(
            f"{nome:<16}"
            f"{_fmt(r.get('fid'), 1)}"
            f"{_fmt(r.get('inception_score_mean'), 2, 7)}"
            f"{_fmt(r.get('judge_entropy_normalized'), 3, 11)}"
            f"{_fmt(r.get('style_coverage_entropy_normalized'), 3, 11)}   {nota}"
        )


def tabella_condizioni(risultati: list[dict], esclusi: set[str]) -> None:
    print(f"\n{'=' * 70}")
    print("MEDIE PER CONDIZIONE (deviazione standard fra seed)")
    print("=" * 70)

    for condizione in ("dcgan", "can"):
        gruppo = [
            r for r in risultati
            if r["condizione"] == condizione and etichetta(r) not in esclusi
        ]
        if not gruppo:
            continue

        print(f"\n{condizione.upper()}  (n = {len(gruppo)})")
        for chiave, nome, decimali in (
            ("fid", "FID (piu' basso e' meglio)", 1),
            ("inception_score_mean", "Inception Score", 2),
            ("judge_entropy_normalized", "Ambiguita' (giudice terzo)", 3),
            ("style_coverage_entropy_normalized", "Copertura degli stili", 3),
        ):
            valori = [r[chiave] for r in gruppo if r.get(chiave) is not None]
            if not valori:
                continue
            media = st.mean(valori)
            if len(valori) > 1:
                print(f"   {nome:<32} {media:>8.{decimali}f}  ± {st.stdev(valori):.{decimali}f}")
            else:
                print(f"   {nome:<32} {media:>8.{decimali}f}  (un solo run)")

    riferimento = next(
        (r for r in risultati if r.get("judge_entropy_real_normalized") is not None), None
    )
    if riferimento:
        print(
            f"\nRiferimenti: arte reale {riferimento['judge_entropy_real_normalized']:.3f}"
            f" · soffitto 1.000 · accuratezza del giudice "
            f"{riferimento.get('judge_val_accuracy', float('nan')):.3f}"
        )


def distribuzione_stili(risultati: list[dict]) -> None:
    print(f"\n{'=' * 70}")
    print("DISTRIBUZIONE DEGLI STILI PREDETTI")
    print("=" * 70)
    print(
        "\nUna marginale piatta significa che il generatore copre tutti gli stili;\n"
        "una concentrata significa che ne produce solo alcuni, e parte dell'ambiguita'\n"
        "misurata sarebbe collasso su una zona generica invece che fusione stilistica."
    )

    for r in sorted(risultati, key=lambda x: (x["condizione"], x["seed"])):
        classi = r.get("style_coverage_classes")
        conteggi = r.get("style_coverage_counts")
        if not classi or not conteggi:
            continue

        totale = max(sum(conteggi), 1)
        attesa = 100.0 / len(classi)
        print(f"\n{etichetta(r)}   (atteso {attesa:.1f}% per stile)")
        for nome, n in sorted(zip(classi, conteggi), key=lambda x: -x[1]):
            percentuale = 100 * n / totale
            barra = "#" * int(round(percentuale / 2))
            print(f"   {nome:<16}{percentuale:>6.1f}%  {barra}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("experiments/results"))
    parser.add_argument(
        "--escludi", nargs="*", default=[],
        help="Run da togliere dalle medie, es. can-seed1. Restano stampati e marcati.",
    )
    args = parser.parse_args()

    risultati = carica(args.results_dir)
    if not risultati:
        print(f"Nessun risultato in {args.results_dir}. Lancia prima valuta_impianto.sh")
        return 1

    esclusi = set(args.escludi)
    tabella_run(risultati, esclusi)
    tabella_condizioni(risultati, esclusi)
    distribuzione_stili(risultati)

    if esclusi:
        print(
            f"\nNota: {', '.join(sorted(esclusi))} escluso dalle medie. "
            f"L'esclusione va motivata in experiments/registry.md: un run anomalo si "
            f"documenta, non si cancella."
        )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
