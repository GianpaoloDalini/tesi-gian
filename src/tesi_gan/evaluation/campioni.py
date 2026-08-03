"""Figure dei campioni generati: cio' che finisce nel capitolo dei risultati.

## Cosa si puo' e cosa non si puo' etichettare

Il generatore e' **incondizionato**: prende un vettore latente e produce un'immagine,
senza ricevere in ingresso uno stile. Un'immagine generata quindi **non ha uno stile
vero** da stampare accanto, e chiedere \"di che stile e' questo campione?\" non ha
risposta. Non e' una lacuna dell'implementazione: e' il presupposto della CAN, che
punta proprio a produrre immagini non attribuibili.

L'unica etichetta di stile legittima e' quella **predetta dal giudice terzo**
(`style_classifier.py`), che e' un'affermazione su come un classificatore
indipendente legge l'immagine — non sulla sua natura. Le didascalie generate qui lo
dicono esplicitamente, perche' una figura che scrive \"Barocco\" sotto un'immagine
generata sta affermando una cosa falsa.

## Le quattro figure

| Funzione | File prodotto | A cosa serve nella tesi |
|---|---|---|
| `save_sample_grid` | `campioni-{cond}-seed{N}-epoca{NNN}.png` | traccia grezza di ogni epoca |
| `save_annotated_grid` | `campioni-annotati-{cond}-seed{N}.png` | **mostra l'effetto CAN a colpo d'occhio** |
| `save_evolution_figure` | `evoluzione-{cond}-seed{N}.png` | progressione dell'addestramento |
| `save_real_styles_grid` | `stili-reali.png` | figura di riferimento del capitolo dati |
| `save_real_vs_generated` | `reali-vs-generate-{cond}-seed{N}.png` | **quanto le generate si discostano dalle reali, stile per stile** |

Tutte scrivono in `thesis/figures/generated/` e **non vanno ritoccate a mano**
(CLAUDE.md §6): si rigenerano.
"""

from __future__ import annotations

import logging
from pathlib import Path

import torch

log = logging.getLogger(__name__)

FIG_CAMPIONI = "campioni-{condizione}-seed{seed}-epoca{epoca:03d}.png"
FIG_ANNOTATI = "campioni-annotati-{condizione}-seed{seed}.png"
FIG_EVOLUZIONE = "evoluzione-{condizione}-seed{seed}.png"
FIG_STILI_REALI = "stili-reali.png"


