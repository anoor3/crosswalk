#!/bin/sh
set -eu
.venv/bin/pytest tests/contract tests/integration -q
