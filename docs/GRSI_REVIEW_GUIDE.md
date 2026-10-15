# GRSI reviewer guide

## Scope

The representative result selected for the Graphics Replicability Stamp
Initiative review is **Figure 7**, Section 4.3, “Eistute model”.

The paper figure presents five saved states numbered 0–4. In the configuration
files, `ADAPTIVE_MAX_STEPS` denotes the highest saved stage index. The Eistute
configuration therefore uses the value `4`.

The representative object is the saved stage-4 candidate mesh used in Figure 7.
The implementation intentionally saves rejected candidates for analysis; the
stage-4 OBJ is verified against the archived paper target independently of the
hybrid transition-acceptance decision.

## Primary review platform

- Windows 10/11, 64-bit;
- MSYS2 UCRT64;
- GCC/MinGW-w64;
- CMake;
- Python 3.

The MinGW compiler runtime is linked statically to avoid accidental use of an
incompatible GCC runtime from another Windows toolchain.

Complete clean-machine instructions are in `INSTALL_WINDOWS.txt`.

## One-command reproduction

From the repository root in PowerShell:

```powershell
.\reproduce_eistute_windows.bat
```

When using the MSYS2 UCRT64 terminal or Git Bash:

```bash
cmd.exe //c reproduce_eistute_windows.bat
```

No parameters are required.

## Expected outputs

The run creates:

```text
results/eistute/
```

The representative mesh name ends with:

```text
passo_4_malha_4.obj
```

The OBJ is a standard text triangular mesh. The verifier requires:

- configured final stage: 4;
- no stage greater than 4;
- final mesh contains triangular faces;
- final triangle count: 7,184.

The run log is written to:

```text
results/eistute/run.log
```

The log may report `FindUV` calls that reached the configured iteration limit.
That counter is a numerical diagnostic and is not part of the GRSI
triangle-count acceptance test.

Legacy internal timing fields are also diagnostic. They are not reproducibility
targets; use an external wall-clock measurement when timing is required.

## Archived evidence

The repository includes:

- `reference/eistute_stage4.obj`;
- `reference/eistute_metrics.csv`;
- `reference/eistute_stage4.json`.

Run:

```powershell
python scripts\verify_reference.py
```

to check consistency among the archived files.

## Additional models

Book and Decor Shelf execution scripts are included, but they are not required
for the representative GRSI review. Their current verifiers check output
structure rather than archived numerical targets.

## Integrity

Before submission, the authors regenerate `MANIFEST.sha256`. Reviewers may
validate it with `sha256sum -c MANIFEST.sha256` in Git Bash or MSYS2.
