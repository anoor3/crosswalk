#!/bin/sh
set -eu
find docs -maxdepth 1 -iname '*PHASE*' -print | sort
