# ADR-0021: consume raw element ownership before storage allocation

Status: accepted; exact published-head and implementation-main gates pass through PR #62.

SubMesh::SetElement promises adoption but previously constructed its unique_ptr
inside vector emplacement, after a possible allocation failure. Actual pinned
units reproduce one leaked triangle on failed empty/populated insertion.

Delegate through AddElement with an owning by-value unique_ptr argument. This
consumes exclusive ownership before vector allocation, preserves successful
identity/order/null semantics and uses the already established owning entry point.
It does not change SetNoh, which copies a borrowed node instead of adopting it.

Triangle construction registers node observers before either insertion API is
entered. Its destructor does not unregister them. Failure cleanup therefore
requires terminal owner unwinding before adjacency is consumed; there is no
exceptional graph reuse/retry/rollback claim. Do not add metadata snapshots or
silently change triangle registration/destruction as part of this entry repair.
Require exclusive deletable elements, live nodes and nonthrowing destructors.

Classification: resource-lifetime defect repair, preserving numerical success.
Constructor registration/observer lifetime is the next isolated item; estimator
root ownership, populated SubMesh move assignment and full-process/parallel
qualification remain separate. See [evidence and limits](../evidence/STAGE3_ELEMENT_ADOPTION.md).
