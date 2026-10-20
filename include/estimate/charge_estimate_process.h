#ifndef ESTIMATE_CHARGE_ESTIMATE_PROCESS_H
#define ESTIMATE_CHARGE_ESTIMATE_PROCESS_H

#include <algorithm>
#include <map>
#include <vector>

#include "../adapter/adapter.h"
#include "../data/curve/curve_adaptive.h"
#include "../data/curve/curve_adaptive_parametric_bezier.h"
#include "../data/geometry.h"
#include "../data/mesh/mesh_adaptive.h"
#include "../data/patch/patch_bezier.h"
#include "../data/point_adaptive.h"
#include "../data/vertex_adaptive.h"
#include "../input_output/patch_reader.h"
#include "../input_output/write_obj_file.h"
#include "../timer/timer.h"

extern double TIME_READ_FILE;
extern double ESTIMATIVE_TOLERANCE;
extern double TRIANGLE_MEDIO;
extern std::string WRITE_MESH;

class ChargeEstimateProcess {
 public:
  ChargeEstimateProcess();
  ~ChargeEstimateProcess();

  std::list<PatchBezier *> ChargeEstimate(Geometry *geometry, Timer *timer);
  std::vector<PointAdaptive> InterpolateControlPointsCurve(
      const PointAdaptive p0, const PointAdaptive p1, const PointAdaptive p2,
      const PointAdaptive p3, const double u, const double v);
  double CalculateKaMedioPatch(PatchBezier *patch, int points);
  double CalculateAreaPatch(PatchBezier *patch, int pointsGaussLegandre);
  double CalculateAreaTriangleMedioRad(PatchBezier *patch);
  // Owns temporary meshes/fresh samples and restores the preceding patch observer.
  // Preserves evaluation order, degree selection and the selected triangle area.
  double CalculateAreaTriangleMedio(PatchBezier *patch, Timer *timer,
                                    int degree);
  // Temporary counting preserves the previous patch observer and borrowed samples.
  long int CalculateNumbersTriangle(PatchBezier *patch, int degree);
  // Transfers sole ownership to the caller; no hidden MeshAdaptive owns the result.
  // Rebind the patch observer before deletion and retain the collective sample owner.
  SubMesh *InitialMeshEstimate(PatchCoons *patch, int degree);
  // The evaluator is privately owned; mesh/timer remain borrowed and may be mutated.
  // Error thresholds and the historical minor_degree_ selection are unchanged.
  bool CalculateErroEstimative(MeshAdaptive *mesh, Timer *timer, int degree);

  double minor_error_;
  int minor_degree_;
  WriteOBJFile write_obj_file_;
  std::vector<double> curvatures_;
};

#endif  // ESTIMATE_CHARGE_ESTIMATE_PROCESS_H
