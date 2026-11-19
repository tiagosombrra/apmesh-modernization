# S40-F8 — Exact signed-Jacobian audit (isolated S40-F6)

The source implementation proves or rejects **continuous strict positivity** for the decimal-defined S40-F6 indexed BP using exact rational Bernstein coefficients. It records failure of patches 0, 1 and 3; no coordinates or full STEP files are published.

## Reproduce with the previously delivered private F6 archive

Extract the S40-F6 private BP, then from `docs/research/nonmanifold-benchmark/probes` run:

```bash
export APMESH_S40F8_PRIVATE_F6_BP=/private/s40f6_four_face_source_island.PRIVATE.bp
python -m unittest -v test_s40f8_exact_planar_jacobian test_s40f8_integration_gate
python s40f8_exact_planar_jacobian.py \
  --private-f6-bp "$APMESH_S40F8_PRIVATE_F6_BP" \
  --output /private/s40f8_private_exact_jacobian_report.json
```

The last command **intentionally returns exit code 3** when the frozen F6 BP fails the strict positivity gate. The complete report is written before exiting. This gate is called from the F7 candidate rebase and does not authorize source-native admission.

For public math-only tests, omit the private variable; the two optional private test classes skip explicitly. The patch-level proof requires the exact F6 BP hash, not a similar or regenerated file.
