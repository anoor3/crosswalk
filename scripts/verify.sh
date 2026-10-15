#!/bin/sh
set -eu

.venv/bin/ruff check .
.venv/bin/mypy packages
.venv/bin/pytest -q
