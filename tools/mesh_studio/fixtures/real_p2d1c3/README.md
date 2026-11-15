# Real source-bound P2d-1c3 physical candidates (not accepted epochs)

These **five OBJ files** were copied byte-for-byte from the successful
[APMesh QUAD source PR #235 CI run 43664129060](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43664129060)
for exact source revision `27851df2625e0c0b37e12023af699a01f3d0304c`.
The Linux artifact ID is `14141039513`; the Windows artifact ID is
`14142185137`. All five Linux and Windows `accepted*.obj` filenames were
independently compared during fixture intake and matched by SHA-256.
The original Linux `report.json` is retained byte-for-byte as
`generator_report.json`, digest
`9de13e6e9b8f6a5f6ae188f19acd0a6b068ddc066df2f4ff9d5579ef96f9f054`.
Do not infer from the prefix `accepted` that the candidate OBJ was adopted.
The program uses `accepted` as the *controlled application execution* label.

| Studio file | Original artifact file | Status | SHA-256 |
| --- | --- | --- | --- |
| control.obj | accepted.obj | Controlled nonadaptive output | cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0 |
| band.obj | accepted.band-candidate.obj | Staged, unaccepted | 76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6 |
| west.obj | accepted.west.second-band-candidate.obj | Staged, unaccepted | ca08918f6d71fa672de22a72eb6fef7c106c90c7fd02d40cb19852972b4274ee |
| north.obj | accepted.north.second-band-candidate.obj | Staged, unaccepted | 6eb4faedeaab44fbfa3d4cb2ca1ea618a3dca513dc241871c57bcc7eae26d500 |
| both.obj | accepted.both.second-band-candidate.obj | Staged, unaccepted | b77afb530724f38ff81f0f3e7f06fca6c8dc0cb4a15562ce933a4013724bd36c |

All five represent **ONE controlled original Bezier patch experiment** with
fixed16 source-boundary sampling. These are not five independent repeated runs.
The 64-by-64 source UV sampling evaluates the same 4096 midpoint sites, with
an independent Bernstein source geometry oracle and explicit TRI barycentric
and QUAD bilinear interpolation. Source-coordinate physical units are unspecified.
No continuous interpolation bound, PDE solution convergence, acceptance policy,
all-QUAD algorithm, tensor anisotropy, global patch welding, or statistical
confidence interval is implied. `accepted_adaptive_epochs=0`.

Use `python -m tools.mesh_studio.real_study_cli --output-dir figures/S5D` from
repository root. The Studio verifier checks the OBJ byte digests, unchanged
source report, physical QUAD/TRI inventory, Bezier UV/XYZ correspondence, edge
incidence and output metric values. Studio provenance checks do **not** replace
native QUAD generator CTest and source CI.
