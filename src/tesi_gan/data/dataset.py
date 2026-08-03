"""Caricamento del dataset con etichette di stile.

Le etichette non sono un accessorio: senza di esse la testa di classificazione
della CAN non e' addestrabile e l'esperimento comparativo di ADR-0003 non esiste.
Per questo il dataloader le espone sempre, anche quando addestra la DCGAN, che le
ignora. Cosi' le due condizioni leggono **gli stessi identici batch**, nello stesso
ordine, a parita' di seed.

Struttura attesa su disco, una cartella per stile:

    data/processed/
        baroque/
            0001.jpg
            ...
        impressionism/
            ...

Il numero di classi si **ricava dai dati**, non si legge dalla configurazione: una
configurazione che dichiara 10 stili su un dataset che ne contiene 7 produrrebbe un
modello con tre classi mai osservate e una metrica di ambiguita' falsata.
"""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import ImageFolder

# Normalizzazione in [-1, 1], coerente con la tanh in uscita dal generatore.
# Se si cambia qui, va cambiata anche la denormalizzazione in evaluation/figures.
_MEAN = (0.5, 0.5, 0.5)
_STD = (0.5, 0.5, 0.5)


def build_transform(image_size: int, augment: bool = True) -> transforms.Compose:
    """Trasformazioni di preprocessing.

    L'unica augmentation e' il flip orizzontale. Ruotare o ritagliare aggressivamente
    dipinti e' discutibile: altera la composizione, che in pittura e' parte dello
    stile che il discriminatore deve classificare.
    """
    ops: list = [
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
    ]
    if augment:
        ops.append(transforms.RandomHorizontalFlip(p=0.5))
    ops += [transforms.ToTensor(), transforms.Normalize(_MEAN, _STD)]
    return transforms.Compose(ops)


def denormalize(images: torch.Tensor) -> torch.Tensor:
    """Riporta le immagini da [-1, 1] a [0, 1] per il salvataggio e le metriche."""
    return (images.clamp(-1, 1) + 1.0) / 2.0


class SyntheticStyleDataset(Dataset):
    """Dataset sintetico per gli smoke test, senza dipendere da dati su disco.

    Genera immagini rumorose con una tinta dominante diversa per classe. Serve a
    verificare che la pipeline giri end-to-end su CPU prima di spendere ore di GPU:
    non produce risultati citabili in tesi e non deve mai comparire in un run
    registrato in `experiments/registry.md`.
    """

    def __init__(self, n: int = 64, image_size: int = 64, num_styles: int = 4) -> None:
        self.n = n
        self.image_size = image_size
        self.num_styles = num_styles
        self.classes = [f"stile_sintetico_{i}" for i in range(num_styles)]
        # Stessa convenzione di ImageFolder: consente lo split stratificato del
        # classificatore di stile senza caricare le immagini.
        self.targets = [i % num_styles for i in range(n)]

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        label = idx % self.num_styles
        generator = torch.Generator().manual_seed(idx)
        img = torch.randn(3, self.image_size, self.image_size, generator=generator) * 0.3
        img[label % 3] += 0.5
        return img.clamp(-1, 1), label


def build_dataset(cfg) -> Dataset:
    """Costruisce il dataset dalla configurazione Hydra."""
    if str(cfg.data.name).lower() in {"synthetic", "placeholder"}:
        return SyntheticStyleDataset(
            n=int(cfg.data.get("synthetic_size", 256)),
            image_size=int(cfg.data.image_size),
            num_styles=int(cfg.data.get("synthetic_styles", 4)),
        )

    root = Path(cfg.data.root)
    if not root.exists():
        raise FileNotFoundError(
            f"Dataset non trovato in {root}. I dati non stanno nel repository "
            f"(CLAUDE.md §2.5): scaricali con `python -m tesi_gan.data.download` e "
            f"documentane la provenienza in data/README.md."
        )

    dataset = ImageFolder(
        root=str(root),
        transform=build_transform(
            int(cfg.data.image_size),
            augment=bool(cfg.data.get("augment", True)),
        ),
    )
    if len(dataset) == 0:
        raise RuntimeError(f"Nessuna immagine trovata sotto {root}.")
    return dataset


