#ifndef DATA_MESH_SUB_MESH_H
#define DATA_MESH_SUB_MESH_H

#include <memory>
#include <vector>

class Patch;
class NodeAdaptive;
class ElementAdaptive;

class SubMesh {
public:
  SubMesh();
  ~SubMesh(); // Defined in .cpp to keep forward declarations valid.

  // Non-copyable to avoid double free.
  SubMesh(const SubMesh&) = delete;
  SubMesh& operator=(const SubMesh&) = delete;

  SubMesh(SubMesh&&) noexcept;
  // Retire old elements before their nodes; self-move preserves this graph.
  // Owned elements may borrow local nodes or independently live external nodes.
  // Moving does not rebind foreign Patch observers of either SubMesh object.
  SubMesh& operator=(SubMesh&&) noexcept;

  Patch* GetPatch() const noexcept;
  void SetPatch(Patch* patch) noexcept;

  NodeAdaptive* GetNoh(unsigned int position) noexcept;
  const NodeAdaptive* GetNoh(unsigned int position) const noexcept;

  ElementAdaptive* GetElement(unsigned int position) noexcept;
  const ElementAdaptive* GetElement(unsigned int position) const noexcept;

  // Transfer unique ownership; the node's address and adjacency are preserved.
  void AddNoh(std::unique_ptr<NodeAdaptive> noh);
  void AddElement(std::unique_ptr<ElementAdaptive> element);

  // Copy ID, position and curvature state into a new owned node. The caller
  // retains the source. Foreign element observers are excluded; local triangles
  // register their adjacency after construction. A null source is ignored.
  void SetNoh(NodeAdaptive* noh);
  // Consume exclusive ownership on entry, including allocation failure.
  // The argument must not already be owned; null appends an empty slot.
  // Its nodes must outlive it, including destruction after failed adoption.
  // TriangleAdaptive destruction unregisters from its live current vertex nodes.
  void SetElement(ElementAdaptive* element);

  unsigned int GetNumberNos() const noexcept;
  unsigned int GetNumberElements() const noexcept;

private:
  Patch* patch_ = nullptr; // non-owning

  std::vector<std::unique_ptr<NodeAdaptive>> nos_;
  std::vector<std::unique_ptr<ElementAdaptive>> elements_;
};

#endif // DATA_MESH_SUB_MESH_H
