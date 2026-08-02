"""Generazione delle figure e delle tabelle della tesi dai risultati sperimentali.

Le figure in `thesis/figures/generated/` **non si modificano a mano**: si
rigenerano (CLAUDE.md §6). Chi le ritocca in un editor grafico rompe la catena
`commit -> run -> checkpoint -> figura -> numero in tesi`, e a quel punto il numero
stampato non e' piu' difendibile.

I nomi dei file sono deterministici, cosi' che il `\\includegraphics` nel LaTeX non
vada aggiornato a ogni rigenerazione.

Input atteso: uno o piu' file JSON prodotti da
`python -m tesi_gan.cli evaluate --output experiments/results/<nome>.json`.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

# Nomi deterministici: se cambiano, va aggiornato il LaTeX che li include.
FIG_CONFRONTO_METRICHE = "confronto-metriche.pdf"
TAB_CONFRONTO_METRICHE = "confronto-metriche.tex"
FIG_CAMPIONI = "campioni-{condizione}.png"


def _load_results(results_dir: Path) -> list[dict]:
    if not results_dir.exists():
        return []
    out = []
    for path in sorted(results_dir.glob("*.json")):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            log.warning("File di risultati illeggibile, ignorato: %s", path)
    return out


def _fmt(value, decimals: int = 2) -> str:
    return "--" if value is None else f"{value:.{decimals}f}"


def write_comparison_table(results: list[dict], out_dir: Path) -> Path:
    """Tabella LaTeX di confronto fra le condizioni.

    Include la colonna dell'entropia di stile, che per la DCGAN e' vuota per
    costruzione: la condizione di controllo non ha testa di stile. Il trattino non
    e' un dato mancante ed e' bene che la caption lo dica.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / TAB_CONFRONTO_METRICHE

    righe = []
    for r in sorted(results, key=lambda x: str(x.get("condizione", ""))):
        righe.append(
            "  {} & {} & {} & {} & {} \\\\".format(
                str(r.get("condizione", "?")).upper(),
                _fmt(r.get("fid")),
                _fmt(r.get("inception_score_mean")),
                _fmt(r.get("inception_score_std")),
                _fmt(r.get("style_entropy_normalized"), 3),
            )
        )

    contenuto = (
        "% File generato da tesi_gan.evaluation.figures — non modificare a mano.\n"
        "\\begin{tabular}{lrrrr}\n"
        "  \\toprule\n"
        "  Condizione & FID $\\downarrow$ & IS $\\uparrow$ & dev.\\ std.\\ IS "
        "& Ambiguità norm. \\\\\n"
        "  \\midrule\n" + "\n".join(righe) + "\n"
        "  \\bottomrule\n"
        "\\end{tabular}\n"
    )
    path.write_text(contenuto, encoding="utf-8")
    return path


def plot_comparison(results: list[dict], out_dir: Path) -> Path | None:
    """Grafico a barre del confronto FID / ambiguità fra le due condizioni."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        log.warning("matplotlib non disponibile: grafico non prodotto.")
        return None

    if not results:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / FIG_CONFRONTO_METRICHE

    condizioni = [str(r.get("condizione", "?")).upper() for r in results]
    fid = [r.get("fid") or 0.0 for r in results]
    ambiguita = [r.get("style_entropy_normalized") or 0.0 for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.2))

    ax1.bar(condizioni, fid, color="#4c72b0")
    ax1.set_title("FID (più basso è meglio)")
    ax1.set_ylabel("FID")

    ax2.bar(condizioni, ambiguita, color="#dd8452")
    ax2.set_title("Ambiguità di stile normalizzata")
    ax2.set_ylabel("entropia / log K")
    ax2.set_ylim(0, 1)

    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def export_all(cfg, results_dir: Path) -> list[Path]:
    """Rigenera tutte le figure e tabelle ricavabili dai risultati disponibili."""
    out_dir = Path(cfg.paths.figures)
    results = _load_results(Path(results_dir))
    if not results:
        return []

    written: list[Path] = [write_comparison_table(results, out_dir)]
    plot = plot_comparison(results, out_dir)
    if plot is not None:
        written.append(plot)
    return written
