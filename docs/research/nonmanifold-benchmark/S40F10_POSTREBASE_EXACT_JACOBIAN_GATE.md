# S40-F10 — exact signed-Jacobian certification after F9 → S3.Y reindexing

**Checkpoint:** 2026-11-19. **Scope:** research PR #225, separate from production `main`. This change adds a mathematical admission *guard*, not an original CAD admission.

## Risk addressed

S40-F9 independently certified the isolated eight-patch F9 decimal BP. S40-F7 then reuses 26 exact parent **indices** through its eight source EDGE_CURVE interfaces, after permitting positional compatibility up to 1e-8 mm. Reindexing substitutes the S3.Y parent coordinates on inherited sides, so a proof on the isolated F9 controls is **not automatically a proof of regularity for the serialized joined BP**.

## Implemented guard

- New `probes/s40f10_postrebase_exact_certificate.py` reads the **actual serialized 1,743-control, 164-patch joined candidate** with exact decimal `Fraction` values.
- Recomputes the bicubic signed Jacobian in the tensor-product Bernstein basis for joined patch indices **156–163**, with source face normals `#1279/#1386/#3269/#3485` and exact subdivision (up to depth 12).
- A candidate proceeds to the original native CAD gate **only if all eight post-rebase Jacobians are certified strictly positive**; altered orientation, degenerate nets, invalid indices, invalid cardinalities and malformed BP are rejected.
- The receipt records the serialized candidate SHA-256, eight certificates, and explicit `False` flags for untested 156 parent-patch regularities, continuous source-STEP trim/Hausdorff equivalence and TRI/QUAD meshing.
- Existing F9 deterministic reproduction, private-byte digests, S40-F7 identity-based joins and original-native gate remain mandatory. No tolerances are increased. No original CAD or derived private BP is committed.

## Local directed tests

`python -m unittest -v test_s40f10_postrebase_exact_certificate` executed **6/6 PASS** using synthetic, source-independent 164-patch fixtures. Negative tests cover reversal, collapse, missing controls, unsupported BP records and out-of-range vertex indices. Tests intentionally do not claim actual S40 F9→S3.Y integration, production C++ regression or original STEP equivalence.

## Still blocked

The frozen original S40 STEP, S3.Y 156-patch BP and S40-F6/F9 private BPs plus associated manifests were **not jointly available in this execution environment**. Therefore the full `s40f9_native_join_gate.py` has not been run on the actual original S40 and **zero new source faces have been admitted**. S3.Y remains **156 patches / 22 of 43 original faces**.

**Next:** obtain the byte-pinned private inputs in an authorized isolated environment, run the S40-F9 native gate with this F10 post-rebase guard, independently inspect the post-rebase certificate and source-native receipt, and retain the candidate label pending complete CAD and mesh qualification. Keep PR #225 **draft** and do not merge to `main`.
