"""Figura dell'esperimento illustrativo condizionato — FUORI da ADR-0003.

Non aggiunge nulla a `campioni.py`, che produce le figure del confronto DCGAN/CAN.
Qui l'unica figura e' una griglia stile-per-riga: a differenza del generatore
incondizionato di D-010, questo generatore **sa** con quale stile ha prodotto
ciascuna immagine (glielo si e' chiesto in ingresso), quindi l'etichetta di riga e'
legittima e non una predizione di un giudice terzo.
"""

from __future__ import annotations

import logging
from pathlib import Path

import torch

log = logging.getLogger(__name__)


def _matplotlib():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        return plt
    except ImportError:
        log.warning("matplotlib non disponibile: figura non prodotta.")
        return None


def _to_numpy_image(tensor: torch.Tensor):
    image = tensor.detach().cpu().float()
    if float(image.min()) < 0.0:
        image = (image.clamp(-1, 1) + 1.0) / 2.0
    return image.clamp(0, 1).permute(1, 2, 0).numpy()


def save_conditional_grid(
    generator,
    classes: list[str],
    out_dir: Path,
    seed: int,
    device: torch.device,
    n_per_style: int = 6,
    generator_seed: int = 42,
) -> Path | None:
    """Griglia illustrativa: una riga per stile, campioni condizionati su richiesta.

    **Didascalia obbligatoria in tesi**: va dichiarato che l'etichetta e' quella con
    cui il generatore e' stato condizionato (non una predizione), che l'architettura
    non e' comparabile a DCGAN/CAN (ADR-0003), e che non esiste un numero (FID/IS)
    pubblicato dalla fonte di ispirazione con cui confrontare questi campioni: la
    figura mostra qualita' visiva, non un risultato quantitativo.
    """
    plt = _matplotlib()
    if plt is None:
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"illustrativo-condizionato-seed{seed}.png"

    generator.eval()
    gen = torch.Generator(device="cpu").manual_seed(generator_seed)
    num_styles = len(classes)

    fig, axes = plt.subplots(
        num_styles, n_per_style,
        figsize=(1.5 * n_per_style, 1.7 * num_styles), squeeze=False,
    )

    for riga in range(num_styles):
        labels = torch.full((n_per_style,), riga, dtype=torch.long)
        z = torch.randn(n_per_style, generator.latent_dim, 1, 1, generator=gen).to(device)
        with torch.no_grad():
            immagini = generator(z, labels.to(device)).cpu()
        for colonna in range(n_per_style):
            ax = axes[riga][colonna]
            ax.axis("off")
            ax.imshow(_to_numpy_image(immagini[colonna]))
            if colonna == 0:
                ax.set_title(classes[riga].replace("_", " "), fontsize=9, loc="left")

    fig.suptitle(
        "Esperimento illustrativo — generatore condizionato per stile "
        "(fuori dal confronto DCGAN/CAN, ADR-0003)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Figura illustrativa condizionata scritta: %s", path)
    return path
