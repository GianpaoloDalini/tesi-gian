"""Acquisizione e preparazione del dataset.

    python -m tesi_gan.data.download --help

I dati non stanno nel repository (CLAUDE.md §2.5): si ricreano da qui, e la
provenienza esatta finisce in `data/README.md` e nell'appendice sulla
riproducibilita'.

**Blocco deliberato.** Il download non parte finche' non si dichiara di aver
verificato i termini d'uso della fonte (V-007, ADR-0004). Non e' burocrazia: una
tesi che discute le implicazioni etiche dell'addestramento di modelli generativi su
opere d'arte, e che scarica un dataset artistico senza guardarne la licenza, si
espone al rilievo piu' facile e piu' meritato che la commissione possa muovere.
Il flag `--licenza-verificata` esiste perche' quella verifica la faccia una persona.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _count_by_style(raw: Path) -> Counter:
    """Conta le immagini per cartella di stile."""
    counts: Counter = Counter()
    for style_dir in sorted(p for p in raw.iterdir() if p.is_dir()):
        n = sum(1 for f in style_dir.iterdir() if f.suffix.lower() in _IMAGE_SUFFIXES)
        if n:
            counts[style_dir.name] = n
    return counts


def _resize_and_save(src: Path, dst: Path, size: int) -> None:
    """Ridimensiona un'immagine al lato `size` e la salva.

    Stessa geometria del dataloader (`data/dataset.py::build_transform`): resize del
    lato corto seguito da ritaglio centrale. Se le due divergessero, il modello
    vedrebbe in addestramento inquadrature diverse da quelle preparate qui, e il
    ritaglio diventerebbe una variabile non dichiarata.
    """
    from PIL import Image

    with Image.open(src) as img:
        img = img.convert("RGB")
        larghezza, altezza = img.size
        lato_corto = min(larghezza, altezza)
        nuova = (
            round(larghezza * size / lato_corto),
            round(altezza * size / lato_corto),
        )
        img = img.resize(nuova, Image.BICUBIC)

        sinistra = (img.width - size) // 2
        alto = (img.height - size) // 2
        img = img.crop((sinistra, alto, sinistra + size, alto + size))
        img.save(dst, quality=95)


def prepare(
    raw: Path,
    processed: Path,
    num_styles: int,
    per_style: int,
    seed: int,
    min_per_style: int,
    stili: list[str] | None = None,
    resize: int | None = None,
) -> dict:
    """Costruisce il sottoinsieme bilanciato a partire dai dati grezzi.

    Due modalita' di selezione degli stili:

    - **esplicita** (`stili=[...]`): prende esattamente quelli indicati. E' la
      modalita' corretta con ArtBench (ADR-0004), che e' gia' bilanciato: chiedere
      "i piu' popolati" non avrebbe senso, sono tutti uguali, e la scelta ricadrebbe
      sull'ordine alfabetico invece che su un criterio dichiarato.
    - **per numerosita'** (`num_styles=N`): prende gli N piu' popolati. Serviva per
      WikiArt, che ha una coda lunga.

    **Il bilanciamento non e' cosmetico.** Con classi sbilanciate la testa di stile
    del discriminatore impara la distribuzione a priori invece dello stile, e
    l'entropia della posterior — cioe' la metrica su cui si regge il confronto —
    diventa ininterpretabile. Il campionamento e' seedato: due preparazioni con lo
    stesso seed producono lo stesso sottoinsieme.

    `resize` scrive le immagini gia' alla risoluzione di addestramento. ArtBench e' a
    256x256 e l'esperimento gira a 64x64: senza ridimensionamento il dataloader
    decodifica un JPEG a 256px a ogni accesso per scartarne il 94% dei pixel, su sei
    run da un centinaio di epoche ciascuno. Riduce anche `processed` da alcuni GB a
    meno di cento megabyte, il che lo rende trasportabile fra macchine.
    """
    if not raw.exists():
        raise FileNotFoundError(f"Cartella dei dati grezzi inesistente: {raw}")

    counts = _count_by_style(raw)
    if not counts:
        raise RuntimeError(
            f"Nessuna sottocartella con immagini in {raw}. Attesa una cartella per "
            f"stile: {raw}/<stile>/<immagine>.jpg"
        )

    if stili:
        mancanti = [s for s in stili if s not in counts]
        if mancanti:
            raise RuntimeError(
                f"Stili richiesti ma non presenti in {raw}: {mancanti}. "
                f"Disponibili: {sorted(counts)}"
            )
        sotto_soglia = [s for s in stili if counts[s] < min_per_style]
        if sotto_soglia:
            raise RuntimeError(
                f"Stili sotto la soglia di {min_per_style} immagini: "
                f"{ {s: counts[s] for s in sotto_soglia} }. In un sottoinsieme "
                f"bilanciato la classe piu' piccola determina la dimensione di "
                f"tutte le altre: abbassa --min-per-style solo se sai cosa comporta."
            )
        selected = [(s, counts[s]) for s in stili]
        tetto = min(counts[s] for s in stili)
        if per_style > tetto:
            log.warning(
                "--per-style vale %d ma lo stile meno popolato ne ha %d: il "
                "sottoinsieme sara' bilanciato a %d per classe.",
                per_style, tetto, tetto,
            )
    else:
        eligible = [(s, n) for s, n in counts.most_common() if n >= min_per_style]
        if len(eligible) < num_styles:
            raise RuntimeError(
                f"Richiesti {num_styles} stili con almeno {min_per_style} immagini, "
                f"ma solo {len(eligible)} li raggiungono. Stili disponibili: "
                f"{dict(counts.most_common())}"
            )
        selected = eligible[:num_styles]

    # Il bilanciamento e' sul minimo effettivo, non sul valore richiesto: copiare
    # 5000 immagini da una classe e 900 da un'altra non e' un dataset bilanciato.
    per_style = min(per_style, min(n for _, n in selected))
    rng = random.Random(seed)
    processed.mkdir(parents=True, exist_ok=True)
    manifest_styles = {}

    for style, available in selected:
        src_dir = raw / style
        dst_dir = processed / style
        dst_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(f for f in src_dir.iterdir() if f.suffix.lower() in _IMAGE_SUFFIXES)
        take = min(per_style, len(files))

        # Si scorre l'INTERA lista mescolata e ci si ferma a `take` successi, invece
        # di estrarne esattamente `take` e sperare che siano tutte leggibili.
        #
        # Motivo: un'immagine corrotta scartata senza rimpiazzo abbasserebbe solo la
        # sua classe, rompendo il bilanciamento — cioe' la proprieta' su cui si regge
        # l'interpretabilita' dell'entropia di stile (ADR-0004). Il guasto sarebbe
        # silenzioso: 4.999 immagini invece di 5.000 non si notano guardando le
        # cartelle. Pescando un rimpiazzo dalla coda, le classi restano allineate.
        ordine = rng.sample(files, len(files))
        copiate = 0
        scartate = 0

        from tesi_gan.utils.progress import progress

        for f in progress(ordine, description=f"{style:<20}", total=take):
            if copiate >= take:
                break
            destinazione = dst_dir / f.name
            try:
                if resize is None:
                    shutil.copy2(f, destinazione)
                else:
                    _resize_and_save(f, destinazione, resize)
            except Exception as exc:  # noqa: BLE001
                log.warning("Immagine illeggibile, sostituita: %s (%s)", f.name, exc)
                destinazione.unlink(missing_ok=True)  # niente file troncati
                scartate += 1
                continue
            copiate += 1

        if copiate < take:
            raise RuntimeError(
                f"Stile {style!r}: richieste {take} immagini ma solo {copiate} "
                f"leggibili ({scartate} scartate su {len(files)} file). Il "
                f"sottoinsieme non sarebbe bilanciato. Verifica l'integrita' dei "
                f"dati grezzi prima di procedere."
            )

        manifest_styles[style] = {"disponibili": available, "copiate": copiate}
        if scartate:
            manifest_styles[style]["scartate_e_sostituite"] = scartate
        log.info(
            "%-24s %5d immagini %s (su %d disponibili)%s",
            style, copiate,
            f"ridimensionate a {resize}px" if resize else "copiate",
            available,
            f" — {scartate} illeggibili sostituite" if scartate else "",
        )

    manifest = {
        "data_preparazione": date.today().isoformat(),
        "sorgente": str(raw.resolve()),
        "destinazione": str(processed.resolve()),
        "seed": seed,
        "num_styles": len(selected),
        "per_style_effettive": per_style,
        # La risoluzione su disco va registrata: un `processed` a 64px e uno a 256px
        # producono run non confrontabili, e a occhio i due sono indistinguibili.
        "risoluzione": resize if resize else "originale",
        "selezione": "esplicita" if stili else "per numerosita'",
        "stili": manifest_styles,
        "totale_immagini": sum(v["copiate"] for v in manifest_styles.values()),
        "nota": (
            "Sottoinsieme costruito per l'esperimento comparativo DCGAN/CAN "
            "(ADR-0003). Dataset non ridistribuibile: vedi ADR-0004."
        ),
    }
    manifest_path = processed / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Manifest scritto in %s", manifest_path)
    log.info(
        "Totale: %d immagini su %d stili. Riporta questi numeri in data/README.md.",
        manifest["totale_immagini"],
        manifest["num_styles"],
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tesi-gan-data", description=__doc__)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"),
                        help="Cartella dei dati grezzi, una sottocartella per stile")
    parser.add_argument("--processed", type=Path, default=Path("data/processed"),
                        help="Cartella di destinazione del sottoinsieme")
    parser.add_argument("--stili", nargs="+", default=None,
                        help="Selezione ESPLICITA degli stili, es. --stili ukiyo_e "
                             "renaissance baroque romanticism realism impressionism. "
                             "E' la modalita' corretta con ArtBench (ADR-0004).")
    parser.add_argument("--num-styles", type=int, default=6,
                        help="Usato solo senza --stili: tiene gli N piu' popolati")
    parser.add_argument("--per-style", type=int, default=5000,
                        help="Immagini per stile; ridotto automaticamente al minimo "
                             "disponibile per non rompere il bilanciamento")
    parser.add_argument("--min-per-style", type=int, default=500,
                        help="Soglia minima perche' uno stile sia ammissibile")
    parser.add_argument("--resize", type=int, default=None, metavar="PX",
                        help="Ridimensiona alla risoluzione di addestramento (es. 64). "
                             "Senza, le immagini vengono copiate alla risoluzione "
                             "originale: piu' pesante e piu' lento a ogni epoca.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ispeziona", action="store_true",
                        help="Mostra solo il conteggio per stile, senza copiare nulla")
    parser.add_argument(
        "--licenza-verificata",
        action="store_true",
        help="Dichiara di aver letto i termini d'uso della fonte (V-007). Obbligatorio.",
    )
    args = parser.parse_args(argv)

    if args.ispeziona:
        counts = _count_by_style(args.raw)
        if not counts:
            log.error("Nessuna sottocartella con immagini in %s", args.raw)
            return 1
        log.info("Immagini per stile in %s:", args.raw)
        for style, n in counts.most_common():
            log.info("  %-28s %6d", style, n)
        log.info("Totale: %d immagini su %d stili", sum(counts.values()), len(counts))
        return 0

    if not args.licenza_verificata:
        log.error(
            "Preparazione bloccata: manca --licenza-verificata.\n"
            "Prima di procedere leggi i termini d'uso della fonte da cui provengono i\n"
            "dati e verifica che l'addestramento di un modello generativo a fini di\n"
            "ricerca, senza ridistribuzione di dati ne' di pesi, vi rientri.\n"
            "Poi registra l'esito in docs/registro-decisioni.md (V-007) e rilancia.\n"
            "Per il solo conteggio, senza copiare nulla, usa --ispeziona."
        )
        return 2

    prepare(
        raw=args.raw,
        processed=args.processed,
        num_styles=args.num_styles,
        per_style=args.per_style,
        seed=args.seed,
        min_per_style=args.min_per_style,
        stili=args.stili,
        resize=args.resize,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
