"""Test del classificatore di stile terzo (ADR-0005).

Verificano le proprieta' da cui dipende la validita' della metrica di ambiguita':
che il giudice sia lo stesso per entrambe le condizioni, che lo split sia
stratificato e riproducibile, che l'entropia si comporti come deve agli estremi, e
che il caricamento fallisca invece di produrre numeri privi di significato.
"""

from __future__ import annotations

import math

import pytest

torch = pytest.importorskip("torch")

from tesi_gan.data.dataset import SyntheticStyleDataset  # noqa: E402
from tesi_gan.evaluation.style_classifier import (  # noqa: E402
    StyleClassifier,
    StyleClassifierInfo,
    _entropy_of_logits,
    entropy_on_generator,
    load_style_classifier,
    save_style_classifier,
    stratified_split,
)
from tesi_gan.models import Generator  # noqa: E402

CPU = torch.device("cpu")


# --------------------------------------------------------------------------- #
#  Architettura
# --------------------------------------------------------------------------- #

def test_classificatore_emette_un_logit_per_stile():
    classifier = StyleClassifier(num_styles=6)
    logits = classifier(torch.randn(4, 3, 64, 64))
    assert logits.shape == (4, 6)


def test_classificatore_rifiuta_meno_di_due_stili():
    """Con una sola classe l'entropia e' costantemente zero: la metrica non esiste."""
    with pytest.raises(ValueError, match="almeno due stili"):
        StyleClassifier(num_styles=1)


def test_classificatore_non_e_pre_addestrato_su_imagenet():
    """Nessun peso scaricato: il giudice non eredita il bias fotografico di ImageNet,
    che e' esattamente la critica che la tesi muove a FID e IS."""
    classifier = StyleClassifier(num_styles=6)
    assert not any("resnet" in name.lower() for name, _ in classifier.named_modules())


# --------------------------------------------------------------------------- #
#  Entropia: comportamento agli estremi
# --------------------------------------------------------------------------- #

def test_entropia_massima_sulla_posterior_uniforme():
    """Logit tutti uguali -> posterior uniforme -> entropia = log(K)."""
    logits = torch.zeros(8, 6)
    entropy = _entropy_of_logits(logits)
    assert torch.allclose(entropy, torch.full((8,), math.log(6)), atol=1e-5)


def test_entropia_quasi_nulla_sulla_posterior_degenere():
    """Un logit enormemente piu' grande -> posterior concentrata -> entropia ~ 0."""
    logits = torch.full((8, 6), -50.0)
    logits[:, 2] = 50.0
    assert float(_entropy_of_logits(logits).max()) < 1e-4


def test_entropia_normalizzata_sta_in_zero_uno():
    classifier = StyleClassifier(num_styles=6)
    generator = Generator(latent_dim=16, features=8)
    _, normalized = entropy_on_generator(
        classifier=classifier, generator=generator,
        n_samples=8, batch_size=4, device=CPU,
    )
    assert 0.0 <= normalized <= 1.0


# --------------------------------------------------------------------------- #
#  Il punto centrale: la misura esiste per entrambe le condizioni
# --------------------------------------------------------------------------- #

def test_ambiguita_misurabile_su_generatore_qualunque():
    """**La ragione per cui questo modulo esiste.**

    Il giudice non riceve ne' il discriminatore ne' l'indicazione della condizione:
    misura un generatore e basta. Quindi la stessa metrica vale per DCGAN e CAN, ed
    e' cio' che rende possibile il confronto di ADR-0003.
    """
    classifier = StyleClassifier(num_styles=6)
    for latent_dim in (16, 32):
        generator = Generator(latent_dim=latent_dim, features=8)
        entropy, normalized = entropy_on_generator(
            classifier=classifier, generator=generator,
            n_samples=8, batch_size=4, device=CPU,
        )
        assert entropy > 0.0
        assert 0.0 <= normalized <= 1.0


