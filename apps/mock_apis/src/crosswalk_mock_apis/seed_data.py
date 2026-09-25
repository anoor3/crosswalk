"""Shared seed data for the mock external APIs.

All three mock APIs (easy/medium/hard) serve the *same* underlying claims —
only the wire *shape* differs. Keeping the source data in one place guarantees
that a claim looks like the same business fact across every difficulty level,
which is exactly what a mapping benchmark needs.

This module is a neutral, framework-free representation of the seed facts. It
is intentionally **not** the canonical Pydantic model (that is Crosswalk's
internal target, which the mock APIs must not leak) and **not** any external
shape (that is applied per-API by the serializers). It is just the raw facts.

Determinism: the seed list is a fixed, ordered constant. No randomness, no
clock, no environment lookups — so every run and every test sees identical
data (CHECKER §11 reproducibility).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class SeedParty:
    """A person on a seed claim, in neutral terms."""

    first_name: str
    last_name: str
    party_id: str


@dataclass(frozen=True, slots=True)
class SeedClaim:
    """One claim's facts, independent of any external API shape.

    Every field here corresponds to a canonical concept; the per-API
    serializers rename/re-nest/re-encode these into their own shapes, and the
    hidden ground-truth files record exactly how.
    """

    claim_id: str
    incident_date: date
    status: str  # canonical status name: OPEN | PENDING | CLOSED | REOPENED
    claimant: SeedParty
    insured: SeedParty
    policy_number: str
    policy_effective_date: date
    policy_expiration_date: date
    reserve: Decimal | None = None
    payments: Decimal | None = None
    total_incurred: Decimal | None = None
    # Fields present but intentionally not part of the canonical model. They
    # exist so mapping has to decide what is relevant vs noise (PLANNER §25).
    extra_fields: dict[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# The fixed seed set. Ordered and deterministic.
# --------------------------------------------------------------------------- #
SEED_CLAIMS: tuple[SeedClaim, ...] = (
    SeedClaim(
        claim_id="C-100",
        incident_date=date(2026, 9, 4),
        status="OPEN",
        claimant=SeedParty("John", "Smith", "P-882"),
        insured=SeedParty("Acme", "Logistics", "P-501"),
        policy_number="POL-99122",
        policy_effective_date=date(2026, 1, 1),
        policy_expiration_date=date(2026, 12, 31),
        reserve=Decimal("10000.00"),
        payments=Decimal("4200.00"),
        total_incurred=Decimal("14200.00"),
        extra_fields={"source_system": "legacy-mainframe", "region": "NE"},
    ),
    SeedClaim(
        claim_id="C-101",
        incident_date=date(2026, 7, 15),
        status="PENDING",
        claimant=SeedParty("Maria", "Garcia", "P-883"),
        insured=SeedParty("Beacon", "Retail", "P-502"),
        policy_number="POL-99123",
        policy_effective_date=date(2026, 3, 1),
        policy_expiration_date=date(2027, 2, 28),
        reserve=Decimal("5000.00"),
        payments=Decimal("0.00"),
        total_incurred=Decimal("5000.00"),
        extra_fields={"source_system": "legacy-mainframe", "region": "SW"},
    ),
    SeedClaim(
        claim_id="C-102",
        incident_date=date(2026, 2, 28),
        status="CLOSED",
        claimant=SeedParty("Wei", "Chen", "P-884"),
        insured=SeedParty("Cedar", "Manufacturing", "P-503"),
        policy_number="POL-99124",
        policy_effective_date=date(2025, 6, 1),
        policy_expiration_date=date(2026, 5, 31),
        reserve=Decimal("0.00"),
        payments=Decimal("22750.50"),
        total_incurred=Decimal("22750.50"),
        extra_fields={"source_system": "legacy-mainframe", "region": "W"},
    ),
    SeedClaim(
        claim_id="C-103",
        incident_date=date(2026, 5, 9),
        status="REOPENED",
        claimant=SeedParty("Amara", "Okafor", "P-885"),
        insured=SeedParty("Delta", "Freight", "P-504"),
        policy_number="POL-99125",
        policy_effective_date=date(2026, 4, 1),
        policy_expiration_date=date(2027, 3, 31),
        reserve=Decimal("8000.00"),
        payments=Decimal("1500.00"),
        total_incurred=Decimal("9500.00"),
        extra_fields={"source_system": "legacy-mainframe", "region": "SE"},
    ),
)

# Index for O(1) lookup by claim id.
SEED_CLAIMS_BY_ID: dict[str, SeedClaim] = {c.claim_id: c for c in SEED_CLAIMS}
