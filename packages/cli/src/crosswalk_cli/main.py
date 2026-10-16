from __future__ import annotations

import argparse

from crosswalk_contracts import HealthResponse


def format_health(response: HealthResponse) -> str:
    return f"{response.status} {response.version}"


def main() -> None:
    parser = argparse.ArgumentParser(prog="crosswalk-inspect")
    parser.add_argument("--version", default="development")
    args = parser.parse_args()
    print(format_health(HealthResponse(status="ok", version=args.version)))
