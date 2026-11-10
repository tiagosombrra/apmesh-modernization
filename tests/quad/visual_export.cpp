#include "experimental_point_rule.h"
#include "uv_mesh.h"

#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
using apmesh::quad::ExperimentalInteriorPoint;
using apmesh::quad::ExperimentalPointRule;
using apmesh::quad::PolygonMesh;
using apmesh::quad::UvVertex;
using apmesh::quad::VertexId;

struct Pattern {
  const char* name;
  std::vector<std::string> cycles;
  std::size_t expected_quads;
};

const std::array<Pattern, 6> kPatterns{{
    {"T1", {"ABCD"}, 4},
    {"T2", {"ABOW", "BCO", "WOCD"}, 11},
    {"T4", {"ABOW", "WOND", "OBCN"}, 12},
    {"T3", {"ABEW", "WECD"}, 8},
    {"T5", {"ASW", "WSND", "SBCN"}, 11},
    {"T6", {"ASOW", "SBEO", "OECN", "WOND"}, 16},
}};

const std::map<char, UvVertex> kPoints{
    {'A', {0, 0}},   {'B', {1, 0}},   {'C', {1, 1}},
    {'D', {0, 1}},   {'S', {0.5, 0}}, {'E', {1, 0.5}},
    {'N', {0.5, 1}}, {'W', {0, 0.5}}, {'O', {0.5, 0.5}},
};

PolygonMesh MakeFixture(const Pattern& pattern, ExperimentalPointRule rule) {
  PolygonMesh input;
  std::map<char, VertexId> ids;
  for (const auto& cycle : pattern.cycles) {
    std::vector<VertexId> polygon;
    std::vector<UvVertex> corners;
    for (char label : cycle) {
      const UvVertex point = kPoints.at(label);
      corners.push_back(point);
      auto found = ids.find(label);
      if (found == ids.end()) {
        const VertexId id = input.vertices.size();
        ids.emplace(label, id);
        input.vertices.push_back(point);
        polygon.push_back(id);
      } else {
        polygon.push_back(found->second);
      }
    }
    // Both center rules are explicitly selected experimental witnesses.
    input.interior_points.push_back(ExperimentalInteriorPoint(corners, rule));
    input.polygons.push_back(std::move(polygon));
  }
  return input;
}

void Export(const std::filesystem::path& directory, const Pattern& pattern,
            ExperimentalPointRule rule, const char* label) {
  const auto mesh = apmesh::quad::Subdivide(MakeFixture(pattern, rule));
  const auto topology = apmesh::quad::Validate(mesh, 1.0L);
  if (mesh.quads.size() != pattern.expected_quads) {
    throw std::runtime_error("Unexpected number of quads");
  }
  const auto path = directory / (std::string(pattern.name) + "_" + label + ".obj");
  std::ofstream output(path, std::ios::binary);
  if (!output) {
    throw std::runtime_error("Cannot open OBJ output");
  }
  apmesh::quad::WriteObj(output, mesh);
  output.close();
  if (!output) {
    throw std::runtime_error("Cannot finish OBJ output");
  }
  std::cout << pattern.name << " center=" << label << " quads="
            << mesh.quads.size() << " boundary=" << topology.boundary_edges << '\n';
}
} // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 2) {
      std::cerr << "Usage: quad_visual_export OUTPUT_DIRECTORY\n";
      return 2;
    }
    const std::filesystem::path output(argv[1]);
    std::filesystem::create_directories(output);
    for (const auto& pattern : kPatterns) {
      Export(output, pattern, ExperimentalPointRule::VertexArithmeticMean, "vertex_mean");
      Export(output, pattern, ExperimentalPointRule::PolygonAreaCentroid, "area_centroid");
    }
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
