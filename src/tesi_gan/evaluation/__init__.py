"""Valutazione. Nessuna di queste metriche misura la creativita': vedi la nota
metodologica in `metrics.py` e Q5 nel registro delle decisioni."""

from tesi_gan.evaluation.metrics import EvaluationResult, evaluate, style_ambiguity

__all__ = ["EvaluationResult", "evaluate", "style_ambiguity"]
