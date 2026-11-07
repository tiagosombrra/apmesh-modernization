# Serial executable-owned CRT lifetime checkpoint

Entry main: `78b9fbf8b150793505946291245873582dc164e0` (PR #167).
Classification: engineering-only required S3-09 W-CRT observation. This follows
the integrated [retained-request attribution](SERIAL_CRT_STATIC_TEARDOWN.md),
whose exact head/main pass 75 CTest entries / 463 Python controls without skips.
Its local integration seal is build/p3-serial-crt-static/delivery/integration-verification.json.

## Fixed admission

The 150-request census excludes allocations first created during shutdown and
does not account for every executable-owned normal/client CRT allocation. The
concrete missing observation is a checkpoint before user-priority executable
initializers through their final static destructor, enclosing the actual serial
RunApplication entry and all its local owners. Runtime/DLL initialization before
the checkpoint, other heaps and later runtime/DLL shutdown remain explicit scope
boundaries; no whole-process/other-instrument equivalence is inferred.

A separate test-only lifetime target links the unchanged complete 75-unit MSVC
C++17 Debug engine with iterator level 2, /EHsc and the existing two-job/600-second
build limit. An early lib-priority RAII owner keeps its checkpoint anchor live
until the final independent CRT dump. No production global is reset or warmed.
Normal/client signed deltas and every newer-live-block dump are retained; net
zero alone cannot establish a clean result.

Require actual release, global-owner release, shutdown-created allocation/release,
deliberate main retention, deliberate shutdown retention, and a second-allocation
denial with real first-owner unwind. The two retained-storage controls must
detect one 64-byte block even when the native process returns zero. The early
observer must run after the normal user-priority owning destructor. Any failed
build, instrument control, unmatched diagnostic or application/checker result
stops expansion and is retained before a justified response; no hidden retry.

Only after calibration, observe existing SP-02 once with its unchanged 60-second
bound and independent physical/UV/positive-boundary checks. If clean, the fixed
SP-01..08 recipes in the [serial ledger](../architecture/SERIAL_EXECUTION_LEDGER.md)
are eligible in their existing finite order, with their original 10/60/300-second
caps and no changed numerical input or model. SP-09/10 require their separately
qualified full-caller terminal observer; they are not silently counted here.
No Cartesian instrument/model campaign, parameter search, unsupported-domain
restriction, additional optimization or scientific policy change follows.

## Calibrated result and fixed inventory

The [compact record](stage3/serial_crt_lifetime/summary.json) binds the unchanged
engine archive, native executable, generated Debug flags, source/input identities,
six actual controls, raw captures and independent checkers. All controls pass
their prescribed outcomes. Real 64-byte allocations are independently identified
with _CrtIsMemoryBlock in main or inside the static destructor; a zero total
without an actual allocation is not release calibration. Main/shutdown retention
each produce exactly their own live 64-byte request. The second allocation is
actually denied; its first owner unwinds and final normal/client accounting is
clean. Native exit 0 in deliberate-retention controls remains an expected
negative, not a clean application result.

| Case | Covered observation | Final normal/client result |
| --- | --- | --- |
| SP-01 | All 23 existing malformed invocation/configuration/model controls; nonzero, Error diagnostic and no generated artifact | Zero deltas; empty newer-object dump |
| SP-02 | Original aligned two-sheet fixture, accepted step 0, positive independent physical/UV/boundary checks | Zero deltas; empty newer-object dump |
| SP-03 | Existing m variant; real nonempty OBJ and independent analytic boundary check | Zero deltas; empty newer-object dump |
| SP-04 | Existing q variant; five physical and ten UV CSV fields independently checked; boundary paired to the real SP-03 OBJ | Zero deltas; empty newer-object dump |
| SP-05 | Unchanged curved_reversed_3_side_2 input; accepted 0/1, rejected 2/3 and actual retry | Zero deltas; empty newer-object dump |
| SP-06 | Two fresh Eistute article processes; exact repeatability and positive independent boundaries | Zero deltas; empty newer-object dump |
| SP-07 | Two fresh Book article processes; exact repeatability and positive independent boundaries | Zero deltas; empty newer-object dump |
| SP-08 | Unchanged existing Eistute no-sync configuration; normal return and static/local owner teardown | Zero deltas; empty newer-object dump; no boundary qualification inferred |

This accounts for the 32 prescribed SP-01..08 executions. The output-mode q
observation uses actual mode-m geometry from the preceding same-input run; it
does not fabricate a q OBJ or establish standalone q geometry coverage. The
repeat helper retains the same executable, configuration, command and working
output path. Each repetition is checked independently before a following native
launch. Every existing per-process 10/60/300-second bound is retained; neither
model, numerical policy nor selection is changed. This is no timing improvement
claim and does not qualify same-Generator reuse.

## Preserved parser failures and bounded continuation

The initial fixed-inventory attempt stops at missing_model: the native app
returns -1, exposed as unsigned DWORD 4294967295 by Windows, and raw captures use
CRLF. The parser initially accepts neither signed reporting nor that raw newline
form. After signed-code correction, a second prefix still stops at CRLF. Both
native captures contain the expected rejection and clean final heap, and both
failed orchestration reports remain byte-identical. They are tool failures,
not solver failures or successful whole campaigns.

The corrected parser normalizes only the parsed newline view and compares all
32 process-code bits, retaining signed native reporting and raw bytes. Mismatched
codes still fail. Offline reanalysis validates both original captures. The
existing invalid-input helper now accepts an explicit nonempty, unique subset
of its existing names, preserving canonical order and the default full 23 cases;
empty, duplicate and unknown selections fail before execution. This permits
running only the 22 unexecuted negative cases. Final audit finds that the early
wrapper exception prevented the missing_model helper from recording its generated-
artifact census, although its expected rejection and final CRT were captured.
One isolated named missing_model run measures that remaining gate: Error,
nonzero return, clean final CRT and zero generated artifacts together. Neither
partial prefix is substituted for a complete gate. There are 32 qualified
inventory observations plus the two preserved parser-prefix executions. No
CompletedProcess is substituted, native result manufactured or other successful
scientific run repeated for the checker corrections.

Local build/p3-serial-crt-lifetime retains qualification, both failed prefixes,
their driver snapshots, resume classification, the complete resumed inventory,
source/input pins and commands. Read-only analysis passes on both new C++ units
with the existing repository check policy. The qualified old engine and both
earlier observer executables remain byte-identical.

## Delivery and remaining scope

The required exact-head/main regression is the existing 75 CTest inventory, now
475 Python controls, without skips, plus source/input/evidence identity, checked
Debug flags, scoped analysis/formatting, whitespace, links, contracts and fresh
remote review. Native observations are reused only within their recorded source,
compiler, binary, input, checker and checkpoint scope. No repeat of the fixed
native campaign is required for unchanged delivery bookkeeping.

S3-09 remains partial/open. The five directed SP-09/10 terminal CLI/library
contexts require their separate full-caller observer. Runtime/DLL baseline and
shutdown outside this checkpoint, other heaps, LSan/UBSan, changed-dependency
ASan requalification and parallel coverage retain their obligations. No Stage 3
row is closed by zero residuals in this finite Windows serial window. All three
bounded-qualified and seven partial/open dispositions are preserved. No additional
source-audit or scientific campaign is selected automatically.
