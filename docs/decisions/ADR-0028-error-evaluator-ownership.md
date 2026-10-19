# ADR-0028: own each temporary error evaluator

Status: accepted for the bounded repair; full scope and receipts in
[the evaluator audit](../evidence/STAGE3_ERROR_ESTIMATE.md).

The estimation caller allocated a GeneratorAdaptive without deleting it, retaining
both the object and its serial per-submesh error vector. Use one unique_ptr in
the caller's isolated implementation unit. Mesh and timer stay borrowed. Propagate
exceptions after automatic evaluator cleanup; do not add metadata rollback or retry.

Preserve the strict minor_degree_ update, unchanged minor_error_, inclusive stopping
comparison and existing serial/OpenMP dispatch. The area caller's degree loop and
temporary mesh/sample/patch roots are a separate work item. This is a resource
lifetime defect repair, not scientific authorization to change selection policy.

Required strict lint also exposes 63 inherited declarations. Add only the reviewed
override specifiers and make the OpenMP header conditional on the actual configured
mode. Neither changes function bodies or serial numerical policy. The failures,
bounded compiler/instrument coverage and remaining limits stay in the audit.
