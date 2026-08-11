"""Ciclo di addestramento dell'esperimento illustrativo condizionato.

Classe separata da `Trainer` (D-010), non una sua variante. `Trainer` presuppone un
generatore incondizionato e le loss di `losses.py`; qui il generatore prende anche
l'etichetta di stile e le loss sono quelle di `conditional_losses.py`. Tenerli
distinti evita che una modifica pensata per le figure illustrative rischi di
alterare, anche per errore di distrazione, il codice su cui si regge il confronto
comparativo.

Stesse pratiche di robustezza del training principale (D-006): checkpoint atomici,
stato completo per la ripresa, griglia a rumore fisso per seguire l'evoluzione.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import optim
from torch.utils.data import DataLoader

from tesi_gan.models.conditional import ConditionalDiscriminator, ConditionalGenerator
from tesi_gan.training.conditional_losses import (
    conditional_discriminator_loss,
    conditional_generator_loss,
)
from tesi_gan.utils.progress import progress

log = logging.getLogger(__name__)

_LATEST = "latest.pt"
_CAMPIONI_PER_STILE = 6  # colonne della griglia illustrativa: una riga per stile


@dataclass
class ConditionalTrainingState:
    epoch: int = 0
    global_step: int = 0


class ConditionalTrainer:
    def __init__(
        self,
        cfg,
        generator: ConditionalGenerator,
        discriminator: ConditionalDiscriminator,
        dataloader: DataLoader,
        device: torch.device,
        tracker=None,
    ) -> None:
        self.cfg = cfg
        self.device = device
        self.generator = generator.to(device)
        self.discriminator = discriminator.to(device)
        self.dataloader = dataloader
        self.tracker = tracker
        self.state = ConditionalTrainingState()
        self.num_styles = generator.num_styles

        t = cfg.training
        betas = (float(t.beta1), float(t.beta2))
        self.opt_g = optim.Adam(self.generator.parameters(), lr=float(t.lr_generator), betas=betas)
        self.opt_d = optim.Adam(
            self.discriminator.parameters(), lr=float(t.lr_discriminator), betas=betas
        )

        self.classification_weight = float(cfg.model.get("classification_weight", 1.0))
        self.label_smoothing = float(t.get("label_smoothing", 0.0))

        self.checkpoint_dir = Path(cfg.paths.checkpoints)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.samples_dir = Path(cfg.paths.get("samples", "experiments/samples"))
        self.samples_dir.mkdir(parents=True, exist_ok=True)
        self.condition_name = str(cfg.model.name)
        self.seed = int(cfg.get("seed", 0))

        # Rumore fisso e, in piu' rispetto al Trainer non condizionato, etichette
        # fisse: una riga per stile, sempre le stesse colonne di rumore, cosi' la
        # griglia mostra sia l'evoluzione sia se il condizionamento funziona (righe
        # visivamente diverse fra loro).
        n_fissi = self.num_styles * _CAMPIONI_PER_STILE
        self.fixed_noise = torch.randn(n_fissi, self.generator.latent_dim, 1, 1, device=device)
        self.fixed_labels = torch.repeat_interleave(
            torch.arange(self.num_styles, device=device), _CAMPIONI_PER_STILE
        )

    def _step(self, real: torch.Tensor, real_labels: torch.Tensor) -> dict[str, float]:
        batch_size = real.size(0)
        real = real.to(self.device, non_blocking=True)
        real_labels = real_labels.to(self.device, non_blocking=True)

        # Etichette bersaglio per le generate: campionate uniformemente sui K stili,
        # cosi' il generatore vede tutte le classi in ogni batch a prescindere dallo
        # sbilanciamento reale del dataset (qui non c'e', ArtBench e' bilanciato per
        # costruzione, ma l'uniformita' e' comunque quella che serve alla griglia
        # illustrativa: un numero paragonabile di esempi per stile).
        gen_labels = torch.randint(0, self.num_styles, (batch_size,), device=self.device)

        # --- Discriminatore ---------------------------------------------------
        self.opt_d.zero_grad(set_to_none=True)

        real_adv, real_style = self.discriminator(real)

        z = torch.randn(batch_size, self.generator.latent_dim, 1, 1, device=self.device)
        fake = self.generator(z, gen_labels)
        fake_adv, fake_style = self.discriminator(fake.detach())

        d_terms = conditional_discriminator_loss(
            real_adv_logits=real_adv,
            fake_adv_logits=fake_adv,
            real_style_logits=real_style,
            real_style_targets=real_labels,
            fake_style_logits=fake_style,
            fake_style_targets=gen_labels,
            label_smoothing=self.label_smoothing,
        )
        d_terms.total.backward()
        self.opt_d.step()

        # --- Generatore -------------------------------------------------------
        self.opt_g.zero_grad(set_to_none=True)

        fake_adv2, fake_style2 = self.discriminator(fake)
        g_terms = conditional_generator_loss(
            fake_adv_logits=fake_adv2,
            fake_style_logits=fake_style2,
            target_labels=gen_labels,
            classification_weight=self.classification_weight,
        )
        g_terms.total.backward()
        self.opt_g.step()

        metrics = {**d_terms.as_log_dict("D"), **g_terms.as_log_dict("G")}
        metrics["D/prob_real"] = float(torch.sigmoid(real_adv).mean().detach())
        metrics["D/prob_fake"] = float(torch.sigmoid(fake_adv).mean().detach())
        return metrics

    def fit(self, epochs: int) -> None:
        log.info(
            "Avvio training illustrativo condizionato: epoche=%d, stili=%d, device=%s",
            epochs, self.num_styles, self.device,
        )
        checkpoint_every = int(self.cfg.training.checkpoint_every)

        for epoch in range(self.state.epoch, epochs):
            self.generator.train()
            self.discriminator.train()
            running: dict[str, float] = {}
            batches = 0

            barra = progress(
                self.dataloader,
                description=f"Epoca {epoch + 1}/{epochs}",
                total=len(self.dataloader),
                enabled=self.cfg.get("progress"),
            )
            for real, labels in barra:
                metrics = self._step(real, labels)
                self.state.global_step += 1
                batches += 1
                for k, v in metrics.items():
                    running[k] = running.get(k, 0.0) + v
                if self.tracker is not None:
                    self.tracker.log(metrics, step=self.state.global_step)

                if batches % 10 == 0 and hasattr(barra, "set_postfix"):
                    barra.set_postfix(
                        G=f"{metrics['G/loss']:.3f}",
                        D=f"{metrics['D/loss']:.3f}",
                        Dreal=f"{metrics['D/prob_real']:.2f}",
                        Dfake=f"{metrics['D/prob_fake']:.2f}",
                    )

            self.state.epoch = epoch + 1
            averaged = {f"epoch/{k}": v / max(batches, 1) for k, v in running.items()}
            averaged["epoch"] = self.state.epoch
            log.info(
                "Epoca %d/%d — G=%.4f D=%.4f",
                self.state.epoch, epochs,
                averaged.get("epoch/G/loss", float("nan")),
                averaged.get("epoch/D/loss", float("nan")),
            )
            campioni = self.sample_grid()
            if self.tracker is not None:
                self.tracker.log(averaged, step=self.state.global_step)
                self.tracker.log_samples(
                    campioni,
                    step=self.state.global_step,
                    caption=(
                        f"{self.condition_name} · seed {self.seed} · "
                        f"epoca {self.state.epoch} · una riga per stile"
                    ),
                )

            self.save_checkpoint(_LATEST)
            if self.state.epoch % checkpoint_every == 0:
                self.save_checkpoint(f"epoch_{self.state.epoch:04d}.pt")

    @torch.no_grad()
    def sample_grid(self) -> torch.Tensor:
        """Griglia dal rumore ed etichette fissi: una riga per stile.

        Usare `torchvision.utils.make_grid(campioni, nrow=6)` a valle produce
        esattamente quella disposizione, perche' `fixed_labels` e' costruito con
        `repeat_interleave` (sei colonne consecutive per ogni stile).
        """
        self.generator.eval()
        images = self.generator(self.fixed_noise, self.fixed_labels)
        self.generator.train()
        return (images.clamp(-1, 1) + 1.0) / 2.0

    def save_checkpoint(self, filename: str) -> Path:
        path = self.checkpoint_dir / filename
        tmp = path.with_suffix(path.suffix + ".tmp")
        torch.save(
            {
                "generator": self.generator.state_dict(),
                "discriminator": self.discriminator.state_dict(),
                "opt_g": self.opt_g.state_dict(),
                "opt_d": self.opt_d.state_dict(),
                "epoch": self.state.epoch,
                "global_step": self.state.global_step,
                "fixed_noise": self.fixed_noise.cpu(),
                "fixed_labels": self.fixed_labels.cpu(),
                "num_styles": self.num_styles,
                "conditional": True,
            },
            tmp,
        )
        tmp.replace(path)
        return path

    def load_checkpoint(self, path: str | Path) -> None:
        path = Path(path)
        ckpt = torch.load(path, map_location=self.device, weights_only=True)

        if not bool(ckpt.get("conditional", False)):
            raise RuntimeError(
                f"Il checkpoint {path} non e' dell'esperimento condizionato: "
                f"caricarlo qui produrrebbe pesi incompatibili con questa architettura."
            )
        if int(ckpt.get("num_styles", -1)) != self.num_styles:
            raise RuntimeError(
                f"Il checkpoint {path} ha {ckpt.get('num_styles')} stili, la "
                f"configurazione corrente {self.num_styles}: non e' caricabile."
            )

        self.generator.load_state_dict(ckpt["generator"])
        self.discriminator.load_state_dict(ckpt["discriminator"])
        self.opt_g.load_state_dict(ckpt["opt_g"])
        self.opt_d.load_state_dict(ckpt["opt_d"])
        self.state.epoch = int(ckpt["epoch"])
        self.state.global_step = int(ckpt["global_step"])
        self.fixed_noise = ckpt["fixed_noise"].to(self.device)
        self.fixed_labels = ckpt["fixed_labels"].to(self.device)
        log.info("Ripreso da %s all'epoca %d", path, self.state.epoch)

    def maybe_resume(self) -> bool:
        latest = self.checkpoint_dir / _LATEST
        if latest.exists():
            self.load_checkpoint(latest)
            return True
        return False
