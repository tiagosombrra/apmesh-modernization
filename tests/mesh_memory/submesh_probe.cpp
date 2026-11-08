#include <array>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <optional>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/mesh/sub_mesh.h"
#include "data/patch/patch.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Submesh lifetime contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Lifetime {
  int nodes = 0, elements = 0, expected_nodes = 0, expected_elements = 0;
  bool ordered = true, read_observers = false;
  bool Complete() const {
    return ordered && nodes == expected_nodes && elements == expected_elements;
  }
};

class CountedNode final : public NodeAdaptive {
public:
  CountedNode(Lifetime& lifetime, int index)
      : NodeAdaptive(index == 1 ? 1.0 : 0.0, index == 2 ? 1.0 : 0.0, 0), lifetime_(lifetime) {
    SetId(40 + index);
    SetGa(4);
    SetGd(5);
    SetHa(6);
    SetHd(7);
    ++lifetime_.expected_nodes;
  }
  ~CountedNode() override { ++lifetime_.nodes; }

private:
  Lifetime& lifetime_;
};

class CountedTriangle final : public TriangleAdaptive {
public:
  CountedTriangle(Lifetime& lifetime, NodeAdaptive* a, NodeAdaptive* b, NodeAdaptive* c)
      : TriangleAdaptive(a, b, c), lifetime_(lifetime) {
    ++lifetime_.expected_elements;
    SetId(72);
    SetParametersN1({0.25, 0.5});
  }
  ~CountedTriangle() override {
    lifetime_.ordered = lifetime_.ordered && lifetime_.nodes == 0;
    // The dedicated ASan experiment intentionally consumes the borrowed nodes.
    // Other modes detect bad ordering without dereferencing expired observers.
    if (lifetime_.read_observers) {
      volatile double observed = n1_->GetX() + n2_->GetY() + n3_->GetZ();
      (void)observed;
    }
    ++lifetime_.elements;
  }

private:
  Lifetime& lifetime_;
};

void Populate(SubMesh& mesh, Lifetime& lifetime, int layout) {
  if (layout == 0)
    return;
  for (int i = 0; i < 3; ++i)
    mesh.AddNoh(std::make_unique<CountedNode>(lifetime, i));
  if (layout == 1)
    return;
  mesh.AddElement(
      std::make_unique<CountedTriangle>(lifetime, mesh.GetNoh(0), mesh.GetNoh(1), mesh.GetNoh(2)));
  if (layout == 3) {
    mesh.AddNoh(nullptr);
    mesh.AddElement(nullptr);
    mesh.AddElement(std::make_unique<CountedTriangle>(lifetime, mesh.GetNoh(0), mesh.GetNoh(0),
                                                      mesh.GetNoh(2)));
  }
}

struct Snapshot {
  std::array<NodeAdaptive*, 4> nodes{};
  std::array<ElementAdaptive*, 3> elements{};
  unsigned int node_count, element_count;
  Patch* patch;
  explicit Snapshot(SubMesh& mesh)
      : node_count(mesh.GetNumberNos()), element_count(mesh.GetNumberElements()),
        patch(mesh.GetPatch()) {
    for (unsigned int i = 0; i < node_count; ++i)
      nodes[i] = mesh.GetNoh(i);
    for (unsigned int i = 0; i < element_count; ++i)
      elements[i] = mesh.GetElement(i);
  }
  bool Matches(SubMesh& mesh) const {
    if (mesh.GetNumberNos() != node_count || mesh.GetNumberElements() != element_count ||
        mesh.GetPatch() != patch)
      return false;
    for (unsigned int i = 0; i < node_count; ++i) {
      auto* node = mesh.GetNoh(i);
      if (node != nodes[i])
        return false;
      if (!node)
        continue;
      if (node->GetId() != 40 + i || node->GetX() != (i == 1 ? 1.0 : 0.0) ||
          node->GetY() != (i == 2 ? 1.0 : 0.0) || node->GetZ() != 0 || node->GetGa() != 4 ||
          node->GetGd() != 5 || node->GetHa() != 6 || node->GetHd() != 7)
        return false;
      unsigned int at = 0;
      for (auto* observer : node->GetElements()) {
        const auto* expected = at == 0 ? elements[0] : elements[2];
        if (observer != expected)
          return false;
        ++at;
      }
      const unsigned int expected =
          element_count == 0
              ? 0
              : (element_count == 3 && i == 0 ? 3 : (element_count == 3 && i == 2 ? 2 : 1));
      if (at != expected)
        return false;
    }
    for (unsigned int i = 0; i < element_count; ++i) {
      auto* element = mesh.GetElement(i);
      if (element != elements[i])
        return false;
      if (element && (element->GetId() != 72 || element->GetArea() != (i == 2 ? 0 : 0.5) ||
                      static_cast<TriangleAdaptive*>(element)->GetParametersN1() !=
                          std::make_tuple(0.25, 0.5)))
        return false;
    }
    return true;
  }
};

