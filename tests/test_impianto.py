"""Test dell'impianto sperimentale di ADR-0003.

Questi non sono test di correttezza del codice: sono test della **validita' del
disegno sperimentale**. Verificano automaticamente le proprieta' su cui si regge la
tesi del capitolo dei risultati, cioe' che DCGAN e CAN differiscano *soltanto* per la
funzione di perdita.

Se uno di questi test fallisce, non e' un bug: e' il confronto sperimentale che non
e' piu' valido, e i numeri gia' prodotti vanno rifatti.
"""

import pytest

torch = pytest.importorskip("torch")

from tesi_gan.models import Discriminator, Generator  # noqa: E402
from tesi_gan.training.losses import (  # noqa: E402
    cross_entropy_uniform,
    discriminator_loss,
    generator_loss,
    negative_entropy,
)

BATCH = 4
NUM_STYLES = 5

# Le risoluzioni su cui l'invariante va verificato. Aggiungerne una qui basta a
# estendere a essa tutti i controlli di validita' del disegno sperimentale.
RISOLUZIONI = [64, 128]


def _generatori(image_size: int = 64):
    torch.manual_seed(0)
    g_dcgan = Generator(image_size=image_size)
    torch.manual_seed(0)
    g_can = Generator(image_size=image_size)
    return g_dcgan, g_can


def _discriminatori(image_size: int = 64):
    torch.manual_seed(0)
    d_dcgan = Discriminator(style_head=False, image_size=image_size)
    torch.manual_seed(0)
    d_can = Discriminator(style_head=True, num_styles=NUM_STYLES, image_size=image_size)
    return d_dcgan, d_can


# --------------------------------------------------------------------------- #
#  L'invariante deve valere a OGNI risoluzione
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("image_size", RISOLUZIONI)
def test_generatore_identico_a_ogni_risoluzione(image_size):
    """Generalizzare le reti sulla risoluzione non deve rompere ADR-0003.

    La tentazione, passando a 128, era scrivere una seconda coppia di classi. Questo
    test verifica che l'invariante — stessa classe, un solo booleano di differenza —
    valga su tutte le risoluzioni supportate.
    """
    g1, g2 = _generatori(image_size)
    for (n1, p1), (n2, p2) in zip(g1.named_parameters(), g2.named_parameters()):
        assert n1 == n2 and torch.equal(p1, p2)


@pytest.mark.parametrize("image_size", RISOLUZIONI)
def test_backbone_identica_a_ogni_risoluzione(image_size):
    d1, d2 = _discriminatori(image_size)
    for (n1, p1), (n2, p2) in zip(
        d1.backbone.named_parameters(), d2.backbone.named_parameters()
    ):
        assert n1 == n2 and torch.equal(p1, p2)


@pytest.mark.parametrize("image_size", RISOLUZIONI)
def test_generatore_produce_la_risoluzione_richiesta(image_size):
    g = Generator(latent_dim=16, features=8, image_size=image_size)
    uscita = g(torch.randn(2, 16, 1, 1))
    assert uscita.shape == (2, 3, image_size, image_size)
    assert uscita.min() >= -1.0 and uscita.max() <= 1.0


@pytest.mark.parametrize("image_size", RISOLUZIONI)
def test_discriminatore_accetta_la_risoluzione_richiesta(image_size):
    d = Discriminator(features=8, style_head=True, num_styles=NUM_STYLES,
                      image_size=image_size)
    adv, stile = d(torch.randn(2, 3, image_size, image_size))
    assert adv.shape == (2,)
    assert stile.shape == (2, NUM_STYLES)


@pytest.mark.parametrize("image_size", [12, 100, 7, 0])
def test_risoluzioni_non_supportate_falliscono_esplicitamente(image_size):
    """L'architettura raddoppia da 4x4: una risoluzione che non sia potenza di due
    non e' rappresentabile e deve fallire subito, non produrre forme sbagliate."""
    with pytest.raises(ValueError, match="potenza di due"):
        Generator(image_size=image_size)


def test_risoluzioni_diverse_danno_reti_diverse():
    """Controllo di sanita': se 64 e 128 producessero la stessa rete, il parametro
    non starebbe facendo nulla e i run a 128 sarebbero run a 64 travestiti."""
    g64 = Generator(latent_dim=16, features=8, image_size=64)
    g128 = Generator(latent_dim=16, features=8, image_size=128)
    n64 = sum(p.numel() for p in g64.parameters())
    n128 = sum(p.numel() for p in g128.parameters())
    assert n128 > n64


# --------------------------------------------------------------------------- #
#  Invarianti del disegno sperimentale
# --------------------------------------------------------------------------- #

def test_generatore_identico_nelle_due_condizioni():
    """Il generatore deve essere bit-a-bit lo stesso: e' la stessa classe."""
    g1, g2 = _generatori()
    for (k1, v1), (k2, v2) in zip(g1.state_dict().items(), g2.state_dict().items(), strict=True):
        assert k1 == k2
        assert torch.equal(v1, v2), f"Parametro divergente nel generatore: {k1}"


def test_backbone_del_discriminatore_identica():
    """La CAN aggiunge una testa, non modifica la backbone condivisa."""
    d_dcgan, d_can = _discriminatori()
    b1 = d_dcgan.backbone.state_dict()
    b2 = d_can.backbone.state_dict()
    assert b1.keys() == b2.keys()
    for k in b1:
        assert torch.equal(b1[k], b2[k]), f"Backbone divergente: {k}"


