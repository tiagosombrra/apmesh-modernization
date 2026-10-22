# Stage 3 Model ownership and caller audit

Source base: `d69f77a868380136153edf6a3274e661fad59d6a` (slice 33 closure, PR #90).
Classification: engineering-only source audit and original hazard reproduction.
No production repair or additional qualified ownership slice is claimed.
The next single repair is slice 34, explicit Model adoption and copy/move intent.
Stage 3 remains open; stages 4-11 remain pending.

## Actual ownership and callers

Model borrows geometry_ and stores raw MeshAdaptive pointers in meshes_. Its
destructor repeatedly pops the last entry and deletes it: retirement is in
reverse insertion order. MeshAdaptive already owns SubMesh objects, which own
physical nodes and elements. Elements borrow their live nodes. Geometry and
patch/current-submesh observers have separate lifetime obligations; owning the
outer Model does not rebind or validate those observers.

[The literal inventory](stage3/model_roots/callers.json) removes comments and
quoted literals before recording Model and its mesh-facing names in src/include.
Manual review distinguishes these source routes:

| Source route | Observation | Limit |
| --- | --- | --- |
| Execute with USE_MPI disabled | Local Geometry is constructed before local Model; SetGeometry publishes its borrowed address and Execute calls Generator(Model&) | No Model copy expression found; supported serial numerical behavior is not implicated by the isolated copy reproductions |
| Serial Generator | Owns its MeshAdaptive through mesh_, not Model::meshes_ | Do not transfer the serial mesh into Model as part of the bounded repair |
| Alternate GeneratorOmp | Both literal model.InsertMeshAdaptive(malha) expressions occur here, inside the USE_OPENMP block | No production invocation of GeneratorOmp was found beyond declaration/definition; this is not parallel execution coverage |
| OpenMP pending meshes | A raw mesh is created, resized and populated before publication; no local unique owner covers that preparation or failed vector append | The audit measures append failure only, not preceding resize/generation/adaptation failure |
| USE_MPI member | GeneratorAdaptive declares Model model_ | No further literal member use found; MPI teardown and indirect/external callers remain unqualified |
| Copy/rvalue interfaces | No special copy/move members are declared; the user-defined destructor prevents an implicit move member | Rvalues bind to the implicit copy operations; positive move traits do not demonstrate ownership transfer |

No production explicit Model copy expression or derived Model class was found in
the inspected sources. This bounded negative evidence is not a whole-program
alias, macro-expansion, template-instantiation or external-client proof. The
protected raw collection also leaves external derived-code compatibility open.
C02 remains an unqualified root contract; no anchor or production file changes.

## Original instrument observations

The standalone [recipe](stage3/model_roots/CMakeLists.txt) compiles fifteen actual
production translation units plus the probe: Model, MeshAdaptive, SubMesh, node,
element, triangle, point/vector, patch, Geometry, curve base/parametric/Bezier and
the two numerical dependencies. No production type, method body or destructor is
replaced by a stub. Each populated mesh contains one submesh, three counted nodes
and one real triangle. Normal traversal checks identity, order, null/out-of-range
slots, area 0.5 and the three live adjacency lists. Normal destruction retires
all six nodes from two meshes and leaves the borrowed Geometry live.

MSVC C++17 ASan and static Debug CRT use separate build directories. Debug
iterator metadata is disabled to match the already qualified container ABI;
optional NRVO is disabled. The CRT hook denies one actual normal allocation in
the append, after the complete pending mesh and any retained prefix exist. No
test accesses an expired object except the deliberately broken UAF control and
the original duplicated-owner scenarios being diagnosed.

The /W4 builds retain existing PointAdaptive signed-conversion warning C4245
and Eigen constant-condition warnings C4127. No warning is suppressed or changed
for this audit; successful compilation is not a whole-tree lint-clean claim.

| Instrument and scenario | Exit | Observed result |
| --- | --- | --- |
| CRT normal ownership/Geometry borrowing | 0 | Zero retained normal blocks/bytes; six nodes destroyed |
| CRT independent deliberate mesh leak | 1 | 15 retained normal blocks, 696 bytes |
| CRT denied append, empty Model, explicit caller cleanup | 0 | One actual denial; unchanged empty prefix; zero retained blocks/bytes |
| CRT denied append, populated Model, explicit caller cleanup | 0 | One actual denial; prior mesh remains live; zero retained blocks/bytes |
| CRT denied append, empty Model, caller-style relinquished raw pointer | 1 | Pending mesh remains undestroyed; 15 blocks/696 bytes retained |
| CRT denied append, populated Model, caller-style relinquished raw pointer | 1 | Prior mesh remains live; pending mesh remains undestroyed; 15 blocks/696 bytes retained |
| ASan normal ownership/Geometry borrowing | 0 | Full live graph checks and destruction complete |
| ASan independent actual UAF control | 1 | heap-use-after-free detected |
| ASan implicit copy construction | 1 | Aliased owner traversal succeeds; subsequent ordinary destruction reports heap-use-after-free |
| ASan implicit copy assignment into populated destination | 1 | Previous destination's nodes are not destroyed by assignment; subsequent aliased-owner destruction reports heap-use-after-free |
| ASan construction from std::move(source) | 1 | Source still contains the same owning pointer; ordinary destruction reports heap-use-after-free |
| ASan assignment from std::move(source) | 1 | Copy assignment loses the old destination payload and duplicates source ownership; ordinary destruction reports heap-use-after-free |
| ASan duplicate adoption, unsupported owner arrangement | 1 | Ordinary destruction of the repeated pointer reports heap-use-after-free |

All thirteen required reproduction expectations are observed. These are four
zero-retention/clean controls, three nonzero CRT retention observations and six
nonzero ASan observations, including independent positive instrument controls.
Successful reproduction does not make any original failing scenario memory-safe.
The old API does not document failed-insertion ownership: the two manual cleanup
controls demonstrate that a caller can retain and release the raw argument. The
pending-owner leak reproduces the relinquishing caller pattern, rather than
asserting a previously specified consume-on-failure guarantee.

[The focused original report](stage3/model_roots/original_reproduction.json)
retains exact executable, probe/recipe/runner, production-input and child-log
hashes, exits, CRT counts and ASan diagnostic kinds. It is explicitly a modified
prepublication working-tree observation. Every recorded src/include/libs input
was separately matched byte-for-byte to the immutable source base. Exact
published-head and post-merge audits must repeat the reproduction and applicable
local/remote gates; their revisions and report hashes are retained in the PR.
Raw child logs remain local under build/s34-model-focused. Earlier preflight
records remain separate and are not substituted for the formatted probe results.

```powershell
cmake -S docs/evidence/stage3/model_roots -B build/model-root-crt -G "Visual Studio 17 2022" -A x64
cmake --build build/model-root-crt --config Debug --parallel 2
cmake -S docs/evidence/stage3/model_roots -B build/model-root-asan -G "Visual Studio 17 2022" -A x64 -DMODEL_AUDIT_ASAN=ON
cmake --build build/model-root-asan --config RelWithDebInfo --parallel 2
python docs/evidence/stage3/model_roots/reproduce.py --asan build/model-root-asan/RelWithDebInfo/model_root_probe.exe --crt build/model-root-crt/Debug/model_root_probe.exe --runtime '<qualified MSVC runtime directory>' --output '<new result directory>'
```

The runner refuses existing output directories and requires actual ASan
diagnostics, positive CRT retention, real denials and clean controls. For later
historical reproduction, use the published audit revision in an isolated checkout
with its original Model implementation. This recipe deliberately compiles the
checked-out production tree; do not relabel a later repaired API as the original.
The historical source repository is not modified.

## Next repair contract and required closure

Slice 34 should establish explicit exclusive mesh owners and prohibit accidental
copy aliasing after the caller/API compatibility audit. Define whether the raw
append consumes on entry, including failure, and provide an owning handoff where
appropriate. Any supported move must retire the destination's prior mesh graph
safely and transfer identity without duplicating owners; define self-move and
moved-from observations. Preserve geometry borrowing, reverse retirement,
append order, null/out-of-range semantics and noncopyable physical payloads.
Duplicate or foreign-owned adoption remains an invalid ownership arrangement,
not a reason to introduce shared ownership or a new numerical policy.

Qualify normal populated/empty/null cases, failed adoption before/after committed
prefixes, all calibrated insertion allocations, repeated use and destination
retirement. Challenge release/adjacency/order oracles with independent broken
controls. Compare live payload/geometry observations against immutable originals
and preserve exact accepted/rejected article traces. A supported move must have
actual runtime evidence; type traits alone are insufficient. Other caller
preparation failures and patch/current-submesh rebinding need separate explicit
dispositions; do not claim they were repaired by changing only Model.

The audit retains all 603 protected implementation/tool/test/build/input/contract
hashes and the existing 47 CTest/74 Python inventory. Its exact head and merged
main require the original thirteen-case reproduction, build, CTest, source
equivalence, selected whitespace/format, architecture/checkout/environment and
complete remote main/branch/PR/check audits. The already completed slice 33
campaigns remain unchanged. A future production repair still needs its complete
exact-head/main instrument, numerical/preservation and prior regression gates.
This audit adds no repaired battery and no accepted/rejected numerical campaign.
No exhaustive allocation sweep, preceding OpenMP preparation, parallel execution,
whole-process, LSan or UBSan qualification follows. Scientific formulas, boundary
synchronization, budgets, tolerances and acceptance/stopping policies are unchanged.
