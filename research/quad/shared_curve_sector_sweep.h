#ifndef APMESH_RESEARCH_QUAD_SHARED_CURVE_SECTOR_SWEEP_H
#define APMESH_RESEARCH_QUAD_SHARED_CURVE_SECTOR_SWEEP_H

#include "shared_curve_sector_audit.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <map>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace apmesh::quad {

// Research-only sampled witness. A finite set of original curve parameters
// and interval probes cannot mathematically certify the continuous surface
// fan between samples or authorize a nonmanifold SubMesh welding policy.
struct SharedCurveSectorSweep {
  std::size_t high_valence_curves = 0;
  std::size_t original_curve_intervals = 0;
  std::size_t parameter_samples = 0;
  std::size_t sector_evaluations = 0;
  std::size_t adjacent_sector_pairs = 0;
  std::size_t order_changes = 0;
  std::size_t coincident_sector_pairs = 0;
  std::size_t invalid_source_samples = 0;
  double minimum_cyclic_gap = std::numeric_limits<double>::infinity();
  double maximum_curve_xyz_error = 0.0;
  double maximum_sample_to_sample_sector_rotation = 0.0;
  double parameter_at_minimum_gap = -1.0;
  bool sampled_order_admitted = false;
  bool automatic_sheet_pairing_enabled = false;
  std::string rejection = "not_evaluated";
  std::vector<std::vector<SharedCurveRadialSector>> observed_frames;
};

// Compare the cyclic permutation, not absolute atan2 angles. A rotating
// tangent-plane reference may change the angle zero without changing the fan.
inline std::vector<std::pair<std::size_t, unsigned>> CanonicalSectorCycle(
    const std::vector<SharedCurveRadialSector>& sorted) {
  PhysicalRequire(sorted.size() >= 3U,
                  "R2b2 sector sweep requires a nonmanifold fan");
  using Key = std::pair<std::size_t, unsigned>;
  std::vector<Key> ring;
  for (const auto& sector : sorted)
    ring.emplace_back(sector.patch, sector.side);
  const auto first = std::min_element(ring.begin(), ring.end());
  std::rotate(ring.begin(), first, ring.end());
  for (std::size_t i = 1; i < ring.size(); ++i)
    PhysicalRequire(ring[i] != ring[i - 1U],
                    "R2b2 sector sweep contains duplicate patch incidence");
  return ring;
}

inline bool SameCyclicSectorOrder(
    const std::vector<SharedCurveRadialSector>& earlier,
    const std::vector<SharedCurveRadialSector>& later) {
  return earlier.size() == later.size() &&
         CanonicalSectorCycle(earlier) == CanonicalSectorCycle(later);
}

inline double WrappedSectorAngleDistance(double left, double right) {
  constexpr double pi = 3.14159265358979323846;
  const double difference = std::remainder(right - left, 2.0 * pi);
  PhysicalRequire(std::isfinite(difference),
                  "R2b2 sector sweep has nonfinite angular drift");
  return std::abs(difference);
}

// Deterministic interior probes: every original interior sampled parameter,
// plus quarter, midpoint and three-quarter probes of EACH source interval.
// Endpoints themselves are excluded because the original Bezier fan may have
// an endpoint singularity; source endpoints are still checked for identity.
inline std::vector<double> SourceSectorSweepParameters(
    const SharedCurveSide& source) {
  const auto& nodes = source.ordered_by_original_parameter;
  PhysicalRequire(nodes.size() >= 3U && nodes.front().t == 0.0 &&
                      nodes.back().t == 1.0,
                  "R2b2 sector sweep requires an original sampled curve");
  std::vector<double> parameters;
  for (std::size_t i = 0; i + 1U < nodes.size(); ++i) {
    const double a = nodes[i].t;
    const double b = nodes[i + 1U].t;
    PhysicalRequire(std::isfinite(a) && std::isfinite(b) &&
                        a < b && a >= 0.0 && b <= 1.0,
                    "R2b2 sector source interval is invalid");
    for (double weight : {0.25, 0.5, 0.75})
      parameters.push_back(a + (b - a) * weight);
    if (i + 1U < nodes.size() - 1U)
      parameters.push_back(b);
  }
  std::sort(parameters.begin(), parameters.end());
  for (std::size_t i = 0; i < parameters.size(); ++i)
    PhysicalRequire(std::isfinite(parameters[i]) &&
                        parameters[i] > 0.0 && parameters[i] < 1.0 &&
                        (i == 0 || parameters[i] > parameters[i - 1U]),
                    "R2b2 source sweep has duplicate or endpoint parameters");
  return parameters;
}

