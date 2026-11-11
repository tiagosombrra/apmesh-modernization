#include "physical_quadrilateral_adaptive.h"

#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>

namespace apmesh::quad::research {
namespace {

bool Finite(const VectorAdaptive& v) {
  return std::isfinite(v.GetX()) && std::isfinite(v.GetY()) &&
         std::isfinite(v.GetZ());
}

double SignedUvTriangle(const QuadrilateralAdaptive::Parameters& uv,
                        unsigned a, unsigned b, unsigned c) {
  const auto& p = uv[a];
  const auto& q = uv[b];
  const auto& r = uv[c];
  return (q[0] - p[0]) * (r[1] - p[1]) -
         (q[1] - p[1]) * (r[0] - p[0]);
}

}  // namespace

QuadrilateralAdaptive::QuadrilateralAdaptive(
    Nodes nodes, Parameters parameters,
    const VectorAdaptive& reference_normal, int fail_before_slot)
    : nodes_(nodes), uv_(parameters), reference_normal_(reference_normal) {
  ValidateInput();
  const GeometryMetrics metrics = EvaluateGeometry();
  vector_normal_ = metrics.unnormalized_normal;
  area_ = metrics.triangulated_area;

  // Validate the entire geometry before the first observer mutation.
  // Any allocation or injected failure restores all pre-existing lists.
  try {
    for (unsigned index = 0; index < nodes_.size(); ++index) {
      if (fail_before_slot == static_cast<int>(index))
        throw std::runtime_error("Injected quadrilateral registration failure");
      nodes_[index]->InsertElement(this);
    }
  } catch (...) {
    for (auto* node : nodes_)
      node->RemoveElementObserver(this);
    throw;
  }
}

QuadrilateralAdaptive::~QuadrilateralAdaptive() {
  for (auto* node : nodes_)
    node->RemoveElementObserver(this);
}

void QuadrilateralAdaptive::ValidateInput() const {
  if (!Finite(reference_normal_) ||
      !(reference_normal_.CalculateModule() > 1e-12))
    throw std::invalid_argument("Invalid chart normal");

  std::set<NodeAdaptive*> unique_nodes;
  for (unsigned i = 0; i < nodes_.size(); ++i) {
    NodeAdaptive* node = nodes_[i];
    if (!node || !unique_nodes.insert(node).second)
      throw std::invalid_argument("Quad nodes must be non-null and unique");
    if (!std::isfinite(node->GetX()) || !std::isfinite(node->GetY()) ||
        !std::isfinite(node->GetZ()))
      throw std::invalid_argument("Nonfinite physical quad node");
    for (double value : uv_[i])
      if (!std::isfinite(value) || value < 0.0 || value > 1.0)
        throw std::invalid_argument("Invalid quad UV domain");
  }
  if (!(SignedUvTriangle(uv_, 0, 1, 2) > 1e-14) ||
      !(SignedUvTriangle(uv_, 0, 2, 3) > 1e-14))
    throw std::invalid_argument("Inverted, concave or collapsed UV quad");
}

QuadrilateralAdaptive::GeometryMetrics
QuadrilateralAdaptive::EvaluateGeometry() const {
  const VectorAdaptive a(*nodes_[0], *nodes_[1]);
  const VectorAdaptive b(*nodes_[0], *nodes_[2]);
  const VectorAdaptive c(*nodes_[0], *nodes_[3]);
  const VectorAdaptive first = a * b;
  const VectorAdaptive second = b * c;
  const double first_size = first.CalculateModule();
  const double second_size = second.CalculateModule();
  const double first_signed = first ^ reference_normal_;
  const double second_signed = second ^ reference_normal_;
  if (!Finite(first) || !Finite(second) ||
      !std::isfinite(first_size) || !std::isfinite(second_size) ||
      !(first_size > 1e-14) || !(second_size > 1e-14) ||
      !(first_signed > 1e-12) || !(second_signed > 1e-12))
    throw std::invalid_argument(
        "Degenerate or reverse-oriented physical quad subtriangle");

  const double area = 0.5 * (first_size + second_size);
  const VectorAdaptive normal = first + second;
  if (!std::isfinite(area) || !Finite(normal) || !(area > 1e-14))
    throw std::invalid_argument("Invalid physical quad area/normal");
  return {normal, area};
}

void QuadrilateralAdaptive::CalculateArea() {
  const auto metrics = EvaluateGeometry();
  area_ = metrics.triangulated_area;
}

void QuadrilateralAdaptive::CalculateNormal() {
  const auto metrics = EvaluateGeometry();
  vector_normal_ = metrics.unnormalized_normal;
}

NodeAdaptive QuadrilateralAdaptive::GetNoh(unsigned const int position) const {
  if (position == 0 || position > 4)
    throw std::out_of_range("Quad node position must be in [1,4]");
  // The NodeAdaptive(PointAdaptive) constructor copies only the physical
  // point and ID; the original element observer list remains exclusive.
  return NodeAdaptive(static_cast<const PointAdaptive&>(*nodes_[position - 1]));
}

PointAdaptive QuadrilateralAdaptive::GetVertexPoint(unsigned int position) const {
  if (position == 0 || position > 4)
    throw std::out_of_range("Quad vertex position must be in [1,4]");
  return static_cast<const PointAdaptive&>(*nodes_[position - 1]);
}

double QuadrilateralAdaptive::GetAngle(const NodeAdaptive& node) {
  for (unsigned i = 0; i < 4; ++i) {
    // Address identity prevents a geometric coincidence from choosing the
    // wrong observer, unlike legacy proximity-based triangle matching.
    if (&node != nodes_[i])
      continue;
    const VectorAdaptive before(*nodes_[i], *nodes_[(i + 3) % 4]);
    const VectorAdaptive after(*nodes_[i], *nodes_[(i + 1) % 4]);
    const double lengths = before.CalculateModule() * after.CalculateModule();
    if (!std::isfinite(lengths) || !(lengths > 1e-14))
      throw std::invalid_argument("Undefined physical quad corner angle");
    const double cosine = std::clamp((before ^ after) / lengths, -1.0, 1.0);
    const double angle = std::acos(cosine);
    if (!std::isfinite(angle))
      throw std::invalid_argument("Nonfinite quad corner angle");
    return angle;
  }
  throw std::invalid_argument("Quad angle requires an identical live node");
}

}  // namespace apmesh::quad::research
