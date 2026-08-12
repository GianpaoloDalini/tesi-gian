"""Figura dell'esperimento illustrativo condizionato — FUORI da ADR-0003.

Non aggiunge nulla a `campioni.py`, che produce le figure del confronto DCGAN/CAN.
Qui l'unica figura e' una griglia stile-per-riga: a differenza del generatore
incondizionato di D-010, questo generatore **sa** con quale stile ha prodotto
ciascuna immagine (glielo si e' chiesto in ingresso), quindi l'etichetta di riga e'
legittima e non una predizione di un giudice terzo.

La griglia puo' opzionalmente affiancare, come prima colonna di ogni riga, una
singola immagine reale dello stile corrispondente. **Non e' un confronto
quantitativo**: e' un solo esemplare scelto a caso dal dataset passato, non una
media ne' il "prototipo" dello stile, e non sostituisce FID/IS. Serve solo a dare
al lettore un riferimento visivo immediato accanto ai campioni generati — va
dichiarato in didascalia che si tratta di un singolo esempio, non di una sintesi
statistica dello stile.
"""

from __future__ import annotations

import logging
import random
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


def _immagine_reale_per_stile(
    dataset, num_styles: int, seed: int = 0
) -> list[torch.Tensor | None]:
    """Un'immagine reale a caso per stile, seedata per riproducibilita'.

    Usa `dataset.targets` se disponibile (ImageFolder e SyntheticStyleDataset la
    espongono entrambi), altrimenti ricostruisce l'elenco leggendo ogni etichetta —
    piu' lento, ma resta corretto anche su dataset che non la definiscono.
    """
    targets = getattr(dataset, "targets", None)
    if targets is None:
        targets = [dataset[i][1] for i in range(len(dataset))]

    indici_per_stile: dict[int, list[int]] = {i: [] for i in range(num_styles)}
    for idx, target in enumerate(targets):
        target = int(target)
        if target in indici_per_stile:
            indici_per_stile[target].append(idx)

    rng = random.Random(seed)
    scelte: list[torch.Tensor | None] = []
    for stile in range(num_styles):
        pool = indici_per_stile.get(stile, [])
        if not pool:
            log.warning("Nessuna immagine reale disponibile per lo stile indice %d", stile)
            scelte.append(None)
            continue
        idx = rng.choice(pool)
        immagine, _ = dataset[idx]
        scelte.append(immagine)
    return scelte


def save_conditional_grid(
    generator,
    classes: list[str],
    out_dir: Path,
    seed: int,
    device: torch.device,
    n_per_style: int = 6,
    generator_seed: int = 42,
    reference_dataset=None,
    reference_seed: int = 0,
) -> Path | None:
    """Griglia illustrativa: una riga per stile, campioni condizionati su richiesta.

    Se `reference_dataset` e' passato (un dataset con `.classes`/`.targets` nello
    stesso ordine di `classes`, tipicamente quello di riferimento — non quello di
    training, per non mescolare "esempio reale" e "immagine su cui il generatore si
    e' allenato), la prima colonna di ogni riga mostra un'immagine reale di
    quell'stile, separata visivamente dai campioni generati.

    **Didascalia obbligatoria in tesi**: va dichiarato che l'etichetta e' quella con
    cui il generatore e' stato condizionato (non una predizione), che l'architettura
    non e' comparabile a DCGAN/CAN (ADR-0003), che non esiste un numero (FID/IS)
    pubblicato dalla fonte di ispirazione con cui confrontare questi campioni — la
    figura mostra qualita' visiva, non un risultato quantitativo — e, se presente la
    colonna reale, che si tratta di UN singolo esemplare scelto a caso, non di un
    prototipo statistico dello stile.
    """
    plt = _matplotlib()
    if plt is None:
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # La risoluzione nel nome evita che un run a 128px sovrascriva silenziosamente
    # la figura di uno a 64px con lo stesso seed (successo una volta, non doveva).
    path = out_dir / f"illustrativo-condizionato-{generator.image_size}px-seed{seed}.png"

    generator.eval()
    gen = torch.Generator(device="cpu").manual_seed(generator_seed)
    num_styles = len(classes)

    reali = None
    if reference_dataset is not None:
        reali = _immagine_reale_per_stile(reference_dataset, num_styles, seed=reference_seed)

    n_colonne = n_per_style + (1 if reali is not None else 0)
    fig, axes = plt.subplots(
        num_styles, n_colonne,
        figsize=(1.5 * n_colonne, 1.7 * num_styles), squeeze=False,
    )

    for riga in range(num_styles):
        offset = 0
        if reali is not None:
            ax = axes[riga][0]
            ax.axis("off")
            if reali[riga] is not None:
                ax.imshow(_to_numpy_image(reali[riga]))
            ax.set_title(
                f"{classes[riga].replace('_', ' ')}\n(reale, 1 esempio)",
                fontsize=8, loc="left",
            )
            # Separatore visivo fra la colonna reale e quelle generate.
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_edgecolor("black")
                spine.set_linewidth(1.2)
            offset = 1

        labels = torch.full((n_per_style,), riga, dtype=torch.long)
        z = torch.randn(n_per_style, generator.latent_dim, 1, 1, generator=gen).to(device)
        with torch.no_grad():
            immagini = generator(z, labels.to(device)).cpu()
        for colonna in range(n_per_style):
            ax = axes[riga][colonna + offset]
            ax.axis("off")
            ax.imshow(_to_numpy_image(immagini[colonna]))
            if colonna == 0 and offset == 0:
                ax.set_title(classes[riga].replace("_", " "), fontsize=9, loc="left")
            elif colonna == 0:
                ax.set_title("generato", fontsize=8, loc="left")

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