def _matplotlib():
    """Importa matplotlib in modalita' headless. Restituisce None se assente."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        return plt
    except ImportError:
        log.warning("matplotlib non disponibile: figura non prodotta.")
        return None


def _to_numpy_image(tensor: torch.Tensor):
    """Da tensore CHW in [-1, 1] o [0, 1] a array HWC in [0, 1] per imshow."""
    image = tensor.detach().cpu().float()
    if float(image.min()) < 0.0:  # ancora in [-1, 1]
        image = (image.clamp(-1, 1) + 1.0) / 2.0
    return image.clamp(0, 1).permute(1, 2, 0).numpy()


# --------------------------------------------------------------------------- #
#  1. Griglia semplice, una per epoca
# --------------------------------------------------------------------------- #

def save_sample_grid(
    images: torch.Tensor,
    out_dir: Path,
    condizione: str,
    seed: int,
    epoca: int,
    nrow: int = 8,
) -> Path | None:
    """Griglia di campioni con l'epoca nel **nome del file** e nel titolo.

    Il nome contiene condizione, seed ed epoca: tre run per condizione (D-010) che
    scrivessero tutti su `campioni.png` si sovrascriverebbero a vicenda, ed e'
    esattamente l'errore gia' corretto sui percorsi dei checkpoint.
    """
    try:
        from torchvision.utils import make_grid
    except ImportError:
        log.warning("torchvision non disponibile: griglia non prodotta.")
        return None

    plt = _matplotlib()
    if plt is None:
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / FIG_CAMPIONI.format(condizione=condizione, seed=seed, epoca=epoca)

    grid = make_grid(images.detach().cpu(), nrow=nrow, padding=2)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(_to_numpy_image(grid))
    ax.axis("off")
    ax.set_title(f"{condizione.upper()} — seed {seed} — epoca {epoca}", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
#  2. Griglia annotata dal giudice — la figura chiave
# --------------------------------------------------------------------------- #

@torch.no_grad()
def save_annotated_grid(
    generator,
    judge,
    classes: list[str],
    out_dir: Path,
    condizione: str,
    seed: int,
    device: torch.device,
    n_images: int = 12,
    ncols: int = 4,
) -> Path | None:
    """Campioni annotati con **stile predetto dal giudice terzo e confidenza**.

    E' la figura che rende visibile l'ipotesi dell'impianto senza bisogno di leggere
    una tabella: nella DCGAN ci si attende attribuzioni sicure (una classe dominante),
    nella CAN attribuzioni incerte (probabilita' distribuite).

    Sotto ogni immagine compaiono le prime due classi con la rispettiva probabilita' e
    l'entropia normalizzata. **La didascalia deve chiarire che si tratta di una
    predizione, non dello stile dell'immagine**: un'immagine generata non ha uno
    stile vero (vedi il docstring del modulo). Il testo suggerito e' restituito da
    `didascalia_griglia_annotata()`.
    """
    import math

    import torch.nn.functional as F

    plt = _matplotlib()
    if plt is None:
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / FIG_ANNOTATI.format(condizione=condizione, seed=seed)

    generator.eval()
    judge.eval()
    images = generator.sample(n_images, device)
    probabilities = F.softmax(judge(images), dim=1)
    entropy = -(probabilities * probabilities.clamp_min(1e-12).log()).sum(dim=1)
    entropy_normalized = entropy / math.log(len(classes))

    nrows = (n_images + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(2.6 * ncols, 3.1 * nrows))
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for i in range(len(axes)):
        ax = axes[i]
        ax.axis("off")
        if i >= n_images:
            continue
        ax.imshow(_to_numpy_image(images[i]))
        top = torch.topk(probabilities[i], k=min(2, len(classes)))
        etichette = " · ".join(
            f"{classes[int(idx)]} {float(p) * 100:.0f}%"
            for p, idx in zip(top.values, top.indices)
        )
        ax.set_title(f"{etichette}\nH = {float(entropy_normalized[i]):.2f}", fontsize=8)

    fig.suptitle(
        f"{condizione.upper()} — seed {seed} — attribuzione secondo il giudice terzo",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Figura annotata scritta: %s", path)
    return path


def didascalia_griglia_annotata(condizione: str, accuratezza_giudice: float) -> str:
    """Didascalia LaTeX suggerita, da incollare e adattare.

    Esiste per una ragione precisa: senza la precisazione che l'etichetta e' una
    *predizione*, la figura afferma che un'immagine generata appartiene a uno stile
    storico, che e' falso e in una tesi sulla creativita' computazionale e' un errore
    concettuale, non una sfumatura.
    """
    return (
        f"Campioni generati dalla condizione {condizione.upper()}. Le etichette "
        f"riportano le due classi di stile piu' probabili \\emph{{secondo il "
        f"classificatore terzo}} (accuratezza di validazione "
        f"{accuratezza_giudice:.2f}) e non lo stile delle immagini, che essendo "
        f"prodotte da un generatore incondizionato non ne possiedono uno. "
        f"$H$ e' l'entropia della posterior normalizzata rispetto a $\\log K$: "
        f"vale 1 quando l'attribuzione e' massimamente incerta."
    )


# --------------------------------------------------------------------------- #
#  3. Evoluzione per epoche
# --------------------------------------------------------------------------- #

def save_evolution_figure(
    campioni_per_epoca: dict[int, torch.Tensor],
    out_dir: Path,
    condizione: str,
    seed: int,
    n_images: int = 6,
) -> Path | None:
    """Stessi vettori latenti a epoche diverse: una riga per epoca.

    Richiede che i campioni provengano dal **rumore fisso** del trainer, altrimenti
    la figura mostrerebbe immagini diverse invece dell'evoluzione delle stesse, e non
    direbbe nulla sull'addestramento.
    """
    plt = _matplotlib()
    if plt is None or not campioni_per_epoca:
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / FIG_EVOLUZIONE.format(condizione=condizione, seed=seed)

    epoche = sorted(campioni_per_epoca)
    fig, axes = plt.subplots(
        len(epoche), n_images, figsize=(1.5 * n_images, 1.6 * len(epoche)), squeeze=False
    )

    for riga, epoca in enumerate(epoche):
        immagini = campioni_per_epoca[epoca]
        for colonna in range(n_images):
            ax = axes[riga][colonna]
            ax.axis("off")
            if colonna < immagini.size(0):
                ax.imshow(_to_numpy_image(immagini[colonna]))
            if colonna == 0:
                ax.set_ylabel(f"ep. {epoca}", fontsize=9)
                ax.axis("on")
                ax.set_xticks([])
                ax.set_yticks([])

    fig.suptitle(f"{condizione.upper()} — seed {seed} — evoluzione a rumore fisso", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Figura di evoluzione scritta: %s", path)
    return path


def carica_campioni_da_checkpoint(
    checkpoint_dir: Path,
    build_generator,
    device: torch.device,
    n_images: int = 6,
) -> dict[int, torch.Tensor]:
    """Rigenera i campioni a rumore fisso da ogni checkpoint numerato.

    Il rumore fisso e' salvato **dentro** il checkpoint dal trainer, quindi le
    immagini prodotte qui sono le stesse che il generatore produceva a quell'epoca:
    la figura e' ricostruibile a posteriori senza aver conservato i PNG.
    """
    checkpoint_dir = Path(checkpoint_dir)
    fuori: dict[int, torch.Tensor] = {}

    for path in sorted(checkpoint_dir.glob("epoch_*.pt")):
        ckpt = torch.load(path, map_location=device, weights_only=True)
        generator = build_generator()
        generator.load_state_dict(ckpt["generator"])
        generator.to(device).eval()
        rumore = ckpt["fixed_noise"][:n_images].to(device)
        with torch.no_grad():
            fuori[int(ckpt["epoch"])] = generator(rumore).cpu()

    if not fuori:
        log.warning("Nessun checkpoint `epoch_*.pt` in %s.", checkpoint_dir)
    return fuori


# --------------------------------------------------------------------------- #
#  4. Griglia di riferimento degli stili reali
# --------------------------------------------------------------------------- #

@torch.no_grad()
def save_real_vs_generated(
    generator,
    judge,
    dataset,
    classes: list[str],
    out_dir: Path,
    condizione: str,
    seed: int,
    device: torch.device,
    n_per_style: int = 3,
    n_candidati: int = 512,
    seed_selezione: int = 42,
) -> Path | None:
    """Confronto affiancato reali / generate, **una riga per stile**.

    Per ciascuno stile la riga mostra `n_per_style` dipinti veri e, accanto,
    altrettante immagini generate **che il giudice terzo attribuisce a quello
    stile**. Il generatore e' incondizionato e non sa nulla degli stili: e' il
    classificatore a smistare i campioni, e la figura mostra il risultato di quello
    smistamento.

    ## Perche' questa figura dice piu' di una griglia di campioni

    Risponde a due domande diverse nella stessa immagine:

    1. **Quanto le generate si discostano dalle reali**, stile per stile invece che
       in aggregato. Un FID e' un numero solo; qui si vede *dove* il modello
       fallisce.
    2. **Se il generatore copre davvero tutti gli stili.** Una riga con poche o
       nessuna immagine generata significa che il modello quello stile non lo produce
       — o che il giudice non ce lo riconosce. In entrambi i casi la copertura e'
       incompleta, e va dichiarata: parte dell'ambiguita' misurata sarebbe collasso
       su una zona generica, non fusione stilistica.

    Le righe rimaste scoperte vengono etichettate esplicitamente invece di essere
    lasciate vuote: una casella bianca in una figura di tesi sembra un errore di
    composizione, mentre qui e' il risultato.
    """
    import random

    import torch.nn.functional as F

    plt = _matplotlib()
    if plt is None:
        return None

    targets = getattr(dataset, "targets", None)
    if targets is None:
        log.warning("Il dataset non espone `targets`: confronto non prodotto.")
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"reali-vs-generate-{condizione}-seed{seed}.png"

    # --- generate, smistate per classe predetta dal giudice --------------------
    generator.eval()
    judge.eval()
    per_classe: dict[int, list] = {i: [] for i in range(len(classes))}
    confidenze: dict[int, list] = {i: [] for i in range(len(classes))}

    visti = 0
    while visti < n_candidati and any(len(v) < n_per_style for v in per_classe.values()):
        n = min(64, n_candidati - visti)
        immagini = generator.sample(n, device)
        probabilita = F.softmax(judge(immagini), dim=1)
        predette = probabilita.argmax(dim=1)
        for j in range(n):
            c = int(predette[j])
            if len(per_classe[c]) < n_per_style:
                per_classe[c].append(immagini[j].cpu())
                confidenze[c].append(float(probabilita[j, c]))
        visti += n

    # --- reali, campionate con seed fisso -------------------------------------
    indici_per_classe: dict[int, list[int]] = {}
    for indice, etichetta in enumerate(targets):
        indici_per_classe.setdefault(int(etichetta), []).append(indice)
    rng = random.Random(seed_selezione)

    # --- composizione ---------------------------------------------------------
    colonne = n_per_style * 2
    fig, axes = plt.subplots(
        len(classes), colonne,
        figsize=(1.45 * colonne + 1.2, 1.7 * len(classes)), squeeze=False,
    )

    for riga, nome in enumerate(classes):
        disponibili = indici_per_classe.get(riga, [])
        reali = rng.sample(disponibili, min(n_per_style, len(disponibili)))

        for k in range(n_per_style):
            ax = axes[riga][k]
            ax.axis("off")
            if k < len(reali):
                ax.imshow(_to_numpy_image(dataset[reali[k]][0]))
            if k == 0:
                ax.text(
                    -0.12, 0.5, nome.replace("_", " "), transform=ax.transAxes,
                    ha="right", va="center", fontsize=9, rotation=0,
                )

        generate = per_classe[riga]
        for k in range(n_per_style):
            ax = axes[riga][n_per_style + k]
            ax.axis("off")
            if k < len(generate):
                ax.imshow(_to_numpy_image(generate[k]))
                ax.set_title(f"{confidenze[riga][k] * 100:.0f}%", fontsize=7, pad=2)
            elif k == 0:
                # Riga scoperta: si dichiara invece di lasciare il bianco.
                ax.text(
                    0.5, 0.5, f"nessuna\nsu {visti}", transform=ax.transAxes,
                    ha="center", va="center", fontsize=7, color="#b00020",
                )

    axes[0][0].set_title("REALI", fontsize=10, loc="left", pad=12)
    axes[0][n_per_style].set_title("GENERATE", fontsize=10, loc="left", pad=12)

    fig.suptitle(
        f"{condizione.upper()} — seed {seed} — reali a confronto con le generate\n"
        f"attribuite a ciascuno stile dal giudice terzo ({visti} campioni esaminati)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    log.info("Confronto reali/generate scritto: %s", path)
    return path


def save_real_styles_grid(
    dataset,
    out_dir: Path,
    n_per_style: int = 6,
    seed: int = 42,
) -> Path | None:
    """Una riga per stile, `n_per_style` esempi reali: figura del capitolo dati.

    Serve a due cose: documentare visivamente il dataset, e dare al lettore il
    termine di paragone senza cui i campioni generati non sono valutabili. Le
    immagini sono estratte con un seed fisso, quindi la figura si rigenera identica.
    """
    import random

    plt = _matplotlib()
    if plt is None:
        return None

    classes = list(getattr(dataset, "classes", []))
    targets = getattr(dataset, "targets", None)
    if not classes or targets is None:
        log.warning("Il dataset non espone `classes`/`targets`: figura non prodotta.")
        return None

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / FIG_STILI_REALI

    per_classe: dict[int, list[int]] = {}
    for indice, etichetta in enumerate(targets):
        per_classe.setdefault(int(etichetta), []).append(indice)

    rng = random.Random(seed)
    fig, axes = plt.subplots(
        len(classes), n_per_style,
        figsize=(1.5 * n_per_style, 1.7 * len(classes)), squeeze=False,
    )

    for riga, nome in enumerate(classes):
        indici = per_classe.get(riga, [])
        scelti = rng.sample(indici, min(n_per_style, len(indici))) if indici else []
        for colonna in range(n_per_style):
            ax = axes[riga][colonna]
            ax.axis("off")
            if colonna < len(scelti):
                ax.imshow(_to_numpy_image(dataset[scelti[colonna]][0]))
            if colonna == 0:
                ax.set_title(nome.replace("_", " "), fontsize=9, loc="left")

    fig.suptitle("Stili presenti nel dataset — esempi reali", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Griglia degli stili reali scritta: %s", path)
    return path
