"""Independently audit read-only pair possibilities against the archived OBJ."""
from collections import Counter, defaultdict
import csv

from independent_common_grid import load_physical_obj


def audit_pair_inventory(archive, candidate_csv=None):
    manifest = list(csv.DictReader((archive / "manifest.csv").open()))
    stages = list(csv.DictReader((archive / "boundary_pair_stages.csv").open()))
    candidates = list(csv.DictReader((candidate_csv or archive / "boundary_pair_candidates.csv").open()))
    assert len(manifest) == len(stages) > 0, "Missing pair stage observation"
    scope_keys = ("step", "epoch", "retry", "domain_generation", "reference_tri_accepted")
    stage_keys = [tuple(row[k] for k in scope_keys) for row in stages]
    assert len(set(stage_keys)) == len(stages), "Repeated pair stage identity"
    assert all(tuple(row[k] for k in scope_keys) in stage_keys for row in candidates), "Foreign pair scope"
    result = []
    for stage, row in zip(stages, manifest):
        key = tuple(row[k] for k in scope_keys)
        assert tuple(stage[k] for k in scope_keys) == key, "Pair/manifest identity differs"
        xyz, _, faces = load_physical_obj(archive / row["quad_tri_obj"])
        quads = int(row["quads"])
        assert int(stage["seed_quad_faces"]) == quads and stage["selected_pairs"] == "0"
        expected = {}
        edges = defaultdict(list)
        exterior = faces[quads:] if quads else []
        for i, face in enumerate(exterior, quads + 1):
            assert len(face) == 3
            for a, b in zip(face, face[1:] + face[:1]):
                edges[tuple(sorted((a + 1, b + 1)))].append(i)
        for edge, owners in edges.items():
            assert len(owners) <= 2, "Nonmanifold TRI source"
            if len(owners) == 2:
                expected[tuple(owners)] = edge
        observed = [candidate for candidate in candidates
                    if tuple(candidate[k] for k in scope_keys) == key]
        assert len(observed) == len(expected) == int(stage["topology_candidates"])
        assert int(stage["observed_aft_triangles"]) == len(exterior)
        assert stage["scope"] == ("topology_only_policy_pending" if quads else
                                  "not_applicable_without_quad_seed")
        seen = set()
        for candidate in observed:
            pair = tuple(int(candidate[k]) for k in ("first_face", "second_face"))
            assert pair not in seen and pair in expected, "Missing/duplicate/foreign TRI pair"
            seen.add(pair)
            assert tuple(int(candidate[k]) for k in ("shared_a", "shared_b")) == expected[pair]
            cycle = [int(candidate[k]) for k in ("quad_a", "quad_b", "quad_c", "quad_d")]
            assert len(set(cycle)) == 4 and all(1 <= i <= len(xyz) for i in cycle)
            assert cycle[0] == min(cycle) and candidate["selection_status"] == "not_evaluated"
            uses = Counter((a + 1, b + 1) for index in pair for face in [faces[index - 1]]
                           for a, b in zip(face, face[1:] + face[:1]))
            boundary = {(a, b) for a, b in uses if (b, a) not in uses}
            assert set(zip(cycle, cycle[1:] + cycle[:1])) == boundary, "Changed pair boundary"
        result.append({"step": int(row["step"]), "triangles": len(exterior),
                       "topology_candidates": len(observed), "selected": 0})
    return result
