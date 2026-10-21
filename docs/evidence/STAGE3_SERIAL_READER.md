# Stage 3 slice 33: serial-reader control ownership

Status: bounded exact-head/main qualification complete (PR #89).
Head `29c5b883b1bdebc0627c611da868f16361d476e4`; implementation main
`bd1e6920dc1792ce6a0e802ac8cdfc3216284518`; complete tree
`b6b45dd550dd201d22505be58b473d3fa0f907a5` (1973 blobs).
Entry main: `f9c7d22c0028e8864da4de5a05bdc19489da52bf` (caller-root audit, PR #88).
Classification: behavior-changing lifetime/resource-propagation defect repair.
No scientific policy change. Stage 3 remains open; stages 4-11 remain pending.

## Repair and preservation boundary

The raw serial loader lost its trailing pending control patch. ReaderFilePatches
then overwrote each parsed-control pointer with a reconstructed patch, losing the
original control object. Repeated loader calls returned accumulated raw aliases.
Original one-patch CRT retention was 1328 bytes for a cleaned raw result and 2656
bytes after complete Geometry reconstruction or repeated use. Retain that
[original caller-root evidence](STAGE3_CALLER_ROOT_AUDIT.md).

LoaderBezierPatchFile now returns an independent list of unique control owners
and retains a local pending owner during every parse/publication step. The sole
audited production caller keeps the control owners until scope exit and consumes
a separate unique reconstructed patch through Geometry::InsertPatch. Geometry's
existing committed prefix is not rolled back. Curves outlive pending destruction;
C25/C26 provide failed-constructor restoration and completed observer retirement.
Other raw loader caches remain untouched. This is an explicit source API migration,
not a binary-compatibility guarantee for unmeasured external callers.

The second file stream and both record streams propagate badbit resource failures
before an incomplete row can be indexed. Validation, ordinary EOF/failbit behavior,
coordinates/indices/IDs, interning and tolerance, curve sharing and direction logic
remain unchanged. The owning charge parser is not substituted for this parser.
Every other token in the reader/header/validation boundary must match immutable
entry main after only the exact reviewed owner/mask delta is normalized.
Six independent ownership, resource-mask, control-order, tolerance and direction
mutations must be rejected. See C27 and ADR-0034.

## Required focused qualification

The probe compiles the actual complete reader TU and fifteen other production
units, not a selected parser-body adapter. Four bounded fixtures cover flat and
curved patches, shared boundaries and a reversed repeated incidence, with empty
and populated Geometry prefixes. Normal contracts require independent result
ownership, repeated reconstruction and live owned incidence after each operation.

The 131 expected ASan/static Debug CRT outcomes include eight rejected input
classes, deliberately corrupt observer-prefix detection, actual ASan UAF, actual
CRT leak and actual allocation-hook controls. Sixteen complete CRT sweeps deny
every calibrated allocation for direct parsing/reconstruction and empty/seeded
Geometry. Every ordinal must be present once, record one actual denial, propagate
an exception, retain a live committed prefix and finish with zero retained blocks
and bytes. Expected nonzero instrument controls are not memory-safety passes.

Eight GCC C++17 paired live traces compare 24 patch records, 384 ordered control
records, 96 curve-incidence/direction records and 3456 Parameterize/Qu/Qv scalar
bits against original actual reader execution. Sixteen MSVC ASan/CRT live pairs
must also match their nonempty control/incidence/scalar rows. Original retention
can fail CRT exit checks while still supplying live numerical comparison rows.

The original full 131-outcome campaign retains 72 failed outcomes and 59 other
expected outcomes. All sixteen original allocation sweeps are partial: 240 actual
denials were observed before failing chunks; later ordinals are unmeasured. Seeded
rejection failures include retention from the original seed read, not a newly
inferred validation defect. No failed original or incomplete sweep is relabeled
as repaired-code validation. Earlier focused probe reports remain separate.

```powershell
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/audit_serial_reader.py --candidate-root .
python tools/qualify_serial_reader.py --asan '<qualified ASan probe>' --crt '<qualified static Debug CRT probe>' --runtime '<qualified MSVC runtime>' --output '<new directory>'
python tools/compare_serial_reader.py --original '<original GCC probe>' --candidate '<candidate GCC probe>' --original-root build/s33-original --candidate-root . --output '<new directory>'
```

For historical raw-result reproduction, explicitly use the original snapshot's
recipe and source tree, not the migrated candidate API:

```powershell
cmake -S build/s33-original/docs/evidence/stage3/caller_roots -B build/original-caller-roots -G "Visual Studio 17 2022" -A x64
cmake --build build/original-caller-roots --config Debug --parallel 2
python build/s33-original/docs/evidence/stage3/caller_roots/reproduce.py --executable build/original-caller-roots/Debug/serial_reader_root_probe.exe --output build/original-caller-results
```

The snapshot is extracted directly from the immutable entry commit's src/include/
libs and original evidence. Keep Windows/GCC/MSVC configurations separate. The
quality guide documents the equivalent explicit Windows GNU configuration.

## Observed exact-head and post-merge results

Both full implementation campaigns pass every required command on the same
603 protected inputs: 47 CTest, zero skips/failures, 74 Python controls, all prior
28 memory batteries plus 131 new outcomes (29/3005), sixteen complete sweeps/2731
actual denials, eight GCC/sixteen MSVC live pairs, six preservation mutations,
all retained scalar/analytic gates, read-only selected lint, explicit changed-
range/new-probe formatting and exact twice-repeated accepted/rejected article
regression. Independent command/case/child-log/artifact/source identity checks
pass. [Delivery qualification](stage3/serial_reader/delivery_qualification.json)
retains exact revisions, source manifest, command/log identities and battery
inventories. Raw failed originals and earlier focused records remain separate.
Zero configured hosted checks is absence of hosted validation.

The closure delivery changes documentation and evidence only. Its exact head and
merged main must retain all 603 protected input hashes and repeat the 47 CTest
entries, 74 Python controls, architecture, whitespace, checkout, environment and
remote tree/branch/PR/check audits. These checks establish source equivalence to
the fully qualified implementation; they do not replace either full campaign.

## Full delivery gates and closure limits

Required exact-head/main delivery adds application.serial_reader_contracts and
tooling.serial_reader_preservation to the previous 45 CTest inventory, retaining
all 74 Python controls and 28 prior memory batteries. The new battery makes 29
batteries/3005 expected outcomes; 47 CTest entries must execute with zero skips.
Retain all prior analytic/scalar comparisons, selected read-only lint, explicit
changed-range/new-probe formatting, current architecture/contracts, hashes and
twice-repeated exact Eistute/Book accepted/rejected/OBJ/incidence/CSV traces.
The local and remote delivery records must identify the exact revisions.

Code, C27, tests, this evidence and ADR-0034 define one bounded parser/result and
reconstruction-owner boundary. No formulas, floating-point order, template/front,
synchronization, interning tolerance, adaptive budget or acceptance/stopping rule
changes. No whole-reader rollback, post-failure retry, arbitrary I/O mutation or
complete-process/parallel/LSan/UBSan qualification follows. Broader input/models,
other loaders, Model/copy, Hermite and remaining UV/cache/metadata roots retain
their finite pending obligations. The full stage 3 is not closed.
