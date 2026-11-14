# R2 controlled valid non-manifold B-Rep surface complex

Status: ONE CONSTRUCTED, LOCALLY VERIFIED POSITIVE SURFACE COMPLEX. External G1/G2 model admission still BLOCKED.
Date: 2026-11-14. Scientific classification: controlled analytic proof of topological reconstruction, not APMesh generation.

## Input and transformation

Pinned upstream geometric recipe:
https://github.com/fusion-energy/model_benchmark_zoo/blob/3a2e69fe62209e33a1e176d816609d69a2aebadc/src/model_benchmark_zoo/three_touching_cuboids.py

The source is a local recreation of the default three-cuboid CAD recipe, NOT an execution of the original upstream library. Its three original B-Rep solids have three distinct topological edge identities occupying the same spatial segment. The prior R2_NATIVE_INTERFACE_PROOF.md derives four surface sheets with exact region semantics A/B, A/C, B/VOID and C/VOID. This is a user-chosen surface-complex interpretation; original CAD topology is not claimed to be a single non-manifold edge.

For each inferred sheet, create a valid planar rectangular face with area 25 using an exact source-derived central spatial segment. Invoke Open CASCADE BRepBuilderAPI_Sewing with tolerance 1e-8 and SetNonManifoldMode(True). This is an explicit topology-construction step, not an input repair or an automatic proof of intended topology. All source B-Reps remain untouched.

## Direct native-kernel results

The sewn output is a kernel-valid Open CASCADE Shell with:
- 4 valid planar faces, each area 25;
- 13 unique TopoDS edge identities in the constructed surface complex;
- face-to-topological-edge incidence histogram: 12 edges with one face, ONE edge with FOUR different faces;
- exactly one BRepBuilderAPI_Sewing multiple edge;
- native central shared edge length 5;
- all four face edges referencing exactly the same TopoDS edge according to IsSame.

A native Open CASCADE BREP binary/text export followed by a fresh import preserves one shared edge with four incident faces. The generated output is NOT an APMesh BP file, and it is not a general converter.

## Negative controls, quality checks and provenance

The same geometry with standard manifold sewing mode produces two separate topological groups, not a single four-face shared edge. Moving one input sheet by 2e-5 source units while keeping sewing tolerance at 1e-8 prevents false four-face matching.

The local suite includes 15 earlier R2 native/JSON controls plus 4 non-manifold sewing tests, all 19 passing. The new four tests cover: valid four-way shared edge identity, control without non-manifold mode, near-but-not-equal geometry, and BREP export/import preservation. This native, derived positive case is not evidence of successful third-party STEP conversion or meshing.

Runtime: Python 3.13.5, CadQuery 2.8.0, Open CASCADE via OCP 7.9.3.1.
The two generated native BREP files were byte-identical and the two JSON report files were byte-identical in local repeat runs.

Expected hashes for this exact local experiment:
- inferred interface graph JSON: 6185e4d0d506f4082a438bc886ff8a7b2b51d77552fb07414d71436475805531 (SHA-256)
- sewn surface complex report JSON: a504aff13b3b507b8177bc69d348b2cf8f3373c78c48921b438cf3f9ab7c8345 (SHA-256)
- generated four-sheet non-manifold BREP file: 10754c555cd43dc1d069bfc33a52b731dfacb37ec533ef1060bde309a26a8a99 (SHA-256)

The exact measured local file bytes correspond to the Git blob identities:
- nonmanifold_sewing_probe.py: 55d64a763e0042dd91c57fc46d6aa4987687a4b6
- test_nonmanifold_sewing_probe.py: 91fb53d15b5368bc4b04a31ada35b5ca78f68d6e

Reproduction from the repo root (Python + CadQuery/OCP installed):

    python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
    python docs/research/nonmanifold-benchmark/probes/interface_graph_probe.py --output build/research-r2/three_cuboids_interface_graph.json
    python docs/research/nonmanifold-benchmark/probes/nonmanifold_sewing_probe.py --interface-graph build/research-r2/three_cuboids_interface_graph.json --output-json build/research-r2/sewn_complex_report.json --output-brep build/research-r2/four_sheet_nonmanifold.brep

This report does not claim that CTest, historical TRI generation, QUAD, all-quad, anisotropy, numeric fitting, or scientific source/model licensing checks were run.

## Explicit blockers

1. The surface-complex selection has a material/VOID interpretation, not formally signed off by the thesis advisors.
2. The input is a local source-recipe mirror, not a signed/hashed original externally sourced CAD artifact. G1 and external G2 admission still pending.
3. All four sheets are planar analytic controls. No automatic patch decomposition, bicubic Bezier fitting, shared 16-control BP writer or independent geometry approximation budget has been established.
4. T-junction partial overlaps, curved/trimmed surfaces, inconsistent orientations and tolerance-scale failures are not supported by this proof.
5. Native sewing may weld unwanted nearly coincident curves if tolerance is inappropriate; current negative control is only a bounded example, NOT a formal global tolerance guarantee.
6. No APMesh load/generation, positive runtime shared-incidence checker, regression or comparison has been executed for this constructed shell.

Outcome: one **topologically valid constructed non-manifold BREP control** is available for the next R3 representation-feasibility pilot. External dataset admission and R2 scientific closure remain BLOCKED. No source APMesh code was modified.
