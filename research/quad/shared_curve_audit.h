#ifndef APMESH_RESEARCH_QUAD_SHARED_CURVE_AUDIT_H
#define APMESH_RESEARCH_QUAD_SHARED_CURVE_AUDIT_H

#include "adapter_capture.h"
#include "data/curve/curve_adaptive.h"
#include "data/geometry.h"
#include "data/patch/patch_coons.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace apmesh::quad {

// All source samples are copies, and Geometry is only inspected. Curve pointer
// identity is used exclusively INSIDE one separately owned PatchReader model
// to reconstruct its graph: IDs alone are not guaranteed globally unique.
struct SharedCurveIncidence {
  std::size_t patch = 0;
  unsigned side = 0;
  bool reversed = false;
  unsigned long curve_id = 0;
};
struct SharedCurveTopology {
  std::size_t patches = 0;
  std::size_t curves = 0;
  std::size_t shared_curves = 0;
  std::size_t exterior_curves = 0;
  std::size_t nonmanifold_curves = 0;
  std::vector<std::vector<SharedCurveIncidence>> incidence;
};

inline SharedCurveTopology BuildSharedCurveTopology(const Geometry& geometry) {
  SharedCurveTopology result;
  result.patches = geometry.GetNumberPatches();
  result.curves = geometry.GetNumberCurves();
  if (result.patches == 0 || result.curves == 0)
    throw std::invalid_argument("R2b2 external model has no patches/curves");
  std::map<const CurveAdaptive*, std::size_t> indices;
  for (std::size_t i = 0; i < result.curves; ++i) {
    auto* curve = geometry.GetCurve(static_cast<unsigned>(i));
    if (!curve || !indices.emplace(curve, i).second)
      throw std::invalid_argument("R2b2 external model has duplicate/null curve owners");
  }
  result.incidence.resize(result.curves);
  for (std::size_t patch = 0; patch < result.patches; ++patch) {
    const auto* source = dynamic_cast<const PatchCoons*>(
        geometry.GetPatch(static_cast<unsigned>(patch)));
    if (!source || source->GetNumBerCurves() != 4U)
      throw std::invalid_argument("R2b2 external model has invalid four-sided patch");
    for (unsigned side = 0; side < 4U; ++side) {
      const auto* curve = source->GetCurve(side);
      const auto found = indices.find(curve);
      if (found == indices.end())
        throw std::invalid_argument("R2b2 patch borrows curve outside model owner");
      auto& group = result.incidence[found->second];
      for (const auto& other : group)
        if (other.patch == patch)
          throw std::invalid_argument("R2b2 patch reuses same curve on multiple sides");
      group.push_back({patch, side, source->IsCurveReversed(side),
                       curve->GetId()});
    }
  }
  std::size_t observed = 0;
  for (const auto& group : result.incidence) {
    if (group.empty())
      throw std::invalid_argument("R2b2 external curve has no patch incidence");
    observed += group.size();
    if (group.size() == 1U) ++result.exterior_curves;
    if (group.size() > 1U) ++result.shared_curves;
    if (group.size() > 2U) ++result.nonmanifold_curves;
  }
  if (observed != 4U * result.patches || result.shared_curves == 0)
    throw std::invalid_argument("R2b2 external model has no audited shared curves");
  return result;
}

struct SharedCurveSample {
  double t = 0.0;
  unsigned long node_id = 0;
  unsigned source_index = 0;
  std::array<double, 3> xyz{};
};
struct SharedCurveSide {
  std::size_t patch = 0;
  unsigned side = 0;
  int traversal = 0;
  unsigned long curve_id = 0;
  std::vector<SharedCurveSample> ordered_by_original_parameter;
};

