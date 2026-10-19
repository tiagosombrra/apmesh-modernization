# ADR-0023: retire physical elements before replacing their node owners

Status: candidate measured; exact-head/main integration gates pending.

SubMesh normal destruction releases elements before nodes, but defaulted move
assignment destroys destination nodes before elements. A counted actual triangle
subclass that reads borrowed nodes in its destructor reproduces ASan UAF. The
current production triangle destructor is empty; this is an owner-order defect
and prerequisite to evaluating safe automatic observer removal.

Use explicit noexcept move assignment: guard self-address, clear old elements,
move node owners, move element owners, copy the incoming patch observer value.
Preserve object addresses, order/null slots and the moved-from patch value.
Moving does not rebind foreign Patch observers. Require local node ownership or
independently live external nodes and nonthrowing element/node destructors.
Incoming elements borrowing destination-owned nodes violate this contract.

Classification: behavior-changing engineering lifetime defect repair. No formulas,
numerical evaluation order or adaptation/acceptance/stopping policies change.
Twenty-eight actual-unit outcomes cover ordering, analytic/identity/adjacency,
zero allocation attempts and deliberate memory/hook controls. Ordinary triangle
deregistration, copy/move/ReplaceNode and whole-process qualification remain open.
See [evidence and closure audit](../evidence/STAGE3_SUBMESH_LIFETIME.md).
