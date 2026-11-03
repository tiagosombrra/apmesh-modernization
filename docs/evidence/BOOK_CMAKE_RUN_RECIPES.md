# Book CMake run aliases

Engineering workflow repair, based on main
3d3ba4a88e4dd75c2d3c5e33d52ec74d161297cd (PR #155).
The three historical target names now call the admitted --config protocol:

- run_book_v5_fix_balanced
- run_book_v5_fix_conservative
- run_book_v5_fix_strict

All three are explicitly the same alias of configs/book/article.conf. They use
input_models/book_v7a.bp and the existing results/book/book output prefix. They
do not represent three distinct scientific profiles. The shared output means
running multiple aliases repeats the same case in the same destination.
The configuration, input model, C++ implementation, compiler flags, output
formats, formulas and acceptance/stopping/adaptation policies are unchanged.

The old recipes referenced an absent book_v5_fix.bp and passed positional
arguments already rejected by the imported executable. An actual original
invocation and its failure are retained in build/cmake-run-recipes. No missing
model is fabricated, and no unsupported positional numbers are translated.
The alias decision uses the existing, supported Book configuration unchanged.

After configuring/building a serial preset, run one alias, for example:

```sh
cmake --build build/local-serial --target run_book_v5_fix_balanced
```

For the existing MSVC preset:

```sh
cmake --build build/windows-msvc-serial --config Debug --target run_book_v5_fix_balanced
```

Each target depends on ap_mesh and the configuration file, uses the source root
as working directory and VERBATIM command argument escaping. Relative model/output
paths therefore retain the configuration's existing interpretation.

Validation checks all three generated Ninja command graph entries and all twelve MSVC
commands (three aliases, four build configurations), without running three
identical new scientific generations. Exact delivery head and merged main require
the existing 75 CTest entries/385 nested Python controls, whitespace, contracts/
inventory and staged/remote checks. Full unchanged C++/tests/config/input hashes,
compilation database, executable and prior-report identities retain PR #155's
nine scientific states, 45 exact artifacts, 123 positive boundary comparisons,
23 MSVC invalid CLI controls and one analytic state/positive boundary comparison.
No new target is added to CTest, no new C++ compilation/static-analysis or
instrument campaign is needed, and historical failures retain their scope.
Commands, revisions, generated recipe inspections and reuse proofs are recorded
in build/cmake-run-recipes/integration-verification.json. First unexpected gate
or identity failure stops delivery. Stage 3 and full Stage 6 remain open.
