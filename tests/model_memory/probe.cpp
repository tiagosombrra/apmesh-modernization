#include "data/model.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

#include <array>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <type_traits>
#include <utility>
#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#ifdef _WIN32
#include <windows.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Model ownership contract failed: %s\n", message);
    std::exit(2);
  }
}
struct Ledger {
  std::array<int, 32> nodes{}, triangles{}, order{};
  std::array<bool, 32> created{};
  int retired = 0;
};
class CountedNode final : public NodeAdaptive {
public:
  CountedNode(Ledger& ledger, int id, double x, double y)
      : NodeAdaptive(x, y, 0), ledger_(ledger), id_(id) {}
  ~CountedNode() override {
    Require(GetNumberElements() == 0, "triangle observers retired before nodes");
    ++ledger_.nodes[id_];
  }

private:
  Ledger& ledger_;
  int id_;
};
class CountedTriangle final : public TriangleAdaptive {
public:
  CountedTriangle(Ledger& ledger, int id, NodeAdaptive* a, NodeAdaptive* b, NodeAdaptive* c)
      : TriangleAdaptive(a, b, c), ledger_(ledger), id_(id) {}
  ~CountedTriangle() override {
    Require(ledger_.nodes[id_] == 0, "element retires before its live vertices");
    ++ledger_.triangles[id_];
    ledger_.order[ledger_.retired++] = id_;
  }

private:
  Ledger& ledger_;
  int id_;
};
std::unique_ptr<MeshAdaptive> Graph(Ledger& ledger, int id) {
  ledger.created[id] = true;
  auto mesh = std::make_unique<MeshAdaptive>();
  auto sub = std::make_unique<SubMesh>();
  sub->AddNoh(std::make_unique<CountedNode>(ledger, id, 0, 0));
  sub->AddNoh(std::make_unique<CountedNode>(ledger, id, 1, 0));
  sub->AddNoh(std::make_unique<CountedNode>(ledger, id, 0, 1));
  for (unsigned int i = 0; i < 3; ++i)
    sub->GetNoh(i)->SetId(static_cast<unsigned long>(10 * id) + i);
  sub->AddElement(std::make_unique<CountedTriangle>(ledger, id, sub->GetNoh(0), sub->GetNoh(1),
                                                    sub->GetNoh(2)));
  sub->GetElement(0)->SetId(static_cast<unsigned long>(id));
  mesh->InsertSubMeshAdaptive(sub.release());
  return mesh;
}
void Complete(const Ledger& ledger, int id) {
  Require(ledger.nodes[id] == 3 && ledger.triangles[id] == 1,
          "each owned payload retires exactly once");
}
void Live(Model& model, unsigned int position, MeshAdaptive* expected, int id, bool trace = false) {
  Require(expected && model.GetMeshAdaptive(position) == expected, "stored mesh identity");
  auto* sub = expected->GetSubMeshAdaptiveByPosition(0);
  Require(sub && sub->GetNumberNos() == 3 && sub->GetNumberElements() == 1,
          "complete owned payload");
  auto* triangle = sub->GetElement(0);
  Require(triangle->GetArea() == 0.5 && triangle->GetId() == static_cast<unsigned long>(id),
          "analytic area and element identity");
  for (unsigned int i = 0; i < 3; ++i) {
    auto* node = sub->GetNoh(i);
    Require(node->GetNumberElements() == 1 && node->GetElement(0) == triangle,
            "live triangle adjacency");
    Require(node->GetId() == static_cast<unsigned long>(10 * id) + i, "node ID unchanged");
    if (trace)
      std::printf("model_node=%u,%lu,%a,%a,%a,adjacency:1\n", i, node->GetId(), node->GetX(),
                  node->GetY(), node->GetZ());
  }
  if (trace)
    std::printf("model_payload=%u,%lu,area:%a,nodes:3,elements:1\n", position, triangle->GetId(),
                triangle->GetArea());
}
// Stack-only fixture; no derived object is deleted through the nonvirtual base.
class FixtureModel final : public Model {
public:
  void Storage(bool spare) {
    if (spare)
      meshes_.reserve(8);
    else
      while (meshes_.size() < meshes_.capacity())
        InsertMeshAdaptive(nullptr);
  }
};
struct RetirementCheck {
  Ledger& ledger;
  ~RetirementCheck() {
    for (int id = 0; id < 32; ++id)
      if (ledger.created[id])
        Complete(ledger, id);
  }
};
struct AppendFixture {
  Ledger ledger;
  RetirementCheck retirement{ledger};
  Geometry geometry;
  FixtureModel model;
  std::unique_ptr<MeshAdaptive> pending;
  MeshAdaptive* prefix = nullptr;
  MeshAdaptive* identity = nullptr;
  unsigned int count;
  int variant;
  explicit AppendFixture(int value, bool spare = false) : variant(value) {
    model.SetGeometry(&geometry);
    if ((variant & 1) != 0) {
      auto graph = Graph(ledger, 0);
      prefix = graph.get();
      model.InsertMeshAdaptive(graph.release());
    }
    model.Storage(spare);
    count = model.GetNumberMeshes();
    if ((variant & 2) == 0)
      pending = Graph(ledger, 1);
    identity = pending.get();
  }
  void Insert() {
#ifndef AP_MESH_MODEL_ORIGINAL
    if ((variant & 4) != 0)
      model.InsertMeshAdaptive(std::move(pending));
    else
#endif
      model.InsertMeshAdaptive(pending.release());
  }
  void Prefix() {
    Require(model.GetGeometry() == &geometry && model.GetNumberMeshes() >= count,
            "borrowed geometry and committed count");
    if (prefix)
      Live(model, 0, prefix, 0);
    for (unsigned int i = prefix ? 1U : 0U; i < count; ++i)
      Require(model.GetMeshAdaptive(i) == nullptr, "committed null slots");
  }
  void Success(bool trace) {
    Insert();
    Prefix();
    Require(!pending && model.GetNumberMeshes() == count + 1 &&
                model.GetMeshAdaptive(count) == identity,
            "append order and owning handoff");
    Require(!model.GetMeshAdaptive(count + 1), "out-of-range getter");
    if (identity)
      Live(model, count, identity, 1, trace);
    if (trace)
      std::printf("model_append=%d,count:%u,null:%d,borrow:1\n", variant, model.GetNumberMeshes(),
                  identity == nullptr);
  }
};
void Append(int variant, bool spare = false) {
  AppendFixture fixture(variant, spare);
  fixture.Success(true);
}
void Lifetime(bool corrupt = false) {
  Ledger ledger;
  Geometry first, second;
  auto* point = first.AddPoint(std::make_unique<PointAdaptive>(1, 2, 3));
  {
    Model model(&first);
    Require(model.GetGeometry() == &first, "borrowed geometry constructor");
    model.InsertMeshAdaptive(Graph(ledger, 0).release());
    model.InsertMeshAdaptive(nullptr);
    model.InsertMeshAdaptive(Graph(ledger, 1).release());
    model.SetGeometry(&second);
    Require(model.GetGeometry() == &second && point->GetX() == 1,
            "setter retains borrowed geometry");
    model.SetGeometry(nullptr);
    Require(!model.GetGeometry(), "null geometry remains a borrow");
  }
  Complete(ledger, 0);
  Complete(ledger, 1);
  if (corrupt)
    ledger.order[0] = 0;
  Require(ledger.retired == 2 && ledger.order[0] == 1 && ledger.order[1] == 0,
          "reverse mesh retirement");
  Require(point->GetZ() == 3, "Model never owns Geometry");
  std::puts("model_lifetime=reverse:1,0,nodes:6,triangles:2,borrow:1");
}
#ifndef AP_MESH_MODEL_ORIGINAL
void Move(int variant) {
  Ledger ledger;
  Geometry old_geometry, new_geometry;
  if (variant == 4) {
    Model source(&new_geometry);
    Model moved(std::move(source));
    Require(!source.GetNumberMeshes() && !source.GetGeometry() && !moved.GetNumberMeshes() &&
                moved.GetGeometry() == &new_geometry,
            "empty move transfers only the geometry borrow");
    Model* alias = &moved;
    moved = std::move(*alias);
    Require(!moved.GetNumberMeshes() && moved.GetGeometry() == &new_geometry,
            "empty self-move preserves geometry borrow");
    std::puts("model_move=4,identity:1,retirement:1,reuse:1");
    return;
  }
  {
    Model source(&new_geometry), destination(&old_geometry);
    if (variant != 0)
      source.InsertMeshAdaptive(Graph(ledger, 0).release());
    source.InsertMeshAdaptive(nullptr);
    auto* identity = source.GetMeshAdaptive(0);
    if (variant >= 2) {
      destination.InsertMeshAdaptive(Graph(ledger, 1).release());
      destination.InsertMeshAdaptive(Graph(ledger, 2).release());
    }
    if (variant == 3) {
      Model* alias = &source;
      source = std::move(*alias);
      Require(source.GetNumberMeshes() == 2 && source.GetGeometry() == &new_geometry,
              "self-move keeps ownership and borrowing");
      Live(source, 0, identity, 0);
    } else if (variant <= 1) {
      Model moved(std::move(source));
      Require(source.GetNumberMeshes() == 0 && !source.GetGeometry(),
              "move construction empties source and clears borrow");
      Require(moved.GetGeometry() == &new_geometry &&
                  moved.GetNumberMeshes() == (variant ? 2U : 1U),
              "constructor transfers exact slots and borrow");
      if (identity)
        Live(moved, 0, identity, 0);
    } else {
      destination = std::move(source);
      Complete(ledger, 1);
      Complete(ledger, 2);
      Require(ledger.retired == 2 && ledger.order[0] == 2 && ledger.order[1] == 1,
              "move assignment retires destination in reverse order");
      Require(source.GetNumberMeshes() == 0 && !source.GetGeometry(),
              "move assignment empties source and clears borrow");
      Require(destination.GetGeometry() == &new_geometry && destination.GetNumberMeshes() == 2,
              "assignment transfers borrow and exact slots");
      Live(destination, 0, identity, 0);
      Model empty;
      destination = std::move(empty);
      Complete(ledger, 0);
      Require(!destination.GetNumberMeshes() && !destination.GetGeometry(),
              "empty source retires populated destination");
    }
    source.SetGeometry(&old_geometry);
    source.InsertMeshAdaptive(Graph(ledger, 3).release());
    Live(source, source.GetNumberMeshes() - 1, source.GetMeshAdaptive(source.GetNumberMeshes() - 1),
         3);
  }
  Complete(ledger, 3);
  if (variant)
    Complete(ledger, 0);
  if (variant >= 2) {
    Complete(ledger, 1);
    Complete(ledger, 2);
  }
  std::printf("model_move=%d,identity:1,retirement:1,reuse:1\n", variant);
}
#endif
#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, target = -1;
int __cdecl AllocationHook(int kind, void*, std::size_t, int block, long, const unsigned char*,
                           int) {
  if (kind == _HOOK_ALLOC && block == _NORMAL_BLOCK && attempts++ == target) {
    ++denied;
    return FALSE;
  }
  return TRUE;
}
class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    attempts = denied = 0;
    target = ordinal;
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }

