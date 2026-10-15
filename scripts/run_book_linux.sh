#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

rm -rf results/book
mkdir -p results/book
./build/bin/ap_mesh --config configs/book/article.conf | tee results/book/run.log
python3 scripts/verify_book.py results/book
