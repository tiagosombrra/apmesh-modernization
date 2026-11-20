"""Synthetic-only R2.7.33 ELF wrapper/parser tests, NOT original CAD experiments."""

from __future__ import annotations

import json
import math
from pathlib import Path
import unittest

from tools.mesh_studio.native_local_selection_provenance import (
    join_selected_local_to_native_csv,
)
from tools.mesh_studio.native_selected_tri_return import (
    attest, inspect_selected_tri_stream, parse_original_tri_bytes,
    parse_real_adapter_returns,
)
from tools.mesh_studio.test_native_local_selection_provenance import (
    fake_complete_cpp_and_csv,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]


def fake_tri_sidecar(record: dict, corruption: str = "") -> bytes:
    """Build a planar synthetic 10-face local fan to test parser invariants."""
    nodes = {0: (0.5, 0.5, 0.0)}
    for i in range(10):
        angle = 2 * math.pi * i / 10
        nodes[i + 1] = (
            round(0.5 + 0.4 * math.cos(angle), 8),
            round(0.5 + 0.4 * math.sin(angle), 8), 0.0)
    header = {
        "type": "source_selected_adapter_return",
        "return_index": record["return_index"],
        "step": record["step"], "retry": record["retry"],
        "patch": record["patch"], "local": record["local"],
        "outer_epoch": record["outer_epoch"],
        "outer_retry": record["outer_retry"], "session": 6306001,
        "native_source_patch_id": 500 + record["patch"],
        "face_count": 10, "node_count": 11,
        "source_curves": [
            {"edge_slot": i, "native_curve_id": 1000 + i,
             "reversed": bool(i & 1), "source_curve_points": 11}
            for i in range(4)],
        "provisional_post_aft_selected_local_not_global_commit": True,
    }
    faces = []
    for i in range(10):
        ids = (0, i + 1, ((i + 1) % 10) + 1)
        faces.append({
            "type": "face", "element_slot": i,
            "native_element_id": i + 2000,
            "vertices": [
                {"native_node_id": k, "xyz": list(nodes[k]),
                 "uv": list(nodes[k][:2])}
                for k in ids],
        })
    if corruption == "false_global_commit":
        header["provisional_post_aft_selected_local_not_global_commit"] = False
    if corruption == "duplicate_elements":
        faces[1]["native_element_id"] = faces[0]["native_element_id"]
    if corruption == "nonfinite":
        faces[0]["vertices"][0]["uv"][0] = float("nan")
    if corruption == "different_return":
        header["return_index"] += 1
    if corruption == "missing_face":
        faces.pop()
    if corruption == "conflicting_node":
        faces[1]["vertices"][0]["xyz"][0] = 0.1
    trailer = {
        "type": "complete", "face_records": 10,
        "not_global_accepted_step": True,
    }
    return ("\n".join(json.dumps(x, allow_nan=True, sort_keys=True)
                      for x in [header, *faces, trailer]) + "\n").encode()


def fake_complete_source(role="original"):
    selection, csv = fake_complete_cpp_and_csv(role)
    choices = join_selected_local_to_native_csv(
        selection, csv, role)["selected_local_returns"]
    rows, sidecars = [], {}
    for selected in choices:
        num = selected["adapter_return_index"] + 1
        sidecar = f"adapter_return_{num}.ndjson" if selected["step"] == 4 else "none"
        record = {
            "return_index": num,
            "outer_epoch": selected["outer_epoch"],
            "outer_retry": 0,
            "step": selected["step"],
            "retry": selected["retry"],
            "patch": selected["patch"],
            "local": selected["original_selected_local_attempt"],
            "faces": 10, "nodes": 11, "file": sidecar,
        }
        rows.append(
            "R2733_TRI_RETURN=return_index=" + str(num) +
            ",outer_epoch=" + str(record["outer_epoch"]) +
            ",outer_retry=0,step=" + str(record["step"]) +
            ",retry=" + str(record["retry"]) +
            ",patch=" + str(record["patch"]) +
            ",local=" + str(record["local"]) +
            ",faces=10,nodes=11,file=" + sidecar)
        if sidecar != "none":
            sidecars[sidecar] = fake_tri_sidecar(record)
    return (selection + ("\n".join(rows) + "\n").encode(), csv, sidecars)


