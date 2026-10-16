# Generation validation contract (stage 1 draft)

## Process and input evidence

`tools/run_generation_case.py` runs one article configuration in a fresh output
directory. Only INPUT_MODEL and OUTPUT_PREFIX are relocated; source config and
executable hashes, command, exit code, timeout and wall time are retained in
process.json. New runs also bind the exact input model path/hash and reject input
mutation during generation. Never reuse an output directory for qualification.

`tools/repeat_generation.py` performs two runs with the exact same executable,
configuration bytes, command, working directory and output prefix. It backs up
all generated files before removing only the owned output files for repetition.
Both raw output sets remain available. The tool exits nonzero on strict drift.

## Input repair boundary

The new standard-library-only validator checks the indexed bicubic BP format
actually read by LoaderBezierPatchFile: column-1 v records with exactly three
finite coordinates and p records with 16 zero-based references to preceding
vertices. Blank lines and #/ // comments are accepted. A model must have at
least one complete patch. Existing coordinate order, control-point interning,
geometric formulas and tolerance policies are untouched.

Configuration uses KEY=VALUE, known runtime keys plus historical BUILD_DIR and
EXECUTABLE metadata, unique keys, complete finite numbers, bounded int parsing
and positive process/thread counts. Existing finite-value clamping remains.
WRITE_MODE must be m/q/h and USE_TEMPLATE y/n. Previously ignored malformed
input now fails explicitly; this is an intentional defect repair, not a claim
of byte-compatible error behavior. Other legacy reader APIs and concurrent
mutation of input files are not qualified by this CLI-focused delivery.

## Accepted-state evidence

For every generated stage, require exactly one mesh, one final acceptance log
and one metrics row. Filename stage and accepted/rejected suffix must agree
with log fields. Stage 0 must be accepted. A requested rejected stage fails
even if the OBJ exists and has the published triangle count. The corrected
historical verifier now rejects Eistute's stage-4 target in the observed run.

The CSV contains attempted states, including rejected candidates. Its nodes
field sums submesh node incidences, whereas OBJ deduplicates by global node ID.
Therefore those node counts are not assumed equal: exported vertices cannot
exceed CSV incidences. Triangle counts must match exactly. At stage 0 the legacy
acceptance log's actual_elements_step is a zero placeholder; counts are checked
through OBJ and CSV. Later candidate element counts must match their logs.
These distinctions follow the writer implementation, not relaxed tolerances.

Independently recompute finite coordinates, face indices, duplicate/degenerate
triangles, edge incidences and 2r/R quality using stable Heron's formula. Compare
quality to logged 3D statistics with an explicit absolute budget of 2e-4 for
the legacy six-significant-digit OBJ/log export. This export comparison budget
does not change meshing, adaptation or scientific acceptance thresholds.

Strict regression additionally requires identical OBJ hashes, all decision
fields, all CSV fields, accepted/rejected steps, final attempt reason and source
configuration hash. Numerical report differences fail; no new numeric tolerance
is introduced to conceal a discrepancy. The original reference's failed
repetitions remain evidence. The isolated smoothing-order defect repair is
qualified separately: compare the input-validation candidate against a reference
with only the same logical-order repair, require exact repetition of both, and
retain the original-reference differences. See evidence/STAGE1_SMOOTHING_ORDER.md.

## Incidence evidence and coverage

The serial SaveMesh observer writes apmesh-incidence-v1 JSON for every attempted
state, before later adaptation or rollback changes the state. Each snapshot
contains the stage, ordered patch indices, four runtime curve-group identities,
16 control points in BP record order, all owned node IDs/XYZ and every actual
triangle's local index and three [node_id,u,v,x,y,z] corners. Floating-point
values use max_digits10 and the classic locale. Non-finite values or output
failures throw. The observer does not call parameterization/inverse mapping.
MPI snapshots and non-Bezier input APIs are not qualified by this implementation.

The independent checker binds the recorded model hash, derives expected curve
identity from exact BP control tuples (forward or reversed), checks every patch
control net, and derives actual boundary chains from triangle incidences. Every
side must cover [0,1] without gaps/overlaps/disconnections. It compares all sheets
in each shared group, including non-manifold groups, after orientation
normalization. It checks runtime group splits/merges, local UV consistency,
node/face positions, global node identity and exact connectivity against the
actual OBJ (with only its documented six-digit coordinate serialization).

De Casteljau provides an independent boundary evaluator. Explicit arithmetic
budgets are 4*epsilon for parameter complement round trips and
512*epsilon*max(1,absolute control coordinate) per XYZ coordinate for evaluator
roundoff. They are not discretization, welding or scientific error budgets and
do not relax strict numerical report comparison. Input controls and identity
matching remain exact; legacy proximity-based interning that changes the source
net will be detected, not silently accepted. These budgets are qualified for the
measured fixtures/cases, not a universal forward-error proof for arbitrary scales.

If any snapshot exists, it must cover exactly every attempted state. Missing,
malformed, contradictory or failed incidence evidence fails default verification
as well as strict coverage requests. Without snapshots, legacy mesh checks can
run but explicitly report absent incidence coverage. Strict coverage requires
positive shared-incidence comparisons in every state; zero is never a pass.
The synchronized legacy group summary remains unmeasured; actual snapshot
observations provide independent evidence rather than certifying that summary.

When both runs have snapshots, strict repetition compares all incidence fields
and snapshot hashes exactly. Before/after comparison against an old reference
without snapshots explicitly returns boundary_regression=not_compared_legacy_reference;
it must be accompanied by separate positive coverage validation of the candidate.

## Separate mandatory report-semantics gate

Exact CSV repetition can reproduce a mislabelled column. The closure audit found
that adaptation_relaxation is placed differently in the legacy CSV header and
emitted row, shifting intermediate control labels. The independent
`tools/audit_metric_schema.py` checks 21 named control fields against the per-stage
analysis log without a numerical tolerance. `application.metric_schema` exercises
this check through actual generation and currently fails. Passing mesh/incidence
validation and strict repetition does not substitute for this required semantic
gate. See evidence/STAGE1_INCIDENCE_AUDIT.md.

Actual mixed-orientation generation currently also fails required CTest
`application.boundary_orientation`: the program can accept a degenerate initial
mesh. Analytic positive checker fixtures do not qualify the generator. Both
failures block stage 1 closure and integration; historical failures remain stored.
