"""Safe repair proposals; applying a proposal remains a human action."""

from .models import RepairProposal, RepairStatus, propose_replacement

__all__ = ["RepairProposal", "RepairStatus", "propose_replacement"]
