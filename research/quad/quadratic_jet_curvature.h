#ifndef APMESH_QUAD_QUADRATIC_JET_CURVATURE_H
#define APMESH_QUAD_QUADRATIC_JET_CURVATURE_H

#include "jet_small_matrix.h"

#include <map>
#include <optional>
#include <set>
#include <string_view>
#include <utility>

namespace apmesh::quad::research::jet {
// Adopted contract: MIXED_CURVATURE_OPERATOR_CONTRACT_20261119.md, section4.
// Local quadratic jets follow the method family of Cazals/Pouget, SGP2003.
// This is a new standard-library implementation, not copied CGAL code.
enum class Status {
  Available,
  InsufficientSamples,
  DuplicateSamples,
  DegenerateScale,
  AmbiguousFrame,
  UndefinedOrientation,
  RankDeficient,
  SolverUnconverged,
  Nonfinite
};
inline std::string_view StatusName(Status status) {
  switch (status) {
  case Status::Available:
    return "available";
  case Status::InsufficientSamples:
    return "insufficient_samples";
  case Status::DuplicateSamples:
    return "duplicate_samples";
  case Status::DegenerateScale:
    return "degenerate_scale";
  case Status::AmbiguousFrame:
    return "ambiguous_frame";
  case Status::UndefinedOrientation:
    return "undefined_orientation";
  case Status::RankDeficient:
    return "rank_deficient";
  case Status::SolverUnconverged:
    return "solver_unconverged";
  case Status::Nonfinite:
    return "nonfinite";
  }
  throw std::invalid_argument("Unknown jet status");
}
struct Curvatures {
  double gaussian = 0, mean = 0;
  Point normal{};
};
struct Estimate {
  Status status = Status::InsufficientSamples;
  std::size_t ring = 0;
  std::vector<std::size_t> support;
  double scale = 0, covariance_guard = 0, orientation = 0, offset = 0;
  Eigen3 covariance;
  LeastSquares6 fit;
  Point tangent1{}, tangent2{}, rough_normal{};
  std::optional<Curvatures> value;
};

// Exposed independently of PCA for analytical known-frame coefficient controls.
inline Curvatures GraphCurvatures(const Row& coefficients, double scale, const Point& tangent1,
                                  const Point& tangent2, const Point& normal,
                                  const Point& reference, double orientation_guard) {
  const double p = coefficients[1], q = coefficients[2];
  const double r = 2 * coefficients[3] / scale, s = coefficients[4] / scale,
               t = 2 * coefficients[5] / scale;
  const double d = 1 + p * p + q * q;
  Curvatures result;
  result.gaussian = (r * t - s * s) / (d * d);
  result.mean = ((1 + q * q) * r - 2 * p * q * s + (1 + p * p) * t) / (2 * d * std::sqrt(d));
  result.normal =
      Scale(Subtract(Subtract(normal, Scale(tangent1, p)), Scale(tangent2, q)), 1 / std::sqrt(d));
  const double alignment = Dot(result.normal, reference);
  if (!std::isfinite(alignment) || std::abs(alignment) <= orientation_guard)
    throw std::domain_error("Undefined fitted jet orientation");
  if (alignment < 0) {
    result.normal = Scale(result.normal, -1);
    result.mean = -result.mean;
  }
  if (!std::isfinite(result.gaussian) || !std::isfinite(result.mean) || !Finite(result.normal))
    throw std::overflow_error("Nonfinite fitted jet curvature");
  return result;
}

inline Estimate FitSamples(const std::vector<Point>& positions, std::size_t query,
                           const std::vector<std::size_t>& support, const Point& reference_normal) {
  if (query >= positions.size())
    throw std::invalid_argument("Foreign jet query");
  Estimate result;
  result.support = support;
  std::set<std::size_t> identities;
  std::set<Point> coordinates;
  for (auto id : support) {
    if (id >= positions.size() || !identities.insert(id).second)
      throw std::invalid_argument("Foreign or repeated jet sample identity");
    if (!Finite(positions[id])) {
      result.status = Status::Nonfinite;
      return result;
    }
    if (!coordinates.insert(positions[id]).second) {
      result.status = Status::DuplicateSamples;
      return result;
    }
    result.scale = std::max(result.scale, Norm(Subtract(positions[id], positions[query])));
  }
  if (!identities.count(query))
    throw std::invalid_argument("Jet support omits query");
  if (support.size() < 6)
    return result;
  if (!(result.scale > 0) || !std::isfinite(result.scale)) {
    result.status = Status::DegenerateScale;
    return result;
  }
  std::vector<Point> normalized;
  Point centroid{};
  for (auto id : support) {
    const auto p = Scale(Subtract(positions[id], positions[query]), 1 / result.scale);
    normalized.push_back(p);
    for (std::size_t i = 0; i < 3; ++i)
      centroid[i] += p[i];
  }
  centroid = Scale(centroid, 1 / static_cast<double>(support.size()));
  std::array<Point, 3> covariance{};
  for (const auto& p : normalized) {
    const auto centered = Subtract(p, centroid);
    for (std::size_t i = 0; i < 3; ++i)
      for (std::size_t j = 0; j < 3; ++j)
        covariance[i][j] += centered[i] * centered[j] / static_cast<double>(support.size());
  }
  result.covariance = SymmetricEigen3(covariance);
  if (!result.covariance.converged) {
    result.status = Status::SolverUnconverged;
    return result;
  }
  const auto& eigenvalues = result.covariance.values;
  const double epsilon = std::numeric_limits<double>::epsilon();
  result.covariance_guard =
      static_cast<double>(std::max<std::size_t>(support.size(), 3)) * epsilon *
      std::max({std::abs(eigenvalues[0]), std::abs(eigenvalues[1]), std::abs(eigenvalues[2])});
  if (!(eigenvalues[1] - eigenvalues[0] > result.covariance_guard)) {
    result.status = Status::AmbiguousFrame;
    return result;
  }
  const double reference_size = Norm(reference_normal);
  if (!Finite(reference_normal)) {
    result.status = Status::Nonfinite;
    return result;
  }
  if (!(reference_size > 0) || !std::isfinite(reference_size)) {
    result.status = Status::UndefinedOrientation;
    return result;
  }
  const auto reference = Scale(reference_normal, 1 / reference_size);
  auto normal = result.covariance.vectors[0];
  const double alignment = Dot(normal, reference);
  const double orientation_guard =
      static_cast<double>(std::max<std::size_t>(support.size(), 3)) * epsilon;
  if (std::abs(alignment) <= orientation_guard) {
    result.status = Status::UndefinedOrientation;
    return result;
  }
  if (alignment < 0)
    normal = Scale(normal, -1);
  std::size_t axis = 0;
  for (std::size_t k = 1; k < 3; ++k)
    if (std::abs(normal[k]) < std::abs(normal[axis]))
      axis = k;
  Point tangent{};
  tangent[axis] = 1;
  tangent = Subtract(tangent, Scale(normal, normal[axis]));
  result.tangent1 = Scale(tangent, 1 / Norm(tangent));
  result.tangent2 = Cross(normal, result.tangent1);
  result.rough_normal = normal;
  std::vector<Row> design;
  std::vector<double> response;
  for (const auto& p : normalized) {
    const double x = Dot(p, result.tangent1), y = Dot(p, result.tangent2);
    design.push_back({1, x, y, x * x, x * y, y * y});
    response.push_back(Dot(p, normal));
  }
  result.fit = SolveLeastSquares6(design, response);
  if (!result.fit.converged) {
    result.status = Status::SolverUnconverged;
    return result;
  }
  if (result.fit.rank != 6) {
    result.status = Status::RankDeficient;
    return result;
  }
  result.offset = result.scale * result.fit.coefficients[0];
  try {
    result.value = GraphCurvatures(result.fit.coefficients, result.scale, result.tangent1,
                                   result.tangent2, normal, reference, orientation_guard);
    result.orientation = Dot(result.value->normal, reference);
  } catch (const std::domain_error&) {
    result.status = Status::UndefinedOrientation;
    return result;
  } catch (const std::overflow_error&) {
    result.status = Status::Nonfinite;
    return result;
  }
  result.status = Status::Available;
  return result;
}

struct Neighborhood {
  std::vector<std::set<std::size_t>> coface;
  std::vector<bool> boundary;
};

// Polygon cycles, not a triangulated/diagonal star. Same fan semantics as P2b;
// validation here does not compute or depend on the P2b angle-defect witness.
inline Neighborhood BuildNeighborhood(std::size_t nodes,
                                      const std::vector<std::vector<std::size_t>>& faces) {
  if (nodes == 0 || faces.empty())
    throw std::invalid_argument("Empty jet chart");
  Neighborhood result;
  result.coface.resize(nodes);
  result.boundary.resize(nodes, false);
  std::map<std::pair<std::size_t, std::size_t>, std::vector<std::pair<std::size_t, std::size_t>>>
      edges;
  std::vector<std::map<std::size_t, std::set<std::size_t>>> links(nodes);
  for (const auto& f : faces) {
    if ((f.size() != 3 && f.size() != 4) ||
        std::set<std::size_t>(f.begin(), f.end()).size() != f.size())
      throw std::invalid_argument("Invalid jet face cycle");
    for (auto id : f)
      if (id >= nodes)
        throw std::invalid_argument("Foreign jet face vertex");
    for (std::size_t i = 0; i < f.size(); ++i) {
      const auto a = f[i], b = f[(i + 1) % f.size()], before = f[(i + f.size() - 1) % f.size()];
      auto& uses = edges[std::minmax(a, b)];
      if (uses.size() >= 2 || (!uses.empty() && uses[0] != std::make_pair(b, a)))
        throw std::invalid_argument("Invalid jet halfedge incidence");
      uses.emplace_back(a, b);
      if (!links[a][before].insert(b).second || !links[a][b].insert(before).second)
        throw std::invalid_argument("Repeated jet vertex-link sector");
      for (auto other : f)
        if (other != a)
          result.coface[a].insert(other);
    }
  }
  for (const auto& entry : edges)
    if (entry.second.size() == 1) {
      result.boundary[entry.first.first] = true;
      result.boundary[entry.first.second] = true;
    }
  for (std::size_t i = 0; i < nodes; ++i) {
    if (links[i].empty())
      throw std::invalid_argument("Unused jet node");
    std::size_t endpoints = 0;
    for (const auto& entry : links[i]) {
      if (entry.second.size() == 1)
        ++endpoints;
      else if (entry.second.size() != 2)
        throw std::invalid_argument("Nonmanifold jet fan");
    }
    if (endpoints != (result.boundary[i] ? 2U : 0U))
      throw std::invalid_argument("Invalid jet boundary fan");
    std::set<std::size_t> visited;
    std::vector<std::size_t> pending{links[i].begin()->first};
    while (!pending.empty()) {
      auto current = pending.back();
      pending.pop_back();
      if (!visited.insert(current).second)
        continue;
      for (auto next : links[i].at(current))
        pending.push_back(next);
    }
    if (visited.size() != links[i].size())
      throw std::invalid_argument("Disconnected jet fan");
  }
  if (std::find(result.boundary.begin(), result.boundary.end(), true) == result.boundary.end() ||
      nodes + faces.size() != edges.size() + 1)
    throw std::invalid_argument("Jet chart must be a manifold disk");
  std::set<std::size_t> reached;
  std::vector<std::size_t> pending{0};
  while (!pending.empty()) {
    const auto id = pending.back();
    pending.pop_back();
    if (!reached.insert(id).second)
      continue;
    for (auto other : result.coface[id])
      pending.push_back(other);
  }
  if (reached.size() != nodes)
    throw std::invalid_argument("Disconnected jet chart");
  return result;
}

inline bool Expandable(Status status) {
  return status == Status::InsufficientSamples || status == Status::AmbiguousFrame ||
         status == Status::RankDeficient;
}
inline Estimate EstimateNode(const std::vector<Point>& positions, const Neighborhood& graph,
                             std::size_t query, const Point& reference) {
  if (query >= positions.size() || graph.coface.size() != positions.size())
    throw std::invalid_argument("Foreign jet neighborhood");
  std::set<std::size_t> first = graph.coface[query];
  first.insert(query);
  auto result = FitSamples(positions, query, {first.begin(), first.end()}, reference);
  result.ring = 1;
  if (!Expandable(result.status))
    return result;
  auto second = first;
  for (auto id : first)
    second.insert(graph.coface.at(id).begin(), graph.coface.at(id).end());
  result = FitSamples(positions, query, {second.begin(), second.end()}, reference);
  result.ring = 2;
  return result;
}

// Separately adopted diagnostic comparison; the original bounded policy above stays unchanged.
inline Estimate EstimateNodeCompleteTwoRing(const std::vector<Point>& positions,
                                            const Neighborhood& graph, std::size_t query,
                                            const Point& reference) {
  if (query >= positions.size() || graph.coface.size() != positions.size())
    throw std::invalid_argument("Foreign jet neighborhood");
  std::set<std::size_t> first = graph.coface[query];
  first.insert(query);
  auto second = first;
  for (auto id : first)
    second.insert(graph.coface.at(id).begin(), graph.coface.at(id).end());
  auto result = FitSamples(positions, query, {second.begin(), second.end()}, reference);
  result.ring = 2;
  return result;
}
} // namespace apmesh::quad::research::jet
#endif
