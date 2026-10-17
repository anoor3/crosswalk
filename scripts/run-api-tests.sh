#!/bin/sh
set -eu
.venv/bin/pytest apps/api/tests -q
