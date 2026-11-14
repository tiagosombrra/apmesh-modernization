#include "physical_quadrilateral_adaptive.h"

#include "four_corner_admission.h"

#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_bezier.h"
#include "data/triangle_adaptive.h"
#include "input_output/models_3d.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {
using apmesh::quad::research::QuadrilateralAdaptive;
using Four = std::array<std::size_t, 4>;
using Three = std::array<std::size_t, 3>;
using Point = std::array<double, 3>;

struct Mesh {
  std::vector<Point> vertices;
  std::vector<Four> quads;
  std::vector<Three> tris;
};

void Require(bool value, const char* reason) {
  if (!value)
    throw std::runtime_error(reason);
}

bool Close(double a, double b, double tolerance = 5e-10) {
  return std::isfinite(a) && std::isfinite(b) && std::abs(a - b) <= tolerance;
}

template <std::size_t N>
void AddFace(const std::vector<std::size_t>& ids, std::vector<std::array<std::size_t, N>>& target) {
  Require(ids.size() == N, "Unexpected face arity");
  std::array<std::size_t, N> face{};
  std::set<std::size_t> unique;
  for (std::size_t i = 0; i < N; ++i) {
    face[i] = ids[i];
    Require(unique.insert(face[i]).second, "Repeated face vertex");
  }
  target.push_back(face);
}

Mesh ReadObj(const std::string& path, bool physical) {
  std::ifstream input(path);
  Require(static_cast<bool>(input), "Cannot open hybrid input");
  Mesh mesh;
  std::string line;
  unsigned group = 0;
  while (std::getline(input, line)) {
    std::istringstream record(line);
    std::string kind;
    if (!(record >> kind) || kind[0] == '#')
      continue;
    if (kind == "v") {
      Require(group == 0, "Vertex after mesh face groups");
      Point p{};
      Require(static_cast<bool>(record >> p[0] >> p[1] >> p[2]), "Invalid OBJ coordinate record");
      for (double value : p)
        Require(std::isfinite(value), "Nonfinite XYZ/UV");
      std::string extra;
      Require(!(record >> extra), "Unexpected OBJ vertex fields");
      mesh.vertices.push_back(p);
    } else if (kind == "g") {
      std::string name;
      Require(static_cast<bool>(record >> name), "Empty group name");
      ++group;
      Require((group == 1 &&
               name == (physical ? "QUAD_native_cpp_lifted" : "QUAD_native_cpp_unmodified")) ||
                  (group == 2 && name == (physical ? "TRI_exterior_Lawson_research_lifted"
                                                   : "TRI_exterior_local_Lawson_research")),
              "Source group provenance mismatch");
    } else if (kind == "f") {
      Require(group == 1 || group == 2, "Face outside source groups");
      std::vector<std::size_t> ids;
      std::string value;
      while (record >> value) {
        Require(value.find_first_not_of("0123456789") == std::string::npos,
                "Nonintegral face reference");
        const auto parsed = std::stoull(value);
        Require(parsed > 0 && parsed <= mesh.vertices.size(), "Out-of-range face reference");
        ids.push_back(static_cast<std::size_t>(parsed - 1));
      }
      if (group == 1)
        AddFace<4>(ids, mesh.quads);
      else
        AddFace<3>(ids, mesh.tris);
    } else {
      throw std::runtime_error("Unsupported OBJ record");
    }
  }
  Require(mesh.vertices.size() == 69 && mesh.quads.size() == 42 && mesh.tris.size() == 36 &&
              group == 2,
          "Source 69/42/36 hybrid inventory changed");
  return mesh;
}

void CheckMixedTopology(const Mesh& uv) {
  struct EdgeIncidence {
    bool quad;
    std::size_t from;
    std::size_t to;
  };
  std::map<std::pair<std::size_t, std::size_t>, std::vector<EdgeIncidence>> edges;
  const auto add = [&edges](auto face, bool quad) {
    for (std::size_t i = 0; i < face.size(); ++i) {
      const auto a = face[i];
      const auto b = face[(i + 1) % face.size()];
      const auto key = std::minmax(a, b);
      edges[{key.first, key.second}].push_back({quad, a, b});
    }
  };
  for (auto face : uv.quads)
    add(face, true);
  for (auto face : uv.tris)
    add(face, false);
  unsigned seam = 0;
  unsigned boundary = 0;
  for (const auto& item : edges) {
    const auto& refs = item.second;
    Require(refs.size() >= 1 && refs.size() <= 2, "Nonmanifold mixed edge incidence");
    if (refs.size() == 2) {
      Require(refs[0].from == refs[1].to && refs[0].to == refs[1].from,
              "Mismatched opposite edge winding");
      if (refs[0].quad != refs[1].quad)
        ++seam;
    } else {
      const Point& a = uv.vertices[item.first.first];
      const Point& b = uv.vertices[item.first.second];
      Require((a[0] == b[0] && (a[0] == 0.0 || a[0] == 1.0)) ||
                  (a[1] == b[1] && (a[1] == 0.0 || a[1] == 1.0)),
              "Exterior edge not on model UV boundary");
      ++boundary;
    }
  }
  Require(seam == 20 && boundary == 16, "Native QUAD/M5 TRI seam or boundary changed");
}

