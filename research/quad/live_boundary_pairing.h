#ifndef APMESH_RESEARCH_QUAD_LIVE_BOUNDARY_PAIRING_H
#define APMESH_RESEARCH_QUAD_LIVE_BOUNDARY_PAIRING_H

#include "boundary_pair_candidates.h"
#include "typed_mixed_quality.h"
#include "uv_mesh.h"

#include <cmath>
#include <string>
#include <tuple>

namespace apmesh::quad {

struct PairSite {
  UvVertex uv;
  research::QualityPoint3 xyz;
  research::QualityPoint3 normal;
};

struct LivePairEvent {
  BoundaryPairCandidate candidate;
  std::size_t front_order;
  std::string status;
  double score = 0.0;
  double edge_ratio = 0.0;
  bool measured = false;
};

inline bool PreferLivePair(const LivePairEvent& a, const LivePairEvent& b) {
  const auto key = [](const LivePairEvent& event) {
    return std::make_tuple(event.score, event.edge_ratio, event.front_order,
                           event.candidate.first_triangle, event.candidate.boundary_cycle);
  };
  return key(a) < key(b);
}

// Incremental selection at triangle-commit time, never a completed-mesh matcher.
// The original TRI scaffold remains owned by AFT. Only value IDs are retained;
// physical publication belongs to a separate, all-or-nothing SubMesh candidate.
class LiveBoundaryPairing {
public:
  std::size_t AddSite(PairSite site) {
    sites_.push_back(site);
    return sites_.size() - 1;
  }

  void ObserveTriangle(const std::array<std::size_t, 3>& triangle) {
    const auto current = triangles_.size();
    for (auto id : triangle)
      if (id >= sites_.size())
        throw std::invalid_argument("Live pair triangle has a foreign site");
    if (triangle[0] == triangle[1] || triangle[1] == triangle[2] || triangle[2] == triangle[0])
      throw std::invalid_argument("Live pair triangle repeats a site");
    triangles_.push_back(triangle);
    consumed_.push_back(false);
    const auto begin = events_.size();
    for (std::size_t side = 0; side < 3; ++side) {
      const auto from = triangle[side], to = triangle[(side + 1) % 3];
      const auto opposite = triangle[(side + 2) % 3];
      const std::pair<std::size_t, std::size_t> key = std::minmax(from, to);
      const auto inserted = edges_.emplace(key, EdgeUse{current, from, to, opposite, 1});
      if (inserted.second)
        continue;
      auto& previous = inserted.first->second;
      if (previous.count != 1 || previous.from != to || previous.to != from ||
          previous.opposite == opposite)
        throw std::invalid_argument("Live pair scaffold has invalid oriented incidence");
      ++previous.count;
      std::array<std::size_t, 4> cycle{previous.from, opposite, previous.to, previous.opposite};
      std::rotate(cycle.begin(), std::min_element(cycle.begin(), cycle.end()), cycle.end());
      LivePairEvent event{
          {previous.triangle, current, {key.first, key.second}, cycle}, side, "already_paired"};
      if (!consumed_[previous.triangle])
        Evaluate(event);
      events_.push_back(std::move(event));
    }
    std::size_t winner = events_.size();
    for (auto i = begin; i < events_.size(); ++i) {
      if (events_[i].status != "eligible")
        continue;
      if (winner == events_.size() || PreferLivePair(events_[i], events_[winner]))
        winner = i;
    }
    if (winner != events_.size()) {
      selected_.push_back(events_[winner].candidate);
      consumed_[events_[winner].candidate.first_triangle] = true;
      consumed_[current] = true;
      events_[winner].status = "selected";
    }
    for (auto i = begin; i < events_.size(); ++i)
      if (events_[i].status == "eligible")
        events_[i].status = "not_selected";
  }

  const auto& Triangles() const noexcept { return triangles_; }
  const auto& Consumed() const noexcept { return consumed_; }
  const auto& Selected() const noexcept { return selected_; }
  const auto& Events() const noexcept { return events_; }

private:
  void Evaluate(LivePairEvent& event) const {
    research::PhysicalQuadCorners points{}, normals{};
    const auto& cycle = event.candidate.boundary_cycle;
    for (std::size_t i = 0; i < 4; ++i) {
      const auto& a = sites_[cycle[i]];
      const auto& b = sites_[cycle[(i + 1) % 4]];
      const auto& c = sites_[cycle[(i + 3) % 4]];
      const double determinant =
          (b.uv.u - a.uv.u) * (c.uv.v - a.uv.v) - (b.uv.v - a.uv.v) * (c.uv.u - a.uv.u);
      if (!std::isfinite(determinant) || determinant <= 1e-14) {
        event.status = "rejected_uv";
        return;
      }
      points[i] = a.xyz;
      normals[i] = a.normal;
    }
    try {
      event.edge_ratio = research::ObservePhysicalQuadQuality(points, normals).edge_ratio;
    } catch (const std::invalid_argument&) {
      event.status = "rejected_physical";
      return;
    }
    constexpr double half_turn = 180.0;
    const double degrees = half_turn / std::acos(-1.0);
    event.score = 1.0;
    for (std::size_t i = 0; i < 4; ++i) {
      research::QualityPoint3 next{}, prev{};
      double dot = 0.0, first = 0.0, second = 0.0;
      for (std::size_t axis = 0; axis < 3; ++axis) {
        next[axis] = points[(i + 1) % 4][axis] - points[i][axis];
        prev[axis] = points[(i + 3) % 4][axis] - points[i][axis];
        dot += next[axis] * prev[axis];
        first += next[axis] * next[axis];
        second += prev[axis] * prev[axis];
      }
      const double cosine = dot / (std::sqrt(first) * std::sqrt(second));
      if (!std::isfinite(cosine)) {
        event.status = "rejected_physical";
        return;
      }
      const double angle = std::acos(std::clamp(cosine, -1.0, 1.0)) * degrees;
      event.score = std::max(event.score, 1.0 + std::abs(angle - 90.0) / 90.0);
    }
    event.measured = true;
    event.status = event.score <= 1.5 ? "eligible" : "rejected_shape";
  }

  struct EdgeUse {
    std::size_t triangle, from, to, opposite;
    unsigned count;
  };
  std::vector<PairSite> sites_;
  std::vector<std::array<std::size_t, 3>> triangles_;
  std::vector<bool> consumed_;
  std::vector<BoundaryPairCandidate> selected_;
  std::vector<LivePairEvent> events_;
  std::map<std::pair<std::size_t, std::size_t>, EdgeUse> edges_;
};

} // namespace apmesh::quad
#endif
