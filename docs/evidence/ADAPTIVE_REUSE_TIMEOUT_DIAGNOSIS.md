# Checked-MSVC Eistute timeout: CPU and stack diagnosis

One diagnostic observation of the existing first-call timeout, starting at
e7359ec59826cb6cbcc3e4f2886867be7ff4cc60 (draft PR #163). Production, tests,
binary, matching PDB, configuration, input, compiler checks and the 300-second
cap are unchanged. The exact original command/configuration paths were retained.
Prior partial output was temporarily archived, then restored byte-for-byte;
new diagnostic output has separate storage. No Book or additional input was run.

The existing SP-05 external observer was adapted only for this command, cap,
module name and six scheduled captures. Its live busy-thread/CPU control passed,
and the target PDB matched and resolved an actual AFT function. CPU was recorded
once per second; primary-thread stacks were captured at 10/60/120/180/240/290 s.
Suspension time counts inside the watchdog deadline. Raw samples, identities,
observer source/build, self-test, restoration manifest and diagnosis are retained
under build/adaptive-reuse-timeout-diagnosis.

| Sample times | Captured production chain |
| --- | --- |
| 10, 60 s | AdaptCurveBySurface -> CurvatureAnalytical -> FindUV -> Parameterize/CalculatePointUV -> Eigen small matrix evaluation |
| 120 s | improveMesh -> laplacianSmoothing -> findAdjacentFaces |
| 180, 240 s | improveMesh -> qualityShapeSmoothing -> findAdjacentFaces |
| 290 s | ErrorGlobal -> CurvatureAnalytical -> FindUV -> Parameterize/CalculatePointUV |

The watchdog terminated the same first call at 300.004 s; observed process wall
time was 300.008 s. Process and primary-thread CPU both reached 295.031 s,
approximately 98.34% of one core. All six stacks were valid; direct suspension
totaled 21.788 ms. The run progressed between phases, with no assertion or blocking
wait observed. It remained incomplete: no successful first return, second-call
comparison or MSVC qualification is claimed. Six scheduled samples are not a
statistical attribution of runtime percentages or proof that no other defect exists.

Source inspection identifies an actionable repeated traversal: findAdjacentFaces
scans every mesh face and constructs a temporary FaceList for each inner vertex.
Both Laplacian and quality-shape smoothing invoke it inside their vertex loops;
the traversal alone is O(V*F) per pass. The third caller in poor-region smoothing
has the same lookup shape. This is source-derived complexity, not a benchmarked
speedup. FindUV/Bezier curvature evaluation is a second observed cost center.

The next production package is a temporary face-to-vertex incidence index during
the topology-stable AFT postprocessing phase. Preserve original mesh face order,
duplicate/repeated-vertex semantics, observer lifetimes, formulas and all update/
acceptance order. This index belongs to the parametric AFT mesh; it is not a
consolidation with physical NodeAdaptive adjacency or a numerical cache. No such
optimization is implemented or qualified by this diagnosis. Measure only the same
case under 300 seconds after a reviewed change; further diagnostic campaigns are
not the queue. The draft remains blocked and main remains unchanged.
