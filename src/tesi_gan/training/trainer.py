"""Ciclo di addestramento, unico per DCGAN e CAN.

Non esistono due training loop. La condizione sperimentale cambia solo per la
presenza della testa di stile nel discriminatore e per i termini di loss che ne
conseguono (ADR-0003).

**Ripristino dopo interruzione.** D-006 stabilisce che il training gira su sessioni
cloud effimere. Un checkpoint che salva solo i pesi non basta: alla ripresa
servono anche stato degli ottimizzatori, epoca, passo globale e rumore fisso per i
campioni, altrimenti il run ripreso non e' la continuazione di quello interrotto ma
un run diverso che gli assomiglia. Il salvataggio e' atomico (scrittura su file
temporaneo e rinomina) perche' una sessione che muore durante la `torch.save`
lascerebbe un checkpoint troncato, cioe' nessun checkpoint.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn, optim
from torch.utils.data import DataLoader

from tesi_gan.models import Discriminator, Generator
from tesi_gan.training.losses import discriminator_loss, generator_loss

log = logging.getLogger(__name__)

_LATEST = "latest.pt"


@dataclass
class TrainingState:
    """Stato minimo sufficiente a riprendere un run senza alterarne la traiettoria."""

    epoch: int = 0
    global_step: int = 0


class Trainer:
    def __init__(
        self,
        cfg,
        generator: Generator,
        discriminator: Discriminator,
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
        self.state = TrainingState()

        t = cfg.training
        betas = (float(t.beta1), float(t.beta2))
        self.opt_g = optim.Adam(self.generator.parameters(), lr=float(t.lr_generator), betas=betas)
        self.opt_d = optim.Adam(
            self.discriminator.parameters(), lr=float(t.lr_discriminator), betas=betas
        )

        self.is_can = self.discriminator.style_head_enabled
        self.ambiguity_weight = (
            float(cfg.model.get("style_ambiguity_weight", 1.0)) if self.is_can else 0.0
        )
        self.ambiguity_fn = str(cfg.model.get("ambiguity_fn", "cross_entropy_uniform"))
        self.label_smoothing = float(t.get("label_smoothing", 0.0))

        self.checkpoint_dir = Path(cfg.paths.checkpoints)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Rumore fisso: gli stessi vettori latenti a ogni epoca, cosi' la griglia di
        # campioni mostra l'evoluzione del generatore e non il caso.
        self.fixed_noise = torch.randn(64, self.generator.latent_dim, 1, 1, device=device)

    # ------------------------------------------------------------------ #
    #  Un passo
    # ------------------------------------------------------------------ #

    def _step(self, real: torch.Tensor, styles: torch.Tensor) -> dict[str, float]:
        batch_size = real.size(0)
        real = real.to(self.device, non_blocking=True)
        styles = styles.to(self.device, non_blocking=True)

        # --- Discriminatore ---------------------------------------------------
        self.opt_d.zero_grad(set_to_none=True)

        real_adv, real_style = self.discriminator(real)

        z = torch.randn(batch_size, self.generator.latent_dim, 1, 1, device=self.device)
        fake = self.generator(z)
        # detach: qui non si aggiorna il generatore, e propagare fino a lui
        # sprecherebbe calcolo oltre a essere concettualmente sbagliato.
        fake_adv, _ = self.discriminator(fake.detach())

        d_terms = discriminator_loss(
            real_adv_logits=real_adv,
            fake_adv_logits=fake_adv,
            real_style_logits=real_style if self.is_can else None,
            style_targets=styles if self.is_can else None,
            label_smoothing=self.label_smoothing,
        )
        d_terms.total.backward()
        self.opt_d.step()

        # --- Generatore -------------------------------------------------------
        self.opt_g.zero_grad(set_to_none=True)

        # Seconda passata sul discriminatore, ora aggiornato: usare i logit calcolati
        # sopra sarebbe piu' economico ma li renderebbe relativi a un discriminatore
        # che non esiste piu'.
        fake_adv2, fake_style = self.discriminator(fake)

        g_terms = generator_loss(
            fake_adv_logits=fake_adv2,
            fake_style_logits=fake_style if self.is_can else None,
            ambiguity_weight=self.ambiguity_weight,
            ambiguity_fn=self.ambiguity_fn,
        )
        g_terms.total.backward()
        self.opt_g.step()

        metrics = {**d_terms.as_log_dict("D"), **g_terms.as_log_dict("G")}
        # Diagnostica del collasso: se D(reale) -> 1 e D(falso) -> 0 stabilmente,
        # il discriminatore ha vinto e il generatore non riceve piu' gradiente utile.
        metrics["D/prob_real"] = float(torch.sigmoid(real_adv).mean().detach())
        metrics["D/prob_fake"] = float(torch.sigmoid(fake_adv).mean().detach())
        return metrics

    # ------------------------------------------------------------------ #
    #  Ciclo completo
    # ------------------------------------------------------------------ #

    def fit(self, epochs: int) -> None:
        log.info(
            "Avvio training: condizione=%s, epoche=%d, device=%s",
            "CAN" if self.is_can else "DCGAN",
            epochs,
            self.device,
        )
        checkpoint_every = int(self.cfg.training.checkpoint_every)

        for epoch in range(self.state.epoch, epochs):
            self.generator.train()
            self.discriminator.train()
            running: dict[str, float] = {}
            batches = 0

            for real, styles in self.dataloader:
                metrics = self._step(real, styles)
                self.state.global_step += 1
                batches += 1
                for k, v in metrics.items():
                    running[k] = running.get(k, 0.0) + v
                if self.tracker is not None:
                    self.tracker.log(metrics, step=self.state.global_step)

            self.state.epoch = epoch + 1
            averaged = {f"epoch/{k}": v / max(batches, 1) for k, v in running.items()}
            averaged["epoch"] = self.state.epoch
            log.info(
                "Epoca %d/%d — G=%.4f D=%.4f",
                self.state.epoch,
                epochs,
                averaged.get("epoch/G/loss", float("nan")),
                averaged.get("epoch/D/loss", float("nan")),
            )
            if self.tracker is not None:
                self.tracker.log(averaged, step=self.state.global_step)
                self.tracker.log_samples(self.sample_grid(), step=self.state.global_step)

            # Il checkpoint `latest` si aggiorna a ogni epoca a prescindere dalla
            # cadenza: e' l'unica difesa contro una sessione che muore fra due
            # checkpoint numerati.
            self.save_checkpoint(_LATEST)
            if self.state.epoch % checkpoint_every == 0:
                self.save_checkpoint(f"epoch_{self.state.epoch:04d}.pt")

    @torch.no_grad()
    def sample_grid(self) -> torch.Tensor:
        """Griglia di campioni dal rumore fisso, in [0, 1]."""
        self.generator.eval()
        images = self.generator(self.fixed_noise)
        self.generator.train()
        return (images.clamp(-1, 1) + 1.0) / 2.0

    # ------------------------------------------------------------------ #
    #  Persistenza
    # ------------------------------------------------------------------ #

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
                "is_can": self.is_can,
            },
            tmp,
        )
        tmp.replace(path)  # atomica: o c'e' il checkpoint vecchio, o quello nuovo
        return path

    def load_checkpoint(self, path: str | Path) -> None:
        path = Path(path)
        ckpt = torch.load(path, map_location=self.device)

        if bool(ckpt.get("is_can", False)) != self.is_can:
            raise RuntimeError(
                f"Il checkpoint {path} appartiene alla condizione "
                f"{'CAN' if ckpt['is_can'] else 'DCGAN'}, ma la configurazione "
                f"corrente e' {'CAN' if self.is_can else 'DCGAN'}. Riprendere un run "
                f"con l'altra condizione invaliderebbe il confronto."
            )

        self.generator.load_state_dict(ckpt["generator"])
        self.discriminator.load_state_dict(ckpt["discriminator"])
        self.opt_g.load_state_dict(ckpt["opt_g"])
        self.opt_d.load_state_dict(ckpt["opt_d"])
        self.state.epoch = int(ckpt["epoch"])
        self.state.global_step = int(ckpt["global_step"])
        self.fixed_noise = ckpt["fixed_noise"].to(self.device)
        log.info("Ripreso da %s all'epoca %d", path, self.state.epoch)

    def maybe_resume(self) -> bool:
        """Riprende automaticamente da `latest.pt` se esiste."""
        latest = self.checkpoint_dir / _LATEST
        if latest.exists():
            self.load_checkpoint(latest)
            return True
        return False


def count_parameters(model: nn.Module) -> int:
    """Parametri addestrabili. Va riportato in appendice: la CAN ne ha di piu' del
    DCGAN per via della testa di stile, e la differenza va dichiarata invece che
    lasciata dedurre."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
