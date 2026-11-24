# S40-F19B — Cross-stage receipt handoff (unadmitted reference)

**Date:** 2026-11-22. **Research branch:** `research/benchmark-corpus-reverse-patches`, PR #225 DRAFT. No main merge or release.

## Scientific scope

The existing F17 stage pins the original STL SHA-256 and source ZIP Git blob; F19 extracts one OBJ/NPZ from the authors' remote ZIP if HTTP Range is supported; F18 inspects the topology of a locally available QUAD reference output. These are **different gates**. Passing each separately does **not** automatically prove that their evidence belongs to the same input/output pair.

`probes/thingi10k_f19b_reference_handoff.py` adds a local, read-only, standard-library cross-check:

1. Match the exact ID across the frozen **23-source** F17 register and the original **12-QuadWild-case** literature register. Require a raw-audited STL with frozen SHA-256 and ZIP Git object.
2. Require an **actual one-member extraction** F19 receipt, not an index-only result; reject another archive URL, another numeric ID, ambiguous ZIP entry, or traversal path.
3. Independently re-hash the selected output file, verify its byte count and canonical local path against F19, and require the same digest and original STL hash in the F18 receipt.
4. Cross-check the F18 result's published vertex/face parity and topology screening flags against the literature roster and recorded combinatorial properties. Count mismatch is not reclassified as success.
5. Never infer original author source/output lineage, rights, exact preprocessing, paper metric equivalence, or an accepted APMesh TRI/QUAD comparison merely from receipt agreement.

A matching **receipt** is not a cryptographically signed upstream provenance attestation. The F18 topology calculation is **not independently re-executed** by F19B; its output hash and stated invariants are cross-checked. Independent reference admission still needs the actual authored output, license review and direct geometry/method correspondence.

## Local test evidence

On 2026-11-22, `python -m unittest -v test_thingi10k_f19b_reference_handoff` passed **18/18 hermetic synthetic tests**. Negative tests include changed local bytes, wrong source/output ID or hash, index-only receipts, ambiguous or unsafe member names, wrong author URL, substituted F18 output, unaudited source, missing literature case, and false parity/admission flags. No real QuadWild reference mesh was retrieved or inspected in this test round.

## Reproduce only after F19 and F18 have genuine local evidence

Run from `docs/research/nonmanifold-benchmark/probes`:

```bash
python -m unittest -v test_thingi10k_f19b_reference_handoff
python thingi10k_f19b_reference_handoff.py \
  --model-id 58012 \
  --source-manifest ../THINGI10K_F17_PINNED_SOURCES_23.csv \
  --literature-manifest ../THINGI10K_LITERATURE_COHORT.csv \
  --f19-extraction-receipt /private/f19-58012-extraction.json \
  --f18-topology-receipt /private/f18-58012-quad-topology.json \
  --actual-quad /private/authorized-quadwild/58012_REAL_MEMBER.obj \
  --output /private/f19b-58012-handoff.json
```

Paths are illustrative only. Select the actual member name from the genuine ZIP central directory; do not invent it.

## Current block and next gate

This execution environment cannot resolve the authors' external ZIP host. HTTP Range capability, archive member #58012, authentic QUAD output byte hash, source/output correspondence and individual redistribution permission **remain unverified**. F19B does not clear them.

Next: on an authorized networked workstation run the original F19 selective ZIP listing; obtain the exact member if permitted, then run F18 and F19B on local byte-pinned evidence. Independently establish author preprocessing, rights and geometric comparison conditions before matching an accepted APMesh TRI/QUAD mesh. Preserve all prior MAMBO CADs, Book/Eistute/Decor Shelf, Tsh249, 23-case denominator, S40 frozen results and the PR as DRAFT.
