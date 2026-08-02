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
