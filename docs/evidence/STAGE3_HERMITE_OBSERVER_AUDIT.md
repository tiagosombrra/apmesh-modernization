# Stage 3: ordinary Hermite observer retirement and caller audit

Source base: `21542d8e739d98604b68fa92414332c694f4642d` (slice 35 closure, PR #96).
Classification: engineering-only source audit and original hazard reproduction.
No production repair or additional qualified memory slice is claimed.
Stage 3 remains open; stages 4-11 remain pending.

## Source contract and actual caller roots

The [repeatable literal inventory](stage3/hermite_observers/callers.json) masks
comments and quoted literals while preserving offsets. It records 25 concrete
Hermite constructions: 23 MakePatch calls in models_3d.cpp and two default new
expressions in the legacy PatchReader::LoaderBPFileHermite. The model calls
belong to eight methods: ModelParaboloide, ModelPneu, ModelLadoDescendente,
ModelBaseCircular, ModelBaseQuadrada, ModelBordaCurva, ModelDoisPatches and
ModelNariz. All 23 use four curves and twists. No invocation of the legacy
Hermite loader was found beyond its declaration/definition. These are bounded
literal observations, not complete alias, macro, instantiation or external proof.

Models3d::MakePatch first owns the pending patch through make_unique, then moves
it into consuming Geometry::InsertPatch. Geometry owns its patches and curves;
it has no public individual patch erasure. Complete destruction and populated
move assignment retire patches before curves. A source branch in serial Execute
selects ModelBaseQuadrada when argv[3] is null. Current main accepts only config
mode and always supplies argv[3] from input_model.data(), so this audit does not
establish that the fallback executes through the current CLI. Existing accepted/
rejected article traces exercise their configured reader paths, not every model.

The ordinary four-curve Hermite constructor appends all four curve pointers,
then publishes this to each curve, in order. Repeated slots create repeated
reciprocal entries. PatchHermite, PatchCoons and Patch have default destructors;
none removes these reciprocal observers. Curves borrow their patch pointers and
clear their own vectors at destruction without dereferencing them. Consequently,
complete Geometry destruction can finish without an ASan error while observers
in independently surviving curves remain expired after patch retirement.

The inventory retains 42 generic GetPatch spellings, including declarations,
definitions and Geometry/SubMesh APIs. Manual review identifies real curve
observer consumers: Adapter evaluates CurvatureAnalytical through curve patch
pointers (adapter.cpp:830/847/1259/1276); Generator's curve factor calculation
reads patch IDs (generator_adaptive.cpp:4763/4808); synchronization disabling
collects these pointers and performs Coons RTTI/rebinding (curve_synchronization.cpp).
Other Generator adjacency/budget paths also traverse curves. A nonnull pointer
check is not a lifetime check. The standalone probe executes the actual public
GetPatch/GetId methods, not the complete Adapter, Generator or CLI algorithms.
No observed production CLI crash or executed parallel caller is claimed.

Constructor failure is a separate unresolved root: Hermite has no observer
rollback scope between publications. Failed consuming Geometry adoption can
destroy a completed pending patch while its curves remain alive. This audit
records those source-level obligations but does not measure their allocations,
publication prefixes or recovery. It does not merge them into a qualified
ordinary-retirement result. ReplaceCurve, copied/foreign observer lists, expired
curves, current SubMesh observers and arbitrary external ownership remain open.

## Original runtime observations

The [standalone recipe](stage3/hermite_observers/CMakeLists.txt) compiles seventeen
actual production units plus the probe, including the real Hermite/Coons/Patch,
Geometry, curve and physical/numerical dependencies. No production class or
method body is replaced. GCC, MSVC ASan and static Debug CRT explicitly use
C++17. The GCC compile database has eighteen C++17 commands; MSVC projects use
stdcpp17. Iterator metadata and optional MSVC NRVO use the prior qualified probe
settings. Existing compiler/Eigen warnings are retained without suppression.

Each layout uses three completed patches, seeded parent/null/parent prefixes,
and four independent, paired repeated or all-repeated curve slots. First,
middle and last patch retirement are observed. Two extra matching registrations
and a null entry are added to every used curve before retirement.

| Observation | Result and interpretation |
| --- | --- |
| Original ordinary retirement, nine cases per build | All original entries remain in order, including 12/8/6 expired target observers by layout. No expired entry is dereferenced in inventory mode. |
| Explicit reference cleanup before retirement, nine cases per build | RemovePatchObservers removes every target match while preserving all other entries in order; subsequent traversal consumes only live nonnull patches. |
| Actual ASan consumption after original retirement, nine cases | Each reports heap-use-after-free through the real Patch::GetId. These are original failures, not safe operations. |
| Live evaluation, three layouts per build | 675 finite point observations overall; 225 bilinear points use an independent 1e-12 fixture bound. Repeated-slot cases are lifetime fixtures, not valid geometry claims. |
| Default empty topology and complete Geometry ownership | Clean executions with no numeric read of default fields and no observer consumption after owned graph retirement. |
| Independent observer oracle challenges | Added-count and same-count reversed-order corruptions are rejected in every build. |
| Independent ASan UAF control | Actual heap-use-after-free is detected. |
| Independent CRT leak control | One normal block/40 bytes retained; nonzero exit required. |

All 83 required reproduction expectations are observed: 72 defined inventory/
reference/control observations, nine original ASan failure cases and two broken
instrument controls. Every defined CRT case retains zero normal blocks/bytes,
including cases with stale observer entries. Thus zero heap retention alone does
not establish valid observers. There is no repaired candidate or new qualified
memory battery. The prior 31 batteries/3157 outcomes remain historical qualified
evidence for their own boundaries.

The [focused report](stage3/hermite_observers/original_reproduction.json) retains
executable, recipe, all 488 original production-file and child-log hashes, exits,
diagnostic kinds and exact observations. Its modified prepublication working-tree
status is explicit. Every src/include/libs byte is matched against an in-memory
Git archive of the source base; the historical repository is untouched. Raw
logs remain under build/hermite-audit-focused. No failed preliminary experiment
is substituted for this report. Build/configuration logs remain local.

```powershell
cmake -S docs/evidence/stage3/hermite_observers -B build/hermite-audit-gcc -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build/hermite-audit-gcc --parallel 2
cmake -S docs/evidence/stage3/hermite_observers -B build/hermite-audit-asan -G "Visual Studio 17 2022" -A x64 -DHERMITE_OBSERVER_AUDIT_ASAN=ON
cmake --build build/hermite-audit-asan --config RelWithDebInfo --parallel 2
cmake -S docs/evidence/stage3/hermite_observers -B build/hermite-audit-crt -G "Visual Studio 17 2022" -A x64
cmake --build build/hermite-audit-crt --config Debug --parallel 2
python docs/evidence/stage3/hermite_observers/inventory.py --check
python docs/evidence/stage3/hermite_observers/reproduce.py --gcc build/hermite-audit-gcc/hermite_observer_probe.exe --asan build/hermite-audit-asan/RelWithDebInfo/hermite_observer_probe.exe --crt build/hermite-audit-crt/Debug/hermite_observer_probe.exe --runtime '<qualified MSVC runtime directory>' --output '<new result directory>'
```

The runner refuses an existing output directory and fails closed on missing or
incorrect observations. Reproduction of this historical result requires this
original implementation; do not relabel a future repaired checkout as original.
No failed-construction/adoption sweep, differential numerical regression, whole-
process/parallel, LSan or UBSan qualification follows.

## Next single repair and delivery gates

The next bounded repair is slice 36: completed Hermite observer retirement.
Require live current borrowed curves through destruction, nonallocating stable
all-match removal of this address, repeated/current slots, null/duplicate foreign
entries, populated incidence and default/detached empty topology. Preserve every
defined constructor/numerical token, directions, public copy availability,
curve ownership and detached-copy contract. Do not silently infer cleanup on
failed construction, foreign/copied observer lists or arbitrary curve rebinding.
Those roots require independent explicit dispositions.

The future repair must reproduce original failures and qualify actual supported
normal/exception/lifetime cases with independent invalid controls, measured
allocation-free operations, original/candidate numerical pairs, all prior memory
and exact accepted/rejected article regressions on its exact head and main.
No formula, order, synchronization, template/front, tolerance, budget or
adaptation/acceptance/stopping policy change is authorized by this audit.

This audit changes none of the 613 previously protected implementation/test/tool/
build/input/contract files and adds no CTest. Exact published audit head and
post-merge main repeat the 83-case reproduction, build, 51 CTest/74 Python
controls, source equivalence, inventory, architecture, selected format/whitespace,
checkout/environment and complete remote main/branch/PR/check gates. Delivery
revision and report hashes are recorded in the PR. A successful audit delivery
does not close stage 3 or qualify the future repair.
