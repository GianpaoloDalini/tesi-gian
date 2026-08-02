"""Pipeline dati. Le etichette di stile sono obbligatorie: senza, la CAN non e'
addestrabile (ADR-0003)."""

from tesi_gan.data.dataset import (
    SyntheticStyleDataset,
    build_dataloader,
    build_dataset,
    build_transform,
    denormalize,
    num_styles_of,
)

__all__ = [
    "SyntheticStyleDataset",
    "build_dataloader",
    "build_dataset",
    "build_transform",
    "denormalize",
    "num_styles_of",
]
