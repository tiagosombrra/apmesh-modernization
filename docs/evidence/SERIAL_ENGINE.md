# Linkable serial engine and thin CLI

Classification: engineering-only production extraction supporting the caller-root
work and the stage 6 library boundary. Entry main is PR #139. The bounded 2026
milestone is a reusable internal serial engine/configuration/CLI boundary with
preserved C++17 behavior, not completion of the modernization roadmap.

APMesh::Engine aliases the static ap_mesh_engine target. The executable now has
a five-line main delegating to apmesh::application::RunApplication. Production
runtime configuration, process-state definitions and application execution live
under include/application and src/application. LoadRuntimeConfig and
ApplyRuntimeConfig are available through the runtime_config header; call them or
RunApplication only serially because the legacy process-wide globals remain.
There is no installed SDK, stable external ABI, reentrancy or thread-safety claim.
ApplyRuntimeConfig expects values validated by LoadRuntimeConfig. Same-process
reuse retains its previous unqualified status; serialized access alone does not
establish that repeated configurations are safe.

The CLI and two principal consumers link the same engine. Their compilation graph
falls from 219 source compilations to 78: 75 engine units and one source for each
executable. This is verified from compiler commands, not a performance benchmark.
All three existing consumers stop embedding main.cpp. GNU wrapping contracts
remain on their existing consumer and are checked by the existing suite.

All 203 global definitions keep their initializer tokens and declaration order in
one production unit. Configuration defaults, whitespace/key validation, numeric
conversions, clamping, assignment order, synthetic arguments and CLI body retain
the original token sequences. Only module placement, linkage and the entry name
change. New modules use English; existing scientific identifiers are preserved.
MSVC explicitly retains /EHsc and diagnoses missing unwind semantics as an error.
The generator, formulas, quadtree/templates, boundary synchronization, acceptance,
retry and stopping policies are unchanged. Eigen and parallel qualification remain
separate obligations.

The [compact record](stage3/serial_engine/summary.json) records the production
outcome, verified source extraction, successful canonical GCC/MSVC builds and
scoped analysis. Delivery requires the existing 75 CTest/385 nested controls,
affected real MSVC CLI controls, frozen nine-state scientific reference (45 exact
artifacts/123 boundary comparisons), format/inventory/contracts and exact-head/
main/remote gates. Local build/serial-engine retains commands, original source,
reference executables and exact delivery reports. Existing input fixtures and
negative controls are reused; no new instrument or scientific campaign is added.

Stage 3 stays open. This delivers a library boundary, not removal of all globals,
full caller/foreign-owner/recovery safety or completion of stage 6. CRT/LSan/UBSan
and parallel observations remain required at the appropriate closure boundary.
