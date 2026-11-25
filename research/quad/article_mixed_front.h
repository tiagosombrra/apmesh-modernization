#ifndef APMESH_RESEARCH_ARTICLE_MIXED_FRONT_H
#define APMESH_RESEARCH_ARTICLE_MIXED_FRONT_H

#include "uv_mesh.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <functional>
#include <limits>
#include <optional>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {

struct ArticleFrontChoice {
  std::array<VertexId, 3> triangle{};
  std::array<VertexId, 4> quad{};
  int side = -1;
  double score = 0.0;
  bool eligible = false;
};
struct ArticleFrontAdditionalPair {
  std::array<VertexId, 3> first_triangle{};
  ArticleFrontChoice choice;
};
struct ArticleFrontPairScreen {
  double limit;
  std::function<std::optional<double>(const std::array<UvVertex, 4>&)> measure;
};
struct ArticleFrontPairMeasurement {
  std::array<VertexId, 4> quad;
  double score;
  std::optional<double> relative_error;
};
struct ArticleFrontCommit {
  std::vector<std::pair<VertexId, VertexId>> before;
  std::vector<VertexId> polygon;
  std::array<ArticleFrontChoice, 2> alternatives{};
  std::array<VertexId, 3> best{};
  int selected_side = -1;
  std::optional<ArticleFrontAdditionalPair> additional_pair;
  std::vector<ArticleFrontPairMeasurement> pair_measurements;
};
struct ArticleFrontResult {
  std::vector<UvVertex> vertices;
  std::vector<std::vector<VertexId>> faces;
  std::vector<ArticleFrontCommit> commits;
  std::size_t seed_quads = 0;
  std::vector<std::array<double, 4>> leaves;
};

// Research-only planar contraction: existing nodes, two prospective neighbors,
// then one polygonal contour update. No production AFT path is replaced.
class ArticleMixedFront {
public:
  using Edge = std::pair<VertexId, VertexId>;
  using Box = std::array<double, 4>;

  ArticleMixedFront(const UvMesh& seed, const std::vector<UvVertex>& boundary,
                    std::vector<Box> leaves, bool additional_pairs = false,
                    std::optional<ArticleFrontPairScreen> pair_screen = std::nullopt)
      : leaves_(std::move(leaves)), additional_pairs_(additional_pairs),
        pair_screen_(std::move(pair_screen)) {
    Require(!pair_screen_ || (additional_pairs_ && pair_screen_->measure &&
                              std::isfinite(pair_screen_->limit) && pair_screen_->limit >= 0),
            "Invalid additional-pair geometry screen");
    Require(boundary.size() >= 3 && !leaves_.empty(), "Article front needs boundary and leaves");
    result_.vertices = seed.vertices;
    result_.leaves = leaves_;
    for (const auto& p : result_.vertices)
      Require(std::isfinite(p.u) && std::isfinite(p.v), "Nonfinite article seed vertex");
    std::set<std::pair<double, double>> unique;
    for (const auto& p : result_.vertices)
      Require(unique.emplace(p.u, p.v).second, "Duplicate article seed vertex");
    for (const auto& box : leaves_)
      Require(std::all_of(box.begin(), box.end(), [](double x) { return std::isfinite(x); }) &&
                  box[0] < box[2] && box[1] < box[3],
              "Invalid article leaf box");
    std::vector<VertexId> outer;
    for (const auto& p : boundary) {
      Require(std::isfinite(p.u) && std::isfinite(p.v) && unique.emplace(p.u, p.v).second,
              "Article boundary duplicates an existing site");
      outer.push_back(result_.vertices.size());
      result_.vertices.push_back(p);
    }
    for (std::size_t i = 0; i < outer.size(); ++i)
      front_.emplace_back(outer[i], outer[(i + 1) % outer.size()]);
    std::vector<Edge> seed_front;
    for (const auto& q : seed.quads) {
      result_.faces.emplace_back(q.vertices.begin(), q.vertices.end());
      for (std::size_t i = 0; i < 4; ++i) {
        Require(q.vertices[i] < seed.vertices.size(), "Foreign article seed index");
        Toggle(seed_front, {q.vertices[i], q.vertices[(i + 1) % 4]});
      }
    }
    for (auto e : seed_front)
      front_.emplace_back(e.second, e.first);
    result_.seed_quads = seed.quads.size();
    Require(!front_.empty(), "Empty article input front");
  }

