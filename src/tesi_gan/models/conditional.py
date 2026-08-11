"""Generatore condizionato per stile — esperimento illustrativo, FUORI da ADR-0003.

**Perche' questo file esiste separato da `networks.py`.** L'impianto comparativo
DCGAN/CAN vale perche' le due condizioni condividono lo stesso generatore e la
stessa backbone del discriminatore: un'unica variabile indipendente (la loss). Un
generatore condizionato per stile e' un'architettura diversa per costruzione (prende
in ingresso anche l'etichetta), quindi non puo' essere una terza condizione dello
stesso confronto senza romperne l'invariante. Vive qui, in un modulo a parte, così
`networks.py` — il file su cui si regge ADR-0003 — resta esattamente com'era.

**Cosa fa e cosa non dimostra.** Ispirato al condizionamento categorico di ArtGAN
(Tan, Chan, Aguirre & Tanaka — % TODO[CITE]: paper non ancora in
`thesis/references/bibliography.bib`, da importare in Zotero prima di citarlo in
tesi) e in particolare al progetto studentesco non ufficiale
github.com/sebastienmeyer2/image-synthesis-artgan, che lo implementa con modifiche
proprie non documentate nel dettaglio. Qui l'obiettivo e' **solo illustrativo**:
ottenere campioni piu' nitidi e stilisticamente coerenti da mostrare in tesi come
contrasto visivo rispetto ai campioni incondizionati di DCGAN/CAN — non un
confronto quantitativo, non una replica verificata dei loro numeri (che non
pubblicano: solo una galleria di immagini scelte, senza FID/IS dichiarati). Se
finisce in tesi, va scritto esplicitamente con questo limite.

Il condizionamento e' per concatenazione: l'etichetta di stile in one-hot viene
concatenata al vettore latente prima del primo strato del generatore, e il
discriminatore ha una testa ausiliaria di classificazione (stesso principio della
testa di stile della CAN, ma usata in verso opposto — vedi
`training/conditional_losses.py`).
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import nn

from tesi_gan.models.networks import _init_weights, _stadi


class ConditionalGenerator(nn.Module):
    """Generatore condizionato: mappa (z, stile) in un'immagine RGB.

    Stessa progressione spaziale del `Generator` incondizionato (4x4 -> ... ->
    `image_size`), ma il primo strato riceve `latent_dim + num_styles` canali
    invece di `latent_dim`: l'etichetta in one-hot e' concatenata al rumore.
    """

    def __init__(
        self,
        num_styles: int,
        latent_dim: int = 100,
        features: int = 64,
        channels: int = 3,
        image_size: int = 64,
    ) -> None:
        super().__init__()
        if num_styles <= 0:
            raise ValueError("num_styles deve essere > 0: senza classi non c'e' nulla da condizionare.")
        self.latent_dim = latent_dim
        self.num_styles = num_styles
        self.image_size = image_size
        stadi = _stadi(image_size)

        def block(in_c: int, out_c: int, stride: int, padding: int) -> nn.Sequential:
            return nn.Sequential(
                nn.ConvTranspose2d(in_c, out_c, 4, stride, padding, bias=False),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
            )

        larghezze = [features * 2 ** (stadi - 1 - i) for i in range(stadi)]
        strati: list[nn.Module] = [block(latent_dim + num_styles, larghezze[0], 1, 0)]
        for i in range(stadi - 1):
            strati.append(block(larghezze[i], larghezze[i + 1], 2, 1))
        strati += [
            nn.ConvTranspose2d(larghezze[-1], channels, 4, 2, 1, bias=False),
            nn.Tanh(),
        ]

        self.net = nn.Sequential(*strati)
        self.apply(_init_weights)

    def forward(self, z: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        if z.dim() == 2:
            z = z.view(z.size(0), z.size(1), 1, 1)
        one_hot = F.one_hot(labels.long(), num_classes=self.num_styles).float()
        one_hot = one_hot.view(one_hot.size(0), self.num_styles, 1, 1)
        z_condizionato = torch.cat([z, one_hot], dim=1)
        return self.net(z_condizionato)

    @torch.no_grad()
    def sample(self, labels: torch.Tensor, device: torch.device | str) -> torch.Tensor:
        """Genera un'immagine per ciascuna etichetta in `labels`."""
        was_training = self.training
        self.eval()
        n = labels.size(0)
        z = torch.randn(n, self.latent_dim, 1, 1, device=device)
        images = self(z, labels.to(device))
        if was_training:
            self.train()
        return images


