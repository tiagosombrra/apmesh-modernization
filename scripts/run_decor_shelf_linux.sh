#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

rm -rf results/decor_shelf
mkdir -p results/decor_shelf
./build/bin/ap_mesh --config configs/decor_shelf/article.conf | tee results/decor_shelf/run.log
python3 scripts/verify_decor_shelf.py results/decor_shelf
