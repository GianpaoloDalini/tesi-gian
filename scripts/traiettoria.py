#!/usr/bin/env python3
"""Curva delle metriche lungo l'addestramento, e selezione del checkpoint.

    python scripts/traiettoria.py --results-dir experiments/traiettoria-128

Legge i JSON prodotti da `valuta_traiettoria.sh` e stampa, per ogni run, come FID
e ambiguita' evolvono attraverso i checkpoint salvati.

## La regola di selezione

Per ciascun run si sceglie il checkpoint con **FID minimo**, identicamente per
entrambe le condizioni. Non e' cherry-picking a tre condizioni:

1. la regola e' la stessa per ogni run;
2. la traiettoria completa viene pubblicata, non solo il punto scelto;
3. l'adozione del criterio e' datata e motivata in `experiments/registry.md`.

Il criterio e' stato adottato dopo aver osservato che `dcgan-seed1` a 128px
raggiunge ottima qualita' all'epoca 97 e collassa all'epoca 98: riportare l'epoca
100, come pre-registrato, avrebbe presentato come risultato un modello degenerato.

**Il FID e' la metrica di selezione, non l'ambiguita'.** Selezionare sull'ambiguita'
significherebbe scegliere il punto che favorisce l'ipotesi: sarebbe circolare.
Scegliendo sul FID si prende il checkpoint dove il modello genera meglio, e
l'ambiguita' viene poi letta li' — un criterio indipendente da cio' che si vuole
dimostrare, e semmai sfavorevole, visto che ci si attendeva che l'ambiguita'
crescesse al peggiorare della fedelta'.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics as st
from pathlib import Path


def epoca_da_nome(percorso: Path) -> int:
    """Ricava l'epoca dal nome del file. `final` diventa l'ultima."""
    if "final" in percorso.stem:
        return 10**6  # ordinato per ultimo, poi rimappato sull'epoca reale
    trovato = re.search(r"epoch_(\d+)", percorso.stem)
    return int(trovato.group(1)) if trovato else -1


def carica(directory: Path) -> dict[str, list[dict]]:
    per_run: dict[str, list[dict]] = {}
    for percorso in sorted(directory.glob("*.json"), key=epoca_da_nome):
        dati = json.loads(percorso.read_text(encoding="utf-8"))
        dati["_epoca"] = int(dati.get("epoca", epoca_da_nome(percorso)))
        dati["_file"] = percorso.name
        chiave = f"{dati['condizione']}-seed{dati['seed']}"
        per_run.setdefault(chiave, []).append(dati)

    for punti in per_run.values():
        punti.sort(key=lambda d: d["_epoca"])
    return per_run


def stampa_traiettorie(per_run: dict[str, list[dict]]) -> None:
    print(f"\n{'=' * 66}")
    print("TRAIETTORIE — come evolvono le metriche lungo l'addestramento")
    print("=" * 66)

    for nome, punti in sorted(per_run.items()):
        print(f"\n{nome}")
        print(f"  {'epoca':>6}{'FID':>9}{'IS':>7}{'ambiguita':>11}{'copertura':>11}")
        migliore = min(punti, key=lambda d: d.get("fid") or float("inf"))
        for d in punti:
            marcatore = "  <- FID minimo" if d is migliore else ""
            print(
                f"  {d['_epoca']:>6}{d.get('fid', float('nan')):>9.1f}"
                f"{d.get('inception_score_mean', float('nan')):>7.2f}"
                f"{d.get('judge_entropy_normalized', float('nan')):>11.3f}"
                f"{(d.get('style_coverage_entropy_normalized') or float('nan')):>11.3f}"
                f"{marcatore}"
            )

        primo, ultimo = punti[0], punti[-1]
        if (ultimo.get("fid") or 0) > 1.5 * (migliore.get("fid") or 1):
            print(
                f"  ATTENZIONE: il FID finale ({ultimo['fid']:.1f}) e' molto peggiore "
                f"del minimo ({migliore['fid']:.1f}) all'epoca {migliore['_epoca']}: "
                f"il run e' degenerato dopo aver raggiunto il suo punto migliore."
            )
        del primo


def stampa_selezione(per_run: dict[str, list[dict]], esclusi: set[str]) -> None:
    print(f"\n{'=' * 66}")
    print("SELEZIONE — checkpoint con FID minimo, regola identica per ogni run")
    print("=" * 66)
    print(f"\n{'run':<16}{'epoca':>7}{'FID':>9}{'IS':>7}{'ambiguita':>11}{'copertura':>11}")
    print("-" * 66)

    selezionati: dict[str, list[dict]] = {"dcgan": [], "can": []}
    for nome, punti in sorted(per_run.items()):
        migliore = min(punti, key=lambda d: d.get("fid") or float("inf"))
        nota = "  ESCLUSO" if nome in esclusi else ""
        print(
            f"{nome:<16}{migliore['_epoca']:>7}{migliore.get('fid', 0):>9.1f}"
            f"{migliore.get('inception_score_mean', 0):>7.2f}"
            f"{migliore.get('judge_entropy_normalized', 0):>11.3f}"
            f"{(migliore.get('style_coverage_entropy_normalized') or 0):>11.3f}{nota}"
        )
        if nome not in esclusi:
            selezionati[migliore["condizione"]].append(migliore)

    print(f"\n{'=' * 66}")
    print("MEDIE PER CONDIZIONE")
    print("=" * 66)
    for condizione, gruppo in selezionati.items():
        if not gruppo:
            continue
        print(f"\n{condizione.upper()}  (n = {len(gruppo)})")
        for chiave, etichetta, dec in (
            ("fid", "FID (piu' basso e' meglio)", 1),
            ("inception_score_mean", "Inception Score", 2),
            ("judge_entropy_normalized", "Ambiguita' (giudice terzo)", 3),
            ("style_coverage_entropy_normalized", "Copertura degli stili", 3),
        ):
            valori = [d[chiave] for d in gruppo if d.get(chiave) is not None]
            if not valori:
                continue
            media = st.mean(valori)
            if len(valori) > 1:
                print(f"   {etichetta:<32}{media:>8.{dec}f}  ± {st.stdev(valori):.{dec}f}")
            else:
                print(f"   {etichetta:<32}{media:>8.{dec}f}  (un solo run)")

    riferimento = next(iter(next(iter(per_run.values()))), None)
    if riferimento and riferimento.get("judge_entropy_real_normalized") is not None:
        print(
            f"\nRiferimenti: arte reale "
            f"{riferimento['judge_entropy_real_normalized']:.3f} · soffitto 1.000 · "
            f"accuratezza del giudice {riferimento.get('judge_val_accuracy', 0):.3f}"
        )
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--escludi", nargs="*", default=[])
    args = parser.parse_args()

    per_run = carica(args.results_dir)
    if not per_run:
        print(f"Nessun risultato in {args.results_dir}.")
        return 1

    stampa_traiettorie(per_run)
    stampa_selezione(per_run, set(args.escludi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
