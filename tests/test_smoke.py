"""Test minimi: verificano che il package sia importabile e coerente.

Servono soprattutto sui servizi di training remoto, dove un errore di import
si scopre altrimenti dopo minuti di setup.
"""

import tesi_gan
from tesi_gan.utils import provenance, seed


def test_progress_disattivata_restituisce_iterabile_intatto():
    """Una barra mancante o disattivata non deve alterare i dati che avvolge."""
    from tesi_gan.utils.progress import progress

    assert list(progress(range(5), "x", enabled=False)) == [0, 1, 2, 3, 4]
    assert sum(progress(range(100), "x", enabled=False)) == 4950


def test_progress_non_consuma_l_iterabile_due_volte():
    """Con la barra attiva l'iterazione deve restare completa: una barra che
    consumasse elementi farebbe saltare batch di training senza errori visibili."""
    from tesi_gan.utils.progress import progress

    assert list(progress(range(7), "x", enabled=True)) == list(range(7))


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
