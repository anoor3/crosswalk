"""Crosswalk mock external APIs.

Three FastAPI applications — ``easy``, ``medium``, ``hard`` — that serve the
same seed claims (:mod:`crosswalk_mock_apis.seed_data`) in deliberately
different shapes. They stand in for unfamiliar customer APIs during discovery,
profiling, mapping, and drift development.

The correct mapping for each API is stored as *hidden ground truth* under
``fixtures/external_apis/<difficulty>/ground_truth.json`` and is deliberately
kept out of this package so it can never leak into the inference system
(CHECKER §10).

Serve one locally, e.g.::

    uvicorn crosswalk_mock_apis.easy:app --reload
"""

from __future__ import annotations

from .easy import app as easy_app
from .easy import create_app as create_easy_app
from .hard import app as hard_app
from .hard import create_app as create_hard_app
from .medium import app as medium_app
from .medium import create_app as create_medium_app

__version__ = "0.1.0"

__all__ = [
    "create_easy_app",
    "create_hard_app",
    "create_medium_app",
    "easy_app",
    "hard_app",
    "medium_app",
]
