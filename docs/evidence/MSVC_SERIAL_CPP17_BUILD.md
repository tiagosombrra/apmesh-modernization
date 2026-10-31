# Complete serial C++17 build with MSVC

Classification: engineering-only portability and automatic scratch ownership.
Base: PR #133 main `57d4cac866cf6a8677d33370e2367fc60045ee01`. This delivers
P1, the bounded stage 4 prerequisite for S3-09. It does not close Stage 3 or
qualify whole-process memory, MPI/OpenMP execution or C++23.

## Implemented correction

The original complete serial MSVC build failed with undeclared M_PI and
runtime-sized local arrays. The failure, 60 diagnostics and compiler error limit
remain immutable under build/stage3-consolidation-audit/msvc-observation.
No source unit is excluded to obtain this build.

- curvature_discrete.cpp includes the project's existing definitions header,
  obtaining the existing fallback pi literal. No curvature expression changes.
- CalculateAreaPatch replaces its two runtime-sized double arrays with
  unique_ptr owners of default-initialized arrays of the same requested extent.
  The quadrature tables, branches, loop bounds, weights and accumulation order
  are unchanged. No zero initialization, new weights or domain policy is added.
- Communicator.cpp replaces 35 local runtime-array declaration sites, containing
  42 Int buffers, with unique_ptr owners of default-initialized arrays. Raw pointer
  views retain the original variable names and decay/call types. Every extent,
  index, count/displacement expression and communication call remains unchanged.
  Serial still uses its real NoCommunicator/TMCommunicator path.

These are dynamic allocations in places that previously used stack VLAs.
Allocation failure may now throw and memory/performance characteristics differ;
no unchanged-allocation, rollback or MPI exception guarantee is claimed. Owners
release buffers on scope exit. Historical uninitialized/undefined quadrature
order 5 remains unchanged and unqualified; only defined orders 3 and 4 are
checked here. This repair does not silently supply a new quadrature rule.

The local source-scope verifier reverses only the recorded includes/storage
declarations to every original production byte, including comments. Every other
src/include/libs file and all 66 protected raw article inputs remain unchanged.
Compiler/runtime routing macros, MPI/OpenMP branches, formulas, scientific
criteria, boundary synchronization, quadtree/templates and front order are fixed.

## Reproducible full target and artifact

On the qualified Windows/Visual Studio 2022 x64 toolchain:

```powershell
cmake --preset windows-msvc-serial
cmake --build --preset windows-msvc-serial
```

The actual executable is `build/windows-msvc-serial/bin/Debug/ap_mesh.exe`.
The preset selects the complete existing ap_mesh source target, C++17, Debug,
MPI/OpenMP off and LTO off; it does not substitute extracted production methods.
Debug runtime/iterator checks are retained. This is a development Debug artifact,
not a qualified Release distribution or an ASan/LSan/UBSan run.

## Focused and application verification

One additional CTest entry, application.serial_cpp17_portability, reuses the
existing full-native curve_orientation_probe executable with an explicit test
argument. No extra production CLI mode or duplicate full-source target is added.
Its MSVC compiler conformance mode matches the existing ap_mesh /permissive-
setting so the native alternative operator tokens are accepted.

The test requires the existing IEEE-754 double pi bits, analytic areas 6 and
sqrt(61) from affine patches at orders 3/4, and four typed buffer forwarding
observations with exact counts/extents/payloads. The recording transport checks
the actual convenience wrappers and is not MPI execution qualification. It
reports language mode and iterator level; actual MSVC Debug must report C++17
and iterator level 2. Curve owners outlive patch retirement in the new cases.

The real compiled MSVC CLI also exercises the existing 23 invalid-input controls
and the existing aligned two-surface generation/independent geometry/boundary
checks. This is a bounded real-process smoke, not all supported-process lifetime.

Exact delivery head and main require 74 CTest entries without failures/skips,
including the existing 380 nested Python controls. The GCC C++17 reference is
rebuilt and its existing Eistute/Book runs must retain all nine accepted/rejected
states, 45 exact scientific artifacts and 123 boundary-incidence comparisons
against the frozen qualified reference. Runtime fields and the already specified
relocated output-prefix field retain their established comparison treatment.
No input, baseline, threshold, acceptance or stopping policy changes.

Changed source lines and the complete new test header receive scoped analysis;
legacy diagnostics outside that declared scope remain debt, not a whole-program
clean claim. Formatting is explicit and limited to changed lines/new header.
Required whitespace, architecture/contracts, staged bytes and remote audits
remain gates. Rebuild the actual canonical MSVC target and revalidate main after
merge; initial successful builds alone are not delivery qualification.

## Preserved preparation and scope limits

An initial preparation rejected a wrong array-site count and implicit locale
decoding that altered comments. Original bytes were restored and UTF-8 made
explicit before compilation; that rejected preparation is not native evidence.
The first focused-test build lacked a pure virtual fixture method and the
production conformance flag; its source/log remain retained. The corrected test
adds the required recording method and matching /permissive- flag. Production
formulas and the successful complete target were unchanged by those corrections.

Local build/msvc-serial-build-repair retains original sources/executable,
reversible edits, the first production build, rejected preparation/test sources,
compiler logs, real CLI observations, source/analysis checks and exact delivery
records. The [compact evidence](stage3/msvc_serial_build/summary.json) binds the
scope and commands. Successful artifact/build identity is recorded in the PR
and local integration seal; P1 completion does not imply complete Stage 4.

P1's compiler-blocker implementation is complete after its exact-head/main gates.
S3-09 still requires supported complete-process instrument observations. P2 is
next: define the supported serial executable/input/caller and terminal-versus-
retry ledger using existing controls before freezing the P3 instrument inventory.
Stage 3 remains open; no new numbered memory slice or scientific result follows.
