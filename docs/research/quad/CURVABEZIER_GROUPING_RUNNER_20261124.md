# Portable CurvaBezier grouping trial

Recorded 2026-11-24 Fortaleza.
[Runner, native changes and directed tests in draft PR 265](https://github.com/tiagosombrra/apmesh-modernization/pull/265).
[Commands and evidence](evidence/CURVABEZIER_GROUPING_RUNNER_20261124.json).

The package connects the previously measured adjacent-group selector, native
detached reconstruction and the frozen two-grid evaluator. The controlled
runner depends on the tracked source checkout, Python and a serial C++17 build
with the experimental QUAD option enabled. It uses a fresh output directory
and the existing CurvaBezier configuration.

```text
python tools/quad_grouping_trial.py --exe <path-to-ap_mesh> --out <new-directory>
```

The first native invocation provides the TRI and mixed histories. The selector
derives its groups and comparison region from the preceding mixed mesh. The
second native invocation replays the same history and stages the grouped
candidate while retaining the original patch owner. Native replay checks both
groups and 2:1 balance. The runner checks the eight reference meshes and the
predecessor front, ordered source curve witnesses and the paired evaluations
before selecting any candidate. Reports record the status and file hashes.
The Python process replaces its selected OBJ only on eligibility. No C++ owner
is moved to the candidate during the staging trial.

| Directed application check | Selected output |
| --- | --- |
| Eligible candidate | Candidate file, 683 nodes and 725 faces |
| Forced rejection after successful comparison | Original mixed OBJ, byte identical |
| Fine-resolution request | Original mixed OBJ, byte identical, no staged candidate |

The eligible OBJ and both comparison reports match the prior isolated native
transfer. The minimum angle in the affected region is 8.24 degrees after
smoothing and the patch-wide minimum is 1.87 degrees. Rejection is a forced
control with the same valid candidate. The selector veto is an injected fine
request using the retained physical sizing replay.

MSVC 19.44 x64 Debug C++17 compiles and runs the exact review tree
`8d360190` at remote head `da4501a4`. The directed suite invokes the runner
outside its checkout and writes to a path with spaces. All three outcomes,
54 native source negatives and 26 Python comparison and reporting tests pass.
The local validation adapter lacks its default required tools and baseline
receipt. The focused build used the configured MSVC profile, and the staged
quality check used installed clang-format 19.1.5 after formatting the new
C++ additions. The initial development CLI string generation issue and
formatter findings were corrected before the exact validation. Hosted checks
on the draft are recorded as pending at this checkpoint.

The selected output is an OBJ of the bounded experiment. The runner supports
one CurvaBezier attempt. Issue 221 still requires a qualified mixed estimator,
accepted-state provenance and repeated mixed-driven epochs. Crash recovery
across native ownership and experimental file publication remains open.
Accepted mixed epochs: zero.
