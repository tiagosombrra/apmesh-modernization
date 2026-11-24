# S40-F19 — Selective original QuadWild output acquisition: tested retrieval gate, actual output pending

**Date:** 2026-11-22. **Research branch:** `research/benchmark-corpus-reverse-patches` / draft PR #225. **Evidence level:** a functioning, synthetic-fixture-tested remote ZIP range extractor, **NOT an original QUAD output experiment**.

## Scientific goal and the source identity that is already established

The first target remains **Thingi10K file ID `58012` (Canopy Test)**. We independently audited its original raw STL in F17:

- Original input STL SHA-256 `2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b`.
- Original input: 9,090 exact-coordinate reconstructed vertices, 27,510 edges, 18,340 triangles; all edges have two face owners, one component, cyclic vertex links, Euler characteristic −80 and genus 41.
- Pietroni et al. (2021), Figure 29 / Table 1, report the output `#V=113799`, `#F=113879`, `#I=7977`, `AD=15.49°`, `ED=12.28%`, `SJ=0.93`. Under a **pure-quad, closed, connected, orientable** assumption, the count-only Euler characteristic is −80 and the hypothetical output genus is 41. It is **not proof of the real output geometry or mesh topology**.

We will not claim actual matching QUAD output, reference quality recomputation, APMesh geometry conversion or accepted TRI/QUAD output until the respective files have been extracted and independently validated.

## External archive discovery (source sites, not downloaded files)

