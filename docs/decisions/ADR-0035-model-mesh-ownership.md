# ADR-0035: exclusive Model mesh adoption and explicit transfer

Status: bounded engineering defect repair; full qualification pending.

## Context

The original Model deletes raw mesh pointers in reverse order but permits
implicit copying. Both copy and rvalue expressions can duplicate owning pointers;
assignment also loses the prior destination. Original ASan reproduces UAFs and
static Debug CRT observes failed-append retention. Serial Generator uses its own
mesh_ owner; the two literal Model append sites belong to alternate GeneratorOmp.
No explicit production Model copy or derived Model was found in the source audit.

## Decision

Store unique_ptr<MeshAdaptive> owners, delete copy construction/assignment and
provide nonthrowing moves. Raw append immediately delegates to an owning overload;
both consume on entry, including allocation failure. Preserve committed prefixes,
identity, order, null/out-of-range getters and reverse destruction. Move transfers
the borrowed Geometry pointer, leaves the source empty/null and retires a populated
destination in reverse order through a temporary Model. Self-move is unchanged.
Geometry remains borrowed. Duplicate/foreign ownership and deletion of derived
MeshAdaptive through its nonvirtual base remain invalid. No shared ownership.

This is an intentional source/layout/copy contract migration, not an unmeasured
external binary-compatibility promise. Existing raw callers retain their normal
interface but must not delete an argument after a failed consuming call.

## Required evidence and limits

Use actual production units, independent analytic payload/adjacency observations,
original/candidate live pairs, runtime move/destination/self-move/reuse tests,
every calibrated insertion allocation, retained committed prefixes and actual
UAF/leak/hook/order/adjacency controls. Retain the original hazard evidence.
Exact-head/main full regression and remote audits block integration until passed.
No numerical policy changes, patch/current-submesh rebinding, complete caller
preparation, whole-process, parallel, LSan or UBSan safety follows. Pointer-taking
patch-copy semantics under C22 remain a separate audit.
