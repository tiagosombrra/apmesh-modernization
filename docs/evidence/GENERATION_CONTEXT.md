# Owned generation identity and output context

Classification: engineering-only production context migration. Entry main is
PR #140. GenerationContext owns four strings: input model, output prefix, write
mode and process suffix. It deliberately contains no numerical policy or mesh
owner. MakeGenerationContext copies the validated runtime identity; the CLI passes
that value into GeneratorAdaptive, which retains it in an optional value.

The generator is explicitly noncopyable/nonmovable, preserving its prior effective
restriction and keeping the owned strings stationary. Its Adapter observes the
context and is declared after its owner, so the borrow retires first. Context
views returned by GetGenerationContext are read-only and expire with the generator.
An independently constructed Adapter requires its observed context to remain live
and stationary. This does not establish arbitrary foreign-observer safety.

The serial reader uses the owned input path. Generator report/log/snapshot names,
format switches and compatibility/runtime summaries use owned identity fields;
domain adaptation logs receive the same prefix through the Adapter. The original
filename spelling, suffix concatenation, stream order and m/q/h decisions remain.
The default constructor retains live legacy reads through nonallocating accessors,
including consumers that change the globals between report calls. Runtime globals
remain for compatibility and unmigrated consumers; MPI/alternate loaders and
standalone estimate/curvature output helpers are outside this first lot.

Ownership is checked inside the existing metrics probe: the source context is
changed and retired, two generators retain distinct values, and three interleaved
report writes produce only their own prefix/suffix files despite conflicting
legacy globals. Existing metric expectations remain unchanged. No new test target,
matrix or scientific model is introduced. Explicit construction owns string copies
and changes allocation timing; legacy default construction does not allocate a
context. Numerical policies, boundary synchronization, quadtree/templates,
acceptance, retry and stopping criteria are unchanged.

Source reversal checks the generator/Adapter bodies modulo the named identity
access substitutions; numerical configuration and other production units stay
unchanged. Delivery uses C++17 GCC/MSVC builds, the existing 75 CTest/385 Python
controls, frozen nine-state scientific comparison (45 exact artifacts and 123
positive boundary comparisons), existing MSVC CLI controls, scoped analysis,
format/whitespace, contracts/inventory and exact-head/main/remote gates.
The [compact record](stage3/generation_context/summary.json) and local
build/generation-context bind the implementation and delivery evidence.

This isolates identification/output values, not complete generation state.
Numerical globals still require serialized execution. Interleaved report writers
do not qualify full reentrant or concurrent generation, same-Generator recovery,
parallel operation or Stage 3/6 closure. The next production lot must identify a
cohesive numerical/runtime-state contract before moving further globals.
