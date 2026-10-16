#!/usr/bin/env bash
set -euo pipefail
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DAP_MESH_USE_MPI=OFF -DAP_MESH_USE_OPENMP=OFF -DAP_MESH_ENABLE_LTO=OFF
cmake --build build --parallel
