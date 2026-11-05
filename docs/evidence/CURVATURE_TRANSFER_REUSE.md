# Single post-transfer MSVC reuse observation

Disposition: fixed Eistute reuse gate remains blocked by timeout. This separate
observation follows the splice package at revision
48c232ac164e858c4d64b382deb54edbedf03766. No production, test, binary, PDB,
configuration, input, compiler option, assertion hook or scientific policy changed.

The checked-MSVC native executable is the qualified artifact under
build/curvature-adjacency-transfer/msvc-probe/Debug/. SHA-256:
6c73afedf438c94a7ed8b2153dd6ad13c2638ec90979710f44a326dec51ac636.
The original captured configuration hash remains
635fc49c6c9275ee64464f86443c66bc059bc5663a61292d5e3224440bdb213d.
Source, executable, PDB, input and prior delivery identities are checked before
the single launch and again after completion. Existing qualified regression is
retained by identity; no additional regression or model campaign is launched.

The unchanged native two-call command runs once with one total 300-second cap.
The wrapper temporarily preserves the previous live output, retains the new
outputs separately and restores the old files byte for byte. Commands and full
identity/manifests are retained in build/curvature-transfer-reuse/:

```text
python build/curvature-transfer-reuse/measure_once.py
python build/curvature-transfer-reuse/check_measurement.py
```

The deadline is reached at 300.001954 s; termination completes at 300.024723 s.
The first call completed with five independently checked states, 25 prior-version
scientific artifacts exact and 15 positive boundary comparisons. Accepted 0/1 and
rejected 2/3/4 agree. The second remains incomplete, with partial acceptance
records for accepted 0/1 and rejected 2/3. Buffered outer return markers were not
flushed, so no two-call archive/FindUV/return equality is claimed.

The first-call diagnostic summary reports full generation 168.724 s, patch
reconstruction 98.1559 s, combined analytical/discrete curvature 50.553 s, curve
update 19.6436 s and output 2.28178 s. These are diagnostic phase totals, not
separately measured call wall times, function-level attribution or a paired
speedup/regression benchmark. The splice package's bounded real allocation
reduction remains valid within its original scope; sufficient end-to-end timing
improvement is not demonstrated.

Stop at this timeout: no retry, Book run, added input, enlarged cap, new sampling
or further implementation follows this observation. Original live output and all
prior positive/negative evidence remain retained. Revised-head timed reuse,
Book, exact-delivery/main and remaining Stage 3 obligations still block
integration. The PR stays a draft; no stage or whole-caller qualification follows.
