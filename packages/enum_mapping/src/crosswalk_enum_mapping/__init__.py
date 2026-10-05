"""Safe external enum mapping for Crosswalk Phase 6."""

from .engine import map_enum_values, translate_enum
from .errors import (
    EnumMappingError,
    InvalidEnumVocabularyError,
    UnapprovedEnumMappingError,
    UnknownEnumValueError,
)
from .models import EnumMappingResult, EnumMappingStatus, EnumValueCandidate

__version__ = "0.1.0"

__all__ = [
    "EnumMappingError",
    "EnumMappingResult",
    "EnumMappingStatus",
    "EnumValueCandidate",
    "InvalidEnumVocabularyError",
    "UnapprovedEnumMappingError",
    "UnknownEnumValueError",
    "__version__",
    "map_enum_values",
    "translate_enum",
]
