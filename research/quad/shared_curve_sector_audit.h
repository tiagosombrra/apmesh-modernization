#ifndef APMESH_RESEARCH_QUAD_SHARED_CURVE_SECTOR_AUDIT_H
#define APMESH_RESEARCH_QUAD_SHARED_CURVE_SECTOR_AUDIT_H

#include "dynamic_physical_audit.h"
#include "shared_curve_audit.h"

#include "data/curve/curve_adaptive_parametric.h"
#include "data/patch/patch_bezier.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace apmesh::quad {

// An independently evaluated radial ordering witness for a high-valence
// original Bézier curve. Angles DO NOT imply permitted sheet connections.
struct SharedCurveRadialSector {
  std::size_t patch = 0;
  unsigned side = 0;
  double angle_radians = 0.0;
  PhysicalXyz inward_unit{};
};
struct SharedCurveSectorAudit {
  std::size_t high_valence_curves_sampled = 0;
  std::size_t incidences_evaluated = 0;
  std::size_t angular_adjacent_pairs = 0;
  std::size_t radial_coincident_pairs = 0;
  double minimum_cyclic_angle_radians =
      std::numeric_limits<double>::infinity();
  double maximum_curve_xyz_error = 0.0;
  std::vector<std::vector<SharedCurveRadialSector>> sectors;
  bool source_geometry_admitted = false;
  bool automatic_sheet_pairing_enabled = false;
  std::string rejection = "not_evaluated";
};

inline PhysicalXyz ScalePhysical(const PhysicalXyz& x, double scale) {
  return {scale * x[0], scale * x[1], scale * x[2]};
}
inline PhysicalXyz NormalizedPhysical(const PhysicalXyz& x,
                                      const char* invalid_message) {
  const double length = PhysicalNorm(x);
  PhysicalRequire(PhysicalFinite(x) && std::isfinite(length) &&
                      length > 1e-13, invalid_message);
  return ScalePhysical(x, 1.0 / length);
}
inline double CircularMinimumAngle(
    const std::vector<SharedCurveRadialSector>& sectors) {
  PhysicalRequire(sectors.size() >= 2U,
                  "R2b2 radial sector comparison requires two sheets");
  constexpr double pi = 3.14159265358979323846;
  double minimum = 2.0 * pi;
  for (std::size_t i = 0; i < sectors.size(); ++i) {
    const double low = sectors[i].angle_radians;
    const double high = i + 1U < sectors.size()
        ? sectors[i + 1U].angle_radians
        : sectors.front().angle_radians + 2.0 * pi;
    const double gap = high - low;
    PhysicalRequire(std::isfinite(gap) && gap >= -1e-12 &&
                        gap <= 2.0 * pi + 1e-12,
                    "R2b2 radial sector angular order is invalid");
    minimum = std::min(minimum, std::max(0.0, gap));
  }
  return minimum;
}

