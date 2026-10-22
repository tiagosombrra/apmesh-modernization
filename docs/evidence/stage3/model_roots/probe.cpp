#include "data/model.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

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
#include <windows.h>

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Original model audit failed: %s\n", message);
    std::exit(2);
  }
}
class CountedNode : public NodeAdaptive {
public:
  CountedNode(double x, double y, int& count) : NodeAdaptive(x, y, 0), count_(count) {}
  ~CountedNode() override { ++count_; }

private:
  int& count_;
};
std::unique_ptr<MeshAdaptive> MakeMesh(int& destroyed) {
  auto mesh = std::make_unique<MeshAdaptive>();
  auto sub = std::make_unique<SubMesh>();
  sub->AddNoh(std::make_unique<CountedNode>(0, 0, destroyed));
  sub->AddNoh(std::make_unique<CountedNode>(1, 0, destroyed));
  sub->AddNoh(std::make_unique<CountedNode>(0, 1, destroyed));
  sub->AddElement(
      std::make_unique<TriangleAdaptive>(sub->GetNoh(0), sub->GetNoh(1), sub->GetNoh(2)));
  mesh->InsertSubMeshAdaptive(sub.release());
  return mesh;
}
void Live(Model& model, unsigned int position, MeshAdaptive* expected) {
  Require(model.GetMeshAdaptive(position) == expected, "stored pointer identity");
  auto* sub = expected->GetSubMeshAdaptiveByPosition(0);
  Require(sub && sub->GetNumberNos() == 3 && sub->GetNumberElements() == 1, "owned payload");
  auto* triangle = sub->GetElement(0);
  Require(triangle->GetArea() == 0.5, "right triangle area");
  for (unsigned int n = 0; n < 3; ++n)
    Require(sub->GetNoh(n)->GetNumberElements() == 1 && sub->GetNoh(n)->GetElement(0) == triangle,
            "live local triangle observers");
}
void Normal() {
  int destroyed = 0;
  Geometry first_geometry, second_geometry;
  auto* first_point = first_geometry.AddPoint(std::make_unique<PointAdaptive>(1, 2, 3));
  {
    Model model(&first_geometry);
    Require(model.GetGeometry() == &first_geometry, "borrow constructor");
    auto first = MakeMesh(destroyed), second = MakeMesh(destroyed);
    auto* a = first.get();
    auto* b = second.get();
    model.InsertMeshAdaptive(first.release());
    model.InsertMeshAdaptive(nullptr);
    model.InsertMeshAdaptive(second.release());
    Require(model.GetNumberMeshes() == 3 && !model.GetMeshAdaptive(1) && !model.GetMeshAdaptive(3),
            "order, null slot and out-of-range behavior");
    Live(model, 0, a);
    Live(model, 2, b);
    model.SetGeometry(&second_geometry);
    Require(model.GetGeometry() == &second_geometry && first_point->GetX() == 1, "borrow setter");
  }
  Require(destroyed == 6 && first_point->GetZ() == 3, "all nodes destroyed; geometry remains live");
  std::printf("normal_meshes=2 nodes_destroyed=%d\n", destroyed);
}
void Alias(const char* mode) {
  int destroyed = 0;
  Model source;
  source.InsertMeshAdaptive(MakeMesh(destroyed).release());
  auto* expected = source.GetMeshAdaptive(0);
  if (std::strcmp(mode, "copy-construct") == 0) {
    Model destination(source);
    Live(destination, 0, expected);
  } else if (std::strcmp(mode, "rvalue-construct") == 0) {
    Model destination(std::move(source));
    Live(destination, 0, expected);
    Require(source.GetNumberMeshes() == 1, "rvalue construction leaves aliased source");
  } else if (std::strcmp(mode, "duplicate-adoption") == 0) {
    source.InsertMeshAdaptive(expected);
  } else {
    Model destination;
    destination.InsertMeshAdaptive(MakeMesh(destroyed).release());
    if (std::strcmp(mode, "copy-assign") == 0)
      destination = source;
    else {
      Require(std::strcmp(mode, "rvalue-assign") == 0, "known alias scenario");
      destination = std::move(source);
    }
    Live(destination, 0, expected);
    Require(destroyed == 0, "previous destination payload lost without destruction");
    std::puts("assignment_old_payload_destroyed=0");
  }
  std::puts("alias_operation_completed=1");
  // Ordinary destruction now exercises the actual duplicated owning pointers.
}
#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0;
int __cdecl Deny(int kind, void*, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC && block == _NORMAL_BLOCK) {
    ++attempts;
    if (denied == 0) {
      ++denied;
      return FALSE;
    }
  }
  return TRUE;
}
void FailedAppend(bool seed, bool clean_argument) {
  int destroyed = 0;
  Model model;
  MeshAdaptive* prefix = nullptr;
  if (seed) {
    prefix = MakeMesh(destroyed).release();
    model.InsertMeshAdaptive(prefix);
  }
  auto* pending = MakeMesh(destroyed).release();
  bool caught = false;
  auto prior = _CrtSetAllocHook(Deny);
  try {
    model.InsertMeshAdaptive(pending);
  } catch (const std::bad_alloc&) {
    caught = true;
  }
  _CrtSetAllocHook(prior);
  Require(caught && denied == 1 && attempts > 0, "actual denied append allocation");
  Require(model.GetNumberMeshes() == (seed ? 1U : 0U), "failed append preserves count");
  if (prefix)
    Live(model, 0, prefix);
  Require(destroyed == 0, "failed append did not destroy pending payload");
  std::printf("append_failure=1 denials=%d attempts=%d prefix=%u destroyed=%d\n", denied, attempts,
              model.GetNumberMeshes(), destroyed);
  if (clean_argument)
    delete pending;
}
#endif
} // namespace

int main(int argc, char** argv) {
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  if (argc != 2)
    return 2;
  std::printf(
      "traits copy_ctor=%d copy_assign=%d rvalue_ctor=%d rvalue_assign=%d nothrow_rvalue=%d\n",
      std::is_copy_constructible_v<Model>, std::is_copy_assignable_v<Model>,
      std::is_move_constructible_v<Model>, std::is_move_assignable_v<Model>,
      std::is_nothrow_move_constructible_v<Model>);
#if defined(_MSC_VER) && defined(_DEBUG)
  for (int report : {_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(report, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(report, _CRTDBG_FILE_STDERR);
  }
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  const char* mode = argv[1];
  if (std::strcmp(mode, "normal") == 0)
    Normal();
  else if (std::strcmp(mode, "leak-control") == 0) {
    int unused = 0;
    std::printf("deliberate_mesh_leak=%p\n", static_cast<void*>(MakeMesh(unused).release()));
  } else if (std::strcmp(mode, "uaf-control") == 0) {
    volatile MeshAdaptive* mesh = new MeshAdaptive();
    delete const_cast<MeshAdaptive*>(mesh);
    std::printf("expired_count=%u\n",
                const_cast<MeshAdaptive*>(mesh)->GetNumberSubMeshesAdaptive());
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  else if (std::strcmp(mode, "failed-empty") == 0)
    FailedAppend(false, false);
  else if (std::strcmp(mode, "failed-seeded") == 0)
    FailedAppend(true, false);
  else if (std::strcmp(mode, "cleanup-empty") == 0)
    FailedAppend(false, true);
  else if (std::strcmp(mode, "cleanup-seeded") == 0)
    FailedAppend(true, true);
#endif
  else
    Alias(mode);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  return delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0 ? 0 : 1;
#else
  return 0;
#endif
}
