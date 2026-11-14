#ifndef APMESH_QUAD_DISJOINT_OWNER_STAGE_H
#define APMESH_QUAD_DISJOINT_OWNER_STAGE_H

#include "data/mesh/mesh_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"
#include "physical_quadrilateral_adaptive.h"

#include <cstddef>
#include <memory>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad::research {

// Research-only proof of strongly exception-safe, *disconnected* chart
// replacement. It deliberately does not attach a Patch observer and cannot
// publish model-wide physical continuity or ownership across patches.
class DisjointOwnerStage final {
 public:
  explicit DisjointOwnerStage(std::size_t expected)
      : expected_(expected) {
    if (expected_ == 0 || expected_ > 28)
      throw std::invalid_argument("Invalid bounded disjoint stage cardinality");
  }

  DisjointOwnerStage(const DisjointOwnerStage&) = delete;
  DisjointOwnerStage& operator=(const DisjointOwnerStage&) = delete;

  // Check that every owned element has only owned chart-local node observers.
  // The caller must not construct an element borrowing another chart's nodes;
  // such a graph would already violate the required external lifetime rule.
  static void CheckChart(const SubMesh& chart) {
    if (chart.GetPatch() != nullptr)
      throw std::invalid_argument("Candidate patch observer must remain detached");
    if (chart.GetNumberNos() == 0 || chart.GetNumberElements() == 0)
      throw std::invalid_argument("Candidate chart is not populated");
    std::set<const NodeAdaptive*> nodes;
    std::set<const ElementAdaptive*> elements;
    for (unsigned i = 0; i < chart.GetNumberNos(); ++i) {
      const auto* node = chart.GetNoh(i);
      if (!node || !nodes.insert(node).second)
        throw std::invalid_argument("Null or duplicated chart node");
    }
    for (unsigned i = 0; i < chart.GetNumberElements(); ++i) {
      const auto* element = chart.GetElement(i);
      if (!element || !elements.insert(element).second)
        throw std::invalid_argument("Null or duplicated chart element");
      if (!dynamic_cast<const QuadrilateralAdaptive*>(element) &&
          !dynamic_cast<const TriangleAdaptive*>(element))
        throw std::invalid_argument("Unexpected untyped research element");
    }
    std::vector<unsigned> observations(chart.GetNumberElements(), 0);
    for (const auto* node : nodes) {
      for (const auto* observer : node->GetElements()) {
        if (!elements.count(observer))
          throw std::invalid_argument("Chart node observes a foreign element");
        for (unsigned i = 0; i < chart.GetNumberElements(); ++i)
          if (chart.GetElement(i) == observer)
            ++observations[i];
      }
    }
    for (unsigned i = 0; i < chart.GetNumberElements(); ++i) {
      const auto* element = chart.GetElement(i);
      const unsigned expected =
          dynamic_cast<const QuadrilateralAdaptive*>(element) ? 4U : 3U;
      if (observations[i] != expected)
        throw std::invalid_argument("Element borrows an unowned chart node");
      if (const auto* quad =
              dynamic_cast<const QuadrilateralAdaptive*>(element)) {
        for (const auto* vertex : quad->GetNodeObservers())
          if (!nodes.count(vertex))
            throw std::invalid_argument("QUAD borrows another chart's node");
      }
    }
  }

  void Add(std::unique_ptr<SubMesh> chart) {
    if (!chart || detached_.size() >= expected_)
      throw std::invalid_argument("Missing or excess disjoint candidate chart");
    CheckChart(*chart);
    detached_.push_back(std::move(chart));
  }

  // Only a fully populated candidate may be returned. Synthetic fault
  // injection tests every intermediate adoption and the pre-publication seam.
  // Failed candidates are destroyed without changing the old active mesh.
  std::unique_ptr<MeshAdaptive> Prepare(int fail_before_chart = -1) {
    if (detached_.size() != expected_)
      throw std::invalid_argument("Incomplete disconnected model stage");
    std::set<const NodeAdaptive*> all;
    for (const auto& chart : detached_) {
      CheckChart(*chart);
      for (unsigned i = 0; i < chart->GetNumberNos(); ++i)
        if (!all.insert(chart->GetNoh(i)).second)
          throw std::invalid_argument("Cross-chart node ownership is not authorized");
    }

    auto candidate = std::make_unique<MeshAdaptive>();
    for (std::size_t i = 0; i < expected_; ++i) {
      if (fail_before_chart == static_cast<int>(i))
        throw std::runtime_error("Injected chart adoption failure");
      candidate->InsertSubMeshAdaptive(detached_[i].release());
    }
    if (fail_before_chart == static_cast<int>(expected_))
      throw std::runtime_error("Injected pre-publication validation failure");
    if (candidate->GetNumberSubMeshesAdaptive() != expected_)
      throw std::runtime_error("Incomplete staged owner adoption");
    return candidate;
  }

  void Replace(std::unique_ptr<MeshAdaptive>& active,
               int fail_before_chart = -1) {
    auto candidate = Prepare(fail_before_chart);
    // This is the sole no-throw publication point. The retiring model is
    // destroyed only after every candidate chart has been fully staged.
    active.swap(candidate);
  }

 private:
  std::size_t expected_;
  std::vector<std::unique_ptr<SubMesh>> detached_;
};

}  // namespace apmesh::quad::research

#endif  // APMESH_QUAD_DISJOINT_OWNER_STAGE_H
