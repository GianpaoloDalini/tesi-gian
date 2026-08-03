"""Metriche di valutazione, con dichiarazione esplicita di cosa non misurano.

**Avvertenza metodologica, da riportare in tesi e non solo qui (Q5).** FID e
Inception Score misurano fedelta' e varieta' rispetto a una distribuzione di
riferimento. Non misurano creativita', novita' o valore estetico. Di piu': entrambe
poggiano su una rete Inception addestrata su ImageNet, cioe' su **fotografie**. Il
suo spazio di feature non e' costruito per rappresentare la pittura, e questo e' un
limite strutturale, non un margine di errore.

Il paradosso e' istruttivo e vale la pena renderlo esplicito nel capitolo di
discussione: un modello che genera immagini stilisticamente ambigue — cioe' che fa
esattamente cio' per cui la CAN e' progettata — si allontana dalla distribuzione dei
dati reali e quindi **peggiora il FID**. Un FID peggiore per la CAN non falsifica
l'ipotesi: mostra che la metrica e l'obiettivo sono in tensione.

Le metriche vanno lette insieme, mai isolate:

| Metrica | Direzione desiderata | Cosa dice davvero |
|---|---|---|
| FID | piu' basso e' meglio | quanto i generati assomigliano ai reali |
| Inception Score | piu' alto e' meglio | quanto sono nitidi e vari secondo ImageNet |
| Ambiguita' (giudice terzo) | alta e' l'obiettivo della CAN | quanto un classificatore indipendente fatica ad attribuire uno stile |
| Ambiguita' (testa di D) | — | diagnostica interna, **non** confrontabile fra condizioni |

**Le due misure di ambiguita' non sono intercambiabili.** Quella prodotta dalla testa
di stile del discriminatore esiste solo nella CAN e proviene da una parte in causa:
resta utile come diagnostica del training, ma il confronto fra le condizioni si regge
esclusivamente sul giudice terzo di `style_classifier.py`, che e' addestrato una volta
sui soli dati reali e poi congelato.

**Il confondimento da non dimenticare:** un generatore collassato produce rumore, e il
rumore massimizza l'entropia del giudice. Ambiguita' alta con FID pessimo non e'
creativita', e' un modello che non ha imparato. Le due metriche si riportano sempre
in coppia.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

log = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    fid: float | None
    inception_score_mean: float | None
    inception_score_std: float | None
    # Ambiguita' secondo la testa di stile del discriminatore: diagnostica interna,
    # presente solo nella CAN, non confrontabile fra condizioni.
    style_entropy: float | None
    style_entropy_normalized: float | None
    n_samples: int
    # Ambiguita' secondo il giudice terzo: **la misura su cui si regge il confronto**.
    # Calcolabile identicamente per DCGAN e CAN.
    judge_entropy: float | None = None
    judge_entropy_normalized: float | None = None
    # Ancore di lettura: senza queste i valori sopra non sono interpretabili.
    judge_entropy_real: float | None = None
    judge_entropy_real_normalized: float | None = None
    judge_val_accuracy: float | None = None
    # Copertura degli stili: distribuzione MARGINALE delle classi predette.
    # Distingue la fusione stilistica (marginale uniforme, e' l'effetto cercato) dal
    # collasso di stile (marginale concentrata su poche classi), che l'entropia per
    # immagine da sola non separa.
    style_coverage_counts: list[int] | None = None
    style_coverage_classes: list[str] | None = None
    style_coverage_entropy: float | None = None
    style_coverage_entropy_normalized: float | None = None

    def as_dict(self) -> dict:
        return asdict(self)


def _to_uint8(images: torch.Tensor) -> torch.Tensor:
    """Da float in [0, 1] a uint8 in [0, 255], come atteso da torchmetrics."""
    return (images.clamp(0, 1) * 255).to(torch.uint8)


@torch.no_grad()
def style_ambiguity(
    discriminator,
    generator,
    n_samples: int,
    batch_size: int,
    device: torch.device,
) -> tuple[float, float] | tuple[None, None]:
    """Entropia media della posterior di stile sulle immagini generate.

    Restituisce `(entropia_nats, entropia_normalizzata)`. La normalizzazione e'
    rispetto a log(K), quindi il valore normalizzato sta in [0, 1] e vale 1 quando
    la posterior e' perfettamente uniforme — ambiguita' massima.

    **Limite da dichiarare:** misura l'ambiguita' *secondo il discriminatore che si
    e' addestrato insieme al generatore*. Non e' un giudizio indipendente, ed e' il
    motivo per cui non puo' sostituire lo studio percettivo. Confrontare l'ambiguita'
    fra DCGAN e CAN misurata da due discriminatori diversi e' legittimo solo come
    indicazione qualitativa: per un confronto pulito serve un classificatore di stile
    terzo, addestrato una volta sola sui dati reali e tenuto fisso.
    """
    if not getattr(discriminator, "style_head_enabled", False):
        return None, None

    discriminator.eval()
    generator.eval()
    total = 0.0
    seen = 0

    while seen < n_samples:
        n = min(batch_size, n_samples - seen)
        images = generator.sample(n, device)
        _, style_logits = discriminator(images)
        log_p = F.log_softmax(style_logits, dim=1)
        entropy = -(log_p.exp() * log_p).sum(dim=1)
        total += float(entropy.sum())
        seen += n

    mean_entropy = total / max(seen, 1)
    k = discriminator.num_styles or 1
    import math

    normalized = mean_entropy / math.log(k) if k > 1 else 0.0
    return mean_entropy, normalized


@torch.no_grad()
def evaluate(
    generator,
    discriminator,
    real_loader: DataLoader,
    device: torch.device,
    n_samples: int = 2048,
    batch_size: int = 64,
    compute_fid: bool = True,
    compute_is: bool = True,
    style_judge=None,
    judge_info=None,
) -> EvaluationResult:
    """Calcola le metriche su `n_samples` immagini generate.

    `n_samples` va tenuto **identico fra le due condizioni**: il FID e' notoriamente
    sensibile alla numerosita' del campione, e confrontare un FID su 2048 campioni
    con uno su 10000 non ha significato.

    `style_judge` e' il classificatore terzo congelato (vedi `style_classifier.py`).
    Va passato **lo stesso oggetto** in tutte le valutazioni dell'impianto: e' cio'
    che rende le entropie confrontabili fra condizioni e fra seed. Se manca, la
    metrica di ambiguita' indipendente non viene calcolata e resta solo la
    diagnostica interna della CAN — cioe' nessun confronto.
    """
    from tesi_gan.data.dataset import denormalize

    generator.eval()
    fid_value = is_mean = is_std = None

    if compute_fid or compute_is:
        try:
            from torchmetrics.image.fid import FrechetInceptionDistance
            from torchmetrics.image.inception import InceptionScore
        except ImportError:
            log.warning("torchmetrics non disponibile: FID e IS non calcolati.")
            compute_fid = compute_is = False

    if compute_fid:
        fid = FrechetInceptionDistance(feature=2048, normalize=False).to(device)
        seen_real = 0
        for real, _ in real_loader:
            real = _to_uint8(denormalize(real.to(device)))
            fid.update(real, real=True)
            seen_real += real.size(0)
            if seen_real >= n_samples:
                break
        seen_fake = 0
        while seen_fake < n_samples:
            n = min(batch_size, n_samples - seen_fake)
            fake = _to_uint8(denormalize(generator.sample(n, device)))
            fid.update(fake, real=False)
            seen_fake += n
        fid_value = float(fid.compute())
        log.info("FID = %.3f su %d campioni per lato", fid_value, n_samples)

    if compute_is:
        inception = InceptionScore(normalize=False).to(device)
        seen = 0
        while seen < n_samples:
            n = min(batch_size, n_samples - seen)
            inception.update(_to_uint8(denormalize(generator.sample(n, device))))
            seen += n
        mean, std = inception.compute()
        is_mean, is_std = float(mean), float(std)
        log.info("Inception Score = %.3f ± %.3f", is_mean, is_std)

    entropy, entropy_norm = style_ambiguity(
        discriminator,
        generator,
        n_samples=min(n_samples, 1024),
        batch_size=batch_size,
        device=device,
    )
    if entropy is not None:
        log.info(
            "[diagnostica interna] Entropia secondo la testa di D = %.4f nats "
            "(normalizzata %.3f)", entropy, entropy_norm,
        )

    # --- Giudice terzo: la misura confrontabile fra le condizioni ---------------
    judge_entropy = judge_entropy_norm = None
    coverage_counts = coverage_classes = None
    coverage_entropy = coverage_entropy_norm = None

    if style_judge is not None:
        from tesi_gan.evaluation.style_classifier import (
            entropy_on_generator,
            format_style_coverage,
            style_coverage,
        )

        judge_entropy, judge_entropy_norm = entropy_on_generator(
            classifier=style_judge,
            generator=generator,
            n_samples=n_samples,
            batch_size=batch_size,
            device=device,
        )
        log.info(
            "Ambiguita' secondo il giudice terzo = %.4f nats (normalizzata %.3f)",
            judge_entropy, judge_entropy_norm,
        )

        # Copertura degli stili: senza, un'entropia alta e' ambigua fra fusione
        # stilistica e collasso su una zona generica.
        conteggi, coverage_entropy, coverage_entropy_norm = style_coverage(
            classifier=style_judge,
            generator=generator,
            n_samples=n_samples,
            batch_size=batch_size,
            device=device,
        )
        coverage_counts = [int(x) for x in conteggi]
        coverage_classes = list(judge_info.classes) if judge_info else None

        log.info(
            "Copertura degli stili (marginale delle classi predette) = %.3f normalizzata",
            coverage_entropy_norm,
        )
        if coverage_classes:
            log.info("\n%s", format_style_coverage(conteggi, coverage_classes))
        if coverage_entropy_norm < 0.85:
            log.warning(
                "Copertura degli stili disomogenea (%.3f): il generatore privilegia "
                "alcuni stili e ne ignora altri. Parte dell'ambiguita' misurata "
                "potrebbe essere collasso su una zona generica invece che fusione "
                "stilistica. Va dichiarato in tesi.",
                coverage_entropy_norm,
            )
        if judge_info is not None:
            log.info(
                "  riferimenti — reali: %.4f nats (%.3f) | soffitto log(K): %.4f | "
                "accuratezza del giudice: %.3f",
                judge_info.entropy_real,
                judge_info.entropy_real_normalized,
                judge_info.max_entropy,
                judge_info.val_accuracy,
            )
        if fid_value is not None and judge_entropy_norm > 0.9 and fid_value > 200:
            log.warning(
                "Ambiguita' quasi massima (%.3f) con FID pessimo (%.1f): l'ipotesi "
                "piu' probabile e' un generatore collassato, non ambiguita' "
                "stilistica. Guarda la griglia di campioni prima di interpretare.",
                judge_entropy_norm, fid_value,
            )
    else:
        log.warning(
            "Nessun giudice terzo fornito: l'ambiguita' non e' confrontabile fra "
            "DCGAN e CAN. Addestralo con `python -m tesi_gan.cli train-style-classifier`."
        )

    return EvaluationResult(
        fid=fid_value,
        inception_score_mean=is_mean,
        inception_score_std=is_std,
        style_entropy=entropy,
        style_entropy_normalized=entropy_norm,
        n_samples=n_samples,
        judge_entropy=judge_entropy,
        judge_entropy_normalized=judge_entropy_norm,
        judge_entropy_real=judge_info.entropy_real if judge_info else None,
        judge_entropy_real_normalized=judge_info.entropy_real_normalized if judge_info else None,
        judge_val_accuracy=judge_info.val_accuracy if judge_info else None,
        style_coverage_counts=coverage_counts,
        style_coverage_classes=coverage_classes,
        style_coverage_entropy=coverage_entropy,
        style_coverage_entropy_normalized=coverage_entropy_norm,
    )
