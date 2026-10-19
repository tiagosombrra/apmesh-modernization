#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Triangle construction contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Fixture {
  NodeAdaptive a{0, 0, 0}, b{1, 0, 0}, c{0, 1, 0};
  std::array<NodeAdaptive*, 3> nodes{&a, &b, &c};
  std::array<NodeAdaptive*, 3> vertices{};
  std::array<std::unique_ptr<TriangleAdaptive>, 2> prior;
  std::unique_ptr<TriangleAdaptive> pending;
  std::array<std::array<const void*, 3>, 3> slots{};
  int shape, layout, prefix;
  Fixture(int kind, int seeded) : shape(kind), layout(seeded), prefix(seeded ? 3 : 0) {
    Require(kind >= 0 && kind < 6 && seeded >= 0 && seeded < 2, "bounded fixture");
    const int indices[6][3]{{0, 1, 2}, {0, 0, 2}, {0, 1, 1}, {0, 0, 0}, {0, 1, 0}, {2, 1, 0}};
    for (unsigned int i = 0; i < 3; ++i) {
      vertices[i] = nodes[indices[kind][i]];
      nodes[i]->SetId(10 + i);
      nodes[i]->SetGa(20 + i);
      nodes[i]->SetGd(30 + i);
      nodes[i]->SetHa(40 + i);
      nodes[i]->SetHd(50 + i);
    }
    if (seeded) {
      prior[0] = std::make_unique<TriangleAdaptive>(&a, &b, &c);
      prior[0]->SetId(70);
      for (auto* node : nodes)
        node->InsertElement(nullptr);
      prior[1] = std::make_unique<TriangleAdaptive>(&c, &b, &a);
      prior[1]->SetId(71);
      for (unsigned int n = 0; n < 3; ++n) {
        unsigned int index = 0;
        for (const auto& entry : nodes[n]->GetElements())
          slots[n][index++] = &entry;
      }
    }
  }
  void Construct() {
    pending = std::make_unique<TriangleAdaptive>(vertices[0], vertices[1], vertices[2]);
    pending->SetId(900);
  }
  bool Restored() const {
    if (pending)
      return false;
    for (unsigned int n = 0; n < 3; ++n) {
      const auto* node = nodes[n];
      if (node->GetNumberElements() != static_cast<unsigned int>(prefix) ||
          node->GetId() != n + 10 || node->GetX() != (n == 1 ? 1 : 0) ||
          node->GetY() != (n == 2 ? 1 : 0) || node->GetZ() != 0 || node->GetGa() != n + 20 ||
          node->GetGd() != n + 30 || node->GetHa() != n + 40 || node->GetHd() != n + 50)
        return false;
      unsigned int index = 0;
      for (const auto& entry : node->GetElements()) {
        const ElementAdaptive* expected =
            index == 0 ? prior[0].get() : (index == 1 ? nullptr : prior[1].get());
        if (entry != expected || &entry != slots[n][index++])
          return false;
      }
    }
    return true;
  }
  void ConsumeRestored() const {
    Require(Restored(), "only exact restored live observer lists can be consumed");
    for (auto* node : nodes) {
      for (auto* element : node->GetElements()) {
        if (element)
          Require(element->GetArea() == 0.5 && (element->GetId() == 70 || element->GetId() == 71),
                  "restored observers refer to live analytic parent triangles");
      }
    }
  }
  void Validate(bool trace) const {
    Require(pending && pending->GetId() == 900, "complete constructed triangle");
    Require(pending->GetArea() == (shape == 0 || shape == 5 ? 0.5 : 0.0),
            "independent analytic area, including degenerate alias guards");
    for (unsigned int n = 0; n < 3; ++n) {
      auto* node = nodes[n];
      unsigned int added = 0;
      for (auto* vertex : vertices)
        if (vertex == node)
          ++added;
      Require(node->GetNumberElements() == static_cast<unsigned int>(prefix) + added,
              "exact registration multiplicity");
      unsigned int index = 0;
      for (const auto& entry : node->GetElements()) {
        if (index < static_cast<unsigned int>(prefix)) {
          auto* expected = index == 0 ? prior[0].get() : (index == 1 ? nullptr : prior[1].get());
          Require(entry == expected && &entry == slots[n][index],
                  "prior ordered observer values and list-node identities");
        } else
          Require(entry == pending.get(), "new observer identity in vertex order");
        ++index;
      }
      if (trace)
        std::printf("triangle_node=index:%u id:%lu adjacency:%u added:%u\n", n, node->GetId(),
                    node->GetNumberElements(), added);
    }
    if (trace)
      std::printf("triangle_observed=shape:%d layout:%d area:%.17g angles:%.17g,%.17g,%.17g\n",
                  shape, layout, pending->GetArea(), pending->CalculateAngleN1(),
                  pending->CalculateAngleN2(), pending->CalculateAngleN3());
  }
};

