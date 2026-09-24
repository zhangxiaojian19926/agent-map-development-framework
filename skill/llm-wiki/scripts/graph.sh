#!/usr/bin/env bash
# Portable public-framework helper. See ../SKILL.md for authorization and completion boundaries.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/wiki.py" graph "$@"
