"""Classificatore di stile **terzo**: il giudice indipendente dell'ambiguita'.

## Perche' esiste

`metrics.style_ambiguity` misura l'entropia della posterior prodotta dalla testa di
stile del discriminatore. Ha due difetti che la rendono inservibile per il confronto
di ADR-0003:

1. **Non e' calcolabile sulla DCGAN**, che la testa di stile non ce l'ha. La
   condizione di controllo resterebbe senza misura, e il confronto non esisterebbe.
2. **Non e' indipendente**: quel discriminatore si e' addestrato *contro* quel
   generatore. Chiedergli se il generatore lo confonde e' chiedere a una parte in
   causa di arbitrare la propria partita.

Questo modulo addestra **una volta sola, sui soli dati reali**, un classificatore di
stile che poi resta congelato. Lo stesso identico giudice valuta entrambe le
condizioni e tutti i seed, quindi le entropie sono confrontabili fra loro.

## Il confondimento da tenere presente, sempre

Un'entropia alta significa \"il classificatore non sa attribuire uno stile\". Ci sono
**due** ragioni per cui puo' succedere, e la metrica da sola non le distingue:

- l'immagine e' pittoricamente sensata ma stilisticamente ibrida — e' l'effetto che
  la CAN cerca;
- l'immagine e' rumore informe — il classificatore e' confuso perche' non c'e' nulla
  da classificare.

**Un generatore collassato ottiene ambiguita' massima.** Per questo l'entropia non va
mai riportata da sola: va letta accanto al FID e alla griglia di campioni. Entropia
alta *e* FID basso e' l'esito interessante; entropia alta *e* FID pessimo e'
semplicemente un modello che non ha imparato a dipingere. La tesi deve dichiararlo
esplicitamente, altrimenti la commissione lo dichiara al posto tuo.

## Riferimenti di lettura obbligatori

Le entropie assolute non dicono nulla senza due ancore, entrambe calcolate qui:

- `entropy_real`: entropia sulle **immagini reali** del set di validazione. E' il
  pavimento — quanto e' sicuro il classificatore su arte vera e attribuibile.
- `log(K)`: il soffitto teorico, raggiunto dalla posterior uniforme.

Un valore normalizzato in [0, 1] senza il confronto col pavimento e' un numero che
sembra significare qualcosa e non significa niente.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, Dataset, Subset

log = logging.getLogger(__name__)

_WEIGHTS = "style_classifier.pt"
_METADATA = "style_classifier.json"

# Sotto questa accuratezza di validazione il giudice non e' credibile: se non sa
# riconoscere lo stile di un dipinto vero, la sua incertezza su un'immagine generata
# non e' informativa. Il valore non e' sacro, ma abbassarlo va motivato in tesi.
MIN_VAL_ACCURACY = 0.60


# --------------------------------------------------------------------------- #
#  Architettura
# --------------------------------------------------------------------------- #

class StyleClassifier(nn.Module):
    """CNN per la classificazione dello stile a 64x64.

    Stessa famiglia architetturale della backbone del discriminatore (blocchi
    Conv-BatchNorm-LeakyReLU con stride 2) per una ragione precisa: se il giudice
    fosse molto piu' capace del discriminatore, misurerebbe un'ambiguita' che nel
    gioco avversario non ha mai avuto un ruolo; se fosse molto meno capace,
    misurerebbe soprattutto la propria incompetenza.

    **Non e' pre-addestrata su ImageNet.** E' una scelta deliberata: la tesi critica
    FID e IS proprio perche' poggiano su feature fotografiche di ImageNet (vedi
    `metrics.py`). Usare un giudice con lo stesso vizio significherebbe muovere
    un'obiezione e poi commetterla. Con sei classi e migliaia di immagini per classe,
    l'addestramento da zero e' ampiamente sufficiente.

    Ingresso atteso: immagini in **[-1, 1]**, la stessa scala del dataloader e
    dell'uscita `tanh` del generatore. Nessuna conversione ai bordi, nessun rischio
    di valutare i due domini su scale diverse.
    """

    def __init__(
        self,
        num_styles: int,
        features: int = 64,
        channels: int = 3,
        dropout: float = 0.3,
    ) -> None:
        super().__init__()
        if num_styles < 2:
            raise ValueError(
                f"num_styles={num_styles}: servono almeno due stili perche' la "
                f"classificazione — e quindi l'entropia — abbia senso."
            )
        self.num_styles = num_styles

        def block(in_c: int, out_c: int, batchnorm: bool = True) -> nn.Sequential:
            layers: list[nn.Module] = [nn.Conv2d(in_c, out_c, 4, 2, 1, bias=False)]
            if batchnorm:
                layers.append(nn.BatchNorm2d(out_c))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return nn.Sequential(*layers)

        self.backbone = nn.Sequential(
            block(channels, features, batchnorm=False),  # 64 -> 32
            block(features, features * 2),               # 32 -> 16
            block(features * 2, features * 4),           # 16 -> 8
            block(features * 4, features * 8),           # 8  -> 4
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(features * 8 * 4 * 4, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, num_styles),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Restituisce i **logit** di stile, non probabilita'."""
        return self.head(self.backbone(x))


