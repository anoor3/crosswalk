import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from crosswalk_api import create_app
from fastapi.testclient import TestClient


def plan() -> dict[str, Any]:
    return {
        "records": [
            {"ref": "A", "policy": {"id": "P1"}, "cents": 125050, "date": "10/04/2026"},
            {"ref": "B", "policy": {"id": "P2"}, "cents": 0, "date": "02/29/2024"},
        ],
        "target": {"id": "A", "insurance": {"policy": "P1"}, "paid": 1250.5, "date": "2026-10-04"},
        "rules": [
            {"source": source, "target": target, "operation": operation, "reviewed": True}
            for source, target, operation in [
                ("/ref", "/id", "copy"),
                ("/policy/id", "/insurance/policy", "copy"),
                ("/cents", "/paid", "cents_to_dollars"),
                ("/date", "/date", "date_us"),
            ]
        ],
    }


def test_preview_and_downloaded_adapter_have_identical_results(tmp_path: Path) -> None:
    request = plan()
    with TestClient(create_app()) as client:
        response = client.post("/workbench/conversion/preview", json=request)
        assert response.status_code == 200
        result = response.json()
        assert result["valid"] == 2
        assert result["output"][0] == request["target"]
        assert result["output"][1]["date"] == "2024-02-29"
        exported = client.post("/workbench/conversion/export", json=request)
        assert exported.status_code == 200
    adapter = tmp_path / "adapter.py"
    adapter.write_text(exported.json()["code"])
    process = subprocess.run(  # noqa: S603 -- execute our generated artifact to verify export parity
        [sys.executable, str(adapter)],
        input=json.dumps(request["records"]),
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout) == result["output"]
    request["records"][0]["date"] = "02/30/2026"
    process = subprocess.run(  # noqa: S603
        [sys.executable, str(adapter)],
        input=json.dumps(request["records"]),
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert process.returncode == 1
    assert process.stdout == ""
    assert "Expected a valid date" in process.stderr


@pytest.mark.parametrize("bad_value", ["not money", True, 2.5, None, "Infinity", "1e9999999"])
def test_invalid_money_is_reported_and_blocks_export(bad_value: Any) -> None:
    request = plan()
    request["records"][0]["cents"] = bad_value
    with TestClient(create_app()) as client:
        response = client.post("/workbench/conversion/preview", json=request)
        assert response.status_code == 200
        result = response.json()
        assert result["invalid"] == 1
        assert result["valid"] == 1
        assert result["rows"][0]["errors"][0]["target"] == "/paid"
        assert client.post("/workbench/conversion/export", json=request).status_code == 422


def test_missing_optional_and_required_fields_are_distinct() -> None:
    request = plan()
    del request["records"][1]["policy"]
    with TestClient(create_app()) as client:
        result = client.post("/workbench/conversion/preview", json=request).json()
        assert result["invalid"] == 1
        request["rules"][1]["required"] = False
        result = client.post("/workbench/conversion/preview", json=request).json()
        assert result["invalid"] == 0
        assert "insurance" not in result["output"][1]


@pytest.mark.parametrize("change", ["unreviewed", "duplicate", "missing", "unknown", "wrong_type"])
def test_invalid_plans_cannot_run(change: str) -> None:
    request = plan()
    if change == "unreviewed":
        request["rules"][0]["reviewed"] = False
    elif change == "duplicate":
        request["rules"].append(request["rules"][0])
    elif change == "missing":
        request["rules"].pop()
    elif change == "unknown":
        request["rules"][0]["source"] = "/nonexistent"
    else:
        request["rules"][2]["operation"] = "copy"
        request["records"][0]["cents"] = "125050"
    with TestClient(create_app()) as client:
        response = client.post("/workbench/conversion/preview", json=request)
        if change == "wrong_type":
            assert response.json()["invalid"] == 1
        else:
            assert response.status_code == 422


def test_suggestions_do_not_guess_ambiguous_leaf_names() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/workbench/conversion/suggest",
            json={
                "records": [{"a": {"id": "A"}, "b": {"id": "B"}, "claimId": "C"}],
                "target": {"id": "A", "claim_id": "C"},
            },
        )
        rules = response.json()["rules"]
        assert rules[0]["source"] == ""
        assert rules[1]["source"] == "/claimId"
        assert not any(rule["reviewed"] for rule in rules)


def test_pointer_escaping_and_code_like_keys_are_only_data(tmp_path: Path) -> None:
    key = "'); __import__('os').system('false'); #"
    request = {
        "records": [{"a/b": {"~key": "safe"}}],
        "target": {key: "safe"},
        "rules": [
            {"source": "/a~1b/~0key", "target": "/" + key, "operation": "copy", "reviewed": True}
        ],
    }
    with TestClient(create_app()) as client:
        assert client.post("/workbench/conversion/preview", json=request).json()["output"] == [
            {key: "safe"}
        ]
        code = client.post("/workbench/conversion/export", json=request).json()["code"]
    adapter = tmp_path / "adapter.py"
    adapter.write_text(code)
    process = subprocess.run(  # noqa: S603
        [sys.executable, str(adapter)],
        input=json.dumps(request["records"]),
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert process.returncode == 0
    assert json.loads(process.stdout) == [{key: "safe"}]


def test_large_numeric_ids_are_rejected_instead_of_rounded() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/workbench/conversion/suggest",
            json={
                "records": [{"id": 9007199254740993}],
                "target": {"id": "example"},
            },
        )
        assert response.status_code == 422


def test_arrays_are_copied_whole_and_omissions_are_explicit() -> None:
    request = {
        "records": [{"items": [{"id": 1}], "unused": "value"}],
        "target": {"entries": [], "note": "example"},
        "rules": [
            {"source": "/items", "target": "/entries", "operation": "copy", "reviewed": True},
            {"source": "", "target": "/note", "operation": "omit", "reviewed": True},
        ],
    }
    with TestClient(create_app()) as client:
        result = client.post("/workbench/conversion/preview", json=request).json()
        assert result["output"] == [{"entries": [{"id": 1}]}]


@pytest.mark.parametrize("target", [{}, {"id": None}])
def test_target_needs_concrete_example_values(target: dict[str, Any]) -> None:
    with TestClient(create_app()) as client:
        assert (
            client.post(
                "/workbench/conversion/suggest",
                json={
                    "records": [{"id": "A"}],
                    "target": target,
                },
            ).status_code
            == 422
        )