def test_misura_riproducibile_a_parita_di_seed():
    """Due misure con lo stesso seed danno lo stesso numero: senza, le differenze
    fra condizioni sarebbero indistinguibili dal rumore di campionamento."""
    classifier = StyleClassifier(num_styles=6).eval()
    generator = Generator(latent_dim=16, features=8).eval()

    torch.manual_seed(7)
    first, _ = entropy_on_generator(classifier, generator, 16, 8, CPU)
    torch.manual_seed(7)
    second, _ = entropy_on_generator(classifier, generator, 16, 8, CPU)
    assert first == pytest.approx(second, abs=1e-6)


# --------------------------------------------------------------------------- #
#  Split stratificato
# --------------------------------------------------------------------------- #

def test_split_preserva_le_proporzioni_di_classe():
    dataset = SyntheticStyleDataset(n=120, num_styles=6)
    train, val = stratified_split(dataset, val_fraction=0.25, seed=0)

    val_labels = [dataset.targets[i] for i in val.indices]
    counts = {label: val_labels.count(label) for label in range(6)}
    assert len(set(counts.values())) == 1, f"validation sbilanciata: {counts}"
    assert len(train) + len(val) == len(dataset)


def test_split_riproducibile_a_parita_di_seed():
    dataset = SyntheticStyleDataset(n=120, num_styles=6)
    a, _ = stratified_split(dataset, val_fraction=0.2, seed=3)
    b, _ = stratified_split(dataset, val_fraction=0.2, seed=3)
    assert a.indices == b.indices


def test_split_diverso_con_seed_diverso():
    dataset = SyntheticStyleDataset(n=120, num_styles=6)
    a, _ = stratified_split(dataset, val_fraction=0.2, seed=3)
    b, _ = stratified_split(dataset, val_fraction=0.2, seed=99)
    assert a.indices != b.indices


def test_split_rifiuta_frazioni_fuori_range():
    dataset = SyntheticStyleDataset(n=60, num_styles=6)
    for bad in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError, match="val_fraction"):
            stratified_split(dataset, val_fraction=bad, seed=0)


# --------------------------------------------------------------------------- #
#  Persistenza e controlli di coerenza
# --------------------------------------------------------------------------- #

def _info(classes: list[str]) -> StyleClassifierInfo:
    return StyleClassifierInfo(
        num_styles=len(classes), classes=classes, val_accuracy=0.8,
        train_size=100, val_size=20, epochs=1, seed=42,
        entropy_real=0.5, entropy_real_normalized=0.28,
        max_entropy=math.log(len(classes)),
    )


def test_salvataggio_e_caricamento_conservano_i_pesi(tmp_path):
    classes = ["baroque", "impressionism", "ukiyo_e"]
    original = StyleClassifier(num_styles=3)
    save_style_classifier(original, _info(classes), tmp_path)

    loaded, info = load_style_classifier(tmp_path, CPU, expected_classes=classes)
    assert info.classes == classes
    for (_, a), (_, b) in zip(original.state_dict().items(), loaded.state_dict().items()):
        assert torch.allclose(a, b)


def test_giudice_caricato_e_congelato(tmp_path):
    """Il giudice non deve poter essere addestrato durante la valutazione."""
    save_style_classifier(StyleClassifier(num_styles=3), _info(["a", "b", "c"]), tmp_path)
    loaded, _ = load_style_classifier(tmp_path, CPU)
    assert not any(p.requires_grad for p in loaded.parameters())
    assert not loaded.training


def test_caricamento_rifiuta_classi_diverse(tmp_path):
    """Valutare con un giudice addestrato su altri stili produrrebbe numeri privi di
    significato: il fallimento dev'essere rumoroso, non silenzioso."""
    save_style_classifier(
        StyleClassifier(num_styles=3), _info(["baroque", "impressionism", "ukiyo_e"]), tmp_path
    )
    with pytest.raises(RuntimeError, match="non sarebbero confrontabili"):
        load_style_classifier(tmp_path, CPU, expected_classes=["cubism", "pop_art", "realism"])


def test_caricamento_assente_spiega_come_rimediare(tmp_path):
    with pytest.raises(FileNotFoundError, match="train-style-classifier"):
        load_style_classifier(tmp_path / "inesistente", CPU)
