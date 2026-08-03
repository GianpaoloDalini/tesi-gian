"""Valutazione. Nessuna di queste metriche misura la creativita': vedi la nota
metodologica in `metrics.py` e Q5 nel registro delle decisioni."""

from tesi_gan.evaluation.metrics import EvaluationResult, evaluate, style_ambiguity
from tesi_gan.evaluation.style_classifier import (
    StyleClassifier,
    StyleClassifierInfo,
    entropy_on_generator,
    load_style_classifier,
    save_style_classifier,
    train_style_classifier,
)

__all__ = [
    "EvaluationResult",
    "evaluate",
    "style_ambiguity",
    "StyleClassifier",
    "StyleClassifierInfo",
    "entropy_on_generator",
    "load_style_classifier",
    "save_style_classifier",
    "train_style_classifier",
]
