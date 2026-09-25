"""EASY mock external claims API.

Difficulty profile (PLANNER §14 "Easy"): obvious field names, flat-ish
structure, ISO-8601 dates, and clean human-readable status strings. This is
the friendliest shape a real customer API might take.

The response models are Pydantic so FastAPI generates an accurate OpenAPI
document — which is the input Crosswalk's discovery phase will consume.

IMPORTANT (CHECKER §10): this module never imports or exposes the hidden
ground-truth mapping. It only knows how to *shape* the seed data.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .seed_data import SEED_CLAIMS, SEED_CLAIMS_BY_ID, SeedClaim

API_TITLE = "Acme Claims API (easy)"
API_VERSION = "1.0.0"


class EasyParty(BaseModel):
    """A person in the easy shape — clear, spelled-out names."""

    firstName: str
    lastName: str
    partyId: str


class EasyClaim(BaseModel):
    """Easy external claim shape: obvious names, ISO dates, string status."""

    claimNumber: str = Field(description="Claim identifier.")
    dateOfLoss: str = Field(description="Incident date, ISO-8601 (YYYY-MM-DD).")
    status: str = Field(description="Claim status: OPEN, PENDING, CLOSED, REOPENED.")
    claimant: EasyParty
    insured: EasyParty
    policyNumber: str
    policyEffectiveDate: str
    policyExpirationDate: str
    reserveAmount: str | None = None
    paidAmount: str | None = None
    totalIncurred: str | None = None


def _money(value: object) -> str | None:
    """Render a Decimal seed amount as a plain decimal string (or None)."""
    return None if value is None else str(value)


def serialize_easy(claim: SeedClaim) -> EasyClaim:
    """Project a neutral seed claim into the easy external shape."""
    return EasyClaim(
        claimNumber=claim.claim_id,
        dateOfLoss=claim.incident_date.isoformat(),  # 2026-09-04
        status=claim.status,  # already OPEN/PENDING/CLOSED/REOPENED
        claimant=EasyParty(
            firstName=claim.claimant.first_name,
            lastName=claim.claimant.last_name,
            partyId=claim.claimant.party_id,
        ),
        insured=EasyParty(
            firstName=claim.insured.first_name,
            lastName=claim.insured.last_name,
            partyId=claim.insured.party_id,
        ),
        policyNumber=claim.policy_number,
        policyEffectiveDate=claim.policy_effective_date.isoformat(),
        policyExpirationDate=claim.policy_expiration_date.isoformat(),
        reserveAmount=_money(claim.reserve),
        paidAmount=_money(claim.payments),
        totalIncurred=_money(claim.total_incurred),
    )


def create_app() -> FastAPI:
    """Build the easy mock API application."""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Mock external claims API with an easy-to-map shape.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/claims", response_model=list[EasyClaim], tags=["claims"])
    def list_claims() -> list[EasyClaim]:
        """Return every claim in the easy shape."""
        return [serialize_easy(c) for c in SEED_CLAIMS]

    @app.get("/claims/{claim_number}", response_model=EasyClaim, tags=["claims"])
    def get_claim(claim_number: str) -> EasyClaim:
        """Return a single claim by its claim number, or 404 if unknown."""
        claim = SEED_CLAIMS_BY_ID.get(claim_number)
        if claim is None:
            raise HTTPException(status_code=404, detail="claim not found")
        return serialize_easy(claim)

    return app


app = create_app()
