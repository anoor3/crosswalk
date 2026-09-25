"""Canonical enumerations.

These are the *canonical* (internal) enum values. External APIs express status
with their own codes (``"OPN"``, ``1``, ``"OPEN"``, ...); mapping those onto
these values is the job of the enum-mapping phase (PLANNER §19). This module
only defines the target vocabulary.
"""

from __future__ import annotations

from enum import StrEnum


class ClaimStatus(StrEnum):
    """Lifecycle status of a claim in the canonical model.

    Using :class:`enum.StrEnum` (Python 3.11+) means each member *is* its
    string value, so ``ClaimStatus.OPEN == "OPEN"`` and it serializes to
    ``"OPEN"`` in JSON — convenient for adapters and API responses while still
    giving us a closed, validated set of values.
    """

    OPEN = "OPEN"
    """Claim is active and being worked."""

    PENDING = "PENDING"
    """Claim is awaiting information or a decision before it can proceed."""

    CLOSED = "CLOSED"
    """Claim has been resolved and closed."""

    REOPENED = "REOPENED"
    """A previously closed claim that has been reopened."""
