"""Test dell'inventario del dataset.

Non toccano la rete: verificano il parsing e il calcolo del bilanciamento su dati
finti. Il download vero lo si prova lanciando il comando.
"""

from tesi_gan.data.inventory import (
    conta_stili,
    leggi_classi,
    simula_bilanciamento,
    tabella_markdown,
)

CLASSI_FINTE = "0 Baroque\n1 Impressionism\n2 Ukiyo_e\n"

CSV_FINTO = (
    "Baroque/a.jpg,0\n"
    "Baroque/b.jpg,0\n"
    "Impressionism/c.jpg,1\n"
    "Impressionism/d.jpg,1\n"
    "Impressionism/e.jpg,1\n"
    "Ukiyo_e/f.jpg,2\n"
)


def test_lettura_classi():
    classi = leggi_classi(CLASSI_FINTE)
    assert classi == {0: "Baroque", 1: "Impressionism", 2: "Ukiyo_e"}


def test_lettura_classi_ignora_righe_vuote():
    assert leggi_classi("\n0 Baroque\n\n") == {0: "Baroque"}


def test_conteggio():
    conteggi = conta_stili(CSV_FINTO)
    assert conteggi[0] == 2
    assert conteggi[1] == 3
    assert conteggi[2] == 1


def test_conteggio_tollera_intestazione_e_righe_sporche():
    sporco = "path,label\nBaroque/a.jpg,0\n\n   \nnonvalida\n"
    conteggi = conta_stili(sporco)
    assert conteggi[0] == 1
    assert sum(conteggi.values()) == 1


def test_conteggio_usa_ultimo_campo():
    """I percorsi possono contenere virgole: conta l'ultimo campo, non il secondo."""
    assert conta_stili("Baroque/titolo, con virgola.jpg,0\n")[0] == 1


def test_bilanciamento_usa_la_classe_piu_piccola():
    classi = leggi_classi(CLASSI_FINTE)
    totali = dict(conta_stili(CSV_FINTO))
    esito = simula_bilanciamento(classi, totali, ["Baroque", "Impressionism", "Ukiyo_e"])
    assert "Tetto per classe:   1" in esito
    assert "Dataset bilanciato: 3" in esito
    assert "classe limitante" in esito


def test_bilanciamento_segnala_stili_inesistenti():
    classi = leggi_classi(CLASSI_FINTE)
    esito = simula_bilanciamento(classi, {0: 2, 1: 3, 2: 1}, ["Cubism"])
    assert "non riconosciuti" in esito


def test_tabella_ordinata_per_totale():
    classi = leggi_classi(CLASSI_FINTE)
    conteggi = conta_stili(CSV_FINTO)
    tabella = tabella_markdown(classi, conteggi, conteggi)
    # La riga di separazione inizia con "|-", quindi resta fuori: righe[0] e'
    # l'intestazione e righe[1] e' il primo dato, cioe' lo stile piu' popolato.
    righe = [r for r in tabella.splitlines() if r.startswith("| ")]
    assert "Impressionism" in righe[1]
    assert "Baroque" in righe[2]
    assert "Ukiyo_e" in righe[3]
