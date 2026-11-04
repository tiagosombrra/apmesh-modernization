#include "../../include/curvature/adjacent.h"

#include <typeinfo>

namespace {
template <bool Snapshot> auto NodePoint(const ElementAdaptive& element, unsigned int position) {
  if constexpr (Snapshot)
    return static_cast<const TriangleAdaptive&>(element).GetVertexPoint(position);
  else
    return element.GetNoh(position);
}
} // namespace

extern double TOLERANCE;

// P de Primeiro, U de Último !!! :D
// confirma que U é adjacente à esquerda de P
template <bool Snapshot>
static bool ConfirmLeftAdjacencyValues(const NodeAdaptive& noh,
                                       const ElementAdaptive& first_element,
                                       const ElementAdaptive& last_element) {
  //	quem é o noh para P? ( n1, n2 ou n3? )
  //	se noh = P.n1 então verifique se U possui a sequência P.n1 P.n3

  if (noh == NodePoint<Snapshot>(first_element, 1)) {
    if (((NodePoint<Snapshot>(first_element, 1) == NodePoint<Snapshot>(last_element, 1)) and
         (NodePoint<Snapshot>(first_element, 3) == NodePoint<Snapshot>(last_element, 2))) or

        ((NodePoint<Snapshot>(first_element, 1) == NodePoint<Snapshot>(last_element, 3)) and
         (NodePoint<Snapshot>(first_element, 3) == NodePoint<Snapshot>(last_element, 1))) or

        ((NodePoint<Snapshot>(first_element, 1) == NodePoint<Snapshot>(last_element, 2)) and
         (NodePoint<Snapshot>(first_element, 3) == NodePoint<Snapshot>(last_element, 3))))
      return true;
  }

  //	se noh = P.n2 então verifique se U possui a sequência P.n2 P.n1
  if (noh == NodePoint<Snapshot>(first_element, 2)) {
    if (((NodePoint<Snapshot>(first_element, 2) == NodePoint<Snapshot>(last_element, 1)) and
         (NodePoint<Snapshot>(first_element, 1) == NodePoint<Snapshot>(last_element, 2))) or

        ((NodePoint<Snapshot>(first_element, 2) == NodePoint<Snapshot>(last_element, 3)) and
         (NodePoint<Snapshot>(first_element, 1) == NodePoint<Snapshot>(last_element, 1))) or

        ((NodePoint<Snapshot>(first_element, 2) == NodePoint<Snapshot>(last_element, 2)) and
         (NodePoint<Snapshot>(first_element, 1) == NodePoint<Snapshot>(last_element, 3))))
      return true;
  }

  //	se noh = P.n3 então verifique se U possui a sequência P.n3 P.n2
  if (noh == NodePoint<Snapshot>(first_element, 3)) {
    if (((NodePoint<Snapshot>(first_element, 3) == NodePoint<Snapshot>(last_element, 1)) and
         (NodePoint<Snapshot>(first_element, 2) == NodePoint<Snapshot>(last_element, 2))) or

        ((NodePoint<Snapshot>(first_element, 3) == NodePoint<Snapshot>(last_element, 3)) and
         (NodePoint<Snapshot>(first_element, 2) == NodePoint<Snapshot>(last_element, 1))) or

        ((NodePoint<Snapshot>(first_element, 3) == NodePoint<Snapshot>(last_element, 2)) and
         (NodePoint<Snapshot>(first_element, 2) == NodePoint<Snapshot>(last_element, 3))))
      return true;
  }

  return false;
}

// confirma que U é adjacente à direita de P
template <bool Snapshot>
static bool ConfirmRightAdjacencyValues(const NodeAdaptive& noh,
                                        const ElementAdaptive& first_element,
                                        const ElementAdaptive& last_element) {
  //	quem é o noh para P? ( n1, n2 ou n3? )
  //	se noh = P.n1 então verifique se U possui a sequência P.n2 P.n1
  if (noh == NodePoint<Snapshot>(first_element, 1)) {
    if (((NodePoint<Snapshot>(last_element, 1) == NodePoint<Snapshot>(first_element, 1)) and
         (NodePoint<Snapshot>(last_element, 3) == NodePoint<Snapshot>(first_element, 2))) or

        ((NodePoint<Snapshot>(last_element, 3) == NodePoint<Snapshot>(first_element, 1)) and
         (NodePoint<Snapshot>(last_element, 2) == NodePoint<Snapshot>(first_element, 2))) or

        ((NodePoint<Snapshot>(last_element, 2) == NodePoint<Snapshot>(first_element, 1)) and
         (NodePoint<Snapshot>(last_element, 1) == NodePoint<Snapshot>(first_element, 2))))
      return true;
  }

  //	se noh = P.n2 então verifique se U possui a sequência P.n3 P.n2
  if (noh == NodePoint<Snapshot>(first_element, 2)) {
    if (((NodePoint<Snapshot>(last_element, 1) == NodePoint<Snapshot>(first_element, 2)) and
         (NodePoint<Snapshot>(last_element, 3) == NodePoint<Snapshot>(first_element, 3))) or

        ((NodePoint<Snapshot>(last_element, 3) == NodePoint<Snapshot>(first_element, 2)) and
         (NodePoint<Snapshot>(last_element, 2) == NodePoint<Snapshot>(first_element, 3))) or

        ((NodePoint<Snapshot>(last_element, 2) == NodePoint<Snapshot>(first_element, 2)) and
         (NodePoint<Snapshot>(last_element, 1) == NodePoint<Snapshot>(first_element, 3))))
      return true;
  }

  //	se noh = P.n3 então verifique se U possui a sequência P.n1 P.n3
  if (noh == NodePoint<Snapshot>(first_element, 3)) {
    if (((NodePoint<Snapshot>(last_element, 1) == NodePoint<Snapshot>(first_element, 3)) and
         (NodePoint<Snapshot>(last_element, 3) == NodePoint<Snapshot>(first_element, 1))) or

        ((NodePoint<Snapshot>(last_element, 3) == NodePoint<Snapshot>(first_element, 3)) and
         (NodePoint<Snapshot>(last_element, 2) == NodePoint<Snapshot>(first_element, 1))) or

        ((NodePoint<Snapshot>(last_element, 2) == NodePoint<Snapshot>(first_element, 3)) and
         (NodePoint<Snapshot>(last_element, 1) == NodePoint<Snapshot>(first_element, 1))))
      return true;
  }

  return false;
}