void ExpectThrows(const std::function<void()>& operation, const char* label) {
  try {
    operation();
  } catch (const std::exception&) {
    return;
  }
  throw std::runtime_error(std::string("Unrejected invalid QUAD: ") + label);
}

void TestLifecycleAndFailureAtomicity() {
  std::array<NodeAdaptive, 4> owned{NodeAdaptive(0, 0, 0), NodeAdaptive(1, 0, 0),
                                    NodeAdaptive(1, 1, 0), NodeAdaptive(0, 1, 0)};
  for (std::size_t i = 0; i < owned.size(); ++i)
    owned[i].SetId(500 + static_cast<unsigned long>(i));
  QuadrilateralAdaptive::Nodes borrowed{&owned[0], &owned[1], &owned[2], &owned[3]};
  QuadrilateralAdaptive::Parameters uv{{{{0, 0}}, {{1, 0}}, {{1, 1}}, {{0, 1}}}};
  const VectorAdaptive normal(0, 0, 1);
  {
    auto first = std::make_unique<QuadrilateralAdaptive>(borrowed, uv, normal);
    Require(Close(first->GetArea(), 1.0), "Wrong flat four-node area");
    Require(Close(first->GetAngle(owned[0]), std::acos(-1.0) / 2.0), "Wrong physical quad angle");
    Require(first->GetNoh(1).GetNumberElements() == 0 && first->GetNoh(1).GetId() == 500,
            "GetNoh copied foreign element observers");
    Require(first->GetVertexPoint(4).GetId() == 503, "Quad vertex ID was not retained");
    for (auto& node : owned)
      Require(node.GetNumberElements() == 1, "Missing exactly one quad node observer");
    ExpectThrows([&] { static_cast<void>(first->GetNoh(0)); }, "zero-based vertex");
    ExpectThrows([&] { static_cast<void>(first->GetNoh(5)); }, "out-of-range vertex");
    ExpectThrows(
        [&] {
          NodeAdaptive identical_location(0, 0, 0);
          static_cast<void>(first->GetAngle(identical_location));
        },
        "foreign node identity");

    for (int fault = 0; fault < 4; ++fault) {
      ExpectThrows([&] { QuadrilateralAdaptive fail(borrowed, uv, normal, fault); },
                   "fault injection rollback");
      for (const auto& node : owned)
        Require(node.GetNumberElements() == 1, "Partial constructor left a stale observer");
    }
    auto duplicate = borrowed;
    duplicate[3] = duplicate[0];
    ExpectThrows([&] { QuadrilateralAdaptive bad(duplicate, uv, normal); },
                 "duplicate borrowed node");
    duplicate = borrowed;
    duplicate[3] = nullptr;
    ExpectThrows([&] { QuadrilateralAdaptive bad(duplicate, uv, normal); }, "null borrowed node");
    auto bad_uv = uv;
    bad_uv[2][0] = std::numeric_limits<double>::quiet_NaN();
    ExpectThrows([&] { QuadrilateralAdaptive bad(borrowed, bad_uv, normal); }, "nonfinite uv");
    bad_uv = uv;
    bad_uv[1][0] = 1.1;
    ExpectThrows([&] { QuadrilateralAdaptive bad(borrowed, bad_uv, normal); }, "out of unit uv");
    bad_uv = uv;
    std::swap(bad_uv[1], bad_uv[3]);
    ExpectThrows([&] { QuadrilateralAdaptive bad(borrowed, bad_uv, normal); }, "negative uv area");
    const VectorAdaptive reversed(0, 0, -1);
    ExpectThrows([&] { QuadrilateralAdaptive bad(borrowed, uv, reversed); },
                 "reversed physical normal");
    auto collapsed = borrowed;
    NodeAdaptive repeated_position(0, 0, 0);
    collapsed[2] = &repeated_position;
    ExpectThrows([&] { QuadrilateralAdaptive bad(collapsed, uv, normal); },
                 "zero physical subtriangle");
    for (const auto& node : owned)
      Require(node.GetNumberElements() == 1, "Invalid construction modified existing observers");
  }
  for (const auto& node : owned)
    Require(node.GetNumberElements() == 0,
            "Destructor leaked quad observer into live borrowed nodes");
  std::cout << "quad_four_node_lifecycle=ok rollback_slots=4 "
               "invalid_inputs=7 external_observers_retired=4\n";
}

