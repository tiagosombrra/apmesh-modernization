# R2 native-kernel interface graph proof: three touching cuboids

Date: 2026-11-14. STATUS: controlled source-mirror feasibility evidence only. G2 external model admission BLOCKED. No APMesh BP conversion, C++ integration, or mesh generation.

Pinned original research example:
https://github.com/fusion-energy/model_benchmark_zoo/blob/3a2e69fe62209e33a1e176d816609d69a2aebadc/src/model_benchmark_zoo/three_touching_cuboids.py

## What was actually tested

A local CadQuery/OCP mirror of the exact default geometric recipe, NOT an execution of the original upstream Python package, creates three separate width-5 cuboids labeled A (northwest), B (northeast), C (southwest), with southeast exterior VOID. Source unit is unspecified. Each body has six planar faces, twelve topological edges, and volume approximately 125. Source solids have 18 faces and 36 edges in total.

The central spatial segment C0 has endpoints (0,0,-2.5) and (0,0,2.5), length 5. It appears as three distinct original B-Rep edges (one per body), with six source-face edge uses in total. Open CASCADE TopoDS_IsSame returns false across different bodies: the SOURCE IS NOT a topologically shared-edge complex.

An isolated research probe uses native Open CASCADE BRepExtrema_DistShapeShape (distance), TopoDS_IsSame (source-edge identity) and BRepAlgoAPI_Common (overlapping face areas) without sewing or modifying the source shapes. The graph consolidates coincident material-interface faces into a source-to-interface analysis record with four geometrically inferred surface sheets incident to spatial C0:

| Sheet | Region pair | Source bodies | Sheet area | Radial direction |
|---|---|---|---:|---|
| S0 | A/B | A and B, opposing normals | 25 | +Y |
| S1 | A/C | A and C, opposing normals | 25 | -X |
| S2 | B/VOID | B only | 25 | +X |
| S3 | C/VOID | C only | 25 | -Y |

CRITICAL: Four inferred spatially coincident sheets do NOT mean the source B-Rep has a single edge with four topological face users. This graph is an experimental reconstruction with a chosen region/VOID semantics, requiring scientific review. No canonical Bezier control curve has yet been authored.

## Kernel round trip and second checker

A test exports an assembly of the separate source solids to a STEP file, imports it via CadQuery/Open CASCADE, recovers the three bodies by their positions, and rechecks the inferred four sheet graph. This proves consistency for the controlled mirror under one STEP round trip, not equivalence with all upstream CAD assets.

A separate standard-library-only JSON validator independently checks the serialized graph and does not import the CadQuery/OCP producer. It rejects wrong region labels, missing or duplicated sheets, invalid source owners, reused face IDs, inverted interface normals, changed common curve endpoints, false B-Rep merging, and claims of G2 approval. It is an independently implemented check of the SAME analytic geometry assumptions, not external validation by another research group.

## Measured local results (exact source-file Git blobs)

- Python 3.13.5, CadQuery 2.8.0, OCP 7.9.3.1.
- 15/15 specific native kernel, STEP round-trip, JSON validation and mutation tests passed.
- 8 tests cover the native source, displacement rejection and STEP round trip; 7 tests cover independent JSON checks.
- Noncoincident offsets 2e-5 and 1e-8 in source units are rejected instead of being silently welded.
- The JSON generator was run twice with byte-identical results, SHA-256 6185e4d0d506f4082a438bc886ff8a7b2b51d77552fb07414d71436475805531.
- All four source/test files passed Python compileall.
- The earlier STEP reference-screen precursor separately recorded 6/6 tests, not a new project-wide gate.
- Git object identities (SHA-1 of exact tested local source bytes) match the staged remote tree:
  - interface_graph_probe.py: 52392f1e47d1debdd7c22bcf5c2e722d097626b6
  - validate_interface_graph.py: a356f8ee8abd8fb7ea09347585c5b7dd029992f3
  - test_interface_graph_probe.py: 3199922ebc86a46b0895ec2e64b0f6383875363d
  - test_validate_interface_graph.py: a2f4255d6348f4443401bafde4d72ec433a06887

Commands from the repository root:

    python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
    python docs/research/nonmanifold-benchmark/probes/interface_graph_probe.py --output build/research-r2/three_cuboids_interface_graph.json
    python docs/research/nonmanifold-benchmark/probes/validate_interface_graph.py build/research-r2/three_cuboids_interface_graph.json

Run prerequisites: Python >=3.10, CadQuery and its Open CASCADE Python runtime for the model producer. The JSON-only checker requires Python standard library. No GitHub hosted CI check or APMesh CTest/mesh generation is claimed from these results.

## Remaining gates and stop conditions

1. Execute and qualify the precise upstream Python package, or independently compare original authorized CAD bytes and a raw SHA-256 (not done).
2. Review source model rights, material interface semantics, VOID treatment, source-to-sheet correspondence and the intended surface-complex topology. These remain scientific decisions.
3. Extend geometric feature splitting beyond exact full-face coincident pairs (partial overlap, curves, trimmed faces, curved and periodic surfaces are out of scope).
4. Introduce canonical shared edge/curve identifiers and oriented side records in a versioned intermediate graph.
5. Freeze geometry approximation tolerances and verify any four-sided bicubic Bezier patch reconstruction independently before producing valid BP.
6. Run TRI generation with positive real shared-incidence checks, accepted/rejected stage trace and historical regression separately. QUAD/anisotropy are later separately qualified methods.

No external candidate has passed G2, no new BP file has been validated, and no production APMesh code has changed. R2 is PARTIALLY ADVANCED, not closed.

## Follow-on native shared-edge construction

The controlled local interface graph was used to create a distinct, **kernel-valid non-manifold surface complex** through Open CASCADE non-manifold sewing, with one genuine TopoDS edge shared by four faces. See [R2_VALID_NONMANIFOLD_BREP.md](R2_VALID_NONMANIFOLD_BREP.md). This is a constructed research control, not a claim that the original three CAD solids contained a shared topological edge or that a valid APMesh BP has been produced. External G1/G2 admission is still blocked.
