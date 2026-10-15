import pytest
from crosswalk_multimodal import InputKind, MediaInput, enforce_size_limit


def test_media_size_limit_is_explicit() -> None:
    item = MediaInput(kind=InputKind.PDF, uri="doc", media_type="application/pdf", byte_size=11)
    assert enforce_size_limit(item, 11) == item
    with pytest.raises(ValueError, match="size limit"):
        enforce_size_limit(item, 10)
