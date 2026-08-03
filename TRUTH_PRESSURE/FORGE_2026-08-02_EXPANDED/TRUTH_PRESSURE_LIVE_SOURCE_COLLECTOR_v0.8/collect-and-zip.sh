#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

node "$SCRIPT_DIR/collect-truth-pressure-live-source.mjs" "$REPO_PATH"

cd "$REPO_PATH"
rm -f truth-pressure-live-source-extract.zip
zip -r truth-pressure-live-source-extract.zip _truth-pressure-live-source-extract >/dev/null

echo
echo "Created:"
echo "  $(pwd)/truth-pressure-live-source-extract.zip"
