#ifndef AP_MESH_TEST_LEGACY_BEZIER_FIND_UV_H
#define AP_MESH_TEST_LEGACY_BEZIER_FIND_UV_H

#include "data/patch/patch_bezier.h"
#include "data/patch/find_uv_statistics.h"
#include <algorithm>
#include <cmath>
#include <iostream>

extern double TOLERANCE;
extern unsigned int I_MAX;

// Frozen Eigen solver from 836df73fb973971b73c021f288a00966aed65e6d.
// Only the receiver binding, inline linkage and comments differ from production.
namespace bezier_find_uv_reference {
constexpr double kFindUvDamping = 0.65;
constexpr double kFindUvParamTol = 1e-5;
constexpr double kFindUvSpatialFactor = 50.0;

inline std::tuple<double, double> FindUV(PatchBezier& patch, const PointAdaptive& point) {
  apmesh::diagnostics::RecordFindUvCall();

  unsigned int iter = 0;

  double u_i = 0.5;
  double v_i = 0.5;

  double delta_u = 0.0;
  double delta_v = 0.0;

  PointAdaptive p_i;
  const double spatial_tol = std::max(1e-12, kFindUvSpatialFactor * std::fabs(TOLERANCE));

  while (true) {
    VectorAdaptive Tu = -(patch.Qu(u_i, v_i));
    VectorAdaptive Tv = -(patch.Qv(u_i, v_i));

    p_i = patch.Parameterize(u_i, v_i);

    Matrix<double, 3, 3> matrix;
    matrix(0, 0) = Tu.GetX();
    matrix(0, 1) = Tv.GetX();
    matrix(0, 2) = p_i.GetX() - point.GetX();
    matrix(1, 0) = Tu.GetY();
    matrix(1, 1) = Tv.GetY();
    matrix(1, 2) = p_i.GetY() - point.GetY();
    matrix(2, 0) = Tu.GetZ();
    matrix(2, 1) = Tv.GetZ();
    matrix(2, 2) = p_i.GetZ() - point.GetZ();

    int k = 0;
    double pivot = matrix(0, 0);

    while ((fabs(pivot) < TOLERANCE) and (k < 2)) {
      ++k;
      pivot = matrix(k, 0);
    }

    matrix.row(k).swap(matrix.row(0));

    if (fabs(pivot) < TOLERANCE) {
      cout << "Erro! Não é possível encontrar as coordenadas paramétricas no "
              "ponto p"
           << point.GetId() << " (" << point.GetX() << ", " << point.GetY() << ", " << point.GetZ()
           << ")" << endl;

      return make_tuple(-1.0, -1.0);
    }

    double A_10 = matrix(1, 0);
    double A_20 = matrix(2, 0);

    for (short j = 0; j < 3; ++j) {
      matrix(0, j) = static_cast<double>(matrix(0, j)) / pivot;
      matrix(1, j) = matrix(1, j) - A_10 * (matrix(0, j));
      matrix(2, j) = matrix(2, j) - A_20 * (matrix(0, j));
    }

    pivot = matrix(1, 1);

    if (fabs(pivot) < TOLERANCE) {
      pivot = matrix(2, 1);
      matrix.row(2).swap(matrix.row(1));
    }

    double A_01 = matrix(0, 1);
    double A_21 = matrix(2, 1);

    for (short j = 0; j < 3; ++j) {
      matrix(1, j) = static_cast<double>(matrix(1, j) / pivot);
      matrix(0, j) = matrix(0, j) - A_01 * (matrix(1, j));
      matrix(2, j) = matrix(2, j) - A_21 * (matrix(1, j));
    }

    delta_u = matrix(0, 2);
    delta_v = matrix(1, 2);

    if (std::isnan(delta_u) || std::isnan(delta_v)) {
      break;
    }

    u_i += kFindUvDamping * delta_u;
    v_i += kFindUvDamping * delta_v;
    u_i = std::clamp(u_i, 0.0, 1.0);
    v_i = std::clamp(v_i, 0.0, 1.0);

    p_i = patch.Parameterize(u_i, v_i);
    const double dist = p_i.CalculateDistance(point);

    const bool param_ok = (fabs(delta_u) < kFindUvParamTol && fabs(delta_v) < kFindUvParamTol);
    if (param_ok || dist < spatial_tol) {
      break;
    }

    ++iter;
    if (iter >= I_MAX) {
      const unsigned long long hit = apmesh::diagnostics::RecordFindUvImaxExit();
#if USE_PRINT_COMENT
      if (hit <= 5ULL || (hit % 2000ULL) == 0ULL) {
        std::cout << "[FindUV Bezier] I_MAX id=" << point.GetId() << " iter=" << iter
                  << " |du|=" << fabs(delta_u) << " |dv|=" << fabs(delta_v) << " u=" << u_i
                  << " v=" << v_i << " dist=" << dist << " spatial_tol=" << spatial_tol
                  << std::endl;
      }
#endif
      break;
    }
  }

  if (u_i <= TOLERANCE)
    u_i = 0.0;
  else if (u_i >= 1.0 - TOLERANCE)
    u_i = 1.0;

  if (v_i <= TOLERANCE)
    v_i = 0.0;
  else if (v_i >= 1.0 - TOLERANCE)
    v_i = 1.0;

  if (std::isnan(u_i) || std::isnan(v_i)) {
    cout << "-nan u_i e v_i" << endl;
  }

  return make_tuple(u_i, v_i);
}
} // namespace bezier_find_uv_reference
#endif
