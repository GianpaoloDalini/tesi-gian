"""Inventario del dataset: quante opere ci sono per ogni stile.

    python -m tesi_gan.data.inventory

Serve a scegliere gli stili dell'esperimento **sui numeri veri** invece che a
occhio. La classe meno popolata determina la dimensione del sottoinsieme
bilanciato, quindi determina di fatto quanti dati vedra' il modello: sceglierla
senza conoscerne la numerosita' significa scoprire troppo tardi di avere un
dataset da duemila immagini.

## Cosa scarica

**Solo due file CSV di indice, circa 5 MB in tutto. Nessuna immagine.** I CSV
elencano le coppie `(percorso, indice di stile)` del dataset WikiArt \"refined\"
pubblicato da Tan et al. insieme ad ArtGAN, e sono versionati nel loro repository
GitHub.

Poiche' non si scarica nessuna opera, questo comando **non e' soggetto al blocco di
V-007**: contare non e' riprodurre. Il blocco resta su
`python -m tesi_gan.data.download`, che le immagini le tocca davvero.

## Avvertenza sulla corrispondenza

Gli indici di stile di ArtGAN coincidono con quelli del dataset `huggan/wikiart`
su Hugging Face (verificato sui nomi delle 27 classi). I **conteggi**, pero',
valgono per la versione \"refined\" di ArtGAN: se poi i dati verranno presi da
Hugging Face, le numerosita' possono differire, perche' le due versioni sono state
filtrate in modo diverso. Il numero da riportare in tesi e' quello del dataset che
si e' effettivamente usato, non quello letto qui.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.request
from collections import Counter
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

_BASE = "https://raw.githubusercontent.com/cs-chan/ArtGAN/master/WikiArt%20Dataset/Style"
_FILES = {
    "classi": f"{_BASE}/style_class.txt",
    "train": f"{_BASE}/style_train.csv",
    "val": f"{_BASE}/style_val.csv",
}

# Fonte dei file, da citare nell'appendice sulla riproducibilita'.
_FONTE = (
    "Tan, Chan, Aguirre, Tanaka — Improved ArtGAN for Conditional Synthesis of "
    "Natural Image and Artwork, IEEE TIP 28(1):394-409, 2019. "
    "Indici: github.com/cs-chan/ArtGAN"
)


def _scarica(url: str, destinazione: Path) -> Path:
    """Scarica un file se non e' gia' in cache. La cache sta in data/external/,
    che e' ignorata da git."""
    if destinazione.exists() and destinazione.stat().st_size > 0:
        log.info("gia' in cache: %s", destinazione.name)
        return destinazione
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    log.info("scarico %s", url)
    with urllib.request.urlopen(url, timeout=60) as risposta:  # noqa: S310
        destinazione.write_bytes(risposta.read())
    log.info("scritto %s (%.1f MB)", destinazione.name, destinazione.stat().st_size / 1e6)
    return destinazione


def leggi_classi(testo: str) -> dict[int, str]:
    """Interpreta `style_class.txt`: righe nella forma `<indice> <nome>`."""
    classi: dict[int, str] = {}
    for riga in testo.splitlines():
        riga = riga.strip()
        if not riga:
            continue
        indice, _, nome = riga.partition(" ")
        try:
            classi[int(indice)] = nome.strip()
        except ValueError:
            log.warning("riga non interpretabile in style_class.txt: %r", riga)
    return classi


def conta_stili(testo: str) -> Counter:
    """Conta le occorrenze di ciascun indice di stile in un CSV `percorso,indice`.

    Tollera righe vuote, spazi e un'eventuale riga di intestazione.
    """
    conteggi: Counter = Counter()
    for riga in testo.splitlines():
        riga = riga.strip()
        if not riga or "," not in riga:
            continue
        _, _, indice = riga.rpartition(",")
        try:
            conteggi[int(indice.strip())] += 1
        except ValueError:
            continue  # intestazione o riga malformata
    return conteggi


