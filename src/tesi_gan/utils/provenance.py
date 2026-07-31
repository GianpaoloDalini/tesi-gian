"""Provenienza di un run: lega risultati, codice e ambiente.

Ogni run deve poter essere ricondotto al commit esatto che lo ha prodotto.
Senza questo, i numeri riportati in tesi non sono difendibili.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Provenance:
    commit: str
    dirty: bool
    branch: str
    python: str
    platform: str

    def as_dict(self) -> dict:
        return asdict(self)


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def collect() -> Provenance:
    return Provenance(
        commit=_git("rev-parse", "HEAD"),
        dirty=bool(_git("status", "--porcelain")),
        branch=_git("rev-parse", "--abbrev-ref", "HEAD"),
        python=platform.python_version(),
        platform=platform.platform(),
    )


def assert_clean_tree() -> None:
    """Blocca il training se ci sono modifiche non committate.

    Un run lanciato con working tree sporco non e' riproducibile: il commit
    registrato non corrisponde al codice effettivamente eseguito.
    """
    prov = collect()
    if prov.dirty:
        raise RuntimeError(
            "Working tree sporco: committa le modifiche prima di lanciare un "
            "training, altrimenti il run non sara' riconducibile a un commit. "
            "Per forzare (sconsigliato) usa il flag --allow-dirty."
        )
