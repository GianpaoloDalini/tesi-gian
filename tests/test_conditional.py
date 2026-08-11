"""Test dell'esperimento illustrativo condizionato — FUORI da ADR-0003.

Non verificano un invariante di confronto (non ce n'e' uno: e' un'architettura a
se'), verificano che il condizionamento funzioni davvero (etichette diverse ->
output diversi) e che non tocchi nulla dell'impianto DCGAN/CAN.
"""

import pytest

torch = pytest.importorskip("torch")

from tesi_gan.models import Discriminator, Generator  # noqa: E402
from tesi_gan.models.conditional import (  # noqa: E402
    ConditionalDiscriminator,
    ConditionalGenerator,
    build_conditional_models,
)
from tesi_gan.training.conditional_losses import (  # noqa: E402
    conditional_discriminator_loss,
    conditional_generator_loss,
)

BATCH = 4
NUM_STYLES = 5
RISOLUZIONI = [64, 128]


# --------------------------------------------------------------------------- #
#  Non deve toccare l'impianto comparativo
# --------------------------------------------------------------------------- #

def test_non_importa_ne_modifica_le_classi_di_adr_0003():
    """Generator/Discriminator restano quelli di sempre: nessuna sottoclasse,
    nessun monkeypatch. Se questo test fallisse per un import rotto, vorrebbe dire
    che il modulo condizionato ha introdotto una dipendenza pericolosa."""
    assert ConditionalGenerator is not Generator
    assert ConditionalDiscriminator is not Discriminator
    assert not issubclass(ConditionalGenerator, Generator)
    assert not issubclass(ConditionalDiscriminator, Discriminator)


# --------------------------------------------------------------------------- #
#  Forme, a entrambe le risoluzioni gia' usate nell'impianto principale
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("image_size", RISOLUZIONI)
def test_generatore_condizionato_produce_la_risoluzione_richiesta(image_size):
    g = ConditionalGenerator(num_styles=NUM_STYLES, latent_dim=16, features=8, image_size=image_size)
    z = torch.randn(BATCH, 16, 1, 1)
    labels = torch.randint(0, NUM_STYLES, (BATCH,))
    out = g(z, labels)
    assert out.shape == (BATCH, 3, image_size, image_size)
    assert out.min() >= -1.0 and out.max() <= 1.0


@pytest.mark.parametrize("image_size", RISOLUZIONI)
def test_discriminatore_condizionato_accetta_la_risoluzione_richiesta(image_size):
    d = ConditionalDiscriminator(num_styles=NUM_STYLES, features=8, image_size=image_size)
    adv, style = d(torch.randn(BATCH, 3, image_size, image_size))
    assert adv.shape == (BATCH,)
    assert style.shape == (BATCH, NUM_STYLES)


def test_num_styles_zero_o_negativo_rifiutato():
    with pytest.raises(ValueError):
        ConditionalGenerator(num_styles=0)
    with pytest.raises(ValueError):
        ConditionalDiscriminator(num_styles=0)


# --------------------------------------------------------------------------- #
#  Il condizionamento deve fare qualcosa, non essere un ingresso ignorato
# --------------------------------------------------------------------------- #

def test_etichette_diverse_producono_immagini_diverse():
    """Controllo di sanita' minimo ma decisivo: se lo stesso z con due etichette
    diverse producesse la stessa immagine, il condizionamento sarebbe un parametro
    morto e l'intero esperimento illustrativo non avrebbe senso."""
    torch.manual_seed(0)
    g = ConditionalGenerator(num_styles=NUM_STYLES, latent_dim=16, features=8, image_size=64)
    z = torch.randn(1, 16, 1, 1)
    label_a = torch.tensor([0])
    label_b = torch.tensor([1])
    out_a = g(z, label_a)
    out_b = g(z, label_b)
    assert not torch.allclose(out_a, out_b)


def test_stessa_etichetta_stesso_z_e_deterministico():
    torch.manual_seed(0)
    g = ConditionalGenerator(num_styles=NUM_STYLES, latent_dim=16, features=8, image_size=64)
    g.eval()
    z = torch.randn(1, 16, 1, 1)
    label = torch.tensor([2])
    with torch.no_grad():
        out1 = g(z, label)
        out2 = g(z, label)
    assert torch.equal(out1, out2)


# --------------------------------------------------------------------------- #
#  build_conditional_models
# --------------------------------------------------------------------------- #

def test_build_conditional_models_rispetta_la_configurazione():
    from omegaconf import OmegaConf

    cfg = OmegaConf.create({
        "model": {
            "latent_dim": 16, "generator_features": 8, "discriminator_features": 8,
            "channels": 3, "num_styles": NUM_STYLES,
        },
        "data": {"image_size": 64},
    })
    g, d = build_conditional_models(cfg)
    assert g.num_styles == NUM_STYLES
    assert d.num_styles == NUM_STYLES
    assert g.image_size == 64


def test_build_conditional_models_richiede_num_styles():
    from omegaconf import OmegaConf

    cfg = OmegaConf.create({
        "model": {
            "latent_dim": 16, "generator_features": 8, "discriminator_features": 8,
            "channels": 3, "num_styles": None,
        },
        "data": {"image_size": 64},
    })
    with pytest.raises(ValueError, match="num_styles"):
        build_conditional_models(cfg)


# --------------------------------------------------------------------------- #
#  Loss
# --------------------------------------------------------------------------- #

