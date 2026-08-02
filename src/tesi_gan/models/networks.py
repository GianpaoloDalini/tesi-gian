"""Architetture di DCGAN e CAN.

**Punto centrale dell'impianto sperimentale (ADR-0003).** Le due condizioni
sperimentali condividono lo stesso identico codice: il generatore e' letteralmente
la stessa classe, e il discriminatore differisce per un solo parametro booleano
(`style_head`). Non esistono due implementazioni separate.

La ragione non e' l'eleganza del codice ma la validita' del confronto: se DCGAN e CAN
fossero implementazioni distinte, ogni differenza osservata nei risultati sarebbe
confusa con differenze di implementazione, e l'esperimento non dimostrerebbe nulla
sul meccanismo di ambiguita' stilistica.

Architettura di riferimento: DCGAN (Radford et al., 2016) a risoluzione 64x64.
Estensione con testa di stile: CAN (Elgammal et al., 2017).
Il discriminatore emette **logit**, non probabilita': le loss usano le varianti
`*WithLogits`, numericamente stabili.
"""

from __future__ import annotations

import torch
from torch import nn


def _init_weights(module: nn.Module) -> None:
    """Inizializzazione prescritta da Radford et al. (2016), §4.

    Normale a media 0 e deviazione standard 0.02 per conv e batchnorm. Non e' un
    dettaglio trascurabile: con l'inizializzazione di default di PyTorch le DCGAN
    a 64x64 collassano molto piu' spesso.
    """
    name = module.__class__.__name__
    if "Conv" in name:
        nn.init.normal_(module.weight.data, 0.0, 0.02)
    elif "BatchNorm" in name:
        nn.init.normal_(module.weight.data, 1.0, 0.02)
        nn.init.constant_(module.bias.data, 0)


class Generator(nn.Module):
    """Generatore DCGAN 64x64. **Identico nelle due condizioni sperimentali.**

    Mappa un vettore latente z ~ N(0, I) di dimensione `latent_dim` in un'immagine
    RGB 64x64 con valori in [-1, 1] (tanh in uscita, coerente con la normalizzazione
    del dataloader).

    Progressione spaziale: 1x1 -> 4x4 -> 8x8 -> 16x16 -> 32x32 -> 64x64.
    """

    def __init__(
        self,
        latent_dim: int = 100,
        features: int = 64,
        channels: int = 3,
    ) -> None:
        super().__init__()
        self.latent_dim = latent_dim

        def block(in_c: int, out_c: int, stride: int, padding: int) -> nn.Sequential:
            return nn.Sequential(
                nn.ConvTranspose2d(in_c, out_c, 4, stride, padding, bias=False),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
            )

        self.net = nn.Sequential(
            block(latent_dim, features * 8, 1, 0),      # -> 4x4
            block(features * 8, features * 4, 2, 1),    # -> 8x8
            block(features * 4, features * 2, 2, 1),    # -> 16x16
            block(features * 2, features, 2, 1),        # -> 32x32
            nn.ConvTranspose2d(features, channels, 4, 2, 1, bias=False),  # -> 64x64
            nn.Tanh(),
        )
        self.apply(_init_weights)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if z.dim() == 2:
            z = z.view(z.size(0), z.size(1), 1, 1)
        return self.net(z)

    @torch.no_grad()
    def sample(self, n: int, device: torch.device | str) -> torch.Tensor:
        """Genera `n` immagini. Usato per i campioni loggati e per le metriche."""
        was_training = self.training
        self.eval()
        z = torch.randn(n, self.latent_dim, 1, 1, device=device)
        images = self(z)
        if was_training:
            self.train()
        return images


