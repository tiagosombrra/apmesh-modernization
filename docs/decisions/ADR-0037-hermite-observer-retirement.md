# ADR-0037: Retire completed Hermite patch observers

Status: accepted for bounded completed-object retirement; exact-head/main qualification complete.

Classification: behavior-changing lifetime defect repair; no scientific change.

The original audit at main 6669a29 records nine actual ASan consumptions of
expired Hermite observers. Completed patch destruction did not unregister itself.
Use the existing CurveAdaptive::RemovePatchObservers operation from the Hermite
destructor for each current nonnull curve. Stable all-match removal preserves
unrelated pointer values and their order without allocating or deleting curves.
Geometry retains its qualified patch-before-curve destruction and move ordering.

Current borrowed curves must remain live through destruction. Empty default and
initialized detached copies have no registrations to retire. Null current slots
are ignored; repeated current slots are harmless. No public signature, layout,
constructor, formula, floating-point order or scientific policy changes.

Construction publication rollback, failed consuming adoption, copied/foreign
observer lists and arbitrary curve replacement require separate work. This
choice provides no complete-process, parallel, LSan or UBSan qualification.
Require the C29 positive/negative instruments, live C++17 original comparisons,
all prior batteries, numerical traces and exact-head/main gates before delivery.
