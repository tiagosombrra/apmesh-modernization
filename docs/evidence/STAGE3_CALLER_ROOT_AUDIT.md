# Stage 3 caller-root audit and next serial-reader boundary

Source base: `9a853348755e0a9125a844278a2bf6d59a82bfba` (slice 32 closure, PR #87).
Classification: engineering-only source audit and original defect reproduction.
No production repair, new scientific policy or additional qualified slice is
claimed. Slice 33, serial-reader control ownership, remains open.

## Actual callers and ownership

[Literal call inventory](stage3/caller_roots/callers.json) records 56 production
new/make_unique/MakePatch occurrences after removing comments: eight default
constructions, 47 eight-argument borrowed-curve calls and one twelve-argument
borrowed-curve call. All 45 Models3d Bezier factories use the borrowed constructor;
MakeCurve commits curves to Geometry before MakePatch adopts its pending patch.
Charge estimation also constructs from already committed Geometry curves.

No literal production caller of the sixteen-point fresh-curve constructor was
found. That is bounded negative source evidence, not runtime qualification of
arbitrary public, indirect or external callers. C25's successful external adoption
precondition remains required. The pointer-copy Bezier constructor also has no
discovered production call; ordinary Patch copying is deleted in the base.

| Root | Source-backed disposition | Remaining observation |
| --- | --- | --- |
| Supported serial input | GeneratorAdaptive calls ReaderFilePatches with the enclosing live Geometry; it calls LoaderBezierPatchFile and reconstructs borrowed-curve Bezier patches | Actual control-only parser result and unused pending patch ownership are defective; reproduce below before repair |
| Serial Geometry adoption | Curves are inserted before borrowed patch construction; InsertPatch consumes its argument including on insertion failure | Preserve matching tolerance, control interning, orientation and committed prefixes; qualify allocation failure and repeated use |
| Charge input | LoaderBPFile already returns unique control owners under C23; its sampled isolated positive control retains zero bytes | Do not substitute this parser for the serial path without independent input/control/direction comparisons |
| MPI input reconstruction | The USE_MPI block creates raw VertexAdaptive controls and preliminary curves later overwritten by matching/reconstruction | Static ownership findings only; no MPI execution or parallel closure follows from this audit |
| Model ownership/copy | Model borrows geometry and deletes raw meshes; InsertMeshAdaptive pushes a raw owner into a vector; copy members are implicit | No production copy expression found; allocation failure, duplicate adoption and copy behavior are not runtime-qualified |
| Other public loaders | OBJ/RIB/ParsePatchesBezier/Hermite methods remain declared; no supported serial call discovered in the inspected sources | Public API and malformed/repeated/error paths remain unqualified; no blanket cleanup claim |

The literal scanner is not a whole-program alias or template-instantiation proof.
Inspect source context separately: the distributed reconstruction is guarded by
USE_MPI, while the supported serial call is in the opposite branch. Model's
mesh-owning API and Hermite observers remain separate from C26 Bezier retirement.

## Original serial retention reproduced

The standalone [probe and recipe](stage3/caller_roots/CMakeLists.txt) compile the
actual complete patch_reader.cpp and fifteen other production units with C++17,
static MSVC Debug CRT, iterator metadata disabled and optional NRVO disabled.
No parser body or production type is replaced by a stub. A valid one-patch file
contains sixteen coordinate records and one index record. Each scenario runs in
a new process with a real CRT checkpoint before and after destruction.

| Scenario | Actual exit | Retained normal blocks | Retained bytes | Interpretation |
| --- | --- | --- | --- | --- |
| Clean automatic PatchBezier owner | 0 | 0 | 0 | Positive release control |
| Deliberately leaked PatchBezier | 1 | 1 | 1328 | Instrument detects the actual leak |
| Unique LoaderBPFile result | 0 | 0 | 0 | Existing owning parser is an independent positive control |
| LoaderBezierPatchFile, returned patches explicitly deleted | 1 | 1 | 1328 | Unused trailing pending patch is lost |
| ReaderFilePatches, Geometry and reader destroyed | 1 | 2 | 2656 | Parsed control patch is overwritten and trailing pending patch is lost |
| Same raw loader called twice, second result explicitly deleted | 1 | 2 | 2656 | Two unused pending patches are lost; second result also repeats the first pointer |

LoaderBezierPatchFile allocates a default raw patch before parsing and another
after each publication. Its reader destructor is defaulted. ReaderFilePatches
overwrites each raw parsed-control pointer with a reconstructed Geometry-owned
patch without retiring the control object. The measured block sizes equal the
independent deliberate PatchBezier leak. Repeated calls return the accumulated
raw list (first=1, second=2, same_first=1); this is an alias/transfer hazard, not a
measured double deletion in this probe. The deliberate control and the three
production scenarios fail their zero-retention expectation; they are retained
as negative evidence, never as memory-safety passes.

This six-scenario original audit is not a twenty-ninth qualified repair battery.
Allocation-failure sweeps, malformed/rejected input, broader models, ASan,
whole-process, parallel, LSan and UBSan remain unmeasured here. Per-process CRT
byte sizes apply to this recorded compiler/ABI. No repaired candidate exists yet.

```powershell
cmake -S docs/evidence/stage3/caller_roots -B build/caller-root-reproduction -G "Visual Studio 17 2022" -A x64
cmake --build build/caller-root-reproduction --config Debug --parallel 2
python docs/evidence/stage3/caller_roots/reproduce.py --executable build/caller-root-reproduction/Debug/serial_reader_root_probe.exe --output build/caller-root-results
```

The reproduction driver exits successfully only when all six original outcomes,
including the expected nonzero defect/control exits and nonempty CRT counts, are
observed. Output directories must be new. That driver success establishes the
reproduction, not a repaired loader. See the retained report and child-log hashes
in [caller_roots](stage3/caller_roots/).

## Next bounded repair and closure obligations

The single next repair is explicit ownership of serial control-only results and
the pending parser patch, including failures and supported repeated use. Preserve
the actual raw/public caller inventory when choosing an owning-result migration;
do not delete Geometry-owned patches or return aliases to destroyed controls.
Qualify allocation denials before publication, after parsed prefixes and during
Geometry reconstruction/adoption; retain actual original negative observations.
Measure normal control order, IDs, shared-curve interning and directions against
this source base, with independent corrupting controls. Preserve the existing
validation domain, 1e-7 merge tolerance, numerical order, consumed-ID policy and
accepted/rejected Eistute/Book traces. Do not claim whole-reader rollback or retry
unless those observations are explicitly defined and measured.

All existing C26 and constructor gates remain required. A future repair must add
its exact-head/main instrument, numerical/preservation and full prior regression
evidence before integration. Model/copy, MPI/Hermite and the other finite stage 3
rows retain their separate pending dispositions. This audit changes only evidence
and documentation; the 598 protected production/tool/test/build/input/contract
identities are unchanged. Stages 4-11 remain pending.
