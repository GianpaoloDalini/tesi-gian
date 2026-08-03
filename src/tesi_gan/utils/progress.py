"""Barre di avanzamento per le operazioni lunghe.

Servono a distinguere «sta lavorando» da «si e' piantato», che a occhio nudo su un
terminale fermo sono la stessa cosa. Con sei run da un centinaio di epoche su una
macchina a noleggio, sapere se il training procede non e' un vezzo estetico.

**Si disattivano da sole quando l'output non e' un terminale.** Se si lancia il
training con `nohup ... > log.txt`, tqdm riscriverebbe la stessa riga migliaia di
volte producendo un file di log illeggibile. In quel caso restano solo le righe di
log per epoca, che sono esattamente cio' che serve in un file.
"""

from __future__ import annotations

import sys
from typing import Iterable, TypeVar

T = TypeVar("T")


def _tty() -> bool:
    """Vero se stderr e' un terminale interattivo."""
    try:
        return sys.stderr.isatty()
    except Exception:  # noqa: BLE001
        return False


def progress(
    iterable: Iterable[T],
    description: str = "",
    total: int | None = None,
    enabled: bool | None = None,
    leave: bool = False,
) -> Iterable[T]:
    """Avvolge un iterabile in una barra di avanzamento, se possibile.

    `enabled=None` (default) attiva la barra solo su terminale interattivo.
    `enabled=True` la forza, `enabled=False` la disattiva.

    Se `tqdm` non e' installato l'iterabile viene restituito intatto: una barra
    mancante non deve mai impedire a un addestramento di partire.
    """
    if enabled is None:
        enabled = _tty()
    if not enabled:
        return iterable

    try:
        from tqdm.auto import tqdm
    except ImportError:
        return iterable

    return tqdm(
        iterable,
        desc=description,
        total=total,
        leave=leave,
        dynamic_ncols=True,
        # Le barre annidate (epoca dentro training) non devono accumularsi a schermo.
        mininterval=0.5,
    )
