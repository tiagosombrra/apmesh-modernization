# Book relative-area experiment: no geometric improvement

Classification: an authorized isolated scientific experiment with a negative
outcome. Advisor alignment was explicitly confirmed for changing only local
smoothing area acceptance at Book patch 0, step 2. No default-policy integration
was authorized or performed. Reference source:
`e6001d3d4dfbbeec1546f16d49438f9041caf577`.

## Question and controlled change

The existing absolute signed-UV-area floor rejects an equilateral triangle with
edge 1/128 even though its native quality is 1. The frozen Book case contains
32 such short shared-curve segments, each incident to 28 sheets. The resulting
896 incidences cannot reach UV quality 0.60 while retaining area above 0.0001.
This geometric constraint does not establish that relaxing the floor improves
the actual smoothing trajectory.

The experiment compares `A > epsilon` with finite, positive
`A > epsilon * Lmax_squared`, where epsilon remains 0.0001. The candidate applies
only to the three existing smoothing checks at patch 0, step 2. The quadtree,
curve sampling, boundary synchronization, quality score, trial directions,
global error formulas and acceptance/stopping criteria remain unchanged.
Native absolute-area degeneracy counters retain their original definition.

The two executables use identical production objects except for one copied AFT
translation unit. A control uses the original predicate with identical
instrumentation. Both conditions were repeated twice with the original Book
article configuration; only input/output paths were relocated. The control
matches all four retained mesh/metric/decision states exactly. A supplemental
observer was then repeated twice under the same candidate policy to explain
the unchanged result, and preserves that candidate's outputs exactly.

## Results

| Patch 0, step 2 | Control | Relative area |
| --- | ---: | ---: |
| Triangles / nodes | 708 / 486 | 708 / 486 |
| Physical quality below 0.30 | 70 | 70 |
| Minimum physical quality | 0.1070494631 | 0.1070494631 |
| Mean physical quality | 0.6220672387 | 0.6220672387 |
| Minimum UV quality | 0.1810018919 | 0.1810018919 |
| Mean UV quality | 0.7111669466 | 0.7111669466 |
| Minimum signed UV area | 0.0001060500 | 0.0001060500 |
| Native small-area faces / nonpositive faces | 0 / 0 | 0 / 0 |
| Global step-2 error | 168.932 | 168.932 |
| Native step-2 decision | rejected | rejected |

No final vertex position changed. The target patch's topology and all 262
boundary-node identities/UV/XYZ values agree. Other 27 patches agree exactly at
steps 2 and 3; initial and accepted step-1 states are unchanged. Independent
shared-boundary verification performs 27 incidence comparisons at every step,
covering the 28-sheet shared feature. The legacy summary's zero group comparisons
are not counted as validation.

Predicate controls pass 24 geometric cases, 96 context-scope checks and four
positive native-quality scale checks. Inverted, collinear, coincident, near-
collinear and nonfinite controls are covered. Outside the selected context,
the original predicate is preserved, including its original NaN comparison
behavior; this is not a claim that nonfinite meshes are acceptable.

The supplementary observer records 4,464 quality-shape trials. Relaxing area
allowed score evaluation for 104 trials that the absolute floor would veto;
**zero improved the existing local score**. Their score changes range from
-0.04045799094 to -0.00073973552, while acceptance requires improvement greater
than 0.00000001. The candidate therefore retains 325 Laplacian and 820 quality-
shape accepted-movement events, identical to the control. These are repeated
movement events, not counts of distinct vertices. Optional poor-region passes
remain disabled and are not positive execution coverage.

The area constraint remains real, but removing it alone is not sufficient for
these existing trial directions and score. The predefined geometric criterion
(fewer physical poor triangles without lowering minimum quality) fails.
Accepted states remain steps 0 and 1; steps 2 and 3 remain rejected. No scientific
improvement, accepted-candidate qualification or stage closure is claimed.

## Reproduction and evidence

The compact [result record](stage3/book_relative_area/result.json) retains metrics,
scope checks, executable identities and local report hashes. Detailed source,
objects, command vectors and raw outputs remain under
`build/book-relative-area-experiment/` in the measured workspace. The original
qualified runs and the default executable remain intact.

Two unapplied patches retain the actual experimental code with portable include
paths. In a separate checkout of the reference revision:

1. Apply [relative-area.patch](stage3/book_relative_area/relative-area.patch) with
   `git apply --unidiff-zero`. Build explicit serial C++17 Release control/candidate
   executables with `APMESH_RELATIVE_AREA_MODE=0` / `=1` respectively. Keep the
   reference compiler/options, including no fast-math, no LTO, disabled MPI/OpenMP
   and the existing aliasing option. This patch is experiment data; it is not
   applied to the production source in this repository.
2. Use the existing `tools/repeat_generation.py --model book --exe <binary>
   --output <fresh-directory> --timeout 300 --report <report>` for each condition.
   Require control agreement with the retained reference before interpreting the
   candidate. Run the independent generation, mesh and boundary-incidence checks.
3. For the supplementary observation, apply
   [score-observation.patch](stage3/book_relative_area/score-observation.patch)
   after the primary patch, build mode 1 and repeat twice. Require exact agreement
   with the first candidate's meshes, CSV metrics, decisions and prior counters.

Patch application and source equivalence are checked separately. A fresh full
rebuild from these portable patches has not been claimed to reproduce executable
bytes; the measured builds use the recorded translation-unit replacement and
record separate executable hashes.

An initial comparison stopped on the compatibility CSV's relocated `model`
output prefix. Its failed report is retained. The field was checked against each
actual configuration prefix, all other fields were compared, and the already
completed control repetitions were reused without regeneration. This was a
verification-preparation failure, not a changed scientific outcome.

Next single work: characterize the existing candidate displacement directions
and incident-face score response on the frozen Book state. Keep the area and
score criteria fixed during that analysis. Another algorithm/policy experiment
requires its own explicit scientific scope and alignment.
