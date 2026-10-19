#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <tuple>
#include <type_traits>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Triangle observer contract failed: %s\n", message);
    std::exit(1);
  }
}

class ObservedTriangle final : public TriangleAdaptive {
public:
  using TriangleAdaptive::TriangleAdaptive;
  NodeAdaptive* Vertex(int index) const { return index == 0 ? n1_ : (index == 1 ? n2_ : n3_); }
  std::array<double, 7> Cache() const {
    return {angle_n1_,
            angle_n2_,
            angle_n3_,
            area_,
            vector_normal_.GetX(),
            vector_normal_.GetY(),
            vector_normal_.GetZ()};
  }
  bool HasCache(const std::array<double, 7>& expected) const {
    const auto current = Cache();
    return std::memcmp(current.data(), expected.data(), 7 * sizeof(double)) == 0;
  }
};

struct Entry {
  ElementAdaptive* value = nullptr;
  const void* identity = nullptr;
};
struct Lists {
  std::array<std::array<Entry, 8>, 4> entries{};
  std::array<unsigned int, 4> sizes{};
  explicit Lists(const std::array<NodeAdaptive*, 4>& nodes) {
    for (unsigned int n = 0; n < 4; ++n)
      for (const auto& entry : nodes[n]->GetElements()) {
        Require(sizes[n] < 8, "bounded adjacency fixture");
        entries[n][sizes[n]++] = {entry, &entry};
      }
  }
  void Transfer(unsigned int from, unsigned int to, ElementAdaptive* element) {
    for (unsigned int i = 0; i < sizes[from]; ++i) {
      if (entries[from][i].value == element) {
        Require(sizes[to] < 8, "bounded destination fixture");
        entries[to][sizes[to]++] = entries[from][i];
        for (unsigned int j = i + 1; j < sizes[from]; ++j)
          entries[from][j - 1] = entries[from][j];
        --sizes[from];
        return;
      }
    }
    Require(false, "oracle transfer must find an existing registration");
  }
  bool Matches(const std::array<NodeAdaptive*, 4>& nodes) const {
    for (unsigned int n = 0; n < 4; ++n) {
      if (nodes[n]->GetNumberElements() != sizes[n])
        return false;
      unsigned int i = 0;
      for (const auto& entry : nodes[n]->GetElements()) {
        if (entry != entries[n][i].value || &entry != entries[n][i].identity)
          return false;
        ++i;
      }
    }
    return true;
  }
};

struct Fixture {
  NodeAdaptive a{0, 0, 0}, b{1, 0, 0}, c{0, 1, 0}, d{2, 3, 1};
  std::array<NodeAdaptive*, 4> nodes{&a, &b, &c, &d};
  std::array<std::unique_ptr<TriangleAdaptive>, 2> parents;
  std::unique_ptr<ObservedTriangle> triangle;
  std::array<unsigned int, 3> vertices{0, 1, 2};
  int variant;
  explicit Fixture(int mode) : variant(mode) {
    Require(mode >= 0 && mode < 10, "bounded replacement variant");
    for (unsigned int n = 0; n < 4; ++n) {
      nodes[n]->SetId(40 + n);
      nodes[n]->SetGa(10 + n);
      nodes[n]->SetGd(20 + n);
      nodes[n]->SetHa(30 + n);
      nodes[n]->SetHd(50 + n);
    }
    parents[0] = std::make_unique<TriangleAdaptive>(&a, &b, &c);
    for (auto* node : nodes)
      node->InsertElement(nullptr);
    parents[1] = std::make_unique<TriangleAdaptive>(&d, &b, &c);
    for (auto* node : nodes)
      node->InsertElement(nullptr);
    if (mode == 3)
      vertices = {0, 0, 2};
    if (mode == 4)
      vertices = {0, 0, 0};
    triangle = std::make_unique<ObservedTriangle>(nodes[vertices[0]], nodes[vertices[1]],
                                                  nodes[vertices[2]]);
    triangle->SetId(700);
    triangle->SetParametersN1({0.125, 0.25});
    triangle->SetParametersN2({0.5, 0.625});
    triangle->SetParametersN3({0.75, 0.875});
    Require(triangle->GetArea() == (mode == 3 || mode == 4 ? 0.0 : 0.5),
            "independent initial analytic area");
    if (mode == 8)
      a.RemoveElementObserver(triangle.get());
  }
  bool Exercise() {
    Lists expected(nodes);
    const auto cache = triangle->Cache();
    const auto from = static_cast<unsigned int>(variant == 1 ? 1 : (variant == 2 ? 2 : 0));
    const auto to = static_cast<unsigned int>(variant == 5 ? 1 : (variant == 6 ? 0 : 3));
    const auto slot = from;
    NodeAdaptive* old_node = variant == 7 ? &d : nodes[from];
    NodeAdaptive* new_node = variant == 9 ? nullptr : nodes[to];
    bool rejected = false;
    try {
      triangle->ReplaceNode(old_node, new_node);
    } catch (const std::logic_error& error) {
      rejected = (variant == 8 && dynamic_cast<const std::invalid_argument*>(&error) == nullptr) ||
                 (variant == 9 && dynamic_cast<const std::invalid_argument*>(&error) != nullptr);
    }
    if (variant < 6) {
      expected.Transfer(from, to, triangle.get());
      vertices[slot] = to;
    }
    bool passed = (variant < 8 ? !rejected : rejected) && expected.Matches(nodes) &&
                  triangle->HasCache(cache) && triangle->GetId() == 700 &&
                  triangle->GetParametersN1() == std::make_tuple(0.125, 0.25) &&
                  triangle->GetParametersN2() == std::make_tuple(0.5, 0.625) &&
                  triangle->GetParametersN3() == std::make_tuple(0.75, 0.875);
    for (unsigned int v = 0; v < 3; ++v)
      passed = passed && triangle->Vertex(v) == nodes[vertices[v]];
    for (unsigned int n = 0; n < 4; ++n)
      passed = passed && nodes[n]->GetId() == 40 + n && nodes[n]->GetGa() == 10 + n &&
               nodes[n]->GetGd() == 20 + n && nodes[n]->GetHa() == 30 + n &&
               nodes[n]->GetHd() == 50 + n;
    // Return to the original topology in successful transfer cases. A matching
    // observer value is never dereferenced after a failed original assertion.
    if (passed && variant < 6) {
      expected.Transfer(to, from, triangle.get());
      triangle->ReplaceNode(nodes[to], nodes[from]);
      // First-match replacement can target an earlier equal vertex after merging.
      unsigned int first = 0;
      while (vertices[first] != to)
        ++first;
      vertices[first] = from;
      passed = expected.Matches(nodes) && triangle->HasCache(cache);
      for (unsigned int v = 0; v < 3; ++v)
        passed = passed && triangle->Vertex(v) == nodes[vertices[v]];
    }
    std::printf("observer_replacement=variant:%d preserved:%d rejected:%d\n", variant, passed,
                rejected);
    return passed;
  }
};

