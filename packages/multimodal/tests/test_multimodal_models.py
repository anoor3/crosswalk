import pytest
from crosswalk_multimodal import InputKind, MediaInput, TextSpan


def test_media_input_and_text_span_are_typed() -> None:
    media = MediaInput(
        kind=InputKind.PDF, uri="s3://bucket/doc.pdf", media_type="application/pdf", byte_size=10
    )
    span = TextSpan(text="claim number", page=1, confidence=0.9)
    assert media.kind is InputKind.PDF
    assert span.page == 1


def test_empty_uri_is_rejected() -> None:
    with pytest.raises(ValueError):
        MediaInput(kind=InputKind.IMAGE, uri="", media_type="image/png", byte_size=1)
