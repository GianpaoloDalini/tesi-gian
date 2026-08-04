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


def export_figure_stili_reali(cfg) -> Path | None:
    """Griglia di riferimento degli stili reali: dipende solo dal dataset.

    Si puo' produrre prima ancora di aver addestrato qualcosa — e' la figura del
    capitolo dati, non di quello dei risultati.
    """
    from tesi_gan.data import build_dataset
    from tesi_gan.evaluation.campioni import save_real_styles_grid

    try:
        dataset = build_dataset(cfg)
    except (FileNotFoundError, RuntimeError) as err:
        log.warning("Dataset non disponibile, griglia degli stili non prodotta: %s", err)
        return None
    return save_real_styles_grid(dataset, Path(cfg.paths.figures))


def export_figure_evoluzione(cfg, device=None) -> Path | None:
    """Evoluzione a rumore fisso, ricostruita dai checkpoint numerati del run corrente."""
    import torch

    from tesi_gan.evaluation.campioni import (
        carica_campioni_da_checkpoint,
        save_evolution_figure,
    )
    from tesi_gan.models import Generator

    device = device or torch.device("cpu")
    checkpoint_dir = Path(cfg.paths.checkpoints)
    if not checkpoint_dir.exists():
        log.warning("Nessun checkpoint in %s: evoluzione non prodotta.", checkpoint_dir)
        return None

    def build_generator():
        return Generator(
            latent_dim=cfg.model.latent_dim,
            features=cfg.model.generator_features,
            channels=cfg.model.channels,
        )

    campioni = carica_campioni_da_checkpoint(checkpoint_dir, build_generator, device)
    if not campioni:
        return None
    return save_evolution_figure(
        campioni,
        out_dir=Path(cfg.paths.figures),
        condizione=str(cfg.model.name).lower(),
        seed=int(cfg.seed),
    )


def export_figure_annotata(cfg, device=None, checkpoint: Path | None = None) -> Path | None:
    """Campioni annotati dal giudice terzo: la figura chiave del confronto.

    Richiede sia un checkpoint sia il giudice addestrato. Se manca l'uno o l'altro
    si limita ad avvisare: e' una figura, non un risultato numerico, e non deve
    bloccare l'export delle altre.
    """
    import torch

    from tesi_gan.data import build_dataset
    from tesi_gan.evaluation.campioni import save_annotated_grid
    from tesi_gan.evaluation.style_classifier import load_style_classifier
    from tesi_gan.models import Generator

    device = device or torch.device("cpu")

    # Il checkpoint si puo' scegliere. Non e' un vezzo: a 128px `dcgan-seed1`
    # collassa fra l'epoca 97 e la 98, quindi `final.pt` contiene un modello
    # degenerato. Una figura di tesi prodotta da quel checkpoint mostrerebbe
    # artefatti a scacchiera invece del comportamento del modello, ed e' bene poter
    # puntare a un'epoca precedente — dichiarando quale, nella didascalia.
    if checkpoint is None:
        checkpoint = Path(cfg.paths.checkpoints) / "final.pt"
        if not checkpoint.exists():
            checkpoint = Path(cfg.paths.checkpoints) / "latest.pt"
    checkpoint = Path(checkpoint)
    if not checkpoint.exists():
        log.warning("Checkpoint inesistente (%s): figura annotata non prodotta.", checkpoint)
        return None
    log.info("Figure generate dal checkpoint %s", checkpoint)

    try:
        dataset = build_dataset(cfg)
        classes = list(getattr(dataset, "classes", []))
        judge, _ = load_style_classifier(Path(cfg.paths.style_judge), device, classes or None)
    except (FileNotFoundError, RuntimeError) as err:
        log.warning("Giudice non disponibile, figura annotata non prodotta: %s", err)
        return None

    generator = Generator(
        latent_dim=cfg.model.latent_dim,
        features=cfg.model.generator_features,
        channels=cfg.model.channels,
    )
    generator.load_state_dict(
        torch.load(checkpoint, map_location=device, weights_only=True)["generator"]
    )
    generator.to(device).eval()

    figure = []
    annotata = save_annotated_grid(
        generator=generator,
        judge=judge,
        classes=classes,
        out_dir=Path(cfg.paths.figures),
        condizione=str(cfg.model.name).lower(),
        seed=int(cfg.seed),
        device=device,
    )
    if annotata is not None:
        figure.append(annotata)

    # Confronto reali / generate, una riga per stile: mostra dove il modello
    # fallisce invece di aggregarlo in un numero solo, e rende visibili gli stili
    # che non produce affatto.
    from tesi_gan.evaluation.campioni import save_real_vs_generated

    confronto = save_real_vs_generated(
        generator=generator,
        judge=judge,
        dataset=dataset,
        classes=classes,
        out_dir=Path(cfg.paths.figures),
        condizione=str(cfg.model.name).lower(),
        seed=int(cfg.seed),
        device=device,
    )
    if confronto is not None:
        figure.append(confronto)

    return figure[0] if figure else None


def export_all(cfg, results_dir: Path, checkpoint: Path | None = None) -> list[Path]:
    """Rigenera tutte le figure e tabelle ricavabili da cio' che e' disponibile.

    Ogni figura ha prerequisiti diversi (risultati JSON, checkpoint, giudice,
    dataset): quelle producibili vengono prodotte, le altre avvisano. Cosi' l'export
    e' utile fin dalle prime fasi invece di richiedere l'impianto completo.
    """
    out_dir = Path(cfg.paths.figures)
    written: list[Path] = []

    results = _load_results(Path(results_dir))
    if results:
        written.append(write_comparison_table(results, out_dir))
        plot = plot_comparison(results, out_dir)
        if plot is not None:
            written.append(plot)
    else:
        log.warning("Nessun risultato in %s: tabella e grafico non prodotti.", results_dir)

    for produttore in (export_figure_stili_reali, export_figure_evoluzione, export_figure_annotata):
        try:
            if produttore is export_figure_annotata:
                path = produttore(cfg, checkpoint=checkpoint)
            else:
                path = produttore(cfg)
        except Exception as exc:  # noqa: BLE001
            log.warning("%s fallita: %s", produttore.__name__, exc)
            continue
        if path is not None:
            written.append(path)

    return written