#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
int AllocationHook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC || kind == _HOOK_REALLOC) {
    ++attempts;
    if (fail_after-- == 0) {
      ++denied;
      return 0;
    }
  }
  return 1;
}
class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    attempts = denied = 0;
    fail_after = ordinal;
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};

bool Failures(int shape, int layout) {
  int total;
  {
    Fixture fixture(shape, layout);
    {
      AllocationScope hook(-1);
      fixture.Construct();
      total = attempts;
    }
    fixture.Validate(false);
  }
  Require(total > 0, "positive actual constructor allocation calibration");
  std::printf("triangle_measured=shape:%d layout:%d allocations:%d\n", shape, layout, total);
  bool all_restored = true;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Fixture fixture(shape, layout);
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        fixture.Construct();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && denied == 1 && attempts == ordinal + 1,
            "one denial propagates without a rollback allocation");
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    const bool restored = fixture.Restored();
    const auto blocks = delta.lCounts[_NORMAL_BLOCK];
    bool fresh = false;
    if (restored) {
      fixture.ConsumeRestored();
      fixture.Construct();
      fixture.Validate(false);
      fresh = true;
    }
    // An original partial publication is measured without consuming its expired entries.
    std::printf("triangle_denied=shape:%d layout:%d ordinal:%d attempts:%d restored:%d "
                "live_blocks:%zu live_bytes:%zu fresh:%d\n",
                shape, layout, ordinal, attempts, restored, blocks, delta.lSizes[_NORMAL_BLOCK],
                fresh);
    all_restored = all_restored && restored && blocks == 0 && delta.lSizes[_NORMAL_BLOCK] == 0;
  }
  std::printf("triangle_failure_sites=shape:%d layout:%d denied:%d/%d restored:%d\n", shape, layout,
              total, total, all_restored);
  return all_restored;
}
#endif

bool Run(const char* mode) {
  if (std::strcmp(mode, "contracts") == 0) {
    for (int shape = 0; shape < 6; ++shape)
      for (int layout = 0; layout < 2; ++layout) {
        Fixture fixture(shape, layout);
        fixture.Construct();
        fixture.Validate(true);
      }
  } else if (std::strncmp(mode, "normal-", 7) == 0) {
    int shape = -1, layout = -1;
    Require(std::sscanf(mode, "normal-%d-%d", &shape, &layout) == 2,
            "normal shape/layout required");
    Fixture fixture(shape, layout);
    fixture.Construct();
    fixture.Validate(true);
  } else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strncmp(mode, "failure-", 8) == 0) {
    int shape = -1, layout = -1;
    Require(std::sscanf(mode, "failure-%d-%d", &shape, &layout) == 2,
            "failure shape/layout required");
    return Failures(shape, layout);
  } else if (std::strcmp(mode, "allocation-hook-control") == 0) {
    bool caught = false;
    {
      AllocationScope hook(0);
      try {
        auto node = std::make_unique<NodeAdaptive>();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && denied == 1 && attempts == 1, "actual CRT denial control");
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
