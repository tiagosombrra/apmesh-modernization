# Generation aggressiveness sensitivity - 2026-11-15

User-authorized bounded research experiment on existing source e90d5a3. The
stated concern was node/element counts. No production file, default config,
formula, acceptance/stopping rule, point budget or historical reference changed.
This is a sensitivity observation, not scientific approval or an optimal policy.

## Method and scope

A small process-local C++ probe links the existing qualified GNU C++17 Release
serial engine. It loads/applies the versioned original-curvature configuration,
sets the requested curve base factor before the existing context factory, and
calls RunRealBoundaryPatch. The internal domain factor retains its original
value. The native engine library, compiler, probe source/image and inputs are
hashed in the receipt. Compiler flags are inherited from the qualified main
object command; the research include path is supplied explicitly.

Before any treatment, the control reproduces all eight qualified application
OBJ files and the complete curve-stage trace byte-for-byte. An invalid factor0
is rejected before generation; control artifacts remain unchanged. No input or
instrument failure is counted as a successful observation.

The original plan contained a control and one lower base-factor treatment.
That treatment increased counts. A separately recorded neutral target-floor
follow-up stayed on the same exported subdivision. One coarser target was then
preregistered to obtain an actually smaller mesh. Four native cases total;
there was no further parameter sweep and no preferred result was substituted
for the negative observations. Each generation had a180-second cap.

All exported TRI/mixed states receive the existing independent UV/source,
orientation, incidence and disk checks. Four-node quality is independently
recomputed against analytic normals. TRI shape quality uses
`2*sqrt(3)*|AB cross AC|/(|AB|^2+|AC|^2+|BC|^2)`, with1 equilateral and values
near0 indicating degeneration. No new quality acceptance threshold is chosen.
No violated UV bounds/source mapping or uncovered sample sites were observed;
this is not a proof of global physical bounds or curved-boundary exactness.

Geometric RMS uses the previous identical-source64/128 grids and original
Jacobian weighting; percentages normalize by the source corner diagonal sqrt8.
Control/neutral metrics are reused only for byte-identical input files. New
actual mixed-stage/grid values exactly match the unchanged existing mixed
kernel. These are sampled geometric errors, not curvature/solution errors or
continuous bounds. Runtime and peak memory were not benchmarked.

## Parameter outcomes

| Case | Changed input | Step1 mixed nodes / RMS | Step2 mixed nodes / RMS | Step3 mixed nodes / RMS |
| --- | --- | --- | --- | --- |
| Control | Original base1.414213562, external factor floor0.8 | 165 /0.198709% | 953 /0.0218567% | 953 /0.0218567% |
| Lower base factor | Curve base1.10 only; internal domain base unchanged | 185 /0.111694% | 1073 /0.0204581% | 1073 /0.0204581% |
| Neutral external floor | Original base; PATCH_FACTOR_MIN1.0 | 165 /0.198709% | 953 /0.0218567% | 953 /0.0218567% |
| Coarser external target | Original base; PATCH_FACTOR_MIN=PATCH_FACTOR_MAX1.5 | 33 /0.830346% | 615 /0.290323% | 843 /0.267236% |

Lowering the base factor is not a monotone node-count control. It participates
in both refinement and coarsening. For a flat curve interval, target length is
old length times base factor times the external factor. At step1, the original
product is1.414213562*0.8 >1, whereas1.10*0.8=0.88 <1. This can reverse the
intended coarsening into subdivision. Straight-side output grows from5 to9
points at step1 and17 to57 at step2; curved-side counts remain9 then65.
The extra nodes improve RMS, but do not meet the requested count reduction.

The neutral trial was actually consumed: recorded curve factors change from
0.8/0.84 at steps1/2 to1.0. Nevertheless all eight OBJ exports remain identical.
A changed scalar therefore does not guarantee a different discretization.

The coarser case fixes the existing external factor bounds at1.5; both bounds
are changed explicitly, outside the default0.8..1.12 range and without default
adoption. It changes curve and domain requested sizes, not just
the boundary. No post-discretization point trimming is enabled. Curved-side
points grow3 ->5 ->9; straight-side points remain3. The control is9 ->65 ->65
on the curved side and5 ->17 ->17 on each straight side.

## Lower counts did not give a combined improvement

