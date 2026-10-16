from crosswalk_multimodal import InputKind, MediaInput, enforce_size_limit


def test_multimodal_boundary_accepts_bounded_inputs() -> None:
    item = MediaInput(kind=InputKind.IMAGE, uri="local.png", media_type="image/png", byte_size=2)
    assert enforce_size_limit(item, 2).kind is InputKind.IMAGE
