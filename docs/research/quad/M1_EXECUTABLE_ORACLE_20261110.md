# M1 executable Figure 7 schematic oracle — 2026-11-10

**Research-only candidate; scientific approval remains pending.**

This iteration does **not** replace the existing `uv_contracts.cpp` C++ D4 tests. It adds a second, independently implemented **exact-rational Python checker** that reads the already committed [Figure 7 transcription](evidence/M1_FIGURE7_TRANSCRIPTION_20261108.json), checks its pinned normalized geometric convention, graph cycles, inferred class order **T1,T2,T4,T3,T5,T6**, and verifies all six cases under eight D4 transformations.

For each of the resulting **48 oriented graphs**, the checker builds two different *test-only witness* QUAD subdivisions with exactly rational coordinates: the arithmetic mean of polygon vertices and the signed-area polygon centroid. It independently checks strict convexity, opposite edge incidence, unique vertex positions, shared midpoint identities, no hanging vertices, crossing edges, disk Euler invariant, exact unit area and each historical graph's 4/11/12/8/11/16 expected quadrilateral counts. This yields **96 witness subdivisions**, not 96 new physical production meshes. Both rules are intentionally evaluated to expose their ambiguity. In particular:
- T2 `ABOW` vertex mean **(3/8,1/4)** differs from area centroid **(7/18,2/9)**.
- T5 `WSND` vertex mean **(1/4,5/8)** differs from area centroid **(5/18,11/18)**.

The checker also verifies all **16 split signatures** partition into class orbit sizes (1,4,4,2,4,1) and rejects nine deliberately altered examples: missing/reversed/duplicated/repeated polygons, invented collinear T5 center, collapsed edge, outside/boundary witness and swapped labels. The original JSON's recorded source SHA-256 is **metadata only**; the checker does **not** download/re-hash the scanned PDF or establish independent visual agreement with the scan.

Run via the new independent `quad.m1.figure7.oracle` CTest under both the Linux GCC and Windows MSVC standalone QUAD matrices. Existing C++ emitter tests and the TRI scientific parity gates remain mandatory. The checker is deliberately separate from the legacy AFT, application, and production `quad_uv` mode.

**Decision still required from Bento/Creto:** confirm the Figure 7 graph transcription, discuss normalized embedding and explicitly choose (or reject) a numerical point policy with analytical/degeneracy rules. No production mode, unqualified historical centroid, fully conforming boundary, UV→XYZ element, multipatch or repeated adaptation is declared.
