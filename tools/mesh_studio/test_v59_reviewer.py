"""Fail-closed controls for exact C++-source reviewer evidence and cleanup."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from . import v59_reviewer as reviewer


class OriginalSourceReviewerTests(unittest.TestCase):
    def test_xml_declaration_has_canonical_lf_on_every_host(self):
        from .svg_figure import URI, write_canonical_svg
        import xml.etree.ElementTree as ET
        root = ET.Element("{" + URI + "}svg")
        ET.SubElement(root, "{" + URI + "}polygon", points="0,0 1,0 0,1")
        with TemporaryDirectory(prefix="v59-canonical-svg-") as folder:
            path = Path(folder) / "source.svg"
            write_canonical_svg(root, path)
            raw = path.read_bytes()
            self.assertTrue(raw.startswith(
                b"<?xml version='1.0' encoding='utf-8'?>\\n<svg"))
            self.assertNotIn(b"\\r\\n", raw)
            self.assertEqual(raw.count(b"\\n"), 1)

    def test_original_source_digest_inventory_has_no_duplicate_paths(self):
        self.assertEqual(len(reviewer.SOURCE_FILES), 10)
        self.assertEqual(len(set(reviewer.SOURCE_FILES)), 10)
        self.assertTrue(all(size > 1000 and len(digest) == 64
                            for size, digest in reviewer.SOURCE_FILES.values()))
        self.assertEqual(reviewer.ORIGINAL_CI_RUN, 45147268663)

    def test_missing_file_is_not_silently_skipped(self):
        with TemporaryDirectory(prefix="v59-untrusted-") as temp:
            with self.assertRaisesRegex(reviewer.ReviewerSourceError,
                                        "missing_or_unexpected_original_cpp_source_file"):
                reviewer._verify_exact_source_bytes(Path(temp))

    def test_rehashed_fake_file_does_not_replace_pinned_original(self):
        with TemporaryDirectory(prefix="v59-source-mutation-") as temp:
            root = Path(temp)
            fake = root / "visual.json"
            fake.write_bytes(b'{"source_cpp_raw_ndjson_reaudited":true}')
            original = reviewer.SOURCE_FILES
            with mock.patch.object(reviewer, "SOURCE_FILES", {
                    "visual.json": (fake.stat().st_size,
                                    "a" * 64)}):
                with self.assertRaisesRegex(reviewer.ReviewerSourceError,
                                            "original_cpp_file_sha_or_size_drift"):
                    reviewer._verify_exact_source_bytes(root)
            self.assertEqual(original["r2720-native-accepted-scene.json"][0],
                             1716994)

    def test_additional_user_file_makes_review_corpus_invalid(self):
        with TemporaryDirectory(prefix="v59-unindexed-") as temp:
            root = Path(temp)
            raw = b"fixture"
            (root / "only-original").write_bytes(raw)
            (root / "unexpected").write_bytes(b"foreign data")
            with mock.patch.object(reviewer, "SOURCE_FILES", {
                    "only-original": (len(raw), sha256(raw).hexdigest())}):
                with self.assertRaisesRegex(reviewer.ReviewerSourceError,
                                            "missing_or_unexpected_original_cpp_source_file"):
                    reviewer._verify_exact_source_bytes(root)

    def test_symlinked_original_cpp_file_rejected(self):
        with TemporaryDirectory(prefix="v59-symlink-") as temp:
            root = Path(temp)
            actual = root / "real"
            actual.write_bytes(b"synthetic")
            link = root / "accepted"
            try:
                link.symlink_to(actual)
            except (NotImplementedError, OSError):
                self.skipTest("host does not permit unprivileged symlinks")
            with mock.patch.object(reviewer, "SOURCE_FILES", {
                    "accepted": (9, sha256(b"synthetic").hexdigest()),
                    "real": (9, sha256(b"synthetic").hexdigest())}):
                with self.assertRaisesRegex(reviewer.ReviewerSourceError,
                                            "symlink_in_original_source_bundle"):
                    reviewer._verify_exact_source_bytes(root)

    def test_original_cpp_source_artifact_is_independently_reopened_if_present(self):
        # This remains an authentic source test when CI downloaded the original
        # two artifacts; ordinary local unit tests do not invent scientific data.
        if not reviewer.CORPUS.is_dir():
            self.skipTest("real original native source not present in ordinary checkout")
        result = reviewer.preflight(reviewer.CORPUS)
        self.assertTrue(result["source_cpp_raw_postcommit_reopened"])
        self.assertEqual(result["accepted_cpp_global_steps"],
                         {"eistute": [1], "book": [1]})
        self.assertFalse(result["native_cpp_recompiled_in_this_review"])
        self.assertFalse(result["scientific_lod_qualified"])


if __name__ == "__main__":
    unittest.main()