struct Fixture {
  Lifetime incoming, retired;
  std::array<Patch, 2> patches;
  std::unique_ptr<SubMesh> source = std::make_unique<SubMesh>();
  std::unique_ptr<SubMesh> destination = std::make_unique<SubMesh>();
  std::optional<SubMesh> moved;
  int variant;
  explicit Fixture(int mode, bool read = false) : variant(mode) {
    incoming.read_observers = retired.read_observers = read;
    Populate(*source, incoming, mode == 5 ? 0 : (mode == 6 ? 1 : (mode == 7 ? 3 : 2)));
    source->SetPatch(&patches[0]);
    destination->SetPatch(&patches[1]);
    if (mode == 3 || mode >= 5)
      Populate(*destination, retired, 2);
  }
  bool Exercise() {
    Snapshot expected(*source);
    bool preserved = true;
    if (variant == 1) {
      moved.emplace(std::move(*source));
      preserved = expected.Matches(*moved);
    } else if (variant == 4) {
      auto* alias = source.get();
      *source = std::move(*alias);
      preserved = expected.Matches(*source);
    } else if (variant != 0) {
      SubMesh* returned = &(*destination = std::move(*source));
      preserved = returned == destination.get() && expected.Matches(*destination);
      preserved = preserved && retired.Complete();
    }
    if (variant != 0 && variant != 4)
      preserved = preserved && source->GetNumberNos() == 0 && source->GetNumberElements() == 0 &&
                  source->GetPatch() == expected.patch;
    moved.reset();
    destination.reset();
    source.reset();
    const bool complete = incoming.Complete() && retired.Complete();
    std::printf(
        "submesh_observed=variant:%d identity:%d ordered:%d complete:%d nodes:%d elements:%d\n",
        variant, preserved, incoming.ordered && retired.ordered, complete,
        incoming.nodes + retired.nodes, incoming.elements + retired.elements);
    return preserved && complete;
  }
};

