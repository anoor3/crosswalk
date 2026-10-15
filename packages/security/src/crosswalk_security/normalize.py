from urllib.parse import urlsplit, urlunsplit


def normalize_url(value: str) -> str:
    parts = urlsplit(value)
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))