def build_reference_dataset(cfg) -> Dataset | None:
    """Dataset di **riferimento**, indipendente da quello di addestramento.

    Corrisponde allo split `test` ufficiale di ArtBench (1.000 immagini per stile).
    Serve a due cose distinte, entrambe di credibilita' e non di prestazioni:

    1. **Validazione del giudice di stile** (ADR-0005). L'accuratezza misurata su
       dati mai visti, e per giunta sullo split ufficiale del dataset, e' un numero
       confrontabile con i benchmark pubblicati. Misurata su una porzione ritagliata
       dal training set sarebbe soltanto un numero interno.
    2. **Distribuzione di riferimento per il FID.** Calcolare il FID contro le stesse
       immagini su cui il generatore si e' addestrato premia la memorizzazione: un
       modello che riproducesse i dati di addestramento otterrebbe un FID eccellente
       senza aver imparato nulla di generalizzabile.

    Restituisce `None` se `data.reference_root` non e' configurato: in quel caso il
    giudice ricade sullo split interno e il FID si calcola contro il training set.
    E' una configurazione ammissibile — il confronto fra le due condizioni resta
    valido perche' il bias e' identico per entrambe — ma va dichiarata.

    **Nessuna augmentation sul riferimento.** Il flip orizzontale ha senso quando si
    addestra, non quando si misura: una distribuzione di riferimento aumentata non e'
    piu' la distribuzione dei dati reali.
    """
    reference_root = cfg.data.get("reference_root")
    if not reference_root:
        return None

    root = Path(reference_root)
    if not root.exists():
        raise FileNotFoundError(
            f"Riferimento configurato ma inesistente: {root}. Prepara lo split di "
            f"riferimento oppure rimuovi `data.reference_root` dalla configurazione."
        )

    dataset = ImageFolder(
        root=str(root),
        transform=build_transform(int(cfg.data.image_size), augment=False),
    )
    if len(dataset) == 0:
        raise RuntimeError(f"Nessuna immagine trovata sotto {root}.")
    return dataset


def assert_same_classes(training: Dataset, reference: Dataset) -> None:
    """Verifica che i due dataset espongano le stesse classi **nello stesso ordine**.

    `ImageFolder` assegna gli indici in ordine alfabetico delle cartelle. Se il
    riferimento contenesse un sottoinsieme diverso di stili, gli indici slitterebbero
    e il giudice verrebbe validato confrontando le sue predizioni con etichette che
    significano altro. Il guasto sarebbe silenzioso e i numeri sembrerebbero
    plausibili: per questo si controlla invece di fidarsi.
    """
    classi_training = list(getattr(training, "classes", []))
    classi_riferimento = list(getattr(reference, "classes", []))
    if classi_training != classi_riferimento:
        raise RuntimeError(
            f"Le classi del set di addestramento {classi_training} non coincidono "
            f"con quelle del riferimento {classi_riferimento}. Gli indici di classe "
            f"slitterebbero e le etichette non significherebbero piu' la stessa cosa."
        )


def num_styles_of(dataset: Dataset) -> int:
    """Numero di classi di stile effettivamente presenti nel dataset."""
    classes = getattr(dataset, "classes", None)
    if classes is None:
        raise AttributeError(
            "Il dataset non espone `classes`: senza etichette di stile la CAN non "
            "e' addestrabile (ADR-0003)."
        )
    return len(classes)


def build_dataloader(cfg, dataset: Dataset | None = None) -> DataLoader:
    """Costruisce il DataLoader.

    `drop_last=True` non e' opzionale: un batch finale piu' piccolo destabilizza le
    statistiche di BatchNorm del discriminatore, con effetti visibili sulle curve.
    """
    dataset = dataset if dataset is not None else build_dataset(cfg)
    return DataLoader(
        dataset,
        batch_size=int(cfg.training.batch_size),
        shuffle=True,
        num_workers=int(cfg.data.get("num_workers", 4)),
        pin_memory=torch.cuda.is_available(),
        drop_last=True,
        persistent_workers=int(cfg.data.get("num_workers", 4)) > 0,
    )
