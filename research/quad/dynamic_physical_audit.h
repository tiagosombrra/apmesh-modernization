#ifndef APMESH_RESEARCH_QUAD_DYNAMIC_PHYSICAL_AUDIT_H
#define APMESH_RESEARCH_QUAD_DYNAMIC_PHYSICAL_AUDIT_H

#include "adapter_capture.h"
#include "data/patch/patch_bezier.h"
#include "data/curve/curve_adaptive_parametric.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <limits>
#include <stdexcept>
#include <vector>

namespace apmesh::quad {

// All inputs are immutable value-only witnesses collected while the actual
// original Adapter and owned research AFT were running. This audit borrows an
// independently loaded original PatchBezier only AFTER production TRI has
// completed, so it cannot change TRI selection, curves, retries or ownership.
using PhysicalTriangleUv = std::array<UvVertex, 3>;
using PhysicalQuadUv = std::array<UvVertex, 4>;
using PhysicalXyz = std::array<double, 3>;

struct DynamicPhysicalAudit {
  std::size_t source_sites_compared = 0;
  std::size_t tri_faces = 0;
  std::size_t quad_faces = 0;
  std::size_t mapped_facets = 0;
  double max_source_xyz_error = 0.0;
  double minimum_jacobian_norm = std::numeric_limits<double>::infinity();
  double minimum_facet_area = std::numeric_limits<double>::infinity();
  double minimum_orientation_alignment = 1.0;
};

inline PhysicalXyz PhysicalValues(const PointAdaptive& value) {
  return {value.GetX(), value.GetY(), value.GetZ()};
}
inline PhysicalXyz PhysicalValues(const VectorAdaptive& value) {
  return {value.GetX(), value.GetY(), value.GetZ()};
}
inline PhysicalXyz PhysicalDifference(const PhysicalXyz& a, const PhysicalXyz& b) {
  return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
}
inline PhysicalXyz PhysicalCross(const PhysicalXyz& a, const PhysicalXyz& b) {
  return {a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]};
}
inline double PhysicalDot(const PhysicalXyz& a, const PhysicalXyz& b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
inline double PhysicalNorm(const PhysicalXyz& a) {
  return std::sqrt(PhysicalDot(a, a));
}
inline bool PhysicalFinite(const PhysicalXyz& xyz) {
  return std::isfinite(xyz[0]) && std::isfinite(xyz[1]) &&
         std::isfinite(xyz[2]);
}
inline void PhysicalRequire(bool condition, const char* failure) {
  if (!condition) throw std::invalid_argument(failure);
}

inline PhysicalXyz EvaluateOriginalBezier(PatchBezier& patch, UvVertex uv) {
  PhysicalRequire(std::isfinite(uv.u) && std::isfinite(uv.v) &&
                      uv.u >= 0.0 && uv.u <= 1.0 &&
                      uv.v >= 0.0 && uv.v <= 1.0,
                  "R2b2 adapted physical candidate contains invalid UV");
  const auto xyz = PhysicalValues(patch.Parameterize(uv.u, uv.v));
  PhysicalRequire(PhysicalFinite(xyz),
                  "R2b2 adapted source PatchBezier XYZ is nonfinite");
  return xyz;
}

inline void AuditOriginalBezierFacet(PatchBezier& patch,
                                     const PhysicalTriangleUv& uv,
                                     DynamicPhysicalAudit& report) {
  const UvVertex center{
      (uv[0].u + uv[1].u + uv[2].u) / 3.0,
      (uv[0].v + uv[1].v + uv[2].v) / 3.0};
  const auto a = EvaluateOriginalBezier(patch, uv[0]);
  const auto b = EvaluateOriginalBezier(patch, uv[1]);
  const auto c = EvaluateOriginalBezier(patch, uv[2]);
  const auto du = PhysicalValues(patch.Qu(center.u, center.v));
  const auto dv = PhysicalValues(patch.Qv(center.u, center.v));
  const auto normal = PhysicalCross(du, dv);
  const auto facet = PhysicalCross(PhysicalDifference(b, a),
                                   PhysicalDifference(c, a));
  const double jacobian = PhysicalNorm(normal);
  const double area = PhysicalNorm(facet) / 2.0;
  const double denom = jacobian * (2.0 * area);
  PhysicalRequire(PhysicalFinite(du) && PhysicalFinite(dv) &&
                      std::isfinite(denom) && denom > 1e-14 &&
                      jacobian > 1e-12 && area > 0.0,
                  "R2b2 adapted source has degenerate physical facet/Jacobian");
  const double alignment = PhysicalDot(normal, facet) / denom;
  PhysicalRequire(std::isfinite(alignment) && alignment > 0.0,
                  "R2b2 adapted source TRI/QUAD physical facet is inverted");
  report.minimum_jacobian_norm = std::min(report.minimum_jacobian_norm, jacobian);
  report.minimum_facet_area = std::min(report.minimum_facet_area, area);
  report.minimum_orientation_alignment =
      std::min(report.minimum_orientation_alignment, alignment);
  ++report.mapped_facets;
}

// Verify EXACTLY the dynamically adapted Adapter's sampled physical curve
// nodes, not equally spaced synthetic UV sites. Preserve their side/reversal
// and native node ID provenance while comparing XYZ against an independent
// PatchBezier/CurveAdaptiveParametric constructed from the same input model.
inline DynamicPhysicalAudit AuditActualAdapterPhysicalFaces(
    PatchBezier& patch, const AdapterBoundaryCapture& original,
    const std::vector<PhysicalQuadUv>& quads,
    const std::vector<PhysicalTriangleUv>& triangles) {
  PhysicalRequire(!original.accepted_mesh_published &&
                      !original.vertices.empty() &&
                      !quads.empty() && !triangles.empty(),
                  "R2b2 dynamic physical audit requires an admitted bounded source");
  DynamicPhysicalAudit report;
  for (const auto& site : original.vertices) {
    PhysicalRequire(site.side < 4U && site.physical_node_id > 0 &&
                        site.aft_vertex_id > 0 &&
                        site.curve_reversed == patch.IsCurveReversed(site.side) &&
                        site.original_parameter >= 0.0 &&
                        site.original_parameter <= 1.0,
                    "R2b2 source adapted curve provenance/reversal has changed");
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
        patch.GetCurve(site.side));
    PhysicalRequire(curve != nullptr,
                    "R2b2 source physical PatchBezier curve type changed");
    const auto on_patch = EvaluateOriginalBezier(patch, site.uv);
    const auto on_curve = PhysicalValues(
        curve->FindPointByParameter(site.original_parameter));
    PhysicalRequire(PhysicalFinite(on_curve) &&
                        PhysicalFinite(site.physical_xyz),
                    "R2b2 adapted source curve XYZ is nonfinite");
    const double scale = std::max(1.0, PhysicalNorm(on_patch));
    const double patch_error =
        PhysicalNorm(PhysicalDifference(on_patch, site.physical_xyz));
    const double curve_error =
        PhysicalNorm(PhysicalDifference(on_curve, site.physical_xyz));
    PhysicalRequire(std::isfinite(patch_error) &&
                        std::isfinite(curve_error) &&
                        patch_error <= 2e-7 * scale &&
                        curve_error <= 2e-7 * scale,
                    "R2b2 original adapted physical curve nodes do not match PatchBezier");
    report.max_source_xyz_error = std::max(
        report.max_source_xyz_error, std::max(patch_error, curve_error));
    ++report.source_sites_compared;
  }
  for (const auto& q : quads) {
    AuditOriginalBezierFacet(patch, {q[0], q[1], q[2]}, report);
    AuditOriginalBezierFacet(patch, {q[0], q[2], q[3]}, report);
    ++report.quad_faces;
  }
  for (const auto& t : triangles) {
    AuditOriginalBezierFacet(patch, t, report);
    ++report.tri_faces;
  }
  PhysicalRequire(report.source_sites_compared == original.vertices.size() &&
                      report.quad_faces == quads.size() &&
                      report.tri_faces == triangles.size() &&
                      report.mapped_facets == triangles.size() + 2 * quads.size() &&
                      std::isfinite(report.minimum_orientation_alignment) &&
                      report.minimum_orientation_alignment > 0.0,
                  "R2b2 dynamic physical audit did not inspect every original face");
  return report;
}

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_DYNAMIC_PHYSICAL_AUDIT_H
