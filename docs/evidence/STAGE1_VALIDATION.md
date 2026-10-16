# Stage 1 draft validation: repairs implemented, integration blocked

Date: 2026-10-16 UTC / 2026-10-15 America/Fortaleza.
Authoritative main before work: `b4087a472015d6898687c0aeff444efb4f1a9524`.
Main source tree: `409e939a6659b9b809ecaa0217d4638d671fc918`.
No concurrent open PRs, unrelated branch changes, remote checks or Actions runs
were present at audit. Existing repositories and the immutable import are unchanged.

## Confirmed repairs

Before modification, missing and empty models, unknown records, short vertices
and short patches all returned code 0 and produced an empty OBJ. The candidate
rejects malformed configuration/CLI/model data with a nonzero result, English
stderr diagnostic and no generated artifacts. All 23 distinct real executable
negative controls pass. The three shipped BP models and six valid configuration
controls are accepted by the validator.

The independent verifier joins every attempted stage's OBJ, acceptance log and
CSV row. It selects the last accepted state and recomputes mesh validity and
quality from exported coordinates. The historical stage-target verifier now
rejects Eistute stage 4 as rejected; 7,184 triangles alone no longer certify it.
Details and exact limitations: GENERATION_VALIDATION_CONTRACT.md.

## Checks executed

- GCC 16.1.0 / MSYS2 UCRT64, native Windows serial Release, C++17; MPI/OpenMP/LTO OFF.
- Build PASS; no meshing formula, ordering, threshold or generator was changed.
- 38 Python tooling/verifier tests PASS.
- 23 real executable invalid-input controls PASS, with no generated artifacts.
- Three valid shipped model grammars and six positive config controls PASS.
- CTest 4/4 PASS: tooling controls, archived Eistute artifact, negative CLI and
  positive grammar controls. This is not a full scientific/memory qualification.
- clang-format on the new header and C++ probe PASS; clang-tidy on the compiled
  probe including the validator header PASS. Legacy full-project debt remains.
- Both article cases independently passed exported mesh/acceptance validation.
- Book strict before/after comparison PASS: 4 OBJ byte-identical, all acceptance
  and CSV fields equal; last accepted stage 1, 4,418 triangles.
- Eistute before/after strict comparison FAIL: 5 OBJ byte-identical and all
  accept/reject decisions preserved, but 43 numerical/derived report fields differ
  in the final candidate (38 in the earlier intermediate candidate).
  Last accepted stage remains 1, 1,168 triangles. Stage 4 remains rejected.
- Eistute unchanged-binary repetition with relocated output FAIL: 43 differing
  numerical/derived fields, same OBJ and accepted/rejected steps.
- A stricter reference-only experiment using identical executable bytes, config
  bytes, command, cwd and fresh identical output prefix also FAILS: 41 differing
  numerical/derived fields. Raw differences and hashes are retained in JSON.

The reusable repeat_generation.py command was also executed directly: Book
strict repetition PASS; Eistute strict repetition FAIL. These additional
experiments retain raw outputs and do not change the failing comparison policy.

ReaderFilePatches now holds its local reader on the stack, so a validation
exception unwinds that object. This bounded lifetime repair accompanies the new
throwing validation path; the pre-existing temporary patch/node ownership audit
and full application sanitizer campaign remain open. Final candidate executable:
`68a9c3464203602d460dbbabe4858fe095ea128e1c5e51bf9b9157e22595e0cb`.

The original baseline executable hash is
`38811329b8e776f1818303e2cdd7b92cbd8e2669f7bfe7129bfeb31a6927a45d`.
Both runs in the fixed-configuration experiment use that hash and the exact
configuration hash recorded in fixed_configuration_comparison.json.
Thus the numerical variation is reproduced without applying the input repair.
This does not identify its root cause or prove the candidate cannot influence
the variation. Identical rounded OBJ files do not prove identical internal
coordinates or curvature calculations. No tolerance or assertion was relaxed.

The first verifier implementation incorrectly assumed CSV nodes were unique OBJ
vertices and that actual_elements_step was populated in stage 0. Source inspection
confirmed incidence counting and an initial zero placeholder. The contract and
controls now distinguish those meanings; triangle counts and subsequent candidate
counts remain strict. These are verifier semantic corrections, not numerical gate
exceptions. No production writer was changed to make the comparison pass.

## Blocking decision

AGENTS.md requires: "merge only after required local gates pass on the exact
head revision". The strict numerical regression is failing, including baseline
self-comparison. Keep the delivery as a draft PR and main unchanged. Diagnose
the numerical repeatability defect before qualifying integration; do not choose
a new tolerance or alter curvature/acceptance policy to obtain a green result.

Per-incidence boundary coverage remains unavailable in legacy exports; the strict
coverage request fails as required. Decor Shelf's earlier timeouts remain open;
this delivery does not rerun the full heavy campaign or claim new coverage there.
Full application memory, Doxygen generation, Eigen replacement, CRABMesh
consolidation, C++23 and performance qualification remain later work.
