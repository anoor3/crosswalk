"""Canonical data models for Crosswalk.

The "clean internal world" that every external API is mapped *into*. These are
Pydantic v2 models so we get parsing, validation, and JSON (de)serialization
for free, and so that a generated adapter's final step — "produce a valid
canonical object" — is a single, enforceable call.

Design decisions
-----------------
* **Nested structure over a flat bag of fields.** ``Claim`` groups policy data
  under :class:`Policy` and money under :class:`Financials`. This keeps related
  concepts together and gives mappings clear dotted canonical paths
  (``claim.policy.policy_number``, ``claim.financials.total_incurred``).
* **Strict-ish validation.** Identifiers must be non-empty; unknown fields are
  rejected (``extra="forbid"``) so that a mapping bug surfaces loudly instead
  of silently dropping data. Models are frozen (immutable) because a canonical
  object is a *result* — downstream code should not mutate it in place.
* **Money is :class:`~decimal.Decimal`, never float.** Financial values must
  not accumulate binary floating-point error.
* **Dates are :class:`datetime.date`.** A claim's incident date is a calendar
  date, not a timestamp; keeping it a ``date`` avoids fake precision and
  timezone ambiguity. Date-*format* translation (e.g. ``"09/04/26"``) is the
  adapter/transform layer's job, not the canonical model's.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import ClaimStatus

# Shared configuration for every canonical model.
#   frozen        -> canonical objects are immutable results
#   extra=forbid  -> reject unexpected fields instead of silently ignoring them
#   str_strip_whitespace -> normalize incidental whitespace on string inputs
_CANONICAL_CONFIG = ConfigDict(
    frozen=True,
    extra="forbid",
    str_strip_whitespace=True,
)


class Person(BaseModel):
    """A person involved in a claim (claimant or insured)."""

    model_config = _CANONICAL_CONFIG

    first_name: str = Field(..., min_length=1, description="Given name.")
    last_name: str = Field(..., min_length=1, description="Family name.")
    person_id: str | None = Field(
        default=None,
        description="Stable external identifier for the person, if the source "
        "API exposes one (used for cross-endpoint relationship resolution).",
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        """Reject names that are empty or whitespace-only.

        ``min_length=1`` combined with ``str_strip_whitespace`` rejects ``""``
        but a value of ``" "`` is stripped to ``""`` *before* length checking
        in Pydantic v2, so this validator makes the intent explicit and guards
        against future config changes.
        """
        if not value.strip():
            raise ValueError("name must not be blank")
        return value


class Policy(BaseModel):
    """The insurance policy a claim is filed against."""

    model_config = _CANONICAL_CONFIG

    policy_number: str = Field(
        ..., min_length=1, description="Human-readable policy identifier."
    )
    effective_date: date | None = Field(
        default=None, description="Date the policy coverage begins."
    )
    expiration_date: date | None = Field(
        default=None, description="Date the policy coverage ends."
    )

    @field_validator("policy_number")
    @classmethod
    def _policy_number_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("policy_number must not be blank")
        return value


class Financials(BaseModel):
    """Monetary figures attached to a claim.

    All fields are optional because a source API may not expose every figure,
    and Crosswalk must never invent a value it did not observe. Money uses
    :class:`~decimal.Decimal`; non-negativity is enforced because reserves,
    payments, and incurred totals are not meaningfully negative in this model.
    """

    model_config = _CANONICAL_CONFIG

    reserve: Decimal | None = Field(
        default=None, ge=0, description="Money set aside to pay the claim."
    )
    payments: Decimal | None = Field(
        default=None, ge=0, description="Money already paid out on the claim."
    )
    total_incurred: Decimal | None = Field(
        default=None,
        ge=0,
        description="Total cost incurred (typically payments + outstanding reserve).",
    )


class Claim(BaseModel):
    """A claim, expressed in Crosswalk's canonical model.

    This is the top-level target that adapters produce and that mapping
    accuracy is measured against.
    """

    model_config = _CANONICAL_CONFIG

    claim_id: str = Field(
        ..., min_length=1, description="Unique identifier for the claim."
    )
    incident_date: date = Field(
        ..., description="Calendar date the underlying incident occurred."
    )
    status: ClaimStatus = Field(..., description="Canonical lifecycle status.")
    claimant: Person = Field(..., description="The party making the claim.")
    insured: Person = Field(..., description="The party covered by the policy.")
    policy: Policy = Field(..., description="The policy the claim is filed against.")
    financials: Financials = Field(
        default_factory=Financials,
        description="Monetary figures; defaults to an all-null Financials when "
        "the source exposes no money data.",
    )

    @field_validator("claim_id")
    @classmethod
    def _claim_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("claim_id must not be blank")
        return value
