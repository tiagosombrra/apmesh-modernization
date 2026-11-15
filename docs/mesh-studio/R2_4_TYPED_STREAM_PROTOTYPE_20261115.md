# Mesh Studio R2.4 — Typed V2 display streaming and synthetic 500k preflight

Date: 2026-11-15. Source branch: `feature/mesh-studio-fixture-first-20261114`.

## New transport

`APMSH002` is a strictly bounded, source-sha-bound, little-endian Float32
**rendering** protocol. It is NOT the original double-precision APMesh mesh.
Original face IDs, native TRI and QUAD cell arities and the original OBJ
SHA-256 are preserved and checked, with a transport CRC32. CRC32 is a wire
error detector, not a cryptographic proof of scientific provenance.

Header: 32 bytes (`<8sIIIIII`: magic, UTF-8 metadata length, number of vertices,
number of faces, polygon word count, 4-byte metadata padding, reserved flags
zero). Then canonical JSON metadata, zero padding, XYZ Float32 tuples, native
VTK `UInt32` cell words, original `UInt32` face IDs, `UInt8` native cell
arity 3/4, and a final little-endian CRC32 over all preceding bytes.

The server prevalidates the entire input before streaming any bytes,
computes a total response length capped at **32 MiB**, and yields bounded
64 KiB chunks. It does NOT remove existing Python `geometry()` internal
allocation; it avoids an additional whole-message Python `bytes` copy.

The JavaScript decoder validates byte lengths, CRC, metadata, native face
arity and indices, exact one-to-one source face ID permutation and finite
vertex coordinates. It returns zero-copy `Float32Array`, `Uint32Array`, and
`Uint8Array` views plus one face-offset index instead of rehydrating nested
vertex/face JavaScript arrays. The original binary V1 endpoint remains
available for compatibility and independent comparisons.

## Scientific isolation

For the source P1 and four staged candidates, the web service still verifies
original OBJ SHA-256 against a curated catalog. Staged candidates are NOT
accepted adaptive epochs. V2 has no power to infer a patch from its
coincidental vertex XYZ or UV, to weld nonmanifold seams or to certify
continuous derivatives, all-QUAD, anisotropy or a physical PDE solution.

## Synthetic 500k

The `/bench.html` synthetic scene now creates typed buffers directly,
sharing native QUAD connectivity and original synthetic face indices across
XYZ and UV. Its explicit original-source SHA is **all zeroes**, and its
semantic provenance is `NOT_APMESH_SOURCE`, so it cannot be mistaken for a
real APMesh result. This also avoids 500k nested 4-corner JS face arrays
per viewport. An actual two-viewport browser WebGL stress and the Windows
GPU test remain separate empirical gates. One *first-render* event does not
certify sustained FPS or native GPU memory. Any lower-resolution LOD is
outside this change and must have an explicit parent-source-ID mapping.

## Qualification gates

1. Python original scientific suites plus V2 unit/negative tests on Linux and Windows.
2. Chromium TypeScript build and typed V2 roundtrip vs source P1 JSON in UV and XYZ.
3. Chromium image/cell picking of the real P1 in packed mode; index fallback
   retains source IDs and previous scientific sidecar classification.
4. Chromium 500k direct typed-buffer allocation without GPU (regular gate).
5. 500k **actual WebGL** stress is separately run with explicit timeout and
   resource limits; no claim before successful CI evidence exists.

No generator C++ code, scientific source branches, or release process are
changed. No installer is implied by the successful browser CI.
