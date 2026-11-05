# Single post-scratch MSVC reuse observation

Disposition: fixed Eistute reuse gate remains blocked by timeout. This separate
observation uses the qualified artifact from revision
1636547f501ed5dd675d3d9f93a1fa9686a5f4f2. No production, test, compiler option,
binary/PDB, input/configuration, assertion hook or scientific policy changes.

Native executable: build/finduv-array-scratch/msvc-probe/Debug/serial_reuse_probe.exe.
Its SHA-256 is 776bd80051ca44707ddeccb5ffd7b5eb341a006eb6a3c80f9da6600038f4a11d.
The original captured configuration remains
635fc49c6c9275ee64464f86443c66bc059bc5663a61292d5e3224440bdb213d.
The qualified source, executable/PDB, model, configuration and preceding delivery
identities are checked before the single launch and again after completion.
Unchanged regression evidence is retained by identity; no extra runtime test or
generation campaign accompanies this observation.

Exact commands, complete hashes and restoration manifests:
build/finduv-scratch-reuse/.

```text
python build/finduv-scratch-reuse/measure_once.py
python build/finduv-scratch-reuse/check_measurement.py
```

The original two-call native command runs once under one total 300-second cap.
The deadline is reached at 300.013471 s; termination completes at 300.017267 s.
The first call completes with five independently checked states, 25 prior-version
scientific artifacts exact and 15 positive boundary comparisons. Accepted 0/1 and
rejected 2/3/4 agree. The second call remains incomplete, with partial accepted
0/1 and rejected 2/3 records. Buffered outer return markers were not flushed;
no two-call archive/FindUV/return equality is claimed. The preceding live output
was restored byte for byte and every previous positive/negative record remains.

First-call diagnostic totals: full generation 175.317 s, reconstruction
100.452 s, combined analytical/discrete curvature 50.7879 s, curve update
23.6267 s, error accumulation 0.025731 s and output 3.41027 s. These are phase
totals, not separately measured call wall times, a function-level profile or a
paired speedup/regression benchmark. The source-preserving array scratch remains
a bounded standard-storage delivery; sufficient total timing improvement has
not been demonstrated.

Stop at this timeout: no retry, Book run, new input, enlarged cap, new profiling
or further implementation follows this observation. Remaining timed reuse,
revised-head Book, exact-delivery/main and Stage 3 obligations block integration.
The PR stays a draft. Next production selection needs function-level attribution
within the remaining reconstruction/curvature work; the phase totals and sparse
historical stacks do not select another implementation on their own.
