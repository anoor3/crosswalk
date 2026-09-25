"""Crosswalk canonical data model.

This package defines the *canonical* (internal) representation that all
external APIs are mapped into. It is deliberately free of web, database, and
AI concerns so it can be safely imported anywhere in the system.

The concrete models (``Claim``, ``Person``, ``Policy``, ``Financials``) are
added in Phase 1a.
"""

__version__ = "0.1.0"
