#ifndef APMESH_QUAD_RESEARCH_PHYSICAL_QUADRILATERAL_ADAPTIVE_H
#define APMESH_QUAD_RESEARCH_PHYSICAL_QUADRILATERAL_ADAPTIVE_H

#include "data/element_adaptive.h"
#include "data/node_adaptive.h"

#include <array>

namespace apmesh::quad::research {

// This experimental four-node element is not linked into the production CLI.
// SubMesh may own it; its four NodeAdaptive pointers are observers only.
// The borrowing element must be destroyed before its node owners.
class QuadrilateralAdaptive final : public ElementAdaptive {
 public:
  using Uv = std::array<double, 2>;
  using Nodes = std::array<NodeAdaptive*, 4>;
  using Parameters = std::array<Uv, 4>;

  // The reference normal must be aligned with the intended patch orientation.
  // The optional slot is a research-only deterministic constructor fault hook:
  // values [0,3] throw just before registering that node observer.
  QuadrilateralAdaptive(Nodes nodes, Parameters parameters,
                        const VectorAdaptive& reference_normal,
                        int fail_before_slot = -1);
  ~QuadrilateralAdaptive() override;

  QuadrilateralAdaptive(const QuadrilateralAdaptive&) = delete;
  QuadrilateralAdaptive& operator=(const QuadrilateralAdaptive&) = delete;
  QuadrilateralAdaptive(QuadrilateralAdaptive&&) = delete;
  QuadrilateralAdaptive& operator=(QuadrilateralAdaptive&&) = delete;

  void CalculateArea() override;
  void CalculateNormal() override;
  NodeAdaptive GetNoh(unsigned const int position) const override;
  double GetAngle(const NodeAdaptive& node) override;

  // Return a position/ID snapshot; never copy foreign element observers.
  PointAdaptive GetVertexPoint(unsigned int position) const;
  const Parameters& GetParameters() const noexcept { return uv_; }
  const Nodes& GetNodeObservers() const noexcept { return nodes_; }

 private:
  struct GeometryMetrics {
    VectorAdaptive unnormalized_normal;
    double triangulated_area = 0.0;
  };

  void ValidateInput() const;
  GeometryMetrics EvaluateGeometry() const;

  Nodes nodes_;
  Parameters uv_;
  VectorAdaptive reference_normal_;
};

}  // namespace apmesh::quad::research

#endif  // APMESH_QUAD_RESEARCH_PHYSICAL_QUADRILATERAL_ADAPTIVE_H
