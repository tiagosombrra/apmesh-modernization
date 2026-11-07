# Shared Bezier control reader

Entry main: `bccd5c1e7af3c058f62085f8fb908f5ccd5db78b` (PR #169), qualified
through its exact-head/main 75 CTest / 479 Python and bounded terminal CRT seal.
Classification: engineering-only implementation consolidation; P4, S3-05,
contracts C23/C27. This is not a cache-mutation repair or scientific proposal.

## Concrete output and invariant

The serial Generator's ReaderFilePatches calls LoaderBezierPatchFile, which
validates input and reconstructs Geometry. ChargeEstimate calls LoaderBPFile and
reconstructs its own patches from control-only owners. Their parser bodies are
identical after removing comments, renaming the filename parameter and accounting
for the existing empty-filename diagnostic. They contain the same 16 ordered
control assignments, IDs, stream masks, owning publication and pending allocation.

Extract one private ReadBezierControlPatches implementation. Preserve both public
signatures and wrapper-specific validation/diagnostics. Retain every parsing
expression, stream/resource failure behavior, allocation/publication order,
by-value point lookup, EOF/failbit interpretation, reconstruction/interner and
curve direction. No new validation, supported-input restriction, parameter/units
change or ownership policy is introduced. Remove duplicate implementation rather
than alter the grammar, numerical work or historical public loaders.

## Finite affected gates

Freeze the current public source and GCC/MSVC probe references before extraction.
An exact expansion audit must reconstruct both original parser bodies and all
unrelated header/reader tokens. Keep the original serial ownership guard and its
six numerical/lifetime negative mutations, applying expansion before its existing
historical comparison; new mutations must reject shared-body, wrapper-validation,
message, API and publication drift. Preserve string literals in the new comparison.

Require original/candidate nonempty control/ID/incidence/scalar/writer traces for
the existing four reader fixtures and two Geometry prefixes. Compare current
allocation counts and complete the existing affected CRT/ASan reader and charge
controls without changing their profiles, caps, assertions or expected negatives.
Stop on the first unexpected failure and preserve raw captures; do not start an
unrelated instrument campaign. Existing profile-specific iterator/CRT limits
remain explicit and do not imply whole-process qualification.

Require canonical GCC/MSVC C++17 builds, full baseline regression on final head
and main, scoped read-only analysis, explicit formatting, contracts/inventory,
staged/remote review and the existing nine-state article reference. Reuse only
identity-bound unaffected evidence; retain all prior failures and ten Stage 3
dispositions. No new scientific model, wider caller qualification or stage closure
is inferred from removing the duplicated parser.

## Candidate implementation and observations

One private ReadBezierControlPatches implementation replaces the duplicate serial
body. Both public signatures, serial validation and distinct empty-name messages
remain. The point lookup still takes its vector by value. Explicit full-file
formatting of the three touched source/header files satisfies the staged-byte
gate; the expansion audit proves every unrelated token and literal unchanged.
No new allocation site, control assignment, data field or virtual operation is
introduced by the helper. Its C++17 prvalue wrapper return adds no result move.

Twenty baseline CRT controls pass, including both caller contracts and actual
allocation hooks. All sixteen serial allocation counts remain equal afterward.
The candidate passes 131 serial and 189 charge ASan/CRT expected outcomes. Sixteen
serial sweeps complete all 2,731 actual denials with live prefixes and zero retained
blocks/bytes. Deliberate UAF/leak detections remain expected negatives, not positive
memory-safety observations. The inherited narrow CRT profile uses static Debug
CRT and iterator level zero; ASan uses RelWithDebInfo and its qualified runtime.
Neither profile substitutes for complete checked-iterator process qualification.
Charge writer-denial controls retain their prior limit: memory and live observers
are measured even when a stream absorbs the denial and produces partial output.
Only the separate positive writer pairs require identical exported bytes.

Current paired traces pass: eight serial scenarios each on GCC, MSVC CRT and
MSVC ASan; 24 charge scenarios each on controlled GCC, actual-numerical GCC,
MSVC CRT and MSVC ASan. These compare positive control coordinates/IDs,
incidence/directions, evaluated scalar bits, stable order and writer bytes.
The fixed trace and memory fixtures are unchanged.

An initial negative-mutation admission matched a diagnostic literal also present
in unrelated legacy loaders. Preserve that tooling failure; the corrected
mutation selects the unique delegate return and retains all eight rejection
checks. The C27 badbit anchor moves with the parser body; immutable plan outputs
receive separate names after changes. No solver or instrument failure is hidden
by these bookkeeping corrections.

Review restores four legacy non-ASCII comment lines after an unintended Windows
decoding conversion during extraction. Their original UTF-8 text, all C++
tokens/literals and the line count are verified independently. The preserved
before/after proof and final runtime-section comparison bind already captured
native/scientific observations to the corrected comments without repeating them.

The full iteration passes 75 CTest / 482 Python without skips/failures; read-only
analysis passes both actual implementation units. Final source/input/executable
identities, article comparisons and delivery/main gates are recorded in the
[compact record](stage3/shared_control_reader/summary.json) and local
build/shared-bezier-control-reader reports. The separate delivery integration
seal is required before this bounded consolidation is closed. All ten Stage 3
dispositions, the negative cache admission, original failures and broader caller/
instrument/parallel obligations remain unchanged.

Both canonical C++17 executables pass Eistute and Book: nine states, 45 exact
scientific artifacts and 123 positive boundary comparisons per ABI. Accepted and
rejected decisions, mesh bytes, exported metrics and relocated compatibility
fields remain identical to their qualified reference. Timing is not a speedup
claim. Only a passed final-head/main integration seal closes this bounded package.
