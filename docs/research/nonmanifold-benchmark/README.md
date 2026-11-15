# Non-manifold benchmark corpus and reverse-patch feasibility

**Status:** R0 documented; R1 40 source leads; R2 controlled constructed multi-sheet BRep; **R3 one exact planar bicubic BP control verified, full R3 pilot and external G2 still OPEN**. Date: 2026-11-14.
**Frozen planning base:** main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
**Research branch:** `research/benchmark-corpus-reverse-patches`, draft PR #225.

## Evidence and review sequence

1. [R0 baseline audit](R0_BASELINE_AUDIT.md): historical Book/Eistute/Decor model identity, frozen main and concurrency; **no fresh production regression**.
2. [R1 source discovery](R1_DISCOVERY_REPORT.md): 40 individually traceable candidates (29 HexMe original CAD files, six Fusion Energy procedural scripts, five upstream Thingi10K invalid-input leads).
3. [R2 topological screening](R2_TOPOLOGY_SCREEN.md): eight structurally traversable original STEP edge-use graphs; one torus/vertex-loop limitation; five local CadQuery pinned-source mirrors. Explicit STEP edge identity is **not** the same as geometrically coincident edges from separate solids.
4. [R2 native-kernel interface proof](R2_NATIVE_INTERFACE_PROOF.md): three-cuboid STEP export/import and 4 reconstructed spatial-interface sheets; 15 native/JSON controls passed; G2 remains blocked.
5. [R2 kernel-valid non-manifold BREP control](R2_VALID_NONMANIFOLD_BREP.md): one constructed four-face shared topological edge; 19 local controls including native BREP export/import; external G2 still blocked.
6. [R3 analytic bicubic pilot](R3_ANALYTIC_BICUBIC_PILOT.md): 4 indexed BP patches, 52 unique control vertices, one canonical 4-incident C0 boundary; 13 new controls and 32 total R2+R3 local tests passed. Not an external admitted model or APMesh mesh generation.
7. [Scientific visual gallery](gallery/README.md): attributed source imagery and author-authored schematic with available/unsupported representation stages.
8. [Candidate register](candidate_register.csv): all 40 are still DISCOVERED; 13 are annotated with screening observations and one extra torus limitation, but no G2 or complete G1-G7 admission.
9. [Execution plan](PLAN.md), [model admission protocol](MODEL_ADMISSION_PROTOCOL.md), [candidate source inventory](CANDIDATE_SOURCES.md) and [risk/decision register](RISK_AND_DECISION_REGISTER.md).

## Limited research probes

Located under `probes/`; not part of the production CMake build:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
python docs/research/nonmanifold-benchmark/probes/export_source_mirror.py --output-dir build/research-r2
python docs/research/nonmanifold-benchmark/probes/cadquery_contact_probe.py
python docs/research/nonmanifold-benchmark/probes/step_structural_screen.py path/to/permitted/original.step
python docs/research/nonmanifold-benchmark/probes/interface_graph_probe.py --output build/research-r2/three_cuboids_interface_graph.json
python docs/research/nonmanifold-benchmark/probes/validate_interface_graph.py build/research-r2/three_cuboids_interface_graph.json
python docs/research/nonmanifold-benchmark/probes/nonmanifold_sewing_probe.py --interface-graph build/research-r2/three_cuboids_interface_graph.json --output-json build/research-r2/sewn_complex_report.json --output-brep build/research-r2/four_sheet_nonmanifold.brep
python docs/research/nonmanifold-benchmark/probes/build_analytic_bp.py --graph build/research-r2/three_cuboids_interface_graph.json --out-bp build/research-r2/four_sheet_planar.bp --out-sidecar build/research-r2/four_sheet_planar.sidecar.json
python docs/research/nonmanifold-benchmark/probes/audit_analytic_bp.py --bp build/research-r2/four_sheet_planar.bp --sidecar build/research-r2/four_sheet_planar.sidecar.json --native-brep build/research-r2/four_sheet_nonmanifold.brep
```

The STEP scanner requires Python; the CadQuery probes additionally require CadQuery/OCP. The locally executed 15 new native-kernel/JSON tests have Git blob SHA identities matching the newly authored Git tree, as recorded in the R2 native proof; this does not certify the original upstream package or the production APMesh build. See R2 report for command scope, results and missing gates.

## Corpus partitions

HISTORICAL (three original author-created article baselines), SYNTHETIC_POSITIVE (analytic engineering controls), EXTERNAL_POSITIVE (**none admitted**), MANIFOLD_CONTROL (independently classified CAD quality/fitting controls), NEGATIVE_UNSUPPORTED (invalid/ambiguous/vertex-contact cases).

## Scientific boundaries

No production C++, published `.bp`, scientific acceptance policy or numerical oracle has been changed. No third-party raw asset is committed. No external 3+-sheet patch-edge source has been verified. Future reconstruction, conversion, TRI qualification and QUAD/TRI/all-quad/anisotropy work require independent gates and advisor decisions before scientific claims.
