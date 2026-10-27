# Typed serial terminal domain failure

Reference main: `2bb1363429b212be0e21457bd0870ab6e26c163f` (PR #109).
Classification: behavior-changing terminal error propagation/diagnostic repair.
Successful meshing, formulas/order, retries, synchronization, selection and
acceptance/stopping policies remain unchanged. No quality improvement is claimed.

## Bounded implementation

After existing serial attempts fail, Adapter throws DomainGenerationError with
step, patch, outer retry index and the completed attempt's status. The exception
owns its status string by moving it from the attempt, so it outlives local
attempt destruction. Construction from that rvalue is noexcept and adds no
global operator-new allocation. The fixed what() text does not lazily format
context. Runtime exception storage is outside this operator-new observation.
Copying an exception with a string is not claimed allocation-free.

The config CLI catches this exact type before std::exception, formats the prior
single diagnostic and returns EXIT_FAILURE (status 1 in the qualified build).
The library no longer logs that terminal serial diagnostic before throwing.
Unrelated input/configuration failures retain their existing catch/status.
MPI/OpenMP retain the old diagnostic/exit branch and are not newly qualified.
No new retry, accepted-state rollback or resume guarantee is introduced.

This enables the qualified UV/pending-owner cleanup and PR #109's owned forward
observation detachment on the false-result terminal path. Geometry and live
owners unwind in their existing scopes. Normal post-owner observations,
SubMesh-to-Patch back observations, broader loader/curve/SaveMesh failures,
metadata recovery and foreign/unsupported arrangements retain their limits.

## Directed and independent evidence

Nine C++17 type cases cover unknown/early/later contexts and status lengths
0/17/257. They move an existing status, clear the source, verify exact payload,
access what() and rethrow the same live exception object under allocation denial.
A native SubMesh allocation attempted during another exception's unwinding must
actually be denied, independently checking the hook.

Two actual library cases force all AFT attempts false at Book step 2 / patch 0
and Eistute step 2 / patch 1. They catch the typed payload, require the original
one/two attempt counts, zero additional allocation during unwinding, empty curve
lists, detached own observations and no new expired forward observations after
owner teardown. Three CLI cases additionally cover Eistute patch 0, require
status 1, exact context once, absence of generic input/configuration classification
and zero observed global operator-new attempts during unwinding. Their failed
process prefixes are rejected rather than counted as generation validation.
Eight Python checker controls reject incomplete payload coverage, copied identity,
missing hooks, changed counts/cleanup, wrong status/classification/context,
duplicate diagnostics and allocation during unwinding.

The current fixture linked with the exact original Adapter rejects both library
and all three CLI integrations; independent type controls still pass. A real
executable linked with the prior main's generic catch and the repaired Adapter
releases observed owners but returns -1 and loses context. The repaired real CLI
is independently checked by the immutable terminal-audit observer: three cases
return 1, release all observed SubMesh allocations and captured samples, and leave
zero own forward observations before local Geometry destruction. Observations
are GNU serial exact-address/destructor measurements, not whole-process heap
accounting or new ASan/CRT qualification.

Reference preparation first ran without the documented compiler PATH from the
audit directory; that failed invocation/log is retained. The qualified-environment
compile uses distinct logs and passes. Static analysis, including the test
headers, passes without changes to diagnostic configuration. The staged gate
requires explicit full-file formatting of main. Retained checks reverse only
the terminal branch, typed CLI catch and added includes, then compare normalized
tokens with the original. They also compare the functional preformat snapshots:
12,396 Adapter and 4,144 main tokens, normalizing trivia, adjacent literals,
closing-angle spacing and preprocessor continuations. This is not an AST proof;
compilation and numerical regression are independent gates. Original sources,
executables, commands, logs and reports remain in `build/typed-domain-failure/`.

## Exact delivery requirements and next work

Require exact-head/main C++17 builds, 62/62 CTest with zero failures/skips and
148 Python controls; all new type/library/CLI controls, original-exit rejection
and independent real CLI/generic-catch observations; full Adapter/main/fixture
and test-header tidy, source preservation, format, whitespace, inventory and
staged checks. Fresh Eistute/Book must preserve nine accepted/rejected states,
boundaries, physical/UV metrics and 45 scientific artifacts, excluding runtime
fields and independently checking relocated compatibility prefixes. Record
source/revision/tree/input/executable/log identities and remote refs/open PR/checks
in the delivery PR. Initial checks alone do not authorize integration.

Stage 3 remains open; no qualified memory-slice count is incremented. No rollback,
resume, full-process, parallel, LSan/UBSan or new ASan/CRT claim follows. Next
single work: audit independence of original/regenerated structural statistics
during candidate comparison with frozen inputs and current criteria, before any
selection repair/proposal. The reverse-direction experiment remains unapproved
and unexecuted.
