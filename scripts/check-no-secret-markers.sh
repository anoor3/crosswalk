#!/bin/sh
set -eu
if rg -n '(AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH) PRIVATE KEY|password=[^" ]+)' packages deploy scripts --glob '!check-no-secret-markers.sh'; then
  echo "credential-shaped marker found" >&2
  exit 1
fi
