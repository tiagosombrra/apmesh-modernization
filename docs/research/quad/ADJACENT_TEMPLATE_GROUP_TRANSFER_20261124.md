# Native transfer of adjacent template grouping on CurvaBezier

Recorded 2026-11-24 Fortaleza. [Commands, hashes and metrics](evidence/ADJACENT_TEMPLATE_GROUP_TRANSFER_20261124.json).

The researcher approved one comparison of an automatically selected adjacent
group under the [frozen eligibility rule](GROUPING_ADMISSION_AND_TRANSFER_20261124.md).
Use CurvaBezier Step 3, retry 0, from the original TRI source. The selector
defines the evaluation region from the unsmoothed limiting TRI on the preceding
mixed front before generating the candidate.

The primary group alone keeps the T6 side split because two half-size leaves
from the same neighboring parent meet that side. Their unique parent is
selected from native leaf geometry. Grouping both changes the primary template
to T5 and projects a physical edge length increase from 0.047312 to 0.097253
in model units. Prospective checks require four actual leaves in each parent,
2:1 balance across the copied tree and a better ratio between the replacement
edge and the transition face size. No active finer requests from the retained
physical residual replay affect the edited or changed neighbor boxes. An
injected finer request inside the additional block vetoes the same projection.
The protection test runs in the selector; no negative mesh is reconstructed.

One native research application re-generates the original mixed predecessor,
calls the Python selector on the fresh trace and stages the detached candidate.
The selected blocks coincide with the earlier manually supplied pair. The
quadtree changes from 223 to 217 leaves and produces 619 seed QUADs. The native
owner, incidence order, previous OBJ, all eight reference-stage TRI and mixed
OBJ files, and 14 original curve segments are preserved. Candidate geometry
and connectivity reproduce the manual archive. An independent replay checks
all 106 front transactions, five UV smoothing passes, 155 template polygon
centers and nine boundary forgeries. The local implementation uses a fixed
workspace driver and does not supply a portable installed entry.

| Measurement | Predecessor | Candidate |
| --- | ---: | ---: |
| Regional minimum angle before smoothing | 1.418 deg | 3.057 deg |
| Regional minimum angle after smoothing | 6.989 deg | 8.242 deg |
| Full-patch minimum angle after smoothing | 1.870 deg | 1.870 deg |
| Regional maximum neighbor size ratio after smoothing | 5.1931 | 4.8631 |
| Regional geometric RMS before smoothing | 0.0356831 | 0.0359095 |
| Regional geometric RMS after smoothing | 0.0164245 | 0.0157619 |
| Full-patch geometric RMS after smoothing | 0.0095417 | 0.0094863 |
| Nodes / faces | 689 / 732 | 683 / 725 |
| TRI / QUAD | 102 / 630 | 100 / 625 |

RMS values are in model units. Both sampling densities confirm lower
final regional and patch-wide RMS and sampled maximum. The final candidate
is **eligible** under the frozen rule. The prior mesh remains the active
output during the rehearsal. The pre-smoothing RMS increase and unchanged
final global minimum expose separate limits. The region here is the footprint
of the worst original TRI and differs from the three-TRI polygon reported in
the older manual comparison.

Build and native invocation pass with MSVC 19.44.35229.0 x64 Debug C++17,
taking 7.57 s and 32.99 s. The first Python audit loaded an older metrics
module. Correcting the import path order allowed the numeric checks to run
on the existing files. Five evaluator tests pass again on PR 264 head
`e1775f38`, and the four hosted checks on that unchanged draft are green.
The default validation wrapper still lacks its tools and validation receipt.
The isolated source diff, selector, meshes and traces are retained locally.
No new full matrix, sanitizer, portable feature integration or scientific
adaptive acceptance is claimed. Mixed adaptive epochs accepted: zero.

Proceed with a portable experimental runner that links the existing selector,
native staging and eligibility decision, records both candidate outcomes and
preserves the predecessor on rejection. Before counting mixed epochs, resolve
the source-compatible estimator and the accepted state and rollback gates in
[issue 221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).
