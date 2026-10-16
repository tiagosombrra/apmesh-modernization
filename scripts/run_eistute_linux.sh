#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

rm -rf results/eistute
mkdir -p results/eistute
./build/bin/ap_mesh --config configs/eistute/article.conf | tee results/eistute/run.log
python3 scripts/verify_eistute.py results/eistute
