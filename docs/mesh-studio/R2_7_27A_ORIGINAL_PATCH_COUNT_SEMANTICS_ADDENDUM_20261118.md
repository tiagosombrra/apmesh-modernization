# Mesh Studio R2.7.27A — source-defined denominator correction (read-only forensic addendum)

**Recorded after** the immutable R2.7.27 preregistration and its initial read-only auditor implementation. This is a **correction to the scope of logical inference**, not a new C++ generation trial, an added experimental treatment, or a revision of the preregistration. Retain the prior protocol unchanged for audit history.

## Original generator source establishes a stronger result

In exact original `src/generator/generator_adaptive.cpp` Git blob `844673ea764f3092330e5e9ebb01d8eb339869bc`, the candidate generation loop iterates **exactly once per CAD patch index** (`for (unsigned int i = 0; i < geometry->GetNumberPatches(); ++i)`). During each iteration it increments `current_underresolved_transition_patch_count_real_` **at most once**, if and only if a nonnull original `Adapter::DomainStructuralStats` reports `structural->transition_underresolved != 0`. After the loop it computes

```cpp
current_underresolved_transition_fraction_real_ =
    static_cast<double>(current_underresolved_transition_patch_count_real_) /
    static_cast<double>(geometry->GetNumberPatches());
```

This denominator is **the full geometry patch count**, not a narrower eligible-transition count as provisionally described in the original R2.7.27 protocol. The original Eistute model and actual accepted postcommit source-sidecar independently certify `native_source_patches=4`. The same input geometry is used for each source-scoped step/retry, and the algorithm does not add CAD patches when generating/rolling back a candidate.

Therefore at original source step 4, both the baseline and the preregistered R2.7.26 trial have true source `underresolved_transition_fraction=1.0`, implying `count_real = 4`, **and, since each of the four patch slots contributes at most one, all four distinct patch slots were flagged**. We know the exhaustive set is `{0,1,2,3}` for this exact input geometry. This is a legitimate deductive inference from the **unchanged compiled source**, not a newly recorded patch-level observer.

**What still cannot be inferred:** individual values of `transition_floor`, `interior_transition_imbalance`, `generated_faces`, quality or the exact structural mechanism for **each patch**; those fields are held in `current_patch_adaptation_[i]` in the source, but are **not** in the R2723 compact precommit gate record. A later purely observational source-attested per-patch export would be needed for **quantitative attribution**, not for identifying which slots were flagged at step 4.

The R2.7.27 auditor should additionally fail closed unless (a) the original generator source blob is unchanged, (b) these exact count/increment/division source expressions are present, and (c) the independently trusted original Eistute accepted source report has four CAD patch slots. It may report the **logically derived** count 4 and all four flag slots only for the exact observed fraction 1.0; no broad inference about fraction values for unrelated geometries or unobserved runs.

**Unchanged conclusion:** Eistute original and trial still have only one original C++ committed step each. Each step-4 rejected candidate violates both readiness `fraction <= 0.25` and coherence `penalty <= 0.42`, as the unmodified penalty has the provable lower bound `0.55 * 1.0 = 0.55`. No rewritten acceptance policy, new accepted epoch, welding or R2.8 scientific LOD is authorized. PR #239 remains draft/unmerged.
