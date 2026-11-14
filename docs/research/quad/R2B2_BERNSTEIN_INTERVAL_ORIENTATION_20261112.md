# R2b2 — interval-wide Bézier radial orientation (research-only candidate)

## Why the earlier sample sweep is not enough

The original source-wide physical audit on Eistute (4 incident sheets, 10 source
intervals, 39 samples) and Book (28 incident sheets, 12 intervals, 47 samples)
observed no cyclic radial order changes. This cannot rule out two crossings
between samples. Book's smallest sampled angular separation is about 1.823
degrees, so a mesh admission decision cannot be based on the sampled sweep.

## Exact algebraic quantity under study

For the original shared cubic curve `C(t)`, let `T(t) = C'(t)` (degree two).
For incident original bicubic Bézier patch `P_i(u,v)`, let

- `E_i(t)` denote its exact shared boundary restriction (degree three);
- `I_i(t)` denote its edge-parallel restriction at the same fixed inward chart
  offset `1/64` as the previously qualified sampled source witness;
- `R_i(t) = I_i(t) - E_i(t)` (degree three), oriented consistently in the
  **original source curve parameter** even for reversed patch incidences.

For every adjacent pair `(i,j)` in the real sampled cyclic fan at `t=0.5`,
test the scalar polynomial

`D_ij(t) = T(t) · ( R_i(t) × R_j(t) )`.

This polynomial has degree at most **eight**. Its positivity has an invariant
geometric meaning: project both original inward displacements into the normal
plane of the original tangent. Their signed orientation is positive, because
tangent-parallel components vanish from the triple product. It does not require
an arbitrary moving angular-zero reference.

The research condition is that **every adjacent pair preserve its initial
oriented sector sign throughout every closed original source interval**. For a
reference cyclic gap in `(0, pi)`, this requires strictly positive `D_ij`;
for a valid wide gap in `(pi, 2pi)`, strictly negative `D_ij` is required.
Checking only positivity would incorrectly reject a legitimate wide empty
sector in Book. Near 0, pi, or 2pi, the reference sign cannot be trusted:
the pair is classified **inconclusive** rather than silently omitted.

Strict sign of the triple product excludes loss of source tangent, projected
radial collapse and pairwise collinearity on the entire interval. Continuity
of the original polynomial fields and the reference cyclic order then excludes
a crossing of adjacent sheets; the circular order is preserved by continuous
deformation unless an adjacent pair collides. This is a **local radial-order**
condition only, not a proof of global disjointness of whole surfaces or a
classification of physical sheet ownership.

## Evaluation strategy and numerical gate

- Extract the original four-by-four `PatchBezier` control net using its
  `GetPtXX` accessors; never fit a curve to sampled radial angles.
- Form the edge-parallel cubic control nets using tensor-product cubic
  Bernstein weights at the fixed inward offset, reversing the longitudinal
  cubic controls when the original patch edge is reversed.
- Obtain the original `CurveAdaptiveParametricBezier` tangent controls as
  `3(P1-P0), 3(P2-P1), 3(P3-P2)`.
- Convolve Bernstein controls with the exact integer binomial factors,
  enclosing every floating-point operation with outward `nextafter` bounds.
  Signed triple-product coefficients provide a degree-eight interval
  enclosure.
- Restrict this polynomial to **each actual source parameter interval** by
  interval-valued de Casteljau subdivision. If all coefficient lower bounds
  are strictly positive, the Bernstein convex-hull property proves
  positivity on the entire interval, not only at the tested samples.
- For a wide initial reference gap greater than pi, negate all degree-eight
  polynomial coefficient intervals and prove strict positivity of `-D_ij`,
  equivalently strict negativity of `D_ij`. A validated opposite sign is a
  **sign-inverted** interval, not an acceptable orientation.
- Otherwise subdivide with a finite recursion budget (currently 10).
  Record a sign-inverted interval only when an opposite-sign convex-hull
  sign is established on a subinterval. A mixed, zero-touching or exhausted
  branch remains **inconclusive**, never accepted.

The reported certification is conditional on IEEE-754 conforming finite
operations and on the stated outward-rounding implementation, with no
`-ffast-math`, reassociation or unsupported toolchain assumptions. The
original source-control values are regarded as the input floating-point
coordinates. The observed native `PatchBezier` implementation, exact
control-net conventions, compiler toolchains and interval bounds require
independent tests before scientific acceptance. A positive test is not an
independent numerical proof of that implementation's correctness.

## Adversarial and scope gates

The candidate includes distinct controls for strictly positive orientation,
reversed orientation, zero/collapsed radial, and a cubic whose endpoints have
the same orientation but whose interior is inverted. It rejects malformed
parameter intervals. Original source-model reporting must include **all**
adjacent pairs times original curve intervals, with separately classified
positive, inverted and inconclusive outcomes.

The current stage does **not** claim certification before its exact-head CI
and actual per-model result logs have been inspected. If one sign is
inconclusive, the complete fan remains unqualified. In particular, endpoint
degeneracy is **not** silently ignored: a closed-interval certificate may be
more restrictive than the physical requirement on the open interior. This
potentially requires a separately reviewed endpoint-exclusion/root-isolation
theorem, not a tolerance-based acceptance.

**Out of scope:** arbitrary non-adjacent self-intersections or patch interior
collisions; patch-to-volume sheet classification; assigning halfedge twins at
valence 4/28; node ownership/welding; full physical mixed `SubMesh` commit;
repeated model adaptation; historical 1993 point-selection formula; and
production QUAD. The implementation keeps `automatic_sheet_pairing_enabled=0`
and `global_mixed_model_admitted=0`, preserves the original TRI behavior,
and remains in draft PR #214 targeting the separate research branch.

## First exact-head CI defect review (2026-11-12)

The preceding experimental push `9d6b46e9d9ba8f9161a34fbaf8f7128196f342c5`
[failed its Linux root CTest gate](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43307082540),
despite native Linux/Windows QUAD and frozen TRI comparison passing. The source
test output showed **Eistute 40/40 sign-certified pair-intervals** with original
Bézier controls, but the new report printed a literal backslash-n rather than
a line ending. The Book source stopped before its interval marker with
`R2b2 continuous Bezier fan interval accounting incomplete`; the initial
candidate rejected wider-than-pi cyclic sectors before counting every pair.

The repair requires retaining wide sectors with **negative** signed scalar
orientation and proving their expected sign, while retaining zero/pi/two-pi
reference ambiguities as `inconclusive` entries. It also repairs the record
newline, strengthens source-wrapper count checks and adds an explicit
expected-negative synthetic control. These are defect repairs in the separate
research candidate, **not** changes to production TRI or newly approved
surface pairing. Until the post-repair exact-head full root tests pass and
the actual Book sign counts are inspected, the interval gate is pending.
