"""Guard the reproducible cold-versus-warm API workload and provenance."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from . import benchmark_web_cache, web_api


class OriginalCacheBenchmarkContracts(unittest.TestCase):
    def test_exact_original_p1_face_equivalence_and_raw_pairs(self):
        report = benchmark_web_cache.measure("p1", "face", pairs=4)
        self.assertEqual(report["schema"], benchmark_web_cache.SCHEMA)
        self.assertEqual(report["source_sha256"], web_api.CATALOG["p1"][2])
        self.assertTrue(report["equivalent_original_scientific_json"])
        self.assertTrue(report["each_request_original_source_sha_rechecked"])
        self.assertEqual(len(report["raw_ms"]["cache_disabled_proxy"]), 4)
        self.assertEqual(len(report["raw_ms"]["warm_source_cache"]), 4)
        self.assertEqual(report["paired_cold_minus_warm_ms"]["count"], 4)
        self.assertEqual(report["orders"][0][0], "cache_disabled_proxy")
        self.assertEqual(report["orders"][1][0], "warm_source_cache")
        self.assertGreaterEqual(report["warm_source_cache"]["p95_ms"],
                                report["warm_source_cache"]["p50_ms"])
        self.assertIn("NOT_NETWORK_OR_BROWSER_RENDER", report["scope"])

    def test_staged_real_candidate_quality_never_becomes_accepted_epoch(self):
        report = benchmark_web_cache.measure("band", "quality", pairs=4)
        self.assertEqual(report["source_status"], "STAGED_UNACCEPTED")
        self.assertTrue(report["equivalent_original_scientific_json"])
        self.assertIn("staged_candidate_is_not_an_accepted_adaptive_epoch",
                      report["limitations"])

    def test_invalid_names_and_sample_limits_fail_before_work(self):
        for model, endpoint, pairs in (
            ("outside", "face", 4), ("p1", "unknown", 4),
            ("p1", "face", 0), ("p1", "face", 101),
            ("p1", "face", True),
        ):
            with self.subTest(model=model, endpoint=endpoint, pairs=pairs):
                with self.assertRaises(ValueError):
                    benchmark_web_cache.measure(model, endpoint, pairs)

    def test_changed_original_file_is_refused_even_with_warm_cache(self):
        source = (Path(web_api.__file__).resolve().parent /
                  "fixtures/real_p1/accepted.obj")
        with tempfile.TemporaryDirectory(prefix="apmesh-v5-bench-") as tmp:
            root = Path(tmp)
            target = root / "real_p1/accepted.obj"
            target.parent.mkdir(parents=True)
            shutil.copyfile(source, target)
            with patch.object(web_api, "ROOT", root):
                benchmark_web_cache.measure("p1", "face", pairs=4)
                target.write_bytes(target.read_bytes() +
                                   b"\n# invalidated source bytes\n")
                with self.assertRaisesRegex(ValueError,
                                            "benchmark_source_sha_mismatch"):
                    benchmark_web_cache.measure("p1", "face", pairs=4)


if __name__ == "__main__":
    unittest.main()
