"""Honest, deterministic evaluation of mapping candidates."""

from .scorer import EvaluationReport, evaluate_candidates

__all__ = ["EvaluationReport", "evaluate_candidates"]
