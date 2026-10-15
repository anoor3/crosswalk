from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import cast


@dataclass(frozen=True)
class SyntheticApi:
    name: str
    seed: int
    schema: dict[str, object]
    records: tuple[dict[str, object], ...]


def generate_api(seed: int = 0, records: int = 10) -> SyntheticApi:
    """Generate stable claim-shaped data without network calls or secrets."""
    if records < 1 or records > 10_000:
        raise ValueError("records must be between 1 and 10000")
    rng = Random(seed)  # noqa: S311 - deterministic fixtures, never credentials
    rows = tuple(
        cast(
            dict[str, object],
            {
                "claim_id": f"clm_{seed}_{index}",
                "amount": round(rng.uniform(10, 1000), 2),
                "status": rng.choice(("open", "closed", "pending")),
            },
        )
        for index in range(records)
    )
    schema = cast(
        dict[str, object],
        {
            "type": "object",
            "properties": {
                "claim_id": {"type": "string"},
                "amount": {"type": "number"},
                "status": {"type": "string", "enum": ["open", "closed", "pending"]},
            },
        },
    )
    return SyntheticApi(name=f"synthetic_{seed}", seed=seed, schema=schema, records=rows)