bool CheckPatchObservers() {
  bool mesh_first = false, patch_first = false, history = false;
  bool rebind = false, foreign = false, moves = false, patch_moves = false;
  {
    Patch patch;
    std::optional<SubMesh> mesh(std::in_place);
    mesh->SetPatch(&patch);
    patch.SetSubMesh(&*mesh);
    mesh.reset();
    mesh_first = patch.GetSubMesh() == nullptr;
  }
  {
    SubMesh mesh;
    std::optional<Patch> patch(std::in_place);
    mesh.SetPatch(&*patch);
    patch->SetSubMesh(&mesh);
    patch.reset();
    patch_first = mesh.GetPatch() == nullptr;
  }
  {
    std::array<SubMesh, 3> retained;
    std::optional<Patch> patch(std::in_place);
    for (auto& mesh : retained)
      mesh.SetPatch(&*patch);
    patch->SetSubMesh(&retained[1]);
    patch.reset();
    history = retained[0].GetPatch() == nullptr && retained[1].GetPatch() == nullptr &&
              retained[2].GetPatch() == nullptr;
  }
  {
    Patch first, second;
    SubMesh mesh, unrelated;
    mesh.SetPatch(&first);
    first.SetSubMesh(&mesh);
    mesh.SetPatch(&second);
    rebind = first.GetSubMesh() == nullptr && mesh.GetPatch() == &second;
    mesh.SetPatch(&second);
    second.SetSubMesh(&unrelated);
    mesh.SetPatch(nullptr);
    mesh.SetPatch(nullptr);
    foreign = second.GetSubMesh() == &unrelated && mesh.GetPatch() == nullptr;
  }
  {
    Patch patch;
    std::optional<SubMesh> oldest(std::in_place), middle(std::in_place), newest(std::in_place);
    oldest->SetPatch(&patch);
    middle->SetPatch(&patch);
    newest->SetPatch(&patch);
    patch.SetSubMesh(&*newest);
    middle.reset();
    oldest.reset();
    history = history && patch.GetSubMesh() == &*newest && newest->GetPatch() == &patch;
    newest.reset();
    history = history && patch.GetSubMesh() == nullptr;
    SubMesh unrelated;
    std::optional<SubMesh> observer(std::in_place);
    observer->SetPatch(&patch);
    patch.SetSubMesh(&unrelated);
    observer.reset();
    foreign = foreign && patch.GetSubMesh() == &unrelated;
  }
  {
    std::optional<Patch> first(std::in_place), second(std::in_place);
    SubMesh source, target;
    source.SetPatch(&*first);
    target.SetPatch(&*second);
    first->SetSubMesh(&source);
    second->SetSubMesh(&target);
    SubMesh moved(std::move(source));
    target = std::move(moved);
    auto* alias = &target;
    target = std::move(*alias);
    moves = source.GetPatch() == &*first && moved.GetPatch() == &*first &&
            target.GetPatch() == &*first && first->GetSubMesh() == &source &&
            second->GetSubMesh() == &target;
    second.reset();
    moves = moves && target.GetPatch() == &*first;
    first.reset();
    moves = moves && source.GetPatch() == nullptr && moved.GetPatch() == nullptr &&
            target.GetPatch() == nullptr;
  }
  {
    SubMesh first_mesh, second_mesh;
    std::optional<Patch> first(std::in_place), second(std::in_place);
    first->SetId(17);
    first_mesh.SetPatch(&*first);
    first->SetSubMesh(&first_mesh);
    second_mesh.SetPatch(&*second);
    Patch copied(&*first);
    Patch moved(std::move(*first));
    *second = std::move(moved);
    auto* alias = &*second;
    *second = std::move(*alias);
    patch_moves = copied.GetId() == 17 && copied.GetSubMesh() == nullptr && second->GetId() == 17 &&
                  second->GetSubMesh() == &first_mesh && first_mesh.GetPatch() == &*first &&
                  second_mesh.GetPatch() == &*second;
    first.reset();
    patch_moves =
        patch_moves && first_mesh.GetPatch() == nullptr && second_mesh.GetPatch() == &*second;
    second.reset();
    patch_moves = patch_moves && second_mesh.GetPatch() == nullptr;
  }
  std::printf("patch_observers mesh_first:%d patch_first:%d history:%d rebind:%d "
              "foreign:%d moves:%d patch_moves:%d\n",
              mesh_first, patch_first, history, rebind, foreign, moves, patch_moves);
  return mesh_first && patch_first && history && rebind && foreign && moves && patch_moves;
}

