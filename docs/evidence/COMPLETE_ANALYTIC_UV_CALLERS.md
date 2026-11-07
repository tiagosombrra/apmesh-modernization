# Complete native analytic UV callers

Classification: engineering-only required caller contract, S3-06/C10. Entry is
PR #175 main `3a333a960439599b363b33f39103ed664c947b73`; its exact-head/main
75 CTest / 499 Python seal is verified. Production, numerical inputs, formulas,
selection, templates, synchronization and stopping policies remain unchanged.
The [compact record](stage3/complete_analytic_uv/summary.json) binds source,
executables, native captures and preserved evidence.

## Missing observation and implementation

The required prefix fixture stopped at geometry entry. Separate geometry callers
stopped before fillMesh and improveMesh. Those observations could not establish
successful transfer and final mesh validity for these callers. An optional
`--complete` fixture mode now resumes the inherited native geometry method and
lets execute return normally through its original transfer and smoothing.
Default prefix mode, six nonempty/two guard-only/one refusal requirements and
historical refused records are preserved. Complete mode rejects guard-only or
missing-curve arguments before entering native execution.

The fixture saves nonowning template pointer lists only in complete mode. After
native completion it requires each saved vertex/edge pointer exactly once in its
front owner and observer lists and each saved face pointer exactly once in the
mesh. Source template owner lists must be empty. No production hook, synthetic
neighbor, selector override, allocation denial, fallback or retry is introduced.
Native front teardown completes before the original live-curve check.

## Fixed native matrix and independent oracle

The same six admitted UV-square contexts run observed/unobserved under GCC C++17
and MSVC C++17 Debug with iterator level 2: two subdivisions, masks 0/15, old UV
faces h=0.25; four subdivisions, masks 0/15, empty/two-face old UV. Existing live
linear Bezier sides, physical 2x3 rectangle, UV domain, ratio 1, tolerance 0.0001,
depth-1 tree, templates, numImproves 7 and phi 0.5 are unchanged. The configured
seven improvements do not establish seven executed passes: convergence remains
native and its pass count is unmeasured. The topology progress line likewise does
not establish entry into the optional topology fallback.

Both standalone builds pass. Each profile passes 17 prefix outcomes and 12 full
native calls. Within each ABI, observed/unobserved saved prefixes and full ordered
vertices, coordinates, edge endpoints, faces, areas, quality and owner/queue state
match exactly. Every child retains its original 30-second cap. No native process
fails, times out or is retried.

| Context | Transferred template V/E/F | Final V/E/F | Final UV area |
| --- | --- | --- | --- |
| Two subdivisions, seeded, masks 0/15 | 7/10/4 | 15/34/20 | 1 |
| Four subdivisions, empty/seeded, masks 0/15 | 9/16/8 | 25/56/32 | 1 |

All source owner lists and front/rejected queues are empty. An independent Python
oracle requires unique live IDs, finite unit-domain coordinates, positive signed
face area, face/edge incidence, root-side boundary, connected disk Euler identity
and unit total area. Final native quality is checked independently as 2r/R using
area and side lengths rather than the production center construction.

The native coarse minimum/mean quality changes from about 0.683282/0.803046 to
0.761679/0.889642. Fine minimum/mean changes from about 0.828427/0.828427 to
0.812546/0.857802. The fine minimum decreases under the existing smoothing
policy; this is recorded without changing that policy or claiming every metric
improves. Original and observed executions agree exactly.

Sixteen added checker/controller tests use two actual captured meshes and reject
failed returns, retained source owners, transfer loss, duplicate IDs, foreign
endpoints, missing/inverted faces, inconsistent final quality, remaining queues,
unknown/missing/duplicate output and continuation after failure/timeout. Timeout
controls preserve both partial byte streams and stop before the unchecked child.
These mocked controller cases are not additional native qualification.

## Delivery gates and remaining scope

The existing application.analytic_template_prefix CTest entry now requires the
17 prefix outcomes plus 12 complete outcomes. Require all 75 CTest / 515 Python
on exact delivery head and merged main, the separate checked-MSVC matrix,
configured read-only analysis, source reversal, inventory/contracts, whitespace
and fresh remote checks. Preserve all 522 production/build/input identities,
43 original evidence identities and all four qualified application executable/
archive identities. Reuse frozen science only by those unchanged identities.
Guarded same-tree main checkout and the canonical main MSVC build remain required.
The local build/complete-analytic-uv/delivery/integration-verification.json seal
must bind the actual final head/main results; this report alone is not integration.

This establishes successful full callers, template transfer and final smoothed
mesh validity for these six contexts. It adds no new ideal-adoption or outside-root
retirement qualification. Allocation-failure cleanup, logical rejection/retry,
rollback, setters/mate sharing/arbitrary aliases, leak/UB/parallel and whole-process
obligations retain their separate scopes. Stage 3 remains three bounded-qualified
and seven partial-open dispositions. No stage closure follows.
