#include "owned_aft_front.h"
#include "interior_template_dispatch.h"
#include "front_interface_audit.h"

#include "crab_mesh/aft/boundary.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/models_3d.h"
#include "input_output/patch_reader.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
using apmesh::quad::InteriorTemplateDispatcher;
using apmesh::quad::InteriorTemplateMode;
using apmesh::quad::OwnedQuadAftFront;
using apmesh::quad::SnapshotLegacyFront;
using apmesh::quad::UvVertex;
using Par2DJMesh::AFT::Boundary;
using Par2DJMesh::AFT::Quadtree;
using Par2DJMesh::AFT::QuadtreeCell;
using Par2DJMesh::Basics::Face;
using Par2DJMesh::Basics::Vertex;
using Xyz = std::array<double, 3>;

void Require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}
Xyz Values(const PointAdaptive& value) {
  return {value.GetX(), value.GetY(), value.GetZ()};
}
Xyz Values(const VectorAdaptive& value) {
  return {value.GetX(), value.GetY(), value.GetZ()};
}
Xyz Difference(const Xyz& a, const Xyz& b) {
  return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
}
Xyz Cross(const Xyz& a, const Xyz& b) {
  return {a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]};
}
double Dot(const Xyz& a, const Xyz& b) {
  return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
}
double Norm(const Xyz& a) { return std::sqrt(Dot(a, a)); }
bool Finite(const Xyz& a) {
  return std::isfinite(a[0]) && std::isfinite(a[1]) && std::isfinite(a[2]);
}

std::unique_ptr<Quadtree> MakeSourceTree(bool refined) {
  auto tree = std::make_unique<Quadtree>();
  auto boundary = std::make_unique<Boundary>();
  // Each chart sample is one of the oriented four original Bezier sides.
  // This is a fixed 16-segment sampling policy, NOT Adapter::AdaptCurve.
  for (int side = 0; side < 4; ++side) {
    for (int step = 0; step < 4; ++step) {
      const double t = 0.25 * static_cast<double>(step);
      const UvVertex uv = side == 0 ? UvVertex{t, 0.0}
          : side == 1 ? UvVertex{1.0, t}
          : side == 2 ? UvVertex{1.0 - t, 1.0}
                      : UvVertex{0.0, 1.0 - t};
      boundary->addVertex(uv.u, uv.v, nullptr);
    }
  }
  Require(boundary->close(nullptr), "R2b2 source UV boundary could not close");
  tree->setBoundary(boundary.release());
  auto low = std::make_unique<Vertex>(0.0, 0.0);
  auto high = std::make_unique<Vertex>(1.0, 1.0);
  auto root = std::make_unique<QuadtreeCell>(
      tree->getCellId(), tree.get(), low.get(), high.get());
  tree->setRoot(root.get());
  root.release();
  low.release();
  high.release();
  tree->getRoot()->subdivideToLevel(2);
  if (refined) {
    bool found = false;
    for (auto* cell : tree->getLeaves()) {
      if (cell->getMin()->getX() == 0.25 &&
          cell->getMin()->getY() == 0.25) {
        cell->subdivideToLevel(3);
        found = true;
        break;
      }
    }
    Require(found, "R2b2 did not locate the native refined cell");
  }
  return tree;
}

UvVertex PointRule(const apmesh::quad::LeafPolygonOrigin&,
                   const std::vector<UvVertex>& polygon) {
  UvVertex center{0.0, 0.0};
  for (const auto& vertex : polygon) {
    center.u += vertex.u;
    center.v += vertex.v;
  }
  center.u /= static_cast<double>(polygon.size());
  center.v /= static_cast<double>(polygon.size());
  return center;
}

Xyz Evaluate(PatchBezier& patch, UvVertex uv) {
  Require(std::isfinite(uv.u) && std::isfinite(uv.v) &&
              uv.u >= 0.0 && uv.u <= 1.0 &&
              uv.v >= 0.0 && uv.v <= 1.0,
          "R2b2 source patch UV is out of the real Bezier chart");
  const Xyz xyz = Values(patch.Parameterize(uv.u, uv.v));
  const Xyz qu = Values(patch.Qu(uv.u, uv.v));
  const Xyz qv = Values(patch.Qv(uv.u, uv.v));
  Require(Finite(xyz) && Finite(qu) && Finite(qv) &&
              Norm(Cross(qu, qv)) > 1e-12,
          "R2b2 actual Bezier XYZ or differential Jacobian is degenerate");
  return xyz;
}

