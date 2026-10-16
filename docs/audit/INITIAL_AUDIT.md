# APMesh article-lineage audit and regression

Date: 2026-10-15. Status: **AUDITED WITH OPEN BLOCKERS**.

## Executive decision

Modernize the implementation in a separate repository while preserving the
published algorithm as an identified reference. Do not yet describe the
application as leak-free, fully portable, scientifically validated by its
current verification scripts, or performance-qualified.

This audit produced real builds, repeated model executions, ownership probes,
an independent accepted-state analysis, and a bounded engineering patch.
It did not complete the architecture/English migration or change the meshing
technique. It did not modify or publish changes to the historical repository.

The highest priorities are reliable success/failure and accepted-state
reporting, ownership, and executable regression. Doxygen and English migration
belong in the modernization, but are not substitutes for those checks.

## 1. Source and audit envelope

- Repository: https://github.com/tiagosombrra/adaptive-nonmanifold-meshing-grsi
- Commit: `a2d644ca6abf87628b6b5477602c1c7d4101b599`.
- This is the article's GRSI replication lineage, not the current private
  adaptive-patch-meshing branch and not the greenfield apmesh-core.
- Recovered and verified 511 exact Git blobs, including vendored Eigen,
  first-party sources, model/configuration inputs and archived mesh reference.
- Excluded only `paper/preprint.pdf` and `assets/grsi_representative.png`.
  They are not build/model-regression inputs. This is not a full archive claim.
- First-party inventory: 117 C++ source/header files, 37,929 lines.
- GCC 16.1.0 from MSYS2 UCRT64; native Windows Release; MPI disabled,
  OpenMP disabled for the serial reference; LTO disabled; C++17 preserved.
- A separate OpenMP build and one Eistute process with two threads were tested.
- MSVC 19.44.35229 / VS 2022 Build Tools was used for isolated Debug CRT probes.
- Full MSVC AddressSanitizer/Debug CRT application builds were attempted and
  failed on portability defects. No full-application sanitizer run is claimed.
- WSL access returned `Wsl/E_ACCESSDENIED`. Direct Git networking failed DNS;
  exact blobs were recovered through the connected GitHub interface instead.

The work combines repository-wide structural inventory, focused ownership and
critical-path source review, and the listed dynamic experiments. It is not an
exhaustive line-by-line proof of all 37,929 lines or all input paths.

## 2. Regression results

The archived Eistute reference check passed: 7,184 TRI, normalized error
0.036712, error reduction 96.3288%, and 58.6303% with q >= 0.60.
That check validates the archived JSON/CSV/OBJ relation; it does not by itself
validate a newly generated accepted mesh.

| Execution | Process outcome | Last accepted adaptive state | Historical verifier |
|---|---|---|---|
| Eistute, serial A/B | Exit 0 both times | Step 1, 1,168 TRI | Passes on step 4, 7,184 TRI, which the run itself rejects. |
| Book, serial A/B | Exit 0 both times | Step 1, 4,418 TRI | Fails because configured stage 4 is absent; generation stops after rejected candidates. |
| Decor Shelf, serial A/B | Both exceed the declared 300-second budget | Step 1, 458 TRI, before timeout | No completed stage-5 result. Neither process is a scientific PASS. |
| Eistute, OpenMP, two threads | Exit 0 | Step 1, 1,168 TRI | Same rejected step-4 artifact is recognized. |
| Candidate fixes, serial Eistute | Exit 0 | Step 1, 1,168 TRI | Same historical verifier behavior. |
| Candidate fixes, serial Book | Exit 0 | Step 1, 4,418 TRI | Same historical verifier failure. |

Nine generation processes were observed: six serial-reference processes,
one OpenMP Eistute process, and two candidate processes. Both Decor processes
timed out. Their already written outputs are partial evidence, not completed
generations. Mesh files written before both timeouts match byte for byte.

All generated OBJ files for repeated serial Eistute and Book match byte for
byte. The candidate produces the same five Eistute and four Book OBJ files as
the serial reference, including identical accepted/rejected classifications.
The two-thread Eistute OBJ files also match the serial files in this envelope.
This is bounded evidence, not proof of general equivalence or race freedom.

