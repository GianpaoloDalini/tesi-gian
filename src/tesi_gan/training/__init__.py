"""Addestramento. Un solo ciclo per le due condizioni comparative DCGAN/CAN; la
differenza sta nelle loss (ADR-0003).

`ConditionalTrainer` addestra l'esperimento illustrativo condizionato per stile,
**fuori** dal confronto: ciclo separato, loss separate (`conditional_losses.py`).
"""

from tesi_gan.training.conditional_losses import (
    conditional_discriminator_loss,
    conditional_generator_loss,
)
from tesi_gan.training.conditional_trainer import ConditionalTrainer
from tesi_gan.training.losses import discriminator_loss, generator_loss
from tesi_gan.training.trainer import Trainer, count_parameters

__all__ = [
    "Trainer",
    "count_parameters",
    "discriminator_loss",
    "generator_loss",
    "ConditionalTrainer",
    "conditional_discriminator_loss",
    "conditional_generator_loss",
]
