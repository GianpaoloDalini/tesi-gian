"""Test minimi: verificano che il package sia importabile e coerente.

Servono soprattutto sui servizi di training remoto, dove un errore di import
si scopre altrimenti dopo minuti di setup.
"""

import tesi_gan
from tesi_gan.utils import provenance, seed


def test_versione_dichiarata():
    assert tesi_gan.__version__


def test_seed_deterministico():
    import numpy as np

    seed.set_seed(42)
    a = np.random.rand(5)
    seed.set_seed(42)
    b = np.random.rand(5)
    assert (a == b).all()


def test_provenance_non_esplode_fuori_da_git():
    p = provenance.collect()
    assert isinstance(p.as_dict(), dict)
