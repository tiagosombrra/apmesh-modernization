# Mixed-cycle admission and stopping proposal

2026-11-25 Fortaleza. [Replay evidence](evidence/MIXED_ADMISSION_CONTRACT_20261125.json).

## Development replay

The replay evaluates five staged native candidates against their own mixed
predecessor. It checks each source mesh, original TRI mesh, native source
tree and staged candidate by SHA-256. It recomputes geometry on common
24 × 24 and 48 × 48 UV sites on each original analytic patch. Regional
shape uses physical angles, TRI shape and QUAD scaled corner Jacobian
in the existing contour-edge, contour-vertex and interior groups.

| Staged candidate | Faces, parent → candidate | RMS drop | TRI touching only a contour vertex below 5° | Existing diagnostic |
| --- | ---: | ---: | ---: | --- |
| CurvaBezier screened | 732 → 779 | 23.80% | 25/92 | Interior TRI angle and shape |
| CurvaBezier grouped | 732 → 754 | 24.57% | 23/90 | Interior TRI angle and shape |
| CurvaBezier refined | 732 → 789 | 24.34% | 26/97 | No veto |
| Ribbed Bracket screened | 547 → 648 | 36.83% | 0/51 | Growth, interior TRI angle and shape, interior QUAD shape |
| Ribbed Bracket selective | 547 → 604 | 13.02% | 0/48 | Interior TRI angle and shape, interior QUAD shape |

RMS reductions compare to the mixed predecessors on the denser grid and
all five reproduce the reduction on the coarser grid. Maximum sampled
distance improves in all five on both grids. Counts below 5° are an
illustrative comparison, with counts below 10° and 20° in the evidence.
The predecessors have 38/94 and 5/53 such TRI, respectively. The
CurvaBezier refined archive passes the existing diagnostic but retains
a worst transition TRI of 2.27°. Ribbed improves transition TRI while
creating seven and three interior TRI below the old diagnostic angle
floor in the screened and selective outputs, respectively. The worst
interior TRI drops from 26.57° to 18.37° in both Ribbed arms. Enforcing
no deterioration at every possible cut-off of the regional quality
distributions would veto at least one metric in every archive. The
observations support explicit quality targets and reporting of both
the count and proportion of faces below them.

Four outputs have the native certificate. The replay verifies its ordered
parent interval, endpoint IDs and inserted site for each split. The
selective Ribbed output passes independent ordered contour verification
but predates the native certificate. It remains a numerical control.
The CurvaBezier refinement is a directed development comparison.
A reusable size field must request useful refinements without selecting
a model, step, leaf or face by identity.

## Proposed ordered decision

1. **Validate and bind the candidate.** Stage its mesh, curve partition,
   native tree, and size requests against the exact accepted owner entry.
   Require valid analytic placement, incidence and mesh coverage. Require
   an identical contour or a certified ordered subdivision of the same
   contour. Preserve shared-curve conformity when there are two owners.
   A failed binding, topology check or certificate rejects the candidate.
2. **Require physical safety and account for quality by region.** Require
   safety floors for every candidate element and use higher quality targets
   per populated region and element type. Use physical minimum angle
   together with TRI shape or QUAD scaled corner Jacobian. A newly populated
   group must meet its targets. An existing group whose candidate remains
   below a target must preserve or improve its minimum and must not increase
   either the count or fraction below that target. Report retained
   shortfalls, removed and absent groups explicitly. Remove no coverage
   obligation when a class disappears. Also report the realized physical
   size contrast at contour, transition and interior. Full quality
   qualification requires all populated groups to meet their targets.
3. **Require measurable geometric improvement at bounded cost.** Compare
   area-weighted RMS and maximum distance on the same analytic sites on
   both predetermined grids. Require the configured positive relative RMS
   gain and maximum non-regression on both. Use fixed evaluation slack if
   needed for floating-point ties and state it in the profile. Enforce
   explicit per-cycle growth and total face budget before committing.
   A zero-RMS predecessor cannot provide positive relative RMS gain.
4. **Make progress and stop explicit.** Record no-op when the size field
   generates no requests. Stop as blocked when existing requests cannot
   be realized or construction or admission fails. Keep the exact accepted owner state
   and retained diagnostic evidence on rejection. On admission, atomically
   adopt the candidate and use it as the only source of the next cycle's
   feedback. Stop when the agreed geometric and quality targets are met,
   the cycle or face budget is exhausted, or there is no admissible
   progress. Count a new epoch only for an actual committed distinct state.

The guard ordering and target rule are proposed for alignment. The five
archives were replayed using the existing diagnostic profile only as a
controlled proxy. Its 1.42° transition angle and 10.42% growth bound reflect
the development data. Establish one independent profile before the reserved
run, including safety floors, regional targets, budgets, improvement,
stopping tolerances and deterministic request order. Run the same profile
and executable without geometry-specific exceptions. Before transfer,
exercise real accepted-owner reentry and rejected-candidate rollback
on development cases.

## Validation scope

The replay uses the Python evaluator at the exact PR 278 source revision.
From the repository workspace run
`python build/quad-mixed-admission-contract-20261125/replay.py`
with the archived inputs identified in the evidence. Twenty-four
boundary and certificate mutation controls are refused. Seven small
regional target controls cover inherited and new poor faces, an
improved minimum with additional poor faces, and absent classes.
Two geometry controls reject identical error and an improved RMS paired
with a larger maximum. Input and candidate artifacts retain their hashes.
The four exact PR 278 checks cover the prior executable revision.
This study has no native generation, threshold adoption, reserved-case run
or accepted mixed epoch. Global mixed-curvature error and shared-curve
qualification remain open.
