> Historical follow-up at 3271996. The subsequent STAGE1_INCIDENCE_AUDIT.md
> implements measured incidence checking and records newly exposed required
> failures. Current CTest is 5/7, not the historical 5/5 below. No stage closure
> or integration is qualified by this earlier numerical result alone.

# Stage 1 follow-up: deterministic smoothing reductions

Date: 2026-10-16 UTC. Work item: issue #2 / draft PR #3.
Base revision: `7853dd3ba817b0a0c8f24871ffad664faa28a79e`.

## Defect and isolated evidence

`Vertex::getAdjacentEdges()` returns `std::set<Edge*>`. The former
`AdvancingFront::findAdjacentEdges` copied that pointer order into the Laplacian
sum. Heap addresses changed between identical executions. Floating-point
addition is not associative, so this changed intermediate smoothing sums.

Two instrumented Eistute executions aligned 424,144 vertex visits. In 306,626
visits the center and the complete multiset of neighbor IDs/coordinates were
identical but their iteration order differed. In 5,685 of those visits the raw
sum differed. The first isolated example has raw Y sums
`0.063019097222222209` and `0.063019097222222223` with identical inputs.
`stage1/smoothing_probe_analysis.json` retains examples and trace hashes.

A separate 17-digit nodal trace found differences in internal triangle areas,
angles, coordinates and curvatures despite identical rounded OBJ exports.
`stage1/numerical_probe_analysis.json` retains that earlier observation. These
experiments explain why OBJ equality alone was insufficient.

## Repair classification and boundary

This is a **behavior-changing defect repair**, not a numerical-neutral refactor.
The adjacency helper orders by existing unique edge ID, assigned monotonically
by boundary/quadtree/front creation. Duplicate IDs fail explicitly instead of
falling back to addresses. No coordinate proximity is used to infer identity.

The neighbor set, formula, weights, relaxation, vertex iteration, backtracking,
quality checks, curvature formulas, quadtree/templates, AFT construction,
adaptation and acceptance/stopping thresholds remain unchanged. The deliberate
change is the order of floating-point additions. Other inputs, compilers and
parallel modes are not proven equivalent by these serial experiments.

The original reference is retained, including its strict failures. A controlled
reference uses main `b4087a472015d6898687c0aeff444efb4f1a9524` plus **only** the
same smoothing helper and call-site repair. It excludes the input-validation
changes. Exact comparison with this reference measures the input repair without
the known address-order defect. This is not a replacement of historical evidence
or a new comparison tolerance.

## Executed checks

GCC 16.1.0, MSYS2 UCRT64, native Windows serial Release, C++17; MPI/OpenMP/LTO OFF.

| Check | Result |
|---|---|
| Candidate exact-configuration repetition, Eistute | PASS, 5 OBJ and every CSV/decision field equal |
| Candidate exact-configuration repetition, Book | PASS, 4 OBJ and every CSV/decision field equal |
| Controlled reference exact repetition, Eistute | PASS |
| Controlled reference vs candidate, both cases | PASS, every OBJ/CSV/decision field equal |
| Instrumented candidate repetition, Eistute | PASS, 8 trace files / 12,968 nodal rows byte-identical at 17 digits |
| Original reference vs repaired candidate, Eistute | FAIL retained, 43 differing report fields; OBJ and decisions preserved |
| Original reference vs repaired candidate, Book | PASS |
| New cancellation/ordering control | PASS, all 6 logical allocation permutations, empty/singleton sets, duplicate-ID rejection |
| Build and CTest | PASS, 5/5 (including 38 Python and 23 invalid CLI controls) |
| New helper/probe clang-format; compiled probe clang-tidy | PASS |
| Required per-incidence boundary coverage | BLOCKED, absent coverage still fails |

The cancellation control exercises the production ordering helper with minimal
ID-bearing samples and deliberately cancellation-sensitive values. It also
checks that pointer-order summation exposes a different result. The application
repetitions exercise the helper with actual legacy Edge/Vertex objects. Legacy
full-project style/static-analysis debt and memory qualification remain open.

Both cases retain last accepted stage 1: Eistute 1,168 triangles, Book 4,418.
Eistute stage 4 remains rejected. Exact executable and source identities are in
`stage1/stable_source_manifest.json`; individual comparison reports use the
`stable_` prefix. No tolerance or regression assertion was relaxed.

## Reproduction

Build with `cmake --preset local-serial` and `cmake --build --preset local-serial`.
Use fresh output directories for these commands:

```sh
ctest --preset local-serial --output-on-failure
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh --model eistute --output build/repeat-eistute-new --report repeat-eistute.json
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh --model book --output build/repeat-book-new --report repeat-book.json
```

On Windows append `.exe` and put the qualified UCRT64 toolchain on PATH.
For the controlled reference, use main's exact `src/main.cpp` and
`src/input_output/patch_reader.cpp` with this candidate's smoothing helper/call
site, using the same build configuration. Run it in fresh directories and use
`tools/verify_generation.py CANDIDATE_RUN --baseline CONTROLLED_REFERENCE_RUN`.

Diagnostic instrumentation is retained as unapplied patches, outside production
sources. In separate disposable checkouts, apply
`stage1/diagnostics/numerical_traces.patch` to base revision `7853dd3`, or
`stage1/diagnostics/stable_numerical_traces.patch` to the repaired revision.
Only use these probes in the serial configuration. Set
`APMESH_NUMERICAL_TRACE_PREFIX` to an absolute path ending in
`OUTPUT/working/numerical_trace` before running the repetition tool with
`--output OUTPUT`. The eight CSV files in each archived repetition must compare
byte-for-byte after repair. To trace the actual smoothing inputs as well, set
`APMESH_SMOOTHING_TRACE` to `OUTPUT/working/smoothing_trace.csv`; those files are
large and remain local. Each row records the actual ordered neighbors and sums,
without replacing the algorithm's arithmetic. The diagnostic patches are not
part of the qualified production build.

Reproduce the isolated-input count with the retained streaming analyzer:

```sh
python docs/evidence/stage1/diagnostics/compare_smoothing_traces.py OUTPUT/repetition-1/smoothing_trace.csv OUTPUT/repetition-2/smoothing_trace.csv --report smoothing-analysis.json
```

## Integration status

The numerical repeatability blocker is resolved for the two measured serial
cases. Stage 1 remains incomplete: the legacy exporter does not preserve every
patch/curve incidence, and synchronized reports compare zero curve groups.
`--require-boundary-coverage` continues to fail; its retained negative result is
`stage1/stable_boundary_gate.json`. Keep PR #3 as a draft and main unchanged.
Next work is incidence export and independent checking of every shared boundary,
including reversed orientations and non-manifold sheets. No stage 2 work began.