inline SharedCurveSide SnapshotSharedCurveSide(
    const AdapterBoundaryCapture& capture, unsigned side) {
  if (side >= 4 || capture.vertices.size() < 4U ||
      capture.attempt.patch_index < 0 || capture.side_counts[side] < 1U)
    throw std::invalid_argument("R2b2 shared curve source has no valid side");
  SharedCurveSide result;
  result.patch = static_cast<std::size_t>(capture.attempt.patch_index);
  result.side = side;
  std::size_t last_index = capture.vertices.size();
  bool have_direction = false;
  bool reversed = false;
  std::size_t first_index = capture.vertices.size();
  for (std::size_t i = 0; i < capture.vertices.size(); ++i) {
    const auto& site = capture.vertices[i];
    if (site.side != side) continue;
    if (first_index == capture.vertices.size()) {
      first_index = i;
      reversed = site.curve_reversed;
      result.curve_id = site.curve_id;
      result.traversal = (side < 2U ? 1 : -1) * (reversed ? -1 : 1);
      have_direction = true;
    }
    if (!have_direction || site.curve_reversed != reversed ||
        site.curve_id != result.curve_id || site.physical_node_id == 0)
      throw std::invalid_argument("R2b2 shared curve source has inconsistent side provenance");
    result.ordered_by_original_parameter.push_back(
        {site.original_parameter, site.physical_node_id,
         site.source_index, site.physical_xyz});
    last_index = i;
  }
  const auto count = result.ordered_by_original_parameter.size();
  if (count == 0 || count != capture.side_counts[side] ||
      last_index == capture.vertices.size())
    throw std::invalid_argument("R2b2 original Adapter curve samples were lost");

  // The original Adapter intentionally omits the last site of each side
  // and reuses the first site on the next side. Recover the true endpoint by
  // this shared boundary vertex, not an independently evaluated substitute.
  const auto& endpoint =
      capture.vertices[(last_index + 1U) % capture.vertices.size()];
  const double chart_end = side < 2U ? 1.0 : 0.0;
  const double original_end = reversed ? 1.0 - chart_end : chart_end;
  result.ordered_by_original_parameter.push_back(
      {original_end, endpoint.physical_node_id,
       original_end == 0.0 ? 0U : static_cast<unsigned>(count),
       endpoint.physical_xyz});

  auto& sites = result.ordered_by_original_parameter;
  std::sort(sites.begin(), sites.end(),
            [](const SharedCurveSample& a, const SharedCurveSample& b) {
              return a.t < b.t;
            });
  for (std::size_t i = 0; i < sites.size(); ++i) {
    const auto& site = sites[i];
    if (!std::isfinite(site.t) || site.t < 0.0 || site.t > 1.0 ||
        site.node_id == 0 || !std::isfinite(site.xyz[0]) ||
        !std::isfinite(site.xyz[1]) || !std::isfinite(site.xyz[2]) ||
        (i > 0 && !(site.t > sites[i - 1U].t)))
      throw std::invalid_argument("R2b2 shared curve has invalid canonical samples");
  }
  if (sites.front().t != 0.0 || sites.back().t != 1.0)
    throw std::invalid_argument("R2b2 shared curve lost original endpoints");
  return result;
}

struct SharedCurveComparison {
  bool matched = false;
  std::string reason = "not_compared";
  std::size_t compared_sites = 0;
  std::size_t node_id_mismatched_sites = 0;
  std::size_t node_id_mismatched_endpoints = 0;
  std::size_t node_id_mismatched_interiors = 0;
  double maximum_xyz_error = 0.0;
};

inline SharedCurveComparison CompareSharedCurveSides(
    const SharedCurveSide& a, const SharedCurveSide& b,
    bool require_opposite_orientation = true,
    bool require_same_node_ids = true) {
  SharedCurveComparison result;
  if (a.patch == b.patch) { result.reason = "same_patch"; return result; }
  if (a.curve_id != b.curve_id) {
    result.reason = "curve_identity"; return result;
  }
  if (a.traversal == 0 || b.traversal == 0 ||
      (require_opposite_orientation &&
       a.traversal != -b.traversal)) {
    result.reason = "orientation"; return result;
  }
  if (a.ordered_by_original_parameter.size() !=
      b.ordered_by_original_parameter.size()) {
    result.reason = "sample_count"; return result;
  }
  for (std::size_t i = 0; i < a.ordered_by_original_parameter.size(); ++i) {
    const auto& x = a.ordered_by_original_parameter[i];
    const auto& y = b.ordered_by_original_parameter[i];
    if (x.t != y.t || x.source_index != y.source_index) {
      result.reason = "parameter"; return result;
    }
    if (x.node_id != y.node_id) {
      ++result.node_id_mismatched_sites;
      if (i == 0U || i + 1U == a.ordered_by_original_parameter.size())
        ++result.node_id_mismatched_endpoints;
      else
        ++result.node_id_mismatched_interiors;
      if (require_same_node_ids) {
        result.reason = "node_identity"; return result;
      }
    }
    double square_error = 0.0, square_scale = 0.0;
    for (unsigned axis = 0; axis < 3U; ++axis) {
      const double d = x.xyz[axis] - y.xyz[axis];
      square_error += d * d;
      square_scale += x.xyz[axis] * x.xyz[axis];
    }
    const double err = std::sqrt(square_error);
    const double scale = std::max(1.0, std::sqrt(square_scale));
    if (!std::isfinite(err) || err > 2e-7 * scale) {
      result.reason = "xyz"; return result;
    }
    result.maximum_xyz_error = std::max(result.maximum_xyz_error, err);
    ++result.compared_sites;
  }
  result.matched = true;
  result.reason = "none";
  return result;
}

