"""Safe, bounded retrieval of a public OpenAPI document."""

from __future__ import annotations

import ipaddress
import json
import socket
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from crosswalk_security import UnsafeUrlError, validate_outbound_url


class RemoteImportError(ValueError):
    """Raised when a remote document cannot be safely imported."""


MAX_DOCUMENT_BYTES = 800_000
READ_TIMEOUT_SECONDS = 8


@dataclass(frozen=True)
class RemoteDocument:
    url: str
    document: dict[str, object]
    bytes_read: int
    content_type: str


def _public_addresses(hostname: str) -> tuple[str, ...]:
    try:
        addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except OSError as error:
        raise RemoteImportError("the document host could not be resolved") from error
    unique = tuple({str(item[4][0]) for item in addresses})
    if not unique:
        raise RemoteImportError("the document host has no address")
    for value in unique:
        try:
            address = ipaddress.ip_address(value)
        except ValueError as error:
            raise RemoteImportError("the document host returned an invalid address") from error
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        ):
            raise RemoteImportError("private or non-public addresses are blocked")
    return unique


def fetch_openapi(url: str) -> RemoteDocument:
    try:
        safe_url = validate_outbound_url(url)
    except UnsafeUrlError as error:
        raise RemoteImportError(str(error)) from error
    hostname = safe_url.split("//", 1)[1].split("/", 1)[0].split(":", 1)[0]
    _public_addresses(hostname)
    request = Request(  # noqa: S310 - scheme and destination were validated above
        safe_url,
        headers={
            "Accept": "application/json, application/yaml;q=0.5",
            "User-Agent": "Crosswalk/0.1",
        },
        method="GET",
    )
    opener = build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=READ_TIMEOUT_SECONDS) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {
                "application/json",
                "text/json",
                "application/yaml",
                "text/yaml",
            }:
                raise RemoteImportError("the URL did not return a JSON or YAML document")
            declared_length = response.headers.get("Content-Length")
            if declared_length is not None:
                try:
                    declared_bytes = int(declared_length)
                except ValueError as error:
                    raise RemoteImportError(
                        "the document server returned an invalid size"
                    ) from error
                if declared_bytes > MAX_DOCUMENT_BYTES:
                    raise RemoteImportError("the OpenAPI document is larger than 800 KB")
            chunks: list[bytes] = []
            total = 0
            while chunk := response.read(64 * 1024):
                total += len(chunk)
                if total > MAX_DOCUMENT_BYTES:
                    raise RemoteImportError("the OpenAPI document is larger than 800 KB")
                chunks.append(chunk)
    except RemoteImportError:
        raise
    except HTTPError as error:
        raise RemoteImportError(f"the document server returned HTTP {error.code}") from error
    except (OSError, URLError, TimeoutError) as error:
        raise RemoteImportError("the OpenAPI document could not be fetched") from error
    try:
        document = json.loads(b"".join(chunks))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RemoteImportError(
            "the document is not valid JSON; YAML is not yet supported"
        ) from error
    if not isinstance(document, dict):
        raise RemoteImportError("the OpenAPI document must be a JSON object")
    return RemoteDocument(safe_url, document, total, content_type)


class _NoRedirect(HTTPRedirectHandler):
    """Prevent a server from redirecting a public request into a private network."""

    def redirect_request(
        self, request: Request, fp: object, code: int, msg: str, headers: object, new_url: str
    ) -> None:
        raise RemoteImportError("redirects are blocked; provide the final public URL")