  // Work stays in this temporary value owner; failure never publishes a partial
  // graph or mutates the caller's native tree, source boundary or physical mesh.
  ArticleFrontResult
  Run(std::size_t abort_before_commit = std::numeric_limits<std::size_t>::max()) {
    Require(!attempted_, "Article contraction is a one-shot owner");
    attempted_ = true;
    std::size_t skipped = 0;
    while (!front_.empty()) {
      Require(result_.commits.size() < 4 * result_.vertices.size(),
              "Article front did not terminate");
      const auto base = front_.front();
      const auto best = Best(base, nullptr);
      if (best == invalid_) {
        std::rotate(front_.begin(), front_.begin() + 1, front_.end());
        Require(++skipped < front_.size(), "Article local search exhausted active contour");
        continue;
      }
      skipped = 0;
      ArticleFrontCommit step;
      step.before = front_;
      step.best = {base.first, base.second, best};
      step.polygon.assign(step.best.begin(), step.best.end());
      const std::array<Edge, 2> sides{{{best, base.second}, {base.first, best}}};
      for (std::size_t side = 0; side < sides.size(); ++side) {
        auto& choice = step.alternatives[side];
        choice.side = static_cast<int>(side);
        const auto other = Best(sides[side], &step.best);
        if (other == invalid_)
          continue;
        choice.triangle = {sides[side].first, sides[side].second, other};
        choice.quad = side == 0 ? std::array<VertexId, 4>{base.first, base.second, other, best}
                                : std::array<VertexId, 4>{base.first, base.second, best, other};
        choice.score = Shape(choice.quad);
        choice.eligible = std::isfinite(choice.score) && choice.score <= 1.5;
        // The paper does not prescribe a tie rule: minimum S, then side order.
        if (choice.eligible &&
            (step.selected_side < 0 ||
             choice.score <
                 step.alternatives[static_cast<std::size_t>(step.selected_side)].score)) {
          step.selected_side = static_cast<int>(side);
          step.polygon.assign(choice.quad.begin(), choice.quad.end());
        }
      }
      if (additional_pairs_ && step.selected_side < 0) {
        step.additional_pair = AdditionalPair(base, step.pair_measurements);
        if (step.additional_pair) {
          const auto& quad = step.additional_pair->choice.quad;
          step.polygon.assign(quad.begin(), quad.end());
        }
      }
      Require(result_.commits.size() != abort_before_commit, "Injected article precommit failure");
      // Prepare every allocating operation before the contour is committed.
      auto next = front_;
      for (std::size_t i = 0; i < step.polygon.size(); ++i)
        Toggle(next, {step.polygon[(i + 1) % step.polygon.size()], step.polygon[i]});
      auto face = step.polygon;
      result_.faces.reserve(result_.faces.size() + 1);
      result_.commits.reserve(result_.commits.size() + 1);
      result_.faces.push_back(std::move(face));
      result_.commits.push_back(std::move(step));
      front_.swap(next);
    }
    return std::move(result_);
  }

private:
  static constexpr VertexId invalid_ = std::numeric_limits<VertexId>::max();
  static constexpr long double epsilon_ = 1e-14L;
  ArticleFrontResult result_;
  std::vector<Box> leaves_;
  std::vector<Edge> front_;
  bool attempted_ = false;
  bool additional_pairs_ = false;
  std::optional<ArticleFrontPairScreen> pair_screen_;

