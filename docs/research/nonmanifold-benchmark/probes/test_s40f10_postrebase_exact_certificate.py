"""Hermetic adversarial tests for S40-F10 post-rebase Jacobian certification."""
import unittest
from fractions import Fraction

from s40f10_postrebase_exact_certificate import certify_postrebase_eight


def make_joined(*, reversed_patch=None, collapsed_patch=None):
    """Build a deliberately synthetic 164-patch BP, never real CAD evidence."""
    points = [("0", "0", "0")] * 1743
    patches = [tuple(range(16))] * 156
    for local in range(8):
        face_id = (1279, 1279, 1386, 1386, 3269, 3269, 3485, 3485)[local]
        start = 1600 + local * 16
        patch = tuple(range(start, start + 16))
        patches.append(patch)
        for j in range(4):
            for i in range(4):
                u = Fraction(i, 3)
                v = Fraction(j, 3)
                if local == reversed_patch:
                    v = -v
                if local == collapsed_patch:
                    u = Fraction(0)
                if face_id in (1279, 1386):
                    pt = (u, -v, Fraction(local))
                elif face_id == 3269:
                    pt = (Fraction(local), u, v)
                else:
                    pt = (Fraction(local), v, u)
                points[start + 4 * j + i] = tuple(format(float(x), ".17g") for x in pt)
    return ("// synthetic; not an original S40 source\n"
            + "\n".join("v " + " ".join(p) for p in points) + "\n"
            + "\n".join("p " + " ".join(map(str, patch)) for patch in patches)
            + "\n").encode()


class PostRebaseTests(unittest.TestCase):
    def test_eight_positive_joined_patches_are_certified(self):
        result = certify_postrebase_eight(make_joined())
        self.assertEqual(result["certified_postrebase_patch_count"], 8)
        self.assertFalse(result["parent_156_patch_regularities_certified"])
        self.assertFalse(result["apmesh_tri_quad_executed"])

    def test_inverted_joined_patch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Joined patch 156"):
            certify_postrebase_eight(make_joined(reversed_patch=0))

    def test_collapsed_joined_patch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Joined patch 160"):
            certify_postrebase_eight(make_joined(collapsed_patch=4))

    def test_missing_controls_are_rejected(self):
        bp = make_joined().decode()
        bp = bp.replace("v 0 0 0\n", "", 1)
        with self.assertRaisesRegex(ValueError, "1743 controls"):
            certify_postrebase_eight(bp.encode())

    def test_unknown_record_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported BP record"):
            certify_postrebase_eight(make_joined() + b"x unsafe\n")

    def test_out_of_bounds_index_is_rejected(self):
        bp = make_joined().decode()
        bp = bp.replace("p 0 1 2 3", "p 1743 1 2 3", 1)
        with self.assertRaisesRegex(ValueError, "Out-of-bounds patch"):
            certify_postrebase_eight(bp.encode())


if __name__ == "__main__":
    unittest.main()
