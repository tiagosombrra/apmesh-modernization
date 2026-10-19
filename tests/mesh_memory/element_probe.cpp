#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Element adoption contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Counts {
  int nodes = 0, prior = 0, argument = 0;
  bool ordered = true;
};

class CountedNode final : public NodeAdaptive {
public:
  CountedNode(Counts& counts, double x, double y) : NodeAdaptive(x, y, 0), counts_(counts) {}
  ~CountedNode() override { ++counts_.nodes; }

private:
  Counts& counts_;
};

class CountedTriangle final : public TriangleAdaptive {
public:
  CountedTriangle(Counts& counts, bool argument, NodeAdaptive* a, NodeAdaptive* b, NodeAdaptive* c)
      : TriangleAdaptive(a, b, c), counts_(counts), argument_(argument) {}
  ~CountedTriangle() override {
    counts_.ordered = counts_.ordered && counts_.nodes == 0;
    if (argument_)
      ++counts_.argument;
    else
      ++counts_.prior;
  }

private:
  Counts& counts_;
  bool argument_;
};

struct Fixture {
  Counts& counts;
  SubMesh mesh;
  std::unique_ptr<ElementAdaptive> pending;
  ElementAdaptive* identity = nullptr;
  NodeAdaptive* nodes[3]{};
  ElementAdaptive* prior[64]{};
  int variant, prefix;
  Fixture(Counts& state, int mode, int existing) : counts(state), variant(mode), prefix(existing) {
    Require(existing >= 0 && existing <= 64 && mode >= 0 && mode < 8, "bounded fixture");
    mesh.AddNoh(std::make_unique<CountedNode>(counts, 0, 0));
    mesh.AddNoh(std::make_unique<CountedNode>(counts, 1, 0));
    mesh.AddNoh(std::make_unique<CountedNode>(counts, 0, 1));
    for (unsigned int i = 0; i < 3; ++i) {
      nodes[i] = mesh.GetNoh(i);
      nodes[i]->SetId(i + 10);
    }
    for (int i = 0; i < prefix; ++i) {
      auto triangle = MakeTriangle(false, 100 + i);
      prior[i] = triangle.get();
      mesh.AddElement(std::move(triangle));
    }
    if (NonNull())
      pending = MakeTriangle(true, 900);
    identity = pending.get();
  }
  bool NonNull() const { return variant % 4 < 2; }
  bool Owning() const { return variant >= 4; }
  std::unique_ptr<ElementAdaptive> MakeTriangle(bool argument, unsigned long id) {
    auto triangle =
        std::make_unique<CountedTriangle>(counts, argument, nodes[0], nodes[1], nodes[2]);
    triangle->SetId(id);
    triangle->SetParametersN1({0, 0});
    triangle->SetParametersN2({1, 0});
    triangle->SetParametersN3({0, 1});
    return triangle;
  }
  void Insert() {
    if (Owning())
      mesh.AddElement(std::move(pending));
    else
      mesh.SetElement(pending.release());
  }
  void PrefixOnly() {
    Require(mesh.GetNumberElements() == static_cast<unsigned int>(prefix),
            "failure preserves owned element slots");
    Require(counts.nodes == 0 && counts.prior == 0,
            "failure preserves existing node/element objects until terminal teardown");
    for (int i = 0; i < prefix; ++i)
      Require(mesh.GetElement(i) == prior[i] &&
                  prior[i]->GetId() == static_cast<unsigned long>(100 + i) &&
                  prior[i]->GetArea() == 0.5,
              "existing ordered element identity and analytic area");
    for (unsigned int i = 0; i < 3; ++i) {
      Require(mesh.GetNoh(i) == nodes[i] && nodes[i]->GetId() == i + 10,
              "existing node identity and ID");
      Require(nodes[i]->GetNumberElements() == static_cast<unsigned int>(prefix),
              "consumed argument destruction removes its observers before failure handling");
      for (int j = 0; j < prefix; ++j)
        Require(nodes[i]->GetElement(j) == prior[j], "existing adjacency prefix is preserved");
      // The exact prefix contains only live owners and may be consumed safely.
    }
  }
  void Validate(SubMesh& current, bool trace) {
    Require(current.GetNumberNos() == 3 &&
                current.GetNumberElements() == static_cast<unsigned int>(prefix + 1),
            "append retains three nodes and ordered slots, including null");
    Require(current.GetElement(prefix) == identity,
            "raw and owning APIs preserve adopted identity");
    for (int i = 0; i <= prefix; ++i) {
      auto* element = current.GetElement(i);
      if (i < prefix)
        Require(element == prior[i], "previous element identity and order");
      if (element) {
        Require(element->GetId() == static_cast<unsigned long>(i < prefix ? 100 + i : 900) &&
                    element->GetArea() == 0.5,
                "ordered IDs and independent analytic area");
        auto* triangle = static_cast<TriangleAdaptive*>(element);
        Require(triangle->GetParametersN1() == std::make_tuple(0.0, 0.0) &&
                    triangle->GetParametersN2() == std::make_tuple(1.0, 0.0) &&
                    triangle->GetParametersN3() == std::make_tuple(0.0, 1.0),
                "ordered UV parameters");
        if (trace)
          std::printf("element_triangle=slot:%d id:%lu area:%.1f\n", i, element->GetId(),
                      element->GetArea());
      }
    }
    for (unsigned int i = 0; i < 3; ++i) {
      auto* node = current.GetNoh(i);
      Require(node == nodes[i] && node->GetId() == i + 10 && node->GetX() == (i == 1 ? 1 : 0) &&
                  node->GetY() == (i == 2 ? 1 : 0) && node->GetZ() == 0,
              "independent coordinates and stable node identity");
      const int adjacent = prefix + (NonNull() ? 1 : 0);
      Require(node->GetNumberElements() == static_cast<unsigned int>(adjacent),
              "exact successful adjacency count");
      for (int j = 0; j < adjacent; ++j)
        Require(node->GetElement(j) == (j < prefix ? prior[j] : identity),
                "exact successful adjacency ordering");
      if (trace)
        std::printf("element_node=index:%u id:%lu xyz:%.1f,%.1f,%.1f adjacency:%d\n", i,
                    node->GetId(), node->GetX(), node->GetY(), node->GetZ(), adjacent);
    }
    if (trace)
      std::printf("element_observed=variant:%d prefix:%d slots:%d nonnull:%d\n", variant, prefix,
                  prefix + 1, NonNull());
  }
};