using SharedEpochKey = std::tuple<std::uint64_t, std::uint64_t, int>;

struct SharedCurveModelAudit {
  std::size_t model_patches = 0;
  std::size_t model_curves = 0;
  std::size_t model_shared_curves = 0;
  std::size_t model_exterior_curves = 0;
  std::size_t model_nonmanifold_curves = 0;
  std::size_t coherent_epoch_patches = 0;
  std::size_t coherent_epoch_shared_curves_compared = 0;
  std::size_t coherent_epoch_shared_curves_matched = 0;
  std::size_t coherent_epoch_shared_curves_rejected = 0;
  std::size_t coherent_epoch_shared_curves_unobserved = 0;
  std::size_t coherent_epoch_shared_curves_geometry_matched = 0;
  std::size_t coherent_epoch_shared_curves_geometry_rejected = 0;
  std::size_t coherent_epoch_shared_curves_source_ids_matched = 0;
  std::size_t coherent_epoch_shared_curves_source_ids_rejected = 0;
  std::size_t shared_node_id_mismatch_pairs = 0;
  std::size_t shared_node_id_mismatch_sites = 0;
  std::size_t shared_node_id_mismatch_endpoints = 0;
  std::size_t shared_node_id_mismatch_interiors = 0;
  std::size_t coherent_epoch_sheet_policy_pending = 0;
  std::size_t shared_same_orientation_pairs = 0;
  std::size_t shared_opposite_orientation_pairs = 0;
  std::size_t shared_site_pairs_compared = 0;
  std::size_t repeated_patch_attempts = 0;
  std::uint64_t epoch = 0;
  int retry = -1;
  double maximum_xyz_error = 0.0;
  std::map<std::string, std::size_t> rejection_reasons;
};

