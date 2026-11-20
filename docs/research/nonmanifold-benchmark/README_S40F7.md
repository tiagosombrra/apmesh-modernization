# S40-F7 — Protected original-source join gate

The `s40f7_parent_lineage_rebase.py` file constructs an indexed candidate joining the isolated four-face S40-F6 island to the frozen 156-patch S3.Y atlas **only if** original source, parent BP, source-edge correspondence and native trimmed-face checks pass. It does not change APMesh production code.

## Local tests

```bash
cd probes
python -m unittest -q test_s40f7_parent_lineage_rebase
```

`APMESH_S40F7_PRIVATE_DIR` may point to a directory containing the original-source-derived private `s40f6_four_face_source_island.PRIVATE.bp` and `s40f6_source_island.PRIVATE.json`; otherwise the four F6 private tests are skipped explicitly. The rest use synthetic coordinates and do not require industrial geometry.

## Native replay

Use the research checkout containing `s3c_step_source_gate.py`, `s3s_full_original_face_census.py`, `s3y_s40_curved_planar_rings.py`, `s40f1_six_edge_planar_builder.py`, `audit_analytic_bp.py`, plus the S40-F7/F6/F5 modules. See `S40F7_FOUR_FACE_NATIVE_PARENT_RECONCILIATION.md` for the full command and limitations. The original STEP and the frozen private S3.Y BP are not included.

**Do not confuse structural compatibility with S3.Y admission or an actual APMesh TRI/QUAD mesh.**