The independent basic OBJ checks cover finite vertex coordinates, triangular
face cardinality, distinct indices within a face and index bounds. They do not
certify element orientation everywhere, surface approximation, intersections,
topological correctness or shared-curve compatibility.

### Accepted state versus archived artifact

Eistute writes `accepted=0` for step 4, even though its 7,184 triangles satisfy
the historical verifier. Its accepted steps are 0 and 1; steps 2, 3 and 4 are
rejected. The artifact reproduction and the accepted-state claim must therefore
be separate checks. This finding does not independently establish that the
published article is wrong. It requires tracing the article's selected state,
the archived snapshot and the current package's acceptance semantics.

Do not change acceptance thresholds to make the 7,184-triangle state pass.

### Compatibility coverage

The completed serial Eistute and Book compatibility CSVs report zero mean/max
error with `compared_groups=0`. No positive compatibility-measurement coverage
is established by those zeros. Source inspection confirms the writer only
increments the comparison count for eligible grouped curve objects; this is
not an independent inspection of every patch-incidence boundary after rebuilding.

The shared-curve construction may still enforce compatibility structurally.
The correct conclusion is that this reporter does not demonstrate its
preservation on the completed meshes. A new checker must follow curve
identity, local orientation, matched samples and boundary segments per incidence.

## 3. Memory evidence and bounded corrections

Debug CRT checkpoints were taken around isolated ownership operations, with
scope destruction before the second checkpoint. A successful explicit-owner
control was included. The two original failures were repeated with identical
allocation counts. These are small component experiments, not full-process
leak measurements.

| Probe | Original code | Corrected candidate / safe API use |
|---|---:|---:|
| `SetNoh(new NodeAdaptive(...))`, following its original header's ownership-transfer description | 3 retained normal blocks / 136 bytes | The description is corrected: SetNoh copies, caller retains ownership. A scoped source produces 0 retained blocks / 0 bytes. The raw-new expression still requires a caller owner. |
| `InsertSubMeshAdaptiveByPosition(new SubMesh(), -1)` | 3 retained normal blocks / 104 bytes | 0 retained blocks / 0 bytes after acquiring ownership before index validation. |
| `AddNoh(make_unique<NodeAdaptive>(...))` control | 0 / 0 | 0 / 0. |

The header/implementation mismatch is important: changing SetNoh to own every
argument would risk deleting shared or borrowed nodes. The patch preserves its
copy behavior, documents that behavior, and removes two actual heap temporaries
used only as copy sources for the coarse central node. Other shared curve
sample lifetimes remain open work.

### Patch contents

`bounded-engineering-fixes.patch` changes six files:

1. Move NOMINMAX before the first Windows header to prevent macro pollution.
2. Replace the compiler-specific long maximum in Quadtree with the standard
   numeric limit for the same type.
3. Make the existing pi value available in discrete-curvature calculations on
   MSVC without changing the numerical value observed by GCC.
4. Acquire SubMesh ownership before an early return on a negative index.
5. Correct the SetNoh contract and add focused English Doxygen documentation.
6. Use scoped central-node copy sources in both coarse-mesh code paths.

No model, factor, threshold, curvature-error formula, boundary adaptation,
quadtree template, advancing-front insertion, acceptance or stopping rule is
changed. `git apply --check` succeeds against the identified baseline.

The patch is a validated candidate for the stated GCC cases and isolated
ownership probes. It is not merged, not a complete modernization, and not a
solution to all memory findings.

### Remaining memory risks

- Boundary samples created during adaptation, restoration and initial meshing
  need one explicit owner across their shared uses, replacements and rejection.
- The load-estimation code contains allocations immediately overwritten by
  addresses of local objects. The reviewed block also downcasts pointers to
  actual PointAdaptive objects as NodeAdaptive pointers. These paths need
  independent lifetime/type-safety corrections and coverage.
- AFT/Quadtree ownership is coupled: Quadtree destroys its boundary, while
  AdvancingFront destroys Quadtree. Replacing either object must preserve that
  ownership relation; adding blanket deletes is unsafe.