def tabella_markdown(
    classi: dict[int, str],
    train: Counter,
    val: Counter,
) -> str:
    """Tabella ordinata per numerosita' decrescente, pronta da incollare nei docs."""
    righe = [
        "| Indice | Stile | Train | Val | Totale |",
        "|---:|---|---:|---:|---:|",
    ]
    totali = {i: train.get(i, 0) + val.get(i, 0) for i in classi}
    for indice in sorted(classi, key=lambda i: totali[i], reverse=True):
        righe.append(
            f"| {indice} | {classi[indice]} | {train.get(indice, 0)} | "
            f"{val.get(indice, 0)} | {totali[indice]} |"
        )
    righe.append(f"| | **Totale** | {sum(train.values())} | {sum(val.values())} "
                 f"| {sum(totali.values())} |")
    return "\n".join(righe)


def simula_bilanciamento(
    classi: dict[int, str],
    totali: dict[int, int],
    selezione: list[str],
) -> str:
    """Dato un insieme di stili, dice quanto grande verrebbe il dataset bilanciato.

    E' il calcolo che conta davvero per la scelta: il tetto lo fissa la classe piu'
    piccola, e il totale e' `tetto x numero di classi`.
    """
    per_nome = {nome: indice for indice, nome in classi.items()}
    mancanti = [s for s in selezione if s not in per_nome]
    if mancanti:
        return f"Stili non riconosciuti: {mancanti}. Nomi validi: {sorted(per_nome)}"

    scelti = {s: totali[per_nome[s]] for s in selezione}
    tetto = min(scelti.values())
    limitante = min(scelti, key=lambda s: scelti[s])

    righe = [f"Selezione di {len(selezione)} stili:"]
    for nome, n in sorted(scelti.items(), key=lambda kv: kv[1], reverse=True):
        marcatore = "  <-- classe limitante" if nome == limitante else ""
        righe.append(f"  {nome:<32} {n:>6}{marcatore}")
    righe.append("")
    righe.append(f"  Tetto per classe:   {tetto}")
    righe.append(f"  Dataset bilanciato: {tetto * len(selezione)} immagini")
    return "\n".join(righe)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tesi-gan-inventory", description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("data/external/artgan_index"),
                        help="Cartella in cui tenere i CSV scaricati (ignorata da git)")
    parser.add_argument("--json", type=Path, default=None,
                        help="Scrive i conteggi anche in un file JSON")
    parser.add_argument("--stili", nargs="*", default=None,
                        help="Simula il bilanciamento su questi stili, es. "
                             "--stili Impressionism Baroque Ukiyo_e Northern_Renaissance")
    args = parser.parse_args(argv)

    try:
        percorsi = {
            nome: _scarica(url, args.cache / Path(url).name.replace("%20", "_"))
            for nome, url in _FILES.items()
        }
    except OSError as exc:
        log.error(
            "Download fallito (%s). I tre file si possono anche scaricare a mano da\n"
            "  %s\ne mettere in %s",
            exc, _BASE, args.cache,
        )
        return 1

    classi = leggi_classi(percorsi["classi"].read_text(encoding="utf-8"))
    train = conta_stili(percorsi["train"].read_text(encoding="utf-8"))
    val = conta_stili(percorsi["val"].read_text(encoding="utf-8"))

    if not classi:
        log.error("Nessuna classe letta: il file degli indici e' vuoto o malformato.")
        return 1

    totali = {i: train.get(i, 0) + val.get(i, 0) for i in classi}

    print()
    print(tabella_markdown(classi, train, val))
    print()
    print(f"Fonte: {_FONTE}")

    if args.stili:
        print()
        print(simula_bilanciamento(classi, totali, args.stili))

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(
                {
                    "fonte": _FONTE,
                    "url": _BASE,
                    "stili": {
                        classi[i]: {
                            "indice": i,
                            "train": train.get(i, 0),
                            "val": val.get(i, 0),
                            "totale": totali[i],
                        }
                        for i in sorted(classi)
                    },
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        log.info("conteggi scritti in %s", args.json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
