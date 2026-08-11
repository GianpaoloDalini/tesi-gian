"""Loss dell'esperimento illustrativo condizionato — FUORI da ADR-0003.

Non tocca `losses.py`, che e' il file su cui si regge il confronto DCGAN/CAN.
Logica AC-GAN-style: il discriminatore classifica lo stile su reali **e** generate,
il generatore e' premiato quando l'immagine prodotta e' classificata come lo stile
richiesto in ingresso. E' l'opposto della penalita' di ambiguita' della CAN, che
spinge lontano dalle categorie invece che verso quella richiesta.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import nn

from tesi_gan.training.losses import LossTerms

_bce = nn.BCEWithLogitsLoss()


def conditional_discriminator_loss(
    real_adv_logits: torch.Tensor,
    fake_adv_logits: torch.Tensor,
    real_style_logits: torch.Tensor,
    real_style_targets: torch.Tensor,
    fake_style_logits: torch.Tensor | None = None,
    fake_style_targets: torch.Tensor | None = None,
    label_smoothing: float = 0.0,
) -> LossTerms:
    """Loss del discriminatore condizionato.

    Classificazione dello stile sulle reali (obbligatoria) e, se fornita, anche
    sulle generate rispetto all'etichetta con cui sono state condizionate: aiuta il
    discriminatore a imparare confini di classe piu' netti, prassi standard nelle
    AC-GAN. Su questo file non vale l'invariante di ADR-0003: i due termini non
    sono pesati per restare equivalenti a nient'altro, sono pesati per la qualita'
    visiva del risultato.
    """
    real_target = torch.full_like(real_adv_logits, 1.0 - label_smoothing)
    fake_target = torch.zeros_like(fake_adv_logits)

    adversarial = _bce(real_adv_logits, real_target) + _bce(fake_adv_logits, fake_target)
    style_ce_real = F.cross_entropy(real_style_logits, real_style_targets)
    total = adversarial + style_ce_real

    style_ce_fake = None
    if fake_style_logits is not None and fake_style_targets is not None:
        style_ce_fake = F.cross_entropy(fake_style_logits, fake_style_targets)
        total = total + style_ce_fake

    return LossTerms(
        total=total,
        adversarial=adversarial,
        style_classification=style_ce_real,
        style_ambiguity=style_ce_fake,  # riuso il campo: qui e' CE sulle generate, non ambiguita'
    )


def conditional_generator_loss(
    fake_adv_logits: torch.Tensor,
    fake_style_logits: torch.Tensor,
    target_labels: torch.Tensor,
    classification_weight: float = 1.0,
) -> LossTerms:
    """Loss del generatore condizionato.

    Non saturante sul termine avversario, come in `losses.py`. Il termine di
    classificazione premia la fedelta' all'etichetta richiesta: e' l'opposto della
    `style_ambiguity` della CAN, che la penalizza.
    """
    target = torch.ones_like(fake_adv_logits)
    adversarial = _bce(fake_adv_logits, target)
    classification = F.cross_entropy(fake_style_logits, target_labels)
    total = adversarial + classification_weight * classification

    return LossTerms(total=total, adversarial=adversarial, style_classification=classification)
