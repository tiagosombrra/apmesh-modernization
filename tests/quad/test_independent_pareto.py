"""Adversarial controls for profiled physical QUAD/TRI dominance."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from independent_pareto import audit_pareto_profiles


def example():
    # This bounded fixture is checked separately against real generated OBJ.
    return {
        "band": dict(nodes=93, quads=62, triangles=44, elements=106,
                     quad_uv_area=.328125, max_xyz=.05160741345747398,
                     rms_source_area=.011810324643012932,
                     min_scaled_jacobian=.567009347028317,
                     min_warpage_cosine=.9970126470841612),
        "west": dict(nodes=109, quads=75, triangles=50, elements=125,
                     quad_uv_area=.375, max_xyz=.02626856930484137,
                     rms_source_area=.009960083459157833,
                     min_scaled_jacobian=.567009347028317,
                     min_warpage_cosine=.9970126470841612),
        "north": dict(nodes=107, quads=71, triangles=54, elements=125,
                      quad_uv_area=.375, max_xyz=.02626856930484137,
                      rms_source_area=.00923331923514389,
                      min_scaled_jacobian=.567009347028317,
                      min_warpage_cosine=.9970126470841612),
        "both": dict(nodes=117, quads=82, triangles=52, elements=134,
                     quad_uv_area=.40625, max_xyz=.02626856930484137,
                     rms_source_area=.009155128673187646,
                     min_scaled_jacobian=.567009347028317,
                     min_warpage_cosine=.9970126470841612),
    }


class PhysicalParetoAuditTest(unittest.TestCase):
    def test_uv_area_profile_independently_exposes_dominance(self):
        actual = audit_pareto_profiles(example())
        profile = actual["profiles"]["uv_area_profile"]
        self.assertEqual(profile["nondominated"], ["band", "both", "north"])
        self.assertEqual(profile["dominated_by"]["west"], ["north"])
        self.assertEqual(actual["adaptive_epochs"], 0)

    def test_quad_count_is_a_separate_objective(self):
        profile = audit_pareto_profiles(example())["profiles"]["quad_count_profile"]
        self.assertEqual(profile["nondominated"], ["band", "both", "north", "west"])
        self.assertEqual(profile["dominated_by"]["west"], [])

    def test_reordering_does_not_change_front(self):
        measurements = example()
        reversed_records = dict(reversed(list(measurements.items())))
        self.assertEqual(audit_pareto_profiles(reversed_records),
                         audit_pareto_profiles(measurements))

    def test_reject_mismatched_typed_counts(self):
        measurements = example()
        measurements["north"]["elements"] += 1
        with self.assertRaises(ValueError):
            audit_pareto_profiles(measurements)

    def test_reject_nonfinite_and_missing_objectives(self):
        for mutation in ("nan", "missing", "foreign", "nonnumeric"):
            with self.subTest(mutation=mutation):
                measurements = example()
                if mutation == "nan":
                    measurements["west"]["rms_source_area"] = float("nan")
                elif mutation == "missing":
                    del measurements["north"]["nodes"]
                elif mutation == "foreign":
                    measurements["both"]["fake_accepted_epoch"] = 2
                else:
                    measurements["band"]["max_xyz"] = "improved"
                with self.assertRaises(ValueError):
                    audit_pareto_profiles(measurements)

    def test_identical_candidates_do_not_dominate_each_other(self):
        measurements = {"a": example()["band"], "b": copy.deepcopy(example()["band"])}
        for profile in audit_pareto_profiles(measurements)["profiles"].values():
            self.assertEqual(profile["nondominated"], ["a", "b"])
            self.assertEqual(profile["dominated_by"], {"a": [], "b": []})


if __name__ == "__main__":
    unittest.main()