# --------------------------------------------------------------------------- #
#  Metadati
# --------------------------------------------------------------------------- #

@dataclass
class StyleClassifierInfo:
    """Cio' che va saputo del giudice prima di fidarsi dei suoi numeri.

    Finisce accanto ai pesi in un JSON e va riportato in appendice: un'entropia
    prodotta da un classificatore di cui non si dichiara l'accuratezza non e' un
    risultato, e' un numero.
    """

    num_styles: int
    classes: list[str]
    val_accuracy: float
    train_size: int
    val_size: int
    epochs: int
    seed: int
    entropy_real: float
    entropy_real_normalized: float
    max_entropy: float
    commit: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
#  Split
# --------------------------------------------------------------------------- #

def _targets_of(dataset: Dataset) -> list[int]:
    """Etichette del dataset senza caricare le immagini.

    `ImageFolder` espone `targets`; il dataset sintetico degli smoke test pure.
    Se manca, si ricade sull'iterazione — corretto ma lento, quindi si avvisa.
    """
    targets = getattr(dataset, "targets", None)
    if targets is not None:
        return [int(t) for t in targets]
    log.warning(
        "Il dataset non espone `targets`: le etichette vengono lette una a una. "
        "Su ImageFolder non dovrebbe accadere."
    )
    return [int(dataset[i][1]) for i in range(len(dataset))]  # type: ignore[index]


def stratified_split(
    dataset: Dataset,
    val_fraction: float,
    seed: int,
) -> tuple[Subset, Subset]:
    """Divide il dataset in train e validation **preservando le proporzioni di classe**.

    Con uno split casuale non stratificato su classi poco numerose, una classe puo'
    finire quasi tutta da un lato: l'accuratezza di validazione diventerebbe una
    misura del caso invece che del modello. Lo split e' seedato, quindi due
    esecuzioni con lo stesso seed producono la stessa partizione — condizione perche'
    il giudice sia riproducibile.
    """
    if not 0.0 < val_fraction < 1.0:
        raise ValueError(f"val_fraction deve stare in (0, 1), ricevuto {val_fraction}")

    targets = _targets_of(dataset)
    by_class: dict[int, list[int]] = {}
    for idx, label in enumerate(targets):
        by_class.setdefault(label, []).append(idx)

    generator = torch.Generator().manual_seed(seed)
    train_idx: list[int] = []
    val_idx: list[int] = []

    for label in sorted(by_class):
        indices = by_class[label]
        permutation = torch.randperm(len(indices), generator=generator).tolist()
        shuffled = [indices[p] for p in permutation]
        n_val = max(1, int(round(len(shuffled) * val_fraction)))
        if n_val >= len(shuffled):
            raise RuntimeError(
                f"La classe {label} ha {len(shuffled)} immagini: troppo poche per "
                f"ricavarne sia train sia validation con val_fraction={val_fraction}."
            )
        val_idx.extend(shuffled[:n_val])
        train_idx.extend(shuffled[n_val:])

    return Subset(dataset, sorted(train_idx)), Subset(dataset, sorted(val_idx))


# --------------------------------------------------------------------------- #
#  Entropia
# --------------------------------------------------------------------------- #

def _entropy_of_logits(logits: torch.Tensor) -> torch.Tensor:
    """Entropia in nats della posterior, per ciascun elemento del batch."""
    log_p = F.log_softmax(logits, dim=1)
    return -(log_p.exp() * log_p).sum(dim=1)


