"""Controllo della riproducibilita'.

Il seed non basta a rendere un run bit-a-bit riproducibile su GPU: alcune
operazioni cuDNN restano non deterministiche. `set_seed(strict=True)` forza il
determinismo a costo di prestazioni; il residuo va comunque dichiarato in tesi
(vedi appendice sulla riproducibilita').
"""

from __future__ import annotations

import os
import random

import numpy as np
import torch


def set_seed(seed: int, strict: bool = False) -> None:
    """Fissa il seed di tutti i generatori pseudocasuali coinvolti."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    if strict:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    else:
        torch.backends.cudnn.benchmark = True
