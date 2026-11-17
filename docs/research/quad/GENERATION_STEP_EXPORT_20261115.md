# Actual generation steps and accepted-source repair

Classification: behavior-changing defect repair in the opt-in research export,
plus synchronous value observers. Default TRI formulas, budgets, acceptance,
retry/stopping rules and the experimental interior point rule are unchanged.
The user requested per-step QUAD/TRI output and Blender inspection and explicitly
chose to preserve current criteria while mixed scientific policy is undecided.

**Subsequent user instruction:** the user explicitly rejected the stable-mode
point clipping and asked to generate the curved geometry. That supersedes the
earlier request to preserve those controls. This research case now selects the
existing `legacy` original-curvature profile, without stable point/element
budgets. No new discretizer, estimator or numerical acceptance formula is added;
default TRI configurations remain unchanged. The earlier stable profile is
retained as an explicit executable control in the application audit.

The curve now retains nine original surface-pass points at step 1 and 65 at
steps 2/3. The physical reconstructions are 165 nodes/120 QUAD/68 TRI, then
953 nodes/784 QUAD/224 TRI. All are exported. The existing TRI curvature metric
accepts step 1 and rejects steps 2/3 for increased relative surface-curvature
error; those reference outcomes are preserved separately from generation.
No mixed scientific acceptance is claimed. The native legacy iteration limit
is unchanged. The analytic model is shown before the generated sequence in
Blender, clearly labelled as a display evaluation rather than an output mesh.

## Repair

The former primary export used the last locally selected source even when its
TRI reference was globally rejected. The primary OBJ now uses the last accepted
reference source. Rejected proposals remain separate, clearly labelled history.
No mixed scientific acceptance is inferred from reference TRI acceptance.

A second ambiguity existed between different domain generations within one
outer attempt. Each native generation now has a scoped ordinal carried with
the actual DomainCandidate through existing selection/moves. Begin/selection
observers join its native source to the physical state, instead of assuming
the last Adapter invocation won. This does not change candidate selection.

Observers copy source values synchronously while owners are live. Initial and
terminal physical TRI states retain node IDs, ordered faces and exact UV/XYZ.
They do not retain borrowed mesh/node/cell pointers. Curvature scalar cloning
and ordered node-element incidence use the existing typed history contracts.

For each completed source step, the application writes the actual TRI state
and a QUAD/original-AFT reconstruction from its selected native tree. If that
tree has no interior cells, the step honestly retains its actual TRI mesh with
zero QUAD. It does not invent an interior island to make a visualization dense.

## Outputs and inspection

Run the existing `configs/quad/curved_patch_original_curves.conf` with a serial
experimental build. Alongside `<prefix>.obj`, `<prefix>.steps/` contains:

- `manifest.csv`: step, epoch, retry, domain generation, reference outcome,
  actual stop reason, TRI/mixed filenames and measured physical counts.
- `step_*_tri.obj` and `step_*_quad_tri.obj`: initial and completed-step states.
- `curve_stages.csv`: original parameter values after the curve pass, surface
  pass and final point-budget rebuild, with attempt and curve identity.

The initial curve parameter list may not yet be initialized although its two
endpoint nodes exist; the input trace records that absence rather than creating
synthetic parameters. Subsequent pass parameters are recorded after their actual
return. The archive is prepared under a reserved `.steps.pending` directory and
published only when its manifest and trace finish. Existing main/archive/pending
outputs are refused before native execution. Multi-file crash recovery remains
a separate accepted-history gate; partial failures are not successful archives.

`tools/quad_generation_blender.py` creates a new inspection scene from this
archive using Blender's supported background Python interface. It preserves
mesh coordinates and compares TRI/mixed by step. White curves are labelled
analytic display guides, yellow lines are the actual mesh chords, and rejected
reference steps are visibly labelled. These guides are not new mesh samples.

## Validation and remaining scientific scope

The independent application audit checks all source steps and outcomes, exact
TRI node/face/UV values against existing full-precision incidence JSON, physical
source geometry/topology, primary accepted-source retention, complete curve-pass
traces, corrupt history/source controls and nonempty rollback. The legacy OBJ
writer uses fewer digits; its rounding is not a reason to relax geometry tests.
Fixed16 remains a separate unchanged-byte regression.

Development failures are retained: the first join found multiple locally selected
domain sources; the scoped domain ordinal resolves that ambiguity. The first
history comparison used the legacy rounded OBJ; the existing max-precision
incidence JSON supplies the exact oracle instead. Exact candidate compiler,
sanitizer, regression and remote results must be recorded in the canonical
checkpoint after execution; this implementation note alone is not qualification.

The retained stable-mode control still demonstrates discarded curved-boundary
samples. The repaired research profile bypasses that controller by selecting the
existing original-curvature flow and verifies equality between the complete
surface-pass and final partitions. It does not introduce a mixed estimator or
acceptance policy. The history remains TRI-driven, accepted mixed adaptive epochs
remain zero, and R3/M7 is open.
