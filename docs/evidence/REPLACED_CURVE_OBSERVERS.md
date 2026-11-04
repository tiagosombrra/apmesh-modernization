# Retirement of replaced curve observers

P4 engineering lifecycle repair, starting at main
de588cab99e45cc466e533eb29faa1b3f944ea16 (PR #160).
The public PatchCoons::ReplaceCurve previously assigned a slot without retiring
the old curve's reverse observations. Bezier/Hermite destruction cleans current
curves only, so a replaced curve could retain an expired Patch pointer. Both
families reproduce the failure before repair through the existing native probe:
last-slot retirement and final observer cleanup fail, while guard, destination
and numerical checks pass. No expired object is consumed or original ASan UAF
claimed; the original binaries, source, logs and identities are retained locally.

ReplaceCurve now ignores an invalid position or identical value, assigns the
replacement, then removes every old-curve observer equal to this Patch only when
no current slot still uses that old curve. Repeated incidences therefore retain
their observations until the last slot leaves. Null old values are safe. Removal
uses the existing stable nonallocating operation; other observers, null entries
and their order survive. All borrowed old curves must remain live through the
call. There is no deletion, allocation, new ownership or layout/API change.

Destination publication remains caller-managed. The synchronization path already
publishes each clone's observer before its nonallocating commit; automatic
publication here would duplicate incidences or introduce allocation into that
commit. Its production tokens, order and behavior are unchanged; its comment is
updated to describe retirement. Patch/control-net coefficients, curve types,
orientation flags, boundary synchronization, formulas and adaptive policies are
unchanged. This does not refresh caches or validate arbitrary geometry mutation.

## Finite validation

Two additions to the existing Hermite observer probe exercise Bezier and Hermite
construction and their public replacement setter. Existing flat/repeated-slot
lifetime arrangements and CloneCurveForPatch supply live objects; no model/input
fixture or CTest target is added. Exact observer snapshots test invalid/same/null
values, repeated old slots, removal of duplicates, unrelated/null order,
prepublished destination identity and destruction after replacement. Twelve point/
derivative scalar results remain bitwise identical across replacement. Repeated slots are
lifetime guards, not new scientific-domain qualification.

Require thirteen focused MSVC ASan/Debug CRT outcomes: both replacement families,
both existing synchronization cases, CRT denial of all allocation during each
replacement/destruction sequence, and actual UAF/leak/allocation-hook controls.
Other prior instrument campaigns retain their original identities and scope;
they are not rerun or relabeled as complete-process qualification. The initial
format comparison detected splitting of one new diagnostic string into adjacent
literals. Its contents were independently checked unchanged; the classified
preparation record and final canonical formatting check are retained.

Require the existing exact-head/main GCC/MSVC C++17 builds, 75 CTest entries/389
Python controls and every previous native marker, including PR #160's retirement
oracles. Preserve the frozen nine scientific states, 45 exact artifacts and 123
positive boundary comparisons, accepted/rejected traces and IDs, all three
same-profile FindUV summaries, 23 MSVC invalid CLI controls and one analytic
state/boundary. Source reversal permits only the named replacement body/includes
and synchronization comment; all other production, scientific inputs, contracts'
historical negative controls and build flags retain their entry identities.
Scoped analysis, formatting, whitespace, source inventory/contracts, staged and
remote gates remain mandatory. Commands, revisions, identities and integration
seal are under build/replaced-curve-observers. Stop on first unexpected failure.

This closes obsolete-curve retirement through ReplaceCurve within S3-05/07.
Destination registration, curve-first invalid lifetimes, arbitrary publications,
copied/foreign lists, cache mutation, broader recovery and full-process/parallel
instruments retain their separate limits. Stage 3 remains open.
