#ifndef APMESH_RESEARCH_QUAD_SHARED_CURVE_BERNSTEIN_AUDIT_H
#define APMESH_RESEARCH_QUAD_SHARED_CURVE_BERNSTEIN_AUDIT_H

#include "bernstein_interval.h"
#include "shared_curve_sector_sweep.h"

#include "data/curve/curve_adaptive_parametric_bezier.h"

#include <array>
#include <cmath>
#include <cstddef>
#include <limits>
#include <map>
#include <string>
#include <vector>

namespace apmesh::quad {

// A local radial ORDER certificate, not a global sheet/volume intersection,
// accepted mesh topology or a nonmanifold edge ownership decision.
struct SharedCurveBernsteinAudit {
  std::size_t high_valence_curves = 0;
  std::size_t adjacent_pairs = 0;
  std::size_t wide_reference_pairs = 0;
  std::size_t ambiguous_reference_pairs = 0;
  std::size_t original_intervals = 0;
  std::size_t pair_intervals_checked = 0;
  std::size_t certified_pair_intervals = 0;
  std::size_t inverted_pair_intervals = 0;
  std::size_t inconclusive_pair_intervals = 0;
  double smallest_positive_lower = std::numeric_limits<double>::infinity();
  bool interval_order_certified = false;
  bool automatic_sheet_pairing_enabled = false;
  std::string reason = "not_evaluated";
};

inline interval::Vector3 IntervalPhysical(const PointAdaptive& point) {
  const auto xyz = PhysicalValues(point);
  return {{interval::Exact(xyz[0]), interval::Exact(xyz[1]),
           interval::Exact(xyz[2])}};
}

inline std::array<interval::Vector3, 3> SourceTangentControls(
    const CurveAdaptiveParametricBezier& curve) {
  const std::array<interval::Vector3, 4> points{
      IntervalPhysical(curve.GetPoint0()), IntervalPhysical(curve.GetPoint1()),
      IntervalPhysical(curve.GetPoint2()), IntervalPhysical(curve.GetPoint3())};
  std::array<interval::Vector3, 3> tangent{};
  for (std::size_t i = 0; i < 3U; ++i)
    tangent[i] = interval::Scale(
        interval::Difference(points[i + 1U], points[i]),
        interval::Exact(3.0));
  return tangent;
}

inline std::array<interval::Bound, 4> CubicWeightsAt(
    double parameter) {
  PhysicalRequire(parameter >= 0.0 && parameter <= 1.0 &&
                      std::isfinite(parameter),
                  "Invalid inward Bezier coordinate");
  const auto t = interval::Exact(parameter);
  const auto s = interval::Sub(interval::Exact(1.0), t);
  return {interval::Mul(interval::Mul(s, s), s),
          interval::Mul(interval::Exact(3.0),
                        interval::Mul(interval::Mul(s, s), t)),
          interval::Mul(interval::Exact(3.0),
                        interval::Mul(interval::Mul(t, t), s)),
          interval::Mul(interval::Mul(t, t), t)};
}

// Read the ORIGINAL bicubic PatchBezier control net in u-major order.
// Its control points, not independently fitted samples, define the exact
// degree-three restriction to an edge-parallel inward parameter line.
inline std::array<std::array<interval::Vector3, 4>, 4>
OriginalBezierNet(const PatchBezier& patch) {
  return {{
      {{IntervalPhysical(patch.GetPt00()), IntervalPhysical(patch.GetPt01()),
        IntervalPhysical(patch.GetPt02()), IntervalPhysical(patch.GetPt03())}},
      {{IntervalPhysical(patch.GetPt10()), IntervalPhysical(patch.GetPt11()),
        IntervalPhysical(patch.GetPt12()), IntervalPhysical(patch.GetPt13())}},
      {{IntervalPhysical(patch.GetPt20()), IntervalPhysical(patch.GetPt21()),
        IntervalPhysical(patch.GetPt22()), IntervalPhysical(patch.GetPt23())}},
      {{IntervalPhysical(patch.GetPt30()), IntervalPhysical(patch.GetPt31()),
        IntervalPhysical(patch.GetPt32()), IntervalPhysical(patch.GetPt33())}}
  }};
}

inline std::array<interval::Vector3, 4> SourceRadialControls(
    const PatchBezier& patch, unsigned side, bool reversed) {
  constexpr double inward = 1.0 / 64.0;
  PhysicalRequire(side < 4U, "Invalid original source Bezier side");
  const auto control = OriginalBezierNet(patch);
  const bool u_edge = side == 0U || side == 2U;
  const bool high = side == 1U || side == 2U;
  const auto weights = CubicWeightsAt(high ? 1.0 - inward : inward);
  std::array<interval::Vector3, 4> displacement{};
  for (std::size_t i = 0; i < 4U; ++i) {
    interval::Vector3 internal{};
    const auto edge = u_edge ? control[i][high ? 3U : 0U]
                             : control[high ? 3U : 0U][i];
    for (std::size_t j = 0; j < 4U; ++j) {
      const auto current = u_edge ? control[i][j] : control[j][i];
      const auto weighted = interval::Scale(current, weights[j]);
      for (std::size_t axis = 0; axis < 3U; ++axis)
        internal.xyz[axis] = interval::Add(
            internal.xyz[axis], weighted.xyz[axis]);
    }
    displacement[i] = interval::Difference(internal, edge);
  }
  if (reversed) std::reverse(displacement.begin(), displacement.end());
  return displacement;
}

inline SharedCurveBernsteinAudit AuditOriginalHighValenceBernsteinIntervals(
    Geometry& geometry, const SharedCurveTopology& topology,
    const std::vector<AdapterBoundaryCapture>& captures,
    const SharedCurveModelAudit& coherence) {
  SharedCurveBernsteinAudit report;
  PhysicalRequire(topology.patches == geometry.GetNumberPatches() &&
                      topology.curves == geometry.GetNumberCurves(),
                  "Source Bezier interval topology mismatch");

  std::map<std::size_t, const AdapterBoundaryCapture*> selected;
  for (const auto& capture : captures)
    if (capture.attempt.outer.epoch == coherence.epoch &&
        capture.attempt.outer.global_retry == coherence.retry &&
        capture.attempt.patch_index >= 0)
      selected.emplace(static_cast<std::size_t>(capture.attempt.patch_index),
                       &capture);

  for (std::size_t c = 0; c < topology.incidence.size(); ++c) {
    const auto& group = topology.incidence[c];
    if (group.size() <= 2U) continue;
    const auto observed = selected.find(group.front().patch);
    if (observed == selected.end()) {
      report.reason = "incomplete_source_epoch";
      return report;
    }
    const auto source = SnapshotSharedCurveSide(
        *observed->second, group.front().side);
    auto* curve = dynamic_cast<CurveAdaptiveParametricBezier*>(
        geometry.GetCurve(static_cast<unsigned>(c)));
    if (curve == nullptr) {
      report.reason = "non_bezier_original_curve";
      return report;
    }
    for (const auto& incidence : group) {
      const auto found = selected.find(incidence.patch);
      if (found == selected.end()) {
        report.reason = "incomplete_source_incidence";
        return report;
      }
      const auto current = SnapshotSharedCurveSide(*found->second, incidence.side);
      if (current.patch != source.patch &&
          !CompareSharedCurveSides(source, current, false, true).matched) {
        report.reason = "original_source_sample_mismatch";
        return report;
      }
    }

    double original_xyz_error = 0.0;
    const auto frame = OriginalSectorFrameAt(
        geometry, group, *curve, 0.5, original_xyz_error);
    const auto tangent = SourceTangentControls(*curve);
    std::map<std::pair<std::size_t, unsigned>,
             std::array<interval::Vector3, 4>> radials;
    for (const auto& incidence : group) {
      auto* patch = dynamic_cast<PatchBezier*>(
          geometry.GetPatch(static_cast<unsigned>(incidence.patch)));
      PhysicalRequire(patch != nullptr &&
                          patch->GetCurve(incidence.side) == curve &&
                          patch->IsCurveReversed(incidence.side) ==
                              incidence.reversed,
                      "Original Bezier interval patch ownership mismatch");
      radials.emplace(std::make_pair(incidence.patch, incidence.side),
                      SourceRadialControls(*patch, incidence.side,
                                           incidence.reversed));
    }

    const auto& sites = source.ordered_by_original_parameter;
    report.original_intervals += sites.size() - 1U;
    for (std::size_t k = 0; k < frame.size(); ++k) {
      const auto& first = frame[k];
      const auto& second = frame[(k + 1U) % frame.size()];
      const double end = k + 1U < frame.size()
          ? second.angle_radians
          : second.angle_radians + 2.0 * 3.14159265358979323846;
      const double gap = end - first.angle_radians;
      constexpr double pi = 3.14159265358979323846;
      // An adjacent sector wider than pi has NEGATIVE signed triple
      // product, not an invalid source fan. Certify the expected sign of
      // every sector; this avoids rejecting a legitimate wide exterior
      // sector in the original Book source.
      const bool ambiguous =
          !(gap > 1e-6 && gap < 2.0 * pi - 1e-6) ||
          std::abs(gap - pi) <= 1e-6;
      const bool wide = gap > pi;
      ++report.adjacent_pairs;
      report.wide_reference_pairs += wide ? 1U : 0U;
      report.ambiguous_reference_pairs += ambiguous ? 1U : 0U;
      if (ambiguous) {
        // No sign choice is defensible at a tangency or antiparallel ray.
        // Account for every original interval as explicitly inconclusive.
        report.pair_intervals_checked += sites.size() - 1U;
        report.inconclusive_pair_intervals += sites.size() - 1U;
        continue;
      }
      auto polynomial = interval::OrientationPolynomial(
          tangent, radials.at({first.patch, first.side}),
                   radials.at({second.patch, second.side}));
      if (wide) {
        for (auto& coefficient : polynomial)
          coefficient = interval::Negate(coefficient);
      }
      for (std::size_t i = 0; i + 1U < sites.size(); ++i) {
        const auto bound = interval::CertifyPositive(
            polynomial, sites[i].t, sites[i + 1U].t);
        ++report.pair_intervals_checked;
        report.certified_pair_intervals += bound.strictly_positive ? 1U : 0U;
        report.inverted_pair_intervals += bound.negative_leaves > 0U ? 1U : 0U;
        report.inconclusive_pair_intervals +=
            (!bound.strictly_positive && bound.negative_leaves == 0U) ? 1U : 0U;
        if (bound.strictly_positive)
          report.smallest_positive_lower = std::min(
              report.smallest_positive_lower, bound.smallest_positive_lower);
      }
    }
    ++report.high_valence_curves;
  }

  report.interval_order_certified =
      report.high_valence_curves == topology.nonmanifold_curves &&
      report.pair_intervals_checked > 0U &&
      report.pair_intervals_checked == report.certified_pair_intervals &&
      report.inverted_pair_intervals == 0U &&
      report.inconclusive_pair_intervals == 0U &&
      report.ambiguous_reference_pairs == 0U;
  report.reason = report.interval_order_certified
      ? "strict_positive_bernstein_bounds" : "unresolved_or_inverted_interval";
  report.automatic_sheet_pairing_enabled = false;
  return report;
}

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_SHARED_CURVE_BERNSTEIN_AUDIT_H