// Match the true original geometry's shared curve owner and sample parameter
// from ONE original generator epoch. This never borrows a production node or
// rewrites the original curve's orientation, IDs, or patch connectivity.
inline SharedCurveSectorAudit AuditOriginalHighValenceSectors(
    Geometry& geometry,
    const SharedCurveTopology& topology,
    const std::vector<AdapterBoundaryCapture>& captures,
    const SharedCurveModelAudit& coherence) {
  SharedCurveSectorAudit report;
  PhysicalRequire(topology.patches == geometry.GetNumberPatches() &&
                      topology.curves == geometry.GetNumberCurves(),
                  "R2b2 model topology and Bézier owner mismatch");
  // Never mix the first boundary of an earlier local attempt with another
  // global epoch. All sector witnesses share the selected generator epoch.
  std::map<std::size_t, const AdapterBoundaryCapture*> observed;
  for (const auto& capture : captures) {
    if (capture.attempt.outer.epoch != coherence.epoch ||
        capture.attempt.outer.global_retry != coherence.retry ||
        capture.attempt.patch_index < 0) continue;
    observed.emplace(static_cast<std::size_t>(capture.attempt.patch_index),
                     &capture);
  }

  constexpr double pi = 3.14159265358979323846;
  constexpr double inward_step = 1.0 / 64.0;
  for (std::size_t curve_index = 0;
       curve_index < topology.incidence.size(); ++curve_index) {
    const auto& group = topology.incidence[curve_index];
    if (group.size() <= 2U) continue;
    const auto baseline = observed.find(group.front().patch);
    if (baseline == observed.end()) {
      report.rejection = "incomplete_epoch";
      return report;
    }
    const auto side = SnapshotSharedCurveSide(
        *baseline->second, group.front().side);
    const auto& sites = side.ordered_by_original_parameter;
    PhysicalRequire(sites.size() >= 3U,
                    "R2b2 original high-valence curve lacks interior sample");
    const double parameter = sites[sites.size() / 2U].t;
    PhysicalRequire(parameter > 0.0 && parameter < 1.0,
                    "R2b2 high-valence source midpoint parameter is invalid");

    auto* original_curve = dynamic_cast<CurveAdaptiveParametric*>(
        geometry.GetCurve(static_cast<unsigned>(curve_index)));
    PhysicalRequire(original_curve != nullptr,
                    "R2b2 source high-valence curve is not parametric");
    const auto center = PhysicalValues(
        original_curve->FindPointByParameter(parameter));
    const auto axis = NormalizedPhysical(
        PhysicalValues(original_curve->CalculateGradientByParameter(parameter)),
        "R2b2 high-valence curve has no usable physical tangent");

    std::vector<SharedCurveRadialSector> sectors;
    sectors.reserve(group.size());
    PhysicalXyz reference{};
    for (const auto& incidence : group) {
      const auto found = observed.find(incidence.patch);
      if (found == observed.end()) {
        report.rejection = "incomplete_epoch";
        return report;
      }
      const auto current = SnapshotSharedCurveSide(
          *found->second, incidence.side);
      const auto& current_sites = current.ordered_by_original_parameter;
      if (current_sites.size() != sites.size() ||
          current_sites[current_sites.size() / 2U].t != parameter) {
        report.rejection = "unmatched_actual_source_sampling";
        return report;
      }
      auto* patch = dynamic_cast<PatchBezier*>(
          geometry.GetPatch(static_cast<unsigned>(incidence.patch)));
      PhysicalRequire(patch != nullptr &&
                          patch->GetCurve(incidence.side) == original_curve &&
                          patch->IsCurveReversed(incidence.side) ==
                              incidence.reversed,
                      "R2b2 source sheet incidence changed");
      const double local = incidence.reversed
          ? 1.0 - parameter : parameter;
      const UvVertex edge = incidence.side == 0U ? UvVertex{local, 0.0}
          : incidence.side == 1U ? UvVertex{1.0, local}
          : incidence.side == 2U ? UvVertex{local, 1.0}
                                 : UvVertex{0.0, local};
      UvVertex inside = edge;
      switch (incidence.side) {
        case 0: inside.v = inward_step; break;
        case 1: inside.u = 1.0 - inward_step; break;
        case 2: inside.v = 1.0 - inward_step; break;
        case 3: inside.u = inward_step; break;
        default: throw std::invalid_argument("R2b2 invalid side");
      }
      const auto edge_xyz = EvaluateOriginalBezier(*patch, edge);
      const double error = PhysicalNorm(PhysicalDifference(edge_xyz, center));
      const double scale = std::max(1.0, PhysicalNorm(center));
      if (!std::isfinite(error) || error > 2e-7 * scale) {
        report.rejection = "source_patch_curve_xyz";
        return report;
      }
      report.maximum_curve_xyz_error =
          std::max(report.maximum_curve_xyz_error, error);
      auto radial = PhysicalDifference(
          EvaluateOriginalBezier(*patch, inside), edge_xyz);
      radial = PhysicalDifference(radial,
          ScalePhysical(axis, PhysicalDot(radial, axis)));
      radial = NormalizedPhysical(radial,
          "R2b2 high-valence source sheet has degenerate inward radial direction");

      if (sectors.empty()) reference = radial;
      double angle = std::atan2(
          PhysicalDot(PhysicalCross(reference, radial), axis),
          PhysicalDot(reference, radial));
      if (angle < 0.0) angle += 2.0 * pi;
      sectors.push_back(
          {incidence.patch, incidence.side, angle, radial});
    }

    std::sort(sectors.begin(), sectors.end(),
              [](const SharedCurveRadialSector& a,
                 const SharedCurveRadialSector& b) {
                if (a.angle_radians != b.angle_radians)
                  return a.angle_radians < b.angle_radians;
                return a.patch < b.patch;
              });
    const double angle = CircularMinimumAngle(sectors);
    report.minimum_cyclic_angle_radians =
        std::min(report.minimum_cyclic_angle_radians, angle);
    report.angular_adjacent_pairs += sectors.size();
    for (std::size_t i = 0; i < sectors.size(); ++i) {
      const double low = sectors[i].angle_radians;
      const double high = i + 1U < sectors.size()
          ? sectors[i + 1U].angle_radians
          : sectors.front().angle_radians + 2.0 * pi;
      if (high - low <= 1e-6)
        ++report.radial_coincident_pairs;
    }
    report.incidences_evaluated += sectors.size();
    ++report.high_valence_curves_sampled;
    report.sectors.push_back(std::move(sectors));
  }
  report.source_geometry_admitted =
      report.high_valence_curves_sampled == topology.nonmanifold_curves &&
      report.incidences_evaluated > 2U &&
      report.radial_coincident_pairs == 0 &&
      std::isfinite(report.minimum_cyclic_angle_radians) &&
      report.minimum_cyclic_angle_radians > 1e-6;
  report.rejection =
      report.source_geometry_admitted ? "none" : "radial_sectors_ambiguous";
  // Sorting is a geometric observation ONLY. True surface/volume sheet
  // topology requires an explicit independent scientific pairing decision.
  report.automatic_sheet_pairing_enabled = false;
  return report;
}

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_SHARED_CURVE_SECTOR_AUDIT_H