  static void Require(bool ok, const char* message) {
    if (!ok)
      throw std::runtime_error(message);
  }
  // Directed contour cancellation: equal undirected sides must be opposite.
  static void Toggle(std::vector<Edge>& front, Edge edge) {
    const auto same = std::find(front.begin(), front.end(), edge);
    Require(same == front.end(), "Article contour has duplicate same-direction edge");
    const auto opposite = std::find(front.begin(), front.end(), Edge{edge.second, edge.first});
    if (opposite == front.end())
      front.push_back(edge);
    else
      front.erase(opposite);
  }
  long double Cross(VertexId a, VertexId b, VertexId c) const {
    const auto& x = result_.vertices[a];
    const auto& y = result_.vertices[b];
    const auto& z = result_.vertices[c];
    return (static_cast<long double>(y.u) - x.u) * (static_cast<long double>(z.v) - x.v) -
           (static_cast<long double>(y.v) - x.v) * (static_cast<long double>(z.u) - x.u);
  }
  bool OnSegment(VertexId a, VertexId b, VertexId c) const {
    const auto& x = result_.vertices[a];
    const auto& y = result_.vertices[b];
    const auto& z = result_.vertices[c];
    return std::abs(Cross(a, b, c)) <= epsilon_ && z.u >= std::min(x.u, y.u) &&
           z.u <= std::max(x.u, y.u) && z.v >= std::min(x.v, y.v) && z.v <= std::max(x.v, y.v);
  }
  bool Crosses(Edge a, Edge b) const {
    const auto x = Cross(a.first, a.second, b.first), y = Cross(a.first, a.second, b.second);
    const auto z = Cross(b.first, b.second, a.first), w = Cross(b.first, b.second, a.second);
    return ((x > epsilon_ && y < -epsilon_) || (y > epsilon_ && x < -epsilon_)) &&
           ((z > epsilon_ && w < -epsilon_) || (w > epsilon_ && z < -epsilon_));
  }
  bool Contains(const std::array<VertexId, 3>& t, VertexId p) const {
    return Cross(t[0], t[1], p) > epsilon_ && Cross(t[1], t[2], p) > epsilon_ &&
           Cross(t[2], t[0], p) > epsilon_;
  }
  bool InsideRemaining(const std::array<VertexId, 3>& t) const {
    const auto& a = result_.vertices[t[0]];
    const auto& b = result_.vertices[t[1]];
    const auto& c = result_.vertices[t[2]];
    const UvVertex p{(a.u + b.u + c.u) / 3, (a.v + b.v + c.v) / 3};
    int winding = 0;
    for (auto e : front_) {
      const auto& x = result_.vertices[e.first];
      const auto& y = result_.vertices[e.second];
      const long double cr = (static_cast<long double>(y.u) - x.u) * (p.v - x.v) -
                             (static_cast<long double>(y.v) - x.v) * (p.u - x.u);
      if (x.v <= p.v && y.v > p.v && cr > 0)
        ++winding;
      if (x.v > p.v && y.v <= p.v && cr < 0)
        --winding;
    }
    return winding == 1;
  }
  bool Valid(const std::array<VertexId, 3>& t, const std::array<VertexId, 3>* excluded) const {
    if (Cross(t[0], t[1], t[2]) <= epsilon_ || !InsideRemaining(t))
      return false;
    for (auto e : front_) {
      for (auto p : {e.first, e.second}) {
        if (p == t[0] || p == t[1] || p == t[2])
          continue;
        if (Contains(t, p))
          return false;
        for (std::size_t i = 0; i < 3; ++i)
          if (OnSegment(t[i], t[(i + 1) % 3], p))
            return false;
      }
      for (std::size_t i = 0; i < 3; ++i) {
        const Edge side{t[i], t[(i + 1) % 3]};
        if (side == Edge{e.second, e.first} || Crosses(side, e))
          return false;
      }
    }
    if (excluded) {
      // Adjacent lookahead must occupy the other side of its shared diagonal.
      // The two positive triangles then have disjoint interiors by construction.
      for (auto p : t)
        if (Contains(*excluded, p))
          return false;
      for (auto p : *excluded)
        if (Contains(t, p))
          return false;
      for (std::size_t i = 0; i < 3; ++i)
        for (std::size_t j = 0; j < 3; ++j)
          if (Crosses({t[i], t[(i + 1) % 3]}, {(*excluded)[j], (*excluded)[(j + 1) % 3]}))
            return false;
    }
    return true;
  }
  static bool Touch(const Box& a, const Box& b) {
    return a[0] <= b[2] && b[0] <= a[2] && a[1] <= b[3] && b[1] <= a[3];
  }
  bool InBox(VertexId v, const Box& b) const {
    const auto& p = result_.vertices[v];
    return p.u >= b[0] && p.u <= b[2] && p.v >= b[1] && p.v <= b[3];
  }
  // Optional collection shares the original first nonempty neighborhood.
  VertexId Best(Edge edge, const std::array<VertexId, 3>* excluded,
                std::vector<VertexId>* candidates = nullptr) const {
    std::vector<bool> cells(leaves_.size(), false);
    for (std::size_t i = 0; i < leaves_.size(); ++i)
      cells[i] = InBox(edge.first, leaves_[i]) || InBox(edge.second, leaves_[i]);
    for (unsigned expansion = 0; expansion < 2; ++expansion) {
      auto expanded = cells;
      for (std::size_t i = 0; i < leaves_.size(); ++i)
        if (cells[i])
          for (std::size_t j = 0; j < leaves_.size(); ++j)
            if (Touch(leaves_[i], leaves_[j]))
              expanded[j] = true;
      cells.swap(expanded);
      VertexId best = invalid_;
      double best_angle = -1;
      std::set<VertexId> active;
      for (auto e : front_) {
        active.insert(e.first);
        active.insert(e.second);
      }
      for (auto p : active) {
        if (p == edge.first || p == edge.second)
          continue;
        bool in = false;
        for (std::size_t i = 0; i < leaves_.size(); ++i)
          if (cells[i] && InBox(p, leaves_[i])) {
            in = true;
            break;
          }
        if (!in || !Valid({edge.first, edge.second, p}, excluded))
          continue;
        if (candidates)
          candidates->push_back(p);
        const auto& a = result_.vertices[edge.first];
        const auto& b = result_.vertices[edge.second];
        const auto& v = result_.vertices[p];
        const double ax = a.u - v.u, ay = a.v - v.v, bx = b.u - v.u, by = b.v - v.v;
        const double angle = std::atan2(std::abs(ax * by - ay * bx), ax * bx + ay * by);
        // Stable source ID order resolves exact ties; no pointer ordering.
        if (angle > best_angle) {
          best_angle = angle;
          best = p;
        }
      }
      if (best != invalid_)
        return best;
    }
    return invalid_;
  }
  std::optional<ArticleFrontAdditionalPair>
  AdditionalPair(Edge base, std::vector<ArticleFrontPairMeasurement>& measurements) const {
    std::vector<VertexId> apices;
    Best(base, nullptr, &apices);
    std::optional<ArticleFrontAdditionalPair> best;
    for (const auto apex : apices) {
      const std::array<VertexId, 3> triangle{base.first, base.second, apex};
      const std::array<Edge, 2> sides{{{apex, base.second}, {base.first, apex}}};
      for (std::size_t side = 0; side < sides.size(); ++side) {
        const auto edge = sides[side];
        std::vector<VertexId> companions;
        Best(edge, &triangle, &companions);
        for (const auto other : companions) {
          const auto quad = side == 0
                                ? std::array<VertexId, 4>{base.first, base.second, other, apex}
                                : std::array<VertexId, 4>{base.first, base.second, apex, other};
          const auto score = Shape(quad);
          if (!std::isfinite(score) || score > 1.5)
            continue;
          if (pair_screen_) {
            const std::array<UvVertex, 4> corners{
                result_.vertices[quad[0]], result_.vertices[quad[1]], result_.vertices[quad[2]],
                result_.vertices[quad[3]]};
            const auto error = pair_screen_->measure(corners);
            measurements.push_back({quad, score, error});
            if (!error || *error > pair_screen_->limit)
              continue;
          }
          // Loops retain vertex ID, side and companion ID order for exact ties.
          if (!best || score < best->choice.score) {
            best = ArticleFrontAdditionalPair{
                triangle,
                {{edge.first, edge.second, other}, quad, static_cast<int>(side), score, true}};
          }
        }
      }
    }
    return best;
  }
  double Shape(const std::array<VertexId, 4>& q) const {
    double score = 1;
    for (std::size_t i = 0; i < 4; ++i) {
      const auto a = q[i], b = q[(i + 1) % 4], c = q[(i + 3) % 4];
      if (Cross(a, b, c) <= epsilon_)
        return std::numeric_limits<double>::infinity();
      const auto& x = result_.vertices[a];
      const auto& y = result_.vertices[b];
      const auto& z = result_.vertices[c];
      const double ux = y.u - x.u, uy = y.v - x.v, vx = z.u - x.u, vy = z.v - x.v;
      const double angle =
          std::atan2(std::abs(ux * vy - uy * vx), ux * vx + uy * vy) * 180 / std::acos(-1.0);
      score = std::max(score, 1 + std::abs(angle - 90) / 90);
    }
    return score;
  }
};
} // namespace apmesh::quad
#endif