// For coherence select exactly ONE observed outer generator epoch+retry, the
// epoch with maximum distinct patch coverage. Never stitch patch captures
// from separate global retries/adaptive epochs or silently deduplicate local
// retries into a claim of committed mixed physical connectivity.
inline SharedCurveModelAudit AuditCoherentAdapterSharedCurves(
    const SharedCurveTopology& graph,
    const std::vector<AdapterBoundaryCapture>& originals) {
  using PatchMap = std::map<std::size_t, const AdapterBoundaryCapture*>;
  std::map<SharedEpochKey, PatchMap> epochs;
  std::map<SharedEpochKey, std::size_t> duplicates;
  for (const auto& capture : originals) {
    const auto& attempt = capture.attempt;
    if (attempt.patch_index < 0 ||
        static_cast<std::size_t>(attempt.patch_index) >= graph.patches ||
        attempt.outer.epoch == 0 || attempt.outer.session == 0)
      throw std::invalid_argument("R2b2 original curve capture lacks generator epoch");
    const SharedEpochKey key{attempt.outer.session, attempt.outer.epoch,
                             attempt.outer.global_retry};
    auto& patches = epochs[key];
    if (!patches.emplace(static_cast<std::size_t>(attempt.patch_index),
                         &capture).second)
      ++duplicates[key];
  }
  SharedCurveModelAudit result;
  result.model_patches = graph.patches;
  result.model_curves = graph.curves;
  result.model_shared_curves = graph.shared_curves;
  result.model_exterior_curves = graph.exterior_curves;
  result.model_nonmanifold_curves = graph.nonmanifold_curves;
  const PatchMap* selected = nullptr;
  SharedEpochKey selected_key{};
  for (const auto& [key, patches] : epochs)
    if (selected == nullptr || patches.size() > selected->size()) {
      selected = &patches;
      selected_key = key;
    }
  if (selected == nullptr || selected->empty())
    throw std::invalid_argument("R2b2 no actual Adapter epoch source capture");
  result.coherent_epoch_patches = selected->size();
  result.epoch = std::get<1>(selected_key);
  result.retry = std::get<2>(selected_key);
  result.repeated_patch_attempts = duplicates[selected_key];

  for (const auto& group : graph.incidence) {
    if (group.size() < 2U) continue;
    std::vector<SharedCurveSide> actual;
    for (const auto& incidence : group) {
      const auto found = selected->find(incidence.patch);
      if (found == selected->end()) continue;
      SharedCurveSide side = SnapshotSharedCurveSide(*found->second, incidence.side);
      if (side.curve_id != incidence.curve_id ||
          found->second->vertices.empty() ||
          found->second->vertices.front().physical_node_id == 0) {
        ++result.rejection_reasons["independent_curve_provenance"];
        continue;
      }
      actual.push_back(std::move(side));
    }
    if (actual.size() < 2U) {
      ++result.coherent_epoch_shared_curves_unobserved;
      continue;
    }
    ++result.coherent_epoch_shared_curves_compared;
    // A multi-sheet curve cannot have pairwise opposing traversal for every
    // incident patch when valence > 2. First audit source node/parameter/XYZ
    // equivalence for ALL curve incidences WITHOUT imposing a sheet pairing.
    // Only a valence-2 incidence may be admitted as one opposing seam here.
    bool geometry_matched = actual.size() == group.size();
    bool source_ids_matched = geometry_matched;
    bool sheet_matched = geometry_matched && group.size() == 2U;
    if (group.size() > 2U) {
      ++result.coherent_epoch_sheet_policy_pending;
      ++result.rejection_reasons["nonmanifold_sheet_policy"];
    }
    if (actual.size() != group.size()) {
      ++result.rejection_reasons["incomplete_curve_incidence"];
    }
    for (std::size_t i = 0; i < actual.size(); ++i) {
      for (std::size_t j = i + 1U; j < actual.size(); ++j) {
        const auto compare = CompareSharedCurveSides(
            actual[i], actual[j], false, false);
        result.shared_site_pairs_compared += compare.compared_sites;
        if (compare.node_id_mismatched_sites != 0U) {
          source_ids_matched = false;
          sheet_matched = false;
          ++result.shared_node_id_mismatch_pairs;
          result.shared_node_id_mismatch_sites += compare.node_id_mismatched_sites;
          result.shared_node_id_mismatch_endpoints +=
              compare.node_id_mismatched_endpoints;
          result.shared_node_id_mismatch_interiors +=
              compare.node_id_mismatched_interiors;
          ++result.rejection_reasons["source_node_identity"];
        }
        result.maximum_xyz_error = std::max(
            result.maximum_xyz_error, compare.maximum_xyz_error);
        if (!compare.matched) {
          geometry_matched = false;
          sheet_matched = false;
          ++result.rejection_reasons[compare.reason];
        }
        if (actual[i].traversal == -actual[j].traversal) {
          ++result.shared_opposite_orientation_pairs;
        } else {
          ++result.shared_same_orientation_pairs;
          // This is a sheet seam failure only for an otherwise two-sided edge.
          if (group.size() == 2U) {
            sheet_matched = false;
            ++result.rejection_reasons["orientation"];
          }
        }
      }
    }
    if (geometry_matched)
      ++result.coherent_epoch_shared_curves_geometry_matched;
    else
      ++result.coherent_epoch_shared_curves_geometry_rejected;
    if (source_ids_matched)
      ++result.coherent_epoch_shared_curves_source_ids_matched;
    else
      ++result.coherent_epoch_shared_curves_source_ids_rejected;
    if (sheet_matched) ++result.coherent_epoch_shared_curves_matched;
    else ++result.coherent_epoch_shared_curves_rejected;
  }
  return result;
}

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_SHARED_CURVE_AUDIT_H
