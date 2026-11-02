# Typed engine execution request

Classification: engineering-only caller/interface refactor, supporting S3-05 and
the bounded stage 6 engine boundary. Entry main is PR #141. The production CLI
passes GenerationRequest directly to GeneratorAdaptive::Execute instead of
creating string and pointer vectors and asking the engine to decode them again.
The request owns an optional fallback input path and carries integer process/thread
counts. Its lifetime covers the synchronous call; the engine does not retain it.
The CLI still constructs the owned GenerationContext from validated configuration.

The serial reader keeps its previous priority: the generator's owned context
input wins, otherwise the request path is used. With neither, the historical
built-in model is selected. An engaged empty path is still a file input, subject
to the existing reader validation; it is not converted to the built-in model.
Counts are supplied from validated configuration. No new validation, clamping,
scientific policy or global-state migration is introduced. Serial generation
continues using its historical default generator counts; conditional MPI/OpenMP
calls receive the same process/thread values and retain their original routing.
Those branches gain no new compiler/runtime qualification from this serial lot.

Execute(char*[]) remains available with its original valid null-terminated layout
precondition. It prints every supplied argument, converts counts only where the
old conditional branch consumed them, copies the fallback path only when needed,
and delegates to typed execution. Null input retains the old built-in-model branch.
Copies and conversion timing can change; no allocation-failure equivalence is
claimed. The CLI prints its seven original argv[] records in the original order,
including template mode, before typed execution. Direct typed callers do not print
an argument transcript. Output naming/formats and the context ownership contract
from the preceding delivery remain intact.

Targeted checks extend the existing metrics probe: three typed and two raw calls
must propagate the exact existing reader failure, retain a copied/retired source
path, distinguish empty input, honor context precedence and print only at the
compatibility boundary. The original eight-attempt/132-field metric oracle and
two-context interleaved-output control remain unchanged. Existing real CLI
scientific executions exercise the successful typed path and its seven transcript
values; no new test target, scientific model or instrument campaign is added.

Require C++17 GCC/MSVC builds, 75 CTest entries/385 nested Python controls, the
frozen nine-state/45-artifact/123-boundary scientific reference, existing MSVC CLI
negative/analytic controls, scoped analysis, explicit format/whitespace, contracts/
inventory and exact-head/main/remote audits. Source reversal verifies the complete
generator body modulo the named request bindings and the unchanged CLI sequence
modulo request construction/transcript relocation. The [compact record](stage3/typed_generation/summary.json)
and local build/typed-generation bind source, commands, hashes and results.

Numerical globals remain shared and require serialization. This removes an
internal textual protocol; it does not qualify full reentrancy, concurrent runs,
same-Generator recovery, complete-process memory or Stage 3/6 closure.
