#ifndef AP_MESH_TEST_LEGACY_CURVATURE_DISCRETE_H
#define AP_MESH_TEST_LEGACY_CURVATURE_DISCRETE_H

#include "curvature/curvature_discrete.h"
#include "data/definitions.h"

// Frozen pre-transfer algorithm from d9e298186f6fa951d6caac976831b74d477c7680.
// Kim, S. J., Jeong, W. K. and Kim, C. H. (1999), LOD generation with discrete
// curvature error metric, Korea Israel Bi-National Conference, pp. 97-104.
namespace curvature_test_reference {
class LegacyCurvatureDiscrete : public Curvature {
public:
  explicit LegacyCurvatureDiscrete(const NodeAdaptive& node);
  double CalculateMeanCurvature() override;
  double CalculateGaussCurvature() override;

private:
  void AdjacencySort(const NodeAdaptive& node);

  NodeAdaptive node_;

  std::list<ElementAdaptive*> elements_;

  double area_;

  double boundary_factor_;

  double angle_sum_;
  Adjacent adjacent_;
};

inline LegacyCurvatureDiscrete::LegacyCurvatureDiscrete(const NodeAdaptive& node) {

  this->AdjacencySort(node);

  this->area_ = 0;
  this->angle_sum_ = 0;

  std::list<ElementAdaptive*>::const_iterator element_iterator;

  for (element_iterator = node.GetElements().begin(); element_iterator != node.GetElements().end();
       ++element_iterator) {

    this->area_ += (*element_iterator)->GetArea();

    this->angle_sum_ += (*element_iterator)->GetAngle(node);
  }

  this->node_ = node;
}

inline double LegacyCurvatureDiscrete::CalculateMeanCurvature() {
  ElementAdaptive* first_element;
  ElementAdaptive* next_element;
  double angle_sum = 0;

  while (this->elements_.size() > 1) {
    first_element = this->elements_.front();
    this->elements_.pop_front();
    next_element = this->elements_.front();

    int concavity_value;

    concavity_value = adjacent_.ConcavityElement(this->node_, *first_element, *next_element);

    if (concavity_value)
      angle_sum += concavity_value * adjacent_.AngleElement(*first_element, *next_element);
  }

  this->elements_.pop_front();
  return 3.0 * angle_sum / this->area_;
}

inline double LegacyCurvatureDiscrete::CalculateGaussCurvature() {
  return (3.0 * (this->boundary_factor_ - this->angle_sum_) / this->area_);
}

inline void LegacyCurvatureDiscrete::AdjacencySort(const NodeAdaptive& node) {
  this->elements_.clear();

  std::list<ElementAdaptive*> new_list_elements;
  new_list_elements = node.GetElements();

  ElementAdaptive* element_front = new_list_elements.front();
  this->elements_.push_back(element_front);
  new_list_elements.pop_front();

  bool find_adj_left = true;

  while (find_adj_left) {
    ElementAdaptive* element = adjacent_.GetElementLeft(node, element_front, new_list_elements);
    if (element) {
      this->elements_.push_back(element);
      element_front = element;
    } else
      find_adj_left = false;
  }

  if (!new_list_elements.empty()) {
    this->boundary_factor_ = M_PI;
    element_front = this->elements_.front();

    bool find_adj_right = true;

    while (find_adj_right) {
      ElementAdaptive* element = adjacent_.GetElementRight(node, element_front, new_list_elements);
      if (element) {
        this->elements_.push_front(element);
        element_front = element;
      } else
        find_adj_right = false;
    }
  }

  else {
    if (adjacent_.ConfirmRightAdjacency(node, *(this->elements_.front()),
                                        *(this->elements_.back()))) {
      this->boundary_factor_ = 2 * M_PI;
      this->elements_.push_back(this->elements_.front());
    } else
      this->boundary_factor_ = M_PI;
  }
}

} // namespace curvature_test_reference
#endif
