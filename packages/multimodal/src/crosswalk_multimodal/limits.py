from .models import MediaInput


def enforce_size_limit(item: MediaInput, max_bytes: int = 25_000_000) -> MediaInput:
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    if item.byte_size > max_bytes:
        raise ValueError("media input exceeds configured size limit")
    return item
