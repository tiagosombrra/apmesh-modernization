# Adaptive generation reuse: initial consistency metadata

P4 engineering diagnostic-state repair, starting at main
d1619137af4ad53e3bb98cf5fc4336f75350629f (PR #162).
Two successful Eistute calls on the same captured Generator reproduce one strict
difference: the second call reports consistency_regularization_active=1 in the
step-0 acceptance record instead of the fresh value 0. Every OBJ byte and all
accepted/rejected decisions already agree. The final adaptation's current flag
survives because it was reset between adaptive steps but not at generation entry.

Reset only that demonstrated flag at the serial generation boundary, beside the
existing archive isolation. The first-call constructor value remains 0; later
adaptation updates are unchanged. No acceptance formula, policy, decision, output
schema, layout, API, captured control or parallel path changes. Other current
fields are not reset speculatively.

## Fixed observation and gates

The existing metrics probe accepts the existing Eistute/Book article configs and
runs two typed Execute calls on the same stationary captured Generator. Runtime
configuration is reapplied and Timer is fresh for each call. Scientific input and
config values are unchanged; only input/output paths are relocated. The caller
archives completed output directories between calls so append-mode reports do
not mix files. There is no selector or failure injection and the process cap
remains 300 seconds for both calls together. No new fixture or CTest target.

GCC first and second outputs must match the frozen fresh-instance reference:
nine states, 45 exact artifacts and 123 positive boundary comparisons per call
across the two models, including full accepted/rejected traces and IDs. Eistute
has five states (accepted 0/1, rejected 2/3/4); Book has four (accepted 0/1,
rejected 2/3). Saved owner and FindUV call/exit counts agree between calls.
MSVC's first output is independently checked for physical/parametric quality and
positive boundary coverage; the second is compared strictly with that fresh
same-ABI output. No cross-ABI byte equality or self-comparison is claimed.

The initial launcher selected the retained original-source directory as output;
no generator process ran. A later report-printing error stopped postprocessing
after Eistute had completed. Both preparation failures are retained. Corrected
postprocessing consumed the existing files without repeating Eistute, then found
the original one-field regression and stopped before Book. The candidate corrects
that field and admits both unchanged article cases. Original sources, executables,
raw outputs, differences and commands remain under build/adaptive-generator-reuse.

Require the fixed GCC/MSVC reuse observations on exact head/main, canonical
builds, all existing 75 CTest entries/389 Python controls and native markers, the
ordinary nine-state/45-artifact/123-boundary frozen regression, three FindUV
summaries, 23 MSVC invalid CLI controls and one analytic state/boundary. Require
source reversal, unchanged scientific inputs/guards, scoped analysis, formatting,
whitespace, inventory/contracts and staged/remote checks. Unchanged destructor
instrument evidence is reused by identity; no new instrument campaign. Timing
CSV values remain outside byte preservation, as in the existing regression.

This closes the observed initial consistency-record leak and qualifies only two
normal adaptive calls with the same captured Eistute or Book profile within
S3-05/08. Exception recovery, context changes, arbitrary output reuse, interleaved/
concurrent execution, external Geometry, other inputs and complete-process memory
retain their obligations. Stage 3 remains open; no broader reuse claim follows.
