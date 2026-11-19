"""Isolated tests for staged, byte-bound original-native research candidates."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock
import json

from s40f11_atomic_candidate_delivery import (
    BP_NAME, RECEIPT_NAME, publish_native_candidate, require_fresh_destination,
)


def valid_report(bp: str):
    """Construct a synthetic receipt, not an actual original S40 native audit."""
    return {
        "classification": "ORIGINAL_NATIVE_SAMPLED_RESEARCH_CANDIDATE",
        "postrebase_exact_jacobian_proof": {
            "status": "CERTIFIED_STRICT_POSITIVE_POSTREBASE_DECIMAL_BP",
            "joined_bp_sha256": sha256(bp.encode()).hexdigest(),
            "joined_patch_count": 164,
            "joined_control_count": 1743,
            "certified_postrebase_patch_count": 8,
            "new_source_patch_indices": list(range(156, 164)),
        },
        "original_native_audit": {"status": "PASS_SAMPLED_ORIGINAL_NATIVE_GATES"},
        "all_original_native_trim_and_edge_gates_executed": True,
        "apmesh_cpp_tri_quad_executed": False,
        "full_43_face_atlas_complete": False,
        "formal_continuous_original_STEP_hausdorff_certified": False,
        "new_original_source_faces_admitted": 0,
    }


class AtomicCandidateDeliveryTests(TestCase):
    def test_successfully_publish_validated_pair(self):
        with TemporaryDirectory() as root:
            bp = "// synthetic BP contents\n"
            receipt = valid_report(bp)
            dest = publish_native_candidate(Path(root) / "candidate", bp, receipt)
            self.assertEqual((dest / BP_NAME).read_text(), bp)
            self.assertEqual(json.loads((dest / RECEIPT_NAME).read_text()), receipt)
            self.assertEqual(sorted(p.name for p in Path(root).iterdir()), ["candidate"])

    def test_never_overwrite_existing_replay(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            dest.mkdir()
            (dest / BP_NAME).write_text("original run\n")
            with self.assertRaises(FileExistsError):
                publish_native_candidate(dest, "new candidate\n", valid_report("new candidate\n"))
            self.assertEqual((dest / BP_NAME).read_text(), "original run\n")

    def test_refuse_dangling_symlink_destination(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            dest.symlink_to(Path(root) / "absent")
            with self.assertRaises(FileExistsError):
                require_fresh_destination(dest)

    def test_reject_wrong_candidate_digest(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            receipt = valid_report("old\n")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                publish_native_candidate(dest, "different\n", receipt)
            self.assertFalse(dest.exists())

    def test_reject_incomplete_postrebase_proof(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            receipt = valid_report("test\n")
            receipt["postrebase_exact_jacobian_proof"]["certified_postrebase_patch_count"] = 7
            with self.assertRaisesRegex(ValueError, "scope"):
                publish_native_candidate(dest, "test\n", receipt)
            self.assertFalse(dest.exists())

    def test_reject_failed_native_audit(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            receipt = valid_report("test\n")
            receipt["original_native_audit"]["status"] = "BLOCKED_NO_NATIVE_ADMISSION"
            with self.assertRaisesRegex(ValueError, "native"):
                publish_native_candidate(dest, "test\n", receipt)
            self.assertFalse(dest.exists())

    def test_reject_false_full_atlas_claim(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            receipt = valid_report("test\n")
            receipt["full_43_face_atlas_complete"] = True
            with self.assertRaisesRegex(ValueError, "misrepresented"):
                publish_native_candidate(dest, "test\n", receipt)
            self.assertFalse(dest.exists())

    def test_reject_unproven_source_face_admission(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            receipt = valid_report("test\n")
            receipt["new_original_source_faces_admitted"] = 4
            with self.assertRaisesRegex(ValueError, "misrepresented"):
                publish_native_candidate(dest, "test\n", receipt)
            self.assertFalse(dest.exists())

    def test_failed_rename_leaves_no_partial_candidate_or_stage(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            bp = "test\n"
            with mock.patch("s40f11_atomic_candidate_delivery.os.rename", side_effect=OSError("simulated failure")):
                with self.assertRaisesRegex(OSError, "simulated failure"):
                    publish_native_candidate(dest, bp, valid_report(bp))
            self.assertFalse(dest.exists())
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_same_destination_cannot_be_republished(self):
        with TemporaryDirectory() as root:
            dest = Path(root) / "candidate"
            bp = "test\n"
            publish_native_candidate(dest, bp, valid_report(bp))
            with self.assertRaises(FileExistsError):
                publish_native_candidate(dest, bp, valid_report(bp))


if __name__ == "__main__":
    main()
