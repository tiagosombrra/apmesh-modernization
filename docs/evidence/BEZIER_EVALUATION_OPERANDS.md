# Rejected Bezier operand-copy candidate

Disposition: rejected; no production, probe, guard or architecture change retained.
Starting production revision: d08d655e46d4e005d2561ac22f955ae4d50a8735.

The preserved CPU/stack diagnosis observed FindUV calling Bezier evaluation.
A bounded engineering candidate replaced nine by-value getter operands inside
CalculatePointUV with the identical member matrices/vectors, preserving every
product parenthesis, coordinate assignment, public getter, solver and policy.
The existing observer also flushed completed-call counters. This was a copy
reduction candidate, not Eigen removal or a scientific change.

Canonical GCC/checked-MSVC C++17 builds passed. The existing detached-copy probe
retained all 5,950 position/derivative vectors bit for bit, with its analytic
planar/bilinear checks and 16 Bezier direction masks. The existing suite passed
75/75 CTest and 389 original plus four candidate-only Python controls. Frozen GCC
Eistute preserved five states, 25 exact artifacts and 15 boundary comparisons.
An initial suite stopped at a stale inventory hash; that failed record and its
subsequent snapshot refresh are retained. No diagnostic was suppressed.

One checked-MSVC Eistute two-call process used the exact original configuration,
input, assertion hook, Debug iterator checks and total 300-second cap. The first
call returned zero with five archives, 14,660 FindUV calls and 1,542 I_MAX exits.
Its five independently checked states, 15 boundary comparisons and all 25
scientific artifacts matched the preceding version. The second call did not
return: the watchdog reached 300 seconds, with termination complete at 300.011 s.
The required two-call gate remained blocked. There was no second observation or
Book run. Original live output was restored byte-identically.

This observation does not demonstrate sufficient performance improvement or
resolve adaptive reuse. Rather than retain additional source-guard exceptions
and controls for an unsuccessful optimization candidate, restore all production,
probe, tooling, contracts and inventory bytes to the starting revision. Preserve
the earlier AFT incidence index and all original scientific/negative controls.
The candidate is not delivered, integrated or counted as modernization completion.

Reproduction and negative evidence: build/bezier-evaluation-borrow/ contains
entry.json, source-proof.json, rejected-candidate.patch, rejected-source/,
rejected-binaries/, rejected-manifest.json, preflight.json, both suite reports,
and msvc-eistute/process.json plus verification.json. The retained native binary,
PDB, configuration/input hashes, source snapshot and commands identify the exact
rejected observation. Canonical builds are restored from the unchanged production
sources; prior qualified regression evidence applies only to those restored bytes.

The next dependency remains identifying the residual cost in the current checked
MSVC reuse path. Do not assume that removing getter copies, another evaluator
rewrite or a larger cap will resolve it. Integration, Book qualification and
Stage 3 closure remain blocked by their existing required gates.
