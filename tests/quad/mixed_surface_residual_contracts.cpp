#include "mixed_surface_residual.h"

#include <array>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

using apmesh::quad::research::MeasureMixedSurfaceResidual;
using apmesh::quad::research::ResidualFace;
using apmesh::quad::research::ResidualPoint3;
using apmesh::quad::research::ResidualUv;

namespace {
void Require(bool ok, const char* message) {
  if (!ok)
    throw std::runtime_error(message);
}
ResidualPoint3 Curved(const ResidualUv& uv) {
  return {uv[0], uv[1], uv[0]*uv[0] + uv[1]*uv[1]};
}
ResidualPoint3 Planar(const ResidualUv& uv) {
  return {uv[0], uv[1], 0.0};
}
}  // namespace

int main() {
  const std::vector<ResidualUv> uv{{0,0}, {0.5,0}, {0.5,1},
                                   {0,1}, {1,0}, {1,1}};
  std::vector<ResidualPoint3> physical;
  for (const auto& point : uv)
    physical.push_back(Curved(point));
  const std::vector<ResidualFace> faces{{0,1,2,3}, {1,4,2}};
  const auto observed = MeasureMixedSurfaceResidual(uv, physical, faces, Curved);
  Require(observed.quadrilaterals == 1 && observed.triangles == 1 &&
              observed.samples == 9 && observed.face_maximum.size() == 2 &&
              observed.maximum > 0.0 && observed.rms > 0.0 &&
              observed.quad_maximum > 0.0 && observed.triangle_maximum > 0.0 &&
              observed.worst_quad_face == 0 && observed.worst_triangle_face == 1 &&
              observed.worst_triangle_sample_uv[0] > 0.0 &&
              observed.worst_triangle_sample_uv[1] > 0.0 &&
              observed.worst_quad_sample_uv[0] > 0.0 &&
              observed.worst_quad_sample_uv[1] > 0.0,
          "Curved QUAD/TRI physical source oracle was not measured");

  // A planar source must not invent curvature or an arbitrary zero-score UV.
  auto flat = physical;
  for (auto& p : flat)
    p[2] = 0.0;
  const auto zero = MeasureMixedSurfaceResidual(uv, flat, faces, Planar);
  Require(zero.maximum == 0.0 && zero.rms == 0.0 &&
              zero.quad_maximum == 0.0 && zero.triangle_maximum == 0.0 &&
              zero.worst_quad_face == 0 && zero.worst_triangle_face == 1 &&
              zero.worst_quad_sample_uv[0] == 0.25 &&
              zero.worst_quad_sample_uv[1] == 0.5,
          "Deterministic planar QUAD residual tie handling is broken");

  unsigned negative = 0;
  const auto reject = [&](const std::vector<ResidualUv>& coords,
                          const std::vector<ResidualPoint3>& values,
                          const std::vector<ResidualFace>& polygons,
                          const apmesh::quad::research::ResidualSurface& source) {
    try {
      (void)MeasureMixedSurfaceResidual(coords, values, polygons, source);
    } catch (const std::invalid_argument&) {
      ++negative;
    }
  };
  reject({}, physical, faces, Curved);
  reject(uv, {}, faces, Curved);
  reject(uv, physical, {}, Curved);
  reject(uv, physical, {{0,1,2,3}, {1,4,4}}, Curved);
  reject(uv, physical, {{0,1,2,99}, {1,4,2}}, Curved);
  reject(uv, physical, {{0,1,2,3}, {1,4,2,5,0}}, Curved);
  reject(uv, physical, {{1,4,2}}, Curved);
  reject(uv, physical, {{0,1,2,3}}, Curved);
  reject(uv, physical, faces, {});
  auto bad_uv = uv;
  bad_uv[0][0] = -0.1;
  reject(bad_uv, physical, faces, Curved);
  bad_uv = uv;
  bad_uv[2][1] = std::numeric_limits<double>::quiet_NaN();
  reject(bad_uv, physical, faces, Curved);
  auto bad_xyz = physical;
  bad_xyz[1][2] = std::numeric_limits<double>::infinity();
  reject(uv, bad_xyz, faces, Curved);
  reject(uv, physical, faces, [](const ResidualUv&) -> ResidualPoint3 {
    return {0.0, 0.0, std::numeric_limits<double>::quiet_NaN()};
  });
  reject(uv, physical, faces, [](const ResidualUv&) -> ResidualPoint3 {
    return {1.0e308, -1.0e308, 0.0};
  });
  Require(negative == 14, "Malformed mixed residual source accepted unexpectedly");
  const auto again = MeasureMixedSurfaceResidual(uv, physical, faces, Curved);
  Require(again.maximum == observed.maximum && again.rms == observed.rms &&
              again.worst_quad_face == observed.worst_quad_face,
          "Physical residual selection is not deterministic");
  std::cout << "QUAD_SURFACE_RESIDUAL native_real_metric=1"
               " negative_cases=14 deterministic=1 actual_adaptive_epochs=0\n";
}
