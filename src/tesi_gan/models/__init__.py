"""Architetture sperimentali.

DCGAN e CAN non sono due modelli distinti ma due configurazioni dello stesso
codice: vedi `networks.py` e ADR-0003.
"""

from tesi_gan.models.networks import (
    Discriminator,
    Generator,
    build_generator,
    build_models,
)

__all__ = ["Discriminator", "Generator", "build_generator", "build_models"]
