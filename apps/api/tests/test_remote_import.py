from typing import Any

import pytest
from crosswalk_api.remote_import import RemoteImportError, fetch_openapi


def test_private_server_is_blocked_before_a_request() -> None:
    with pytest.raises(RemoteImportError, match=r"private|local|loopback"):
        fetch_openapi("http://127.0.0.1:8000/openapi.json")


@pytest.mark.parametrize(
    "url", ["file:///etc/passwd", "http://localhost:8000", "ftp://example.com/schema"]
)
def test_unsafe_schemes_and_hosts_are_rejected(url: str) -> None:
    with pytest.raises(RemoteImportError):
        fetch_openapi(url)


def test_public_hostname_is_resolved_and_fetched(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "crosswalk_api.remote_import._public_addresses", lambda _host: ("93.184.216.34",)
    )
    monkeypatch.setattr("crosswalk_api.remote_import.build_opener", lambda _handler: _FakeOpener())
    result = fetch_openapi("https://api.example.com/schema")
    assert result.document["openapi"] == "3.0.0"
    assert result.bytes_read > 0
    assert result.content_type == "application/json"


class _Headers:
    def get_content_type(self) -> str:
        return "application/json"

    def get(self, _key: str) -> str | None:
        return None


class _Response:
    headers = _Headers()

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_args: object) -> None:
        pass

    def read(self, size: int) -> bytes:
        del size
        if hasattr(self, "read_once"):
            return b""
        self.read_once = True
        return b'{"openapi":"3.0.0","paths":{}}'


class _FakeOpener:
    def open(self, _request: Any, timeout: int) -> _Response:
        assert timeout == 8
        return _Response()


def test_non_json_and_invalid_documents_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "crosswalk_api.remote_import._public_addresses", lambda _host: ("93.184.216.34",)
    )

    class BadResponse(_Response):
        headers = type("Headers", (), {"get_content_type": lambda _self: "text/html"})()

    class BadOpener(_FakeOpener):
        def open(self, _request: Any, timeout: int) -> BadResponse:
            del timeout
            return BadResponse()

    monkeypatch.setattr("crosswalk_api.remote_import.build_opener", lambda _handler: BadOpener())
    with pytest.raises(RemoteImportError, match="JSON or YAML"):
        fetch_openapi("https://api.example.com/schema")


def test_document_size_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "crosswalk_api.remote_import._public_addresses", lambda _host: ("93.184.216.34",)
    )

    class LargeResponse(_Response):
        headers = _Headers()

        def read(self, size: int) -> bytes:
            del size
            if hasattr(self, "read_once"):
                return b""
            self.read_once = True
            return b"{" + b"a" * 800_000

    class LargeOpener(_FakeOpener):
        def open(self, _request: Any, timeout: int) -> LargeResponse:
            del timeout
            return LargeResponse()

    monkeypatch.setattr("crosswalk_api.remote_import.build_opener", lambda _handler: LargeOpener())
    with pytest.raises(RemoteImportError, match="800 KB"):
        fetch_openapi("https://api.example.com/schema")


def test_declared_document_size_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "crosswalk_api.remote_import._public_addresses", lambda _host: ("93.184.216.34",)
    )

    class Headers(_Headers):
        def get(self, key: str) -> str | None:
            return "800001" if key == "Content-Length" else None

    class DeclaredLargeResponse(_Response):
        headers = Headers()

    class DeclaredLargeOpener(_FakeOpener):
        def open(self, _request: Any, timeout: int) -> DeclaredLargeResponse:
            del timeout
            return DeclaredLargeResponse()

    monkeypatch.setattr(
        "crosswalk_api.remote_import.build_opener", lambda _handler: DeclaredLargeOpener()
    )
    with pytest.raises(RemoteImportError, match="800 KB"):
        fetch_openapi("https://api.example.com/schema")