// Build an original-geometry radial frame for one true source parameter.
// Physical source correspondence is rechecked at EVERY probe, not just at
// the old central midpoint, and no candidate topology is modified.
inline std::vector<SharedCurveRadialSector> OriginalSectorFrameAt(
    Geometry& geometry, const std::vector<SharedCurveIncidence>& group,
    CurveAdaptiveParametric& owner, double parameter,
    double& maximum_curve_xyz_error) {
  constexpr double pi = 3.14159265358979323846;
  constexpr double inward_step = 1.0 / 64.0;
  const auto center = PhysicalValues(owner.FindPointByParameter(parameter));
  const auto axis = NormalizedPhysical(
      PhysicalValues(owner.CalculateGradientByParameter(parameter)),
      "R2b2 sector sweep source curve tangent is degenerate");
  std::vector<SharedCurveRadialSector> frame;
  frame.reserve(group.size());
  PhysicalXyz reference{};
  for (const auto& incidence : group) {
    auto* patch = dynamic_cast<PatchBezier*>(
        geometry.GetPatch(static_cast<unsigned>(incidence.patch)));
    PhysicalRequire(patch != nullptr &&
                        patch->GetCurve(incidence.side) == &owner &&
                        patch->IsCurveReversed(incidence.side) ==
                            incidence.reversed,
                    "R2b2 sector sweep source patch incidence changed");
    const double local = incidence.reversed ? 1.0 - parameter : parameter;
    const UvVertex edge = incidence.side == 0U ? UvVertex{local, 0.0}
        : incidence.side == 1U ? UvVertex{1.0, local}
        : incidence.side == 2U ? UvVertex{local, 1.0}
                               : UvVertex{0.0, local};
    UvVertex inside = edge;
    switch (incidence.side) {
      case 0U: inside.v = inward_step; break;
      case 1U: inside.u = 1.0 - inward_step; break;
      case 2U: inside.v = 1.0 - inward_step; break;
      case 3U: inside.u = inward_step; break;
      default: throw std::invalid_argument("R2b2 source side invalid");
    }
    const auto edge_xyz = EvaluateOriginalBezier(*patch, edge);
    const double error = PhysicalNorm(PhysicalDifference(edge_xyz, center));
    PhysicalRequire(std::isfinite(error) &&
                        error <= 2e-7 * std::max(1.0, PhysicalNorm(center)),
                    "R2b2 shared physical source curves diverge within interval");
    maximum_curve_xyz_error = std::max(maximum_curve_xyz_error, error);
    auto radial = PhysicalDifference(
        EvaluateOriginalBezier(*patch, inside), edge_xyz);
    radial = PhysicalDifference(radial,
        ScalePhysical(axis, PhysicalDot(radial, axis)));
    radial = NormalizedPhysical(radial,
        "R2b2 source sheet radial direction collapsed");
    if (frame.empty()) reference = radial;
    double angle = std::atan2(
        PhysicalDot(PhysicalCross(reference, radial), axis),
        PhysicalDot(reference, radial));
    if (angle < 0.0) angle += 2.0 * pi;
    frame.push_back({incidence.patch, incidence.side, angle, radial});
  }
  std::sort(frame.begin(), frame.end(),
      [](const SharedCurveRadialSector& a, const SharedCurveRadialSector& b) {
        if (a.angle_radians != b.angle_radians)
          return a.angle_radians < b.angle_radians;
        return std::tie(a.patch, a.side) < std::tie(b.patch, b.side);
      });
  return frame;
}

