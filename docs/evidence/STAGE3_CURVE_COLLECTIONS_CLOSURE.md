# Stage 3 slice 8 closure

Head `2c7edff9070810ea8e27574e4449aeebf369824e` integrated through PR #30 as main
`587c91923b48d7f55414df720d29bcb1d2dacc11`, preserving complete tree
`914030fb831c060cfe980c912b3aa5eec0ecb776` (942 blobs). Full exact-head and
implementation-main campaigns pass: CTest 18/18, zero skips, 74 Python controls,
curve 19/19, UV 81/81, node 7/7, two-unit lint, range/probe formatting, inventory
and strict repeated Eistute/Book regression. All nine attempted states, measured
shared incidences, acceptance/rejection, 189 CSV fields and 1,168/4,256 final
accepted triangles remain exact.

The original partially overwrites live values in both populated-growth setter
cases at denied ordinal 7. Each setter now swaps its prepared input, preserving
live values/nodes and lvalue caller inputs on failure. Fourteen setter/copy
sweeps deny 76 calibrated allocations with preserved state and successful retry. Original/repaired normal ordered traces match. Successful
allocation counts and node reuse deliberately change: the second copy is removed
and old nodes are destroyed after swap. Borrowed points/patches remain external
owners' responsibility; old element observers are invalidated on success.

This exceptional-exit defect repair changes no scientific expression, ordering,
input, tolerance or adaptation/acceptance/stopping policy. Three explicit local
override annotations unblock unchanged lint rules; failed setup and lint logs
remain retained. C07/ADR-0009 limit the two independent transactions; they do
not form a joint point/parameter update. See STAGE3_CURVE_COLLECTIONS.md for
reproduction and the original failures.

## Explicit closure audit

- Code: the two setters swap prepared standard lists; their public function
  types remain unchanged. Three local overrides become explicit. Successful
  allocations/node reuse/destruction timing deliberately change; ordered
  values, borrowed object ownership and scientific policies are preserved.
  Historical source, vendor, licenses and attribution remain untouched.
- Tests: full exact implementation head/main campaigns pass 18 CTest tests,
  zero skips and 74 Python controls, curve 19/19, UV 81/81 and node 7/7.
  Fourteen normal setter variants, two normal pointer-taking copy controls,
  14 independently calibrated sweeps and all 76 measured denials are observed.
  ASan UAF, CRT retention and denial-hook negative controls retain the expected
  diagnostic response. All old UV/node negative controls remain required.
- Contracts: C07 defines per-list failed values/nodes, caller ownership and
  successful element-observer invalidation. Point/parameter transactions remain
  independent. Production inventory stays 123 C++ files (57 units, 66 headers),
  six CMake inputs, 22 contracts and 98 anchors; semantic review remains distinct
  from lexical anchor existence. The six-header cycle remains known debt.
- Documentation: state, plan, worklog, quality commands, architecture sequence,
  ADR-0009, original diagnostics and compact reports describe scope and limits.
- Scientific scope: same final normal traces against original and exact
  entry/head/main article outcomes, all nine attempted states, positive shared
  incidence coverage, zero measured position gap and 189 named CSV fields.
  Accepted steps stay 0/1; rejected Eistute 2/3/4 and Book 2/3 remain visible.
  Last accepted triangles remain 1,168/4,256. No threshold or verifier changes.
- Failure/coverage inventory: two original populated-growth failures remain;
  17 other original outcomes are as expected, including deliberately invalid
  controls. Two initial probe include-order build failures and the required
  missing-override lint failure and raw-log publication whitespace failure
  remain retained. The repaired fresh campaigns pass unchanged rules. Rvalue success is not a denial sweep; CRT retention is
  scoped and not a full-process leak claim. The pointer-taking parametric
  constructor's omitted parameter sequence remains a static semantic finding;
  copied sequence/value semantics, implicit copy/assignment and derived curves
  are not qualified. Other ownership/retry/parallel limits remain below.

## Retained evidence and documentation-only gates

stage3/curve_collections/head_qualification.json and main_qualification.json
retain complete implementation results, commands and raw-log identities.
source_identities.json identifies all 510 qualified inputs. Original normal and
replacement case logs, the 460-blob snapshot map, toolchains and failed setup/
lint reports are retained.
Original deliberate-negative raw diagnostic logs remain local with hashes, as
recorded in original_raw_log_inventory.json. Large current instrument and
verbose CTest/JUnit logs remain local with hashes; no full raw campaign archive
is claimed.

This follow-up changes documentation/evidence only. Its published complete
remote/local Git tree and exact working bytes must match; all qualified source,
tool, test, build, input and contract identities must stay unchanged. CTest
18/18, zero skips and 74 controls, inventory and diff/whitespace checks must
pass on its exact head and again on final main. Full numerical/instrument
campaigns already passed at the exact implementation head/main on those same
compiled inputs. Final documentation commit/tree/log hashes go on the closure
PR and issue #29 to avoid a self-referential repository commit. No hosted
check/status contexts or Actions are configured; absent checks are not green CI.

## Remaining work

Full stage 3 remains open with eight qualified slices. Next characterize the
remaining curve constructor/mutation contracts, including the pointer-taking
parametric constructor's omitted parameter sequence, before shared sample
ownership, initialization and rollback. Current constructor controls qualify
unwind, borrowed collections and selected initialized scalar/coefficient state;
full value-copy semantics are not claimed. General observers, joint updates,
other helpers/templates/tree/mate paths, failed-tree observer consumption/retry
and full-process/parallel/LSan/UBSan qualification remain open. Stages 0-2 stay
closed; stages 4-11 stay pending. Doxygen undocumented-API debt stays stage 8.
