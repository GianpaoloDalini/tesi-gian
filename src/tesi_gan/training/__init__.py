"""Addestramento. Un solo ciclo per entrambe le condizioni sperimentali; la
differenza sta nelle loss (ADR-0003)."""

from tesi_gan.training.losses import discriminator_loss, generator_loss
from tesi_gan.training.trainer import Trainer, count_parameters

__all__ = ["Trainer", "count_parameters", "discriminator_loss", "generator_loss"]