template <class T> bool Identity() {
  constexpr bool copy = std::is_copy_constructible_v<T>;
  constexpr bool assign = std::is_copy_assignable_v<T>;
  constexpr bool move = std::is_move_constructible_v<T>;
  constexpr bool move_assign = std::is_move_assignable_v<T>;
  bool unregistered_copy = false;
  if constexpr (copy && move && assign && move_assign) {
    NodeAdaptive a(0, 0, 0), b(1, 0, 0), c(0, 1, 0);
    T original(&a, &b, &c);
    T copied(original);
    T moved(std::move(original));
    T assigned;
    assigned = original;
    T move_assigned;
    move_assigned = std::move(original);
    unregistered_copy = a.GetNumberElements() == 1 && a.GetElement(0) == &original &&
                        copied.GetArea() == 0.5 && moved.GetArea() == 0.5 &&
                        assigned.GetArea() == 0.5 && move_assigned.GetArea() == 0.5;
  }
  std::printf("observer_identity=copy:%d assign:%d move:%d move_assign:%d unregistered_copy:%d\n",
              copy, assign, move, move_assign, unregistered_copy);
  return !copy && !assign && !move && !move_assign;
}

bool Guards() {
  NodeAdaptive absent(0, 0, 0), incoming(1, 0, 0);
  ObservedTriangle empty;
  empty.ReplaceNode(&absent, nullptr);
  empty.ReplaceNode(nullptr, nullptr);
  bool rejected = false;
  try {
    empty.ReplaceNode(nullptr, &incoming);
  } catch (const std::logic_error&) {
    rejected = true;
  }
  const bool passed = rejected && empty.Vertex(0) == nullptr && empty.Vertex(1) == nullptr &&
                      empty.Vertex(2) == nullptr && incoming.GetNumberElements() == 0;
  std::printf("observer_guards=preserved:%d\n", passed);
  return passed;
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

int Variant(const char* mode, unsigned int prefix, int limit) {
  Require(std::strlen(mode) == prefix + 1 && mode[prefix] >= '0' && mode[prefix] < '0' + limit,
          "bounded single-digit mode");
  return mode[prefix] - '0';
}
bool Run(const char* mode) {
  if (std::strcmp(mode, "contracts") == 0) {
    bool passed = Identity<TriangleAdaptive>() && Guards();
    for (int variant = 0; variant < 10; ++variant) {
      Fixture fixture(variant);
      passed = fixture.Exercise() && passed;
    }
    return passed;
  }
  if (std::strncmp(mode, "normal-", 7) == 0) {
    Fixture fixture(Variant(mode, 7, 10));
    return fixture.Exercise();
  }
  if (std::strcmp(mode, "identity") == 0)
    return Identity<TriangleAdaptive>();
  if (std::strcmp(mode, "guards") == 0)
    return Guards();
  if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strncmp(mode, "noalloc-", 8) == 0) {
    Fixture fixture(Variant(mode, 8, 8));
    bool passed;
    {
      AllocationScope hook;
      passed = fixture.Exercise();
    }
    std::printf("observer_allocation=attempts:%d denied:%d\n", attempts, denied);
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
    Require(caught && attempts == 1 && denied == 1, "actual CRT denial control");
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