def test_can_senza_ambiguita_degenera_in_dcgan():
    """Con peso 0 il termine di ambiguita' sparisce: le due loss coincidono.

    E' l'ablazione che dimostra che l'implementazione condivisa non introduce
    differenze spurie fra le condizioni.
    """
    torch.manual_seed(0)
    fake_adv = torch.randn(BATCH)
    fake_style = torch.randn(BATCH, NUM_STYLES)

    senza_testa = generator_loss(fake_adv, fake_style_logits=None)
    con_testa_peso_zero = generator_loss(
        fake_adv, fake_style_logits=fake_style, ambiguity_weight=0.0
    )

    assert torch.allclose(senza_testa.total, con_testa_peso_zero.total)
    assert con_testa_peso_zero.style_ambiguity is None


def test_discriminatore_senza_testa_di_stile_rifiuta_num_styles_mancante():
    with pytest.raises(ValueError, match="num_styles"):
        Discriminator(style_head=True, num_styles=None)


# --------------------------------------------------------------------------- #
#  Forme e comportamento delle reti
# --------------------------------------------------------------------------- #

def test_generatore_produce_64x64_in_meno_uno_uno():
    g = Generator(latent_dim=100)
    z = torch.randn(BATCH, 100, 1, 1)
    out = g(z)
    assert out.shape == (BATCH, 3, 64, 64)
    assert out.min() >= -1.0 and out.max() <= 1.0


def test_discriminatore_dcgan_non_emette_logit_di_stile():
    d = Discriminator(style_head=False)
    adv, style = d(torch.randn(BATCH, 3, 64, 64))
    assert adv.shape == (BATCH,)
    assert style is None


def test_discriminatore_can_emette_logit_di_stile():
    d = Discriminator(style_head=True, num_styles=NUM_STYLES)
    adv, style = d(torch.randn(BATCH, 3, 64, 64))
    assert adv.shape == (BATCH,)
    assert style.shape == (BATCH, NUM_STYLES)


# --------------------------------------------------------------------------- #
#  Penalita' di ambiguita'
# --------------------------------------------------------------------------- #

def test_ambiguita_minima_sulla_posterior_uniforme():
    """Entrambe le penalita' devono premiare la posterior uniforme.

    E' la proprieta' che rende il termine interpretabile come 'ambiguita'':
    se non valesse, il generatore verrebbe spinto altrove.
    """
    uniforme = torch.zeros(BATCH, NUM_STYLES)          # softmax -> 1/K
    concentrata = torch.zeros(BATCH, NUM_STYLES)
    concentrata[:, 0] = 10.0                            # softmax -> quasi one-hot

    assert cross_entropy_uniform(uniforme) < cross_entropy_uniform(concentrata)
    assert negative_entropy(uniforme) < negative_entropy(concentrata)


def test_cross_entropy_uniforme_vale_log_k():
    import math

    uniforme = torch.zeros(BATCH, NUM_STYLES)
    assert cross_entropy_uniform(uniforme).item() == pytest.approx(math.log(NUM_STYLES), abs=1e-5)


# --------------------------------------------------------------------------- #
#  Loss complete
# --------------------------------------------------------------------------- #

def test_loss_discriminatore_include_lo_stile_solo_sulle_reali():
    real_adv = torch.randn(BATCH)
    fake_adv = torch.randn(BATCH)
    real_style = torch.randn(BATCH, NUM_STYLES)
    targets = torch.randint(0, NUM_STYLES, (BATCH,))

    dcgan = discriminator_loss(real_adv, fake_adv)
    can = discriminator_loss(real_adv, fake_adv, real_style, targets)

    assert dcgan.style_classification is None
    assert can.style_classification is not None
    assert torch.allclose(dcgan.adversarial, can.adversarial)
    assert can.total > can.adversarial  # la cross-entropy e' strettamente positiva


def test_loss_sono_differenziabili():
    g = Generator()
    d = Discriminator(style_head=True, num_styles=NUM_STYLES)
    z = torch.randn(BATCH, g.latent_dim, 1, 1)
    fake_adv, fake_style = d(g(z))
    terms = generator_loss(fake_adv, fake_style, ambiguity_weight=1.0)
    terms.total.backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in g.parameters())


# --------------------------------------------------------------------------- #
#  Persistenza
# --------------------------------------------------------------------------- #

def test_checkpoint_rifiuta_di_mischiare_le_condizioni(tmp_path):
    """Riprendere un run CAN da un checkpoint DCGAN invaliderebbe il confronto."""
    from omegaconf import OmegaConf

    from tesi_gan.training import Trainer

    def _cfg(model_name, style_head):
        return OmegaConf.create(
            {
                "seed": 42,
                "model": {
                    "name": model_name,
                    "latent_dim": 100,
                    "channels": 3,
                    "generator_features": 8,
                    "discriminator_features": 8,
                    "num_styles": NUM_STYLES if style_head else None,
                    "style_ambiguity_weight": 1.0,
                },
                "training": {
                    "batch_size": BATCH,
                    "epochs": 1,
                    "lr_generator": 2e-4,
                    "lr_discriminator": 2e-4,
                    "beta1": 0.5,
                    "beta2": 0.999,
                    "checkpoint_every": 1,
                    "label_smoothing": 0.0,
                },
                "paths": {"checkpoints": str(tmp_path)},
            }
        )

    device = torch.device("cpu")
    cfg_dcgan = _cfg("dcgan", False)
    t_dcgan = Trainer(
        cfg_dcgan,
        Generator(features=8),
        Discriminator(features=8, style_head=False),
        dataloader=[],
        device=device,
    )
    path = t_dcgan.save_checkpoint("dcgan.pt")

    cfg_can = _cfg("can", True)
    t_can = Trainer(
        cfg_can,
        Generator(features=8),
        Discriminator(features=8, style_head=True, num_styles=NUM_STYLES),
        dataloader=[],
        device=device,
    )
    with pytest.raises(RuntimeError, match="condizione"):
        t_can.load_checkpoint(path)
