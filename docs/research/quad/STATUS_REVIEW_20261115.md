# QUAD advancement review and physical mesh inspection

Date: 2026-11-15 Fortaleza. Classification: engineering/documentation review;
no scientific policy or production source change.

## Verified revision and scope

Canonical `quad-templates` was `392d02c0dc1fd52bcc6cb83320469d1143636ef6`.
The clean primary local checkout was at `3beec583fd4b95717d62716d819dd4cd81b02239`,
162 commits behind. `git fetch origin` and `git merge --ff-only origin/quad-templates`
aligned it without rewriting history or modifying the other worktrees.
Live remote `main` remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
Open PR214 remains a separate draft targeting research; PR225 targets `main`.
Neither was merged during this review.

PR236 feature `f55b8e4aec4c06eb6603f3cf6f6de54d3fdf1f81` was merged at
`8a451eee7fad416d36604a61afd35412c65cd72a`. Live Actions API readback confirms
[exact feature #43704424433](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43704424433)
and [exact research merge #43705007549](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43705007549)
completed successfully with four successful jobs each: Linux native, Windows
native, frozen TRI science and baseline/tooling. Recorded feature evidence
includes 85 CTests, 527 Python tooling controls and Linux ASan/UBSan/leak;
those campaigns were not rerun locally for this review. The diff of `research`,
`tests`, `.github`, `src`, `include` and `CMakeLists.txt` between the exact
feature and reviewed canonical head was empty.

## Bounded findings

1. `ProbePhysicalOwnerTransactionRehearsal` remeasures residuals from the
   already published P1 owner, constructs and clones a genuine native AFT
   successor, tests five pre-adoption faults, temporarily registers the new
   forward/back observers, then restores the old owner. Its restoration guard,
   full prior node/element witness and exact ordered node observers agree with
   the bounded claim. It deliberately retains no accepted successor.
2. `MixedEpochPreflight` remains metadata-only. Neither it nor the physical
   candidate exports implement the durable accepted-state archive and combined
   memory/file publication required for P2d-1c4b. Post-publication fault/recovery
   qualification and an approved selection policy remain gates, not defects
   hidden by the five pre-adoption fault checks.
3. The roadmap introduction still called PR236 a draft with CI pending, while
   its table and GitHub showed integration. The state heading also called its
   rehearsal active. Those current summaries were reconciled; the intermediate
   GCC compilation failure remains recorded. The evidence's historical pending
   statement is explicitly historical rather than a current gate status.
4. Sampled source-error/Pareto diagnostics do not authorize choosing north,
   west or both as a scientific policy. A fixed16 single-chart experiment does
   not establish full production `AdaptCurve`, whole-model high-valence welding,
   original 1993 equivalence, all-QUAD output or anisotropy.

This is a focused code/status/artifact review, not a replacement for the wider
scientific, allocation-denial, sanitizer or milestone closure inventory.

## Exact physical artifacts and local replay

Downloaded artifact
`controlled-quad-windows-2022-f55b8e4aec4c06eb6603f3cf6f6de54d3fdf1f81`
from run #43704424433 with `gh run download`. Parsed the original OBJ face
cycles without triangulating QUADs. All five have 16 singly incident boundary
edges and all edge incidences are one or two; this bounded check alone does
not prove global topology, overlap absence or general scientific validity.

| Original artifact | Nodes | QUAD | AFT TRI | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `accepted.obj` | 69 | 42 | 36 | `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0` |
| `accepted.band-candidate.obj` | 93 | 62 | 44 | `76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6` |
| `accepted.north.second-band-candidate.obj` | 107 | 71 | 54 | `6eb4faedeaab44fbfa3d4cb2ca1ea618a3dca513dc241871c57bcc7eae26d500` |
| `accepted.west.second-band-candidate.obj` | 109 | 75 | 50 | `ca08918f6d71fa672de22a72eb6fef7c106c90c7fd02d40cb19852972b4274ee` |
| `accepted.both.second-band-candidate.obj` | 117 | 82 | 52 | `b77afb530724f38ff81f0f3e7f06fca6c8dc0cb4a15562ce933a4013724bd36c` |

Local helper `python build/quad-review-20261115/inspect_artifacts.py` imported
the existing `tests/quad/test_controlled_application.py` verifiers and replayed
the actual `accepted.stdout` and `rollback.stdout`: both real receipts accepted,
eight forged variants rejected per run, accepted adaptive epochs zero. The
first helper invocation could not import a sibling test module; setting its
local `tests/quad` import path resolved that setup error. This is receipt replay,
not local native execution or a new independent physical-error campaign.

Blender 5.3.0 was opened through its installed Windows application entry.
The five actual OBJ meshes were imported using its Python API, with face
arity/counts and source hashes checked. Original XYZ, UV and face cycles were
preserved; only object translations separate the comparison. QUADs are teal,
AFT triangles amber; no smoothing, subdivision, artificial Z scaling or
remeshing was used. All source Z coordinates remain in [0, 0.09817555546760559].
The visible scene labels all band variants as unaccepted candidates and states
`accepted adaptive epochs: 0`.

Local artifacts, intentionally outside tracked research evidence:
`build/quad-review-20261115/APMesh_QUAD_review.blend`,
`artifact_review.json`, `blender_import_check.json`, original CI files and
the two inspection helpers under the same build directory. The Blender scene
was saved and visually inspected. A screenshot is visualization, not an oracle.

## Next action and closure boundary

Specify P2d-1c4b accepted typed-state ownership/archive, immutable source
fingerprints and the combined memory/file publication failure matrix. Register
the advisor-approved error/quality/complexity policy before counting accepted
transitions; demonstrate two distinct transitions driven by their actual
previous accepted physical states. Keep R3/M7 issue #221 open and
`adaptive_epochs=0` until its required gates pass.

This session changes documentation only. No local native build, CTest,
sanitizer, full historical oracle or new CI campaign was executed. Whitespace
and JSON syntax checks apply to this checkpoint; prior CI qualifies its own
feature/merge revisions rather than this later documentation commit.
