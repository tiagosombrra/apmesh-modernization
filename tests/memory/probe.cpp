#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double EPSYLON = 1e-8;
double TOLERANCE = 1e-8;

namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}

class CountedNode : public NodeAdaptive {
public:
  explicit CountedNode(int& destroyed) : destroyed_(destroyed) {}
  ~CountedNode() override { ++destroyed_; }

private:
  int& destroyed_;
};

void contracts() {
  for (int iteration = 0; iteration < 200; ++iteration) {
    SubMesh first;
    SubMesh second;
    {
      NodeAdaptive source(1.0, 2.0, 3.0, 42);
      source.SetGa(4.0);
      source.SetGd(5.0);
      source.SetHa(6.0);
      source.SetHd(7.0);
      NodeAdaptive b(2.0, 2.0, 3.0);
      NodeAdaptive c(1.0, 3.0, 3.0);
      TriangleAdaptive original(&source, &b, &c);
      first.SetNoh(&source);
      second.SetNoh(&source);
      first.SetNoh(nullptr);
      require(first.GetNumberNos() == 1, "null copy is ignored");
      auto* copy = first.GetNoh(0);
      require(copy != &source && copy != second.GetNoh(0), "independent identity");
      require(copy->GetId() == 42 && copy->GetX() == 1.0 && copy->GetY() == 2.0 &&
                  copy->GetZ() == 3.0,
              "ID and physical position preserved");
      require(copy->GetGa() == 4.0 && copy->GetGd() == 5.0 && copy->GetHa() == 6.0 &&
                  copy->GetHd() == 7.0,
              "curvature state preserved");
      require(source.GetNumberElements() == 1 && source.GetElement(0) == &original,
              "source adjacency untouched");
      require(copy->GetNumberElements() == 0 && second.GetNoh(0)->GetNumberElements() == 0,
              "copied node starts without foreign element observers");
      source.SetX(99.0);
      require(copy->GetX() == 1.0, "independent scalar storage");
    }
    require(first.GetNoh(0)->GetNumberElements() == 0, "source destruction is safe");
    first.AddNoh(std::make_unique<NodeAdaptive>(2.0, 2.0, 3.0));
    first.AddNoh(std::make_unique<NodeAdaptive>(1.0, 3.0, 3.0));
    auto local =
        std::make_unique<TriangleAdaptive>(first.GetNoh(0), first.GetNoh(1), first.GetNoh(2));
    auto* element = local.get();
    first.AddElement(std::move(local));
    require(first.GetNoh(0)->GetNumberElements() == 1 && first.GetNoh(0)->GetElement(0) == element,
            "local triangle rebuilds adjacency");
    require(element->GetArea() == 0.5, "local geometry preserved");
    SubMesh moved(std::move(first));
    require(moved.GetElement(0) == element && moved.GetNoh(0)->GetElement(0) == element,
            "move preserves owned addresses");
    second = std::move(moved);
    require(second.GetNumberNos() == 3 && second.GetElement(0) == element,
            "replacement transfers owned nodes and elements");
  }
  int destroyed = 0;
  {
    SubMesh owner;
    auto node = std::make_unique<CountedNode>(destroyed);
    auto* identity = node.get();
    owner.AddNoh(std::move(node));
    require(!node && owner.GetNoh(0) == identity, "unique adoption preserves identity");
  }
  require(destroyed == 1, "adopted node destroyed exactly once");
}

// Deliberately broken controls must run in separate processes.
void broken(const char* mode) {
  if (std::strcmp(mode, "expired-copy") == 0) {
    SubMesh destination;
    NodeAdaptive a(0, 0, 0), b(1, 0, 0), c(0, 1, 0);
    auto source = std::make_unique<TriangleAdaptive>(&a, &b, &c);
    destination.SetNoh(&a);
    source.reset();
    auto* copy = destination.GetNoh(0);
    if (copy->GetNumberElements() != 0) {
      std::printf("expired-area=%g\n", copy->GetElement(0)->GetArea());
    }
  } else if (std::strcmp(mode, "leak") == 0) {
    auto* leaked = new NodeAdaptive(1, 2, 3);
    std::printf("deliberate-leak=%p\n", static_cast<void*>(leaked));
  } else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "double-free") == 0) {
    auto* data = static_cast<int*>(std::malloc(64));
    std::free(data);
    std::free(data);
  } else {
    require(false, "unknown mode");
  }
}
} // namespace

int main(int argc, char** argv) {
  require(argc == 2, "one mode required");
  std::puts("Node lifetime diagnostic");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  if (std::strcmp(argv[1], "contracts") == 0) {
    contracts();
  } else {
    broken(argv[1]);
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  const auto blocks = delta.lCounts[_NORMAL_BLOCK];
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", blocks, delta.lSizes[_NORMAL_BLOCK]);
  if (blocks != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    return 1;
  }
#endif
  std::puts("PASS");
}
