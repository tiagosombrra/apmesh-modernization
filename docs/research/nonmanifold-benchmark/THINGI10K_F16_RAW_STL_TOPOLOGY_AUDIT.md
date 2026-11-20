# S40-F16 — Three actual pinned Thingi10K STL files: independent incidence and vertex-link audit

**Executed:** 2026-11-20. **Research PR:** [#225](https://github.com/tiagosombrra/apmesh-modernization/pull/225) (DRAFT). This is a **source-triangular-mesh topology** checkpoint, not a QuadWild-vs-APMesh benchmark result, full STL-to-Bézier conversion, or license authorization.

## Inputs and identity proof

The same frozen 23-ID literature roster from F15 was retained (**12 QuadWild, 11 Badia**). Rather than treating third-party catalog flags as independent geometry proofs, the three actual **ZIP-packaged STL payloads** below were obtained through a GitHub public mirror at pinned upstream Git revisions. The audit verified the **Git blob identity of the original ZIP**, its ZIP local/central headers, single numeric STL entry, exact decompressed byte length and CRC32, and independently computed the **SHA-256 digest of the unmodified STL byte sequence**.

The original Thingiverse author-upload byte equivalence and per-object permissions were **not established**. Do not redistribute these third-party STEP/STL objects or CAD/mesh derivatives in the research branch.

| File ID, literature | Pinned mirror ZIP Git blob SHA-1 | Raw decompressed STL SHA-256 | Encoding | Raw STL bytes |
|---|---|---|---|---:|
| 293137 (Badia) | `359c26b16664e9ba8d2415ca065a85bd27504d5f` | `4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a` | binary | 14684 |
| 37881 (Badia) | `71e78988f89aa2d937133be581b5a2ccb0de058a` | `a3418939fd2caacffe62ee987a265afd19fdf125cbf0221149ee1175bd114f0a` | binary | 170084 |
| 61394 (QuadWild) | `19d7b777747e3b3f7a37560b0f798378c0aa5973` | `7a614a8d71b65cae465868a6c7f3800e44b4c4a79d56aa58e6b501a58bff8c3c` | ASCII | 1701140 |

Pinned mirror commits: `larsbrubaker/Thingi10K-meshes-1@2d6f82c6f7934f23b051daf2b19e918c62d30d7b` and `larsbrubaker/Thingi10K-meshes-2@ab50a098405dc2dfcf882e87dab3811b5ea8ce92`. Original mirror paths `meshes/<file_id>.stl.zip`. Metadata catalog `larsbrubaker/Thingi10K@6c29395a9c14766eb04a9a27746f681e2eb584c7` was independently screened in F15; its face counts agree with **all three** raw files in this stage.

## Real topology results — unmodified STL face soup

Vertex IDs were reconstructed deterministically from **exact numeric equality of parsed XYZ coordinates** across STL triangle corners, without epsilon welding or repair. This is appropriate for a conservative mesh-incidence screen, but **is not proof of original author-provided indexed topology**: STL carries positions and facets, not original B-Rep curve IDs. Incidence counts include duplicated/degenerate input triangles exactly as present.

| ID | Triangles | Unique XYZ vertices | Unique edges | Free edges | 2-face edges | 3-face edges | 4-face edges | Connected components | Singular vertex links | Zero-area triangles | Duplicate triangles |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 293137 | 292 | 148 | 438 | 0 | 438 | 0 | 0 | 1 | 0 | 0 | 0 |
| 37881 | 3400 | 1700 | 5100 | 0 | 5100 | 0 | 0 | 1 | 0 | 0 | 0 |
| 61394 | 6747 | 3367 | 10127 | 87 | 9979 | 48 | 13 | 4 | 86 | 72 | 1 |

### Controlled interpretations

- **Bunny LowPoly #293137 (Badia):** binary STL, 292 triangles and 148 vertices, 438/438 edges with exactly two face uses, 1 connected component, all 148 vertex links single cycles, zero degenerates, duplicates or winding conflicts. Source mesh is **a clean manifold geometric control** by these tests, **not a published QUAD comparison target**.
- **Input Pinion #37881 (Badia):** binary STL, 3,400 triangles and 1,700 vertices, 5,100/5,100 edges with exactly two face uses, 1 connected component, all 1,700 vertex links single cycles, zero degenerates/duplicates/winding conflicts. A second regular **feature-geometry** control, again **not** a direct published QUAD output pair.
- **Millennium Falcon Top #61394 (QuadWild):** the original compressed payload is **ASCII STL** (not binary), 6,747 triangles, 3,367 vertices, 4 components, 87 1-face edges, 9,979 2-face edges, **48 3-face edges, 13 4-face edges**, 86 singular vertex links, 72 zero-area faces and 1 duplicate triangle. There are 61 high-incidence edges **in the coordinate-reconstructed raw source mesh**. This is **not yet evidence of 61 intentional multi-sheet CAD junctions**, because degeneracies and duplicate facets coexist; preserve them as adversarial input features and explicitly document any future repair.
- The source mesh **edge winding conflicts** count is 0 for all three in this specific two-face orientation check; this does not imply all global 3+-incident neighborhoods are consistently oriented.

**Critical nuance:** a QuadWild original model can be an invalid/non-manifold triangle soup even when the authors show a valid remeshed QUAD output. Comparisons must retain the original input hash, the comparator's actual preprocessing and the exact postprocessed mesh, not merely compare their published Table 1 scalar scores to unrelated APMesh stages.

## New audited reproducer and tests

- `probes/zip_stl_probe.js`: dependency-free bounded ZIP (single-entry, central-directory and CRC32), base64, DEFLATE, SHA256, STL binary/ASCII exact-coordinate incidence and vertex-link auditor. Original live file objects were analyzed using the GitHub connector and this **same byte-verified source implementation**.
- `probes/thingi10k_zip_audit.cjs`: local fail-closed Node.js 20+ CLI, requiring an **expected Git blob SHA-1** and the **decompressed original STL SHA-256**. Generates a JSON receipt using exclusive-write semantics. No mesh repair.
- `probes/test_thingi10k_zip_audit.cjs`: **16/16 synthetic adversarial unit tests passed locally**, including SHA cross-check against Node crypto, ZIP/CRC/central directory integrity, stored/deflated ZIPs, binary/ASCII STL cases, 3-face edge, duplicate faces, topology/vertex links, file-ID matching, mutation and atomic receipts. Actual mirror STL ZIP objects could not be materialized in the isolated local execution container; the three real ZIP objects **were actually decoded and analyzed through the GitHub connector execution environment**, with source Git blob SHA matched.
- [Real 3-model JSON receipt](evidence/thingi10k/thingi10k_f16_raw_stl_topology_3.json) stores original unmodified source hashes, full raw topology metrics and limitations, **without the third-party STL/ZIP bytes**.

To reproduce locally using a separately obtained authorized ZIP from the *pinned mirror revision* (example #293137):

```bash
cd docs/research/nonmanifold-benchmark/probes
node --test test_thingi10k_zip_audit.cjs
node thingi10k_zip_audit.cjs \
  --zip /private/authorized/293137.stl.zip \
  --file-id 293137 \
  --expected-zip-sha1 359c26b16664e9ba8d2415ca065a85bd27504d5f \
  --expected-stl-sha256 4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a \
  --output /private/new_receipts/293137.json
```

## Blocked gates, next work

1. **Larger QuadWild clean-pilot IDs #67792 and #94884** were independently identified in their public mirror repositories, but the connected API delivered no binary payload in this execution. No source bytes, SHA-256 or native topology is claimed for them yet. Use an authorized bounded downloader in an environment with normal network access, pin byte hashes, then perform this same gate.
2. Validate **per-object author license** and permitted redistribution of all source/derived assets, respecting the #230923 No-Derivatives hold. The mirror-declared licenses are not independent legal clearance.
3. Establish actual **published QuadWild reference output pairs** for all twelve IDs. The 4.4-GB aggregate archive has not been inspected/extracted here; neither `#61394` nor any other ID may be counted as a verified reference-output match.
4. Design source-feature recovery and charted bicubic Bézier approximation for the **two clean small Badia controls**, declaring whether a strict four-sided atlas is possible and how approximation error/feature fidelity will be measured.
5. Only then perform accepted **APMesh C++ TRI / supported QUAD** generation and paired, target-resolution-matched QUAD comparison (quality, invalid/negative cases, runtime and pre-processing). Keep actual 3+-sheet original-source intended junction and reconstructed Tsh249 proof as different scientific claims.

**No existing M5/S40/S27/M3/Book/Eistute/Decor Shelf/Tsh249 artefact was changed. S40 remains 156 indexed Bézier patches / 22 of 43 original STEP faces. Draft PR #225 and `main` barriers unchanged.**
