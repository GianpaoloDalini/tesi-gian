"""Test della preparazione del sottoinsieme bilanciato.

Verificano la proprieta' che regge tutto l'esperimento: **le classi devono uscire
bilanciate**. Se non lo sono, la testa di stile impara la distribuzione a priori
invece dello stile e l'entropia della posterior perde significato (ADR-0004).
"""

import pytest

from tesi_gan.data.download import prepare


def _crea_dataset_finto(radice, composizione: dict[str, int]) -> None:
    """Crea cartelle di stile con il numero di immagini indicato (file vuoti)."""
    for stile, n in composizione.items():
        cartella = radice / stile
        cartella.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            (cartella / f"{i:04d}.jpg").write_bytes(b"")


def _crea_dataset_con_immagini(radice, composizione: dict[str, int], size: int = 256):
    """Come sopra, ma con JPEG veri: serve ai test di ridimensionamento."""
    Image = pytest.importorskip("PIL.Image")
    for stile, n in composizione.items():
        cartella = radice / stile
        cartella.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            Image.new("RGB", (size, size), color=(i * 10 % 256, 100, 150)).save(
                cartella / f"{i:04d}.jpg"
            )


def test_selezione_esplicita_prende_gli_stili_richiesti(tmp_path):
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_finto(raw, {"ukiyo_e": 20, "baroque": 20, "surrealism": 20})

    manifest = prepare(
        raw=raw, processed=processed, num_styles=0, per_style=10,
        seed=42, min_per_style=1, stili=["ukiyo_e", "baroque"],
    )

    assert set(manifest["stili"]) == {"ukiyo_e", "baroque"}
    assert not (processed / "surrealism").exists()
    assert manifest["selezione"] == "esplicita"


def test_bilanciamento_sul_minimo_effettivo(tmp_path):
    """Se una classe ne ha meno del richiesto, TUTTE scendono al suo livello."""
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_finto(raw, {"ukiyo_e": 7, "baroque": 50, "realism": 50})

    manifest = prepare(
        raw=raw, processed=processed, num_styles=0, per_style=50,
        seed=42, min_per_style=1, stili=["ukiyo_e", "baroque", "realism"],
    )

    copiate = {s: v["copiate"] for s, v in manifest["stili"].items()}
    assert set(copiate.values()) == {7}, f"classi sbilanciate: {copiate}"
    assert manifest["totale_immagini"] == 21


def test_stile_inesistente_fallisce_esplicitamente(tmp_path):
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_finto(raw, {"ukiyo_e": 10})

    with pytest.raises(RuntimeError, match="non presenti"):
        prepare(raw=raw, processed=processed, num_styles=0, per_style=5,
                seed=42, min_per_style=1, stili=["cubism"])


def test_stile_sotto_soglia_fallisce(tmp_path):
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_finto(raw, {"ukiyo_e": 3, "baroque": 100})

    with pytest.raises(RuntimeError, match="sotto la soglia"):
        prepare(raw=raw, processed=processed, num_styles=0, per_style=50,
                seed=42, min_per_style=10, stili=["ukiyo_e", "baroque"])


def test_selezione_per_numerosita_prende_i_piu_popolati(tmp_path):
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_finto(raw, {"a": 30, "b": 20, "c": 10})

    manifest = prepare(
        raw=raw, processed=processed, num_styles=2, per_style=10,
        seed=42, min_per_style=1, stili=None,
    )

    assert set(manifest["stili"]) == {"a", "b"}
    assert manifest["selezione"] == "per numerosita'"


def test_campionamento_riproducibile_a_parita_di_seed(tmp_path):
    raw = tmp_path / "raw"
    _crea_dataset_finto(raw, {"a": 40, "b": 40})

    def nomi(destinazione):
        prepare(raw=raw, processed=destinazione, num_styles=0, per_style=5,
                seed=7, min_per_style=1, stili=["a", "b"])
        return sorted(p.name for p in (destinazione / "a").iterdir())

    assert nomi(tmp_path / "p1") == nomi(tmp_path / "p2")


# --------------------------------------------------------------------------- #
#  Ridimensionamento
# --------------------------------------------------------------------------- #

def test_resize_scrive_alla_risoluzione_richiesta(tmp_path):
    """Le immagini finiscono su disco gia' a 64x64, non a 256x256."""
    Image = pytest.importorskip("PIL.Image")
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 4, "baroque": 4}, size=256)

    prepare(raw=raw, processed=processed, num_styles=0, per_style=4,
            seed=42, min_per_style=1, stili=["ukiyo_e", "baroque"], resize=64)

    for immagine in (processed / "ukiyo_e").glob("*.jpg"):
        with Image.open(immagine) as img:
            assert img.size == (64, 64)


