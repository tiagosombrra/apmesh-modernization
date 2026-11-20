# S40-F11 — Staged, hash-bound original-native candidate delivery

**Date:** 2026-11-19. **Branch:** research/benchmark-corpus-reverse-patches, PR #225 (DRAFT). **Scientific classification:** infrastructure guard; no new CAD faces admitted.

## Discovered operational risk

Previously the F9 command wrote the joined .bp candidate and its JSON receipt as **two separate, non-transactional writes**, and its failure response could be misunderstood if an earlier candidate remained at the same output path. A failure between writes could leave incomplete scientific evidence, and repeated execution could overwrite an earlier run.

## Implemented safety gate

- New Python module: \`probes/s40f11_atomic_candidate_delivery.py\`.
- F9 now rejects preexisting output targets, including dangling symlinks, **before** the expensive private native import. Reusing a destination is an error; choose a fresh per-run path.
- Before emitting, the publisher checks receipt classification, byte-identical SHA-256 binding of the post-rebase F10 certificate to the BP text, eight exact certificates, native sampled-gate status, and explicit non-admission/non-completeness claims.
- The BP and receipt are written to a private temporary sibling directory, read back and verified. Only then is the staging directory renamed to a fresh output directory. If validation or staging fails, no new destination is published and the temporary directory is removed.
- F9 catches output errors in its normal fail-closed branch. It now reports \`new_candidate_emitted_this_run: false\` and \`output_destination_preexisting\` when failing, instead of implying that a previously existing file could not exist.
- Successful stdout calls the result a **candidate** with 164 patches / 26 source faces covered under sampled native checks; \`new_source_faces_homologated: 0\`. Neither this output nor the new gate claims full CAD equivalence or APMesh TRI/QUAD generation.

**Scope note:** same-filesystem rename publishes both artifacts as one directory in normal isolated operation; a malicious concurrent writer racing on the path is outside the path-based exclusion guarantee. The staged publisher is not a replacement for verifying the CAD source or the F10 mathematical proof.

## Tests

The new module was run locally on hermetic synthetic data: **10/10 PASS** for publishing, no overwrite, dangling symlink, hash mismatch, incomplete exact proof, failed native proof, false full-model status, false source-face admission, staged rename failure cleanup and repeat-run rejection.

Previous S40-F10 local exact-Jacobian tests were re-executed: **6/6 PASS**. Three additional isolated F9 CLI entrypoint tests now verify that existing destinations are rejected before calling the private CAD trial, absent private inputs produce no candidate, and a synthetic success is explicitly labelled as a candidate, not a scientifically admitted model. **19/19 directed tests PASS** (10 publisher + 3 CLI + 6 F10) in a single local Python unittest run. The committed F9 CLI and F11 publisher Git blobs match the exact locally checked source bytes. These are distinct from the full historical Python suite, any C++ production regression or a native original S40 run.

## Remaining scientific block

The original private byte-pinned S40 STEP, S3.Y 156-patch BP, F6/F9 BPs and geometric manifests are not together in the present execution environment. The full F9→S3.Y original native candidate has **not been generated** here, so **S3.Y remains 156 patches and 22/43 original faces**. No authenticated original non-manifold-positive model is admitted. Keep PR #225 DRAFT; no merge into main.

## Reproduction

From \`docs/research/nonmanifold-benchmark/probes\`:

\`\`\`bash
python -m unittest -v test_s40f11_native_join_entrypoint test_s40f11_atomic_candidate_delivery test_s40f10_postrebase_exact_certificate
\`\`\`

Run the existing \`s40f9_native_join_gate.py\` with all SHA-pinned private parameters in an isolated environment, specifying an output directory that does **not yet exist**. A complete result is the directory pair \`s40f9_source_joined.ORIGINAL_NATIVE_SAMPLED_CANDIDATE.bp\` and \`s40f9_original_native_reconciliation_receipt.json\`.