private:
  _CRT_ALLOC_HOOK previous_;
};
void Failures(int variant) {
  int total;
  {
    AppendFixture calibration(variant);
    {
      AllocationScope hook(-1);
      calibration.Insert();
    }
    total = attempts;
    Require(total > 0 && denied == 0, "calibrated actual growth allocation");
  }
  std::printf("model_measured=%d,allocations:%d\n", variant, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    {
      AppendFixture fixture(variant);
      bool caught = false;
      {
        AllocationScope hook(ordinal);
        try {
          fixture.Insert();
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      Require(caught && denied == 1 && attempts == ordinal + 1,
              "each calibrated allocation denied exactly once");
      fixture.Prefix();
      Require(fixture.model.GetNumberMeshes() == fixture.count && !fixture.pending,
              "failed append preserves count and consumes handoff");
      if (fixture.identity)
        Complete(fixture.ledger, 1);
      // A new independent argument may be appended after the observed failure.
      fixture.model.InsertMeshAdaptive(Graph(fixture.ledger, 2).release());
      Live(fixture.model, fixture.count, fixture.model.GetMeshAdaptive(fixture.count), 2);
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    Require(delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0,
            "failed adoption and subsequent reuse release all payloads");
    std::printf("model_denied=%d,ordinal:%d,attempts:%d,retained:0,bytes:0,prefix:1,reuse:1\n",
                variant, ordinal, attempts);
  }
  std::printf("model_sweep=%d,denied:%d/%d\n", variant, total, total);
}
void NoAllocation(int variant) {
  if (variant < 8) {
    AppendFixture fixture(variant, true);
    {
      AllocationScope hook(0);
      fixture.Insert();
    }
    Require(attempts == 0 && denied == 0, "spare-storage append does not allocate");
    fixture.Prefix();
    Require(fixture.model.GetMeshAdaptive(fixture.count) == fixture.identity,
            "spare-storage identity");
    if (fixture.identity)
      Live(fixture.model, fixture.count, fixture.identity, 1);
  }
#ifndef AP_MESH_MODEL_ORIGINAL
  else {
    Ledger ledger;
    Model a, b;
    a.InsertMeshAdaptive(Graph(ledger, 0).release());
    b.InsertMeshAdaptive(Graph(ledger, 1).release());
    {
      AllocationScope hook(0);
      if (variant == 8) {
        Model moved(std::move(a));
      } else if (variant == 9)
        b = std::move(a);
      else if (variant == 10) {
        Model* alias = &a;
        a = std::move(*alias);
      } else if (variant == 11) {
        Model empty;
        b = std::move(empty);
      } else
        Require(false, "known nonallocating operation");
    }
    Require(attempts == 0 && denied == 0, "transfer and retirement do not allocate");
    if (variant == 8)
      Complete(ledger, 0);
    else if (variant == 9 || variant == 11)
      Complete(ledger, 1);
  }
#endif
  std::printf("model_noalloc=%d,attempts:0\n", variant);
}
#endif
void Run(const char* mode) {
  if (std::strcmp(mode, "contracts") == 0) {
    Lifetime();
#ifndef AP_MESH_MODEL_ORIGINAL
    Require(!std::is_copy_constructible_v<Model> && !std::is_copy_assignable_v<Model> &&
                std::is_nothrow_move_constructible_v<Model> &&
                std::is_nothrow_move_assignable_v<Model>,
            "explicit noncopyable nonthrowing move contract");
    for (int i = 0; i < 5; ++i)
      Move(i);
    for (int i = 0; i < 8; ++i)
      Append(i);
#endif
  } else if (std::strncmp(mode, "trace-", 6) == 0)
    Append(std::atoi(mode + 6));
  else if (std::strcmp(mode, "lifetime") == 0)
    Lifetime();
  else if (std::strcmp(mode, "order-control") == 0)
    Lifetime(true);
  else if (std::strcmp(mode, "adjacency-control") == 0) {
    Ledger ledger;
    Model model;
    auto graph = Graph(ledger, 0);
    auto* raw = graph.get();
    auto* sub = raw->GetSubMeshAdaptiveByPosition(0);
    sub->GetNoh(0)->RemoveElementObserver(sub->GetElement(0));
    model.InsertMeshAdaptive(graph.release());
    Live(model, 0, raw, 0);
  } else if (std::strcmp(mode, "uaf-control") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired_x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak-control") == 0) {
    std::printf("deliberate_leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
  }
#ifndef AP_MESH_MODEL_ORIGINAL
  else if (std::strncmp(mode, "move-", 5) == 0)
    Move(std::atoi(mode + 5));
#endif
#if defined(_MSC_VER) && defined(_DEBUG)
  else if (std::strncmp(mode, "failure-", 8) == 0)
    Failures(std::atoi(mode + 8));
  else if (std::strncmp(mode, "noalloc-", 8) == 0)
    NoAllocation(std::atoi(mode + 8));
  else if (std::strcmp(mode, "hook-control") == 0) {
    bool caught = false;
    {
      AllocationScope hook(0);
      try {
        auto node = std::make_unique<NodeAdaptive>();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && denied == 1 && attempts == 1, "actual allocation hook control");
    std::puts("model_hook=detected");
  }
#endif
  else
    Require(false, "known mode");
}
} // namespace
int main(int argc, char** argv) {
#ifdef _WIN32
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
#endif
  Require(argc == 2, "one mode required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_MSC_VER) && defined(_DEBUG)
  for (int report : {_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(report, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(report, _CRTDBG_FILE_STDERR);
  }
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  Run(argv[1]);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  if (delta.lCounts[_NORMAL_BLOCK] || delta.lSizes[_NORMAL_BLOCK])
    return 1;
#endif
  std::puts("PASS");
}
