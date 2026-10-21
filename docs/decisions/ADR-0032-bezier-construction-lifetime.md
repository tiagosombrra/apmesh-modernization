# ADR 0032: Bezier construction lifetime

Status: accepted for bounded repair; exact-head/main qualification complete.

Keep fresh curves in four local unique owners until the complete sixteen-point
PatchBezier constructor succeeds. Publish raw curve observers in the original
order and release only at successful completion, retaining the existing external
curve-ownership contract. The caller must still adopt those four curves.

Checkpoint borrowed curve observer prefixes before the curve-based constructor
publishes this. Restore exclusively appended suffixes on failed construction;
commit after the original matrix construction finishes. Share the byte-equivalent
scope already used by charge estimation, whose wider evaluation/adoption interval
is retained. No formula, direction, construction order or class layout change.

Require actual constructor allocation denials, preserved prefixes, terminal
cleanup, numerical/control/direction trace pairs and full exact-head/main gates.
Ordinary patch destruction, subsequent caller adoption failures, arbitrary foreign
publications and full-process/parallel qualification remain separate. See
[the construction audit](../evidence/STAGE3_BEZIER_CONSTRUCTION.md).
