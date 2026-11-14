# R2c-0: read-only original-source radial edge incidence and pending sheet policy

**Date:** 2026-11-12/13 UTC. **Status:** experimental implementation;
exact-head CI and source-linked artifact evidence must be inspected before
this stage is recorded as qualified. This is not approval for welding.

## Boundaries and dependencies

- The real original `GeneratorAdaptive` + `PatchReader` C++ source probe
  emits `R2C0_ORIGINAL_SOURCE_RING` on the same coherent epoch/retry as the
  qualified R2b2 signed Bernstein proof. It records the **actual original
  curve registry index**, original curve ID, exact source parameter knots
  (17 significant decimal digits), copied original physical node IDs and
  ordered `patch:side` radial incidence cycle. The source curves are *not*
  reconstructed from equivalent XYZ coordinates.
- The existing `test_generator_outcomes.py` requires that source marker's
  knot count, strict monotonicity, real physical node IDs, coherent
  epoch/retry, radial order and continuous proof status agree with the
  separately emitted original R2b2 sampled and Bernstein witnesses.
- Independent native `PatchReader` source incidence hypergraphs in
  `m4_sheet_incidence/` link each radial member to its actual physical
  curve, `curve_reversed`, and original UV boundary winding. The verifier
  checks both historically unapproved internal center rules produce
  exactly the same source identities and incidence records; their center
  choices cannot decide curve topology.
- Only **Eistute (one 4-valence curve, ten original source intervals)**
  and **Book (one 28-valence curve, twelve original source intervals)** have
  the continuous original high-valence Bernstein evidence required by this
  first R2c-0 implementation. The Ribbed Bracket's four valence-three
  junctions are still unqualified for continuous radial sorting; never
  report them as covered by this gate.

## Source records

Each interval record includes:
`curve_index`, `interval_ordinal`, exact start/end parameters from
source, the original source node IDs at each interval boundary and an
ordered list of *all* incident `(patch_index, side)` records. Each
incidence retains `curve_reversed` and `winding_sign` and exposes
`radial_next` as an **ordered geometric neighbor**, not a physical
`manifold_twin`. The latter is always `null` and node sharing remains
`NOT_AUTHORIZED`.

The entire result is anchored by exact original model bytes SHA-256, exact
original CTest log SHA-256, original M4 graph blob SHA-256, original epoch,
retry, source curve and interval numeric bounds. No pointer or temporary
C++ owner is serialized; every key is a value copy. The reproducible JSON
artifacts are written by `test_r2c0_source_radial_incidence.py` in
`build/local-serial/r2c0_radial_incidence/`.

## Fail-closed sheet policy

The policy validator requires the exact pending `schema_version=1` record:
source model hash, curve registry index, epoch/retry, all original curve
incidences with direction, `junction_kind=UNDECIDED`,
`approval_status=PENDING_ADVISOR_REVIEW`, null sheet IDs,
`node_sharing_policy=UNDECIDED`, **empty approved continuations** and
hashes of the source witness, M4 graph and canonical radial interval
record. Unknown fields or any change to those values must fail.

The script deliberately **does not accept a fabricated
`SCIENTIFICALLY_APPROVED` flag**, even if the source angular certificate
is complete. This stage validates a pending decision, not an approval
workflow. A later R2c-1 policy validator must bind actual advisor-
reviewed sheet/junction semantics to the exact immutable model and
produce negative controls for ambiguous pairings and contradictory
orientations before any physical node co-ownership can be considered.

Adversarial controls include wrong model/curve SHA, changed epoch/retry,
fabricated patch/side/reversal, duplicate incidence, unknown sheet ID,
attempted nonempty continuation, forged approval, forged radial digest,
and node-sharing override. At all times
`automatic_sheet_pairing_enabled=false`,
`physical_nodes_welded=false` and `physical_SubMesh_published=false`.

## Exact CI and limitations

The existing root CTest suite still executes original production source
and M4 independent physical models first. Afterwards a dedicated,
read-only `R2c0` GitHub Actions step consumes the retained verbose
source CTest log and exact M4 source graph outputs and uploads separate
14-day research JSON artifacts. Every failure returns nonzero and blocks
that CI job. The other native Linux GCC, Windows MSVC, Python tooling and
frozen original TRI regressions remain required unchanged.

No new application CLI option, production `SubMesh`, source curve
ownership, AFT behavior, original TRI operation or historical 1993
formula is introduced. R2c-0 does **not** demonstrate whole-surface
nonintersection or coordinated physical node identities across sheets.
The actual source `NodeAdaptive` observer lifetime and cross-patch
transactional rollback are R2c-2/R2c-3 obligations, not implied by
these read-only records.

**Next:** inspect exact CI source reports and negative-control counts,
record verified source model hashes/results and retain all unresolved
fields. Obtain explicit scientific junction semantics for the valence-4
Eistute axis and valence-28 Book spine before permitting any topology
policy that changes node ownership.