// Extend the existing foreign-forward and object-move arrangements through
// retirement of the observed mesh; neither direction implies the other.
bool CheckForwardPatchObservers() {
  bool single = false, shared = false, rebind = false, patch_first = false;
  bool patch_moves = false, mesh_moves = false;
  {
    Patch patch;
    std::optional<SubMesh> mesh(std::in_place);
    patch.SetSubMesh(&*mesh);
    single = mesh->GetPatch() == nullptr;
    mesh.reset();
    single = single && patch.GetSubMesh() == nullptr;
  }
  {
    SubMesh unrelated;
    std::array<Patch, 4> patches;
    std::optional<SubMesh> mesh(std::in_place);
    for (auto& patch : patches)
      patch.SetSubMesh(&*mesh);
    patches[1].SetSubMesh(nullptr);
    patches[2].SetSubMesh(&unrelated);
    mesh.reset();
    shared = patches[0].GetSubMesh() == nullptr && patches[1].GetSubMesh() == nullptr &&
             patches[2].GetSubMesh() == &unrelated && patches[3].GetSubMesh() == nullptr;
  }
  {
    Patch patch;
    std::optional<SubMesh> first(std::in_place), second(std::in_place);
    patch.SetSubMesh(&*first);
    patch.SetSubMesh(&*first);
    patch.SetSubMesh(&*second);
    first.reset();
    rebind = patch.GetSubMesh() == &*second;
    second.reset();
    rebind = rebind && patch.GetSubMesh() == nullptr;
    patch.SetSubMesh(nullptr);
    patch.SetSubMesh(nullptr);
  }
  {
    std::array<std::optional<Patch>, 3> patches;
    std::optional<SubMesh> mesh(std::in_place);
    for (auto& patch : patches) {
      patch.emplace();
      patch->SetSubMesh(&*mesh);
    }
    patches[0].reset();
    patches[2].reset();
    patch_first = patches[1]->GetSubMesh() == &*mesh;
    mesh.reset();
    patch_first = patch_first && patches[1]->GetSubMesh() == nullptr;
  }
  {
    std::optional<SubMesh> first_mesh(std::in_place), second_mesh(std::in_place);
    Patch first, second;
    first.SetId(17);
    first.SetSubMesh(&*first_mesh);
    second.SetSubMesh(&*second_mesh);
    Patch detached(&first);
    Patch moved(std::move(first));
    second = std::move(moved);
    auto* alias = &second;
    second = std::move(*alias);
    patch_moves = detached.GetSubMesh() == nullptr && second.GetId() == 17 &&
                  first.GetSubMesh() == &*first_mesh && moved.GetSubMesh() == &*first_mesh &&
                  second.GetSubMesh() == &*first_mesh;
    second_mesh.reset();
    patch_moves = patch_moves && second.GetSubMesh() == &*first_mesh;
    first_mesh.reset();
    patch_moves = patch_moves && first.GetSubMesh() == nullptr && moved.GetSubMesh() == nullptr &&
                  second.GetSubMesh() == nullptr;
  }
  {
    Patch first, second;
    std::optional<SubMesh> source(std::in_place), target(std::in_place);
    source->SetPatch(&first);
    target->SetPatch(&second);
    first.SetSubMesh(&*source);
    second.SetSubMesh(&*target);
    SubMesh moved(std::move(*source));
    *target = std::move(moved);
    mesh_moves = first.GetSubMesh() == &*source && second.GetSubMesh() == &*target;
    source.reset();
    mesh_moves = mesh_moves && first.GetSubMesh() == nullptr && second.GetSubMesh() == &*target;
    target.reset();
    mesh_moves = mesh_moves && second.GetSubMesh() == nullptr;
  }
  std::printf("forward_patch_observers single:%d shared:%d rebind:%d patch_first:%d "
              "patch_moves:%d mesh_moves:%d\n",
              single, shared, rebind, patch_first, patch_moves, mesh_moves);
  return single && shared && rebind && patch_first && patch_moves && mesh_moves;
}

