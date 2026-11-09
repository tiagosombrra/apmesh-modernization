# Post-merge PR #185 exact-head CI verification — 2026-11-09

**Status:** Passed in recorded scope. No QUAD physical mesh or wider scientific milestone claimed.

- Repository `tiagosombrra/apmesh-modernization`, canonical branch `quad-templates`.
- Verified exact checkout/branch SHA: `3650a50e4101fa9348147cdfb6979c1bad77a7a7`.
- [GitHub Actions run #42637555612](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42637555612): completed **success**, 4/4 jobs passed, 2026-11-09 14:44:04–14:50:23 UTC (approximately 6 min 19 sec).
- Native Linux GCC QUAD: **2/2 CTest passed**. Native Windows MSVC QUAD: **2/2 CTest passed**. Both actual-tree demos reported 19 source leaves, 42 quads, 53 vertices, included UV area 0.25.
- TRI baseline: **75/75 CTest** passed. Python tooling: **527/527** tests passed.
- Independent TRI science against frozen `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`: Eistute five states, Book four states, matching acceptance decisions, metrics, byte-identical generated OBJ outputs and verified boundary-incidence coverage. Last accepted meshes: 1168 triangles Eistute, 4256 Book. The candidate and reference executables shared SHA-256 `4d5861edfc3bd69cfc03f841550a0e55aa3f74f5b1403459836ffda9de707ab5`. Science artifact ID `13682654557` from this run.
- Output was reviewed in completed GitHub job logs for all four jobs, not inferred from a queued workflow.
- This run qualifies the **unchanged integrated UV prototype and preserved TRI baseline within tested scenarios**. No approval of a numerical M1 centroid, 3D QUAD/XYZ, complete boundary, multipatch, repetition/adaptation, ASan/LSan/CRT whole-process or physical benchmark scope.

The original PR #185 remains **merged** only into `quad-templates`; the modernization `main` remains at `f6050ec1...`. The previous 2026-11-09-16 checkpoint labeled post-merge CI as pending: this record supersedes that status without deleting the earlier entry.
