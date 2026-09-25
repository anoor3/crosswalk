"""HARD mock external claims API.

Difficulty profile (PLANNER §14 "Hard"): deeply nested structure, a slashed
``YYYY/MM/DD`` date buried inside a sub-object, numeric status codes, and
misleading-sounding keys. Money is nested under a ``ledger`` object with terse
keys. Parties live under ``involved`` with numeric role types.

Mapping this shape requires: walking nested paths, parsing yet another date
format, translating *numeric* status codes, and disambiguating terse keys.

IMPORTANT (CHECKER §10): no ground-truth mapping is imported or exposed here.
"""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .seed_data import SEED_CLAIMS, SEED_CLAIMS_BY_ID, SeedClaim

API_TITLE = "LegacyCore Case Endpoint (hard)"
API_VERSION = "0.9.7"

# Canonical status name -> this API's numeric state code.
_STATE_CODE: dict[str, int] = {
    "OPEN": 1,
    "PENDING": 2,
    "CLOSED": 3,
    "REOPENED": 4,
}


class HardIncident(BaseModel):
    """Nested incident block holding the slashed-format date."""

    occurred_at: str = Field(description="Incident date, slashed YYYY/MM/DD.")


class HardParty(BaseModel):
    """A nested involved-party with a numeric role type."""

    id: str
    given: str
    family: str
    roleType: int = Field(description="1 = claimant, 2 = insured.")


class HardLedger(BaseModel):
    """Terse money block; values as strings to avoid float precision loss."""

    rsv: str | None = None
    pd: str | None = None
    inc: str | None = None


class HardCoverage(BaseModel):
    """Nested policy/coverage block."""

    num: str
    effFrom: str
    effTo: str


class HardCase(BaseModel):
    """The nested case object — the real payload lives here."""

    ref: str = Field(description="Case/claim reference.")
    incident: HardIncident
    state: int = Field(description="Numeric status code (1/2/3/4).")
    involved: list[HardParty]
    coverage: HardCoverage
    ledger: HardLedger


class HardEnvelope(BaseModel):
    """Top-level envelope; everything of interest is under ``case``."""

    case: HardCase


def _fmt_slashed(d: date) -> str:
    """Format a date as YYYY/MM/DD."""
    return d.strftime("%Y/%m/%d")


def _money(value: object) -> str | None:
    return None if value is None else str(value)


def serialize_hard(claim: SeedClaim) -> HardEnvelope:
    """Project a neutral seed claim into the hard external shape."""
    return HardEnvelope(
        case=HardCase(
            ref=claim.claim_id,
            incident=HardIncident(occurred_at=_fmt_slashed(claim.incident_date)),
            state=_STATE_CODE[claim.status],
            involved=[
                HardParty(
                    id=claim.claimant.party_id,
                    given=claim.claimant.first_name,
                    family=claim.claimant.last_name,
                    roleType=1,
                ),
                HardParty(
                    id=claim.insured.party_id,
                    given=claim.insured.first_name,
                    family=claim.insured.last_name,
                    roleType=2,
                ),
            ],
            coverage=HardCoverage(
                num=claim.policy_number,
                effFrom=_fmt_slashed(claim.policy_effective_date),
                effTo=_fmt_slashed(claim.policy_expiration_date),
            ),
            ledger=HardLedger(
                rsv=_money(claim.reserve),
                pd=_money(claim.payments),
                inc=_money(claim.total_incurred),
            ),
        )
    )


def create_app() -> FastAPI:
    """Build the hard mock API application."""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Mock legacy case endpoint with deep nesting and numeric codes.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/cases", response_model=list[HardEnvelope], tags=["cases"])
    def list_cases() -> list[HardEnvelope]:
        """Return every case in the hard shape."""
        return [serialize_hard(c) for c in SEED_CLAIMS]

    @app.get("/cases/{ref}", response_model=HardEnvelope, tags=["cases"])
    def get_case(ref: str) -> HardEnvelope:
        """Return a single case by reference, or 404 if unknown."""
        claim = SEED_CLAIMS_BY_ID.get(ref)
        if claim is None:
            raise HTTPException(status_code=404, detail="case not found")
        return serialize_hard(claim)

    return app


app = create_app()