ElementAdaptive* Adjacent::GetElementLeft(const NodeAdaptive& noh, ElementAdaptive* element,
                                          std::list<ElementAdaptive*>& list_element) {
  ElementAdaptive* element_result = nullptr;
  std::list<ElementAdaptive*>::iterator element_iterator;

  for (element_iterator = list_element.begin(); element_iterator != list_element.end();
       ++element_iterator) {
    if (Adjacent::ConfirmLeftAdjacency(noh, *element, *(*element_iterator))) {
      element_result = *element_iterator;
      list_element.erase(element_iterator);
      break;
    }
  }

  return element_result;
}

// busca na lista um elemento adjacente à direita de elem
ElementAdaptive* Adjacent::GetElementRight(const NodeAdaptive& noh, ElementAdaptive* element,
                                           std::list<ElementAdaptive*>& list_element) {
  ElementAdaptive* element_result = nullptr;
  std::list<ElementAdaptive*>::iterator element_iterator;

  for (element_iterator = list_element.begin(); element_iterator != list_element.end();
       ++element_iterator) {
    if (Adjacent::ConfirmRightAdjacency(noh, *element, *(*element_iterator))) {
      element_result = *element_iterator;
      list_element.erase(element_iterator);
      break;
    }
  }

  return element_result;
}

// verifica a concavidade de dois elementos adjacentes
template <bool Snapshot>
static int ConcavityValues(const NodeAdaptive& noh, const ElementAdaptive& first_element,
                           const ElementAdaptive& next_element) {
  VectorAdaptive vector;

  if (noh == NodePoint<Snapshot>(next_element, 1))
    vector =
        VectorAdaptive(NodePoint<Snapshot>(next_element, 1), NodePoint<Snapshot>(next_element, 3));
  else if (noh == NodePoint<Snapshot>(next_element, 2))
    vector =
        VectorAdaptive(NodePoint<Snapshot>(next_element, 2), NodePoint<Snapshot>(next_element, 1));
  else
    vector =
        VectorAdaptive(NodePoint<Snapshot>(next_element, 3), NodePoint<Snapshot>(next_element, 2));

  double d;
  d = first_element.GetVectorNormal() ^ vector;

  if (fabs(d) <= TOLERANCE)
    return 0;

  if (d > 0)
    return -1;
  else
    return 1;
}

double Adjacent::AngleElement(const ElementAdaptive& first_element,
                              const ElementAdaptive& next_element) {
  VectorAdaptive first_vector = first_element.GetVectorNormal();
  VectorAdaptive next_vector = next_element.GetVectorNormal();

  return first_vector.CalculateAngle(next_vector);
}

// Exact triangles use coordinate snapshots; polymorphic extensions keep node values.
bool Adjacent::ConfirmLeftAdjacency(const NodeAdaptive& node, const ElementAdaptive& first,
                                    const ElementAdaptive& last) {
  if (typeid(first) == typeid(TriangleAdaptive) && typeid(last) == typeid(TriangleAdaptive))
    return ConfirmLeftAdjacencyValues<true>(node, first, last);
  return ConfirmLeftAdjacencyValues<false>(node, first, last);
}

bool Adjacent::ConfirmRightAdjacency(const NodeAdaptive& node, const ElementAdaptive& first,
                                     const ElementAdaptive& last) {
  if (typeid(first) == typeid(TriangleAdaptive) && typeid(last) == typeid(TriangleAdaptive))
    return ConfirmRightAdjacencyValues<true>(node, first, last);
  return ConfirmRightAdjacencyValues<false>(node, first, last);
}

int Adjacent::ConcavityElement(const NodeAdaptive& node, const ElementAdaptive& first,
                               const ElementAdaptive& next) {
  if (typeid(next) == typeid(TriangleAdaptive))
    return ConcavityValues<true>(node, first, next);
  return ConcavityValues<false>(node, first, next);
}
