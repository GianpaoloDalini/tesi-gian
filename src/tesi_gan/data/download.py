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


def prepare(
    raw: Path,
    processed: Path,
    num_styles: int,
    per_style: int,
    seed: int,
    min_per_style: int,
) -> dict:
    """Costruisce il sottoinsieme bilanciato a partire dai dati grezzi.

    Sceglie i `num_styles` stili piu' popolati, ne campiona `per_style` immagini
    ciascuno e li copia in `processed/<stile>/`.

    **Il bilanciamento non e' cosmetico.** Con classi sbilanciate la testa di stile
    del discriminatore impara la distribuzione a priori invece dello stile, e
    l'entropia della posterior — cioe' la metrica su cui si regge il confronto —
    diventa ininterpretabile. Il campionamento e' seedato: due preparazioni con lo
    stesso seed producono lo stesso sottoinsieme.
    """
    if not raw.exists():
        raise FileNotFoundError(f"Cartella dei dati grezzi inesistente: {raw}")

    counts = _count_by_style(raw)
    if not counts:
        raise RuntimeError(
            f"Nessuna sottocartella con immagini in {raw}. Attesa una cartella per "
            f"stile: {raw}/<stile>/<immagine>.jpg"
        )

    eligible = [(s, n) for s, n in counts.most_common() if n >= min_per_style]
    if len(eligible) < num_styles:
        raise RuntimeError(
            f"Richiesti {num_styles} stili con almeno {min_per_style} immagini, "
            f"ma solo {len(eligible)} li raggiungono. Stili disponibili: "
            f"{dict(counts.most_common())}"
        )

    selected = eligible[:num_styles]
    rng = random.Random(seed)
    processed.mkdir(parents=True, exist_ok=True)
    manifest_styles = {}

    for style, available in selected:
        src_dir = raw / style
        dst_dir = processed / style
        dst_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(f for f in src_dir.iterdir() if f.suffix.lower() in _IMAGE_SUFFIXES)
        take = min(per_style, len(files))
        chosen = rng.sample(files, take)
        for f in chosen:
            shutil.copy2(f, dst_dir / f.name)

        manifest_styles[style] = {"disponibili": available, "copiate": take}
        log.info("%-24s %5d immagini copiate (su %d disponibili)", style, take, available)

    manifest = {
        "data_preparazione": date.today().isoformat(),
        "sorgente": str(raw.resolve()),
        "destinazione": str(processed.resolve()),
        "seed": seed,
        "num_styles": len(selected),
        "per_style_richieste": per_style,
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
    parser.add_argument("--num-styles", type=int, default=8,
                        help="Numero di stili da tenere, i piu' popolati")
    parser.add_argument("--per-style", type=int, default=2000,
                        help="Immagini per stile nel sottoinsieme bilanciato")
    parser.add_argument("--min-per-style", type=int, default=500,
                        help="Soglia minima perche' uno stile sia ammissibile")
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
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
