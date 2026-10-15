"""Credential-free adapter specifications and source generation."""

from .generator import generate_adapter
from .models import AdapterField, AdapterSpec

__all__ = ["AdapterField", "AdapterSpec", "generate_adapter"]
