"""Tracciamento degli esperimenti su Weights & Biases (D-004).

Il nome del run include l'hash del commit: e' il primo anello della catena
`commit -> run -> checkpoint -> figura -> numero in tesi` (CLAUDE.md §6).

Il wrapper degrada senza errori quando W&B non e' disponibile o disattivato, cosi'
gli smoke test girano senza rete e senza credenziali. Un run non tracciato pero'
**non e' registrabile in `experiments/registry.md`** e i suoi numeri non vanno in tesi.
"""

from __future__ import annotations

import logging
from typing import Any

import torch

log = logging.getLogger(__name__)


class NullTracker:
    """Tracker inerte: usato negli smoke test e quando `tracking.mode=disabled`."""

    run_id = None
    run_name = "offline"

    def log(self, metrics: dict[str, Any], step: int | None = None) -> None:  # noqa: ARG002
        return

    def log_samples(  # noqa: ARG002
        self, images: torch.Tensor, step: int | None = None, caption: str | None = None
    ) -> None:
        return

    def finish(self) -> None:
        return


class WandbTracker:
    def __init__(self, cfg, provenance) -> None:
        import wandb  # import locale: non deve essere richiesto per gli smoke test

        self._wandb = wandb
        short_commit = provenance.commit[:8] if provenance.commit != "unknown" else "nocommit"
        condition = str(cfg.model.name).lower()
        seed = int(cfg.seed)

        # Il seed fa parte del nome. Senza, i tre run per condizione (D-010) si
        # chiamerebbero tutti allo stesso modo e sarebbero indistinguibili nella
        # dashboard: e' lo stesso errore gia' corretto sui percorsi dei checkpoint.
        self._run = wandb.init(
            project=str(cfg.tracking.project),
            entity=cfg.tracking.get("entity"),
            name=f"{condition}-seed{seed}-{short_commit}",
            config={
                "model": dict(cfg.model),
                "data": dict(cfg.data),
                "training": dict(cfg.training),
                "seed": cfg.seed,
                "provenance": provenance.as_dict(),
            },
            tags=[condition, f"seed{seed}", short_commit],
        )
        self.run_id = self._run.id
        self.run_name = self._run.name
        log.info("Run W&B avviato: %s (id=%s)", self.run_name, self.run_id)

    def log(self, metrics: dict[str, Any], step: int | None = None) -> None:
        self._wandb.log(metrics, step=step)

    def log_samples(
        self, images: torch.Tensor, step: int | None = None, caption: str | None = None
    ) -> None:
        """Logga la griglia con la didascalia che riporta condizione, seed ed epoca.

        Senza didascalia, nella dashboard W&B lo storico dei campioni e' una sequenza
        di griglie indistinguibili e non si sa quale epoca si sta guardando.
        """
        from torchvision.utils import make_grid

        grid = make_grid(images.cpu(), nrow=8, padding=2)
        self._wandb.log(
            {"campioni": self._wandb.Image(grid, caption=caption)}, step=step
        )

    def finish(self) -> None:
        self._run.finish()


def build_tracker(cfg, provenance):
    """Costruisce il tracker, ripiegando su `NullTracker` se W&B non e' utilizzabile."""
    backend = str(cfg.tracking.get("backend", "wandb")).lower()
    if backend in {"none", "disabled", "null"}:
        return NullTracker()
    try:
        return WandbTracker(cfg, provenance)
    except Exception as exc:  # noqa: BLE001
        log.warning(
            "W&B non disponibile (%s). Il run procede NON tracciato: i suoi numeri "
            "non sono citabili in tesi (CLAUDE.md §6).",
            exc,
        )
        return NullTracker()