@torch.no_grad()
def entropy_on_loader(
    classifier: StyleClassifier,
    loader: DataLoader,
    device: torch.device,
    max_batches: int | None = None,
) -> tuple[float, float]:
    """Entropia media su immagini **reali**: il pavimento di riferimento.

    Restituisce `(accuratezza, entropia_media)`. L'accuratezza serve a sapere se il
    giudice e' credibile; l'entropia serve come termine di paragone per quella
    misurata sulle immagini generate.
    """
    classifier.eval()
    correct = seen = 0
    entropy_sum = 0.0

    for i, (images, labels) in enumerate(loader):
        if max_batches is not None and i >= max_batches:
            break
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        logits = classifier(images)
        correct += int((logits.argmax(dim=1) == labels).sum())
        entropy_sum += float(_entropy_of_logits(logits).sum())
        seen += images.size(0)

    if seen == 0:
        raise RuntimeError("Loader vuoto: nessuna immagine su cui misurare.")
    return correct / seen, entropy_sum / seen


@torch.no_grad()
def entropy_on_generator(
    classifier: StyleClassifier,
    generator,
    n_samples: int,
    batch_size: int,
    device: torch.device,
) -> tuple[float, float]:
    """Entropia media della posterior di stile sulle immagini **generate**.

    Funziona identicamente per DCGAN e CAN — e' esattamente il punto: il giudice non
    sa e non deve sapere quale condizione ha prodotto le immagini.

    Restituisce `(entropia_nats, entropia_normalizzata)` dove la normalizzazione e'
    rispetto a `log(K)`: 1.0 significa posterior perfettamente uniforme.
    """
    classifier.eval()
    total = 0.0
    seen = 0

    while seen < n_samples:
        n = min(batch_size, n_samples - seen)
        images = generator.sample(n, device)  # [-1, 1], come i dati reali
        total += float(_entropy_of_logits(classifier(images)).sum())
        seen += n

    mean_entropy = total / max(seen, 1)
    return mean_entropy, mean_entropy / math.log(classifier.num_styles)


# --------------------------------------------------------------------------- #
#  Addestramento
# --------------------------------------------------------------------------- #

def train_style_classifier(
    dataset: Dataset,
    num_styles: int,
    classes: list[str],
    device: torch.device,
    epochs: int = 15,
    batch_size: int = 64,
    lr: float = 2e-4,
    val_fraction: float = 0.15,
    seed: int = 42,
    num_workers: int = 4,
    commit: str | None = None,
) -> tuple[StyleClassifier, StyleClassifierInfo]:
    """Addestra il giudice sui dati reali e ne misura l'attendibilita'.

    **Si addestra una volta sola.** Il classificatore prodotto qui va poi riusato
    identico per tutti i run e tutte le condizioni: riaddestrarlo fra un run e
    l'altro introdurrebbe una variabile nascosta e renderebbe le entropie non
    confrontabili, che e' precisamente il difetto che questo modulo esiste per
    eliminare.
    """
    train_set, val_set = stratified_split(dataset, val_fraction, seed)
    log.info(
        "Split stratificato: %d immagini di addestramento, %d di validazione",
        len(train_set), len(val_set),
    )

    train_loader = DataLoader(
        train_set, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=torch.cuda.is_available(), drop_last=True,
    )
    val_loader = DataLoader(
        val_set, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=torch.cuda.is_available(),
    )

    classifier = StyleClassifier(num_styles=num_styles).to(device)
    optimizer = torch.optim.Adam(classifier.parameters(), lr=lr, betas=(0.5, 0.999))
    criterion = nn.CrossEntropyLoss()

    best_accuracy = 0.0
    best_state = None

    for epoch in range(1, epochs + 1):
        classifier.train()
        running = 0.0
        batches = 0
        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(classifier(images), labels)
            loss.backward()
            optimizer.step()
            running += float(loss.detach())
            batches += 1

        accuracy, entropy = entropy_on_loader(classifier, val_loader, device)
        log.info(
            "Epoca %2d/%d — loss %.4f | accuratezza val %.3f | entropia val %.3f nats",
            epoch, epochs, running / max(batches, 1), accuracy, entropy,
        )

        # Si tiene l'epoca migliore, non l'ultima: il giudice deve essere il piu'
        # attendibile possibile, e continuare ad addestrare oltre il massimo lo
        # peggiorerebbe per overfitting senza che se ne accorga nessuno.
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_state = {k: v.detach().cpu().clone() for k, v in classifier.state_dict().items()}

    if best_state is not None:
        classifier.load_state_dict(best_state)

    accuracy, entropy_real = entropy_on_loader(classifier, val_loader, device)
    max_entropy = math.log(num_styles)

    if accuracy < MIN_VAL_ACCURACY:
        log.warning(
            "Accuratezza di validazione %.3f sotto la soglia di %.2f. Il "
            "classificatore non e' un giudice affidabile: la sua incertezza sulle "
            "immagini generate rifletterebbe la propria debolezza piu' che "
            "l'ambiguita' stilistica. Aumenta le epoche o i dati prima di usarlo, "
            "oppure dichiara e giustifica la soglia piu' bassa in tesi.",
            accuracy, MIN_VAL_ACCURACY,
        )

    info = StyleClassifierInfo(
        num_styles=num_styles,
        classes=list(classes),
        val_accuracy=accuracy,
        train_size=len(train_set),
        val_size=len(val_set),
        epochs=epochs,
        seed=seed,
        entropy_real=entropy_real,
        entropy_real_normalized=entropy_real / max_entropy,
        max_entropy=max_entropy,
        commit=commit,
    )
    log.info(
        "Giudice pronto — accuratezza %.3f | entropia sui reali %.3f nats "
        "(normalizzata %.3f) | soffitto log(K) = %.3f",
        accuracy, entropy_real, info.entropy_real_normalized, max_entropy,
    )
    return classifier, info