void ValidateSourceCurves(PatchBezier& patch) {
  // Oriented patch controls and the source CurveAdaptiveParametric instances
  // must map the same geometric sites along all four original patch sides.
  for (unsigned side = 0; side < 4; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    Require(curve != nullptr, "R2b2 physical source curve is not parametric");
    for (unsigned n = 0; n <= 4; ++n) {
      const double t = static_cast<double>(n) / 4.0;
      const UvVertex uv = side == 0 ? UvVertex{t, 0.0}
          : side == 1 ? UvVertex{1.0, t}
          : side == 2 ? UvVertex{t, 1.0}
                      : UvVertex{0.0, t};
      const double curve_t = patch.IsCurveReversed(side) ? 1.0 - t : t;
      const Xyz on_patch = Evaluate(patch, uv);
      const Xyz on_curve = Values(curve->FindPointByParameter(curve_t));
      const double scale = std::max(1.0, Norm(on_patch));
      Require(Finite(on_curve) &&
                  Norm(Difference(on_patch, on_curve)) <= 2e-7 * scale,
              "R2b2 source Bezier physical curve/patch boundary mismatch");
    }
  }
}

struct FaceUv {
  std::array<UvVertex, 3> triangle;
};

void CheckFacet(PatchBezier& patch, const FaceUv& face,
                double& smallest_alignment) {
  const UvVertex middle{
      (face.triangle[0].u + face.triangle[1].u + face.triangle[2].u) / 3.0,
      (face.triangle[0].v + face.triangle[1].v + face.triangle[2].v) / 3.0};
  const Xyz a = Evaluate(patch, face.triangle[0]);
  const Xyz b = Evaluate(patch, face.triangle[1]);
  const Xyz c = Evaluate(patch, face.triangle[2]);
  const Xyz du = Values(patch.Qu(middle.u, middle.v));
  const Xyz dv = Values(patch.Qv(middle.u, middle.v));
  const Xyz reference = Cross(du, dv);
  const Xyz facet = Cross(Difference(b, a), Difference(c, a));
  const double denom = Norm(reference) * Norm(facet);
  Require(std::isfinite(denom) && denom > 1e-14,
          "R2b2 physical mapped face has near-zero projected area");
  const double alignment = Dot(reference, facet) / denom;
  Require(std::isfinite(alignment) && alignment > 0.0,
          "R2b2 mapped Bezier TRI/QUAD facet is inverted");
  smallest_alignment = std::min(smallest_alignment, alignment);
}

struct Witness {
  std::size_t triangles = 0;
  std::size_t quads = 0;
  std::size_t seam = 0;
  std::size_t sampled_facets = 0;
  double min_alignment = 1.0;
};

Witness RunNativePatch(PatchBezier& patch, bool refined) {
  // No physical element is published; source curves/SubMesh are borrowed only.
  auto* original_submesh = patch.GetSubMesh();
  ValidateSourceCurves(patch);
  auto original = MakeSourceTree(refined);
  Require(original->makeTemplateBasedMesh() ==
              Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "R2b2 original native TRI template reference failed");
  const auto original_front = SnapshotLegacyFront(*original);
  auto tree = MakeSourceTree(refined);
  InteriorTemplateDispatcher selector(*tree);
  const auto selected = selector.Select(
      InteriorTemplateMode::ExperimentalQuad, PointRule);
  auto* raw = tree.get();
  auto aft = std::make_unique<OwnedQuadAftFront>(raw->getBoundary(), raw);
  tree.release();
  const auto seeded = aft->Seed(selected, original_front);
  Require(seeded.patch_boundary_edges == 16 &&
              seeded.quad_interface_edges == (refined ? 20U : 16U),
          "R2b2 real Bezier AFT seam/source identity changed");

  for (auto* e : aft->getBoundary()->getEdges()) {
    aft->getQuadtree()->findCell(e);
    Require(e->getCell() != nullptr,
            "R2b2 physical patch source UV edge has no native cell");
  }

  const auto report = aft->AttemptExteriorTriangulation(selected);
  Require(report.exterior_triangles > 0 && report.front_drained &&
              report.triangles_positive && report.seam_orientation_complete &&
              report.seam_edges_with_one_tri == seeded.quad_interface_edges &&
              report.seam_vertices_unchanged && report.uv_area_balanced &&
              report.spatial_overlap_tested && report.no_spatial_overlap,
          "R2b2 original AFT did not close the source-aligned Bezier UV chart");

  Witness witness;
  witness.triangles = aft->Triangles().size();
  witness.quads = selected.uv_quads.quads.size();
  witness.seam = seeded.quad_interface_edges;
  for (const auto& q : selected.uv_quads.quads) {
    const auto& uv = selected.uv_quads.vertices;
    CheckFacet(patch, {{{uv[q.vertices[0]], uv[q.vertices[1]], uv[q.vertices[2]]}}},
               witness.min_alignment);
    CheckFacet(patch, {{{uv[q.vertices[0]], uv[q.vertices[2]], uv[q.vertices[3]]}}},
               witness.min_alignment);
    witness.sampled_facets += 2;
  }
  for (Face* f : aft->Triangles()) {
    CheckFacet(patch, {{{f->getV1()->getX(), f->getV1()->getY()},
                        {f->getV2()->getX(), f->getV2()->getY()},
                        {f->getV3()->getX(), f->getV3()->getY()}}},
               witness.min_alignment);
    ++witness.sampled_facets;
  }
  // Physical boundary/site data must remain independent of failed candidates.
  Require(patch.GetSubMesh() == original_submesh,
          "R2b2 research candidate mutated an accepted physical SubMesh");

  // The research physical evaluator must reject invalid inputs without
  // publishing or changing the previously accepted model.
  bool rejected = false;
  try {
    static_cast<void>(Evaluate(patch, {-0.01, 0.5}));
  } catch (const std::runtime_error&) {
    rejected = true;
  }
  Require(rejected && patch.GetSubMesh() == original_submesh,
          "R2b2 invalid UV escaped physical publication guard");
  return witness;
}