class ConditionalDiscriminator(nn.Module):
    """Discriminatore con testa ausiliaria di classificazione (stile AC-GAN-style).

    A differenza della `Discriminator` della CAN — dove la testa di stile classifica
    solo le immagini **reali** e il generatore viene spinto verso l'ambiguita' — qui
    la testa classifica **sia reali sia generate**, e il generatore viene premiato
    quando l'immagine prodotta e' classificata correttamente come lo stile richiesto.
    E' l'esatto opposto della logica di ADR-0003, per questo vive in una classe
    separata invece di riusare `style_head` di `networks.Discriminator`.
    """

    def __init__(
        self,
        num_styles: int,
        features: int = 64,
        channels: int = 3,
        image_size: int = 64,
    ) -> None:
        super().__init__()
        if num_styles <= 0:
            raise ValueError("num_styles deve essere > 0.")
        self.num_styles = num_styles
        self.image_size = image_size
        stadi = _stadi(image_size)

        def block(in_c: int, out_c: int, batchnorm: bool = True) -> nn.Sequential:
            layers: list[nn.Module] = [nn.Conv2d(in_c, out_c, 4, 2, 1, bias=False)]
            if batchnorm:
                layers.append(nn.BatchNorm2d(out_c))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return nn.Sequential(*layers)

        larghezze = [features * 2**i for i in range(stadi)]
        strati: list[nn.Module] = [block(channels, larghezze[0], batchnorm=False)]
        for i in range(stadi - 1):
            strati.append(block(larghezze[i], larghezze[i + 1]))
        self.backbone = nn.Sequential(*strati)
        self.features_finali = larghezze[-1]

        self.adv_head = nn.Conv2d(self.features_finali, 1, 4, 1, 0, bias=False)
        self.class_head = nn.Sequential(
            nn.Conv2d(self.features_finali, self.features_finali, 3, 1, 1, bias=False),
            nn.BatchNorm2d(self.features_finali),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Flatten(),
            nn.Linear(self.features_finali * 4 * 4, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, num_styles),
        )
        self.apply(_init_weights)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        adv_logit = self.adv_head(h).view(x.size(0))
        style_logits = self.class_head(h)
        return adv_logit, style_logits


def build_conditional_models(cfg) -> tuple[ConditionalGenerator, ConditionalDiscriminator]:
    """Costruisce la coppia condizionata dalla configurazione Hydra.

    Unico punto di costruzione, sulla stessa logica di `networks.build_models`: un
    parametro dimenticato in un punto e ripetuto a mano altrove e' la classe di
    errore gia' incontrata due volte nell'impianto principale (D-018).
    """
    image_size = int(cfg.data.image_size)
    num_styles = cfg.model.get("num_styles")
    if not num_styles:
        raise ValueError(
            "model.num_styles non impostato: va ricavato dai dati prima di costruire "
            "il modello (vedi cmd_train_conditional in cli.py)."
        )
    generator = ConditionalGenerator(
        num_styles=int(num_styles),
        latent_dim=int(cfg.model.latent_dim),
        features=int(cfg.model.generator_features),
        channels=int(cfg.model.channels),
        image_size=image_size,
    )
    discriminator = ConditionalDiscriminator(
        num_styles=int(num_styles),
        features=int(cfg.model.discriminator_features),
        channels=int(cfg.model.channels),
        image_size=image_size,
    )
    return generator, discriminator