| Step | Node reduction | RMS error multiplier | Control minimum TRI quality | Coarser minimum TRI quality |
| --- | --- | --- | --- | --- |
| 1 | 80.00% | 4.18x worse | 0.418930 | 0.458415 |
| 2 | 35.47% | 13.28x worse | 0.245704 | 0.0398114 |
| 3 | 11.54% | 12.23x worse | 0.245704 | 0.0398114 |

Coarser mixed output counts (nodes/QUAD/TRI) are33/16/24,615/548/122 and
843/772/126. The interior still jumps16 ->548 QUAD and33 ->615 total nodes
between steps1 and2, despite the gentler curved-side progression. Curved-side
sampling alone is therefore not the complete growth control in this flow.
At step2 the QUAD minimum scaled Jacobian falls0.851067 ->0.520605 too.

Considering only nodes and geometric RMS, the coarser steps2/3 are inferior
even to control step1: they use more than165 nodes with RMS above0.198709%.
This is not a full Pareto claim over all quality metrics. The coarser first
step may be useful at a looser error target, but no such target was supplied.
There is no demonstrated optimum from these few observations.

Profile trajectories have different accepted predecessors after decisions
diverge. Same-step totals compare whole trajectories, not isolated responses
to an identical preceding mesh.

The coarser TRI reference accepts all three adapted source steps, unlike the
control's rejected steps2/3. That does not certify mixed reconstruction quality:
its reference metric and mesh differ from the exported mixed layout. Accepted
mixed adaptive epochs remain0; the source workflow is still TRI-driven.

## Disposition, failures and next action

No tested variant is promoted as a default. Preserve the current profile and
all observations. Before choosing a new controller, separate boundary fidelity
from interior size-field damping, and require explicit geometric error, quality
and growth targets on the actual mixed state. Do not restore endpoint-only
point clipping as a shortcut. Advisor/independent approval and existing R3/M7
and integration gates remain necessary.

This experiment was executed in GNU Release only. New-variant MSVC, sanitizers,
full CTest/CI, runtime/memory benchmarks and equal-error-budget optimization were
not run. Prior e90d5a3 qualification is unchanged and does not qualify these new
parameter choices. No merge, stage closure or production policy change occurred.

Retained setup failure: run1 compilation lacked the private research include
path. It stopped before any native case. Only that include path was corrected
for run2; source/parameter changes were not used to hide the failure. Raw
configs, plans, commands, stdout/stderr and source remain under ignored
build/quad-aggressiveness-20261115 and the dedicated native experiment folder.
Copied physical OBJ files and manifests are available in the local exports
subdirectory. Portable input/image hashes and all outcomes are retained in the
[receipt](evidence/AGGRESSIVENESS_SENSITIVITY_20261115.json).

## Probe entry used

The code below is a research-only process entry, not a production API change.
Its raw executed source hash is recorded (including its original file encoding).

```cpp
#include "application/runtime_config.h"
#include "controlled_patch_application.h"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
  try {
    if (argc != 3) throw std::invalid_argument("Expected config and isolated curve factor");
    std::size_t consumed = 0;
    const std::string value(argv[2]);
    const double factor = std::stod(value, &consumed);
    if (consumed != value.size() || !std::isfinite(factor) || factor <= 1.0)
      throw std::invalid_argument("Curve factor must be finite and greater than one");
    const auto config = apmesh::application::LoadRuntimeConfig(argv[1]);
    if (config.num_processes != 1 || config.num_threads != 1 || config.adaptive_mode != "legacy")
      throw std::invalid_argument("Experiment requires the unchanged serial legacy profile");
    apmesh::application::ApplyRuntimeConfig(config);
    // This process-local override precedes the existing context factory. The
    // internal domain factor and every other control retain their initial value.
    DISCRETIZATION_CURVE_FACTOR = factor;
    std::cout << std::setprecision(17) << "CURVE_FACTOR_EXPERIMENT base=" << factor
              << " internal=" << DISCRETIZATION_CURVE_FACTOR_INTERNAL << '\n';
    return apmesh::quad::RunRealBoundaryPatch(config);
  } catch (const std::exception& error) {
    std::cerr << "Curve factor experiment failed: " << error.what() << '\n';
    return 2;
  }
}
```
