"""MEDIUM mock external claims API.

Difficulty profile (PLANNER §14 "Medium"): abbreviated field names, a US
``MM/DD/YY`` date format, coded enum values, and parties expressed as an array
of role-tagged objects rather than named ``claimant``/``insured`` keys. This
mirrors the realistic ``partyInfo`` pattern in the PLANNER persona example.

Mapping this shape requires: expanding abbreviations, parsing a non-ISO date,
translating status codes, and resolving parties by their ``roleCd``.

IMPORTANT (CHECKER §10): no ground-truth mapping is imported or exposed here.
"""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .seed_data import SEED_CLAIMS, SEED_CLAIMS_BY_ID, SeedClaim

API_TITLE = "Northstar Loss Service (medium)"
API_VERSION = "2.3.0"

# Canonical status name -> this API's status code.
_STATUS_CODE: dict[str, str] = {
    "OPEN": "OPN",
    "PENDING": "PND",
    "CLOSED": "CLS",
    "REOPENED": "RPN",
}


class MediumParty(BaseModel):
    """A party entry — abbreviated names, tagged with a role code."""

    roleCd: str = Field(description="Role code: CLMT (claimant) or INSD (insured).")
    firstNm: str
    lastNm: str
    partyRef: str


class MediumClaim(BaseModel):
    """Medium external claim shape: abbreviations, coded status, US dates."""

    lossNo: str = Field(description="Loss/claim number.")
    occDt: str = Field(description="Occurrence date, US format MM/DD/YY.")
    stateCd: str = Field(description="Status code (OPN/PND/CLS/RPN).")
    partyInfo: list[MediumParty] = Field(description="Parties with role codes.")
    polNum: str
    polEffDt: str
    polExpDt: str
    rsrvAmt: float | None = None
    pdAmt: float | None = None
    incurredAmt: float | None = None


def _fmt_us(d: date) -> str:
    """Format a date as MM/DD/YY (two-digit year)."""
    return d.strftime("%m/%d/%y")


def _money(value: object) -> float | None:
    """Render a Decimal seed amount as a float (this API uses JSON numbers).

    Note: emitting money as a float is deliberately *worse* than the easy
    API's decimal string — it reflects a real API that loses precision, which
    Crosswalk's profiler should notice.
    """
    return None if value is None else float(value)  # type: ignore[arg-type]


def serialize_medium(claim: SeedClaim) -> MediumClaim:
    """Project a neutral seed claim into the medium external shape."""
    return MediumClaim(
        lossNo=claim.claim_id,
        occDt=_fmt_us(claim.incident_date),
        stateCd=_STATUS_CODE[claim.status],
        partyInfo=[
            MediumParty(
                roleCd="CLMT",
                firstNm=claim.claimant.first_name,
                lastNm=claim.claimant.last_name,
                partyRef=claim.claimant.party_id,
            ),
            MediumParty(
                roleCd="INSD",
                firstNm=claim.insured.first_name,
                lastNm=claim.insured.last_name,
                partyRef=claim.insured.party_id,
            ),
        ],
        polNum=claim.policy_number,
        polEffDt=_fmt_us(claim.policy_effective_date),
        polExpDt=_fmt_us(claim.policy_expiration_date),
        rsrvAmt=_money(claim.reserve),
        pdAmt=_money(claim.payments),
        incurredAmt=_money(claim.total_incurred),
    )


def create_app() -> FastAPI:
    """Build the medium mock API application."""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Mock external loss service with abbreviated, coded fields.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/losses", response_model=list[MediumClaim], tags=["losses"])
    def list_losses() -> list[MediumClaim]:
        """Return every loss in the medium shape."""
        return [serialize_medium(c) for c in SEED_CLAIMS]

    @app.get("/losses/{loss_no}", response_model=MediumClaim, tags=["losses"])
    def get_loss(loss_no: str) -> MediumClaim:
        """Return a single loss by its loss number, or 404 if unknown."""
        claim = SEED_CLAIMS_BY_ID.get(loss_no)
        if claim is None:
            raise HTTPException(status_code=404, detail="loss not found")
        return serialize_medium(claim)

    return app


app = create_app()