def save_progression_grid(
    generator,
    classes: list[str],
    checkpoint_paths: list[Path],
    out_dir: Path,
    seed: int,
    device: torch.device,
    generator_seed: int = 42,
) -> Path | None:
    """Griglia di progressione: una riga per stile, una colonna per checkpoint.

    Ogni colonna e' un checkpoint diverso (tipicamente uno ogni `checkpoint_every`
    epoche, gli `epoch_NNNN.pt` scritti da `ConditionalTrainer`); ogni riga usa lo
    STESSO rumore fisso per tutte le colonne, cosi' la differenza visibile fra una
    colonna e la successiva e' imputabile solo all'evoluzione dei pesi nel tempo, non
    a un campione diverso.

    `checkpoint_paths` va gia' ordinato per epoca crescente da chi chiama: questa
    funzione non assume nulla sul nome del file, si fida solo dell'ordine ricevuto e
    del campo `"epoch"` dentro ogni checkpoint per l'etichetta di colonna.

    **Il generatore passato viene mutato**: i pesi vengono sovrascritti a ogni
    colonna caricando lo state_dict del checkpoint corrispondente. Non riusarlo dopo
    la chiamata aspettandosi i pesi con cui e' stato passato.

    Ogni checkpoint deve essere dell'esperimento condizionato (flag `"conditional"`
    a `True`, come scritto da `ConditionalTrainer.save_checkpoint`) e avere lo stesso
    numero di stili di `generator`/`classes`: altrimenti la figura mescolerebbe
    epoche di run diversi senza che sia visibile a occhio.
    """
    plt = _matplotlib()
    if plt is None:
        return None
    if not checkpoint_paths:
        log.warning("Nessun checkpoint fornito: figura di progressione non prodotta.")
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Stesso motivo della risoluzione nel nome di save_conditional_grid: evitare
    # che risoluzioni diverse con lo stesso seed si sovrascrivano.
    path = out_dir / f"illustrativo-progressione-{generator.image_size}px-seed{seed}.png"

    num_styles = len(classes)
    gen = torch.Generator(device="cpu").manual_seed(generator_seed)
    # Un solo campione per stile: la figura mostra l'evoluzione nel tempo, non la
    # variabilita' fra campioni (quella e' il compito di save_conditional_grid).
    z = torch.randn(num_styles, generator.latent_dim, 1, 1, generator=gen).to(device)
    labels = torch.arange(num_styles, device=device)

    n_colonne = len(checkpoint_paths)
    fig, axes = plt.subplots(
        num_styles, n_colonne,
        figsize=(1.5 * n_colonne, 1.7 * num_styles), squeeze=False,
    )

    for colonna, ckpt_path in enumerate(checkpoint_paths):
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
        if not bool(ckpt.get("conditional", False)):
            raise ValueError(
                f"{ckpt_path} non e' un checkpoint dell'esperimento condizionato "
                f"(manca il flag 'conditional')."
            )
        if int(ckpt.get("num_styles", -1)) != num_styles:
            raise ValueError(
                f"{ckpt_path} ha {ckpt.get('num_styles')} stili, la figura ne usa "
                f"{num_styles}: non sono confrontabili nella stessa colonna."
            )
        generator.load_state_dict(ckpt["generator"])
        generator.eval()
        epoca = int(ckpt.get("epoch", -1))

        with torch.no_grad():
            immagini = generator(z, labels).cpu()

        for riga in range(num_styles):
            ax = axes[riga][colonna]
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.imshow(_to_numpy_image(immagini[riga]))
            if colonna == 0:
                ax.set_ylabel(classes[riga].replace("_", " "), fontsize=9)
            if riga == 0:
                ax.set_title(f"epoca {epoca}", fontsize=9)

    fig.suptitle(
        "Esperimento illustrativo — progressione per stile nel tempo "
        "(fuori dal confronto DCGAN/CAN, ADR-0003)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Figura di progressione scritta: %s", path)
    return path
