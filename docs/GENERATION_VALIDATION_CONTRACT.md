# Generation validation contract (stage 1 draft)

## Process and input evidence

`tools/run_generation_case.py` runs one article configuration in a fresh output
directory. Only INPUT_MODEL and OUTPUT_PREFIX are relocated; source config and
executable hashes, command, exit code, timeout and wall time are retained in
process.json. Never reuse an output directory for qualification.

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
is introduced to conceal the current Eistute repeatability blocker.

## Boundary coverage limit

The legacy OBJ carries no patch/sheet incidence labels. Its indexed edge counts
cannot prove compatibility of every incident parametric boundary. Moreover,
the legacy summary only compares curve groups when synchronization is disabled.
The synchronized article cases consequently report compared_groups=0.

`--require-boundary-coverage` fails for the current export, even if a legacy
group summary is measured. Default accepted-mesh validation reports absent
incidence coverage explicitly and does not certify compatibility. Exporting
and independently checking each incidence, including reversed orientation and
non-manifold sheets, remains required work; do not infer it from error zero.
