# Hermite constructor publication rollback

Classification: behavior-changing exception-safety defect repair; no scientific change.
Source base: `8eff0d6c4d69bb413674b003a22e49c3c6faca46` (PR #99).
Status: bounded full exact-head and post-merge main qualification complete (PR #100).
The focused record below preserves the earlier preparation checkpoint.

## Defect and repair

The four-curve constructor publishes four reciprocal patch observers. An exception
from a later publication does not execute the complete PatchHermite destructor.
The preserved original probe reproduces stale observers and actual ASan
heap-use-after-free, both directly and through Models3d::ModelBaseQuadrada.
At tested model allocation ordinals 49-51, four owned curves remain with zero
owned patches and one, two or three stale observers. Zero CRT retention in those
cases does not establish valid observers.

The only production delta is the scope include, an entry PatchObserverScope and
terminal Commit in src/data/patch/patch_hermite.cpp. The existing Bezier helper
captures each curve's observer count and truncates exclusively appended suffixes
on failure. Repeated curve slots retain their common original prefix. The guard
does not allocate. Successful publication, control reads, initialization and all
numerical expression tokens/order match the source base. Completed destruction
continues to use the separately qualified C29 behavior.

All arguments must be live nonnull Hermite curves. Construction permits only
exclusive append-only publication, without foreign appends or intermediate
consumption of a pending patch. These are the existing helper's preconditions.
No tolerance, formula, synchronization, template/front, adaptation, acceptance
or stopping policy changes. Repeated slots test lifetime, not geometric validity.

## Focused evidence

The [compact record](stage3/hermite_construction_repair/focused.json) binds the
82-outcome report, instrument executables and four unchanged original audit files.
The original CMakeLists.txt, inventory.py, callers.json and probe.cpp under
stage3/hermite_construction remain byte-identical. Their inventory is a snapshot
of 25 literal roots at the source base, not an executable caller-coverage claim.
Its absence-of-rollback assertion is intentionally historical; do not regenerate
that inventory against repaired production.

The new actual-production probe covers three incidence layouts, four alternating
foreign/null prefixes and all sixteen flags. Each calibrated allocation denial
must propagate, make no additional allocation during unwind, preserve the exact
prefix and permit successful construction/retirement on retry. The separate
model sweep calibrates and denies every observed allocation. Failed adoption
preserves a committed Geometry prefix and retires the completed pending patch.
ASan UAF, CRT leak, denial and independent count/order controls must work.

The formatted probe passes 82 expected ASan/static CRT outcomes: 768 constructor
sweeps/5888 actual denials and 212 model denials, including the explicitly repeated
contracts mode. These totals include repetitions, not distinct failure sites.
Defined CRT modes retain zero blocks/bytes. The new stronger probe compiled
against immutable original production is rejected under Debug CRT at the first
stale observer (exit 2). The original ASan failure evidence remains unchanged.

A GCC Release original negative attempt returned zero and observed only four
allocations in the chosen sweep; it did not demonstrate detection of the defect
and is not accepted as failure coverage. Debug CRT supplies the independent
original rejection. GCC live numerical comparison remains separately required.
The earlier inherited-environment GCC rebuild failed without a useful diagnostic;
fresh Ninja builds with the explicit UCRT64 toolchain PATH pass. Its exact cause
was not isolated. An initial formatter invocation found no tool on inherited PATH;
explicit UCRT64 PATH uses the installed formatter. Both preparation findings
remain local; neither is a passed gate.

## Reproduction and delivery

Configure tests/hermite_construction_memory in separate GCC, MSVC ASan and static
Debug CRT directories. Set AP_MESH_HERMITE_CONSTRUCTION_SOURCE_ROOT to an
immutable archive for original tests; default is current production. Enable
AP_MESH_HERMITE_CONSTRUCTION_ASAN only for MSVC ASan RelWithDebInfo.

```powershell
python tools/qualify_hermite_construction.py --asan build/s37qa/RelWithDebInfo/hermite_construction_probe.exe --crt build/s37qd/Debug/hermite_construction_probe.exe --runtime "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64" --output build/new-hermite-construction-run
python tools/audit_hermite_construction.py --candidate-root .
```

Two required CTest gates retain all prior 53 entries (55 total). The source guard
rejects eight independent scope/commit/curve/allocation/publication/numerical
mutations. Older retirement/copy guards normalize only this exactly located
delta and retain their existing mutations. Delivery also requires prior memory
batteries, explicit C++17 point/derivative/incidence pairs, exact repeated
Eistute/Book accepted/rejected/OBJ/incidence/CSV traces, local quality and fresh
remote/checkout/input audits on the exact published revision.

## Limits

Model resource-failure observation is not a current config-CLI failure. No
complete model/loader/adaptive atomicity, consumed-ID rollback, arbitrary curve
replacement, copied/foreign observer graph, SubMesh observer, broader-model,
whole-process, parallel, LSan or UBSan qualification follows. Stage 3 stays open;
the next root must be chosen from the finite closure inventory after this bounded
repair is qualified and integrated.


## Exact delivery qualification

Head `c4bbe0354935243bee8ea84e8ff5454e4215825c` and main
`e81eb804eb67599e47c1068069f602c7dd231da9` share tree
`df1bd7111abaddec0840522b130b381f06ca21be` (2031 blobs). Each full campaign passes
156 recorded commands with their expected exits, 55/55 CTest without failures/
skips, 74 Python controls, 33 memory batteries/3392 outcomes, 1040 retained scalar
sequences, 18 Hermite live C++17 pairs and exact repeated article traces. All 622
protected input identities and independent checks pass. Fresh remote audits
retain complete branch/tree identity; absent hosted checks do not validate code.

Head full report SHA-256: `5e133ff0d3a37097e9590906ef29cb5a8fcc5c19ddacec9a468e37786989c6ed`.
Main full report SHA-256: `3899238fe3b66bc930780a17b158562b67403b7f05ce993cbd995278927eda74`.
The [compact delivery record](stage3/hermite_construction_repair/delivery.json)
binds the revisions, report/check hashes, original audit files and scope. Raw
reports and logs remain in build/s37-head and build/s37-main. Each invocation
binds its actual executable; no cross-build executable-byte equality is claimed.
Only src/data/patch/patch_hermite.cpp changes in production; all other 487 archived
production files remain byte-identical. The original CRT rejection, GCC Release
negative limitation and all earlier failures/preparation findings remain retained.

Documentation closure changes only six declared documentation paths. Applicable
head/main gates repeat builds, 55 CTest/74 Python controls, 82 construction and
153 retirement outcomes, 18 live pairs, source/architecture/format/whitespace,
checkout/environment and remote audits. The complete implementation campaigns
are hash-linked without repeating them for prose. The same 622 protected inputs
must remain fixed. Closure delivery revisions and reports are recorded in its PR.

Slice 37 is qualified only within C30's exclusive-publication/live-curve boundary.
No stage closure or wider rollback/observer/parallel qualification follows.
Next work diagnoses retained mesh quality and rejected transitions before any
new algorithmic repair; scientific policy changes still require advisor alignment.
