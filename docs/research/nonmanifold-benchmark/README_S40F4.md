# S40-F4 private replay and bidirectional curve coverage

Research-only implementation for the original industrial S40. No new source
face was admitted. Neither original STEP nor private BP coordinates are bundled.

## Files

- `s40f1_six_edge_planar_builder.py`: updated source-indexed candidate builder.
- `s40f4_private_s3y_replay.py`: replays the exact selected S3.Y from a private S3.W ZIP.
- `test_s40f4_bidirectional_source_arc_coverage.py`: 15 tests, including source-derived OCP arc descriptors.
- `test_s40f4_private_s3y_replay.py`: 14 synthetic fixture tests for fail-closed replay.
- Previous S40-F1/F2/F3 tests plus regressions and evidence reports.

## Regressions

```bash
python -m unittest -q test_s40f1_canonical_circle_math test_s40f2_inherited_vertex_prebinding test_s40f2_native_admission_gate test_s40f2_cli_rejection test_s40f3_curve_distance_vs_synchronized test_s40f4_bidirectional_source_arc_coverage test_s40f4_private_s3y_replay
```

The previous S3.Z.4 tests are bundled in their separate `s3z4/` directory.
Review `S40F4_BIDIRECTIONAL_SOURCE_CURVE_AND_PRIVATE_REPLAY.md` for the
private replay invocation and exact original hashes. Do not infer full-S40
CAD approval from synthetic unit tests.