def test_resize_riduce_lo_spazio_occupato(tmp_path):
    """La ragione pratica del flag: `processed` deve pesare molto meno di `raw`."""
    pytest.importorskip("PIL.Image")
    raw = tmp_path / "raw"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 6}, size=256)

    def peso(destinazione, resize):
        prepare(raw=raw, processed=destinazione, num_styles=0, per_style=6,
                seed=42, min_per_style=1, stili=["ukiyo_e"], resize=resize)
        return sum(p.stat().st_size for p in (destinazione / "ukiyo_e").glob("*.jpg"))

    assert peso(tmp_path / "piccolo", 64) < peso(tmp_path / "grande", None)


def test_senza_resize_le_immagini_restano_originali(tmp_path):
    """Il comportamento predefinito non cambia: `resize=None` copia e basta."""
    Image = pytest.importorskip("PIL.Image")
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 3}, size=256)

    manifest = prepare(raw=raw, processed=processed, num_styles=0, per_style=3,
                       seed=42, min_per_style=1, stili=["ukiyo_e"], resize=None)

    assert manifest["risoluzione"] == "originale"
    for immagine in (processed / "ukiyo_e").glob("*.jpg"):
        with Image.open(immagine) as img:
            assert img.size == (256, 256)


def test_manifest_registra_la_risoluzione(tmp_path):
    """Un `processed` a 64px e uno a 256px sono indistinguibili a occhio ma
    producono run non confrontabili: la risoluzione va tracciata."""
    pytest.importorskip("PIL.Image")
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 3}, size=256)

    manifest = prepare(raw=raw, processed=processed, num_styles=0, per_style=3,
                       seed=42, min_per_style=1, stili=["ukiyo_e"], resize=64)

    assert manifest["risoluzione"] == 64


def test_immagine_corrotta_viene_sostituita_non_solo_scartata(tmp_path):
    """**Il bilanciamento va difeso anche dai file corrotti.**

    Scartare un'immagine illeggibile senza rimpiazzarla abbasserebbe solo la sua
    classe: 4.999 contro 5.000 non si nota guardando le cartelle, ma rompe la
    proprietà su cui si regge l'interpretabilità dell'entropia di stile.
    """
    pytest.importorskip("PIL.Image")
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 10, "baroque": 10}, size=64)
    (raw / "ukiyo_e" / "corrotta.jpg").write_bytes(b"non sono un jpeg")

    manifest = prepare(raw=raw, processed=processed, num_styles=0, per_style=8,
                       seed=42, min_per_style=1,
                       stili=["ukiyo_e", "baroque"], resize=64)

    # Il punto: entrambe le classi arrivano a 8, la corrotta è stata sostituita.
    assert manifest["stili"]["ukiyo_e"]["copiate"] == 8
    assert manifest["stili"]["baroque"]["copiate"] == 8
    assert len(list((processed / "ukiyo_e").glob("*.jpg"))) == 8


def test_nessun_file_troncato_dopo_uno_scarto(tmp_path):
    """Un'immagine fallita non deve lasciare sul disco un file mezzo scritto, che
    poi il dataloader tenterebbe di aprire."""
    Image = pytest.importorskip("PIL.Image")
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 6}, size=64)
    (raw / "ukiyo_e" / "corrotta.jpg").write_bytes(b"non sono un jpeg")

    prepare(raw=raw, processed=processed, num_styles=0, per_style=6,
            seed=42, min_per_style=1, stili=["ukiyo_e"], resize=64)

    for immagine in (processed / "ukiyo_e").glob("*.jpg"):
        with Image.open(immagine) as img:
            img.verify()  # solleva se il file è troncato


def test_troppi_file_corrotti_interrompono_invece_di_sbilanciare(tmp_path):
    """Se non si riesce a raggiungere la quota, meglio fallire che consegnare in
    silenzio un dataset sbilanciato."""
    pytest.importorskip("PIL.Image")
    raw, processed = tmp_path / "raw", tmp_path / "processed"
    _crea_dataset_con_immagini(raw, {"ukiyo_e": 2}, size=64)
    for i in range(6):
        (raw / "ukiyo_e" / f"rotta{i}.jpg").write_bytes(b"non sono un jpeg")

    with pytest.raises(RuntimeError, match="non sarebbe bilanciato"):
        prepare(raw=raw, processed=processed, num_styles=0, per_style=8,
                seed=42, min_per_style=1, stili=["ukiyo_e"], resize=64)
