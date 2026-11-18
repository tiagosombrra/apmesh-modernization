# Step 1 / Step 2 boundary provenance and template-center review

Date: 2026-11-18 Fortaleza. Read-only audit of exact source
`beb2aee2605110ec5c7a542bb45b10cb8c876b40`, draft PR240. Canonical starting
checkpoint53b3266; modernization main ef40c0f remains separate. Retained hosted
run44408768431 is reverified successful; no tests are rerun or newly qualified.
[Evidence](evidence/BOUNDARY_ORIGIN_AND_CENTERS_20261118.json) records original
history hashes, every measured side and retained/proposed point witnesses.

## Why the visible boundary changes

The user observes QUAD near the boundary in Step1 and mainly TRI in Step2.
Reconcile every final face by vertex cycle against `seed_faces` and actual
prospective `commits`, independently deriving outer edges by incidence one.
Do not infer provenance from shape, color or final post-smoothing coordinates.

| Scope | Step1 | Step2 |
| --- | ---: | ---: |
| Native leaves | 16 | 67 |
| Interior template QUAD | 16 | 242 |
| Advancing-front QUAD / TRI, whole transition region | 8 /8 | 7 /52 |
| Faces with an actual outer-contour edge: QUAD / TRI | 8 /0 | 2 /8 |
| Interior-template interface edges | 16 | 56 |
| Original outer-contour segments | 8 | 10 |
| Cells excluded by clearance0.2 | 0 | 0 |

None of the template faces touches an original outer-contour vertex in either
step. The eight contour QUADs at Step1 come from prospective front decisions.
Step2 still has two contour QUADs, both on v=0 (the analytical curved side in
XYZ); the three straight physical sides u=0/u=1/v=1 each have two contour TRI.
Five other front QUADs lie in the transition. TRI also touch contour vertices,
so the table's outer-edge count must not be mistaken for all boundary-incident
elements or for the total52 front triangles.

The stage loop in `controlled_patch_application.cpp` replays each stage's own
captured native tree/source and calls Generate to construct a fresh mixed layout.
It does not preserve the previous mixed face types or just subdivide each old
QUAD. Inner and outer partitions evolve differently; here inner interface16->56
while outer8->10. This explains the changing candidate geometry, not a proof of
the best possible transition or a new accepted mixed adaptive process.

For every one of the eight Step2 TRI with an outer edge, its two actual QUAD
alternatives are nonconvex/collapsed or fail the existing S<=1.5 rule. Several
convex proposals have S=1.7048327646991335; one has1.5233032987035993. Those
alternatives are rejected and TRI is retained. The stage itself is not thereby
rejected. Across all52 TRI commits:57 alternatives lack a valid prospective
triangle,36 produce a nonconvex/collapsed union and11 exceed S1.5. These are
104 alternative decisions, not104 rejected meshes or independent convergence
observations. The local search/order remains the existing rule; this audit does
not exhaust all possible quad combinations.

Both stages exclude zero cells by the0.2 clearance rule. That recent repair does
not explain this particular Step1->Step2 difference. Smoothing retains face
connectivity, so it also cannot change a QUAD into TRI. No threshold is relaxed.
Mixed boundary TRI are allowed by the planned method; their poor quality and
the measured spacing mismatch remain valid limitations requiring separate work.

Personal visual comparison, no mesh edits:
`build/quad-boundary-origin-20261118/step1_step2_origin.png`.
Blue means template QUAD, green front QUAD, orange front TRI and red original
contour. It shows the UV chart, not the analytical XYZ shape; geometry is from
the existing fifth-pass snapshot. Two fully inspected panels have readable
titles/legend. The existing Blender is not changed this session.

## Progress on the authorized next action: center interpretation

Reinspect complete printed pp287-288 of the original seven-page1993 scan;
local bytes again match SHA256
49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5.
Figure7's paragraph specifies polygon midpoint subdivision and a polygon
centroid connected to the midpoints. It does not state a numerical equation.
The referenced1987 Baehmann et al. publisher record is located at
[DOI10.1002/nme.1620240603](https://doi.org/10.1002/nme.1620240603), but attempts
to read its publisher full text/PDF remain unavailable. Search results and
papers merely citing it are not substituted for primary formula evidence.

Current application PointRule computes the arithmetic mean of polygon vertices.
The existing experimental point-rule implementation also supplies a signed-area
centroid. A geometric centroid of the filled planar region is the stronger
mathematical interpretation of the wording, not proof of the authors' code.
No area-weighted physical-surface centroid or numerical formula is invented.

Reconstruct actual pre-smoothing polygons from each seed QUAD's source corner,
edge midpoints and center incidence. Every retained center equals its source
vertex mean. In Step1,0 of4 polygons distinguish the rules; in Step2,18 of62 do,
maximum displacement0.003882062460937146 in UV; in Step3,0 of156 do. This is a
coordinate comparison, not a newly generated alternative mesh or improvement
measurement. Existing normalized96-case quality evidence remains scoped and
does not establish a universal winner.

A descriptive scientific question is sent: adopt existing signed-area centroid
in UV as an explicit experiment and compare actual histories before integration,
or retain vertex mean until historical evidence is confirmed. Explain the
difference, affected18 polygons, unavailable1987 full text and absence of a
quality/error guarantee. User answer is pending at this checkpoint. The general
instruction to continue the plan does not silently select a new formula.

## Closure and next action

Read-only classification, polygon reconstruction, evidence and documentation
are audited. The initial diagnostic assumed native output retained commit order;
it actually groups physical face kinds. Reconcile exact face cycles instead and
retain this diagnostic correction; there is no production defect finding here.
No native build/test, new generation, policy/center change, Blender change, merge
or whole-stage closure. Existing source85/native20/hosted4 checks remain retained
evidence ofbeb2aee, not checks on a new centroid rule.

Next: obtain the pending scientific center decision, then implement only that
bounded rule in the article experiment with original TRI and current front/
curve/smoothing/adaptive contracts preserved. Regenerate and compare real
histories before independent review/integration. Keep mixed global error and
accepted adaptation0, old enum-analysis/WSL dispositions, historical identity
and broader exact-head/research-merge/native/oracle gates open.