1. The **authors' official website** [quadmesh.cloud](https://www.quadmesh.cloud/) links to a ZIP archive of QuadWild output meshes: [thingi10k-quad-dataset.zip](https://www.quadmesh.cloud/thingi10k-quad-dataset.zip). An HTTP download link was confirmed on the author website; **we have not examined the ZIP central directory, HTTP Range capability, any member names, ZIP checksum or author output SHA-256**. Never fabricate a file name for ID 58012.
2. The Thingi10K/Hugging Face dataset publishes a second archive [Thingi10K_quadwild_npz.tar.gz](https://huggingface.co/datasets/Thingi10K/Thingi10K/blob/aaae0bb650cf464eb6c7d86d5ce39597cb71e106/Thingi10K_quadwild_npz.tar.gz), about 4.4 GB. Its remotely advertised SHA-256 is `79d213585fce31c61f661221266c967b26c5eb446e394d2022280f5a02399011`. **The 4.4 GB payload and its internal member list were not fetched or checked**. A normal solid `.tar.gz` cannot be indexed using ZIP central-directory random access; do not pretend this is a per-file web API.
3. The public QuadWild code [nicopietroni/quadwild](https://github.com/nicopietroni/quadwild) documents `quadrangulation_smooth.obj` (smoothed) and `quadrangulation.obj` (unsmoothed) as potential output suffixes. **Those names describe program outputs, not necessarily paths found in the archives above.** The README warns results from current code can differ from the published paper.

## F19 code and tested scope

`probes/thingi10k_f19_remote_zip_range.py` is a standard-library-only Python 3.10+ selective acquisition helper:

- Accepts an HTTPS ZIP URL and refuses an HTTP 200 whole-body response on an HTTP Range request; requires `206 Partial Content` with strict `Content-Range` and exact requested byte lengths.
- Supports a seekable, bounded cached HTTP byte-range stream, interpreted with Python `zipfile.ZipFile` (including ZIP64). Limits chunk size, request count, total bytes, entry count, decompressed member size, and excessive compression ratios.
- Pins the remote archive's response length/ETag/Last-Modified **for the acquisition session** and rejects source changes during requests. These response metadata **do not substitute for the full archive SHA-256**.
- Lists candidate entries matching file ID `58012` with strict numeric token boundaries, without inventing output paths. If several `.obj`/`.npz` members are matched (e.g. smoothed and unsmoothed), **explicit exact `--member` selection is required**.
- Rejects path traversal and writing to an existing output; extracts at most **one selected local member** into a private directory and records its SHA-256 and ZIP entry checksum, without silently repairing the model.
- Emits an explicitly *unadmitted* JSON receipt: `REMOTE_ZIP_CENTRAL_DIRECTORY_INSPECTED_ONLY` or `ONE_ORIGINAL_OUTPUT_MEMBER_EXTRACTED_NOT_PAIR_VERIFIED`.

`probes/test_thingi10k_f19_remote_zip_range.py` ran **14/14 hermetic tests PASS** on an isolated localhost HTTP server with synthetic ZIP fixtures. The tests cover valid range read and seek, rejected full-body fallback, an ETag mutation, an enforced transfer budget, malformed Content-Range, invalid ZIP, traversal, file ID collisions, ambiguous variants, safe extraction, no-overwrite, excessive compression ratio and an archive containing >4 MiB of incompressible unrelated bytes (less than 1/8 transferred for index-only access).

The runtime running this research cannot resolve external archive hosts from the local Python container; an independent download attempt through the available file acquisition interface also failed. **No HTTP Range compliance or actual output availability has been observed on the real author server**. Thus the stage is an **acquisition capability gate**, not an accomplished extraction.

## How to run against the author ZIP from a network-enabled research workstation

The first command fetches only the central index **if the server supports HTTP Range**. If the origin refuses it, the tool stops without downloading the full dataset.

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_thingi10k_f19_remote_zip_range
python thingi10k_f19_remote_zip_range.py \
  --url https://www.quadmesh.cloud/thingi10k-quad-dataset.zip \
  --model-id 58012 --list-model \
  --receipt /private/f19-58012-index.json
```

**Inspect the actual `candidate_members[].name` values from this output.** Only after selecting a legitimate exact entry and verifying object-specific license/usage permissions, create a private output directory (not the project Git checkout) and run:

```bash
python thingi10k_f19_remote_zip_range.py \
  --url https://www.quadmesh.cloud/thingi10k-quad-dataset.zip \
  --model-id 58012 \
  --member 'PASTE_AN_EXACT_MEMBER_NAME_FROM_THE_INDEX' \
  --output-dir /private/authorized-quadwild \
  --receipt /private/f19-58012-extraction.json
```

If the real origin is non-seekable or 58012 is absent, keep **BLOCKED** and do not substitute a different model or another QuadWild pipeline run for the published output. The Hugging Face archive can be acquired and fully hash-verified independently where 4.4 GB is permitted, then its exact internal NPZ members can be indexed *locally*. Do not automatically download it in the limited environment.

After extracting an actual output and recording its authentic SHA-256, run the pre-existing **F18** checker separately (an OBJ/NPZ member may need schema-specific support):

```bash
python thingi10k_f18_quad_reference_gate.py \
  --published-csv ../THINGI10K_LITERATURE_COHORT.csv \
  --model-id 58012 \
  --actual-quad /private/authorized-quadwild/58012_ACTUAL_EXTRACTED_NAME.obj \
  --expected-quad-sha256 PASTE_REAL_64_CHARACTER_HASH \
  --source-stl-sha256 2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b \
  --output /private/f19-58012-quad-topology.json
```

The **F18 parser's currently supported NPZ arrays are `vertices` and `faces`**; files with other array names must undergo a separately documented, hash-pinned, lossless adapter before any metric is reported. Even after shape counts and incidence pass, the checker deliberately retains `reference_pair_accepted_for_fair_comparison=false` until input-output provenance, author preprocessing, metrics and rights are independently established.

## Admission decision and next independent gates

- **Acquisition program tests:** PASS 14/14; not a reference output mesh validation.
- **Official remote archive Range capability:** NOT OBSERVED.
- **Official ZIP internal member names and ID 58012 membership:** NOT VERIFIED.
- **Individual output SHA-256 or actual OBJ/NPZ QUAD topology:** NOT VERIFIED.
- **Actual source-to-QUAD vertex/face/geometric correspondence and metrics:** NOT VERIFIED.
- **Original/derived permissions:** NOT CLEARED.
- **APMesh STL→Bézier conversion, TRI/QUAD meshing:** NOT RUN.

**Keep PR #225 DRAFT; preserve all four primary original MAMBO CAD models, Book/Eistute/Decor Shelf, Tsh249 and S40 frozen baselines. Do not merge to `main` or distribute third-party geometry.**