def test_loss_generatore_condizionato_e_differenziabile():
    g = ConditionalGenerator(num_styles=NUM_STYLES, latent_dim=16, features=8)
    d = ConditionalDiscriminator(num_styles=NUM_STYLES, features=8)
    z = torch.randn(BATCH, 16, 1, 1)
    labels = torch.randint(0, NUM_STYLES, (BATCH,))
    fake = g(z, labels)
    fake_adv, fake_style = d(fake)
    terms = conditional_generator_loss(fake_adv, fake_style, labels)
    terms.total.backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in g.parameters())


def test_loss_discriminatore_condizionato_penalizza_classificazione_sbagliata():
    """Con logit di stile fortemente sbagliati la cross-entropy deve essere alta;
    con logit fortemente giusti, bassa. Non e' un test di training, solo che la
    loss risponda nella direzione corretta."""
    real_adv = torch.randn(BATCH)
    fake_adv = torch.randn(BATCH)
    targets = torch.zeros(BATCH, dtype=torch.long)

    logit_giusti = torch.full((BATCH, NUM_STYLES), -10.0)
    logit_giusti[:, 0] = 10.0  # fortemente classe 0, che e' il target

    logit_sbagliati = torch.full((BATCH, NUM_STYLES), -10.0)
    logit_sbagliati[:, 1] = 10.0  # fortemente classe 1, sbagliata

    buona = conditional_discriminator_loss(real_adv, fake_adv, logit_giusti, targets)
    cattiva = conditional_discriminator_loss(real_adv, fake_adv, logit_sbagliati, targets)
    assert buona.style_classification < cattiva.style_classification


# --------------------------------------------------------------------------- #
#  Trainer — smoke test end-to-end su dati sintetici
# --------------------------------------------------------------------------- #

def test_conditional_trainer_smoke(tmp_path):
    from omegaconf import OmegaConf

    from tesi_gan.data import SyntheticStyleDataset, build_dataloader
    from tesi_gan.training import ConditionalTrainer

    cfg = OmegaConf.create({
        "seed": 0,
        "model": {
            "name": "conditional_artgan",
            "latent_dim": 16, "generator_features": 8, "discriminator_features": 8,
            "channels": 3, "num_styles": NUM_STYLES, "classification_weight": 1.0,
        },
        "data": {"image_size": 64, "name": "synthetic", "synthetic_size": 32,
                  "synthetic_styles": NUM_STYLES},
        "training": {
            "batch_size": BATCH, "epochs": 1, "lr_generator": 2e-4, "lr_discriminator": 2e-4,
            "beta1": 0.5, "beta2": 0.999, "checkpoint_every": 1, "label_smoothing": 0.0,
        },
        "paths": {"checkpoints": str(tmp_path / "ckpt"), "samples": str(tmp_path / "samples")},
        "progress": False,
    })

    dataset = SyntheticStyleDataset(n=32, image_size=64, num_styles=NUM_STYLES)
    dataloader = build_dataloader(cfg, dataset)
    g, d = build_conditional_models(cfg)
    trainer = ConditionalTrainer(cfg, g, d, dataloader, device=torch.device("cpu"))
    trainer.fit(1)

    grid = trainer.sample_grid()
    assert grid.shape[0] == NUM_STYLES * 6  # _CAMPIONI_PER_STILE
    assert grid.min() >= 0.0 and grid.max() <= 1.0

    path = trainer.save_checkpoint("final.pt")
    assert path.exists()


def test_conditional_checkpoint_non_si_carica_su_trainer_incompatibile(tmp_path):
    from omegaconf import OmegaConf

    from tesi_gan.data import SyntheticStyleDataset, build_dataloader
    from tesi_gan.training import ConditionalTrainer

    def _cfg(num_styles, ckpt_dir):
        return OmegaConf.create({
            "seed": 0,
            "model": {
                "name": "conditional_artgan",
                "latent_dim": 16, "generator_features": 8, "discriminator_features": 8,
                "channels": 3, "num_styles": num_styles, "classification_weight": 1.0,
            },
            "data": {"image_size": 64, "name": "synthetic", "synthetic_size": 16,
                      "synthetic_styles": num_styles},
            "training": {
                "batch_size": BATCH, "epochs": 1, "lr_generator": 2e-4, "lr_discriminator": 2e-4,
                "beta1": 0.5, "beta2": 0.999, "checkpoint_every": 1, "label_smoothing": 0.0,
            },
            "paths": {"checkpoints": str(ckpt_dir), "samples": str(ckpt_dir / "samples")},
            "progress": False,
        })

    device = torch.device("cpu")

    cfg_a = _cfg(NUM_STYLES, tmp_path / "a")
    dataset_a = SyntheticStyleDataset(n=16, image_size=64, num_styles=NUM_STYLES)
    g_a, d_a = build_conditional_models(cfg_a)
    trainer_a = ConditionalTrainer(
        cfg_a, g_a, d_a, build_dataloader(cfg_a, dataset_a), device
    )
    path = trainer_a.save_checkpoint("final.pt")

    cfg_b = _cfg(NUM_STYLES + 1, tmp_path / "b")
    dataset_b = SyntheticStyleDataset(n=16, image_size=64, num_styles=NUM_STYLES + 1)
    g_b, d_b = build_conditional_models(cfg_b)
    trainer_b = ConditionalTrainer(
        cfg_b, g_b, d_b, build_dataloader(cfg_b, dataset_b), device
    )
    with pytest.raises(RuntimeError, match="stili"):
        trainer_b.load_checkpoint(path)