class OriginalNativeSelectedTriSyntheticContracts(unittest.TestCase):
    def test_source_original_cpp_and_elf_symbol_preregistered(self):
        source = attest(ROOT)
        self.assertIn("src/adapter/adapter.cpp", source)

    def test_genuine_scopes_replayed_from_fake_serial_cpp_stream(self):
        stdout, csv, sidecars = fake_complete_source()
        result = inspect_selected_tri_stream(stdout, csv, sidecars, "original")
        self.assertEqual(result["original_adapter_returns"], 40)
        self.assertEqual(result["true_selected_post_aft_tri_adapter_returns_step4"], 16)
        self.assertFalse(result["scientific_lod_qualified"])

    def test_one_factor_variant_is_not_a_second_original_epoch(self):
        stdout, csv, sidecars = fake_complete_source("variant")
        result = inspect_selected_tri_stream(stdout, csv, sidecars, "variant")
        self.assertEqual(result["true_selected_post_aft_tri_adapter_returns_step4"], 16)
        self.assertFalse(result["native_global_second_accepted_step"])

    def test_read_only_uv_boundary_incidence_is_local(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        data = parse_original_tri_bytes(tri[event["file"]], event)
        self.assertEqual(data["face_records"], 10)
        self.assertEqual(data["local_uv_edges_with_two_faces"], 10)
        self.assertEqual(data["local_uv_edges_with_one_face"], 10)
        self.assertFalse(data["cross_patch_physical_node_welding_qualified"])

    def test_reject_missing_actual_return(self):
        stdout, csv, tri = fake_complete_source()
        chunks = stdout.splitlines()
        lines = [line for line in chunks
                 if not line.startswith(b"R2733_TRI_RETURN=return_index=40,")]
        with self.assertRaises(NativeLineageValidationError):
            inspect_selected_tri_stream(b"\n".join(lines) + b"\n",
                                        csv, tri, "original")

    def test_reject_unselected_sidecar(self):
        stdout, csv, tri = fake_complete_source()
        tri["adapter_return_2.ndjson"] = next(iter(tri.values()))
        with self.assertRaises(NativeLineageValidationError):
            inspect_selected_tri_stream(stdout, csv, tri, "original")

    def test_reject_corrupted_callback_selected_identity(self):
        stdout, csv, tri = fake_complete_source()
        stdout = stdout.replace(
            b"R2733_TRI_RETURN=return_index=1,outer_epoch=1",
            b"R2733_TRI_RETURN=return_index=1,outer_epoch=2", 1)
        with self.assertRaises(NativeLineageValidationError):
            inspect_selected_tri_stream(stdout, csv, tri, "original")

    def test_reject_forged_return_counts(self):
        stdout, csv, tri = fake_complete_source()
        stdout = stdout.replace(b",faces=10,nodes=11,file=",
                                b",faces=11,nodes=11,file=", 1)
        with self.assertRaises(NativeLineageValidationError):
            inspect_selected_tri_stream(stdout, csv, tri, "original")

    def test_reject_forged_global_commit_from_provisional_local(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        with self.assertRaises(NativeLineageValidationError):
            parse_original_tri_bytes(fake_tri_sidecar(
                event, "false_global_commit"), event)

    def test_reject_duplicate_original_native_face_id(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        with self.assertRaises(NativeLineageValidationError):
            parse_original_tri_bytes(fake_tri_sidecar(
                event, "duplicate_elements"), event)

    def test_reject_wrong_original_cpp_adapter_return_index(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        with self.assertRaises(NativeLineageValidationError):
            parse_original_tri_bytes(fake_tri_sidecar(
                event, "different_return"), event)

    def test_reject_incomplete_real_tri_faces(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        with self.assertRaises(NativeLineageValidationError):
            parse_original_tri_bytes(fake_tri_sidecar(
                event, "missing_face"), event)

    def test_reject_conflicting_node_coordinates(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        with self.assertRaises(NativeLineageValidationError):
            parse_original_tri_bytes(fake_tri_sidecar(
                event, "conflicting_node"), event)

    def test_reject_nonfinite_original_vertex_uv(self):
        stdout, _, tri = fake_complete_source()
        event = next(x for x in parse_real_adapter_returns(stdout)
                     if x["step"] == 4)
        with self.assertRaises(NativeLineageValidationError):
            parse_original_tri_bytes(fake_tri_sidecar(
                event, "nonfinite"), event)


if __name__ == "__main__":
    unittest.main()