class Discriminator(nn.Module):
    """Discriminatore a backbone condivisa, con testa di stile opzionale.

    - `style_head=False` -> discriminatore DCGAN standard (condizione di controllo).
    - `style_head=True`  -> discriminatore CAN (condizione sperimentale): stessa
      backbone convoluzionale, piu' una seconda testa che classifica lo stile in
      `num_styles` classi.

    La backbone e' condivisa fra le due teste: e' cio' che rende possibile il
    meccanismo della CAN, perche' il segnale di ambiguita' stilistica si propaga al
    generatore attraverso le stesse feature che decidono reale/falso.

    Restituisce sempre una coppia `(logit_reale_falso, logit_stile)`, con il secondo
    elemento a `None` quando la testa di stile e' assente. Firma unica per le due
    condizioni: il training loop non deve ramificare sull'architettura.
    """

    def __init__(
        self,
        features: int = 64,
        channels: int = 3,
        style_head: bool = False,
        num_styles: int | None = None,
    ) -> None:
        super().__init__()

        if style_head and not num_styles:
            raise ValueError(
                "style_head=True richiede num_styles > 0. Il numero di classi deve "
                "coincidere con gli stili effettivamente presenti nel dataset: "
                "vedi ADR-0004."
            )

        self.style_head_enabled = style_head
        self.num_styles = num_styles if style_head else None

        def block(in_c: int, out_c: int, batchnorm: bool = True) -> nn.Sequential:
            layers: list[nn.Module] = [nn.Conv2d(in_c, out_c, 4, 2, 1, bias=False)]
            if batchnorm:
                layers.append(nn.BatchNorm2d(out_c))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return nn.Sequential(*layers)

        # Backbone condivisa: 64x64 -> 4x4. Nessuna batchnorm sul primo blocco,
        # come prescritto da Radford et al. (2016).
        self.backbone = nn.Sequential(
            block(channels, features, batchnorm=False),  # -> 32x32
            block(features, features * 2),               # -> 16x16
            block(features * 2, features * 4),           # -> 8x8
            block(features * 4, features * 8),           # -> 4x4
        )

        # Testa reale/falso: presente in entrambe le condizioni.
        self.adv_head = nn.Conv2d(features * 8, 1, 4, 1, 0, bias=False)

        # ATTENZIONE ALL'ORDINE. L'inizializzazione va applicata a backbone e testa
        # avversaria **prima** di costruire la testa di stile, non con un solo
        # `self.apply()` alla fine.
        #
        # Motivo: costruire la testa di stile consuma numeri dal generatore
        # pseudocasuale. Con un `apply()` finale, la backbone della CAN verrebbe
        # inizializzata a partire da uno stato del RNG diverso da quello della
        # DCGAN, e a parita' di seed i due modelli **partirebbero da pesi diversi**.
        # L'inizializzazione diventerebbe una seconda variabile non controllata, e
        # l'esperimento di ADR-0003 non avrebbe piu' una sola variabile indipendente.
        #
        # Con questo ordine, a parita' di seed backbone e testa avversaria sono
        # identiche nelle due condizioni. Verificato da
        # tests/test_impianto.py::test_backbone_del_discriminatore_identica.
        self.backbone.apply(_init_weights)
        self.adv_head.apply(_init_weights)

        # Testa di stile: presente solo nella CAN.
        # Due layer convoluzionali aggiuntivi prima della classificazione, cosi' che
        # la rappresentazione stilistica non sia forzata a coincidere con quella
        # usata per reale/falso.
        if style_head:
            self.style_head = nn.Sequential(
                nn.Conv2d(features * 8, features * 8, 3, 1, 1, bias=False),
                nn.BatchNorm2d(features * 8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Flatten(),
                nn.Linear(features * 8 * 4 * 4, 512),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Linear(512, num_styles),
            )
            self.style_head.apply(_init_weights)
        else:
            self.style_head = None

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor | None]:
        h = self.backbone(x)
        adv_logit = self.adv_head(h).view(x.size(0))
        style_logits = self.style_head(h) if self.style_head is not None else None
        return adv_logit, style_logits


def build_models(cfg) -> tuple[Generator, Discriminator]:
    """Costruisce la coppia (generatore, discriminatore) dalla configurazione Hydra.

    Unico punto in cui la scelta fra DCGAN e CAN si traduce in architettura. La
    distinzione passa da `cfg.model.name`, non da import diversi.
    """
    is_can = str(cfg.model.name).lower() == "can"

    generator = Generator(
        latent_dim=cfg.model.latent_dim,
        features=cfg.model.generator_features,
        channels=cfg.model.channels,
    )
    discriminator = Discriminator(
        features=cfg.model.discriminator_features,
        channels=cfg.model.channels,
        style_head=is_can,
        num_styles=cfg.model.get("num_styles") if is_can else None,
    )
    return generator, discriminator