// The fixture owner unwinds before the driver handles a terminal exception.
void Operation(std::unique_ptr<Fixture> fixture, bool trace) {
  try {
    fixture->Insert();
  } catch (...) {
    fixture->PrefixOnly();
    throw;
  }
  fixture->Validate(fixture->mesh, trace);
  if (trace) {
    SubMesh moved(std::move(fixture->mesh));
    fixture->Validate(moved, false);
  }
}

bool Complete(const Counts& counts, int prefix, bool argument) {
  return counts.nodes == 3 && counts.prior == prefix && counts.argument == (argument ? 1 : 0) &&
         counts.ordered;
}

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

int MeasuredPrefix(bool growth) {
  SubMesh mesh;
  for (int prefix = 0; prefix < 64; ++prefix) {
    {
      AllocationScope hook(-1);
      mesh.AddElement(nullptr);
    }
    if (prefix > 0 && (attempts > 0) == growth)
      return prefix;
  }
  Require(false, "qualified toolchain must expose measured populated growth/spare storage");
  return -1;
}

bool Failures(int variant) {
  const int prefix = variant % 2 == 0 ? 0 : MeasuredPrefix(true);
  int total;
  {
    Counts counts;
    auto fixture = std::make_unique<Fixture>(counts, variant, prefix);
    {
      AllocationScope hook(-1);
      Operation(std::move(fixture), false);
      total = attempts;
    }
    Require(Complete(counts, prefix, variant % 4 < 2),
            "calibration destroys every owned object in order");
  }
  Require(total > 0, "positive actual storage-growth calibration");
  std::printf("element_measured=variant:%d prefix:%d allocations:%d\n", variant, prefix, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Counts counts;
    bool caught = false;
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    {
      auto fixture = std::make_unique<Fixture>(counts, variant, prefix);
      AllocationScope hook(ordinal);
      try {
        Operation(std::move(fixture), false);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    Require(caught && denied == 1 && attempts == ordinal + 1,
            "one denial propagates through allocation-free terminal owner unwinding");
    const auto blocks = delta.lCounts[_NORMAL_BLOCK];
    const bool complete = Complete(counts, prefix, variant % 4 < 2);
    std::printf(
        "element_denied=variant:%d ordinal:%d attempts:%d complete:%d retained:%zu bytes:%zu\n",
        variant, ordinal, attempts, complete, blocks, delta.lSizes[_NORMAL_BLOCK]);
    if (!complete || blocks != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("element_failure_sites=variant:%d denied:%d/%d\n", variant, total, total);
  return true;
}

bool NoAllocation(int variant) {
  const int prefix = MeasuredPrefix(false);
  Counts counts;
  auto fixture = std::make_unique<Fixture>(counts, variant, prefix);
  {
    AllocationScope hook(0);
    Operation(std::move(fixture), false);
  }
  Require(attempts == 0 && denied == 0 && Complete(counts, prefix, variant % 4 < 2),
          "spare-storage insertion and terminal destruction do not allocate");
  std::printf("element_noalloc=variant:%d prefix:%d attempts:0\n", variant, prefix);
  return true;
}
#endif

bool Normal(int variant) {
  const int prefix = variant % 2;
  Counts counts;
  Operation(std::make_unique<Fixture>(counts, variant, prefix), true);
  return Complete(counts, prefix, variant % 4 < 2);
}

bool Run(const char* mode) {
  if (std::strcmp(mode, "contracts") == 0) {
    for (int variant = 0; variant < 8; ++variant)
      if (!Normal(variant))
        return false;
  } else if (std::strncmp(mode, "normal-", 7) == 0)
    return Normal(std::atoi(mode + 7));
  else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strncmp(mode, "failure-", 8) == 0)
    return Failures(std::atoi(mode + 8));
  else if (std::strncmp(mode, "noalloc-", 8) == 0)
    return NoAllocation(std::atoi(mode + 8));
  else if (std::strcmp(mode, "allocation-hook-control") == 0) {
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
