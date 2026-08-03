"""Punto di ingresso unico degli esperimenti.

    python -m tesi_gan.cli train-style-classifier          # una volta sola, prima di tutto
    python -m tesi_gan.cli train model=dcgan
    python -m tesi_gan.cli train model=can
    python -m tesi_gan.cli evaluate --checkpoint experiments/checkpoints/latest.pt
    python -m tesi_gan.cli export-figures

Ogni comando legge la configurazione da `configs/` tramite Hydra: nessun
iperparametro va passato modificando il codice sorgente (D-007). Gli override si
scrivono in coda al comando, es. `training.epochs=100 model=can`.

Si usa l'API di composizione di Hydra invece del decoratore `@hydra.main` per poter
convivere con i sottocomandi di argparse e per rendere la configurazione
componibile dai test.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("tesi_gan")

_CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"


def load_config(overrides: list[str] | None = None):
    """Compone la configurazione Hydra a partire da `configs/config.yaml`."""
    from hydra import compose, initialize_config_dir
    from hydra.core.global_hydra import GlobalHydra

    if GlobalHydra.instance().is_initialized():
        GlobalHydra.instance().clear()
    with initialize_config_dir(config_dir=str(_CONFIG_DIR), version_base=None):
        return compose(config_name="config", overrides=overrides or [])


def _device():
    import torch

    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# --------------------------------------------------------------------------- #
#  train
# --------------------------------------------------------------------------- #

def cmd_train(cfg, allow_dirty: bool, resume: bool) -> int:
    from omegaconf import OmegaConf

    from tesi_gan.data import build_dataloader, build_dataset, num_styles_of
    from tesi_gan.models import build_models
    from tesi_gan.training import Trainer, count_parameters
    from tesi_gan.utils import provenance
    from tesi_gan.utils.seed import set_seed
    from tesi_gan.utils.tracking import build_tracker

    if not allow_dirty:
        provenance.assert_clean_tree()
    prov = provenance.collect()

    set_seed(int(cfg.seed), strict=bool(cfg.get("strict_determinism", False)))
    device = _device()

    dataset = build_dataset(cfg)
    detected = num_styles_of(dataset)
    declared = cfg.model.get("num_styles")

    # Il numero di stili si ricava dai dati (ADR-0004). Se la configurazione ne
    # dichiara un altro, il modello avrebbe classi mai osservate e l'entropia della
    # posterior — la metrica su cui si regge il confronto — sarebbe falsata.
    if str(cfg.model.name).lower() == "can":
        if declared is None:
            log.info("model.num_styles non dichiarato: ricavato dai dati = %d", detected)
            OmegaConf.update(cfg, "model.num_styles", detected, force_add=True)
        elif int(declared) != detected:
            raise ValueError(
                f"model.num_styles={declared} non coincide con gli stili presenti nel "
                f"dataset ({detected}). Correggi la configurazione o il dataset: "
                f"addestrare su un numero di classi sbagliato invalida la metrica di "
                f"ambiguita' stilistica."
            )

    dataloader = build_dataloader(cfg, dataset)
    generator, discriminator = build_models(cfg)

    log.info(
        "Condizione: %s | stili: %d | immagini: %d | batch: %d",
        str(cfg.model.name).upper(),
        detected,
        len(dataset),
        int(cfg.training.batch_size),
    )
    log.info(
        "Parametri addestrabili — G: %s, D: %s",
        f"{count_parameters(generator):,}",
        f"{count_parameters(discriminator):,}",
    )

    tracker = build_tracker(cfg, prov)
    trainer = Trainer(cfg, generator, discriminator, dataloader, device, tracker)

    if resume and trainer.maybe_resume():
        log.info("Run ripreso dall'epoca %d", trainer.state.epoch)

    try:
        trainer.fit(int(cfg.training.epochs))
    finally:
        trainer.save_checkpoint("final.pt")
        tracker.finish()

    log.info(
        "Training concluso. Registra il run in experiments/registry.md: "
        "run_id=%s, commit=%s",
        tracker.run_id,
        prov.commit[:8],
    )
    return 0


# --------------------------------------------------------------------------- #
#  train-style-classifier
# --------------------------------------------------------------------------- #

def cmd_train_style_classifier(cfg, force: bool) -> int:
    """Addestra il giudice terzo dell'ambiguita' stilistica (ADR-0005).

    Va eseguito **una volta sola**, prima dei run dell'impianto. Riaddestrarlo fra
    un run e l'altro renderebbe le entropie non confrontabili.
    """
    from tesi_gan.data import (
        assert_same_classes,
        build_dataset,
        build_reference_dataset,
        num_styles_of,
    )
    from tesi_gan.evaluation.style_classifier import (
        save_style_classifier,
        train_style_classifier,
    )
    from tesi_gan.utils import provenance
    from tesi_gan.utils.seed import set_seed

    directory = Path(cfg.paths.style_judge)
    if (directory / "style_classifier.pt").exists() and not force:
        log.error(
            "Esiste gia' un classificatore in %s.\n"
            "Riaddestrarlo invaliderebbe il confronto con i run gia' valutati, che "
            "sono stati misurati da un giudice diverso.\n"
            "Se e' davvero cio' che vuoi, usa --force e rivaluta TUTTI i checkpoint.",
            directory,
        )
        return 1

    judge_cfg = cfg.style_judge
    set_seed(int(judge_cfg.seed))
    device = _device()

    dataset = build_dataset(cfg)
    num_styles = num_styles_of(dataset)
    classes = list(getattr(dataset, "classes", []))

    # Split di riferimento, se configurato: l'accuratezza del giudice viene misurata
    # su dati mai visti invece che su una porzione ritagliata dal training set.
    reference = build_reference_dataset(cfg)
    if reference is not None:
        assert_same_classes(dataset, reference)

    log.info(
        "Addestramento del giudice — %d immagini, %d stili: %s",
        len(dataset), num_styles, ", ".join(classes),
    )
    if reference is not None:
        log.info("Validazione sullo split esterno: %d immagini", len(reference))
    else:
        log.warning(
            "Nessuno split di riferimento configurato (`data.reference_root`): "
            "l'accuratezza sara' misurata su una porzione del training set. "
            "Ammissibile, ma va dichiarato in tesi."
        )

    try:
        commit = provenance.collect().commit
    except Exception:  # fuori da git il giudice si addestra comunque
        commit = None

    classifier, info = train_style_classifier(
        dataset=dataset,
        num_styles=num_styles,
        classes=classes,
        device=device,
        epochs=int(judge_cfg.epochs),
        batch_size=int(judge_cfg.batch_size),
        lr=float(judge_cfg.lr),
        val_fraction=float(judge_cfg.val_fraction),
        seed=int(judge_cfg.seed),
        num_workers=int(cfg.data.get("num_workers", 4)),
        commit=commit,
        val_dataset=reference,
        # La risoluzione viene dalla configurazione dei dati, come per le reti
        # dell'impianto: un giudice costruito per una risoluzione diversa da quella
        # delle immagini fallisce con un errore di forma.
        image_size=int(cfg.data.image_size),
    )
    save_style_classifier(classifier, info, directory)

    print(json.dumps(info.as_dict(), indent=2, ensure_ascii=False))
    log.info(
        "Riporta accuratezza (%.3f) ed entropia sui reali (%.3f nats) in appendice: "
        "senza, le entropie sui generati non sono interpretabili.",
        info.val_accuracy, info.entropy_real,
    )
    return 0


# --------------------------------------------------------------------------- #
#  inspect-style-classifier
# --------------------------------------------------------------------------- #

def cmd_inspect_style_classifier(cfg) -> int:
    """Diagnostica del giudice gia' addestrato: dove sbaglia, non solo quanto.

    Non riaddestra nulla, quindi si puo' lanciare quante volte si vuole senza
    invalidare i run gia' valutati.
    """
    import torch
    from torch.utils.data import DataLoader

    from tesi_gan.data import assert_same_classes, build_dataset, build_reference_dataset
    from tesi_gan.evaluation.style_classifier import (
        confusion_matrix,
        format_confusion_matrix,
        load_style_classifier,
    )

    device = _device()
    dataset = build_dataset(cfg)
    classes = list(getattr(dataset, "classes", []))

    reference = build_reference_dataset(cfg)
    if reference is not None:
        assert_same_classes(dataset, reference)
    valutazione = reference if reference is not None else dataset

    classifier, info = load_style_classifier(
        Path(cfg.paths.style_judge), device, expected_classes=classes or None
    )

    loader = DataLoader(
        valutazione,
        batch_size=int(cfg.style_judge.get("batch_size", 64)),
        shuffle=False,
        num_workers=int(cfg.data.get("num_workers", 4)),
        pin_memory=torch.cuda.is_available(),
    )
    matrice = confusion_matrix(classifier, loader, device)

    print()
    print(f"Matrice di confusione su {int(matrice.sum())} immagini reali "
          f"(split {info.validazione}) — riga = stile vero, colonna = predetto")
    print()
    print(format_confusion_matrix(matrice, classes))
    print()
    print(f"Accuratezza complessiva : {info.val_accuracy:.3f}")
    print(f"Entropia sui reali      : {info.entropy_real:.3f} nats "
          f"(normalizzata {info.entropy_real_normalized:.3f})")
    print(f"Soffitto log(K)         : {info.max_entropy:.3f}")
    print()

    # La lettura che conta: errori concentrati fra stili vicini oppure sparsi.
    k = len(classes)
    fuori_diagonale = matrice.clone()
    fuori_diagonale.fill_diagonal_(0)
    if int(fuori_diagonale.sum()) > 0:
        peggiori = torch.topk(fuori_diagonale.flatten(), k=min(5, k * (k - 1)))
        print("Confusioni piu' frequenti:")
        for valore, indice in zip(peggiori.values, peggiori.indices):
            if int(valore) == 0:
                continue
            i, j = divmod(int(indice), k)
            print(f"  {classes[i]:<16} scambiato per {classes[j]:<16} {int(valore):>5} volte")
        print()
    return 0


# --------------------------------------------------------------------------- #
#  evaluate
# --------------------------------------------------------------------------- #

def cmd_evaluate(
    cfg, checkpoint: Path, n_samples: int, output: Path | None, allow_no_judge: bool = False
) -> int:
    import torch
    from omegaconf import OmegaConf

    from tesi_gan.data import (
        assert_same_classes,
        build_dataloader,
        build_dataset,
        build_reference_dataset,
        num_styles_of,
    )
    from tesi_gan.evaluation import evaluate
    from tesi_gan.evaluation.style_classifier import load_style_classifier
    from tesi_gan.models import build_models
    from tesi_gan.utils.seed import set_seed

    if not checkpoint.exists():
        log.error("Checkpoint inesistente: %s", checkpoint)
        return 1

    set_seed(int(cfg.seed))
    device = _device()

    dataset = build_dataset(cfg)
    if str(cfg.model.name).lower() == "can" and cfg.model.get("num_styles") is None:
        OmegaConf.update(cfg, "model.num_styles", num_styles_of(dataset), force_add=True)

    # Il giudice terzo va caricato prima di valutare: senza, l'ambiguita' non e'
    # confrontabile fra DCGAN e CAN e la valutazione non risponde alla domanda
    # dell'impianto (ADR-0005).
    style_judge = judge_info = None
    try:
        style_judge, judge_info = load_style_classifier(
            Path(cfg.paths.style_judge),
            device,
            expected_classes=list(getattr(dataset, "classes", [])) or None,
        )
    except FileNotFoundError as err:
        if not allow_no_judge:
            log.error("%s", err)
            log.error(
                "Valutare senza giudice produce solo FID e IS, due metriche che per "
                "costruzione penalizzano la CAN. Usa --allow-no-judge solo per "
                "controlli rapidi, mai per i numeri che finiscono in tesi."
            )
            return 1
        log.warning("Valutazione senza giudice terzo: risultati non confrontabili.")

    generator, discriminator = build_models(cfg)
    ckpt = torch.load(checkpoint, map_location=device, weights_only=True)
    generator.load_state_dict(ckpt["generator"])
    discriminator.load_state_dict(ckpt["discriminator"])
    generator.to(device).eval()
    discriminator.to(device).eval()

    # Il FID si calcola contro il RIFERIMENTO, non contro i dati di addestramento:
    # misurarlo sulle stesse immagini che il generatore ha visto premia la
    # memorizzazione invece della generalizzazione.
    reference = build_reference_dataset(cfg)
    if reference is not None:
        assert_same_classes(dataset, reference)
        log.info("FID calcolato contro lo split di riferimento (%d immagini)", len(reference))
    else:
        log.warning(
            "Nessuno split di riferimento: il FID e' calcolato contro i dati di "
            "addestramento. Va dichiarato in tesi — favorisce la memorizzazione."
        )

    result = evaluate(
        generator=generator,
        discriminator=discriminator,
        real_loader=build_dataloader(cfg, reference if reference is not None else dataset),
        device=device,
        n_samples=n_samples,
        batch_size=int(cfg.training.batch_size),
        style_judge=style_judge,
        judge_info=judge_info,
    )

    payload = {
        "checkpoint": str(checkpoint),
        "condizione": str(cfg.model.name),
        "seed": int(cfg.seed),
        "epoca": int(ckpt.get("epoch", -1)),
        "riferimento_fid": "split esterno" if reference is not None else "training set",
        **result.as_dict(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("Risultati scritti in %s", output)
    return 0


# --------------------------------------------------------------------------- #
#  export-figures
# --------------------------------------------------------------------------- #

def cmd_export_figures(cfg, results_dir: Path) -> int:
    from tesi_gan.evaluation.figures import export_all

    written = export_all(cfg, results_dir)
    if not written:
        log.warning(
            "Nessuna figura prodotta: non ci sono ancora risultati in %s. "
            "Lancia prima `train` e `evaluate`.",
            results_dir,
        )
        return 1
    for path in written:
        log.info("Figura scritta: %s", path)
    return 0


# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="tesi-gan", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_train = sub.add_parser("train", help="Addestra un modello")
    p_train.add_argument("--allow-dirty", action="store_true",
                         help="Consente il training con modifiche non committate (sconsigliato)")
    p_train.add_argument("--resume", action="store_true",
                         help="Riprende da experiments/checkpoints/latest.pt se esiste")

    p_judge = sub.add_parser(
        "train-style-classifier",
        help="Addestra il giudice terzo dell'ambiguita' stilistica (una volta sola)",
    )
    p_judge.add_argument(
        "--force", action="store_true",
        help="Sovrascrive un giudice esistente. Obbliga a rivalutare TUTTI i checkpoint.",
    )

    sub.add_parser(
        "inspect-style-classifier",
        help="Matrice di confusione del giudice gia' addestrato, senza riaddestrarlo",
    )

    p_eval = sub.add_parser("evaluate", help="Calcola le metriche su un checkpoint")
    p_eval.add_argument("--checkpoint", type=Path, required=True)
    p_eval.add_argument("--n-samples", type=int, default=2048,
                        help="Deve restare identico fra le due condizioni")
    p_eval.add_argument("--output", type=Path, default=None,
                        help="File JSON in cui salvare i risultati")
    p_eval.add_argument("--allow-no-judge", action="store_true",
                        help="Valuta senza giudice terzo: solo per controlli rapidi, "
                             "i risultati non sono confrontabili fra condizioni")

    p_fig = sub.add_parser("export-figures", help="Rigenera le figure della tesi")
    p_fig.add_argument("--results-dir", type=Path, default=Path("experiments/results"))

    args, overrides = parser.parse_known_args(argv)
    cfg = load_config(overrides)

    if args.command == "train":
        return cmd_train(cfg, allow_dirty=args.allow_dirty, resume=args.resume)
    if args.command == "train-style-classifier":
        return cmd_train_style_classifier(cfg, force=args.force)
    if args.command == "inspect-style-classifier":
        return cmd_inspect_style_classifier(cfg)
    if args.command == "evaluate":
        return cmd_evaluate(
            cfg, args.checkpoint, args.n_samples, args.output,
            allow_no_judge=args.allow_no_judge,
        )
    if args.command == "export-figures":
        return cmd_export_figures(cfg, args.results_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
