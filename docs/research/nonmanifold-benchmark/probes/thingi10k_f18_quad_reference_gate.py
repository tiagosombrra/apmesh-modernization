#!/usr/bin/env python3
"""Reproduce conservative QuadWild reference identity and topology gates.

This script intentionally does not download, repair, convert or redistribute meshes.
Published (V, F) counts alone cannot establish the topology of a QUAD output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import zipfile
from collections import Counter, defaultdict, deque
from pathlib import Path

MAX_BYTES = 250_000_000
MAX_VERTICES = 6_000_000
MAX_FACES = 6_000_000


def published_rows(path: Path) -> dict[int, dict]:
    """Keep literature IDs and published QUAD counts distinct from STL counts."""
    required = {"thingi10k_file_id", "literature_cohort", "published_quad_vertices", "published_quad_faces"}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Published roster lacks the mandatory columns")
        rows: dict[int, dict] = {}
        for row in reader:
            if row["literature_cohort"] != "QUADWILD_FIG29":
                continue
            file_id = int(row["thingi10k_file_id"])
            if file_id in rows:
                raise ValueError("Duplicate published QUAD file ID")
            v, f = int(row["published_quad_vertices"]), int(row["published_quad_faces"])
            if v <= 0 or f <= 0 or v > MAX_VERTICES or f > MAX_FACES:
                raise ValueError("Invalid or implausibly large published QUAD count")
            rows[file_id] = {"file_id": file_id, "published_vertices": v, "published_faces": f}
        if len(rows) != 12:
            raise ValueError("Expected exactly twelve frozen QuadWild cases")
    return rows


def conditional_euler(v: int, f: int) -> dict:
    """Only a *hypothetical* closed pure-quad genus follows from V and F."""
    chi = v - f
    numerator = 2 - chi
    g = numerator // 2 if numerator % 2 == 0 and numerator >= 0 else None
    return {
        "hypothetical_closed_quad_euler": chi,
        "hypothetical_closed_connected_orientable_genus": g,
        "closed_connected_orientable_possible_by_counts": g is not None,
        "verified_quad_topology": False,
    }


def normalize_source_catalog(row: dict) -> dict:
    """Identify a source whose metadata flags are consistent with a clean surface."""
    expected = {"closed", "edge_manifold", "vertex_manifold", "single_component", "pwn"}
    if not expected.issubset(row):
        raise ValueError("Source catalog lacks required flags")
    clean = all(row[k] is True for k in expected) and (
        row.get("degenerate_faces") is False and row.get("duplicated_faces") is False
    )
    n_vertices = row.get("vertices")
    n_triangles = row.get("faces")
    if not isinstance(n_vertices, int) or not isinstance(n_triangles, int) or n_vertices <= 0 or n_triangles <= 0:
        raise ValueError("Invalid source catalog V/F counts")
    source_chi = None
    source_genus = None
    if clean and n_triangles % 2 == 0:
        source_chi = n_vertices - n_triangles // 2
        if (2 - source_chi) >= 0 and (2 - source_chi) % 2 == 0:
            source_genus = (2 - source_chi) // 2
    return {"catalog_flags_clean": clean, "catalog_vertices": n_vertices,
            "catalog_triangles": n_triangles, "conditional_source_euler": source_chi,
            "conditional_source_genus": source_genus,
            "source_topology_independently_verified": False}


def build_published_comparison(roster: dict[int, dict], catalog_subset: list[dict],
                               raw_audit: dict | None = None) -> dict:
    """Match source-vs-reference necessary Euler invariants without false admission."""
    catalog = {int(x["id"]): x for x in catalog_subset}
    if len(catalog) != len(catalog_subset) or len(catalog) != 12 or set(catalog) != set(roster):
        raise ValueError("Catalog subset must match all twelve QuadWild file IDs")
    audits = {}
    if raw_audit is not None:
        audits = {int(x["thingi10k_file_id"]): x for x in raw_audit.get("raw_stl_audits", [])}
        if len(audits) != len(raw_audit.get("raw_stl_audits", [])):
            raise ValueError("Duplicate raw audit ID")
        if not set(audits).issubset(set(roster) | {293137, 37881, 47076, 550964, 96457}):
            raise ValueError("Unexpected raw-audit source ID")
    result = []
    for file_id, pub in roster.items():
        c = normalize_source_catalog(catalog[file_id])
        out = conditional_euler(pub["published_vertices"], pub["published_faces"])
        raw = audits.get(file_id)
        raw_euler = None
        raw_valid = False
        if raw:
            t = raw.get("topology", {})
            digest = raw.get("raw_stl_sha256", "")
            if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("Raw source audit lacks a byte-pinned SHA-256")
            if t["source_triangles"] != c["catalog_triangles"]:
                raise ValueError("Actual STL triangle count conflicts with source catalog")
            raw_euler = t["source_unique_exact_vertices"] - t["source_unique_exact_edges"] + t["source_triangles"]
            raw_valid = (
                t["boundary_edges"] == 0 and t["three_plus_edges"] == 0 and
                t["vertex_link_singular"] == 0 and t["vertex_connected_components"] == 1 and
                t["zero_area_triangles"] == 0 and t["raw_duplicate_triangles"] == 0 and
                t["edge_winding_conflicts"] == 0
            )
        # A failing byte-audited source must never be 'rescued' by its catalog flags.
        source_chi = raw_euler if raw_valid else (None if raw is not None else c["conditional_source_euler"])
        matches = source_chi is not None and out["closed_connected_orientable_possible_by_counts"] and (
            source_chi == out["hypothetical_closed_quad_euler"]
        )
        result.append({"file_id": file_id, **pub, **out,
                       "catalog_flags_clean": c["catalog_flags_clean"],
                       "source_euler": source_chi,
                       "source_euler_evidence": "AUDITED_EXACT_COORDINATE_STL" if raw_valid else
                       "AUDITED_SOURCE_CONTRADICTS_MANIFOLD_CONTRACT" if raw is not None else
                       "CONDITIONAL_CATALOG_TRIANGLE_MANIFOLD" if c["catalog_flags_clean"] else "NOT_ESTABLISHED",
                       "published_output_euler_compatible_with_source": bool(matches),
                       "quad_output_raw_file_checked": False,
                       "quad_input_output_pair_hash_verified": False})
    return {
        "schema": "apmesh-thingi10k-f18-published-quad-euler-v1",
        "status": "PUBLISHED_QUAD_COUNTS_ONLY_NO_OUTPUT_FILE_INSPECTION",
        "quadwild_paper": "Pietroni_et_al_2021_SIGGRAPH_FIG29_TABLE1",
        "source_manifest_count": len(result),
        "published_euler_possible_under_strict_closed_orientable_assumptions": sum(
            r["closed_connected_orientable_possible_by_counts"] for r in result),
        "source_vs_published_euler_conditional_matches": sum(
            r["published_output_euler_compatible_with_source"] for r in result),
        "original_stl_audited_and_source_euler_match_count": sum(
            r["published_output_euler_compatible_with_source"] and
            r["source_euler_evidence"] == "AUDITED_EXACT_COORDINATE_STL" for r in result),
        "actual_quad_outputs_read": 0,
        "actual_apmesh_generated_meshes": 0,
        "cases": result,
    }


def parse_obj_quad(path: Path) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    """Parse a bounded indexed OBJ pure-quad mesh without coordinate welding."""
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing, empty or oversized reference OBJ")
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    with path.open("r", encoding="utf-8", errors="strict") as stream:
        for line in stream:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            chunks = line.split()
            if chunks[0] == "v":
                if len(chunks) < 4:
                    raise ValueError("Malformed OBJ vertex")
                coords = tuple(float(s) for s in chunks[1:4])
                if not all(map(math.isfinite, coords)):
                    raise ValueError("Nonfinite OBJ coordinates")
                vertices.append(coords)
                if len(vertices) > MAX_VERTICES:
                    raise ValueError("Too many OBJ vertices")
            elif chunks[0] == "f":
                if len(chunks) != 5:
                    raise ValueError("Not a pure-quad OBJ face")
                idx = []
                for cell in chunks[1:]:
                    label = cell.split("/", 1)[0]
                    if not label or label.startswith("+"):
                        raise ValueError("Unsupported OBJ vertex reference")
                    value = int(label)
                    if value == 0:
                        raise ValueError("OBJ vertex zero not allowed")
                    # Interpret standard negative OBJ indices relative to preceding vertices.
                    k = value - 1 if value > 0 else len(vertices) + value
                    if not 0 <= k < len(vertices):
                        raise ValueError("OBJ references a missing or future vertex")
                    idx.append(k)
                faces.append(tuple(idx))
                if len(faces) > MAX_FACES:
                    raise ValueError("Too many OBJ faces")
            elif chunks[0] in ("vt", "vn", "o", "g", "s", "usemtl", "mtllib", "l"):
                continue
            else:
                raise ValueError("Unsupported OBJ directive: " + chunks[0])
    return vertices, faces


def read_quad_npz(path: Path):
    """Load NPZ arrays only with pickle disabled; fail if schema is unfamiliar."""
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized NPZ")
    try:
        import numpy as np
    except ImportError as exc:
        raise ValueError("NumPy required to inspect NPZ output") from exc
    # Preflight the archive to avoid decompressing oversized or unfamiliar arrays.
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > 16 or sum(i.file_size for i in members) > MAX_BYTES * 3:
            raise ValueError("Unbounded or unfamiliar NPZ archive")
        if any(i.flag_bits & 1 or i.is_dir() or i.file_size > MAX_BYTES * 2
               or not i.filename.endswith(".npy") or "/" in i.filename
               or "\\" in i.filename for i in members):
            raise ValueError("Unsafe NPZ ZIP archive structure")
    with np.load(path, allow_pickle=False) as data:
        if not {"vertices", "faces"}.issubset(set(data.files)):
            raise ValueError("Unknown NPZ schema; expected vertices and faces arrays")
        v, f = data["vertices"], data["faces"]
        if v.ndim != 2 or v.shape[1] != 3 or f.ndim != 2 or f.shape[1] != 4:
            raise ValueError("NPZ is not an indexed pure-quad surface")
        if v.shape[0] > MAX_VERTICES or f.shape[0] > MAX_FACES or v.shape[0] == 0 or f.shape[0] == 0:
            raise ValueError("Invalid NPZ dimensions")
        if v.dtype.kind not in ("f", "i", "u") or f.dtype.kind not in ("i", "u"):
            raise ValueError("Unsupported NPZ numeric dtypes")
        if not np.isfinite(v).all() or (f < 0).any() or (f >= v.shape[0]).any():
            raise ValueError("Invalid NPZ indices or coordinates")
        return [tuple(map(float, x)) for x in v], [tuple(map(int, x)) for x in f]


def audit_quad_index_topology(vertices, faces) -> dict:
    """Determine actual quad incidence, face components, vertex-link validity and Euler."""
    if not vertices or not faces or len(vertices) > MAX_VERTICES or len(faces) > MAX_FACES:
        raise ValueError("Missing or oversized QUAD topology")
    if any(len(v) != 3 or not all(math.isfinite(float(x)) for x in v) for v in vertices):
        raise ValueError("Invalid 3D vertex")
    edges = defaultdict(list)
    link = defaultdict(list)
    face_by_vertex = defaultdict(list)
    face_keys = set()
    used = set()
    for fi, face in enumerate(faces):
        if len(face) != 4 or len(set(face)) != 4 or any(not isinstance(i, int) or i < 0 or i >= len(vertices) for i in face):
            raise ValueError("Invalid indexed quadrilateral")
        key = tuple(sorted(face))
        if key in face_keys:
            raise ValueError("Duplicated quadrilateral")
        face_keys.add(key)
        used.update(face)
        for j in range(4):
            a, b = face[j], face[(j + 1) % 4]
            edge = (min(a, b), max(a, b))
            edges[edge].append((fi, (a, b)))
            v = face[j]
            link[v].append((face[(j - 1) % 4], face[(j + 1) % 4]))
            face_by_vertex[v].append(fi)
    if len(used) != len(vertices):
        raise ValueError("OBJ/NPZ contains unused vertices; published V would be ambiguous")
    parent = list(range(len(faces)))
    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def join(a, b):
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[rb] = ra
    hist = Counter()
    winding_conflicts = 0
    for users in edges.values():
        hist[len(users)] += 1
        if len(users) == 2:
            (fa, ab), (fb, cd) = users
            if fa == fb or ab == cd:
                winding_conflicts += 1
            join(fa, fb)
        elif len(users) > 2:
            for index in range(1, len(users)):
                join(users[0][0], users[index][0])
    face_components = len({root(i) for i in range(len(faces))})
    singular_vertex_links = 0
    for vi in used:
        neighbors = defaultdict(list)
        degree = Counter()
        for a, b in link[vi]:
            neighbors[a].append(b)
            neighbors[b].append(a)
            degree[a] += 1
            degree[b] += 1
        start = next(iter(neighbors))
        visited = {start}
        pending = [start]
        while pending:
            for adjacent in neighbors[pending.pop()]:
                if adjacent not in visited:
                    visited.add(adjacent)
                    pending.append(adjacent)
        # A manifold interior vertex must have one 2-regular link cycle.
        if len(visited) != len(neighbors) or any(d != 2 for d in degree.values()):
            singular_vertex_links += 1
    v, e, f = len(vertices), len(edges), len(faces)
    chi = v - e + f
    closed = (hist.get(1, 0) == 0 and sum(n for k,n in hist.items() if k > 2) == 0 and
              hist.get(2, 0) == e and winding_conflicts == 0 and
              singular_vertex_links == 0 and face_components == 1)
    genus = None
    if closed and (2 - chi) >= 0 and (2 - chi) % 2 == 0:
        genus = (2 - chi) // 2
    return {
        "vertices": v, "quad_faces": f, "edges": e, "euler": chi,
        "edge_incidence_counts": dict(sorted(hist.items())),
        "face_components": face_components,
        "singular_vertex_links": singular_vertex_links,
        "orientation_conflicts": winding_conflicts,
        "closed_connected_orientable_combinatorial": closed,
        "genus_if_valid": genus,
        "valence_4_irregular_vertex_count": sum(1 for x in used if len(link[x]) != 4),
        "valence_defect_index_sum": sum(4 - len(link[x]) for x in used),
        "closed_quad_gauss_bonnet_parity_pass": (sum(4 - len(link[x]) for x in used) == 4 * chi) if closed else None,
        "paper_irregular_vertex_definition_matched": False,
        "paper_scaled_jacobian_definition_matched": False,
        "paper_angle_and_edge_deviation_definition_matched": False,
    }


def inspect_actual_reference(path: Path, file_id: int, expected_sha256: str,
                             reference_row: dict, source_sha256: str) -> dict:
    """Confirm raw output data and topology; no source pairing without source ID and hash."""
    if file_id != reference_row["file_id"]:
        raise ValueError("Published paper file-ID mismatch")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError("Expected SHA-256 must be a 64-digit lowercase hex string")
    if not isinstance(source_sha256, str) or len(source_sha256) != 64 or any(c not in "0123456789abcdef" for c in source_sha256):
        raise ValueError("Original STL SHA-256 must be supplied")
    if path.suffix.lower() not in (".obj", ".npz"):
        raise ValueError("Only authored OBJ or NPZ QUAD arrays supported")
    if not path.stem.startswith(str(file_id)) or (len(path.stem) > len(str(file_id)) and path.stem[len(str(file_id))].isdigit()):
        raise ValueError("Quad reference filename does not prove the same file ID")
    if not path.is_file() or path.stat().st_size == 0 or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing/oversized actual QUAD source")
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for buf in iter(lambda: stream.read(1 << 20), b""):
            hasher.update(buf)
    digest = hasher.hexdigest()
    if digest != expected_sha256:
        raise ValueError("Reference QUAD output digest mismatch")
    vs, fs = parse_obj_quad(path) if path.suffix.lower() == ".obj" else read_quad_npz(path)
    topo = audit_quad_index_topology(vs, fs)
    counts_match = topo["vertices"] == reference_row["published_vertices"] and topo["quad_faces"] == reference_row["published_faces"]
    return {"file_id": file_id, "actual_quad_sha256": digest, "original_stl_sha256": source_sha256,
            "published_vertex_face_counts_match": counts_match,
            "published_figure_metric_parity_verified": False,
            "exact_input_output_mesh_point_correspondence_verified": False,
            "source_and_quad_author_license_independently_verified": False,
            "raw_quad_topology": topo,
            "classification": "ACTUAL_QUAD_READ_WITH_SOURCE_IDS_UNMATCHED_PAPER_METRIC_DEFINITIONS" if counts_match else
            "ACTUAL_QUAD_READ_PUBLISHED_COUNTS_MISMATCH",
            "reference_topology_screen_passed": bool(counts_match and topo["closed_connected_orientable_combinatorial"] and topo["genus_if_valid"] is not None),
            "reference_pair_accepted_for_fair_comparison": False}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--published-csv", type=Path, required=True)
    ap.add_argument("--model-id", type=int)
    ap.add_argument("--actual-quad", type=Path)
    ap.add_argument("--expected-quad-sha256")
    ap.add_argument("--source-stl-sha256")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    published = published_rows(args.published_csv)
    if args.actual_quad is None or args.model_id is None:
        raise ValueError("This CLI inspects an actual output; model-id and actual-quad are mandatory")
    if args.model_id not in published:
        raise ValueError("ID not in frozen QuadWild cohort")
    receipt = inspect_actual_reference(args.actual_quad, args.model_id, args.expected_quad_sha256,
                                       published[args.model_id], args.source_stl_sha256)
    # Exclusive output creation prevents a result being silently replaced.
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
