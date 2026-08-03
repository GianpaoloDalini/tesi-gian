"""Pipeline dati. Le etichette di stile sono obbligatorie: senza, la CAN non e'
addestrabile (ADR-0003)."""

from tesi_gan.data.dataset import (
    SyntheticStyleDataset,
    assert_same_classes,
    build_dataloader,
    build_dataset,
    build_reference_dataset,
    build_transform,
    denormalize,
    num_styles_of,
)

__all__ = [
    "SyntheticStyleDataset",
    "assert_same_classes",
    "build_dataloader",
    "build_dataset",
    "build_reference_dataset",
    "build_transform",
    "denormalize",
    "num_styles_of",
]
