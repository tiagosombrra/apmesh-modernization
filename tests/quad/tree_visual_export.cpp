#include "experimental_point_rule.h"
#include "quadtree_quad.h"
#include "tree_fixture.h"
#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using apmesh::quad::UvMesh;
using apmesh::quad::UvVertex;
using apmesh::quad::ExperimentalPointRule;
struct Region {
  std::size_t ordinal;
  long cell_id;
  long level;
  double x0, y0, x1, y1;
  bool inside;
  std::string pattern;
  std::size_t quads = 0;
};
void Check(bool ok, const char* why) {
  if (!ok) throw std::runtime_error(why);
}
std::string Label(apmesh::quad::LeafPattern p) {
  return "T" + std::to_string(static_cast<int>(p));
}
std::vector<Region> ReadRealCells(quad_test::TreeFixture& fixture) {
  const auto capture = apmesh::quad::CaptureLeafPolygons(fixture.tree);
  const auto leaves = fixture.tree.getLeaves();
  Check(leaves.size() == capture.source_leaves, "Capture leaf count mismatch");
  std::vector<Region> result;
  for (auto* c : leaves) {
    const std::size_t i = result.size();
    Check(c && c->getMin() && c->getMax(), "Null real Quadtree cell");
    bool inside = true;
    for (int side = 0; side < 4; ++side)
      if (c->getNeighbors(side).empty()) inside = false;
    result.push_back({i, c->getId(), c->getLevel(),
      c->getMin()->getX(), c->getMin()->getY(),
      c->getMax()->getX(), c->getMax()->getY(), inside, "", 0});
  }
  for (std::size_t i = 0; i < capture.origins.size(); ++i) {
    const auto& origin = capture.origins[i];
    Check(origin.leaf_ordinal < result.size(), "Out-of-range captured origin");
    auto& leaf = result[origin.leaf_ordinal];
    Check(leaf.inside && leaf.cell_id == origin.cell_id,
          "Captured polygon does not belong to included leaf");
    const std::string pattern = Label(origin.pattern);
    Check(leaf.pattern.empty() || leaf.pattern == pattern,
          "One leaf has incompatible classified patterns");
    leaf.pattern = pattern;
    leaf.quads += capture.input.polygons[i].size();
  }
  std::size_t excluded = 0, emitted = 0;
  for (const auto& leaf : result) {
    if (!leaf.inside) {
      Check(leaf.pattern.empty() && leaf.quads == 0,
            "Excluded boundary was incorrectly meshed");
      ++excluded;
    } else {
      Check(!leaf.pattern.empty() && leaf.quads > 0,
            "Interior leaf has no actual QUAD topology");
      emitted += leaf.quads;
    }
  }
  Check(result.size() == 19 && excluded == 12 && emitted == 42 &&
        capture.excluded_boundary_leaves == excluded &&
        std::abs(capture.interior_area - 0.25L) < 1.0e-15L,
        "Frozen real Quadtree fixture inventory changed");
  return result;
}
UvMesh Emit(quad_test::TreeFixture& fixture, ExperimentalPointRule rule) {
  auto mesh = apmesh::quad::EmitLeafQuads(fixture.tree,
    [rule](const auto&, const std::vector<UvVertex>& polygon) {
      return apmesh::quad::ExperimentalInteriorPoint(polygon, rule);
    });
  const auto topology = apmesh::quad::Validate(mesh, 0.25L);
  Check(mesh.quads.size() == 42 &&
        std::abs(topology.area - 0.25L) < 1.0e-15L,
        "Real source QUAD mesh area/count invalid");
  return mesh;
}
void Obj(const std::filesystem::path& path, const UvMesh& mesh) {
  std::ofstream out(path, std::ios::binary | std::ios::trunc);
  Check(static_cast<bool>(out), "Cannot open real QUAD OBJ");
  apmesh::quad::WriteObj(out, mesh);
  out.close();
  Check(static_cast<bool>(out), "Cannot close real QUAD OBJ");
}
void Csv(const std::filesystem::path& path, const std::vector<Region>& regions) {
  std::ofstream out(path);
  Check(static_cast<bool>(out), "Cannot open real Quadtree CSV");
  out.imbue(std::locale::classic());
  out << std::setprecision(17);
  out << "ordinal,cell_id,level,min_u,min_v,max_u,max_v,region,pattern,quads\n";
  for (const auto& p : regions)
    out << p.ordinal << ',' << p.cell_id << ',' << p.level << ','
        << p.x0 << ',' << p.y0 << ',' << p.x1 << ',' << p.y1 << ','
        << (p.inside ? "quad_candidate" : "excluded_boundary_unmeshed") << ','
        << p.pattern << ',' << p.quads << '\n';
  out.close();
  Check(static_cast<bool>(out), "Cannot close real Quadtree CSV");
}
double X(double u, double offset) { return offset + 55.0 + 585.0 * u; }
double Y(double v) { return 130.0 + 585.0 * (1.0 - v); }
void Svg(const std::filesystem::path& path, const std::vector<Region>& regions,
         const UvMesh& mean, const UvMesh& centroid) {
  std::ofstream out(path);
  Check(static_cast<bool>(out), "Cannot open real Quadtree SVG");
  out.imbue(std::locale::classic());
  out << std::fixed << std::setprecision(5);
  out << "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"2115\" height=\"790\""
      << " viewBox=\"0 0 2115 790\""
      << " data-source=\"real-apmesh-cpp-quadtree-fixture\">\n"
      << "<rect width=\"2115\" height=\"790\" fill=\"#fafcfe\" />\n"
      << "<text x=\"35\" y=\"42\" font-family=\"Arial\" font-size=\"27\""
      << " fill=\"#1b3850\">APMesh - Quadtree real (fixture C++)</text>\n"
      << "<text x=\"35\" y=\"71\" font-family=\"Arial\" font-size=\"17\""
      << " fill=\"#52687b\">19 folhas: 7 QUAD interiores, 12 exteriores SEM TRI.</text>\n";
  const double offsets[] = {0, 702, 1404};
  const char* ids[] = {"source-tree", "quad-vertex-mean", "quad-area-centroid"};
  const char* titles[] = {"A. Celulas reais e classificacao",
                          "B. 42 QUAD UV - media (teste)",
                          "C. 42 QUAD UV - centroide (teste)"};
  for (int panel = 0; panel < 3; ++panel) {
    const double xoff = offsets[panel];
    out << "<g id=\"" << ids[panel] << "\"><text x=\"" << xoff + 55
        << "\" y=\"110\" font-family=\"Arial\" font-size=\"17\""
        << " fill=\"#183e57\">" << titles[panel] << "</text>\n";
    for (const auto& p : regions) {
      const double x = X(p.x0, xoff), y = Y(p.y1);
      out << "<rect x=\"" << x << "\" y=\"" << y << "\" width=\""
          << 585 * (p.x1 - p.x0) << "\" height=\""
          << 585 * (p.y1 - p.y0) << "\" fill=\""
          << (p.inside ? "#d0efdf" : "#f4d9d0")
          << "\" stroke=\"#415466\" stroke-width=\"1.35\"/>\n";
      if (panel == 0)
        out << "<text x=\"" << X((p.x0 + p.x1) / 2, xoff)
            << "\" y=\"" << Y((p.y0 + p.y1) / 2)
            << "\" font-family=\"Arial\" font-size=\"12\" text-anchor=\"middle\""
            << " fill=\"#233d4f\">" << (p.inside ? p.pattern : "EXT")
            << "</text>\n";
    }
    const UvMesh* mesh = panel == 1 ? &mean : panel == 2 ? &centroid : nullptr;
    if (mesh)
      for (const auto& face : mesh->quads) {
        out << "<polygon points=\"";
        for (auto id : face.vertices) {
          const auto& v = mesh->vertices.at(id);
          out << X(v.u, xoff) << ',' << Y(v.v) << ' ';
        }
        out << "\" fill=\"#b7d9f5\" stroke=\"#164568\""
            << " stroke-width=\"1.1\" />\n";
      }
    out << "</g>\n";
  }
  out << "<text x=\"35\" y=\"750\" font-family=\"Arial\" font-size=\"15\""
      << " fill=\"#38546a\">Verde: QUAD interior. Rosa: contorno excluido,"
      << " sem Delaunay/TRI gerado.</text>\n"
      << "<text x=\"35\" y=\"777\" font-family=\"Arial\" font-size=\"13\""
      << " fill=\"#607280\">Origem: Quadtree + CaptureLeafPolygons +"
      << " EmitLeafQuads + Validate + WriteObj (C++). UV, nao XYZ.</text>\n"
      << "</svg>\n";
  out.close();
  Check(static_cast<bool>(out), "Cannot close real Quadtree SVG");
}
void Manifest(const std::filesystem::path& path, const UvMesh& mean,
              const UvMesh& area) {
  std::ofstream out(path);
  Check(static_cast<bool>(out), "Cannot open real Quadtree JSON");
  out << "{\n"
      << " \"schema\":1,\n"
      << " \"source\":\"real_APMesh_CXX_Quadtree_fixture\",\n"
      << " \"status\":\"UV_research_not_physical_hybrid\",\n"
      << " \"source_leaves\":19,\n"
      << " \"included_quad_leaves\":7,\n"
      << " \"excluded_boundary_unmeshed_leaves\":12,\n"
      << " \"triangles_emitted\":0,\n"
      << " \"mean_quads\":" << mean.quads.size() << ",\n"
      << " \"centroid_quads\":" << area.quads.size() << ",\n"
      << " \"uv_interior_area\":0.25,\n"
      << " \"historical_centroid_approved\":false\n"
      << "}\n";
  out.close();
  Check(static_cast<bool>(out), "Cannot close real Quadtree JSON");
}
}

int main(int argc, char** argv) {
  try {
    if (argc != 2) {
      std::cerr << "Usage: quad_tree_visual_export OUTPUT_DIRECTORY\n";
      return 2;
    }
    quad_test::TreeFixture fixture;
    fixture.CentralLeaf()->subdivideToLevel(3);
    const auto rows = ReadRealCells(fixture);
    const auto mean = Emit(fixture, ExperimentalPointRule::VertexArithmeticMean);
    const auto centroid = Emit(fixture, ExperimentalPointRule::PolygonAreaCentroid);
    const std::filesystem::path folder(argv[1]);
    std::filesystem::create_directories(folder);
    Obj(folder / "quads_vertex_mean.obj", mean);
    Obj(folder / "quads_area_centroid.obj", centroid);
    Csv(folder / "tree_regions.csv", rows);
    Svg(folder / "tree_visual.svg", rows, mean, centroid);
    Manifest(folder / "manifest.json", mean, centroid);
    std::cout << "real_tree_leaves=19 quad_leaves=7 boundary_unmeshed=12"
              << " quads=42 triangles_emitted=0 area=0.25\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Real tree visualization failed: " << error.what() << '\n';
    return 1;
  }
}