- Public list getters advance and dereference without bounds checks; currently
  valid workload use does not prove safe behavior on invalid positions.
- History retention, rejected candidates, adjacency observers and exceptional
  exits need memory-growth and cleanup checks in long runs.

## 4. Prioritized findings register

P1 means a release-blocking correctness, safety or evidence problem for the
intended claim. P2 is important engineering debt. Confirmed source findings
are distinguished from dynamic observations and further investigation.

| ID | Priority | Finding and evidence | Required action |
|---|---|---|---|
| A01 | P1 | A missing BP model returns process exit 0, writes an empty step-0 mesh and reports target_error_reached. Dynamically reproduced. | Fail before generation, use nonzero status and test empty/malformed inputs. |
| A02 | P1 | Eistute verifier recognizes a step marked rejected. Dynamically reproduced twice. | Validate artifact reproduction and accepted-state semantics separately. Trace publication-state provenance. |
| A03 | P1 | Zero compatibility result with zero compared groups. Dynamically reproduced. | Report NOT_COVERED, implement incidence-level verification and negative controls. |
| A04 | P1 | Copy/ownership contract mismatch and negative-index leak. Isolated CRT experiments. | Candidate fixes supplied; finish ownership migration without changing shared semantics. |
| A05 | P1 | Unowned central copy sources; overwritten allocations and unsafe downcasts in load-estimation code. Source-confirmed, uneven path coverage. | Fix each owner/type path separately and add meaningful lifetime coverage. |
| A06 | P1 | Full memory-sanitizer build blocked on nonstandard C++ VLAs and platform dependencies. MSVC build evidence. | Port storage with correct semantics, then execute full ASan plus leak coverage. |
| A07 | P1 | Internal timing can report about 1.79e9 seconds for a process measured in seconds; Book error_evaluation exceeds total wall time. Observed. | Audit start/end pairing and initialization; use a monotonic clock and consistency checks. Do not use current timing for speedup claims. |
| A08 | P1/P2 | Decor Shelf does not complete within 300 seconds in either observed run. | Profile in an isolated environment, record where progress stops, distinguish expensive work from nontermination. Do not count partial output as pass. |
| A09 | P2 | CTest discovers zero tests in the GRSI build. | Register actual tests and fail CI on empty discovery. This finding is specific to the audited snapshot. |
| A10 | P2 | CMake run targets reference a missing Book input and a removed positional-argv interface. | Repair/remove obsolete convenience targets, preserving the historical run recipe. |
| A11 | P2 | All source files are globbed into one executable. | Introduce a library/CLI seam and explicit responsibilities, preserving algorithm ordering. |
| A12 | P2 | Generator implementation is 8,096 lines; definitions header has 921 lines; communicator implementation has 3,746 lines. | Separate configuration, ownership, orchestration, policy, evaluation and IO incrementally. |
| A13 | P2 | Inventory finds 398 extern declarations, 165 parent-relative includes and 42 using-namespace occurrences. | Reduce global state and header coupling; counts include comments and are not independent defect totals. |
| A14 | P2 | GCC build emits 285 warning occurrences, including 45 VLA warnings. | Triage unique diagnostics, fix project issues and classify vendor warnings separately. Do not silence the entire warning surface. |
| A15 | P2 | Mixed English/Portuguese identifiers, messages and comments; 769 language-candidate lines in a heuristic scan. | Review and translate first-party material; preserve external interfaces through aliases/versioning. The count is not a translation-completeness score. |
| A16 | P2 | No Doxyfile/documentation target in the audited tree. | Add English API and architecture/ownership pages, then build/review the actual generated documentation. |
| A17 | P2 | Native MSVC also exposes Windows macro ordering, GCC-specific limits and unavailable M_PI. | Three bounded corrections supplied; broader VLA portability remains open. |
| A18 | P2 | IDs, sizes and limits cross platform-dependent integer types. | Audit conversions and Linux LP64/Windows LLP64 boundaries before widening support claims. |
| A19 | P2 | Raw-pointer ordering is used in some geometric bookkeeping. | Audit portability/determinism; do not infer a measured failure solely from this source pattern. |
| A20 | P2 | Missing-model diagnostics are emitted to stdout, and English CLI consistency is absent. | Define stable errors, stderr use and exit codes as an interface migration. |
| A21 | P2 | Parallel coverage here is one two-thread Eistute run. | Add repeated thread counts and bounded race/determinism checks; keep MPI a separate claim. |
| A22 | P2 | Third-party notices explicitly describe Eigen, while integrated CRABMesh needs provenance review. | Preserve authorship and check redistribution terms before a new public repository. No infringement is alleged by this documentation gap. |
| A23 | P2 | Existing reference checks do not independently certify geometry/topology/quality. | Add meaningful mesh checks with explicit coverage and acceptance joins; keep the historical metric named. |
| A24 | P2 | Many allocations occur in geometry, adaptation and communication. Inventory alone cannot rank cost. | Profile allocation and rebuild workloads before caching or changing containers. |

