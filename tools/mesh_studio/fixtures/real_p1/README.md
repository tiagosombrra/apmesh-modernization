# Original P1 controlled QUAD/AFT triangle source — non-synthetic

- Original repository: `tiagosombrra/apmesh-modernization`.
- Source PR #217 merged to `quad-templates` at `d39bbc447f88e179c3c4ee674bd9309f59c18eed`.
- GitHub Actions successful post-merge run `43588588497`; Linux artifact `14111372234`, Windows artifact `14111247733`.
- `accepted.obj` was extracted unchanged from the original Linux artifact. Linux and Windows archive `accepted.obj` bytes independently compared equal: SHA-256 `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
- The two `corrupt-*.obj` files are exact source-provided negative controls, not generated Studio mutations.
- `generator_report.json` is the original report extracted from the Linux CI artifact.
- The artifact is **real C++ application output**, not a Blender construction, screenshot or invented run. It is deliberately a **controlled single curved Bezier patch** with fixed16 vertex-mean QUAD template sampling, 42 QUAD, 36 native original AFT TRI, 69 physical nodes and 16 original boundary intervals.
- The OBJ `g QUAD` and `g TRI_AFT` records are **element classes**, not different source patches. The full indexed complex is a disk, while the isolated TRI exterior is an annulus. Original UV and XYZ are preserved; no patch welding is inferred.
- Only a single fixed generation is captured. It does **not** certify two accepted adaptation epochs, a global nonmanifold patch complex, original 1993 algorithm equivalence, all-quad support, anisotropic adaptation or continuous Jacobian correctness.
- Independent 4x4 production-source Bezier control-net oracle and source seam/normal controls live in `p1_source_oracle.py`. This source qualification must not be used for unrelated OBJ files.
- The scientific importer and model use no Qt/VTK dependency. Figure exports are full-vector **UV** scenes, not promises of a fully vector shaded 3D view.

Run from repository root:

```bash
python -m tools.mesh_studio.real_p1_cli --output-dir /tmp/apmesh_p1_studio_demo
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards tools.mesh_studio.test_quality_analysis tools.mesh_studio.test_real_p1 -v
```