std::pair<unsigned, unsigned> AuditExternal(
    const std::string& model_path, unsigned expected, bool refined) {
  Geometry geometry;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&geometry, model_path) == &geometry &&
              geometry.GetNumberPatches() == expected,
          "R2b2 physical PatchReader model identity changed");
  unsigned qualified = 0;
  unsigned rejected = 0;
  for (unsigned i = 0; i < geometry.GetNumberPatches(); ++i) {
    auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(i));
    Require(patch != nullptr, "R2b2 loaded non-Bezier source patch");
    try {
      const auto witness = RunNativePatch(*patch, refined);
      Require(witness.triangles > 0 && witness.quads > 0 &&
                  witness.seam == (refined ? 20U : 16U) &&
                  witness.sampled_facets ==
                      witness.triangles + 2 * witness.quads,
              "R2b2 mapped physical witness lost mixed face incidence");
      ++qualified;
    } catch (const std::runtime_error& error) {
      // A rejected chart is evidence of a scientific admission blocker,
      // never an accepted physical QUAD/TRI mesh. Preserve the reason.
      ++rejected;
      std::cout << "R2B2_SOURCE_REJECT patch=" << i
                << " reason=" << error.what() << '\n';
    }
  }
  Require(qualified + rejected == expected && qualified > 0,
          "R2b2 physical models have no successfully mapped Bezier chart");
  std::cout << "R2B2_SOURCE_MODEL patches=" << expected
            << " mapped=" << qualified << " rejected=" << rejected
            << " source=PatchReader+PatchBezier+OriginalAFT"
            << " experimental_UV_sampling=1 physical_SubMesh=0\n";
  return {qualified, rejected};
}
}  // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 3,
            "Usage: quad_r2b2_bezier_aft_probe EISTUTE_BP BOOK_BP");
    Geometry built_in;
    Models3d models;
    Require(models.ModelCurvaBezier(&built_in) == &built_in &&
                built_in.GetNumberPatches() == 1U,
            "R2b2 expected one real built-in curved Bezier patch");
    auto* native = dynamic_cast<PatchBezier*>(built_in.GetPatch(0));
    Require(native != nullptr, "R2b2 original built-in patch type changed");
    const Witness builtin = RunNativePatch(*native, true);
    Require(builtin.triangles > 0 && builtin.quads > 0 &&
                builtin.seam == 20 && builtin.min_alignment > 0.0,
            "R2b2 built-in curved Bezier source failed");
    const auto eistute = AuditExternal(argv[1], 4U, false);
    const auto book = AuditExternal(argv[2], 28U, true);
    std::cout << "quad.r2b2.real_bezier_aft=source_probe_pass"
              << " builtin_mapped=1 eistute_mapped=" << eistute.first
              << " book_mapped=" << book.first
              << " rejected_external=" << eistute.second + book.second
              << " original_AFT=1 native_PatchBezier_XYZ=1"
              << " NOT_Adapter_AdaptCurve NOT_mixed_SubMesh"
              << " NOT_full_model_acceptance NOT_quad_uv_CLI\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "quad.r2b2.real_bezier_aft=failed: " << error.what() << '\n';
    return 1;
  }
}
