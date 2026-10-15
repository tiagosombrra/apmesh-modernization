# Reproducibility protocol

The package builds the project in Release mode and provides article
configurations for Book, Eistute and Decor Shelf. All three representative runs
use one process and one thread.

## Stage numbering

Saved meshes are indexed from stage 0. `ADAPTIVE_MAX_STEPS` denotes the highest
saved stage index, not the number of saved states. Consequently:

- `ADAPTIVE_MAX_STEPS=4` produces stages 0, 1, 2, 3 and 4;
- `ADAPTIVE_MAX_STEPS=5` produces stages 0 through 5.

The Eistute Figure 7 target uses stages 0–4 and therefore sets
`ADAPTIVE_MAX_STEPS=4`.

## Saved candidate semantics

The adaptive workflow can reject a candidate transition while retaining the
candidate OBJ for analysis. The representative Eistute target is the saved
stage-4 candidate mesh used in Figure 7. Its presence and archived numerical
properties are verified independently of the hybrid transition-acceptance
decision.

## Validation levels

### Eistute

Eistute has an archived numerical reference. The principal stage-4 target is:

- 7,184 triangles;
- normalized error 0.036712;
- total error reduction 96.3288%;
- 58.6303% of triangles with quality at least 0.60;
- recorded mean shared-curve compatibility error 0.0.

`python scripts/verify_reference.py` checks the archived OBJ and CSV against
the JSON target. After execution, `scripts/verify_eistute.py` checks the
configured final stage and triangle count.

### Book and Decor Shelf

The repository includes their input models and article configurations. Their
current execution verifiers are structural: they require the configured
final-stage OBJ to exist, prohibit stages beyond the configured limit and
require at least one triangular face.

Authoritative numerical reference JSON/CSV/OBJ files for Book and Decor Shelf
are not bundled because no unambiguous archived targets were established
during the audit. They should be added only from verified experimental records.

## Numerical diagnostics

The run log reports how many `FindUV` calls reached the configured iteration
limit. The value depends on the exact run and configuration. It is retained as
a diagnostic and is not used by the GRSI triangle-count verifier.

The implementation also prints legacy internal timing fields. Those values are
not used as paper-reproduction targets. Use an external wall-clock tool when a
runtime measurement is required.

## Windows runtime portability

The Windows build links the MinGW GCC runtime statically. This prevents the
executable from loading an incompatible `libgcc`, `libstdc++` or
`libwinpthread` DLL merely because another Windows toolchain appears earlier in
`PATH`.

The Windows build script deletes the previous CMake build directory before
configuration, preventing reuse of a cache created by another compiler.

## Commands

### Windows

```bat
run_grsi.bat
```

From MSYS2 UCRT64 or Git Bash:

```bash
cmd.exe //c run_grsi.bat
```

### Linux

```bash
./run_grsi.sh
```
