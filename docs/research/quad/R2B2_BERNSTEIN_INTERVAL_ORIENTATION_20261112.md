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

The research condition is **strictly positive on every closed original curve
parameter interval for every adjacent cyclic pair**, and initial observed
adjacent gaps strictly between 0 and pi. Then the tangent cannot vanish and no
adjacent projected radial can become zero or collinear on that interval.
Continuity of the source polynomial fields and their cyclic order at the
reference parameter permits continuation of the radial fan without an adjacent
swap. The sum of positive adjacent gaps cannot jump winding number. This is a
**local radial-order** condition only, not a proof of global disjointness of
whole surfaces, nor a classification of physical sheet ownership.

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
- Otherwise subdivide with a finite recursion budget (currently 10).
  Record a negative interval only when a negative convex-hull sign is
  established on a subinterval. A mixed, zero-touching or exhausted branch
  remains **inconclusive**, never accepted.

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
