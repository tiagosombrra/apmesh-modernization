# Stage 3 slice 35: initialized detached patch copies

Status: focused candidate passes; full exact-published-head/main qualification PENDING.
Entry main: `ace7abf0ce1b559d20b5c94f8e9120013c093f81` (C22 audit, PR #94).
Classification: behavior-changing initialization defect repair; no scientific change.
Stage 3 remains open; stages 4-11 remain pending.

## Boundary and compatibility

The pointer-taking Bezier/Hermite paths retain their signatures, layout, ID,
defined numeric payload and detached topology: zero curves, no reciprocal
registration and null SubMesh. C22 and ADR-0036 define their initialization
preconditions and destination state. This remains a partial detached copy.

Bezier constructs its existing basis and resets five load metrics and two
process/patch IDs to zero without reading source metadata. Fully constructed
geometric sources may have indeterminate load metadata, so copying those fields
would introduce a new invalid read. Existing control values/IDs, transformed
geometry/scratch matrices and four direction flags keep their original reads
and order. Hermite initializes its internal direction flags true without reading
source flags, retains the existing Hermite basis construction and copies the
same corners/tangents/twists/transformed/scratch fields. Its inherited public
orientation fallback stays false. No numerical expression or order changes.

Sources must be live and non-null, with initialized geometric/scratch payload
and, for Bezier, directions. A default/control-only reader object does not meet
that precondition merely because setters populated its control values. No new
null-source or default-geometric contract is introduced. Repeated copying is
qualified only after a valid first construction. Ordinary C++ copy/move remains
unavailable. No complete geometry clone, external-client or ABI guarantee follows.

The original literal caller inventory remains historical: 81 production
constructions, no single-pointer call outside the constructor base chain. That
negative evidence is not a whole-program or external-client proof. The audit
recipe/records remain unchanged and must be reproduced against their original
revision, not relabeled after rebuilding against repaired production files.

## Focused observations and preservation

[The focused record](stage3/detached_patch_copy/focused.json) separates candidate
instrument observations, live original/candidate pairs and retained preparation
findings. It is prepublication evidence, not exact-published-head/main evidence.
The immutable original snapshot contains 488 Git-archive-verified production
files. Only the two constructor initializer lists change production code; two
headers add English contract comments. The other 484 files remain byte-identical.

The new probe compiles sixteen actual production translation units. Explicit
GCC C++17, MSVC ASan C++17 and static Debug CRT builds preserve the existing
container ABI, disable optional NRVO on MSVC and retain compiler warnings.
There are 95 ASan/CRT expected outcomes: 72 normal/aggregate contracts, twelve
measured nonallocating operations, eight deliberately rejected corruptions and
three working UAF/leak/allocation-hook controls. Copy/retirement is measured
under an active denial hook; twelve zero-attempt observations are not allocation
sweeps or positive denial counts. The independent hook must actually deny one
allocation. Defined CRT cases retain zero normal blocks/bytes.

Normal observations cover planar/bilinear surfaces, all sixteen Bezier direction
masks, initialized basis coefficients, all zero load metadata, initialized Hermite
flags, controls/IDs, transformed/scratch matrices, repeated detached copies and
independent scratch storage. One Bezier fixture leaves source metadata
indeterminate and another seeds all seven fields; the destination is zero in
both. Source incidence retains repeated parent/null/source entries in order.
Source-first Bezier and copy-first Hermite retirement are measured. Hermite
source observers are explicitly removed by the fixture before source teardown;
ordinary Hermite retirement remains unqualified.

There are 105 nonempty original/candidate pairs: 35 per GCC/MSVC ASan/CRT build.
The original adapter excludes reads of its omitted basis/metadata/direction
fields; it does not replace any production body. Each build preserves 5,950 XYZ
vectors/17,850 scalar bits and 850 independently checked analytic points per
executable. Totals are 17,850 paired vectors/53,550 scalar bits and 2,550 analytic
points. Twenty-five points per shape and six first/second partials are exercised.
Equality is within each build, not cross-compiler. The 1e-12 analytic fixture bound
does not alter production tolerances or establish general accuracy.

tools/audit_patch_copy.py accepts only the exact two initializer prefixes and
comment-only header deltas against immutable entry main; eight independent
basis, source-metadata-read, direction, ID, control, topology, orientation and
arithmetic mutations are rejected. The earlier Bezier construction/observer
guards normalize only that exact separately checked copy prefix and retain all
four/six prior negative controls. Their original lifetime/numerical obligations
and the new required copy-preservation gate all remain mandatory.

The initial local probe preparation stopped before writing on an ambiguous
replacement assertion; an attempted context patch also made no change. A saved
bounded helper then prepared uniquely checked sites. These are preparation
failures, not test passes. The architecture preflight rejected a tooling path
as a source anchor; the record is retained in build/s35-architecture-preflight-failure.log.
The corrected contract uses actual production anchors without changing the
validator. An initial build of the unchanged observation probe and all earlier
focused records remain separate from the final qualification. No completed
instrument campaign was retried or acceptance criterion weakened.

## Commands and complete delivery requirements

```powershell
cmake -S tests/patch_copy_memory -B build/s35qa -G "Visual Studio 17 2022" -A x64 -DAP_MESH_PATCH_COPY_ASAN=ON
cmake --build build/s35qa --config RelWithDebInfo --parallel 2
cmake -S tests/patch_copy_memory -B build/s35qd -G "Visual Studio 17 2022" -A x64
cmake --build build/s35qd --config Debug --parallel 2
python tools/qualify_patch_copy.py --asan build/s35qa/RelWithDebInfo/detached_patch_copy_probe.exe --crt build/s35qd/Debug/detached_patch_copy_probe.exe --runtime '<qualified MSVC runtime directory>' --output '<new directory>'
python tools/compare_patch_copy.py --original '<explicit C++17 original probe>' --candidate '<matching candidate probe>' --original-root build/s35-original --candidate-root . --runtime '<qualified MSVC runtime directory>' --output '<new directory>'
python tools/audit_patch_copy.py --candidate-root .
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
```

Standalone original configurations set AP_MESH_PATCH_COPY_SOURCE_ROOT to the
immutable original and AP_MESH_PATCH_COPY_ORIGINAL=ON. All probe targets require
C++17 explicitly; check actual compiler flags/projects. The drivers refuse
existing output directories and retain failing reports. Child logs/executables,
original/current production and all protected inputs require independent hashes.

The required inventory is 51 CTest with zero failures/skips and 74 Python
controls, all earlier 30 memory batteries/3062 expected outcomes plus this
95-outcome battery (31/3157), 1040 retained scalar sequences and exact twice-
repeated Eistute/Book accepted/rejected/OBJ/incidence/CSV traces. Full exact-head
and post-merge main require unchanged protected hashes, selected lint/explicit
formatting, architecture/contracts, exact checkout/environment and complete
remote main/branch/PR/status/check-run audits. No hosted workflow is introduced.
Missing or failing required gates block integration; focused success is insufficient.

Complete cloning, ordinary Hermite observer retirement, source preparation,
other loaders/MPI, arbitrary publications, foreign/current-patch rebinding,
cache/metadata rollback, complete extreme meshes and whole-process/parallel/
LSan/UBSan remain outside scope. No numerical policy changes or performance claim.
After bounded qualification, the next single audit is ordinary Hermite observer
retirement and actual callers. Full stage 3 closure remains blocked by its inventory.
