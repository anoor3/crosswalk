"""Crosswalk canonical data model.

This package defines the *canonical* (internal) representation that all
external APIs are mapped into. It is deliberately free of web, database, and
AI concerns so it can be safely imported anywhere in the system.

Public API::

    from crosswalk_canonical import Claim, Person, Policy, Financials, ClaimStatus
"""

from __future__ import annotations

from .enums import ClaimStatus
from .models import Claim, Financials, Person, Policy

__version__ = "0.1.0"

__all__ = [
    "Claim",
    "ClaimStatus",
    "Financials",
    "Person",
    "Policy",
    "__version__",
]