void CheckAdjacency(SubMesh& mesh, const std::array<NodeAdaptive*, 69>& identities,
                    const Mesh& uv) {
  std::array<unsigned, 69> degree{};
  for (auto face : uv.quads)
    for (auto id : face)
      ++degree[id];
  for (auto face : uv.tris)
    for (auto id : face)
      ++degree[id];
  unsigned links = 0;
  std::set<ElementAdaptive*> all_elements;
  for (unsigned i = 0; i < mesh.GetNumberElements(); ++i) {
    ElementAdaptive* element = mesh.GetElement(i);
    Require(element != nullptr && all_elements.insert(element).second,
            "Duplicate or null SubMesh element");
  }
  for (unsigned i = 0; i < 69; ++i) {
    NodeAdaptive* node = mesh.GetNoh(i);
    Require(node == identities[i] && node->GetId() == static_cast<unsigned long>(i + 1) &&
                node->GetNumberElements() == degree[i],
            "Shared node pointer, ID or incidence changed after move");
    for (auto* observer : node->GetElements()) {
      Require(all_elements.count(observer) == 1, "Node references a foreign or retired element");
      ++links;
    }
  }
  Require(links == 42 * 4 + 36 * 3, "Wrong total reverse quadrilateral/triangle observers");
}

void TestNativeMixedMesh(const Mesh& uv, const Mesh& xyz) {
  Require(uv.quads == xyz.quads && uv.tris == xyz.tris,
          "Physical model changed native mixed face IDs");
  CheckMixedTopology(uv);

  Geometry geometry;
  Models3d model;
  model.ModelCurvaBezier(&geometry);
  Require(geometry.GetNumberPatches() == 1,
          "Expected the actual production-owned one-patch Bezier model");
  auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  Require(patch != nullptr, "Built-in model is not a physical PatchBezier");

  auto owned = std::make_unique<SubMesh>();
  std::array<NodeAdaptive*, 69> identities{};
  for (std::size_t i = 0; i < xyz.vertices.size(); ++i) {
    const auto& p = xyz.vertices[i];
    auto node = std::make_unique<NodeAdaptive>(p[0], p[1], p[2]);
    node->SetId(static_cast<unsigned long>(i + 1));
    identities[i] = node.get();
    owned->AddNoh(std::move(node));
    const auto expected = patch->Parameterize(uv.vertices[i][0], uv.vertices[i][1]);
    Require(Close(p[0], expected.GetX()) && Close(p[1], expected.GetY()) &&
                Close(p[2], expected.GetZ()),
            "Physical node is detached from its real model UV identity");
  }

  for (const auto& face : uv.quads) {
    QuadrilateralAdaptive::Nodes four{};
    QuadrilateralAdaptive::Parameters parameters{};
    double u = 0.0, v = 0.0;
    for (unsigned j = 0; j < 4; ++j) {
      four[j] = identities[face[j]];
      parameters[j] = {uv.vertices[face[j]][0], uv.vertices[face[j]][1]};
      u += parameters[j][0] / 4.0;
      v += parameters[j][1] / 4.0;
    }
    const auto du = patch->Qu(u, v);
    const auto dv = patch->Qv(u, v);
    auto quad = std::make_unique<QuadrilateralAdaptive>(four, parameters, du * dv);
    Require(quad->GetArea() > 1e-12 && quad->GetVectorNormal().CalculateModule() > 1e-12,
            "Nonpositive physical QUAD size");
    owned->AddElement(std::move(quad));
  }
  for (auto face : uv.tris) {
    auto tri = std::make_unique<TriangleAdaptive>(identities[face[0]], identities[face[1]],
                                                  identities[face[2]]);
    Require(tri->GetArea() > 1e-12, "Degenerate physical TRI");
    owned->AddElement(std::move(tri));
  }
  Require(owned->GetNumberNos() == 69 && owned->GetNumberElements() == 78,
          "SubMesh did not adopt 69 physical nodes and 78 mixed elements");
  CheckAdjacency(*owned, identities, uv);
  auto moved = std::make_unique<SubMesh>(std::move(*owned));
  Require(owned->GetNumberNos() == 0 && owned->GetNumberElements() == 0,
          "Moved-from SubMesh retains owned physical objects");
  CheckAdjacency(*moved, identities, uv);
  SubMesh assigned;
  assigned = std::move(*moved);
  CheckAdjacency(assigned, identities, uv);
  assigned = std::move(assigned);
  CheckAdjacency(assigned, identities, uv);
  auto* quad = dynamic_cast<QuadrilateralAdaptive*>(assigned.GetElement(0));
  Require(quad != nullptr && quad->GetNodeObservers()[0] == identities[uv.quads[0][0]],
          "Moved physical QUAD lost its original borrowed node addresses");
  // The SubMesh destructor retires all 78 elements before its 69 nodes.
  std::cout << "quad_four_node_mixed=ok model=ModelCurvaBezier "
               "vertices=69 quads=42 tri=36 elements=78 observer_links=276 "
               "shared_seam=20 boundary=16 move_and_self_move=ok "
               "NOT_production_QUAD\n";
}

} // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 3, "Usage: quad_four_node_probe NATIVE_UV_MIXED_OBJ PHYSICAL_XYZ_MIXED_OBJ");
    TestLifecycleAndFailureAtomicity();
    apmesh::quad::test::TestFourCornerAdmission();
    const Mesh uv = ReadObj(argv[1], false);
    const Mesh xyz = ReadObj(argv[2], true);
    TestNativeMixedMesh(uv, xyz);
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "quad_four_node_probe_failed: " << error.what() << '\n';
    return 1;
  }
}
