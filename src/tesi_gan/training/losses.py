"""Funzioni di perdita: **l'unica variabile indipendente dell'esperimento**.

Tutto il resto — generatore, backbone del discriminatore, ottimizzatori, seed,
epoche, dataset — e' identico fra le due condizioni. Se i risultati differiscono,
differiscono per cio' che sta in questo file (ADR-0003).

## DCGAN (condizione di controllo)

Gioco minimax standard (Goodfellow et al., 2014) nella variante non saturante:

    L_D = BCE(D(x), 1) + BCE(D(G(z)), 0)
    L_G = BCE(D(G(z)), 1)

## CAN (condizione sperimentale)

Due termini aggiuntivi (Elgammal et al., 2017):

1. **Al discriminatore**, classificazione dello stile sulle sole immagini **reali**:
   il discriminatore impara a riconoscere gli stili art-storici. Sulle immagini
   generate non c'e' etichetta vera, quindi il termine non si applica.

       L_D = BCE(D_r(x), 1) + BCE(D_r(G(z)), 0) + CE(D_c(x), stile_vero)

2. **Al generatore**, ambiguita' stilistica: il generatore e' spinto a produrre
   immagini che il discriminatore **non riesce ad attribuire** a nessuno stile,
   cioe' la cui posterior di stile e' il piu' possibile vicina all'uniforme.

       L_G = BCE(D_r(G(z)), 1) + lambda * A(D_c(G(z)))

   dove A e' la penalita' di ambiguita' definita sotto.

## Avvertenza sulla formulazione di A

Elgammal et al. formulano l'ambiguita' come entropia incrociata rispetto alla
distribuzione uniforme. Sono implementate due varianti perche' **la forma esatta va
verificata sul paper originale prima di dichiararla in tesi** (CLAUDE.md §2.1):

- `cross_entropy_uniform` (default): CE(p, uniforme) = -(1/K) * sum_k log p_k.
  Minimizzarla equivale a minimizzare KL(uniforme || p), che spinge p verso
  l'uniforme. E' la lettura piu' diretta del testo del paper.
- `negative_entropy`: -H(p). Minimizzarla massimizza l'entropia di p, quindi la
  spinge anch'essa verso l'uniforme, ma penalizza diversamente le posterior
  quasi-uniformi.

Le due non sono equivalenti: KL(u||p) esplode se una classe ha probabilita' quasi
nulla, mentre -H(p) e' limitata. La scelta va giustificata in tesi, non subita.
Se emergesse una discrepanza fra le due, e' materiale per la discussione dei limiti.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F
from torch import nn

_bce = nn.BCEWithLogitsLoss()


# --------------------------------------------------------------------------- #
#  Penalita' di ambiguita' stilistica
# --------------------------------------------------------------------------- #

def cross_entropy_uniform(style_logits: torch.Tensor) -> torch.Tensor:
    """Entropia incrociata fra la posterior di stile e la distribuzione uniforme.

    Restituisce -(1/K) * sum_k log softmax(logits)_k, mediato sul batch.
    Vale log(K) quando la posterior e' uniforme, e cresce man mano che si concentra
    su una classe.
    """
    log_p = F.log_softmax(style_logits, dim=1)
    return -log_p.mean(dim=1).mean()


def negative_entropy(style_logits: torch.Tensor) -> torch.Tensor:
    """Opposto dell'entropia della posterior di stile.

    Minimizzarla massimizza l'entropia. Vale -log(K) sull'uniforme e 0 su una
    posterior degenere.
    """
    log_p = F.log_softmax(style_logits, dim=1)
    p = log_p.exp()
    return (p * log_p).sum(dim=1).mean()


_AMBIGUITY_FNS = {
    "cross_entropy_uniform": cross_entropy_uniform,
    "negative_entropy": negative_entropy,
}


def get_ambiguity_fn(name: str):
    if name not in _AMBIGUITY_FNS:
        raise ValueError(
            f"Penalita' di ambiguita' sconosciuta: {name!r}. "
            f"Disponibili: {sorted(_AMBIGUITY_FNS)}"
        )
    return _AMBIGUITY_FNS[name]


# --------------------------------------------------------------------------- #
#  Loss complete
# --------------------------------------------------------------------------- #

@dataclass
class LossTerms:
    """Scomposizione della loss, cosi' che ogni termine sia loggabile separatamente.

    Non e' un vezzo: se la CAN diverge, sapere *quale* termine e' esploso e'
    la differenza fra una diagnosi e un'ipotesi.
    """

    total: torch.Tensor
    adversarial: torch.Tensor
    style_classification: torch.Tensor | None = None
    style_ambiguity: torch.Tensor | None = None

    def as_log_dict(self, prefix: str) -> dict[str, float]:
        out = {
            f"{prefix}/loss": float(self.total.detach()),
            f"{prefix}/adversarial": float(self.adversarial.detach()),
        }
        if self.style_classification is not None:
            out[f"{prefix}/style_classification"] = float(self.style_classification.detach())
        if self.style_ambiguity is not None:
            out[f"{prefix}/style_ambiguity"] = float(self.style_ambiguity.detach())
        return out


def discriminator_loss(
    real_adv_logits: torch.Tensor,
    fake_adv_logits: torch.Tensor,
    real_style_logits: torch.Tensor | None = None,
    style_targets: torch.Tensor | None = None,
    label_smoothing: float = 0.0,
) -> LossTerms:
    """Loss del discriminatore, comune alle due condizioni.

    Il termine di classificazione dello stile e' incluso solo se il discriminatore
    ha la testa di stile (CAN) e sono disponibili le etichette vere. **Si applica
    alle sole immagini reali**: le generate non hanno uno stile di riferimento.

    `label_smoothing` sostituisce il target 1.0 delle immagini reali con
    `1 - label_smoothing`. E' una mitigazione standard contro l'eccesso di
    sicurezza del discriminatore; se attivata va dichiarata in appendice.
    """
    real_target = torch.full_like(real_adv_logits, 1.0 - label_smoothing)
    fake_target = torch.zeros_like(fake_adv_logits)

    adversarial = _bce(real_adv_logits, real_target) + _bce(fake_adv_logits, fake_target)
    total = adversarial
    style_ce: torch.Tensor | None = None

    if real_style_logits is not None and style_targets is not None:
        style_ce = F.cross_entropy(real_style_logits, style_targets)
        total = total + style_ce

    return LossTerms(total=total, adversarial=adversarial, style_classification=style_ce)


def generator_loss(
    fake_adv_logits: torch.Tensor,
    fake_style_logits: torch.Tensor | None = None,
    ambiguity_weight: float = 1.0,
    ambiguity_fn: str = "cross_entropy_uniform",
) -> LossTerms:
    """Loss del generatore, comune alle due condizioni.

    Variante **non saturante**: si massimizza log D(G(z)) invece di minimizzare
    log(1 - D(G(z))). Con la seconda forma il gradiente svanisce proprio quando il
    generatore va male, cioe' all'inizio dell'addestramento.

    Il termine di ambiguita' compare solo nella CAN. Con `ambiguity_weight=0` la
    CAN degenera esattamente nella DCGAN: e' un'ablazione utile per verificare che
    l'implementazione condivisa sia davvero equivalente nelle due condizioni.
    """
    target = torch.ones_like(fake_adv_logits)
    adversarial = _bce(fake_adv_logits, target)
    total = adversarial
    ambiguity: torch.Tensor | None = None

    if fake_style_logits is not None and ambiguity_weight != 0.0:
        ambiguity = get_ambiguity_fn(ambiguity_fn)(fake_style_logits)
        total = total + ambiguity_weight * ambiguity

    return LossTerms(total=total, adversarial=adversarial, style_ambiguity=ambiguity)