# --------------------------------------------------------------------------- #
#  Persistenza
# --------------------------------------------------------------------------- #

def save_style_classifier(
    classifier: StyleClassifier,
    info: StyleClassifierInfo,
    directory: Path,
) -> tuple[Path, Path]:
    """Salva pesi e metadati. I due file vanno sempre insieme."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    weights_path = directory / _WEIGHTS
    tmp = weights_path.with_suffix(weights_path.suffix + ".tmp")
    torch.save({"state_dict": classifier.state_dict(), "num_styles": classifier.num_styles}, tmp)
    tmp.replace(weights_path)  # atomica, come i checkpoint del trainer

    metadata_path = directory / _METADATA
    metadata_path.write_text(
        json.dumps(info.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log.info("Classificatore salvato in %s", weights_path)
    return weights_path, metadata_path


def load_style_classifier(
    directory: Path,
    device: torch.device,
    expected_classes: list[str] | None = None,
) -> tuple[StyleClassifier, StyleClassifierInfo]:
    """Carica il giudice congelato.

    Se `expected_classes` e' fornito, verifica che coincida con le classi su cui il
    classificatore e' stato addestrato. Valutare un generatore addestrato su sei
    stili con un giudice addestrato su altri stili produrrebbe numeri privi di
    significato, e senza questo controllo il fallimento sarebbe silenzioso.
    """
    directory = Path(directory)
    weights_path = directory / _WEIGHTS
    metadata_path = directory / _METADATA

    if not weights_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"Classificatore di stile assente in {directory}. Addestralo con:\n"
            f"    python -m tesi_gan.cli train-style-classifier\n"
            f"Va addestrato una volta sola e poi riusato identico per tutti i run."
        )

    info = StyleClassifierInfo(**json.loads(metadata_path.read_text(encoding="utf-8")))

    if expected_classes is not None and list(expected_classes) != info.classes:
        raise RuntimeError(
            f"Il classificatore e' stato addestrato sulle classi {info.classes}, ma "
            f"il dataset corrente espone {list(expected_classes)}. Le entropie non "
            f"sarebbero confrontabili: riaddestra il giudice sul dataset corretto."
        )

    payload = torch.load(weights_path, map_location=device)
    classifier = StyleClassifier(num_styles=int(payload["num_styles"]))
    classifier.load_state_dict(payload["state_dict"])
    classifier.to(device).eval()

    # Il giudice non si addestra mai durante la valutazione.
    for parameter in classifier.parameters():
        parameter.requires_grad_(False)

    log.info(
        "Giudice caricato da %s — accuratezza dichiarata %.3f, entropia sui reali %.3f nats",
        weights_path, info.val_accuracy, info.entropy_real,
    )
    return classifier, info
