"""Architetture sperimentali.

DCGAN e CAN non sono due modelli distinti ma due configurazioni dello stesso
codice: vedi `networks.py` e ADR-0003.

`conditional.py` e' un'architettura terza, **fuori** dal confronto di ADR-0003:
un generatore condizionato per stile, per soli scopi illustrativi (vedi il
docstring del modulo).
"""

from tesi_gan.models.conditional import (
    ConditionalDiscriminator,
    ConditionalGenerator,
    build_conditional_models,
)
from tesi_gan.models.networks import (
    Discriminator,
    Generator,
    build_generator,
    build_models,
)

__all__ = [
    "Discriminator",
    "Generator",
    "build_generator",
    "build_models",
    "ConditionalGenerator",
    "ConditionalDiscriminator",
    "build_conditional_models",
]
