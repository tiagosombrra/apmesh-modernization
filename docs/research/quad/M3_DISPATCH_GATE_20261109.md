# M3-1 — fail-closed application mesh-kind dispatch

**Status:** proposed candidate pending native CI and independent review; not QUAD production emission.

The legacy `input_validation.h` remains byte-for-byte unchanged. The new mesh-kind grammar is isolated in the application configuration reader and a pure helper in `runtime_config.h`, preserving the existing serial-reader preservation contract. The optional `MESH_ELEMENT_KIND=tri` config setting retains the existing TRI path by default. Explicit `MESH_ELEMENT_KIND=quad_uv` is parsed separately from `USE_TEMPLATE=y/n` but rejected **before** `ApplyRuntimeConfig`, TRI global changes or article output: the research bridge has no approved numerical point-selection policy. Unknown/empty mode values and duplicate config keys are refused.

New standalone `quad.mesh_mode.contracts` exercises 11 positive/negative grammar cases in Linux GCC and Windows MSVC. An additional baseline CI step invokes the real `ap_mesh --config` executable for seven explicit rejection cases, including both historical template settings. The original 75 CTest/527 Python and strict frozen Eistute/Book equivalence remain mandatory. CI scientific source guard allows only four new dispatch/parser changes under `src/` and `include/`, and refuses any other change to production sources/configs.

**Limits:** no production call to `EmitLeafQuads`; no scientific centroid selected, no complete UV boundary, 3D elements/XYZ, multipatch or repeated adaptation. No QUAD output is claimed. This is only the first safe, testable M3 entry point.

**Next:** inspect exact-head CI and negative controls; then design the read-only Quadtree capture callback/lifecycle in the application, with independently approved point-selection and output scope before actual QUAD emission.
