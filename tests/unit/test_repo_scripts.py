from pathlib import Path


def test_verification_script_is_present() -> None:
    assert Path("scripts/verify.sh").is_file()
    assert Path("scripts/check-no-secret-markers.sh").is_file()
