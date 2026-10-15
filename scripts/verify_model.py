#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

_STAGE_RE = re.compile(r"passo_(\d+)_malha_(\d+)\.obj$")


def fail(message: str) -> None:
    raise SystemExit(f"Verification failed: {message}")


def read_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def expected_final_stage(config_path: Path) -> int:
    values = read_config(config_path)
    raw_count = values.get("ADAPTIVE_MAX_ITERATIONS", values.get("ADAPTIVE_MAX_STEPS"))
    if raw_count is None:
        fail(f"missing ADAPTIVE_MAX_STEPS in {config_path}")
    try:
        count = int(raw_count)
    except ValueError:
        fail(f"invalid adaptive stage count in {config_path}: {raw_count}")
    if count < 1:
        fail(f"adaptive stage count must be positive in {config_path}")
    return count


def discover_stage_meshes(root: Path) -> list[tuple[int, Path]]:
    discovered: list[tuple[int, Path]] = []
    for path in root.rglob("*.obj"):
        match = _STAGE_RE.search(path.name)
        if match and match.group(1) == match.group(2):
            discovered.append((int(match.group(1)), path))
    return sorted(discovered, key=lambda item: (item[0], str(item[1])))


def count_triangles(mesh: Path) -> int:
    return sum(
        1
        for line in mesh.open(encoding="utf-8", errors="ignore")
        if line.startswith("f ")
    )


def verify_result(
    root: Path,
    label: str,
    config_path: Path,
    reference_json: Optional[Path] = None,
) -> None:
    if not root.is_dir():
        fail(f"result directory does not exist: {root}")

    final_stage = expected_final_stage(config_path)
    meshes = discover_stage_meshes(root)
    if not meshes:
        fail(f"no stage mesh was found under {root}")

    unexpected = [(stage, path) for stage, path in meshes if stage > final_stage]
    if unexpected:
        details = ", ".join(f"stage {stage}: {path}" for stage, path in unexpected)
        fail(f"stages beyond configured final stage {final_stage}: {details}")

    final_meshes = [path for stage, path in meshes if stage == final_stage]
    if not final_meshes:
        found = sorted({stage for stage, _ in meshes})
        fail(f"stage {final_stage} mesh was not found; available stages: {found}")

    mesh = final_meshes[-1]
    triangles = count_triangles(mesh)
    if triangles <= 0:
        fail(f"final mesh contains no triangular faces: {mesh}")

    if reference_json is not None:
        expected = json.loads(reference_json.read_text(encoding="utf-8"))
        if int(expected["stage"]) != final_stage:
            fail(
                f"reference stage {expected['stage']} differs from configured "
                f"stage {final_stage}"
            )
        if triangles != int(expected["triangles"]):
            fail(
                f"triangle count {triangles} differs from "
                f"reference {expected['triangles']}"
            )

    print(f"{label} final stage verified: {final_stage}")
    print(f"Mesh: {mesh}")
    print(f"Triangles: {triangles}")
