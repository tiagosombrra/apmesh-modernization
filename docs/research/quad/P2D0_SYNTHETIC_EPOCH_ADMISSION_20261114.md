# P2d-0 — metadata-only mixed epoch preflight

Date: 2026-11-14. Tracking: [R3/M7 issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## What this change actually tests

This is an isolated C++17 **synthetic receipt** contract. It is deliberately not
called from the application and does not publish, clone, adapt or replace a real
`SubMesh`. It is designed to reject obvious false-positive epoch claims before
future application integration.

The `MixedEpochPreflight` receives an initial metadata receipt for epoch 0,
then checks subsequent receipts for:

- valid SHA-256 *syntax* (NOT actual file-byte verification);
- unchanged source model, boundary hash, number of original boundary edges,
  and named metric policy between epochs;
- exact parent-mesh identity and contiguous epoch number;
- changed physical OBJ hash **and** changed typed topology hash;
- nonzero claimed native quadtree edits (only metadata, not independent proof);
- finite and positive physical Jacobian/area witnesses, nonempty TRI and QUAD
  counts, nonempty native AFT and independent-oracle claims;
- strictly decreasing normalized research error (a provisional monotone
  rule, NOT an approved universal quality or efficiency decision);
- exception-safe append of metadata, leaving the prior record unchanged
  on invalid input or failed allocation.

This gate is metadata-only: claimed hashes are not independently attested,
and a nonzero claimed tree edit does not prove that a Quadtree changed.

The native test uses **fabricated** hashes and a fabricated sequence of three
metadata states with two transitions, plus **14 targeted negative witnesses**.
A passing test prints `synthetic_states=3` and
`actual_adaptive_epochs=0`. The synthetic transitions are never evidence of
P2/R3 or M7 completion.

## Known gaps: required before any real accepted epoch claim

1. Bind the receipt fields to immutable, hash-verified actual source BP bytes,
   real Quadtree change logs, exact patch/curve intervals, typed physical owner
   hashes, OBJ bytes and independently checked output.
2. Define an approved quality/error metric for TRI and QUAD; the monotone
   normalized-error rule here is a **test policy only**.
3. Make candidate generation depend on the **previous accepted mixed mesh**
   and actually invoke native template dispatch/AFT at the next state.
4. Validate the candidate and fail injection **before atomic owner and output
   publication**, with explicit candidate/accepted/rejected statuses.
5. Demonstrate at least **two further genuinely distinct mixed accepted
   adaptive epochs**, with exact Linux/Windows, ASan/UBSan/leak, native,
   independent geometric and scientific baseline regression gates.

No production TRI, `main`, source curve sampling, all-QUAD, anisotropy,
original 1993 reconstruction, continuous Jacobian or nonmanifold welding
is modified. Keep this PR in draft until exact-head native and baseline checks
are complete; status P2/R3 **OPEN**.