## 5. Architecture, English and Doxygen acceptance

The accompanying `MODERNIZATION_PLAN.md` defines M0-M6. Its purpose is to
integrate CRABMesh coherently with the application, not flatten source folders
or replace the existing interior algorithm.

The new repository should have English first-party source comments,
documentation and user-facing diagnostics, a stable terminology map, clear
owners/observers, a reusable library boundary, reproducible presets and real
regression gates. Keep old public config/CSV/file naming contracts recognizable
until a deliberate migration is provided.

Doxygen must document domains/units, ownership, nullability, orientation,
preconditions, results and failures, and the relationship to the article's
pipeline. Do not count extracted symbols as documented contracts.
`EXTRACT_ALL=YES` suppresses undocumented-member warnings according to the
[official configuration documentation](https://www.doxygen.nl/manual/config.html).
The provided `Doxyfile.in` is a template, not generated/reviewed HTML.

## 6. Memory-tool and performance limitations

Windows AddressSanitizer and Debug CRT are different instruments. ASan on
Windows is not a substitute for a successful Linux LeakSanitizer campaign.
The Microsoft documentation treats ASan and future leak/undefined-behavior
sanitizers separately:
https://learn.microsoft.com/en-us/cpp/sanitizers/asan

CRT checkpoints here cover allocations tracked by the Debug CRT in isolated
probes. Documentation of these APIs:
https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/crtsetdbgflag
https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/crtdumpmemoryleaks

The full application sanitizer build was **BLOCKED**, not PASS. MPI, Linux
LSan/UBSan, TSan and a completed full-application leak campaign were not run.
Uninstrumented runs reporting no ASan string must never be interpreted as an
ASan pass.

The observed wall times include contention with other audit builds and have
different instrumentation/configuration costs. They diagnose impossible
internal timing and enforce the declared timeout. They do not establish a
performance ranking or speedup for the patch or OpenMP.

## 7. Completion status and next delivery

| Work | Status |
|---|---|
| Source provenance and structural inventory | Completed for the stated 511-blob envelope. |
| Serial build and repeated article-config execution | Completed with explicit failures/limits. |
| Accepted-state and compatibility-coverage audit | Completed; blocking gaps identified. |
| Isolated ownership probes | Completed with repeated failures and passing controls. |
| Six-file engineering candidate | Prepared and GCC-regressed on Eistute/Book; isolated corrected probes pass. |
| Full sanitizer/leak qualification | Blocked; not complete. |
| Complete architecture/English/Doxygen migration | Planned; not implemented in this audit. |
| New GitHub repository, PR or upstream integration | Not created/published by this audit. |
| Scientific mechanism changes | None performed. |

The next bounded implementation should establish trustworthy failure and
accepted-state regression, finish memory ownership for active paths and enable
the full sanitizer campaign. Architecture extraction and English/Doxygen
migration should follow in reviewable pieces under the same baseline.

The release objective remains: an effective, maintainable implementation of
the agreed technique with no memory findings in its declared validation
envelope. That objective has not yet been reached, and this report does not
substitute documentation or successful compilation for it.
