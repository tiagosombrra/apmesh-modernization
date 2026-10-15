#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

./scripts/build_linux.sh
./scripts/run_book_linux.sh
./scripts/run_eistute_linux.sh
./scripts/run_decor_shelf_linux.sh

echo "All three article model runs completed successfully."
