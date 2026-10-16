#!/bin/sh
set -eu
find packages -name pyproject.toml -print | sort >/dev/null