#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0;
int AllocationHook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC || kind == _HOOK_REALLOC) {
    ++attempts;
    ++denied;
    return 0;
  }
  return 1;
}
class AllocationScope {
public:
  AllocationScope() {
    attempts = denied = 0;
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};
#endif

bool ExternalNodes() {
  for (bool populated : {false, true}) {
    Lifetime previous, borrowed;
    borrowed.read_observers = true;
    {
      std::array<std::unique_ptr<CountedNode>, 3> nodes;
      for (int i = 0; i < 3; ++i)
        nodes[i] = std::make_unique<CountedNode>(borrowed, i);
      {
        SubMesh incoming;
        auto element = std::make_unique<CountedTriangle>(borrowed, nodes[0].get(), nodes[1].get(),
                                                         nodes[2].get());
        auto* identity = element.get();
        incoming.AddElement(std::move(element));
        {
          SubMesh target;
          if (populated)
            Populate(target, previous, 2);
          target = std::move(incoming);
          Require(previous.Complete(), "replaced local graph retires before external borrowing");
          Require(target.GetNumberNos() == 0 && target.GetNumberElements() == 1 &&
                      target.GetElement(0) == identity && identity->GetArea() == 0.5,
                  "external-node move preserves actual element identity and analytic area");
          for (const auto& node : nodes)
            Require(node->GetNumberElements() == 1 && node->GetElement(0) == identity,
                    "live external nodes observe the moved element once");
        }
        Require(borrowed.elements == 1 && borrowed.nodes == 0,
                "borrowed nodes survive element teardown");
        for (const auto& node : nodes)
          Require(node->GetNumberElements() == 0,
                  "element teardown retires external-node observations");
      }
    }
    Require(borrowed.Complete(), "independent node owner retires after its borrowing element");
    std::printf("external_nodes populated:%d identity:1 adjacency:1 complete:1\n", populated);
  }
  return true;
}

bool ExpiredReplacementControl() {
  Lifetime previous;
  SubMesh target, incoming;
  Populate(target, previous, 2);
  // Deliberately violate the documented independently-live-node precondition.
  incoming.AddElement(
      std::make_unique<TriangleAdaptive>(target.GetNoh(0), target.GetNoh(1), target.GetNoh(2)));
  target = std::move(incoming);
  return true;
}

bool Run(const char* mode) {
  if (std::strcmp(mode, "external-nodes") == 0)
    return ExternalNodes();
  if (std::strcmp(mode, "replaced-node-borrow") == 0)
    return ExpiredReplacementControl();
  if (std::strcmp(mode, "patch-observers") == 0)
    return CheckPatchObservers();
  if (std::strcmp(mode, "forward-patch-observers") == 0)
    return CheckForwardPatchObservers();
  if (std::strcmp(mode, "contracts") == 0) {
    bool passed = CheckPatchObservers() && ExternalNodes();
    for (int i = 0; i < 8; ++i) {
      Fixture fixture(i);
      passed = fixture.Exercise() && passed;
    }
    return CheckForwardPatchObservers() && passed;
  }
  if (std::strncmp(mode, "normal-", 7) == 0) {
    int variant = -1;
    Require(std::sscanf(mode, "normal-%d", &variant) == 1 && variant >= 0 && variant < 8,
            "valid normal variant");
    Fixture fixture(variant);
    return fixture.Exercise();
  }
  if (std::strcmp(mode, "observer-read") == 0) {
    Fixture fixture(3, true);
    return fixture.Exercise();
  }
  if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strcmp(mode, "patch-noalloc") == 0) {
    bool passed;
    {
      AllocationScope hook;
      passed = CheckPatchObservers();
    }
    std::printf("patch_allocation=attempts:%d denied:%d\n", attempts, denied);
    return passed && attempts == 0 && denied == 0;
  } else if (std::strcmp(mode, "forward-patch-noalloc") == 0) {
    bool passed;
    {
      AllocationScope hook;
      passed = CheckForwardPatchObservers();
    }
    std::printf("forward_patch_allocation=attempts:%d denied:%d\n", attempts, denied);
    return passed && attempts == 0 && denied == 0;
  } else if (std::strncmp(mode, "noalloc-", 8) == 0) {
    int variant = -1;
    Require(std::sscanf(mode, "noalloc-%d", &variant) == 1 && variant >= 0 && variant < 8,
            "valid no-allocation variant");
    Fixture fixture(variant);
    bool passed;
    {
      AllocationScope hook;
      passed = fixture.Exercise();
    }
    std::printf("submesh_allocation=attempts:%d denied:%d\n", attempts, denied);
    return passed && attempts == 0 && denied == 0;
  } else if (std::strcmp(mode, "allocation-hook-control") == 0) {
    bool caught = false;
    {
      AllocationScope hook;
      try {
        auto node = std::make_unique<NodeAdaptive>();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && attempts == 1 && denied == 1, "actual allocation denial control");
    std::puts("allocation_hook_control=detected");
#endif
  } else
    Require(false, "unknown mode");
  return true;
}
} // namespace

int main(int argc, char** argv) {
  Require(argc == 2, "one mode required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  bool passed = Run(argv[1]);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  passed = passed && delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0;
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