inline SharedCurveSectorSweep AuditOriginalHighValenceSectorSweep(
    Geometry& geometry, const SharedCurveTopology& topology,
    const std::vector<AdapterBoundaryCapture>& captures,
    const SharedCurveModelAudit& coherence) {
  SharedCurveSectorSweep report;
  PhysicalRequire(topology.patches == geometry.GetNumberPatches() &&
                      topology.curves == geometry.GetNumberCurves(),
                  "R2b2 sweep model topology mismatch");
  std::map<std::size_t, const AdapterBoundaryCapture*> selected;
  for (const auto& capture : captures) {
    if (capture.attempt.outer.epoch == coherence.epoch &&
        capture.attempt.outer.global_retry == coherence.retry &&
        capture.attempt.patch_index >= 0)
      selected.emplace(static_cast<std::size_t>(capture.attempt.patch_index),
                       &capture);
  }
  for (std::size_t curve_id = 0; curve_id < topology.incidence.size(); ++curve_id) {
    const auto& group = topology.incidence[curve_id];
    if (group.size() <= 2U) continue;
    const auto ref = selected.find(group.front().patch);
    if (ref == selected.end()) {
      report.rejection = "missing_source_patch";
      return report;
    }
    const auto source = SnapshotSharedCurveSide(*ref->second,
                                                group.front().side);
    for (const auto& incidence : group) {
      const auto found = selected.find(incidence.patch);
      if (found == selected.end()) {
        report.rejection = "missing_shared_curve_incidence";
        return report;
      }
      const auto current = SnapshotSharedCurveSide(*found->second, incidence.side);
      if (!CompareSharedCurveSides(source, current, false, true).matched &&
          current.patch != source.patch) {
        report.rejection = "shared_original_samples_mismatch";
        ++report.invalid_source_samples;
        return report;
      }
    }
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
        geometry.GetCurve(static_cast<unsigned>(curve_id)));
    PhysicalRequire(curve != nullptr, "R2b2 sweep source curve type changed");
    const auto parameters = SourceSectorSweepParameters(source);
    report.original_curve_intervals +=
        source.ordered_by_original_parameter.size() - 1U;
    std::vector<SharedCurveRadialSector> earlier;
    for (const double parameter : parameters) {
      const auto frame = OriginalSectorFrameAt(
          geometry, group, *curve, parameter, report.maximum_curve_xyz_error);
      const double gap = CircularMinimumAngle(frame);
      if (gap < report.minimum_cyclic_gap) {
        report.minimum_cyclic_gap = gap;
        report.parameter_at_minimum_gap = parameter;
      }
      if (gap <= 1e-6) ++report.coincident_sector_pairs;
      if (!earlier.empty()) {
        if (!SameCyclicSectorOrder(earlier, frame))
          ++report.order_changes;
        for (const auto& current : frame) {
          const auto previous = std::find_if(
              earlier.begin(), earlier.end(),
              [&](const SharedCurveRadialSector& item) {
                return item.patch == current.patch && item.side == current.side;
              });
          PhysicalRequire(previous != earlier.end(),
                          "R2b2 original radial sheet incidence disappeared");
          report.maximum_sample_to_sample_sector_rotation = std::max(
              report.maximum_sample_to_sample_sector_rotation,
              WrappedSectorAngleDistance(previous->angle_radians,
                                         current.angle_radians));
        }
      }
      report.sector_evaluations += frame.size();
      report.adjacent_sector_pairs += frame.size();
      ++report.parameter_samples;
      report.observed_frames.push_back(frame);
      earlier = frame;
    }
    ++report.high_valence_curves;
  }
  report.sampled_order_admitted =
      report.high_valence_curves == topology.nonmanifold_curves &&
      report.parameter_samples > report.high_valence_curves &&
      report.order_changes == 0U &&
      report.coincident_sector_pairs == 0U &&
      report.invalid_source_samples == 0U &&
      std::isfinite(report.minimum_cyclic_gap) &&
      report.minimum_cyclic_gap > 1e-6;
  report.rejection = report.sampled_order_admitted
      ? "none" : "sampled_sector_order_or_separation_unqualified";
  report.automatic_sheet_pairing_enabled = false;
  return report;
}

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_SHARED_CURVE_SECTOR_SWEEP_H
