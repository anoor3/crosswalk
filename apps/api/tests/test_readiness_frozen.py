from dataclasses import FrozenInstanceError

import pytest
from crosswalk_api import Readiness


def test_readiness_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        Readiness().ready = False  # type: ignore[misc]
