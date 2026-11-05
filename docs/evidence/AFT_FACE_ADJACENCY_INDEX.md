# Temporary AFT face adjacency index

Classification: engineering-only traversal optimization. This package continues
the unintegrated adaptive-reuse candidate; it changes no scientific policy.

`improveMesh` now constructs one scoped, non-owning face-incidence index for its
topology-stable smoothing passes. Each vertex's list follows the original mesh
sequence. Repeated mesh entries remain repeated; repeated endpoints within one
entry contribute once, matching the former OR predicate. Missing vertices return
an empty list. Hash iteration never drives a reduction or a vertex update.

All three smoothers borrow these ordered lists. Face quality, coordinates and
scores are evaluated live in the original order; no numerical values are cached.
The index is destroyed on normal return or unwinding and is rebuilt on the next
call. It owns only its containers, never vertices or faces. Construction and stored
incidences are O(F) expected; vertex lookup is O(1) expected instead of rescanning
all F faces for each inner vertex in every smoothing pass. Local face reductions
and edge-adjacency work remain unchanged.

The existing smoothing-adjacency control now compares against the original scan
predicate, including ordered duplicates, repeated endpoints, null vertex keys,
missing vertices, empty meshes, live values and a rebuilt scope. Existing native
AFT context checks use the same explicit index. A source comparison against
`df00fa24eac88a918a610ed933f117f7590cd0d7` permits only the scoped index, adjacency
bindings, const iterators and removal of the old scan; all remaining implementation
tokens, formulas, decisions and reconstruction operations are identical.

## Bounded validation

Artifacts and exact commands: `build/aft-face-adjacency/`.

- Canonical GCC and checked MSVC C++17 builds pass with unchanged build settings.
- Existing CTest: 75/75, including 389 nested Python controls and original negative
  controls. No new test target or model.
- Existing MSVC initial serial-reuse control passes.
- Eistute GCC: five states, 25 exact scientific artifacts and 15 independently
  compared boundary incidences; accepted 0/1, rejected 2/3/4 match the frozen run.
- Scoped clang-tidy, explicit token-preserving formatting, source preservation
  and architecture inventory/contracts checks pass.

The first proof attempt rejected an extra blank line removed by explicit formatting;
its diff is retained. Analysis setup also rejected an ambiguous multi-target
compilation-database selection and shell-damaged filter JSON. The corrected
analysis uses the actual engine/probe commands and structured argument passing;
these setup failures are retained separately from successful analysis.

## Same-case checked MSVC observation

One Eistute process only, with the original two-call native reuse command and the
same 300-second cap for both calls together. The exact original configuration
hash is `635fc49c6c9275ee64464f86443c66bc059bc5663a61292d5e3224440bdb213d`.
Input, Debug iterator checks, scientific settings and assertion hook are unchanged.
The new executable is rebuilt from the authorized production change. Old binary,
PDB, timeout reports and partial output remain preserved; the old live output is
temporarily archived and restored byte for byte after this observation.

The process reached the fixed deadline at 300.008 s (300.016 s including process
termination). The first call completed successfully: its archived output has five
independently verified states and 15 positive boundary comparisons, accepted 0/1
and rejected 2/3/4. The second live directory proves the first returned zero: the
unchanged observer starts that directory only after checking the first return.
All 18 available per-step artifacts from the old incomplete first call remain
byte-identical. The second call reached step 4 but did not return before the total
cap; its partial output remains negative evidence. The buffered outer stdout was
not flushed on termination, so no native return-marker/count comparison or exact
first-call timing is claimed. The old runtime-summary timer is not used as a
stopwatch. This demonstrates first-call completion under the fixed observation,
not a qualified two-call speedup or complete adaptive reuse.

The initial output verification rejected missing input-identity metadata. That
metadata was supplied from the pinned original input and verification then passed
for the completed first call, without another generation. Both reports are kept.
`msvc-eistute/process.json` and `msvc-eistute/verification.json` retain the timeout,
binary/configuration/input hashes, commands and measured coverage.

Book is not rerun in this package. Its required revised-head adaptive qualification
and the other unmeasured delivery gates remain open; this package alone does not
authorize integration or close Stage 3.
