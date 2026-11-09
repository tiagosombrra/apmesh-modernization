#include "uv_mesh.h"

#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

namespace {
using namespace apmesh::quad;

void Check(bool condition, const std::string& message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

void Reject(const std::function<void()>& operation, const std::string& expected = {}) {
  try {
    operation();
  } catch (const std::invalid_argument& error) {
    Check(expected.empty() || std::string(error.what()).find(expected) != std::string::npos,
          "Wrong rejection reason: " + std::string(error.what()));
    return;
  }
  throw std::runtime_error("Invalid topology was accepted");
}

PolygonMesh Square() { return {{{0, 0}, {1, 0}, {1, 1}, {0, 1}}, {{0, 1, 2, 3}}, {{0.5, 0.5}}}; }

PolygonMesh Fixture(std::size_t column) {
  const std::map<char, UvVertex> points{{'A', {0, 0}},   {'B', {1, 0}},   {'C', {1, 1}},
                                        {'D', {0, 1}},   {'S', {0.5, 0}}, {'E', {1, 0.5}},
                                        {'N', {0.5, 1}}, {'W', {0, 0.5}}, {'O', {0.5, 0.5}}};
  // Connectivity from the Figure 7 transcription. Test points are explicitly
  // injected positive geometry, not historical/numerical centroid oracles.
  const std::vector<std::vector<std::string>> cycles{
      {"ABCD"},         {"ABOW", "BCO", "WOCD"}, {"ABOW", "WOND", "OBCN"},
      {"ABEW", "WECD"}, {"ASW", "WSND", "SBCN"}, {"ASOW", "SBEO", "OECN", "WOND"}};
  const std::vector<std::vector<UvVertex>> centers{
      {{0.5, 0.5}},
      {{0.375, 0.25}, {5.0 / 6.0, 0.5}, {0.375, 0.75}},
      {{0.375, 0.25}, {0.25, 0.75}, {0.75, 0.625}},
      {{0.5, 0.25}, {0.5, 0.75}},
      {{1.0 / 6.0, 1.0 / 6.0}, {0.25, 0.625}, {0.75, 0.5}},
      {{0.25, 0.25}, {0.75, 0.25}, {0.75, 0.75}, {0.25, 0.75}}};
  PolygonMesh input;
  std::map<char, VertexId> ids;
  for (const auto& cycle : cycles.at(column)) {
    std::vector<VertexId> face;
    for (char name : cycle) {
      const auto found = ids.find(name);
      if (found != ids.end()) {
        face.push_back(found->second);
      } else {
        const auto id = input.vertices.size();
        ids.emplace(name, id);
        input.vertices.push_back(points.at(name));
        face.push_back(id);
      }
    }
    input.polygons.push_back(std::move(face));
  }
  input.interior_points = centers.at(column);
  return input;
}

bool Equal(const PolygonMesh& a, const PolygonMesh& b) {
  if (a.polygons != b.polygons || a.vertices.size() != b.vertices.size() ||
      a.interior_points.size() != b.interior_points.size()) {
    return false;
  }
  for (std::size_t i = 0; i < a.vertices.size(); ++i) {
    if (a.vertices[i].u != b.vertices[i].u || a.vertices[i].v != b.vertices[i].v) {
      return false;
    }
  }
  for (std::size_t i = 0; i < a.interior_points.size(); ++i) {
    if (a.interior_points[i].u != b.interior_points[i].u ||
        a.interior_points[i].v != b.interior_points[i].v) {
      return false;
    }
  }
  return true;
}

VertexId Intern(PolygonMesh& input, UvVertex vertex) {
  for (VertexId i = 0; i < input.vertices.size(); ++i) {
    if (input.vertices[i].u == vertex.u && input.vertices[i].v == vertex.v) {
      return i;
    }
  }
  const auto id = input.vertices.size();
  input.vertices.push_back(vertex);
  return id;
}

struct DecimalComma : std::numpunct<char> {
  char do_decimal_point() const override { return ','; }
};

} // namespace

int main() {
  std::size_t outcomes = 0;
  try {
    const auto run = [&outcomes](const std::string& name, const std::function<void()>& test) {
      test();
      ++outcomes;
      std::cout << "PASS " << name << '\n';
    };
    const std::array<std::size_t, 6> counts{4, 11, 12, 8, 11, 16};
    for (std::size_t column = 0; column < counts.size(); ++column) {
      for (int reflection = 0; reflection < 2; ++reflection) {
        for (int turns = 0; turns < 4; ++turns) {
          run("pattern-" + std::to_string(column + 1) + "-r" + std::to_string(reflection) + "-t" +
                  std::to_string(turns),
              [=] {
                auto input = Fixture(column);
                const auto transform = [=](UvVertex& vertex) {
                  if (reflection != 0) {
                    vertex.u = 1 - vertex.u;
                  }
                  for (int i = 0; i < turns; ++i) {
                    const double u = 1 - vertex.v;
                    vertex.v = vertex.u;
                    vertex.u = u;
                  }
                };
                for (auto& point : input.vertices) {
                  transform(point);
                }
                for (auto& point : input.interior_points) {
                  transform(point);
                }
                if (reflection != 0) {
                  for (auto& polygon : input.polygons) {
                    std::reverse(polygon.begin(), polygon.end());
                  }
                }
                const auto before = input;
                const auto mesh = Subdivide(input);
                Check(Equal(input, before), "Generator mutated polygon input");
                Check(mesh.quads.size() == counts[column], "Wrong four-node element count");
                const auto topology = Validate(mesh, 1);
                Check(topology.boundary_edges > 0 && topology.interior_edges > 0,
                      "No actual topology comparisons");
                for (std::size_t i = 0; i < input.vertices.size(); ++i) {
                  Check(mesh.vertices[i].u == input.vertices[i].u &&
                            mesh.vertices[i].v == input.vertices[i].v,
                        "Original vertex IDs changed");
                }
              });
        }
      }
    }
    run("shared-midpoint-and-exact-square-connectivity", [] {
      const auto mesh = Subdivide(Square());
      const std::vector<std::array<VertexId, 4>> expected{
          {0, 4, 8, 7}, {1, 5, 8, 4}, {2, 6, 8, 5}, {3, 7, 8, 6}};
      Check(mesh.vertices.size() == 9, "Square vertex count");
      for (std::size_t i = 0; i < expected.size(); ++i) {
        Check(mesh.quads[i].vertices == expected[i], "Square connectivity/order changed");
      }
      const auto summary = Validate(mesh, 1);
      Check(summary.boundary_edges == 8 && summary.interior_edges == 4, "Square incidences");
    });
    run("two-to-one-neighbor-conformity", [] {
      auto input = Fixture(1);
      for (int row = 0; row < 2; ++row) {
        const double y = 0.5 * row;
        input.polygons.push_back({Intern(input, {-0.5, y}), Intern(input, {0, y}),
                                  Intern(input, {0, y + 0.5}), Intern(input, {-0.5, y + 0.5})});
        input.interior_points.push_back({-0.25, y + 0.25});
      }
      const auto mesh = Subdivide(input);
      Check(mesh.quads.size() == 19, "2:1 transition quad count");
      Validate(mesh, 1.5);
      for (double y : {0.25, 0.75}) {
        Check(std::count_if(mesh.vertices.begin(), mesh.vertices.end(),
                            [=](const UvVertex& p) { return p.u == 0 && p.v == y; }) == 1,
              "2:1 seam has duplicated midpoint identity");
      }
    });
    run("id-permutation", [] {
      auto input = Fixture(5);
      std::reverse(input.vertices.begin(), input.vertices.end());
      for (auto& polygon : input.polygons) {
        for (auto& id : polygon) {
          id = input.vertices.size() - 1 - id;
        }
      }
      Check(Subdivide(input).quads.size() == 16, "ID permutation changed topology");
    });
    run("uniform-scale-translation", [] {
      auto input = Fixture(2);
      for (auto* points : {&input.vertices, &input.interior_points}) {
        for (auto& point : *points) {
          point.u = 3.25 * point.u - 2;
          point.v = 3.25 * point.v + 1.25;
        }
      }
      Validate(Subdivide(input), 3.25L * 3.25L);
    });
    for (int seed = 0; seed < 32; ++seed) {
      run("bounded-grid-" + std::to_string(seed), [=] {
        const int nx = 1 + seed % 5;
        const int ny = 1 + (seed * 3) % 7;
        PolygonMesh input;
        for (int y = 0; y < ny; ++y) {
          for (int x = 0; x < nx; ++x) {
            const auto point = [=](int a, int b) {
              return UvVertex{static_cast<double>(a) / nx, static_cast<double>(b) / ny};
            };
            input.polygons.push_back({Intern(input, point(x, y)), Intern(input, point(x + 1, y)),
                                      Intern(input, point(x + 1, y + 1)),
                                      Intern(input, point(x, y + 1))});
            input.interior_points.push_back({(x + 0.5) / nx, (y + 0.5) / ny});
          }
        }
        const auto mesh = Subdivide(input);
        Check(mesh.quads.size() == static_cast<std::size_t>(4 * nx * ny), "Grid quad count");
        Validate(mesh, 1);
      });
    }
    for (const std::string mode : {"outside", "edge", "concave-output", "missing", "nonfinite"}) {
      run("reject-point-" + mode, [&] {
        auto input = Square();
        if (mode == "outside") {
          input.interior_points[0] = {2, 2};
        } else if (mode == "edge") {
          input.interior_points[0] = {0, 0.5};
        } else if (mode == "concave-output") {
          input.interior_points[0] = {0.01, 0.01};
        } else if (mode == "missing") {
          input.interior_points.clear();
        } else {
          input.interior_points[0].u = std::numeric_limits<double>::infinity();
        }
        Reject([&] { Subdivide(input); });
      });
    }
    for (const std::string mode :
         {"repeated", "out-of-range", "clockwise", "coincident", "unused", "empty", "nonfinite"}) {
      run("reject-input-" + mode, [&] {
        auto input = Square();
        if (mode == "repeated") {
          input.polygons[0][1] = 0;
        } else if (mode == "out-of-range") {
          input.polygons[0][1] = 100;
        } else if (mode == "clockwise") {
          std::reverse(input.polygons[0].begin(), input.polygons[0].end());
        } else if (mode == "coincident") {
          input.vertices.push_back(input.vertices.front());
        } else if (mode == "unused") {
          input.vertices.push_back({2, 2});
        } else if (mode == "empty") {
          input.polygons.clear();
        } else {
          input.vertices[0].v = std::numeric_limits<double>::quiet_NaN();
        }
        Reject([&] { Subdivide(input); });
      });
    }
    run("failure-preserves-source", [] {
      auto input = Square();
      input.interior_points[0] = {0.01, 0.01};
      const auto before = input;
      Reject([&] { Subdivide(input); });
      Check(Equal(input, before), "Failure mutated source");
    });
    for (const std::string mode : {"repeated", "out-of-range", "clockwise", "missing-face",
                                   "duplicate-face", "third-incidence", "wrong-area"}) {
      run("reject-quad-" + mode, [&] {
        auto mesh = Subdivide(Square());
        if (mode == "repeated") {
          mesh.quads[0].vertices[1] = mesh.quads[0].vertices[0];
        } else if (mode == "out-of-range") {
          mesh.quads[0].vertices[1] = 100;
        } else if (mode == "clockwise") {
          std::reverse(mesh.quads[0].vertices.begin(), mesh.quads[0].vertices.end());
        } else if (mode == "missing-face") {
          mesh.quads.pop_back();
        } else if (mode == "duplicate-face") {
          mesh.quads.push_back(mesh.quads.front());
        } else if (mode == "third-incidence") {
          mesh.quads.push_back(mesh.quads.front());
          mesh.quads.push_back(mesh.quads.front());
        }
        Reject([&] { Validate(mesh, mode == "wrong-area" ? 2 : 1); });
      });
    }
    run("reject-hanging-node", [] {
      const UvMesh mesh{{{0, 0}, {1, 0}, {1, 1}, {0, 1}, {2, 0}, {2, 0.5}, {1, 0.5}, {2, 1}},
                        {{{0, 1, 2, 3}}, {{1, 4, 5, 6}}, {{6, 5, 7, 2}}}};
      Reject([&] { Validate(mesh, 2); }, "hanging node");
    });
    for (const std::string mode : {"crossing", "contained", "disconnected"}) {
      run("reject-" + mode, [&] {
        UvMesh mesh{{{0, 0}, {1, 0}, {1, 1}, {0, 1}}, {{{0, 1, 2, 3}}}};
        const double offset = mode == "crossing" ? 0.5 : (mode == "contained" ? 0.25 : 2);
        const double size = mode == "contained" ? 0.5 : 1;
        mesh.vertices.insert(mesh.vertices.end(), {{offset, offset},
                                                   {offset + size, offset},
                                                   {offset + size, offset + size},
                                                   {offset, offset + size}});
        mesh.quads.push_back({{4, 5, 6, 7}});
        const std::string reason =
            mode == "crossing" ? "cross" : (mode == "contained" ? "overlap" : "disconnected");
        Reject([&] { Validate(mesh, 1 + size * size); }, reason);
      });
    }
    run("reject-hole", [] {
      const UvMesh mesh{{{0, 0}, {3, 0}, {3, 3}, {0, 3}, {1, 1}, {2, 1}, {2, 2}, {1, 2}},
                        {{{0, 1, 5, 4}}, {{1, 2, 6, 5}}, {{2, 3, 7, 6}}, {{3, 0, 4, 7}}}};
      Reject([&] { Validate(mesh, 8); }, "topological disk");
    });
    for (long double tolerance :
         {0.0L, -1.0L, 1.0L, std::numeric_limits<long double>::quiet_NaN()}) {
      run("reject-invalid-tolerance", [&] { Reject([&] { Subdivide(Square(), tolerance); }); });
    }
    run("quad-obj-roundtrip", [] {
      const auto mesh = Subdivide(Fixture(4));
      std::ostringstream output;
      WriteObj(output, mesh);
      std::istringstream lines(output.str());
      std::size_t vertices = 0;
      std::size_t faces = 0;
      std::string line;
      while (std::getline(lines, line)) {
        std::istringstream fields(line);
        std::string kind;
        fields >> kind;
        if (kind == "v") {
          double u = 0;
          double v = 0;
          double z = 1;
          Check(static_cast<bool>(fields >> u >> v >> z), "Invalid OBJ vertex");
          Check(z == 0 && u == mesh.vertices[vertices].u && v == mesh.vertices[vertices].v,
                "OBJ coordinate precision changed");
          ++vertices;
        } else {
          Check(kind == "f", "Unexpected OBJ record");
          std::size_t id = 0;
          std::size_t count = 0;
          while (fields >> id) {
            Check(id >= 1 && id <= mesh.vertices.size(), "Invalid OBJ ID");
            ++count;
          }
          Check(count == 4, "OBJ contains a non-QUAD face");
          ++faces;
        }
      }
      Check(vertices == mesh.vertices.size() && faces == 11, "OBJ inventory changed");
    });
    run("reject-invalid-export", [] {
      UvMesh empty;
      std::ostringstream stream;
      Reject([&] { WriteObj(stream, empty); });
      Check(stream.str().empty(), "Invalid export wrote a prefix");
    });
    run("export-independent-of-stream-format-and-locale", [] {
      const auto mesh = Subdivide(Fixture(1));
      std::ostringstream expected;
      WriteObj(expected, mesh);
      std::ostringstream actual;
      actual.imbue(std::locale(std::locale::classic(), new DecimalComma));
      actual << std::fixed << std::setprecision(2);
      actual.width(8);
      const auto flags = actual.flags();
      WriteObj(actual, mesh);
      Check(actual.str() == expected.str(), "Caller format/locale changed OBJ bytes");
      Check(actual.flags() == flags && actual.precision() == 2 && actual.width() == 8,
            "Writer changed caller stream format");
    });
    run("export-io-failure", [] {
      std::ostringstream stream;
      stream.setstate(std::ios::badbit);
      try {
        WriteObj(stream, Subdivide(Square()));
      } catch (const std::runtime_error&) {
        return;
      }
      throw std::runtime_error("Write failure was ignored");
    });
    std::cout << "quad_contract_outcomes=" << outcomes << " failed=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL after " << outcomes << " outcomes: " << error.what() << '\n';
    return 1;
  }
}
