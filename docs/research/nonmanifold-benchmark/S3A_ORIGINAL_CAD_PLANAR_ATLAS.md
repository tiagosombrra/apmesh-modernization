# S3.A — Bounded planar patch atlas from original complex CAD

**Classification:** isolated research code; not an APMesh generator modification or an accepted paper result. Pinned source CAD originals remain outside Git.

This package extracts ONLY convex planar source faces having a single four-straight-edge outer wire. It converts a planar bilinear patch into a 4x4 polynomial bicubic control net through degree elevation, preserving exact TopoDS vertex and edge identities in shared global BP control indices. The JSON sidecar retains original face/edge IDs, source SHA-256, exclusions and independent audit outcomes. It does **not** silently sew near contacts, decompose holes, heal source geometry, fit curved surfaces, claim genuine external 3+-sheet geometry or submit a model to APMesh TRI.

Run from the repository root with CadQuery/OCP installed and original STEP assets acquired separately in an external `sources` directory. For M5, S40, S27 and M3:

```sh
python docs/research/nonmanifold-benchmark/probes/original_cad_planar_atlas.py --model M5 --sources /external/mambo/sources --output build/research-s3
python docs/research/nonmanifold-benchmark/probes/audit_original_cad_planar_atlas.py --source /external/mambo/sources/i05o_m5.step --expected-sha256 895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb --bp build/research-s3/m5.partial.bp --sidecar build/research-s3/m5.partial.json
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p test_original_cad_planar_atlas.py -v
```

**2026-11-15 local directed result:** 11 tests passed on authored native BRep controls including identity preservation, de Casteljau/native-face independent samples, holes, concavity, nonplanar rejection, forged source edges, tampered BP and near-coincident topologically distinct solids. Source-original M5/S40/S27/M3 conversions are **NOT RUN** in this delivery environment; their original STEP bytes were not available here. The previously recorded native S1 screening found 6, 9, 20 and 10 *candidates*, not guaranteed outputs from this new stricter converter.

**Residual risk:** corner/edge indices are importer-local and pinned to a particular exact source, importer release and traversal; cross-kernel reindexing requires explicit revalidation. Sampled native distance is diagnostic, not a continuous bound for arbitrary surfaces. The exact polynomial guarantee is restricted to the accepted convex planar quad class. No complete four-model atlas or R4/R5/G1-G7 admission follows.

**Next research gate:** execute original-source conversions in the pinned CadQuery/OCP environment; independently audit all resulting partial BP; analyze excluded source curves and trims; then design model-specific curved-feature approximation with a budget fixed before fitting. External non-manifold original 3+-sheet model acquisition remains separate and blocked.
