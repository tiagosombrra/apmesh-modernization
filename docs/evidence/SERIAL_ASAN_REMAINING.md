# Remaining fixed serial ASan production cases

Classification: engineering-only complete-process observations; no production,
fixture, configuration policy or scientific criterion changes. Entry is PR #137
main `00f93c3f3cdbdabaacdead1fa9d9bb9011b3427e`. This work measures the previously
unrun SP-06..08 groups in the fixed serial execution ledger and contributes to
S3-01/08/09 without closing any of those obligations.

## Artifact and execution decision

Reuse the already qualified complete 73-unit C++17 MSVC/ASan RelWithDebInfo
application from build/face-quality-scratch/application/bin/RelWithDebInfo/ap_mesh.exe.
Its SHA-256 is
`c8a33d26d8f9766a7f68a97bcbeb740974ca919c31841cf57e3bbbedd94a1bc5`.
No compilation or instrument recalibration is performed. Verify the previous
integration seal, source/runtime hashes and actual release/expired-access control
evidence before execution. Earlier SP-01..05 observations keep their own measured
artifact identities; this is not a rerun of every case on the new artifact.

Run only the five prescribed launches, sequentially, with ASAN_OPTIONS set to
halt_on_error=1 and the unchanged 300-second cap for each process. Preserve all
configuration bytes except INPUT_MODEL/OUTPUT_PREFIX path relocation. Stop before
another launch at the first unexpected process, ASan, scientific-verification or
repeatability failure. No timeout extension, retry or alternative fixture is used.

The local command is `python build/p3-msvc-asan-remaining/run.py`; the retained
driver invokes the existing repeat_generation.repeat/run_case recipes, observing
each actual subprocess. Its per-repetition verification additionally requires
positive boundary coverage and the ledger's exact accepted/rejected step lists.
SP-08 uses the unchanged synchronization-disabled configuration directly, with
the ledger's process/owner-teardown oracle rather than a synchronized-boundary
qualification claim.

## Results

| Group | Executions and wall seconds | Required result |
| --- | --- | --- |
| SP-06 Eistute | 202.4684; 218.1307 | Both return zero; accepted 0/1, rejected 2/3/4; independent physical/UV/boundary checks; exact repeatability across five mesh states; 30 positive boundary comparisons total. |
| SP-07 Book | 130.0868; 134.9004 | Both return zero; accepted 0/1, rejected 2/3; independent physical/UV/boundary checks; exact repeatability across four mesh states; 216 positive boundary comparisons total. |
| SP-08 Eistute no-sync | 32.5366 | Returns zero through ordinary complete CLI teardown with the existing clone-owner path enabled by ENABLE_SHARED_CURVE_SYNC=0. No synchronized-boundary qualification. |

All five stderr files are empty. Every process completes under its original cap,
with no ASan diagnostic. The two repeatability comparisons retain byte-identical
OBJ files, equal acceptance fields and exact boundary-incidence comparisons.
The observed campaign runs from 2026-11-01 11:36:24 to 11:48:30 Fortaleza. No
unexpected failure occurs and no additional production launch is made.

The [compact record](stage3/serial_asan_remaining/summary.json) binds the native
commands, inputs, configurations, wall times, prior seal and local record hashes.
The local build/p3-msvc-asan-remaining directory retains raw outputs, both repeat
archives, per-process logs, independent verifications and an immutable manifest.
The original SP-05 failures and the successful quality correction stay intact.

## Delivery and limits

Documentation delivery requires unchanged non-documentation/source/raw-input/
application/runtime/prior-evidence identities, replay of all five process records,
positive comparison counts, whitespace, inventory/contracts, staged/remote audits
and the existing 75 CTest entries with 380 nested Python controls on exact head
and merged main. Reuse the prior nine-state GCC scientific regression (45 exact
artifacts, 123 boundary comparisons) by unchanged dependency and report identity;
do not rebuild or repeat the native ASan or article campaigns for documentation.

This completes only the pending natural SP-06..08 MSVC/ASan observations. Fresh
subprocess repetition does not establish same-Generator reuse or reconstruction
after failure. ASan success is not leak accounting or proof of arbitrary observer
safety. SP-09/10 terminal-observer portability and full-caller measurements,
complete-process CRT/LSan/UBSan, parallel coverage and the remaining supported
caller obligations remain open. Stage 3 retains three bounded and seven
partial/open closure rows. The next bounded dependency is a portable full-caller
observer for the existing SP-09/10 cases; do not expand their context inventory.
