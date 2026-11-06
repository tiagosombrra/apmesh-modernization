# P4 cache-mutation admission and qualified checkpoint

Engineering-only documentation, starting at main
`b8a0bb905e650715e5846ae6bdcd13aaae9f9205`. This is one bounded admission
question for S3-05/S3-07 and contract C17, not a numerical repair, a new experiment
or qualification of arbitrary public mutation. The [existing P4 sequence](../architecture/REFACTOR_SEQUENCE.md)
and [ten-row closure inventory](../architecture/STAGE3_CLOSURE_INVENTORY.md)
retain their scope, acceptance rules and dispositions.

## Qualified dependencies

PR #164 integrated the [archive diagnostic repair](REUSE_ARCHIVE_DIAGNOSTICS.md)
as main `249492d299ca9192443ccb12bdf55b78e8e88198`. Its local integration seal
records exact-head/main GCC/MSVC compilation, four archive controls per ABI,
the fixed Eistute/Book reuse gates and 246 independent reuse boundaries per ABI
and revision. Original timeout/archive failures remain, and the original sharing
holder remains unattributed. This is bounded diagnostic/reuse qualification,
not general recovery, stable timing or whole-process memory qualification.

PR #165 integrated the local-validation companion at the entry main above.
Final delivery head `da961afe94be7dde1ddc74e2fd95b6c322c49af7` and merged main
pass 75 CTest entries and 441 Python controls without skips. Native build/source
binding, post-build test inventory and interrupted-process cleanup are checked;
three targeted POSIX interruption controls pass separately. The companion
preserves the production/scientific inputs, existing build/presets and original
pre-commit. These results do not discharge the seven partial/open Stage 3 rows.

## Fixed admission question

Do the inspected serial control-setter callers mutate an already published,
fully constructed geometric object and then evaluate its stale coefficient cache
without the required reconstruction? The fixed scope is Bezier patch control
setters, parametric endpoint/tangent setters and the known serial reader/charge
consumers. Source facts answer admission only; they are not native lifetime,
independent recomputation or scientific regression observations.

| Observation | Evidence and limit |
| --- | --- |
| Patch setters assign controls without rebuilding transformed matrices | This is the existing C17 statement in [contracts.json](../architecture/contracts.json), not a newly established serial regression. |
| Direct patch-control member calls occur in two source files | The fixed source scan finds 16 in [control_patch_reader.cpp](../../src/input_output/control_patch_reader.cpp) and 48 in [patch_reader.cpp](../../src/input_output/patch_reader.cpp). Of these, 32 belong to the two qualified control loaders; 32 belong to other raw loader methods outside this admission's qualified caller scope. A textual scan is not a complete indirect/external call graph. |
| LoaderBPFile produces control-only owners | C23 and [charge input ownership](STAGE3_CHARGE_INPUT.md) describe the storage boundary. [ChargeEstimate](../../src/estimate/charge_input_estimate.cpp) consumes its sixteen coordinates and constructs the geometric patch rather than treating the parsed object as initialized geometric state. |
| LoaderBezierPatchFile produces control-only owners | C27 and [serial reader ownership](STAGE3_SERIAL_READER.md) describe this boundary. [ReaderFilePatches](../../src/input_output/patch_reader.cpp) interns controls, constructs/selects four curves, constructs a separate initialized PatchBezier and transfers that pending owner into Geometry. |
| Control assignment is not geometric initialization | C22 expressly excludes default/control-only sources from the initialized geometric-source precondition. [Detached copy qualification](STAGE3_DETACHED_PATCH_COPY.md) does not turn setters into a complete geometry rebuild API. |
| Endpoint/tangent mutation has no direct member-call witness in the fixed source scan | The scan of source member-call syntax finds none for SetPoint0/1/2/3, SetPoint0Point1 or SetVector0/1. This excludes neither indirect nor external callers and does not qualify arbitrary mutation. |

## Admission decision and stop

**No production cache-mutation repair is admitted by this bounded observation.**
The two inspected qualified serial consumers reconstruct geometric objects from
control-only storage. Their use of setters does not supply the post-publication
mutation trigger required by the fixed question. This does not prove that all
public setters or foreign callers are safe, nor does it resolve C17.

Automatically rebuilding matrices in these setters would introduce a new
mutation contract and numerical evaluation behavior without an admitted caller
or oracle. No such change, input-domain restriction or scientific acceptance
decision is made. Preserve every existing formula, expression order, direction,
coefficient/scratch convention and all negative evidence.

The next dependency is one named supported post-publication mutation/rebinding
caller with its owner/observer order, expected cache/registration invariant,
independent recomputation or lifetime oracle and finite affected gate inventory.
The caller must be admitted before implementation. This decision stops the
automatic source-audit successor chain required by the existing P4 rule; it
does not erase the obligation, declare it unsupported, or select another audit.

## Delivery and remaining limits

This package updates the current checkpoint while retaining previous chronology
under explicit historical headings. Production, inputs, numerical references,
contracts, build configuration and all ten closure dispositions remain unchanged.
Exact delivery/main gates are the existing 75 CTest/441 Python inventory,
changed-document whitespace/local links, inventory/contracts and fresh remote
review. No new tests, compiler qualification or scientific campaign is introduced.
Reuse unchanged qualified runtime/instrument evidence by source/input/artifact
identity; do not rerun unrelated long observations for a documentation delta.

Local source/call-site identities, commands and delivery/main results are retained
under `build/p4-cache-mutation-admission/`; the PR identifies the delivered and
merged revisions. Source-only admission and green ordinary regression are not
whole-process CRT/UB/leak, parallel or Stage 3 closure. Doxygen debt remains open.
