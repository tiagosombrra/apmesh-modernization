# Stage 3 C22: pointer-taking patch-copy audit

Source base: `b48070fa733e09b3b5974f00616dc7da968b881d` (slice 34 closure, PR #93).
Classification: engineering-only source audit and original observations.
No production repair, complete clone or new qualified ownership slice is claimed.
Stage 3 remains open; stages 4-11 remain pending.

## Construction routes and actual callers

[The repeatable literal inventory](stage3/patch_copy/callers.json) masks comments
and quoted literals while preserving offsets. It records 81 concrete production
construction expressions: 68 MakePatch calls in models_3d.cpp, nine in
patch_reader.cpp, two in control_patch_reader.cpp, one in charge_input_estimate.cpp
and one in generator_adaptive.cpp. None supplies a single pointer argument.
The 39 direct constructor spellings are retained separately: declarations,
definitions, destructor spellings, base-constructor calls and seven raw new sites.
No named direct-object construction was found. Manual review found no concrete
production call to a pointer-taking patch constructor outside its base chain.

MakePatch forwards arguments after its Geometry argument through make_unique and
then consuming Geometry adoption. Its 68 concrete calls provide curve/control or
curve/twist arguments, not a patch pointer. Other discovered routes default-create
control-only reader objects or reconstruct a patch from four curves and controls.
The alternate generator reconstruction belongs to the USE_OPENMP block; source
inspection is not parallel execution coverage. The current serial CLI is not
shown to fail because of these unused pointer-copy paths.

This is bounded negative evidence. It does not resolve aliases, macro expansion,
all template instantiations, indirect/external clients or future callers. These
constructors are public; absence of a literal production call is not authority
to silently delete or redefine an external interface. Ordinary C++ copy/move
construction of Bezier/Hermite remains unavailable through the deleted Patch
copy operations and the derived special-member declarations. Pointer-taking
construction is a separate API, not a qualified copy/move operation.

## Source semantics and initialization inventory

| Path | Defined source behavior | Omission or boundary |
| --- | --- | --- |
| Patch(Patch*) | Copies GetId() from a non-null source; null produces ID zero | The in-class sub_mesh_ initializer leaves the copy detached; it does not copy or own the source mesh |
| PatchCoons(PatchCoons*) | Invokes the Patch pointer path | curves_ is an independently empty vector; no curves or reciprocal patch observers are copied |
| PatchBezier(PatchBezier*) | Copies sixteen PointAdaptive control values/IDs, three transformed geometric matrices, U/V scratch matrices and four direction flags | Does not initialize mat_base_ or seven load/process metadata members; does not populate curves_ or sub_mesh_ |
| PatchHermite(PatchHermite*) | Copies four corners, eight tangents, four twists, three transformed geometric matrices and U/V scratch; constructs a fresh Hermite basis | Does not initialize four direction members; curves_ and sub_mesh_ remain empty/null. IsCurveReversed uses the Coons default false rather than these members |

The inventory retains the exact assigned-member sets from each copy body. The
Bezier default constructor initializes direction and load/process metadata, but
its pointer-copy constructor does not delegate to that constructor. The two
geometric Bezier constructors also leave the load/process metadata uninitialized.
The fixed-size Eigen basis has no field initializer and is not initialized by
the Bezier pointer-copy path. These are source observations; the probe never
evaluates the omitted members, calls GetB/printing on that copy, or copies
metadata from a source that may itself lack initialized values. Ordinary ASan
and CRT do not establish initialized-value safety for those omitted fields.

Derived pointer constructors dereference the supplied source after the null-safe
base path. No derived null-source behavior is qualified. Control-only/default
objects do not supply initialized geometric matrices merely because setters
populated control values. The probe uses fully constructed geometric sources.

An empty curve vector prevents detached Bezier destruction from touching source
incidence. Its copied transformed matrices can still evaluate a surface without
curves or the omitted basis; CalculatePointUV uses U, transformed G and V. Thus a
successful numerical comparison is compatible with an incomplete topology and
does not prove a complete clone. Adding shared curves/reciprocal registration or
copying a current SubMesh would change the contract and lifetime obligations.

## Defined original observations

The standalone [recipe](stage3/patch_copy/CMakeLists.txt) compiles sixteen actual
production translation units plus the probe, including Patch/Coons/Bezier/Hermite,
both derived curve classes, actual physical mesh dependencies and numerical units.
No production type, method body, constructor or destructor is replaced by a stub.
GCC, MSVC ASan and static Debug CRT explicitly use C++17. The GCC command line is
checked for -std=c++17 and MSVC projects for stdcpp17. Debug iterator metadata is
disabled to match the existing qualified container ABI; optional NRVO is disabled
on MSVC. Existing C4245 and Eigen C4127 warnings are retained, without suppression.

The focused audit observes 110 expectations: 36 defined cases per build (108),
one actual ASan heap-use-after-free control and one positive CRT point-leak
control. Each defined CRT case retains zero normal blocks/bytes. The independent
broken controls must fail with their actual diagnostic/retention; their failures
are not qualified memory-safe operations.

Each build exercises the base ID-only/null path, both planar/bilinear Bezier
surfaces with all sixteen direction masks, both planar/bilinear Hermite surfaces,
and a deliberately corrupted payload/topology oracle challenge. Source/copy
comparisons cover control values/IDs, initialized matrices, 25 parameter points
and all six first/second partials at each point. Totals across the three builds
are 17,850 paired XYZ vectors/53,550 scalar bit comparisons and 2,550 independent
analytic points. The 1e-12 analytic test bound is a fixture check, not a production
tolerance change or a broad numerical accuracy claim. No cross-compiler bitwise
equality is required; each source/copy pair is compared within its own build.

Copies have the source ID, zero curves and null SubMesh. Seeded source incidence
retains repeated parent observers, null and source in order. Bezier controls,
scratch, directions and defined payload remain independent; its copy evaluates
after ordinary source retirement, and neither detached-copy retirement changes
the retained curve prefix. Hermite copy-first retirement leaves source incidence
unchanged. The fixture explicitly removes Hermite source observers before source
teardown; no Hermite destructor cleanup or expired-observer safety is inferred.
Two deliberate corruption types are rejected in each of the three builds.

[The compact focused record](stage3/patch_copy/focused.json) retains recipe,
executable, all 488 src/include/libs input and child-log hashes, exits and measured
counts. It is a prepublication working-tree observation at the source base.
Every production input remains identical to that immutable Git base; exact
published-head/main gates must repeat the audit and retain their own identities.
Raw focused logs and the earlier two GCC preflight observations remain local in
build/patch-copy-focused and build/patch-copy-gcc-*-preflight.log.

```powershell
cmake -S docs/evidence/stage3/patch_copy -B build/patch-copy-gcc -G Ninja -DCMAKE_CXX_COMPILER=C:/msys64/ucrt64/bin/c++.exe
cmake --build build/patch-copy-gcc --parallel 2
cmake -S docs/evidence/stage3/patch_copy -B build/patch-copy-asan -G "Visual Studio 17 2022" -A x64 -DPATCH_COPY_AUDIT_ASAN=ON
cmake --build build/patch-copy-asan --config RelWithDebInfo --parallel 2
cmake -S docs/evidence/stage3/patch_copy -B build/patch-copy-crt -G "Visual Studio 17 2022" -A x64
cmake --build build/patch-copy-crt --config Debug --parallel 2
python docs/evidence/stage3/patch_copy/inventory.py --check
python docs/evidence/stage3/patch_copy/reproduce.py --gcc build/patch-copy-gcc/patch_copy_probe.exe --asan build/patch-copy-asan/RelWithDebInfo/patch_copy_probe.exe --crt build/patch-copy-crt/Debug/patch_copy_probe.exe --runtime '<qualified MSVC runtime directory>' --output '<new directory>'
```

The runner refuses existing output directories and retains a failing report.
It requires all 110 actual observations, nonempty bitwise comparisons, independent
analytic points, zero CRT retention in defined cases and both working instruments.
Published-head and merged-main revision/report hashes are recorded in the PR.

## Next bounded item and delivery limits

The next single repair is slice 35: explicit initialized detached patch-copy
intent under C22. Preserve existing defined ID/control/transformed-matrix/scratch
values, empty curve incidence, null SubMesh and source borrowing. Establish the
source initialization preconditions and a deterministic basis/direction/metadata
initialization contract; do not read possibly uninitialized source metadata to
make a nominal field-for-field copy. Review the source/API migration and tests
before implementing it. Complete geometry cloning, foreign/current-patch rebinding
and Hermite ordinary observer retirement remain separate obligations.

This audit adds evidence only. It preserves all 608 slice 34 protected inputs,
the 49 CTest/74 Python inventory and all completed full campaigns/negative traces.
Exact audit head/main require rebuilding all three probes, the 110 observations,
49 CTest/74 Python controls, inventory/contracts, explicit format/whitespace,
complete checkout/environment/source/remote main/branches/PR/check audits and
independent child-log/executable/input identities. Prior repaired batteries and
accepted/rejected numerical campaigns are retained; they are not replayed or
relabeled as new complete-clone validation. A future production repair requires
its full exact-head/main numerical/preservation and prior regression gates.
No allocation-denial sweep, FindUV, complete caller execution, parallel,
full-process, LSan or UBSan qualification follows. No formula, floating-point
order, synchronization, quadtree/template/front reconstruction, tolerance,
budget or adaptation/acceptance/stopping policy changes.
