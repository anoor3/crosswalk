from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


class UnsafeUrlError(ValueError):
    """Raised when a user-supplied URL is unsafe for outbound access."""


def validate_outbound_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeUrlError("only http and https URLs with a host are allowed")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("URLs with embedded credentials are blocked")
    if parsed.fragment:
        raise UnsafeUrlError("URL fragments are not sent to servers")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise UnsafeUrlError("local hosts are blocked")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and (address.is_private or address.is_loopback or address.is_link_local):
        raise UnsafeUrlError("private, loopback, and link-local addresses are blocked")
    return parsed.geturl()
