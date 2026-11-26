#include "controlled_patch_application.h"
#include "boundary_pair_candidates.h"
#include "live_boundary_pairing.h"
#include "article_mixed_front.h"
#include "mixed_uv_smoothing.h"
#include "experimental_point_rule.h"
#include "application/runtime_config.h"
#include "physical_quadrilateral_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/triangle_adaptive.h"
#include <functional>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <locale>
#include <set>
#include <sstream>
#include <tuple>
#include "owned_aft_front.h"
#include "interior_template_dispatch.h"
#include "front_interface_audit.h"
#include "typed_mixed_curvature.h"
#include "typed_mixed_quality.h"
#include "mixed_surface_residual.h"
#include "real_boundary_source.h"
#include "generator/generator_adaptive.h"

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
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <iterator>
#include <map>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace apmesh::quad {
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
  if (!condition)
    throw std::runtime_error(message);
}
Xyz Values(const PointAdaptive& value) { return {value.GetX(), value.GetY(), value.GetZ()}; }
Xyz Values(const VectorAdaptive& value) { return {value.GetX(), value.GetY(), value.GetZ()}; }
Xyz Difference(const Xyz& a, const Xyz& b) { return {a[0] - b[0], a[1] - b[1], a[2] - b[2]}; }
Xyz Cross(const Xyz& a, const Xyz& b) {
  return {a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]};
}
double Dot(const Xyz& a, const Xyz& b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
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
      const UvVertex uv = side == 0   ? UvVertex{t, 0.0}
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
  auto root = std::make_unique<QuadtreeCell>(tree->getCellId(), tree.get(), low.get(), high.get());
  tree->setRoot(root.get());
  root.release();
  low.release();
  high.release();
  tree->getRoot()->subdivideToLevel(2);
  if (refined) {
    bool found = false;
    for (auto* cell : tree->getLeaves()) {
      if (cell->getMin()->getX() == 0.25 && cell->getMin()->getY() == 0.25) {
        cell->subdivideToLevel(3);
        found = true;
        break;
      }
    }
    Require(found, "R2b2 did not locate the native refined cell");
  }
  return tree;
}

UvVertex PointRule(const apmesh::quad::LeafPolygonOrigin&, const std::vector<UvVertex>& polygon) {
  UvVertex center{0.0, 0.0};
  for (const auto& vertex : polygon) {
    center.u += vertex.u;
    center.v += vertex.v;
  }
  center.u /= static_cast<double>(polygon.size());
  center.v /= static_cast<double>(polygon.size());
  return center;
}

UvVertex AreaPointRule(const apmesh::quad::LeafPolygonOrigin&,
                       const std::vector<UvVertex>& polygon) {
  return ExperimentalInteriorPoint(polygon, ExperimentalPointRule::PolygonAreaCentroid);
}

Xyz Evaluate(PatchBezier& patch, UvVertex uv) {
  Require(std::isfinite(uv.u) && std::isfinite(uv.v) && uv.u >= 0.0 && uv.u <= 1.0 && uv.v >= 0.0 &&
              uv.v <= 1.0,
          "R2b2 source patch UV is out of the real Bezier chart");
  const Xyz xyz = Values(patch.Parameterize(uv.u, uv.v));
  const Xyz qu = Values(patch.Qu(uv.u, uv.v));
  const Xyz qv = Values(patch.Qv(uv.u, uv.v));
  Require(Finite(xyz) && Finite(qu) && Finite(qv) && Norm(Cross(qu, qv)) > 1e-12,
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
      const UvVertex uv = side == 0   ? UvVertex{t, 0.0}
                          : side == 1 ? UvVertex{1.0, t}
                          : side == 2 ? UvVertex{t, 1.0}
                                      : UvVertex{0.0, t};
      const double curve_t = patch.IsCurveReversed(side) ? 1.0 - t : t;
      const Xyz on_patch = Evaluate(patch, uv);
      const Xyz on_curve = Values(curve->FindPointByParameter(curve_t));
      const double scale = std::max(1.0, Norm(on_patch));
      Require(Finite(on_curve) && Norm(Difference(on_patch, on_curve)) <= 2e-7 * scale,
              "R2b2 source Bezier physical curve/patch boundary mismatch");
    }
  }
}

struct FaceUv {
  std::array<UvVertex, 3> triangle;
};

void CheckFacet(PatchBezier& patch, const FaceUv& face, double& smallest_alignment) {
  const UvVertex middle{(face.triangle[0].u + face.triangle[1].u + face.triangle[2].u) / 3.0,
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

struct IdealFrontLimits {
  std::size_t points;
  double min_angle;
  double min_shape;
  // Shape and angle, in the same order as the scoring routine.
  std::optional<std::array<double, 2>> quad_floors;
  bool order_only = false;
};

struct Candidate {
  std::unique_ptr<SubMesh> mesh = std::make_unique<SubMesh>();
  std::vector<UvVertex> uv;
  std::vector<unsigned long> node_ids;
  std::vector<std::vector<std::size_t>> faces;
  std::vector<LeafPolygonOrigin> quad_origins;
  std::vector<BoundaryPairCandidate> aft_pair_origins;
  std::vector<LivePairEvent> live_pair_events;
  std::vector<ArticleFrontCommit> article_commits;
  std::vector<ArticleMixedFront::Box> article_leaves;
  std::vector<UvVertex> article_uv_before_smoothing;
  std::vector<Xyz> article_xyz_before_smoothing;
  bool guarded_smoothing_comparison = false;
  bool additional_pair_search = false;
  std::optional<double> additional_pair_error_limit;
  std::optional<IdealFrontLimits> ideal_front_limits;
  MixedUvSmoothingTrace article_smoothing;
  std::vector<std::vector<Xyz>> article_smoothing_xyz;
  std::size_t clearance_excluded_cells = 0;
  bool article_area_centroid = false;
  std::vector<std::vector<std::size_t>> source_faces;
  std::size_t seed_quads = 0;
  std::size_t quads = 0;
  double min_alignment = 1.0;
  double min_quality = 1.0;
  bool real_boundary = false;
  const RealBoundarySource* source_witness = nullptr;
  int generation_step = -1;
  bool reference_accepted = false;
  std::string stage_reason;
};

struct PublicationFailure : std::runtime_error {
  using std::runtime_error::runtime_error;
};

template <class Boxes>
RealBoundarySource GroupTemplateBlocks(const RealBoundarySource& source, const Boxes& boxes) {
  Require(source.source_leaves / 4 >= boxes.size() &&
              std::is_sorted(source.leaf_order.begin(), source.leaf_order.end()),
          "Grouping requires its ordered native tree");
  auto result = source;
  result.cells.clear();
  result.leaf_order.clear();
  std::size_t grouped = 0;
  const auto copy = [&](auto&& recurse, std::size_t original) -> std::size_t {
    const auto& cell = source.cells.at(original);
    const auto index = result.cells.size();
    result.cells.push_back(cell);
    if (std::find(boxes.begin(), boxes.end(), cell.box) != boxes.end()) {
      Require(cell.subdivided && std::all_of(cell.children.begin(), cell.children.end(),
                                             [&](std::size_t child) {
                                               return !source.cells.at(child).subdivided;
                                             }),
              "Grouping requires four leaf children in each approved block");
      result.cells[index].children = {};
      result.cells[index].subdivided = false;
      ++grouped;
    }
    if (result.cells[index].subdivided) {
      for (std::size_t i = 0; i < cell.children.size(); ++i) {
        const auto child = recurse(recurse, cell.children[i]);
        result.cells[index].children[i] = child;
      }
    } else {
      result.leaf_order.push_back(cell.source_id);
    }
    return index;
  };
  copy(copy, 0);
  // Subdivision appends children in increasing captured cell ID order.
  std::sort(result.leaf_order.begin(), result.leaf_order.end());
  result.source_leaves = result.leaf_order.size();
  Require(grouped == boxes.size() &&
              result.source_leaves + 3 * boxes.size() == source.source_leaves &&
              source.cells.size() - result.cells.size() == 4 * boxes.size(),
          "Grouping changed more than the approved children");
  return result;
}

bool ShareTreeSide(const std::array<double, 4>& a, const std::array<double, 4>& b) {
  return ((a[0] == b[2] || b[0] == a[2]) && std::max(a[1], b[1]) < std::min(a[3], b[3])) ||
         ((a[1] == b[3] || b[1] == a[3]) && std::max(a[0], b[0]) < std::min(a[2], b[2]));
}

void CheckGroupedBalance(const RealBoundarySource& grouped) {
  for (const auto& cell : grouped.cells) {
    if (cell.subdivided)
      continue;
    for (const auto& other : grouped.cells)
      Require(other.subdivided || cell.level <= other.level + 1 ||
                  !ShareTreeSide(cell.box, other.box),
              "Grouping would violate native 2:1 balance");
  }
}

class MixedGeometryRejection : public std::runtime_error {
public:
  using std::runtime_error::runtime_error;
};

void RequireMixedGeometry(bool condition, const char* message) {
  if (!condition)
    throw MixedGeometryRejection(message);
}

using PhysicalLift = std::function<Xyz(UvVertex)>;
using TrialFaces = std::vector<std::vector<VertexId>>;
using TrialScores = std::array<double, 5>;

void CheckMixedSmoothingFace(PatchBezier& patch, const std::vector<VertexId>& face,
                             const std::vector<UvVertex>& positions,
                             const std::vector<Xyz>& physical,
                             std::vector<std::array<UvVertex, 3>>* facets,
                             TrialScores* scores = nullptr) {
  double alignment = 1.0;
  const auto check = [&](std::size_t a, std::size_t b, std::size_t c) {
    const std::array<UvVertex, 3> triangle{positions[face[a]], positions[face[b]],
                                           positions[face[c]]};
    try {
      CheckFacet(patch, FaceUv{triangle}, alignment);
    } catch (const std::runtime_error& error) {
      throw MixedGeometryRejection(error.what());
    }
    if (facets)
      facets->push_back(triangle);
  };
  check(0, 1, 2);
  if (face.size() == 4) {
    check(0, 2, 3);
    research::PhysicalQuadCorners corners{}, normals{};
    for (std::size_t i = 0; i < 4; ++i) {
      const auto uv = positions[face[i]];
      const auto next = positions[face[(i + 1) % 4]], prev = positions[face[(i + 3) % 4]];
      RequireMixedGeometry((next.u - uv.u) * (prev.v - uv.v) - (next.v - uv.v) * (prev.u - uv.u) >
                               1e-14,
                           "Mixed smoothing inverted or collapsed a UV quad");
      corners[i] = physical[face[i]];
      normals[i] = Cross(Values(patch.Qu(uv.u, uv.v)), Values(patch.Qv(uv.u, uv.v)));
    }
    try {
      const auto q = research::ObservePhysicalQuadQuality(corners, normals);
      if (scores) {
        (*scores)[2] = std::min((*scores)[2], q.min_scaled_jacobian);
        (*scores)[4] = std::min((*scores)[4], -q.edge_ratio);
      }
    } catch (const std::invalid_argument& error) {
      throw MixedGeometryRejection(error.what());
    }
  }
  if (!scores)
    return;
  if (face.size() == 3) {
    const auto a = positions[face[0]], b = positions[face[1]], c = positions[face[2]];
    RequireMixedGeometry((b.u - a.u) * (c.v - a.v) - (b.v - a.v) * (c.u - a.u) > 1e-14,
                         "Local mixed smoothing inverted or collapsed a UV triangle");
    const auto ab = Difference(physical[face[1]], physical[face[0]]);
    const auto ac = Difference(physical[face[2]], physical[face[0]]);
    const auto bc = Difference(physical[face[2]], physical[face[1]]);
    const auto q =
        2 * std::sqrt(3.0) * Norm(Cross(ab, ac)) / (Dot(ab, ab) + Dot(ac, ac) + Dot(bc, bc));
    (*scores)[0] = std::min((*scores)[0], q);
  }
  auto& angle = (*scores)[face.size() == 3 ? 1 : 3];
  for (std::size_t i = 0; i < face.size(); ++i) {
    const auto& point = physical[face[i]];
    const auto a = Difference(physical[face[(i + 1) % face.size()]], point);
    const auto b = Difference(physical[face[(i + face.size() - 1) % face.size()]], point);
    angle = std::min(angle, std::atan2(Norm(Cross(a, b)), Dot(a, b)) * 180 / std::acos(-1.0));
  }
}

ArticleFrontFaces ChangedClosureFaces(const ArticleFrontFaces& faces,
                                      const ArticleFrontFaces& other) {
  const auto canonical = [](ArticleFrontFaces polygons) {
    for (auto& polygon : polygons)
      std::rotate(polygon.begin(), std::min_element(polygon.begin(), polygon.end()), polygon.end());
    std::sort(polygons.begin(), polygons.end());
    return polygons;
  };
  const auto a = canonical(faces), b = canonical(other);
  ArticleFrontFaces changed;
  std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(changed));
  return changed;
}

auto ClosureBoundary(const ArticleFrontFaces& faces) {
  std::map<std::pair<VertexId, VertexId>, int> boundary;
  for (const auto& face : faces) {
    for (std::size_t i = 0; i < face.size(); ++i) {
      const auto a = face[i], b = face[(i + 1) % face.size()];
      const auto key = std::make_pair(std::min(a, b), std::max(a, b));
      auto& balance = boundary[key];
      balance += a < b ? 1 : -1;
      if (balance == 0)
        boundary.erase(key);
    }
  }
  return boundary;
}

std::size_t ClosureRegion(const std::vector<VertexId>& face, const std::vector<UvVertex>& uv) {
  bool touches_contour = false;
  const auto on_side = [](double x) { return x == 0 || x == 1; };
  for (std::size_t i = 0; i < face.size(); ++i) {
    const auto a = uv[face[i]], b = uv[face[(i + 1) % face.size()]];
    if ((a.u == b.u && on_side(a.u)) || (a.v == b.v && on_side(a.v)))
      return 0; // Contour edge.
    touches_contour |= on_side(a.u) || on_side(a.v);
  }
  return touches_contour ? 1 : 2; // Contour vertex, then interior.
}

bool PreservesClosureQuality(PatchBezier& patch, const PhysicalLift& lift,
                             const IdealFrontLimits& limits, const std::vector<UvVertex>& uv,
                             const ArticleFrontFaces& control, const ArticleFrontFaces& trial) {
  const auto replaced = ChangedClosureFaces(control, trial);
  const auto replacement = ChangedClosureFaces(trial, control);
  if (replaced.empty() || replacement.empty() ||
      ClosureBoundary(replaced) != ClosureBoundary(replacement))
    return false;
  std::vector<Xyz> xyz;
  xyz.reserve(uv.size());
  for (const auto p : uv)
    xyz.push_back(lift(p));
  const auto score = [&](const ArticleFrontFaces& faces) {
    std::array<TrialScores, 3> regional;
    for (auto& values : regional)
      values.fill(std::numeric_limits<double>::infinity());
    std::vector<std::array<UvVertex, 3>> facets;
    for (const auto& face : faces)
      CheckMixedSmoothingFace(patch, face, uv, xyz, &facets, &regional[ClosureRegion(face, uv)]);
    RequireMixedGeometry(AuditUvOverlap({}, facets).no_overlap, "Overlapping preview closure");
    return regional;
  };
  try {
    const auto before = score(replaced), after = score(replacement);
    const auto& quad = *limits.quad_floors;
    const std::array<double, 4> floors{limits.min_shape, limits.min_angle, quad[0], quad[1]};
    bool improves = false;
    for (std::size_t region = 0; region < before.size(); ++region) {
      for (std::size_t metric = 0; metric < floors.size(); ++metric) {
        if (!std::isfinite(after[region][metric]))
          continue;
        const bool comparable = std::isfinite(before[region][metric]);
        const auto reference = comparable ? before[region][metric] : floors[metric];
        const auto tolerance = 1e-12 * std::max(1.0, std::abs(reference));
        if (after[region][metric] < reference - tolerance)
          return false;
        improves |= comparable && after[region][metric] > reference + tolerance;
      }
    }
    return !limits.order_only || improves;
  } catch (const MixedGeometryRejection&) {
    return false;
  }
}

std::vector<Xyz> ValidateMixedSmoothing(PatchBezier& patch, const TrialFaces& faces,
                                        const std::vector<UvVertex>& positions,
                                        const PhysicalLift& lift) {
  std::vector<Xyz> physical;
  for (const auto uv : positions)
    physical.push_back(lift(uv));
  std::vector<std::array<UvVertex, 3>> facets;
  for (std::size_t i = 0; i < faces.size(); ++i) {
    try {
      CheckMixedSmoothingFace(patch, faces[i], positions, physical, &facets);
    } catch (const MixedGeometryRejection& error) {
      throw MixedGeometryRejection(std::string(error.what()) + " at face " + std::to_string(i));
    }
  }
  RequireMixedGeometry(AuditUvOverlap({}, facets).no_overlap,
                       "Mixed smoothing overlaps physical facets");
  return physical;
}

void SaveMixedSmoothingFrame(const std::filesystem::path& path, const TrialFaces& faces,
                             const std::vector<UvVertex>& uv, const std::vector<Xyz>& xyz) {
  std::ofstream out(path, std::ios::binary);
  out.imbue(std::locale::classic());
  out << std::setprecision(17);
  for (const auto& p : xyz)
    out << "v " << p[0] << ' ' << p[1] << ' ' << p[2] << '\n';
  for (const auto p : uv)
    out << "vt " << p.u << ' ' << p.v << '\n';
  for (const auto& face : faces) {
    out << 'f';
    for (auto id : face)
      out << ' ' << id + 1 << '/' << id + 1;
    out << '\n';
  }
  out.close();
  Require(bool(out), "Cannot retain mixed smoothing frame");
}

bool BetterMixedNeighborhood(const TrialScores& old, const TrialScores& next) {
  bool improves = false;
  for (std::size_t i = 0; i < old.size(); ++i) {
    if (!std::isfinite(old[i]))
      continue;
    const double tolerance = 1e-12 * std::max({1.0, std::abs(old[i]), std::abs(next[i])});
    if (next[i] < old[i] - tolerance)
      return false;
    improves |= next[i] > old[i] + tolerance;
  }
  return improves;
}

std::vector<UvVertex> CompareMixedSmoothing(PatchBezier& patch, const ArticleFrontResult& article,
                                            const PhysicalLift& lift,
                                            const RealBoundarySource& source,
                                            const std::filesystem::path& directory) {
  std::ofstream journal(directory / "passes.csv", std::ios::binary);
  journal << "arm,pass,status,full,half,quarter,eighth,skipped,reason\n";
  std::vector<Xyz> lifted;
  for (auto p : article.vertices)
    lifted.push_back(lift(p));
  SaveMixedSmoothingFrame(directory / "before.obj", article.faces, article.vertices, lifted);
  try {
    (void)ValidateMixedSmoothing(patch, article.faces, article.vertices, lift);
    journal << "both,0,valid,0,0,0,0,0,\n";
  } catch (const MixedGeometryRejection& error) {
    journal << "both,0,rejected,0,0,0,0,0," << error.what() << '\n';
    journal.close();
    throw;
  }
  std::vector<std::vector<std::size_t>> incidence(article.vertices.size());
  for (std::size_t i = 0; i < article.faces.size(); ++i)
    for (const auto id : article.faces[i])
      incidence[id].push_back(i);
  std::set<VertexId> fixed;
  for (VertexId i = 0; i < article.vertices.size(); ++i)
    for (const auto& site : source.sites)
      if (site.uv.u == article.vertices[i].u && site.uv.v == article.vertices[i].v)
        fixed.insert(i);
  Require(fixed.size() == source.sites.size(), "Comparison lost a source contour vertex");

  auto last = article.vertices;
  for (const bool guarded : {false, true}) {
    const auto arm = guarded ? "guarded" : "control";
    last = article.vertices;
    std::size_t current_pass = 0;
    std::array<std::size_t, 5> counts{};
    MixedUvPassFilter filter;
    if (guarded)
      filter = [&](std::size_t pass, const auto& current, auto& means) {
        current_pass = pass;
        counts.fill(0);
        auto working = current;
        std::vector<Xyz> physical;
        for (const auto p : working)
          physical.push_back(lift(p));
        const auto score = [&](VertexId node) {
          TrialScores values;
          values.fill(std::numeric_limits<double>::infinity());
          for (auto f : incidence[node])
            CheckMixedSmoothingFace(patch, article.faces[f], working, physical, nullptr, &values);
          return values;
        };
        constexpr std::array<double, 4> fractions{1.0, 0.5, 0.25, 0.125};
        for (VertexId id = 0; id < working.size(); ++id) {
          const auto origin = working[id], target = means[id];
          if (fixed.count(id) || (origin.u == target.u && origin.v == target.v))
            continue;
          const auto before = score(id);
          const auto start = physical[id];
          std::size_t accepted = fractions.size();
          for (std::size_t t = 0; t < fractions.size(); ++t) {
            const double a = fractions[t];
            working[id] = t == 0 ? target
                                 : UvVertex{origin.u + a * (target.u - origin.u),
                                            origin.v + a * (target.v - origin.v)};
            physical[id] = lift(working[id]);
            try {
              if (BetterMixedNeighborhood(before, score(id))) {
                accepted = t;
                break;
              }
            } catch (const MixedGeometryRejection&) {
              // Try a shorter displacement for this same node.
            }
          }
          if (accepted == fractions.size()) {
            working[id] = origin;
            physical[id] = start;
          }
          ++counts[accepted];
        }
        means.swap(working);
      };
    try {
      (void)SmoothMixedUv(
          article.vertices, article.faces,
          [&](std::size_t pass, const auto& uv) {
            current_pass = pass;
            const auto physical = ValidateMixedSmoothing(patch, article.faces, uv, lift);
            SaveMixedSmoothingFrame(directory /
                                        (std::string(arm) + "_" + std::to_string(pass) + ".obj"),
                                    article.faces, uv, physical);
            last = uv;
            journal << arm << ',' << pass << ",valid";
            for (auto n : counts)
              journal << ',' << n;
            journal << ",\n";
          },
          filter);
    } catch (const MixedGeometryRejection& error) {
      journal << arm << ',' << current_pass << ",rejected";
      for (auto n : counts)
        journal << ',' << n;
      journal << ',' << error.what() << '\n';
    }
    SaveMixedSmoothingFrame(directory / (std::string(arm) + "_final.obj"), article.faces, last,
                            ValidateMixedSmoothing(patch, article.faces, last, lift));
  }
  journal.close();
  Require(bool(journal), "Cannot retain mixed smoothing comparison trace");
  return last;
}

using ResearchSourceTreeFactory = std::function<std::unique_ptr<Quadtree>()>;

Candidate Generate(PatchBezier& patch, bool fail_before_commit,
                   const ResearchSourceTreeFactory& source_tree_factory = {},
                   const RealBoundarySource* source = nullptr, bool pair_during_front = false,
                   bool article_front = false, bool article_area_centroid = false,
                   const Candidate* previous_search = nullptr,
                   const std::filesystem::path* guarded_smoothing = nullptr,
                   bool additional_pairs = false,
                   std::optional<double> additional_pair_error_limit = std::nullopt,
                   std::optional<IdealFrontLimits> ideal_front_limits = std::nullopt) {
  ValidateSourceCurves(patch);
  Require(!article_front || !pair_during_front, "Article and TRI-observer modes are exclusive");
  Require(!article_area_centroid || article_front, "Area centroid requires the article mode");
  std::unique_ptr<Quadtree> original;
  std::vector<UvFrontSegment> front;
  if (!article_front) {
    original = source_tree_factory ? source_tree_factory() : MakeSourceTree(true);
    Require(original->makeTemplateBasedMesh() ==
                Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
            "Original interior TRI reference failed");
    front = SnapshotLegacyFront(*original);
  }
  auto tree = source_tree_factory ? source_tree_factory() : MakeSourceTree(true);
  std::vector<UvVertex> contour;
  std::optional<UvContourClearance> clearance;
  if (article_front) {
    for (auto* vertex : tree->getBoundary()->getBoundary())
      contour.push_back({vertex->getX(), vertex->getY()});
    clearance.emplace(contour);
  }
  InteriorTemplateDispatcher dispatch(*tree);
  const auto selected = dispatch.Select(InteriorTemplateMode::ExperimentalQuad,
                                        article_area_centroid ? AreaPointRule : PointRule,
                                        clearance ? &*clearance : nullptr);
  auto* raw = tree.get();
  std::unique_ptr<OwnedQuadAftFront> aft;
  OwnedAftFrontReport seeded;
  if (!article_front) {
    aft = std::make_unique<OwnedQuadAftFront>(raw->getBoundary(), raw);
    tree.release();
    seeded = aft->Seed(selected, front);
  }
  LiveBoundaryPairing pairing;
  std::map<Vertex*, std::size_t> live_ids;
  const auto physical_point = [&](UvVertex uv) {
    auto xyz = Evaluate(patch, uv);
    if (source)
      for (const auto& site : source->sites)
        if (site.uv.u == uv.u && site.uv.v == uv.v) {
          xyz = site.xyz;
          break;
        }
    return xyz;
  };
  const auto add_pair_site = [&](UvVertex uv) {
    return pairing.AddSite(
        {uv, physical_point(uv), Values(patch.Qu(uv.u, uv.v) * patch.Qv(uv.u, uv.v))});
  };
  if (pair_during_front) {
    std::map<std::pair<double, double>, std::size_t> seeded_ids;
    for (const auto& uv : selected.uv_quads.vertices)
      seeded_ids.emplace(std::make_pair(uv.u, uv.v), add_pair_site(uv));
    for (auto* vertex : aft->OwnedSeamVertices())
      live_ids.emplace(vertex, seeded_ids.at({vertex->getX(), vertex->getY()}));
    aft->SetTriangleCommitObserver([&](const std::array<Vertex*, 3>& vertices) {
      std::array<std::size_t, 3> ids{};
      for (std::size_t i = 0; i < vertices.size(); ++i) {
        auto found = live_ids.find(vertices[i]);
        if (found == live_ids.end())
          found =
              live_ids
                  .emplace(vertices[i], add_pair_site({vertices[i]->getX(), vertices[i]->getY()}))
                  .first;
        ids[i] = found->second;
      }
      pairing.ObserveTriangle(ids);
    });
  }
  if (aft)
    for (auto* edge : aft->getBoundary()->getEdges())
      aft->getQuadtree()->findCell(edge);
  Candidate result;
  result.article_area_centroid = article_area_centroid;
  ArticleFrontResult article;
  if (article_front) {
    // This front derives its exact inner interface from the selected QUAD seed.
    // The older TRI bridge requires missing-neighbor classification and must not
    // be seeded with a different, clearance-filtered interior region.
    std::vector<ArticleMixedFront::Box> boxes;
    for (auto* leaf : raw->getLeaves())
      boxes.push_back({leaf->getMin()->getX(), leaf->getMin()->getY(), leaf->getMax()->getX(),
                       leaf->getMax()->getY()});
    if (previous_search) {
      const auto& seed = selected.uv_quads;
      const auto& reference_uv = previous_search->article_uv_before_smoothing;
      const auto same_uv = [](UvVertex a, UvVertex b) { return a.u == b.u && a.v == b.v; };
      Require(reference_uv.size() == seed.vertices.size() + contour.size() &&
                  seed.quads.size() == previous_search->seed_quads &&
                  std::equal(seed.vertices.begin(), seed.vertices.end(), reference_uv.begin(),
                             same_uv) &&
                  std::equal(contour.begin(), contour.end(),
                             reference_uv.begin() + seed.vertices.size(), same_uv),
              "Previous lookup requires identical ordered seed vertices and contour");
      for (std::size_t i = 0; i < seed.quads.size(); ++i) {
        const auto& corners = seed.quads[i].vertices;
        const auto& reference = previous_search->faces[i];
        Require(std::equal(corners.begin(), corners.end(), reference.begin(), reference.end()),
                "Previous lookup requires identical ordered seed QUADs");
      }
      boxes = previous_search->article_leaves;
    }
    std::optional<ArticleFrontPairScreen> pair_screen;
    if (additional_pair_error_limit) {
      const auto measure = [&](const std::array<UvVertex, 4>& corners) -> std::optional<double> {
        std::array<research::ResidualUv, 4> uv;
        std::array<Xyz, 4> xyz;
        for (std::size_t i = 0; i < corners.size(); ++i) {
          uv[i] = {corners[i].u, corners[i].v};
          xyz[i] = physical_point(corners[i]);
        }
        const double chord =
            std::hypot(xyz[1][0] - xyz[0][0], xyz[1][1] - xyz[0][1], xyz[1][2] - xyz[0][2]);
        if (!std::isfinite(chord) || chord <= 0)
          return std::nullopt;
        const auto exact = [&patch](const research::ResidualUv& p) {
          return Evaluate(patch, {p[0], p[1]});
        };
        const double error = research::MeasureQuadSurfaceMaximum(uv, xyz, exact) / chord;
        return std::isfinite(error) ? std::optional<double>{error} : std::nullopt;
      };
      pair_screen.emplace(ArticleFrontPairScreen{*additional_pair_error_limit, measure});
    }
    std::optional<ArticleFrontIdealPoint> ideal_point;
    std::optional<ArticleFrontOrder> alternate_order;
    if (ideal_front_limits) {
      const auto meets_floor =
          [&, limits = *ideal_front_limits](const std::array<UvVertex, 3>& corners) {
            const std::vector<UvVertex> uv(corners.begin(), corners.end());
            const std::vector<Xyz> xyz{physical_point(uv[0]), physical_point(uv[1]),
                                       physical_point(uv[2])};
            TrialScores scores;
            scores.fill(std::numeric_limits<double>::infinity());
            try {
              CheckMixedSmoothingFace(patch, {0, 1, 2}, uv, xyz, nullptr, &scores);
            } catch (const MixedGeometryRejection&) {
              return false;
            }
            return std::isfinite(scores[0]) && scores[0] >= limits.min_shape &&
                   std::isfinite(scores[1]) && scores[1] >= limits.min_angle;
          };
      const auto check_closure = [&](const std::vector<UvVertex>& uv,
                                     const ArticleFrontFaces& control,
                                     const ArticleFrontFaces& trial) {
        return PreservesClosureQuality(patch, physical_point, *ideal_front_limits, uv, control,
                                       trial);
      };
      if (ideal_front_limits->order_only) {
        alternate_order.emplace(ArticleFrontOrder{meets_floor, check_closure});
      } else {
        ideal_point.emplace(ArticleFrontIdealPoint{ideal_front_limits->points, meets_floor, {}});
        if (ideal_front_limits->quad_floors)
          ideal_point->preserves_closure = check_closure;
      }
    }
    article = ArticleMixedFront(selected.uv_quads, contour, std::move(boxes), additional_pairs,
                                std::move(pair_screen), std::move(ideal_point),
                                std::move(alternate_order))
                  .Run();
    result.additional_pair_search = additional_pairs;
    result.additional_pair_error_limit = additional_pair_error_limit;
    result.ideal_front_limits = ideal_front_limits;
    std::vector<std::array<UvVertex, 3>> audit_triangles;
    for (std::size_t i = article.seed_quads; i < article.faces.size(); ++i) {
      const auto& face = article.faces[i];
      audit_triangles.push_back(
          {article.vertices[face[0]], article.vertices[face[1]], article.vertices[face[2]]});
      if (face.size() == 4)
        audit_triangles.push_back(
            {article.vertices[face[0]], article.vertices[face[2]], article.vertices[face[3]]});
    }
    Require(!article.commits.empty() &&
                AuditUvOverlap(selected.uv_quads, audit_triangles).no_overlap,
            "Article contraction has incomplete or overlapping output");
    result.article_uv_before_smoothing = article.vertices;
    for (const auto uv : article.vertices)
      result.article_xyz_before_smoothing.push_back(physical_point(uv));
    if (guarded_smoothing) {
      Require(source != nullptr, "Guarded smoothing comparison needs the native curve");
      result.guarded_smoothing_comparison = true;
      article.vertices =
          CompareMixedSmoothing(patch, article, physical_point, *source, *guarded_smoothing);
    } else {
      result.article_smoothing = SmoothMixedUv(
          article.vertices, article.faces,
          [&](std::size_t, const std::vector<UvVertex>& positions) {
            std::vector<Xyz> physical;
            for (const auto uv : positions)
              physical.push_back(physical_point(uv));
            std::vector<std::array<UvVertex, 3>> facets;
            double alignment = 1.0;
            for (const auto& face : article.faces) {
              const auto check = [&](std::size_t a, std::size_t b, std::size_t c) {
                const std::array<UvVertex, 3> triangle{positions[face[a]], positions[face[b]],
                                                       positions[face[c]]};
                CheckFacet(patch, FaceUv{triangle}, alignment);
                facets.push_back(triangle);
              };
              check(0, 1, 2);
              if (face.size() == 4) {
                check(0, 2, 3);
                research::PhysicalQuadCorners corners{}, normals{};
                for (std::size_t i = 0; i < 4; ++i) {
                  const auto uv = positions[face[i]];
                  const auto next = positions[face[(i + 1) % 4]],
                             prev = positions[face[(i + 3) % 4]];
                  Require((next.u - uv.u) * (prev.v - uv.v) - (next.v - uv.v) * (prev.u - uv.u) >
                              1e-14,
                          "Mixed smoothing inverted or collapsed a UV quad");
                  corners[i] = physical[face[i]];
                  normals[i] = Cross(Values(patch.Qu(uv.u, uv.v)), Values(patch.Qv(uv.u, uv.v)));
                }
                (void)research::ObservePhysicalQuadQuality(corners, normals);
              }
            }
            // Reuse the existing complete TRI intersection audit for all facets,
            // including the two halves of each QUAD, with unchanged tolerances.
            Require(AuditUvOverlap({}, facets).no_overlap,
                    "Mixed smoothing overlaps physical facets");
            result.article_smoothing_xyz.push_back(std::move(physical));
          });
      article.vertices = result.article_smoothing.passes.back();
    }
  } else {
    const auto report = aft->AttemptExteriorTriangulation(selected);
    Require(report.front_drained && report.triangles_positive && report.seam_orientation_complete &&
                report.seam_vertices_unchanged && report.uv_area_balanced &&
                report.spatial_overlap_tested && report.no_spatial_overlap &&
                report.exterior_triangles > 0,
            "Original AFT failed complete nonoverlapping UV coverage");
  }
  result.real_boundary = source != nullptr;
  result.source_witness = source;
  unsigned long source_max_id = 0;
  if (source)
    for (const auto& site : source->sites)
      source_max_id = std::max(source_max_id, site.source_id);
  std::map<std::pair<double, double>, std::size_t> uv_ids;
  const auto add_node = [&](UvVertex uv) {
    auto xyz = Evaluate(patch, uv);
    const auto id = result.uv.size();
    Require(uv_ids.emplace(std::make_pair(uv.u, uv.v), id).second,
            "Unpaired coincident UV nodes in controlled chart");
    unsigned long node_id = static_cast<unsigned long>(id + 1);
    if (source) {
      Require(id < std::numeric_limits<unsigned long>::max() - source_max_id,
              "Real-boundary node identity range overflow");
      node_id += source_max_id;
      for (const auto& site : source->sites)
        if (site.uv.u == uv.u && site.uv.v == uv.v) {
          xyz = site.xyz;
          node_id = site.source_id;
          break;
        }
    }
    auto node = std::make_unique<NodeAdaptive>(xyz[0], xyz[1], xyz[2]);
    node->SetId(node_id);
    result.node_ids.push_back(node_id);
    result.mesh->AddNoh(std::move(node));
    result.uv.push_back(uv);
    return id;
  };
  for (const auto& uv : (article_front ? article.vertices : selected.uv_quads.vertices))
    add_node(uv);
  for (const auto& quad : selected.uv_quads.quads)
    result.faces.emplace_back(quad.vertices.begin(), quad.vertices.end());
  result.quads = result.faces.size();
  result.seed_quads = result.quads;
  result.quad_origins = selected.quad_face_origins;
  result.clearance_excluded_cells = selected.excluded_clearance_leaves;
  Require(result.quad_origins.size() == result.quads,
          "Mixed residual leaf provenance differs from the real native tree");
  if (aft) {
    std::map<Vertex*, std::size_t> aft_ids;
    // Only the already-audited seam may bridge source pointer identities to QUAD IDs.
    for (auto* v : aft->OwnedSeamVertices())
      aft_ids.emplace(v, uv_ids.at({v->getX(), v->getY()}));
    Require(aft_ids.size() == seeded.distinct_quad_front_vertices,
            "Incomplete canonical QUAD/AFT seam");
    for (auto* face : aft->Triangles()) {
      std::vector<std::size_t> ids;
      for (auto* v : {face->getV1(), face->getV2(), face->getV3()}) {
        auto it = aft_ids.find(v);
        if (it == aft_ids.end())
          it = aft_ids.emplace(v, add_node({v->getX(), v->getY()})).first;
        ids.push_back(it->second);
      }
      result.faces.push_back(std::move(ids));
    }
  }
  if (article_front) {
    for (std::size_t i = result.uv.size(); i < article.vertices.size(); ++i)
      add_node(article.vertices[i]);
    result.faces = article.faces;
    result.article_commits = std::move(article.commits);
    result.article_leaves = std::move(article.leaves);
    // Preserve seed-first output; mixed commits retain their independent order.
    std::stable_partition(result.faces.begin() + static_cast<std::ptrdiff_t>(result.seed_quads),
                          result.faces.end(), [](const auto& face) { return face.size() == 4; });
    result.quads =
        static_cast<std::size_t>(std::count_if(result.faces.begin(), result.faces.end(),
                                               [](const auto& face) { return face.size() == 4; }));
  }
  if (pair_during_front) {
    Require(pairing.Triangles().size() == aft->Triangles().size(),
            "Live pair observer missed an AFT triangle commit");
    result.source_faces = result.faces;
    result.aft_pair_origins = pairing.Selected();
    result.live_pair_events = pairing.Events();
    result.faces.resize(result.seed_quads);
    for (const auto& pair : pairing.Selected())
      result.faces.emplace_back(pair.boundary_cycle.begin(), pair.boundary_cycle.end());
    result.quads = result.faces.size();
    for (std::size_t i = 0; i < pairing.Triangles().size(); ++i) {
      const auto& triangle = pairing.Triangles()[i];
      Require(result.source_faces[result.seed_quads + i] ==
                  std::vector<std::size_t>(triangle.begin(), triangle.end()),
              "Live pair site identity differs from the retained AFT scaffold");
      if (!pairing.Consumed()[i])
        result.faces.emplace_back(triangle.begin(), triangle.end());
    }
    Require(result.quads == result.quad_origins.size() + result.aft_pair_origins.size(),
            "Mixed QUAD origins do not distinguish native templates from AFT pairs");
  }
  struct Incidence {
    unsigned count = 0;
    std::size_t a = 0, b = 0, face = 0;
  };
  std::map<std::pair<std::size_t, std::size_t>, Incidence> edges;
  std::vector<std::vector<std::size_t>> adjacency(result.faces.size());
  unsigned boundary_edges = 0;
  for (std::size_t i = 0; i < result.faces.size(); ++i) {
    const auto& ids = result.faces[i];
    for (std::size_t k = 0; k < ids.size(); ++k) {
      const auto a = ids[k], b = ids[(k + 1) % ids.size()];
      auto& edge = edges[std::minmax(a, b)];
      Require(edge.count < 2 && a != b, "Nonmanifold or collapsed mixed edge");
      if (edge.count == 1) {
        Require(edge.a == b && edge.b == a, "Mixed edge winding mismatch");
        adjacency[i].push_back(edge.face);
        adjacency[edge.face].push_back(i);
      } else {
        edge.a = a;
        edge.b = b;
        edge.face = i;
      }
      ++edge.count;
    }
    const auto audit_facet = [&](unsigned a, unsigned b, unsigned c) {
      CheckFacet(patch, {{result.uv[ids[a]], result.uv[ids[b]], result.uv[ids[c]]}},
                 result.min_alignment);
      const auto x = Evaluate(patch, result.uv[ids[a]]), y = Evaluate(patch, result.uv[ids[b]]),
                 z = Evaluate(patch, result.uv[ids[c]]);
      const auto ab = Difference(y, x), ac = Difference(z, x), bc = Difference(z, y);
      const double quality =
          2 * std::sqrt(3.0) * Norm(Cross(ab, ac)) / (Dot(ab, ab) + Dot(ac, ac) + Dot(bc, bc));
      Require(std::isfinite(quality) && quality > 0, "Invalid physical facet quality");
      result.min_quality = std::min(result.min_quality, quality);
    };
    audit_facet(0, 1, 2);
    auto* a = result.mesh->GetNoh(static_cast<unsigned>(ids[0]));
    auto* b = result.mesh->GetNoh(static_cast<unsigned>(ids[1]));
    auto* c = result.mesh->GetNoh(static_cast<unsigned>(ids[2]));
    if (ids.size() == 4) {
      audit_facet(0, 2, 3);
      auto* d = result.mesh->GetNoh(static_cast<unsigned>(ids[3]));
      research::QuadrilateralAdaptive::Parameters uv{{{result.uv[ids[0]].u, result.uv[ids[0]].v},
                                                      {result.uv[ids[1]].u, result.uv[ids[1]].v},
                                                      {result.uv[ids[2]].u, result.uv[ids[2]].v},
                                                      {result.uv[ids[3]].u, result.uv[ids[3]].v}}};
      double u = 0, v = 0;
      for (auto id : ids) {
        u += result.uv[id].u / 4;
        v += result.uv[id].v / 4;
      }
      const auto normal = patch.Qu(u, v) * patch.Qv(u, v);
      auto quad = std::make_unique<research::QuadrilateralAdaptive>(
          research::QuadrilateralAdaptive::Nodes{a, b, c, d}, uv, normal);
      quad->SetId(static_cast<unsigned long>(i + 1));
      result.mesh->AddElement(std::move(quad));
    } else {
      auto tri = std::make_unique<TriangleAdaptive>(a, b, c);
      tri->SetId(static_cast<unsigned long>(i + 1));
      tri->SetParametersN1({result.uv[ids[0]].u, result.uv[ids[0]].v});
      tri->SetParametersN2({result.uv[ids[1]].u, result.uv[ids[1]].v});
      tri->SetParametersN3({result.uv[ids[2]].u, result.uv[ids[2]].v});
      result.mesh->AddElement(std::move(tri));
    }
  }
  for (const auto& entry : edges)
    if (entry.second.count == 1) {
      const auto& a = result.uv[entry.second.a];
      const auto& b = result.uv[entry.second.b];
      Require((a.u == b.u && (a.u == 0 || a.u == 1)) || (a.v == b.v && (a.v == 0 || a.v == 1)),
              "Gap or unexpected interior boundary");
      ++boundary_edges;
    }
  Require(boundary_edges == (source ? source->sites.size() : 16) &&
              result.uv.size() + result.faces.size() == edges.size() + 1,
          "Original boundary or Euler disk contract changed");
  if (source)
    for (std::size_t i = 0; i < source->sites.size(); ++i) {
      const auto& site = source->sites[i];
      const auto& next = source->sites[(i + 1) % source->sites.size()];
      const auto a = uv_ids.at({site.uv.u, site.uv.v});
      const auto b = uv_ids.at({next.uv.u, next.uv.v});
      const auto edge = edges.find(std::minmax(a, b));
      const auto* node = result.mesh->GetNoh(static_cast<unsigned>(a));
      Require(edge != edges.end() && edge->second.count == 1 && edge->second.a == a &&
                  edge->second.b == b && node->GetId() == site.source_id &&
                  Xyz{node->GetX(), node->GetY(), node->GetZ()} == site.xyz,
              "Physical QUAD/AFT export changed an original source node or interval");
    }
  std::set<std::size_t> seen{0};
  std::vector<std::size_t> work{0};
  while (!work.empty()) {
    const auto i = work.back();
    work.pop_back();
    for (auto j : adjacency[i])
      if (seen.insert(j).second)
        work.push_back(j);
  }
  Require(seen.size() == result.faces.size(), "Disconnected physical chart");
  for (unsigned i = 0; i < result.mesh->GetNumberElements(); ++i)
    Require(result.mesh->GetElement(i)->GetId() == i + 1, "Physical element identity differs");
  if (fail_before_commit)
    throw PublicationFailure("Injected failure before physical publication");
  return result;
}

// The entire history lives inside the caller's unpublished staging directory.
// These are actual polygon commits, not successive snapshots of a TRI matcher.
void ExportArticleSteps(const Candidate& candidate, const std::filesystem::path& directory) {
  Require(!candidate.article_commits.empty(), "Missing article contraction history");
  const bool guarded = candidate.guarded_smoothing_comparison;
  Require(candidate.article_uv_before_smoothing.size() == candidate.uv.size() &&
              candidate.article_xyz_before_smoothing.size() == candidate.uv.size(),
          "Missing article birth geometry");
  Require(guarded || (candidate.article_smoothing.passes.size() == 5 &&
                      candidate.article_smoothing_xyz.size() == 5),
          "Missing complete mixed smoothing history");
  Require(std::filesystem::create_directory(directory), "Article history already exists");
  std::ofstream trace(directory / "front.json", std::ios::binary);
  trace.imbue(std::locale::classic());
  trace << std::setprecision(17);
  const auto ids = [&](const auto& values) {
    trace << '[';
    bool first = true;
    for (auto value : values) {
      if (!first)
        trace << ',';
      trace << value;
      first = false;
    }
    trace << ']';
  };
  trace << "{\"schema\":\""
        << (candidate.additional_pair_error_limit ? "apmesh.quad.article_front_screened_pairs.v1"
            : candidate.additional_pair_search    ? "apmesh.quad.article_front_guarded_pairs.v1"
            : guarded                             ? "apmesh.quad.article_front_guarded.v1"
                                                  : "apmesh.quad.article_front.v1")
        << '"';
  if (candidate.additional_pair_error_limit)
    trace << ",\"additional_pair_error_limit\":" << *candidate.additional_pair_error_limit;
  if (candidate.ideal_front_limits && candidate.ideal_front_limits->order_only) {
    const auto& limits = *candidate.ideal_front_limits;
    trace << ",\"front_order\":{\"policy\":\"paired_adjacent_base_closure_v1\",\"min_angle_deg\":"
          << limits.min_angle << ",\"min_shape\":" << limits.min_shape
          << ",\"quad_min_angle_deg\":" << (*limits.quad_floors)[1]
          << ",\"quad_min_shape\":" << (*limits.quad_floors)[0] << '}';
  } else if (candidate.ideal_front_limits) {
    const auto& limits = *candidate.ideal_front_limits;
    trace << ",\"ideal_front_points\":{\"policy\":\""
          << (limits.quad_floors ? "legacy_leaf_height_guarded_closure_v1"
                                 : "legacy_unit_leaf_height_v1")
          << "\",\"limit\":" << limits.points << ",\"min_angle_deg\":" << limits.min_angle
          << ",\"min_shape\":" << limits.min_shape;
    if (limits.quad_floors)
      trace << ",\"quad_min_angle_deg\":" << (*limits.quad_floors)[1]
            << ",\"quad_min_shape\":" << (*limits.quad_floors)[0];
    trace << '}';
  }
  trace << ",\"point_rule\":\""
        << (candidate.article_area_centroid ? "polygon_area_centroid_uv_v1" : "vertex_mean_uv_v1")
        << "\",\"clearance\":{"
        << "\"policy\":\"minimum_cell_segment_uv_v1\",\"factor\":0.2,\"excluded_cells\":"
        << candidate.clearance_excluded_cells << "},\"vertices\":[";
  for (std::size_t i = 0; i < candidate.article_uv_before_smoothing.size(); ++i) {
    if (i)
      trace << ',';
    const auto uv = candidate.article_uv_before_smoothing[i];
    trace << '[' << uv.u << ',' << uv.v << ']';
  }
  trace << "],\"leaves\":[";
  for (std::size_t i = 0; i < candidate.article_leaves.size(); ++i) {
    if (i)
      trace << ',';
    ids(candidate.article_leaves[i]);
  }
  trace << "],\"seed_faces\":[";
  std::vector<std::vector<VertexId>> faces;
  for (std::size_t i = 0; i < candidate.seed_quads; ++i) {
    if (i)
      trace << ',';
    ids(candidate.faces[i]);
    faces.push_back(candidate.faces[i]);
  }
  trace << "],\"commits\":[";
  const auto snapshot = [&](const std::string& name, const std::string& caption,
                            const std::vector<UvVertex>& positions,
                            const std::vector<Xyz>& physical,
                            const std::vector<std::vector<VertexId>>& snapshot_faces) {
    std::ofstream out(directory / name, std::ios::binary);
    out.imbue(std::locale::classic());
    out << std::setprecision(17) << "# " << caption << '\n';
    for (const auto& p : physical)
      out << "v " << p[0] << ' ' << p[1] << ' ' << p[2] << '\n';
    for (const auto& uv : positions)
      out << "vt " << uv.u << ' ' << uv.v << '\n';
    for (const auto& face : snapshot_faces) {
      out << 'f';
      for (auto id : face)
        out << ' ' << id + 1 << '/' << id + 1;
      out << '\n';
    }
    out.close();
    Require(bool(out), "Cannot write article commit frame");
  };
  const auto frame = [&](std::size_t step) {
    snapshot("commit_" + std::to_string(step) + ".obj",
             "actual prospective mixed-front commit " + std::to_string(step),
             candidate.article_uv_before_smoothing, candidate.article_xyz_before_smoothing, faces);
  };
  if (!guarded)
    frame(0);
  for (std::size_t i = 0; i < candidate.article_commits.size(); ++i) {
    const auto& step = candidate.article_commits[i];
    if (i)
      trace << ',';
    trace << "{\"before\":[";
    for (std::size_t j = 0; j < step.before.size(); ++j) {
      if (j)
        trace << ',';
      ids(std::array<VertexId, 2>{step.before[j].first, step.before[j].second});
    }
    trace << "],\"best\":";
    ids(step.best);
    trace << ",\"selected_side\":" << step.selected_side << ",\"polygon\":";
    ids(step.polygon);
    trace << ",\"alternatives\":[";
    for (std::size_t j = 0; j < step.alternatives.size(); ++j) {
      const auto& choice = step.alternatives[j];
      if (j)
        trace << ',';
      trace << "{\"side\":" << choice.side << ",\"triangle\":";
      ids(choice.triangle);
      trace << ",\"quad\":";
      ids(choice.quad);
      trace << ",\"eligible\":" << (choice.eligible ? "true" : "false") << ",\"score\":";
      if (std::isfinite(choice.score))
        trace << choice.score;
      else
        trace << "null";
      trace << '}';
    }
    trace << ']';
    if (step.additional_pair) {
      const auto& extra = *step.additional_pair;
      trace << ",\"additional_pair\":{\"first_triangle\":";
      ids(extra.first_triangle);
      trace << ",\"second_triangle\":";
      ids(extra.choice.triangle);
      trace << ",\"side\":" << extra.choice.side << ",\"score\":" << extra.choice.score << '}';
    }
    if (step.introduced_vertex)
      trace << ",\"introduced_vertex\":" << *step.introduced_vertex;
    if (!step.closure_trials.empty()) {
      trace << ",\"closure_trials\":[";
      for (std::size_t j = 0; j < step.closure_trials.size(); ++j) {
        const auto& trial = step.closure_trials[j];
        if (j)
          trace << ',';
        const char* status = "incomplete";
        if (trial.outcome == ArticleClosureOutcome::shape_regression)
          status = "shape_regression";
        else if (trial.outcome == ArticleClosureOutcome::accepted)
          status = "accepted";
        trace << "{\"fraction\":" << trial.fraction << ",\"status\":\"" << status << "\"}";
      }
      trace << ']';
    }
    if (step.original_order_triangle) {
      trace << ",\"original_order_triangle\":";
      ids(*step.original_order_triangle);
      trace << ",\"order_trials\":[";
      for (std::size_t j = 0; j < step.order_trials.size(); ++j) {
        const auto& trial = step.order_trials[j];
        if (j)
          trace << ',';
        trace << "{\"base\":";
        ids(std::array<VertexId, 2>{trial.base.first, trial.base.second});
        const char* status = "incomplete";
        if (trial.outcome == ArticleClosureOutcome::shape_regression)
          status = "quality_rejected";
        else if (trial.outcome == ArticleClosureOutcome::accepted)
          status = "accepted";
        trace << ",\"status\":\"" << status << "\"}";
      }
      trace << ']';
    }
    if (candidate.additional_pair_error_limit && step.selected_side < 0) {
      trace << ",\"pair_measurements\":[";
      for (std::size_t j = 0; j < step.pair_measurements.size(); ++j) {
        const auto& measure = step.pair_measurements[j];
        if (j)
          trace << ',';
        trace << "{\"quad\":";
        ids(measure.quad);
        trace << ",\"score\":" << measure.score << ",\"relative_error\":";
        if (measure.relative_error)
          trace << *measure.relative_error;
        else
          trace << "null";
        trace << '}';
      }
      trace << ']';
    }
    trace << '}';
    if (!guarded) {
      faces.push_back(step.polygon);
      frame(i + 1);
    }
  }
  trace << "],\"smoothing\":";
  if (guarded) {
    trace << "null}\n";
    trace.close();
    Require(bool(trace), "Cannot complete guarded article front trace");
    return;
  }
  trace << "{\"policy\":\"uv_distinct_incident_vertices_jacobi_5_v1\",\"boundary\":";
  ids(candidate.article_smoothing.boundary);
  trace << ",\"passes\":[";
  for (std::size_t pass = 0; pass < 5; ++pass) {
    if (pass)
      trace << ',';
    trace << '[';
    const auto& positions = candidate.article_smoothing.passes[pass];
    for (std::size_t i = 0; i < positions.size(); ++i) {
      if (i)
        trace << ',';
      trace << '[' << positions[i].u << ',' << positions[i].v << ']';
    }
    trace << ']';
    snapshot("smoothing_" + std::to_string(pass + 1) + ".obj",
             "approved mixed UV smoothing pass " + std::to_string(pass + 1), positions,
             candidate.article_smoothing_xyz[pass], candidate.faces);
  }
  trace << "]}}\n";
  trace.close();
  Require(bool(trace), "Cannot complete article front trace");
}

// Capture exactly the live non-owning element links, including their order.
std::vector<std::vector<ElementAdaptive*>> CaptureNodeObservers(SubMesh& mesh) {
  std::vector<std::vector<ElementAdaptive*>> snapshots;
  snapshots.reserve(mesh.GetNumberNos());
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    const auto& observers = mesh.GetNoh(i)->GetElements();
    snapshots.emplace_back(observers.begin(), observers.end());
  }
  return snapshots;
}

// Verify that a physical history node observes only its own actual elements.
void CheckTypedIncidence(SubMesh& mesh, const Candidate& layout) {
  Require(mesh.GetNumberNos() == layout.uv.size() &&
              mesh.GetNumberNos() == layout.node_ids.size() &&
              mesh.GetNumberElements() == layout.faces.size(),
          "Typed history size differs from the accepted QUAD/TRI layout");
  std::vector<std::set<ElementAdaptive*>> expected(mesh.GetNumberNos());
  for (unsigned i = 0; i < mesh.GetNumberElements(); ++i) {
    auto* element = mesh.GetElement(i);
    Require(element != nullptr, "Missing physical history element");
    const auto& face = layout.faces[i];
    Require(face.size() == 3 || face.size() == 4, "Unexpected mixed element arity");
    const bool is_quad = dynamic_cast<research::QuadrilateralAdaptive*>(element) != nullptr;
    const bool is_tri = dynamic_cast<TriangleAdaptive*>(element) != nullptr;
    Require((face.size() == 4 && is_quad && !is_tri) || (face.size() == 3 && is_tri && !is_quad),
            "History element type does not match its physical topology");
    for (const auto index : face) {
      Require(index < expected.size() && expected[index].insert(element).second,
              "Duplicate or invalid typed history incidence");
    }
  }
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    auto* node = mesh.GetNoh(i);
    Require(node != nullptr && node->GetId() == layout.node_ids[i],
            "Typed history node identity changed");
    const auto& actual = node->GetElements();
    Require(actual.size() == expected[i].size() &&
                std::set<ElementAdaptive*>(actual.begin(), actual.end()) == expected[i],
            "Typed history contains a stale, foreign or duplicated observer");
  }
}

// Rebuild a true owned mixed-element graph; never copy borrowed observer lists.
std::unique_ptr<SubMesh> CloneTypedHistory(const SubMesh& original, const Candidate& layout,
                                           PatchBezier& patch, int fail_before_element) {
  Require(original.GetNumberNos() == layout.uv.size() &&
              original.GetNumberElements() == layout.faces.size(),
          "Typed history source/layout count mismatch");
  auto clone = std::make_unique<SubMesh>();
  for (unsigned i = 0; i < original.GetNumberNos(); ++i) {
    const auto* node = original.GetNoh(i);
    Require(node != nullptr, "Typed history source has a missing node");
    auto copied = std::make_unique<NodeAdaptive>(node->GetX(), node->GetY(), node->GetZ());
    copied->SetId(node->GetId());
    copied->SetGa(node->GetGa());
    copied->SetGd(node->GetGd());
    copied->SetHa(node->GetHa());
    copied->SetHd(node->GetHd());
    clone->AddNoh(std::move(copied));
  }
  for (unsigned i = 0; i < original.GetNumberElements(); ++i) {
    if (fail_before_element == static_cast<int>(i))
      throw PublicationFailure("Injected partial typed history clone failure");
    const auto& face = layout.faces[i];
    auto* source_element = original.GetElement(i);
    Require(source_element != nullptr, "Typed history source has a missing element");
    auto* a = clone->GetNoh(static_cast<unsigned>(face.at(0)));
    auto* b = clone->GetNoh(static_cast<unsigned>(face.at(1)));
    auto* c = clone->GetNoh(static_cast<unsigned>(face.at(2)));
    if (face.size() == 4) {
      const auto* source_quad =
          dynamic_cast<const research::QuadrilateralAdaptive*>(source_element);
      Require(source_quad != nullptr, "A QUAD was lost during typed history cloning");
      research::QuadrilateralAdaptive::Parameters parameters{};
      double u = 0.0, v = 0.0;
      for (unsigned corner = 0; corner < 4; ++corner) {
        const auto uv = layout.uv.at(face[corner]);
        parameters[corner] = {uv.u, uv.v};
        Require(source_quad->GetParameters()[corner] == parameters[corner],
                "QUAD source UV metadata differs from layout");
        u += uv.u / 4.0;
        v += uv.v / 4.0;
      }
      auto* d = clone->GetNoh(static_cast<unsigned>(face[3]));
      const auto normal = patch.Qu(u, v) * patch.Qv(u, v);
      auto copied = std::make_unique<research::QuadrilateralAdaptive>(
          research::QuadrilateralAdaptive::Nodes{a, b, c, d}, parameters, normal);
      copied->SetId(static_cast<unsigned long>(i + 1));
      clone->AddElement(std::move(copied));
    } else {
      Require(face.size() == 3, "Unsupported history element arity");
      const auto* source_tri = dynamic_cast<const TriangleAdaptive*>(source_element);
      Require(source_tri != nullptr, "An AFT triangle was lost during typed history cloning");
      auto matches = [](const std::tuple<double, double>& values, UvVertex uv) {
        return std::get<0>(values) == uv.u && std::get<1>(values) == uv.v;
      };
      Require(matches(source_tri->GetParametersN1(), layout.uv.at(face[0])) &&
                  matches(source_tri->GetParametersN2(), layout.uv.at(face[1])) &&
                  matches(source_tri->GetParametersN3(), layout.uv.at(face[2])),
              "AFT triangle source UV metadata differs from layout");
      auto copied = std::make_unique<TriangleAdaptive>(a, b, c);
      copied->SetId(static_cast<unsigned long>(i + 1));
      copied->SetParametersN1({layout.uv[face[0]].u, layout.uv[face[0]].v});
      copied->SetParametersN2({layout.uv[face[1]].u, layout.uv[face[1]].v});
      copied->SetParametersN3({layout.uv[face[2]].u, layout.uv[face[2]].v});
      clone->AddElement(std::move(copied));
    }
    const auto* replica = clone->GetElement(i);
    Require(replica != source_element &&
                std::abs(replica->GetArea() - source_element->GetArea()) <=
                    1e-12 * std::max(1.0, std::abs(source_element->GetArea())),
            "History copy changed physical element area or reused its identity");
  }
  return clone;
}

void ProbeTypedHistory(SubMesh& accepted, const Candidate& layout, PatchBezier& patch) {
  // The probe runs before OBJ publication and before the candidate is committed.
  SubMesh* previous_patch_owner = patch.GetSubMesh();
  CheckTypedIncidence(accepted, layout);
  const auto original_observers = CaptureNodeObservers(accepted);
  const auto* first_original_node = accepted.GetNoh(0);
  const auto* first_original_element = accepted.GetElement(0);
  {
    auto clone = CloneTypedHistory(accepted, layout, patch, -1);
    CheckTypedIncidence(*clone, layout);
    Require(clone->GetNoh(0) != first_original_node &&
                clone->GetElement(0) != first_original_element,
            "Typed history clone aliases a previously accepted owner");

    // Restore the original observer even if a later verification throws.
    struct RestoreOriginalPatch final {
      PatchBezier& patch;
      SubMesh* previous;
      ~RestoreOriginalPatch() { patch.SetSubMesh(previous); }
    } restore{patch, previous_patch_owner};
    clone->SetPatch(&patch);
    patch.SetSubMesh(clone.get());
    Require(patch.GetSubMesh() == clone.get(),
            "Typed clone could not be staged as the current Patch submesh");
    bool rejected = false;
    try {
      auto failed = CloneTypedHistory(*clone, layout, patch, 7);
      (void)failed;
    } catch (const PublicationFailure&) {
      rejected = true;
    }
    Require(rejected && patch.GetSubMesh() == clone.get(),
            "Rejected partial history clone replaced the accepted candidate");
    CheckTypedIncidence(*clone, layout);
    CheckTypedIncidence(accepted, layout);
    Require(CaptureNodeObservers(accepted) == original_observers,
            "Transient history clone mutated previously accepted node observers");
  }
  Require(patch.GetSubMesh() == previous_patch_owner && accepted.GetNoh(0) == first_original_node &&
              accepted.GetElement(0) == first_original_element &&
              CaptureNodeObservers(accepted) == original_observers,
          "Typed history clone teardown damaged previously accepted state");
  std::cout << "QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1"
               " source_observers_preserved=1 adaptive_epochs=0\n";
}

// Observe the physical mixed graph without changing its accepted QUAD/TRI faces.
void ProbeMixedCurvature(SubMesh& mesh, const Candidate& layout) {
  std::vector<research::MixedPoint3> physical;
  physical.reserve(mesh.GetNumberNos());
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    const auto* node = mesh.GetNoh(i);
    Require(node != nullptr, "Missing node for typed mixed curvature");
    physical.push_back({node->GetX(), node->GetY(), node->GetZ()});
  }
  const auto observed = research::AuditMixedCurvature(physical, layout.faces);
  Require(observed.vertices.size() == layout.uv.size() && observed.quadrilaterals == layout.quads &&
              observed.triangles == layout.faces.size() - layout.quads &&
              observed.boundary_edges == 16 && observed.boundary_vertices == 16 &&
              observed.interior_vertices + observed.boundary_vertices == layout.uv.size() &&
              observed.interior_vertices > 0 && observed.min_barycentric_area > 0,
          "Mixed TRI/QUAD curvature metrics differ from validated physical chart");

  // Each malformed metric witness is rejected independently of the live mesh.
  unsigned rejected = 0;
  const auto must_reject = [&](const std::vector<research::MixedPoint3>& points,
                               const std::vector<research::MixedFace>& faces) {
    try {
      (void)research::AuditMixedCurvature(points, faces);
    } catch (const std::invalid_argument&) {
      ++rejected;
    }
  };
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}}, {{0, 1, 1}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {-1, 0, 0}, {0, -1, 0}}, {{0, 1, 2}, {0, 3, 4}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {1, 1, 0}}, {{0, 1, 2}, {0, 1, 3}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {2, 0, 0}}, {{0, 1, 2}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, std::numeric_limits<double>::quiet_NaN()}},
              {{0, 1, 2}});
  Require(rejected == 5, "Malformed typed mixed curvature input was accepted");

  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17) << "QUAD_TYPED_CURVATURE quad=" << observed.quadrilaterals
         << " tri=" << observed.triangles << " boundary_edges=" << observed.boundary_edges
         << " boundary_vertices=" << observed.boundary_vertices
         << " interior_vertices=" << observed.interior_vertices
         << " angle_defect_total=" << observed.total_angle_defect
         << " min_barycentric_area=" << observed.min_barycentric_area
         << " negative_cases=" << rejected
         << " policy=triangulated_barycentric_probe adaptive_epochs=0\n";
  std::cout << output.str();
}

// Observe true physical four-corner quality without changing QUAD ownership.
void ProbePhysicalQuadQuality(SubMesh& mesh, const Candidate& layout, PatchBezier& patch) {
  double min_scaled = 1.0;
  double min_warp_cosine = 1.0;
  double max_edge_ratio = 1.0;
  unsigned count = 0;
  for (std::size_t i = 0; i < layout.quads; ++i) {
    const auto& face = layout.faces.at(i);
    Require(face.size() == 4 && dynamic_cast<research::QuadrilateralAdaptive*>(
                                    mesh.GetElement(static_cast<unsigned>(i))) != nullptr,
            "Unexpected physical element in typed QUAD quality gate");
    research::PhysicalQuadCorners points{};
    research::PhysicalQuadCorners normals{};
    for (unsigned corner = 0; corner < 4; ++corner) {
      const auto id = face[corner];
      const auto* node = mesh.GetNoh(static_cast<unsigned>(id));
      Require(node != nullptr, "Missing physical QUAD quality node");
      points[corner] = {node->GetX(), node->GetY(), node->GetZ()};
      const auto uv = layout.uv.at(id);
      normals[corner] = Cross(Values(patch.Qu(uv.u, uv.v)), Values(patch.Qv(uv.u, uv.v)));
    }
    const auto metric = research::ObservePhysicalQuadQuality(points, normals);
    min_scaled = std::min(min_scaled, metric.min_scaled_jacobian);
    min_warp_cosine = std::min(min_warp_cosine, metric.diagonal_normal_cosine);
    max_edge_ratio = std::max(max_edge_ratio, metric.edge_ratio);
    ++count;
  }
  Require(count == 42 && min_scaled > 0.0 && min_warp_cosine > 0.0 && std::isfinite(max_edge_ratio),
          "Invalid controlled typed QUAD physical quality");

  // Independent malformed physical-only witnesses do not mutate the live mesh.
  const research::PhysicalQuadCorners square{{{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}}};
  const research::PhysicalQuadCorners forward{{{0, 0, 1}, {0, 0, 1}, {0, 0, 1}, {0, 0, 1}}};
  const auto flat = research::ObservePhysicalQuadQuality(square, forward);
  Require(std::abs(flat.min_scaled_jacobian - 1.0) < 1e-12 &&
              std::abs(flat.diagonal_normal_cosine - 1.0) < 1e-12 &&
              std::abs(flat.edge_ratio - 1.0) < 1e-12,
          "Analytic square QUAD physical quality witness failed");
  unsigned rejected = 0;
  const auto must_reject = [&](const research::PhysicalQuadCorners& points,
                               const research::PhysicalQuadCorners& normals) {
    try {
      (void)research::ObservePhysicalQuadQuality(points, normals);
    } catch (const std::invalid_argument&) {
      ++rejected;
    }
  };
  must_reject({{{0, 0, 0}, {0, 1, 0}, {1, 1, 0}, {1, 0, 0}}}, forward);
  must_reject({{{0, 0, 0}, {1, 0, 0}, {1, 0, 0}, {0, 1, 0}}}, forward);
  must_reject(square, {{{0, 0, -1}, {0, 0, -1}, {0, 0, -1}, {0, 0, -1}}});
  auto nonfinite = square;
  nonfinite[0][0] = std::numeric_limits<double>::quiet_NaN();
  must_reject(nonfinite, forward);
  Require(rejected == 4, "Malformed typed QUAD physical quality input was admitted");
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17) << "QUAD_TYPED_QUALITY quads=" << count
         << " min_scaled_jacobian=" << min_scaled << " min_warpage_cosine=" << min_warp_cosine
         << " max_edge_ratio=" << max_edge_ratio << " negative_cases=" << rejected
         << " policy=corner_normal_metric_probe adaptive_epochs=0\n";
  std::cout << output.str();
}

// Read the accepted physical candidate and choose a real native source leaf by error.
research::MixedSurfaceResidual ProbeMixedSurfaceResidual(const Candidate& candidate,
                                                         PatchBezier& patch) {
  std::vector<research::ResidualUv> parametric;
  std::vector<research::ResidualPoint3> physical;
  parametric.reserve(candidate.uv.size());
  physical.reserve(candidate.uv.size());
  for (std::size_t i = 0; i < candidate.uv.size(); ++i) {
    parametric.push_back({candidate.uv[i].u, candidate.uv[i].v});
    const auto* n = candidate.mesh->GetNoh(static_cast<unsigned>(i));
    Require(n != nullptr, "Mixed residual references a missing accepted physical node");
    physical.push_back({n->GetX(), n->GetY(), n->GetZ()});
  }
  const auto source = [&patch](const research::ResidualUv& uv) -> research::ResidualPoint3 {
    return Evaluate(patch, UvVertex{uv[0], uv[1]});
  };
  const auto metrics =
      research::MeasureMixedSurfaceResidual(parametric, physical, candidate.faces, source);
  Require(metrics.quadrilaterals == candidate.quads &&
              metrics.triangles == candidate.faces.size() - candidate.quads &&
              metrics.samples == 5 * metrics.quadrilaterals + 4 * metrics.triangles &&
              metrics.worst_quad_face < candidate.quad_origins.size() &&
              metrics.maximum >= metrics.quad_maximum &&
              metrics.maximum >= metrics.triangle_maximum &&
              metrics.worst_triangle_face >= candidate.quads &&
              metrics.worst_triangle_face < candidate.faces.size(),
          "Mixed physical error/source-leaf witness is invalid");
  const auto& leaf = candidate.quad_origins[metrics.worst_quad_face];
  Require(leaf.cell_id >= 0 && leaf.relative_depth >= 2 && metrics.worst_quad_sample_uv[0] > 0.0 &&
              metrics.worst_quad_sample_uv[0] < 1.0 && metrics.worst_quad_sample_uv[1] > 0.0 &&
              metrics.worst_quad_sample_uv[1] < 1.0,
          "Mixed residual selected an invalid real native quadtree source leaf");
  std::ostringstream line;
  line.imbue(std::locale::classic());
  line << std::setprecision(17) << "QUAD_SOURCE_RESIDUAL samples=" << metrics.samples
       << " quads=" << metrics.quadrilaterals << " triangles=" << metrics.triangles
       << " maximum=" << metrics.maximum << " rms=" << metrics.rms
       << " quad_maximum=" << metrics.quad_maximum
       << " triangle_maximum=" << metrics.triangle_maximum
       << " worst_quad_face=" << metrics.worst_quad_face
       << " worst_triangle_face=" << metrics.worst_triangle_face << " dominant_region="
       << (metrics.triangle_maximum > metrics.quad_maximum ? "tri_aft" : "quad_interior")
       << " tri_sample_u=" << metrics.worst_triangle_sample_uv[0]
       << " tri_sample_v=" << metrics.worst_triangle_sample_uv[1]
       << " real_leaf_ordinal=" << leaf.leaf_ordinal << " real_cell_id=" << leaf.cell_id
       << " source_depth=" << leaf.relative_depth << " select_u=" << metrics.worst_quad_sample_uv[0]
       << " select_v=" << metrics.worst_quad_sample_uv[1]
       << " policy=physical_bilinear_quad_tri_barycentric_v1"
       << " real_tree_edits=0 adaptive_epochs=0\n";
  std::cout << line.str();
  return metrics;
}

// Mutate only fresh native Quadtree proposals; preserve the first physical candidate.
struct NativeRefinementTrial {
  long chosen_cell_id = -1;
  unsigned initial_leaf_depth = 0;
  std::size_t leaves = 0;
  std::size_t quads = 0;
  long double interior_uv_area = 0.0L;
  bool emitted_disk = false;
  std::string rejection = "none";
};

NativeRefinementTrial TrialRealTreeRefinement(const research::ResidualUv& selected_uv) {
  Require(std::isfinite(selected_uv[0]) && std::isfinite(selected_uv[1]) && selected_uv[0] > 0.0 &&
              selected_uv[0] < 1.0 && selected_uv[1] > 0.0 && selected_uv[1] < 1.0,
          "Native QUAD tree refinement selection requires strict interior UV");
  auto tree = MakeSourceTree(true);
  NativeRefinementTrial trial;
  QuadtreeCell* target = nullptr;
  for (auto* leaf : tree->getLeaves()) {
    auto* minimum = leaf->getMin();
    auto* maximum = leaf->getMax();
    if (selected_uv[0] > minimum->getX() && selected_uv[0] < maximum->getX() &&
        selected_uv[1] > minimum->getY() && selected_uv[1] < maximum->getY()) {
      Require(target == nullptr, "Ambiguous native source cell chosen for refinement");
      target = leaf;
    }
  }
  Require(target != nullptr && !target->subdivided() && target->getLevel() < 8,
          "No eligible original native source quadtree leaf contains the error site");
  trial.chosen_cell_id = target->getId();
  trial.initial_leaf_depth = static_cast<unsigned>(target->getLevel());
  const auto leaves_before = tree->GetLeafCount();
  target->subdivideToLevel(target->getLevel() + 1);
  tree->refineAccordingToNeighbors();
  trial.leaves = tree->GetLeafCount();
  Require(trial.leaves > leaves_before,
          "Native source tree trial did not actually refine a source leaf");
  try {
    const auto captured = CaptureLeafPolygons(*tree);
    trial.interior_uv_area = captured.interior_area;
    const auto emitted = EmitLeafQuads(*tree, PointRule);
    trial.quads = emitted.quads.size();
    trial.emitted_disk = true;
  } catch (const std::invalid_argument& error) {
    // A disconnected island or broken 2:1 interface is a rejected native trial.
    trial.rejection = error.what();
  }
  return trial;
}

// A bounded three-leaf source refinement band reconnects a corner AFT island
// toward the interior QUAD region, without claiming any new physical mesh.
struct ConnectedBandTrial {
  std::array<long, 3> refined_cell_ids{{-1, -1, -1}};
  std::size_t baseline_leaves = 0;
  std::size_t leaves = 0;
  std::size_t quads = 0;
  long double uv_area = 0.0L;
  bool admitted_uv_disk = false;
  std::string rejection = "none";
};

ConnectedBandTrial
TrialConnectedAftBand(const research::ResidualUv& selected_uv,
                      std::unique_ptr<Quadtree>* retained_native_tree = nullptr) {
  Require(std::isfinite(selected_uv[0]) && std::isfinite(selected_uv[1]) && selected_uv[0] > 0.0 &&
              selected_uv[0] < 1.0 && selected_uv[1] > 0.0 && selected_uv[1] < 1.0,
          "Connected AFT band needs a real interior source residual sample");
  auto tree = MakeSourceTree(true);
  ConnectedBandTrial result;
  result.baseline_leaves = tree->GetLeafCount();
  const auto find_leaf = [&tree](double u, double v) -> QuadtreeCell* {
    QuadtreeCell* chosen = nullptr;
    for (auto* cell : tree->getLeaves()) {
      auto* low = cell->getMin();
      auto* high = cell->getMax();
      if (u > low->getX() && u < high->getX() && v > low->getY() && v < high->getY()) {
        Require(chosen == nullptr, "Ambiguous source leaf in connected band");
        chosen = cell;
      }
    }
    Require(chosen != nullptr, "Connected band source site lacks a native leaf");
    return chosen;
  };

  auto* corner = find_leaf(selected_uv[0], selected_uv[1]);
  const double u0 = corner->getMin()->getX();
  const double v0 = corner->getMin()->getY();
  const double du = corner->getMax()->getX() - u0;
  const double dv = corner->getMax()->getY() - v0;
  const double center_u = u0 + 0.5 * du;
  const double center_v = v0 + 0.5 * dv;
  // Only the current lower-left AFT-dominated corner geometry is qualified.
  Require(corner->getLevel() == 2 && center_u < 0.5 && center_v < 0.5 && std::isfinite(du) &&
              std::isfinite(dv) && du > 0.0 && dv > 0.0,
          "Connected AFT band requires the pinned corner source chart");
  auto* east = find_leaf(center_u + du, center_v);
  auto* north = find_leaf(center_u, center_v + dv);
  const std::array<QuadtreeCell*, 3> selected{{corner, east, north}};
  std::set<QuadtreeCell*> unique(selected.begin(), selected.end());
  Require(unique.size() == 3 && east->getLevel() == corner->getLevel() &&
              north->getLevel() == corner->getLevel(),
          "Connected band did not select three distinct native source leaves");
  for (std::size_t i = 0; i < selected.size(); ++i) {
    auto* leaf = selected[i];
    result.refined_cell_ids[i] = leaf->getId();
    Require(!leaf->subdivided(), "Connected band attempted repeat native leaf edit");
    leaf->subdivideToLevel(leaf->getLevel() + 1);
  }
  tree->refineAccordingToNeighbors();
  result.leaves = tree->GetLeafCount();
  Require(result.leaves >= result.baseline_leaves + 9,
          "Connected band did not perform three actual native subdivisions");
  try {
    const auto region = CaptureLeafPolygons(*tree);
    result.uv_area = region.interior_area;
    auto emitted = EmitLeafQuads(*tree, PointRule);
    result.quads = emitted.quads.size();
    result.admitted_uv_disk = true;
  } catch (const std::invalid_argument& failure) {
    // Retain the genuine native topological failure as a rejected proposal.
    result.rejection = failure.what();
  }
  if (result.admitted_uv_disk && retained_native_tree)
    *retained_native_tree = std::move(tree);
  return result;
}

void ProbeConnectedAftBand(const Candidate& unchanged,
                           const research::MixedSurfaceResidual& residual) {
  Require(unchanged.mesh && unchanged.quads > 0 &&
              residual.worst_triangle_face >= unchanged.quads &&
              residual.worst_triangle_face < unchanged.faces.size(),
          "Connected band has no previous real physical AFT source error");
  const auto observers = CaptureNodeObservers(*unchanged.mesh);
  const auto* original_node = unchanged.mesh->GetNoh(0);
  const auto* original_element = unchanged.mesh->GetElement(0);
  const auto band = TrialConnectedAftBand(residual.worst_triangle_sample_uv);
  Require(band.refined_cell_ids[0] == 6 && band.refined_cell_ids[1] > 0 &&
              band.refined_cell_ids[2] > 0 && unchanged.mesh->GetNoh(0) == original_node &&
              unchanged.mesh->GetElement(0) == original_element &&
              CaptureNodeObservers(*unchanged.mesh) == observers,
          "Connected native band lost physical source selection or prior owner identity");
  std::ostringstream out;
  out.imbue(std::locale::classic());
  out << std::setprecision(17) << "QUAD_CONNECTED_BAND_TRIAL"
      << " source=real_candidate_worst_aft_triangle"
      << " source_cell_id=" << band.refined_cell_ids[0]
      << " bridge_east_cell_id=" << band.refined_cell_ids[1]
      << " bridge_north_cell_id=" << band.refined_cell_ids[2]
      << " baseline_leaves=" << band.baseline_leaves << " refined_leaves=" << band.leaves
      << " native_leaf_edits=3"
      << " admitted_uv_disk=" << int(band.admitted_uv_disk) << " quad_uv_area=" << band.uv_area
      << " emitted_quads=" << band.quads << " prior_physical_owner_preserved=1"
      << " actual_aft_retriangulations=0"
      << " adaptive_epochs=0\n";
  std::cout << out.str();
  if (!band.admitted_uv_disk)
    std::cout << "QUAD_CONNECTED_BAND_REJECTION reason=" << band.rejection << '\n';
}

void ProbeNativeTreeAlternatives(const Candidate& unchanged,
                                 const research::MixedSurfaceResidual& residual) {
  Require(unchanged.mesh != nullptr && unchanged.quads > 0 &&
              residual.worst_quad_face < unchanged.quads &&
              residual.worst_triangle_face >= unchanged.quads &&
              residual.worst_triangle_face < unchanged.faces.size(),
          "Native tree trials lack a real physical candidate/error-face identity");
  const auto previous_observers = CaptureNodeObservers(*unchanged.mesh);
  const auto* node = unchanged.mesh->GetNoh(0);
  const auto* element = unchanged.mesh->GetElement(0);
  const auto baseline_tree = MakeSourceTree(true);
  const auto baseline = CaptureLeafPolygons(*baseline_tree);
  Require(baseline.source_leaves == 19 && baseline.interior_area == 0.25L,
          "Unexpected original fixed16 native QUAD region before refinement");
  const auto quad_trial = TrialRealTreeRefinement(residual.worst_quad_sample_uv);
  const auto aft_trial = TrialRealTreeRefinement(residual.worst_triangle_sample_uv);
  Require(quad_trial.chosen_cell_id != aft_trial.chosen_cell_id &&
              quad_trial.initial_leaf_depth == 2 && aft_trial.initial_leaf_depth == 2 &&
              quad_trial.leaves > baseline.source_leaves &&
              aft_trial.leaves > baseline.source_leaves,
          "Mixed source errors did not select two distinct real native level-2 leaves");
  Require(unchanged.mesh->GetNoh(0) == node && unchanged.mesh->GetElement(0) == element &&
              CaptureNodeObservers(*unchanged.mesh) == previous_observers,
          "Transient native tree trials damaged the original accepted physical candidate");
  Require(quad_trial.interior_uv_area >= baseline.interior_area || !quad_trial.emitted_disk,
          "Interior QUAD trial unexpectedly lost admitted source region");
  Require(aft_trial.interior_uv_area >= baseline.interior_area || !aft_trial.emitted_disk,
          "Boundary AFT trial unexpectedly lost admitted source region");

  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17) << "QUAD_NATIVE_TREE_TRIALS"
         << " source=generated_real_mixed_physical_candidate"
         << " baseline_leaves=" << baseline.source_leaves
         << " baseline_quad_uv_area=" << baseline.interior_area
         << " quad_cell_id=" << quad_trial.chosen_cell_id << " quad_leaves=" << quad_trial.leaves
         << " quad_emitted_disk=" << int(quad_trial.emitted_disk)
         << " quad_uv_area=" << quad_trial.interior_uv_area << " quad_faces=" << quad_trial.quads
         << " aft_cell_id=" << aft_trial.chosen_cell_id << " aft_leaves=" << aft_trial.leaves
         << " aft_emitted_disk=" << int(aft_trial.emitted_disk)
         << " aft_uv_area=" << aft_trial.interior_uv_area << " aft_quad_faces=" << aft_trial.quads
         << " source_candidate_preserved=1"
         << " native_trial_refinements=2"
         << " actual_adaptive_epochs=0\n";
  std::cout << output.str();
  // Preserve rejected-candidate reasons without admitting a partial quadtree.
  if (!quad_trial.emitted_disk)
    std::cout << "QUAD_NATIVE_TRIAL_REJECTION region=quad reason=" << quad_trial.rejection << '\n';
  if (!aft_trial.emitted_disk)
    std::cout << "QUAD_NATIVE_TRIAL_REJECTION region=aft reason=" << aft_trial.rejection << '\n';
}

void Export(const Candidate& result, const std::filesystem::path& path,
            bool source_scaffold = false) {
  Require(!std::filesystem::exists(path), "Controlled output already exists");
  auto staging = path;
  staging += ".pending";
  Require(std::filesystem::create_directory(staging), "Pending output already exists");
  const auto temporary = staging / "mesh.obj";
  try {
    std::ofstream out(temporary, std::ios::binary);
    out.imbue(std::locale::classic());
    Require(bool(out), "Cannot create controlled output");
    out << std::setprecision(17)
        << (result.generation_step == 0
                ? "# actual initial TRI reference; no native interior or mixed adaptive epoch\n"
            : result.real_boundary
                ? "# original curve workflow/native tree; experimental vertex_mean; mixed "
                  "adaptive_epochs=0\n"
                : "# controlled curved Bezier; experimental fixed16/vertex_mean; not adaptive\n");
    if (result.generation_step >= 0)
      out << "# generation_stage step=" << result.generation_step
          << " reference_tri_accepted=" << result.reference_accepted
          << " mixed_adaptive_epochs=0 reason=" << result.stage_reason << '\n';
    if (result.source_witness) {
      const auto& source = *result.source_witness;
      out << "# original_source step=" << source.source_step << " leaves=" << source.source_leaves
          << " nonuniform_sides=" << source.nonuniform_sides
          << " reversed_sides=" << source.reversed_sides
          << " domain_generation=" << source.domain_generation
          << " reference_tri_accepted=" << source.reference_tri_accepted << '\n';
      for (unsigned side = 0; side < 4; ++side)
        for (const auto& sample : source.original_curves[side])
          out << "# original_curve " << side << ' ' << source.reversed_curves[side] << ' '
              << sample.parameter << ' ' << sample.source_id << ' ' << sample.xyz[0] << ' '
              << sample.xyz[1] << ' ' << sample.xyz[2] << '\n';
      for (const auto& site : source.sites)
        out << "# source_site " << site.side << ' ' << site.parameter << ' ' << site.uv.u << ' '
            << site.uv.v << ' ' << site.source_id << ' ' << site.xyz[0] << ' ' << site.xyz[1] << ' '
            << site.xyz[2] << ' ' << site.edge_mid[0] << ' ' << site.edge_mid[1] << ' '
            << site.normalized_length << ' ' << site.refined_length << '\n';
    }
    for (unsigned i = 0; i < result.mesh->GetNumberNos(); ++i) {
      const auto* n = result.mesh->GetNoh(i);
      out << "v " << n->GetX() << ' ' << n->GetY() << ' ' << n->GetZ() << '\n';
      if (result.real_boundary)
        out << "# node_id " << i + 1 << ' ' << n->GetId() << '\n';
    }
    for (const auto& uv : result.uv)
      out << "vt " << uv.u << ' ' << uv.v << '\n';
    const auto& faces =
        source_scaffold && !result.source_faces.empty() ? result.source_faces : result.faces;
    const auto quads = source_scaffold ? result.seed_quads : result.quads;
    if (!result.article_commits.empty())
      out << "# article_front planar_UV_1993_rule prospective_choice_before_front_update=1"
             " smoothing="
          << (result.guarded_smoothing_comparison ? "guarded_uv_comparison"
                                                  : "uv_distinct_incident_vertices_jacobi_5_v1")
          << " curved_XYZ_lift=experimental\n";
    if (result.article_area_centroid)
      out << "# point_rule=polygon_area_centroid_uv_v1 historical_numeric_identity=unproven\n";
    if (!result.source_faces.empty()) {
      out << "# live_pair_policy physical_angle_pair_v1 source_scaffold=" << source_scaffold
          << " seed_quads=" << result.seed_quads
          << " paired_quads=" << result.aft_pair_origins.size() << '\n';
      if (!source_scaffold)
        for (std::size_t i = 0; i < result.aft_pair_origins.size(); ++i) {
          const auto& pair = result.aft_pair_origins[i];
          out << "# aft_pair_origin " << result.seed_quads + i + 1 << ' '
              << result.seed_quads + pair.first_triangle + 1 << ' '
              << result.seed_quads + pair.second_triangle + 1 << '\n';
        }
    }
    for (std::size_t i = 0; i < faces.size(); ++i) {
      if (i == 0)
        out << "g QUAD\n";
      if (i == quads)
        out << "g TRI_AFT\n";
      out << "f";
      for (auto id : faces[i])
        out << ' ' << id + 1 << '/' << id + 1;
      out << '\n';
    }
    out.close();
    Require(bool(out), "Controlled output write failed");
    // Same-directory link publishes without replacing any concurrently created output.
    std::filesystem::create_hard_link(temporary, path);
  } catch (...) {
    std::error_code ec;
    std::filesystem::remove(temporary, ec);
    std::filesystem::remove(staging, ec);
    throw;
  }
  std::error_code ec;
  std::filesystem::remove(temporary, ec);
  std::filesystem::remove(staging, ec);
}
// Test the *next* source-error-selected boundary band on actual native trees.
// The previously refined first band is rebuilt before every candidate trial.
// This does not publish a second physical SubMesh or accept an adaptive epoch.
struct SecondNativeBandTrial {
  std::size_t baseline_leaves = 0;
  std::size_t leaves = 0;
  std::size_t quads = 0;
  long double uv_area = 0.0L;
  long selected_cell_id = -1;
  long west_cell_id = -1;
  long north_cell_id = -1;
  bool admitted_uv_disk = false;
  std::string rejection = "none";
};

SecondNativeBandTrial
TrialSecondNativeBand(const research::ResidualUv& first_source,
                      const research::ResidualUv& second_source, unsigned variant,
                      std::unique_ptr<Quadtree>* retained_native_tree = nullptr) {
  Require(variant < 4 && std::isfinite(second_source[0]) && std::isfinite(second_source[1]) &&
              second_source[0] > 0.75 && second_source[0] < 1.0 && second_source[1] > 0.0 &&
              second_source[1] < 0.25,
          "Second connected AFT band needs the measured lower-right source chart");
  std::unique_ptr<Quadtree> tree;
  const auto first = TrialConnectedAftBand(first_source, &tree);
  Require(first.admitted_uv_disk && tree && first.leaves == 28 && first.quads == 62 &&
              first.uv_area == 0.328125L,
          "Second native trial did not reproduce the first physical source band");
  SecondNativeBandTrial result;
  result.baseline_leaves = tree->GetLeafCount();
  const auto find_leaf = [&tree](double u, double v) -> QuadtreeCell* {
    QuadtreeCell* chosen = nullptr;
    for (auto* cell : tree->getLeaves()) {
      auto* low = cell->getMin();
      auto* high = cell->getMax();
      if (u > low->getX() && u < high->getX() && v > low->getY() && v < high->getY()) {
        Require(chosen == nullptr, "Ambiguous second-band native source leaf");
        chosen = cell;
      }
    }
    Require(chosen != nullptr, "Second AFT source site lacks a native leaf");
    return chosen;
  };
  auto* corner = find_leaf(second_source[0], second_source[1]);
  Require(corner->getLevel() == 2 && corner->getMin()->getX() == 0.75 &&
              corner->getMin()->getY() == 0.0,
          "Second AFT source leaf was not the original lower-right level-2 cell");
  const double du = corner->getMax()->getX() - corner->getMin()->getX();
  const double dv = corner->getMax()->getY() - corner->getMin()->getY();
  Require(du == 0.25 && dv == 0.25, "Second AFT source cell changed its original dyadic extent");
  const double u = corner->getMin()->getX() + 0.5 * du;
  const double v = corner->getMin()->getY() + 0.5 * dv;
  auto* west = find_leaf(u - du, v);
  auto* north = find_leaf(u, v + dv);
  Require(west != corner && north != corner && west != north && west->getLevel() == 2 &&
              north->getLevel() == 2,
          "Second native AFT bridge cells are not distinct original leaves");
  result.selected_cell_id = corner->getId();
  result.west_cell_id = west->getId();
  result.north_cell_id = north->getId();
  std::vector<QuadtreeCell*> chosen{corner};
  if (variant & 1u)
    chosen.push_back(west);
  if (variant & 2u)
    chosen.push_back(north);
  for (auto* leaf : chosen) {
    Require(!leaf->subdivided() && leaf->getLevel() == 2,
            "Second native AFT trial attempted an invalid repeat source edit");
    leaf->subdivideToLevel(3);
  }
  tree->refineAccordingToNeighbors();
  result.leaves = tree->GetLeafCount();
  Require(result.leaves >= result.baseline_leaves + 3 * chosen.size(),
          "Second AFT native trial lost required source leaf edits");
  try {
    const auto region = CaptureLeafPolygons(*tree);
    result.uv_area = region.interior_area;
    const auto emitted = EmitLeafQuads(*tree, PointRule);
    result.quads = emitted.quads.size();
    result.admitted_uv_disk = true;
    if (retained_native_tree)
      *retained_native_tree = std::move(tree);
  } catch (const std::invalid_argument& failure) {
    // A disconnected island is reported as a rejected native proposal.
    result.rejection = failure.what();
  }
  return result;
}

void ProbeSecondNativeAftVariants(const Candidate& previous_physical,
                                  const research::MixedSurfaceResidual& first_source,
                                  const research::MixedSurfaceResidual& second_source) {
  Require(previous_physical.mesh && previous_physical.quads == 62 &&
              second_source.worst_triangle_face >= previous_physical.quads &&
              second_source.worst_triangle_face < previous_physical.faces.size(),
          "Second native refinement lacks the actual preceding physical AFT error");
  const auto previous_observers = CaptureNodeObservers(*previous_physical.mesh);
  const auto* previous_node = previous_physical.mesh->GetNoh(0);
  const auto* previous_element = previous_physical.mesh->GetElement(0);
  static const std::array<const char*, 4> names{{"corner", "west", "north", "both"}};
  for (unsigned variant = 0; variant < names.size(); ++variant) {
    const auto trial = TrialSecondNativeBand(first_source.worst_triangle_sample_uv,
                                             second_source.worst_triangle_sample_uv, variant);
    Require(previous_physical.mesh->GetNoh(0) == previous_node &&
                previous_physical.mesh->GetElement(0) == previous_element &&
                CaptureNodeObservers(*previous_physical.mesh) == previous_observers,
            "Second temporary native refinement modified the previous physical owner");
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::setprecision(17) << "QUAD_SECOND_NATIVE_BAND"
        << " variant=" << names[variant] << " source=staged_previous_physical_worst_aft"
        << " selected_native_id=" << trial.selected_cell_id
        << " west_native_id=" << trial.west_cell_id << " north_native_id=" << trial.north_cell_id
        << " baseline_leaves=" << trial.baseline_leaves << " refined_leaves=" << trial.leaves
        << " native_leaf_edits=" << (1u + ((variant & 1u) != 0u) + ((variant & 2u) != 0u))
        << " admitted_uv_disk=" << int(trial.admitted_uv_disk) << " quad_uv_area=" << trial.uv_area
        << " emitted_quads=" << trial.quads << " previous_physical_owner_preserved=1"
        << " actual_second_aft_retriangulations=0"
        << " adaptive_epochs=0\n";
    std::cout << out.str();
    if (!trial.admitted_uv_disk)
      std::cout << "QUAD_SECOND_NATIVE_BAND_REJECTION variant=" << names[variant]
                << " reason=" << trial.rejection << '\n';
  }
}

// Reconstruct each new native disk with the ORIGINAL AFT exterior pipeline.
// A failure remains a rejected proposal: no prior typed owner is replaced.
// The original source's fixed16 boundary is retained, so no true mixed epoch.
void ProbeSecondPhysicalAftVariants(const Candidate& previous_physical, PatchBezier& patch,
                                    const research::MixedSurfaceResidual& first_source,
                                    const research::MixedSurfaceResidual& second_source,
                                    const std::filesystem::path& output_prefix) {
  Require(previous_physical.mesh && previous_physical.quads == 62 &&
              second_source.worst_triangle_face >= previous_physical.quads &&
              second_source.worst_triangle_face < previous_physical.faces.size(),
          "Second physical AFT trials require the preceding real mixed source residual");
  const auto previous_observers = CaptureNodeObservers(*previous_physical.mesh);
  auto* previous_node = previous_physical.mesh->GetNoh(0);
  auto* previous_element = previous_physical.mesh->GetElement(0);
  auto* previous_patch_owner = patch.GetSubMesh();
  static const std::array<const char*, 4> names{{"corner", "west", "north", "both"}};
  for (unsigned variant = 0; variant < names.size(); ++variant) {
    const auto native = TrialSecondNativeBand(first_source.worst_triangle_sample_uv,
                                              second_source.worst_triangle_sample_uv, variant);
    const auto candidate_path = std::filesystem::path(
        output_prefix.string() + "." + names[variant] + ".second-band-candidate.obj");
    bool staged = false;
    std::string reason = native.rejection;
    std::size_t physical_nodes = 0;
    std::size_t physical_quads = 0;
    std::size_t physical_triangles = 0;
    double min_facet_quality = 0.0;
    double max_source_error = 0.0;
    if (native.admitted_uv_disk) {
      try {
        const auto factory = [&first_source, &second_source, variant,
                              &native]() -> std::unique_ptr<Quadtree> {
          std::unique_ptr<Quadtree> ready;
          const auto repeat =
              TrialSecondNativeBand(first_source.worst_triangle_sample_uv,
                                    second_source.worst_triangle_sample_uv, variant, &ready);
          Require(ready && repeat.admitted_uv_disk && repeat.quads == native.quads &&
                      repeat.leaves == native.leaves && repeat.uv_area == native.uv_area,
                  "Original native AFT and QUAD template trees differ for second band");
          return ready;
        };
        // Generate invokes the same native tree factory separately for the
        // original TRI reference front and typed QUAD/interior AFT pipeline.
        auto candidate = Generate(patch, false, factory);
        CheckTypedIncidence(*candidate.mesh, candidate);
        Require(candidate.quads == native.quads && candidate.faces.size() > candidate.quads &&
                    candidate.mesh->GetNumberNos() == candidate.uv.size(),
                "Native second physical band lost actual typed QUAD/AFT elements");
        std::vector<research::ResidualUv> uv;
        std::vector<research::ResidualPoint3> xyz;
        uv.reserve(candidate.uv.size());
        xyz.reserve(candidate.uv.size());
        for (std::size_t i = 0; i < candidate.uv.size(); ++i) {
          uv.push_back({candidate.uv[i].u, candidate.uv[i].v});
          const auto* node = candidate.mesh->GetNoh(static_cast<unsigned>(i));
          Require(node != nullptr, "Second AFT physical candidate contains a null node");
          xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
        }
        const auto source = [&patch](const research::ResidualUv& site) -> research::ResidualPoint3 {
          return Evaluate(patch, {site[0], site[1]});
        };
        const auto errors = research::MeasureMixedSurfaceResidual(uv, xyz, candidate.faces, source);
        Require(errors.quadrilaterals == candidate.quads &&
                    errors.triangles == candidate.faces.size() - candidate.quads &&
                    errors.triangles > 0 && std::isfinite(errors.maximum) &&
                    std::isfinite(candidate.min_quality) && candidate.min_quality > 0.0,
                "Second AFT physical proposal failed typed Bezier quality/source checks");
        physical_nodes = candidate.mesh->GetNumberNos();
        physical_quads = candidate.quads;
        physical_triangles = errors.triangles;
        min_facet_quality = candidate.min_quality;
        max_source_error = errors.maximum;
        Require(!std::filesystem::exists(candidate_path),
                "Second unaccepted AFT physical output already exists");
        // Preserve both previously generated physical owners: artifact only.
        Export(candidate, candidate_path);
        staged = true;
      } catch (const std::exception& failure) {
        reason = failure.what();
      }
    }
    Require(patch.GetSubMesh() == previous_patch_owner &&
                previous_physical.mesh->GetNoh(0) == previous_node &&
                previous_physical.mesh->GetElement(0) == previous_element &&
                CaptureNodeObservers(*previous_physical.mesh) == previous_observers,
            "Second AFT physical proposal mutated earlier typed owner/observers");
    Require(staged == std::filesystem::exists(candidate_path),
            "Second physical AFT output presence differs from recorded status");
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::setprecision(17) << "QUAD_SECOND_PHYSICAL_AFT_CANDIDATE"
        << " variant=" << names[variant]
        << " status=" << (staged ? "staged_unaccepted" : "rejected")
        << " source=previous_staged_physical_worst_aft"
        << " native_leaves=" << native.leaves << " native_quad_uv_area=" << native.uv_area
        << " native_emitted_quads=" << native.quads << " physical_nodes=" << physical_nodes
        << " physical_quads=" << physical_quads << " physical_triangles=" << physical_triangles
        << " min_facet_quality=" << min_facet_quality << " max_source_error=" << max_source_error
        << " original_aft_pipeline_requested=" << int(native.admitted_uv_disk)
        << " exported_candidate=" << int(staged) << " previous_physical_owner_preserved=1"
        << " adaptive_epochs=0\n";
    std::cout << out.str();
    if (!staged)
      std::cout << "QUAD_SECOND_PHYSICAL_AFT_REJECTION variant=" << names[variant]
                << " reason=" << reason << '\n';
  }
}

// A completely separate, non-accepted physical candidate rebuilt from the
// exact source-error-selected connected native tree and original AFT pipeline.
void ProbePhysicalConnectedBand(const Candidate& previous, PatchBezier& patch,
                                const research::MixedSurfaceResidual& source_residual,
                                const std::filesystem::path& output_prefix) {
  Require(previous.mesh && previous.quads > 0 &&
              source_residual.worst_triangle_face >= previous.quads &&
              source_residual.worst_triangle_face < previous.faces.size(),
          "Physical connected band requires a genuine preceding mixed candidate");
  const auto previous_observers = CaptureNodeObservers(*previous.mesh);
  auto* previous_node = previous.mesh->GetNoh(0);
  auto* previous_element = previous.mesh->GetElement(0);
  auto* previous_patch_owner = patch.GetSubMesh();
  const auto sample = source_residual.worst_triangle_sample_uv;
  const auto candidate_path = std::filesystem::path(output_prefix.string() + ".band-candidate.obj");
  const auto factory = [sample]() -> std::unique_ptr<Quadtree> {
    std::unique_ptr<Quadtree> ready;
    const auto band = TrialConnectedAftBand(sample, &ready);
    Require(band.admitted_uv_disk && ready && band.refined_cell_ids[0] == 6 &&
                band.refined_cell_ids[1] == 7 && band.refined_cell_ids[2] == 9 &&
                band.leaves == 28 && band.quads == 62 && band.uv_area == 0.328125L,
            "Physical connected band lacks an independently admissible original native tree");
    return ready;
  };
  bool staged = false;
  std::string reason = "none";
  std::size_t physical_quads = 0;
  std::size_t physical_triangles = 0;
  std::size_t physical_nodes = 0;
  double maximum_error = 0.0;
  double maximum_triangle_error = 0.0;
  double maximum_quad_error = 0.0;
  double minimum_facet_quality = 0.0;
  try {
    // The original AFT gets its own real *band-refined* legacy front.
    // The new QUAD selector consumes a second identical but independent tree.
    auto candidate = Generate(patch, false, factory);
    CheckTypedIncidence(*candidate.mesh, candidate);
    Require(candidate.quads == 62 && candidate.faces.size() > candidate.quads &&
                candidate.mesh->GetNumberNos() == candidate.uv.size(),
            "Band-refined physical proposal lacks both typed QUAD and original AFT TRI");
    std::vector<research::ResidualUv> uv;
    std::vector<research::ResidualPoint3> xyz;
    uv.reserve(candidate.uv.size());
    xyz.reserve(candidate.uv.size());
    for (std::size_t i = 0; i < candidate.uv.size(); ++i) {
      uv.push_back({candidate.uv[i].u, candidate.uv[i].v});
      const auto* node = candidate.mesh->GetNoh(static_cast<unsigned>(i));
      Require(node != nullptr, "Physical band has a null typed node");
      xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
    }
    const auto source = [&patch](const research::ResidualUv& uv_site) -> research::ResidualPoint3 {
      return Evaluate(patch, {uv_site[0], uv_site[1]});
    };
    const auto errors = research::MeasureMixedSurfaceResidual(uv, xyz, candidate.faces, source);
    Require(errors.quadrilaterals == candidate.quads &&
                errors.triangles == candidate.faces.size() - candidate.quads &&
                errors.triangles > 0 && std::isfinite(errors.maximum) &&
                std::isfinite(candidate.min_quality) && candidate.min_quality > 0.0,
            "Band candidate failed original Bezier source or facet quality admission");
    ProbeSecondNativeAftVariants(candidate, source_residual, errors);
    ProbeSecondPhysicalAftVariants(candidate, patch, source_residual, errors, output_prefix);
    physical_quads = candidate.quads;
    physical_triangles = errors.triangles;
    physical_nodes = candidate.mesh->GetNumberNos();
    maximum_error = errors.maximum;
    maximum_quad_error = errors.quad_maximum;
    maximum_triangle_error = errors.triangle_maximum;
    minimum_facet_quality = candidate.min_quality;
    Require(!std::filesystem::exists(candidate_path),
            "Nonaccepted physical band candidate output already exists");
    // Candidate-only artifact; no Patch/SubMesh owner adoption and no epoch commit.
    Export(candidate, candidate_path);
    staged = true;
  } catch (const std::exception& error) {
    reason = error.what();
  }
  Require(patch.GetSubMesh() == previous_patch_owner && previous.mesh->GetNoh(0) == previous_node &&
              previous.mesh->GetElement(0) == previous_element &&
              CaptureNodeObservers(*previous.mesh) == previous_observers,
          "Rejected or staged physical band damaged the existing mixed owner");
  Require(staged == std::filesystem::exists(candidate_path),
          "Physical candidate publication status disagrees with actual file");
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17) << "QUAD_BAND_PHYSICAL_CANDIDATE"
         << " status=" << (staged ? "staged_unaccepted" : "rejected")
         << " source=original_native_connected_band"
         << " previous_physical_owner_preserved=1"
         << " original_aft_pipeline_requested=1"
         << " physical_quads=" << physical_quads << " physical_triangles=" << physical_triangles
         << " physical_nodes=" << physical_nodes << " max_source_error=" << maximum_error
         << " max_quad_error=" << maximum_quad_error << " max_aft_error=" << maximum_triangle_error
         << " min_facet_quality=" << minimum_facet_quality << " exported_candidate=" << int(staged)
         << " adaptive_epochs=0\n";
  std::cout << output.str();
  if (!staged)
    std::cout << "QUAD_BAND_PHYSICAL_REJECTION reason=" << reason << '\n';
}

// A complete physical owner snapshot also records the ORDERED node observers.
struct OwnerRehearsalWitness {
  SubMesh* owner = nullptr;
  std::vector<NodeAdaptive*> nodes;
  std::vector<ElementAdaptive*> elements;
  std::vector<unsigned long> node_ids;
  std::vector<Xyz> physical_xyz;
  std::vector<std::array<double, 4>> node_curvatures;
  std::vector<unsigned long> element_ids;
  std::vector<double> element_areas;
  std::vector<std::vector<ElementAdaptive*>> ordered_observers;
};

OwnerRehearsalWitness SnapshotOwnerRehearsal(SubMesh& mesh) {
  OwnerRehearsalWitness result;
  result.owner = &mesh;
  result.ordered_observers = CaptureNodeObservers(mesh);
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    auto* node = mesh.GetNoh(i);
    Require(node != nullptr, "Accepted owner has a missing physical node");
    result.nodes.push_back(node);
    result.node_ids.push_back(node->GetId());
    result.physical_xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
    result.node_curvatures.push_back({node->GetGa(), node->GetGd(), node->GetHa(), node->GetHd()});
  }
  for (unsigned i = 0; i < mesh.GetNumberElements(); ++i) {
    auto* element = mesh.GetElement(i);
    Require(element != nullptr, "Accepted owner has a missing typed element");
    result.elements.push_back(element);
    result.element_ids.push_back(element->GetId());
    result.element_areas.push_back(element->GetArea());
  }
  return result;
}

void RequireOwnerRehearsalUnchanged(PatchBezier& patch, const OwnerRehearsalWitness& original) {
  Require(original.owner != nullptr && patch.GetSubMesh() == original.owner &&
              original.owner->GetPatch() == &patch &&
              original.nodes.size() == original.owner->GetNumberNos() &&
              original.elements.size() == original.owner->GetNumberElements() &&
              CaptureNodeObservers(*original.owner) == original.ordered_observers,
          "Owner rehearsal lost the previously accepted physical graph");
  for (std::size_t i = 0; i < original.nodes.size(); ++i) {
    const auto* node = original.owner->GetNoh(static_cast<unsigned>(i));
    Require(node == original.nodes[i] && node->GetId() == original.node_ids[i] &&
                Xyz{node->GetX(), node->GetY(), node->GetZ()} == original.physical_xyz[i] &&
                (std::array<double, 4>{node->GetGa(), node->GetGd(), node->GetHa(),
                                       node->GetHd()}) == original.node_curvatures[i],
            "Failed physical transaction changed accepted node identity, XYZ or curvature");
  }
  for (std::size_t i = 0; i < original.elements.size(); ++i) {
    auto* element = original.owner->GetElement(static_cast<unsigned>(i));
    Require(element == original.elements[i] && element->GetId() == original.element_ids[i] &&
                element->GetArea() == original.element_areas[i],
            "Failed physical transaction changed accepted element identity or area");
  }
}

std::string ReadRehearsalOutput(const std::filesystem::path& file) {
  std::ifstream stream(file, std::ios::binary);
  Require(bool(stream), "Previously accepted physical OBJ was not readable");
  return {std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>()};
}

// Test only: real native AFT successor of an already-published physical P1
// graph. Swaps are reversible rehearsals, not scientifically admitted epochs.
// No second artifact is published; all exceptions precede the noexcept swap.
void ProbePhysicalOwnerTransactionRehearsal(PatchBezier& patch, SubMesh& accepted,
                                            const Candidate& original,
                                            const research::MixedSurfaceResidual& first_source,
                                            const std::filesystem::path& output_prefix) {
  Require(accepted.GetNumberNos() == 69 && original.quads == 42 && original.faces.size() == 78 &&
              patch.GetSubMesh() == &accepted,
          "Owner transaction rehearsal requires the real previously published P1 graph");
  CheckTypedIncidence(accepted, original);
  const auto witness = SnapshotOwnerRehearsal(accepted);
  const auto previous_file = std::filesystem::path(output_prefix.string() + ".obj");
  const auto original_bytes = ReadRehearsalOutput(previous_file);

  // Recompute the source error from the ACTUAL published previous owner,
  // not merely from a separate proposal measured before publication.
  std::vector<research::ResidualUv> accepted_uv;
  std::vector<research::ResidualPoint3> accepted_xyz;
  accepted_uv.reserve(original.uv.size());
  accepted_xyz.reserve(original.uv.size());
  for (std::size_t i = 0; i < original.uv.size(); ++i) {
    accepted_uv.push_back({original.uv[i].u, original.uv[i].v});
    const auto* node = accepted.GetNoh(static_cast<unsigned>(i));
    Require(node != nullptr, "Accepted prior owner has a missing source-error node");
    accepted_xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
  }
  const auto source = [&patch](const research::ResidualUv& site) -> research::ResidualPoint3 {
    return Evaluate(patch, {site[0], site[1]});
  };
  const auto actual_prior_source =
      research::MeasureMixedSurfaceResidual(accepted_uv, accepted_xyz, original.faces, source);
  Require(actual_prior_source.worst_triangle_face == first_source.worst_triangle_face &&
              actual_prior_source.worst_triangle_sample_uv ==
                  first_source.worst_triangle_sample_uv &&
              std::abs(actual_prior_source.maximum - first_source.maximum) <= 1e-14,
          "Actual published P1 owner source error diverges from original native AFT");
  const auto source_site = actual_prior_source.worst_triangle_sample_uv;
  const auto factory = [source_site]() -> std::unique_ptr<Quadtree> {
    std::unique_ptr<Quadtree> tree;
    const auto trial = TrialConnectedAftBand(source_site, &tree);
    Require(trial.admitted_uv_disk && tree && trial.leaves == 28 && trial.quads == 62 &&
                trial.uv_area == 0.328125L,
            "Owner rehearsal successor differs from the real native error-selected band");
    return tree;
  };
  unsigned injected_failures = 0;
  for (unsigned stage = 0; stage < 5; ++stage) {
    try {
      if (stage == 0)
        throw PublicationFailure("Injected owner trial failure before native reconstruction");
      auto layout = Generate(patch, stage == 1, factory);
      CheckTypedIncidence(*layout.mesh, layout);
      Require(layout.quads == 62 && layout.mesh->GetNumberNos() == 93 && layout.faces.size() == 106,
              "Owner transaction trial successor is not the genuine typed physical band");
      auto trial = CloneTypedHistory(*layout.mesh, layout, patch, stage == 2 ? 7 : -1);
      CheckTypedIncidence(*trial, layout);
      if (stage == 3) {
        // A back observer may be prepared without adopting the forward owner.
        trial->SetPatch(&patch);
        throw PublicationFailure("Injected failure after back-observer staging");
      }
      if (stage == 4)
        throw PublicationFailure("Injected failure immediately before noexcept owner swap");
      throw std::runtime_error("Physical owner failure injection did not fire");
    } catch (const PublicationFailure&) {
      ++injected_failures;
    }
    RequireOwnerRehearsalUnchanged(patch, witness);
    Require(ReadRehearsalOutput(previous_file) == original_bytes,
            "Failed physical transaction altered accepted OBJ output bytes");
  }
  Require(injected_failures == 5,
          "Accepted physical owner rehearsal did not reject every injected failure");

  auto physical = Generate(patch, false, factory);
  Require(physical.quads == 62 && physical.mesh->GetNumberNos() == 93 &&
              physical.faces.size() == 106,
          "Owner rehearsal success is not the actual next native AFT physical band");
  auto staged = CloneTypedHistory(*physical.mesh, physical, patch, -1);
  CheckTypedIncidence(*staged, physical);
  Require(staged->GetNoh(0) != witness.nodes.front() &&
              staged->GetElement(0) != witness.elements.front(),
          "Replacement typed physical history aliases the accepted owner");

  // No filesystem mutation or unknown-throwing work occurs after this point.
  // This real patch swap is deliberately REVERSED before the function returns.
  {
    struct RestorePrevious final {
      PatchBezier& patch;
      SubMesh* prior;
      ~RestorePrevious() noexcept { patch.SetSubMesh(prior); }
    } restore{patch, &accepted};
    staged->SetPatch(&patch);
    patch.SetSubMesh(staged.get());
    Require(patch.GetSubMesh() == staged.get() && staged->GetPatch() == &patch,
            "Noexcept owner rehearsal could not temporarily adopt the real typed successor");
    CheckTypedIncidence(*staged, physical);
    patch.SetSubMesh(&accepted);
    staged->SetPatch(nullptr);
  }
  RequireOwnerRehearsalUnchanged(patch, witness);
  Require(ReadRehearsalOutput(previous_file) == original_bytes,
          "Temporary owner swap modified the original published physical OBJ");
  CheckTypedIncidence(*staged, physical);
  std::cout << "QUAD_OWNER_TRANSACTION_REHEARSAL"
            << " source=published_previous_P1_real_AFT"
            << " prior_nodes=69 prior_quads=42 prior_triangles=36"
            << " next_nodes=93 next_quads=62 next_triangles=44"
            << " injected_failures=" << injected_failures << " temporary_noexcept_swaps=1"
            << " reverted_to_previous_owner=1"
            << " ordered_node_observers_preserved=1"
            << " node_curvature_and_element_area_preserved=1"
            << " previous_obj_bytes_unchanged=1"
            << " measured_after_actual_prior_owner_publication=1"
            << " accepted_adaptive_epochs=0\n";
}

// Copy the actual TRI state while its owner is live. Coarse steps with no
// interior cells remain TRI; no QUAD island or extra source samples are invented.
Candidate SnapshotTriStage(const SubMesh& mesh, PatchBezier& patch) {
  Candidate result;
  result.real_boundary = true;
  std::map<unsigned long, std::size_t> ids;
  result.uv.resize(mesh.GetNumberNos());
  std::vector<bool> assigned(mesh.GetNumberNos(), false);
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    const auto id = mesh.GetNoh(i)->GetId();
    Require(ids.emplace(id, i).second, "Reference TRI node IDs are not unique");
    result.node_ids.push_back(id);
  }
  for (unsigned i = 0; i < mesh.GetNumberElements(); ++i) {
    const auto* tri = dynamic_cast<const TriangleAdaptive*>(mesh.GetElement(i));
    Require(tri != nullptr, "Reference state contains a non-TRI element");
    const std::array<std::tuple<double, double>, 3> parameters{
        tri->GetParametersN1(), tri->GetParametersN2(), tri->GetParametersN3()};
    std::vector<std::size_t> face;
    for (unsigned j = 0; j < 3; ++j) {
      const auto vertex = tri->GetVertexPoint(j + 1);
      const auto index = ids.at(vertex.GetId());
      const UvVertex uv{std::get<0>(parameters[j]), std::get<1>(parameters[j])};
      Require(!assigned[index] || (result.uv[index].u == uv.u && result.uv[index].v == uv.v),
              "Reference TRI parameter identity is inconsistent");
      result.uv[index] = uv;
      assigned[index] = true;
      face.push_back(index);
    }
    result.faces.push_back(std::move(face));
  }
  Require(std::all_of(assigned.begin(), assigned.end(), [](bool value) { return value; }),
          "Reference state has unused nodes");
  result.mesh = CloneTypedHistory(mesh, result, patch, -1);
  CheckTypedIncidence(*result.mesh, result);
  return result;
}

using GroupingBoxes = std::array<std::array<double, 4>, 2>;

struct GeometricRequest {
  std::size_t face;
  UvVertex site;
  double size;
};

struct ChildCurveRequest {
  std::size_t interval;
  int child;
};
constexpr std::size_t MaxCertifiedChildRequests = 3;

struct FeedbackPlan {
  std::vector<GeometricRequest> predecessor, recovered;
  std::vector<std::size_t> curve_intervals;
  std::vector<ChildCurveRequest> child_curves;
  bool replay_previous_search = false;
  bool guarded_smoothing = false;
  bool additional_pairs = false;
  std::optional<double> additional_pair_error_limit;
  bool certify_boundary_refinement = false;
  std::vector<std::array<double, 4>> group_feedback_parents;
  std::optional<std::array<double, 4>> measured_contour_parent;
  std::optional<std::size_t> refine_feedback_leaf_again;
  std::optional<IdealFrontLimits> ideal_front_limits;
};

FeedbackPlan ReadFeedbackPlan(const std::filesystem::path& path) {
  std::ifstream input(path);
  input.imbue(std::locale::classic());
  std::string schema;
  input >> schema;
  Require(bool(input) && schema == "apmesh_curvabezier_feedback_v1",
          "Invalid geometric feedback plan");
  FeedbackPlan plan;
  std::string arm;
  while (input >> arm) {
    if (arm == "previous_search") {
      Require(!plan.replay_previous_search, "Duplicate predecessor lookup control");
      plan.replay_previous_search = true;
      continue;
    }
    if (arm == "guarded_smoothing") {
      Require(!plan.guarded_smoothing, "Duplicate guarded smoothing comparison");
      plan.guarded_smoothing = true;
      continue;
    }
    if (arm == "curve") {
      std::size_t i = 0;
      input >> i;
      Require(bool(input), "Missing feedback curve interval");
      plan.curve_intervals.push_back(i);
      continue;
    }
    GeometricRequest request{};
    input >> request.face >> request.site.u >> request.site.v >> request.size;
    Require(bool(input) && request.site.u >= 0 && request.site.u <= 1 && request.site.v >= 0 &&
                request.site.v <= 1 && std::isfinite(request.size) && request.size > 0,
            "Invalid geometric feedback request");
    Require(arm == "predecessor" || arm == "recovered", "Unknown geometric feedback arm");
    auto& requests = arm == "predecessor" ? plan.predecessor : plan.recovered;
    requests.push_back(request);
  }
  Require(input.eof() && !plan.predecessor.empty() && !plan.recovered.empty(),
          "Geometric feedback needs both measured request lists");
  Require(!plan.replay_previous_search || plan.curve_intervals.empty(),
          "Previous lookup requires an unchanged curve");
  Require(!plan.guarded_smoothing || !plan.curve_intervals.empty(),
          "Guarded smoothing comparison requires curve feedback");
  return plan;
}

struct NativeFeedbackPlan {
  int step = 0;
  FeedbackPlan feedback;
  std::optional<std::filesystem::path> reference;
};

NativeFeedbackPlan ReadNativeFeedbackPlan(const std::filesystem::path& path) {
  std::ifstream input(path);
  input.imbue(std::locale::classic());
  std::string schema;
  NativeFeedbackPlan plan;
  input >> schema >> plan.step;
  Require(bool(input) && schema == "apmesh_single_patch_feedback_v1" && plan.step > 0,
          "Invalid single-patch feedback plan");
  std::string kind;
  auto& feedback = plan.feedback;
  feedback.guarded_smoothing = true;
  while (input >> kind) {
    if (kind == "group_feedback_parent" || kind == "group_feedback_contour_parent" ||
        kind == "group_feedback_contour_parent_preserve_sizes") {
      std::array<double, 4> box{};
      for (double& coordinate : box)
        input >> coordinate;
      const bool on_contour = box[0] == 0 || box[1] == 0 || box[2] == 1 || box[3] == 1;
      const bool contour_plan = kind != "group_feedback_parent";
      // Contour parents are handed to the advancing front by the existing template dispatcher.
      Require(bool(input) && 0 <= box[0] && 0 <= box[1] && box[0] < box[2] && box[1] < box[3] &&
                  box[2] <= 1 && box[3] <= 1 && box[2] - box[0] == box[3] - box[1] &&
                  on_contour == contour_plan,
              contour_plan ? "Invalid contour feedback grouping parent"
                           : "Invalid interior feedback grouping parent");
      for (const auto& prior : feedback.group_feedback_parents)
        Require(std::max(prior[0], box[0]) >= std::min(prior[2], box[2]) ||
                    std::max(prior[1], box[1]) >= std::min(prior[3], box[3]),
                "Feedback grouping parents must have disjoint interiors");
      if (kind == "group_feedback_contour_parent_preserve_sizes") {
        Require(!feedback.measured_contour_parent, "Only one measured contour parent is allowed");
        feedback.measured_contour_parent = box;
      }
      feedback.group_feedback_parents.push_back(box);
    } else if (kind == "certify_boundary_refinement") {
      Require(!feedback.certify_boundary_refinement, "Duplicate boundary refinement certification");
      feedback.certify_boundary_refinement = true;
    } else if (kind == "additional_pairs") {
      Require(!feedback.additional_pairs, "Duplicate additional-pair request");
      feedback.additional_pairs = true;
    } else if (kind == "additional_pair_error_limit") {
      double limit = 0.0;
      input >> limit;
      Require(bool(input) && std::isfinite(limit) && limit >= 0 &&
                  !feedback.additional_pair_error_limit,
              "Invalid additional-pair relative error limit");
      feedback.additional_pair_error_limit = limit;
    } else if (kind == "ideal_front_points" || kind == "guarded_ideal_closure" ||
               kind == "guarded_front_order") {
      long long limit = 0;
      IdealFrontLimits floors{};
      floors.order_only = kind == "guarded_front_order";
      if (!floors.order_only)
        input >> limit;
      input >> floors.min_angle >> floors.min_shape;
      Require(bool(input) && (floors.order_only || limit > 0) &&
                  static_cast<unsigned long long>(limit) <=
                      std::numeric_limits<std::size_t>::max() &&
                  floors.min_angle > 0 && floors.min_angle <= 60 && floors.min_shape > 0 &&
                  floors.min_shape <= 1 && !feedback.ideal_front_limits,
              "Invalid guarded front policy limits");
      floors.points = static_cast<std::size_t>(limit);
      if (kind != "ideal_front_points") {
        std::array<double, 2> quad{};
        input >> quad[1] >> quad[0];
        Require(bool(input) && quad[1] > 0 && quad[1] <= 90 && quad[0] > 0 && quad[0] <= 1,
                "Invalid ideal closure QUAD quality limits");
        floors.quad_floors = quad;
      }
      feedback.ideal_front_limits = floors;
    } else if (kind == "reference") {
      std::string path;
      input >> std::quoted(path);
      Require(bool(input) && !path.empty() && !plan.reference,
              "Invalid single-patch feedback reference");
      plan.reference = path;
    } else if (kind == "curve") {
      std::size_t interval = 0;
      input >> interval;
      Require(bool(input), "Missing single-patch curve interval");
      feedback.curve_intervals.push_back(interval);
    } else if (kind == "curve_child") {
      ChildCurveRequest request{};
      input >> request.interval >> request.child;
      const auto repeated = [&](const auto& prior) {
        return prior.interval == request.interval && prior.child == request.child;
      };
      Require(
          bool(input) && (request.child == 0 || request.child == 1) &&
              !std::any_of(feedback.child_curves.begin(), feedback.child_curves.end(), repeated),
          "Invalid or repeated single-patch child curve request");
      Require(feedback.child_curves.size() < MaxCertifiedChildRequests,
              "Single-patch child curve request limit exceeded");
      feedback.child_curves.push_back(request);
    } else if (kind == "refine_feedback_leaf_again") {
      std::size_t face = 0;
      input >> face;
      Require(bool(input) && !feedback.refine_feedback_leaf_again,
              "Invalid or duplicate follow-up leaf request");
      feedback.refine_feedback_leaf_again = face;
    } else {
      GeometricRequest request{};
      input >> request.face >> request.site.u >> request.site.v >> request.size;
      Require(bool(input) && kind == "face" && request.site.u >= 0 && request.site.u <= 1 &&
                  request.site.v >= 0 && request.site.v <= 1 && std::isfinite(request.size) &&
                  request.size > 0,
              "Invalid single-patch face request");
      feedback.recovered.push_back(request);
    }
  }
  Require(input.eof(), "Unexpected data in single-patch feedback plan");
  const bool have_requests = !feedback.recovered.empty() || !feedback.curve_intervals.empty();
  Require(have_requests == plan.reference.has_value(),
          "Single-patch feedback requests and reference must be supplied together");
  Require(!feedback.additional_pairs || have_requests,
          "Additional local pairs require a successor request");
  Require(!feedback.additional_pair_error_limit || feedback.additional_pairs,
          "An additional-pair error limit requires additional local pairs");
  Require(!feedback.certify_boundary_refinement || have_requests,
          "Boundary refinement certification requires a bound successor request");
  for (const auto request : feedback.child_curves)
    Require(feedback.certify_boundary_refinement &&
                std::count(feedback.curve_intervals.begin(), feedback.curve_intervals.end(),
                           request.interval) == 1,
            "Child curve requests require one certified parent split");
  Require(feedback.group_feedback_parents.empty() || feedback.certify_boundary_refinement,
          "Feedback grouping requires certified predecessor boundary refinement");
  Require(!feedback.ideal_front_limits || feedback.certify_boundary_refinement,
          "Ideal front points require certified predecessor boundary refinement");
  if (feedback.refine_feedback_leaf_again) {
    const auto face = *feedback.refine_feedback_leaf_again;
    Require(feedback.certify_boundary_refinement &&
                std::count_if(feedback.recovered.begin(), feedback.recovered.end(),
                              [&](const auto& request) { return request.face == face; }) == 1,
            "Follow-up leaf refinement requires one certified face request");
  }
  return plan;
}

std::string NativeFeedbackSourceBinding(const RealBoundarySource& source,
                                        const OuterAttemptIdentity& attempt) {
  std::ostringstream out;
  out.imbue(std::locale::classic());
  out << std::setprecision(17) << source.source_step << ' ' << attempt.epoch << ' '
      << attempt.global_retry << ' ' << source.domain_generation << '\n'
      << source.tree_counter << ' ' << source.tree_factor << ' ' << source.tree_cap << ' '
      << source.face_quality << ' ' << source.low_quality_h << ' ' << source.template_quality
      << '\n';
  for (const auto& cell : source.cells) {
    out << cell.source_id << ' ' << cell.level << ' ' << cell.subdivided;
    for (double limit : cell.box)
      out << ' ' << limit;
    for (const auto child : cell.children)
      out << ' ' << child;
    out << '\n';
  }
  out << "leaf_order";
  for (const auto leaf : source.leaf_order)
    out << ' ' << leaf;
  out << '\n';
  return out.str();
}

struct GroupingPlan {
  GroupingBoxes boxes{};
  bool verify_rejection = false;
};

GroupingPlan ReadGroupingPlan(const std::filesystem::path& path) {
  std::ifstream input(path);
  input.imbue(std::locale::classic());
  std::string schema;
  input >> schema;
  Require(bool(input) && schema == "apmesh_adjacent_group_v1", "Invalid grouping plan schema");
  GroupingPlan plan;
  auto& boxes = plan.boxes;
  for (auto& box : boxes) {
    for (auto& coordinate : box)
      input >> coordinate;
    Require(bool(input) &&
                std::all_of(box.begin(), box.end(),
                            [](double value) { return value >= 0 && value <= 1; }) &&
                box[0] < box[2] && box[1] < box[3],
            "Invalid grouping plan box");
  }
  const auto& [ax, ay, a_right, a_top] = boxes[0];
  const auto& [bx, by, b_right, b_top] = boxes[1];
  const bool horizontal = (ax == b_right || bx == a_right) && ay == by && a_top == b_top;
  const bool vertical = (ay == b_top || by == a_top) && ax == bx && a_right == b_right;
  Require(horizontal || vertical, "Grouping boxes must share a complete side");
  Require(boxes[0][2] - boxes[0][0] == boxes[1][2] - boxes[1][0] &&
              boxes[0][3] - boxes[0][1] == boxes[1][3] - boxes[1][1],
          "Grouping boxes must have the same size");
  std::string extra;
  if (input >> extra) {
    Require(extra == "verify_native_rejection", "Unknown grouping control");
    plan.verify_rejection = true;
  }
  Require(!(input >> extra) && input.eof(), "Unexpected trailing grouping plan data");
  return plan;
}

struct CertifiedSplitWitness {
  std::size_t interval;
  unsigned long start_id, end_id, inserted_id;
  unsigned side;
  double parameter;
};

CertifiedSplitWitness ReadCertifiedSplit(const RealBoundarySource& parent,
                                         const RealBoundarySource& refined,
                                         const CertifiedBoundarySplit& split) {
  const auto& start = parent.sites[split.parent_interval];
  const auto& end = parent.sites[(split.parent_interval + 1) % parent.sites.size()];
  const auto& added = refined.sites[split.inserted_site];
  return {split.parent_interval, start.source_id, end.source_id,
          added.source_id,       added.side,      added.parameter};
}

void WriteCertifiedSplit(std::ostream& out, const CertifiedSplitWitness& split) {
  out << "{\"parent_interval\":" << split.interval << ",\"start_id\":" << split.start_id
      << ",\"end_id\":" << split.end_id << ",\"inserted_id\":" << split.inserted_id
      << ",\"side\":" << split.side << ",\"parameter\":" << std::setprecision(17) << split.parameter
      << '}';
}

std::pair<RealBoundarySource, CertifiedSplitWitness>
SubdivideCertifiedChild(PatchBezier& patch, const RealBoundarySource& first_pass,
                        const RealBoundarySource& current, std::size_t first_child,
                        unsigned long last_id) {
  const auto start = first_pass.sites.at(first_child).source_id;
  const auto end = first_pass.sites.at((first_child + 1) % first_pass.sites.size()).source_id;
  const auto site = std::find_if(current.sites.begin(), current.sites.end(),
                                 [&](const auto& row) { return row.source_id == start; });
  Require(site != current.sites.end(), "Certified child start site was lost");
  const auto interval = static_cast<std::size_t>(site - current.sites.begin());
  Require(current.sites[(interval + 1) % current.sites.size()].source_id == end,
          "Certified child endpoints are no longer adjacent");
  std::vector<bool> flags(current.sites.size(), false);
  flags[interval] = true;
  auto refined = SplitFeedbackIntervals(patch, current, flags, last_id);
  const auto proof = CertifyBoundaryRefinement(patch, current, refined, flags, last_id);
  Require(proof.size() == 1 && proof.front().parent_interval == interval,
          "Incorrect child subdivision certificate");
  const auto witness = ReadCertifiedSplit(current, refined, proof.front());
  return {std::move(refined), witness};
}

bool ContainsRequestSite(const Candidate& candidate, const std::vector<VertexId>& face,
                         UvVertex site) {
  // Use the closed convex UV face. The reporting tolerance includes both
  // incident faces when a request is on their common edge.
  for (std::size_t i = 0; i < face.size(); ++i) {
    const auto a = candidate.uv[face[i]];
    const auto b = candidate.uv[face[(i + 1) % face.size()]];
    if ((b.u - a.u) * (site.v - a.v) - (b.v - a.v) * (site.u - a.u) < -2e-13)
      return false;
  }
  return true;
}

double MedianPhysicalEdge(const SubMesh& mesh, const std::vector<VertexId>& face) {
  std::array<double, 4> edges{};
  for (std::size_t i = 0; i < face.size(); ++i) {
    const auto* a = mesh.GetNoh(static_cast<unsigned>(face[i]));
    const auto* b = mesh.GetNoh(static_cast<unsigned>(face[(i + 1) % face.size()]));
    edges[i] = Norm(Difference(Values(*a), Values(*b)));
    Require(std::isfinite(edges[i]) && edges[i] > 0, "Invalid physical sizing edge");
  }
  std::sort(edges.begin(), edges.begin() + face.size());
  return face.size() == 3 ? edges[1] : (edges[1] + edges[2]) / 2;
}

bool CheckProtectedPhysicalSizes(const Candidate& candidate,
                                 const std::vector<GeometricRequest>& requests,
                                 const std::filesystem::path& directory) {
  std::ofstream evidence(directory / "protected_size_measurements.json", std::ios::binary);
  evidence.imbue(std::locale::classic());
  evidence << std::setprecision(17)
           << "{\"schema\":\"apmesh.quad.protected_size_measurements.v1\",\"requests\":[";
  bool passed = true;
  for (std::size_t r = 0; r < requests.size(); ++r) {
    const auto& request = requests[r];
    if (r)
      evidence << ',';
    evidence << "{\"face\":" << request.face << ",\"uv\":[" << request.site.u << ','
             << request.site.v << "],\"requested_size\":" << request.size << ",\"incident\":[";
    bool measured = false;
    for (std::size_t i = 0; i < candidate.faces.size(); ++i) {
      const auto& face = candidate.faces[i];
      if (!ContainsRequestSite(candidate, face, request.site))
        continue;
      const double h = MedianPhysicalEdge(*candidate.mesh, face);
      if (measured)
        evidence << ',';
      evidence << "{\"face\":" << i << ",\"median_edge\":" << h << '}';
      measured = true;
      passed &= h <= request.size;
    }
    passed &= measured;
    evidence << "]}";
  }
  evidence << "],\"passed\":" << (passed ? "true" : "false") << "}\n";
  evidence.close();
  Require(bool(evidence), "Cannot retain protected size measurements");
  return passed;
}

void StageGeometricFeedback(PatchBezier& patch, const Candidate& previous,
                            const RealBoundarySource& source,
                            const std::vector<GeometricRequest>& requests,
                            const std::filesystem::path& directory,
                            const std::filesystem::path& previous_path,
                            const FeedbackPlan* comparison = nullptr) {
  struct RestorePatchLink {
    PatchBezier& patch;
    SubMesh* original;
    ~RestorePatchLink() { patch.SetSubMesh(original); }
  } restore{patch, patch.GetSubMesh()};
  previous.mesh->SetPatch(&patch);
  patch.SetSubMesh(previous.mesh.get());
  CheckTypedIncidence(*previous.mesh, previous);
  const auto witness = SnapshotOwnerRehearsal(*previous.mesh);
  const auto bytes = ReadRehearsalOutput(previous_path);
  std::optional<RealBoundarySource> split_source;
  const bool certify_boundary = comparison && comparison->certify_boundary_refinement;
  std::vector<bool> split;
  if (certify_boundary || (comparison && !comparison->curve_intervals.empty()))
    split.resize(source.sites.size(), false);
  if (comparison && !comparison->curve_intervals.empty()) {
    for (const auto i : comparison->curve_intervals) {
      Require(i < split.size() && !split[i], "Invalid or repeated feedback curve interval");
      split[i] = true;
    }
    const auto last_id = *std::max_element(previous.node_ids.begin(), previous.node_ids.end());
    split_source = SplitFeedbackIntervals(patch, source, split, last_id);
  }
  const auto& intermediate = split_source ? *split_source : source;
  std::vector<CertifiedBoundarySplit> certificate;
  std::optional<RealBoundarySource> child_source;
  std::vector<CertifiedSplitWitness> child_certificate;
  if (certify_boundary) {
    const auto last_id = *std::max_element(previous.node_ids.begin(), previous.node_ids.end());
    certificate = CertifyBoundaryRefinement(patch, source, intermediate, split, last_id);
    auto contour_last_id = last_id;
    for (const auto& site : intermediate.sites)
      contour_last_id = std::max(contour_last_id, site.source_id);
    for (const auto request : comparison->child_curves) {
      const auto parent = std::find_if(certificate.begin(), certificate.end(), [&](const auto& s) {
        return s.parent_interval == request.interval;
      });
      Require(parent != certificate.end(), "Missing certified root interval for the child split");
      const auto child = parent->inserted_site - 1 + static_cast<std::size_t>(request.child);
      const auto& current = child_source ? *child_source : intermediate;
      auto [refined, proof] =
          SubdivideCertifiedChild(patch, intermediate, current, child, contour_last_id);
      contour_last_id = proof.inserted_id;
      child_source = std::move(refined);
      child_certificate.push_back(proof);
    }
  }
  const auto& effective_source = child_source ? *child_source : intermediate;
  auto tree = ReplayRealSourceTree(patch, effective_source);
  const auto leaves = tree->getLeaves();
  const auto cap = tree->getMaxLevelCap();
  std::set<long> requested;
  const GeometricRequest* follow_up = nullptr;
  int follow_up_initial_level = -1;
  const auto containing_leaf = [](const auto& leaves, UvVertex site) {
    QuadtreeCell* chosen = nullptr;
    for (auto* leaf : leaves) {
      if (site.u >= leaf->getMin()->getX() && site.u <= leaf->getMax()->getX() &&
          site.v >= leaf->getMin()->getY() && site.v <= leaf->getMax()->getY() &&
          (!chosen || leaf->getLevel() > chosen->getLevel()))
        chosen = leaf;
    }
    return chosen;
  };
  Require(std::filesystem::create_directory(directory),
          "Cannot reserve geometric feedback evidence");
  if (certify_boundary) {
    std::ofstream evidence(directory / "boundary_refinement.json", std::ios::binary);
    evidence.imbue(std::locale::classic());
    const char* version = child_certificate.empty()       ? "v1"
                          : child_certificate.size() == 1 ? "v2"
                                                          : "v3";
    evidence << "{\"schema\":\"apmesh.quad.boundary_refinement." << version
             << "\",\"parent_sites\":" << source.sites.size()
             << ",\"candidate_sites\":" << effective_source.sites.size() << ",\"splits\":[";
    for (std::size_t i = 0; i < certificate.size(); ++i) {
      if (i)
        evidence << ',';
      WriteCertifiedSplit(evidence, ReadCertifiedSplit(source, intermediate, certificate[i]));
    }
    evidence << ']';
    const auto write_request = [&](std::size_t i) {
      const auto request = comparison->child_curves[i];
      evidence << "{\"interval\":" << request.interval << ",\"child\":" << request.child << '}';
    };
    if (!child_certificate.empty())
      evidence << ",\"intermediate_sites\":" << intermediate.sites.size();
    if (child_certificate.size() == 1) {
      evidence << ",\"child_request\":";
      write_request(0);
      evidence << ",\"child_split\":";
      WriteCertifiedSplit(evidence, child_certificate.front());
    } else if (!child_certificate.empty()) {
      evidence << ",\"child_splits\":[";
      for (std::size_t i = 0; i < child_certificate.size(); ++i) {
        if (i)
          evidence << ',';
        evidence << "{\"request\":";
        write_request(i);
        evidence << ",\"split\":";
        WriteCertifiedSplit(evidence, child_certificate[i]);
        evidence << '}';
      }
      evidence << ']';
    }
    evidence << "}\n";
    evidence.close();
    Require(bool(evidence), "Cannot retain the boundary refinement certificate");
  }
  std::ofstream trace(directory / "requests.csv", std::ios::binary);
  trace.imbue(std::locale::classic());
  trace << "face,u,v,requested_size,leaf_id,leaf_level,cap,disposition\n" << std::setprecision(17);
  for (const auto& request : requests) {
    Require(request.face < previous.faces.size(),
            "Geometric feedback face is outside the predecessor");
    auto* chosen = containing_leaf(leaves, request.site);
    Require(chosen != nullptr, "Geometric feedback site is outside the native tree");
    const auto level = chosen->getLevel();
    const bool capped = cap >= 0 && level >= cap;
    if (!capped)
      requested.insert(chosen->getId());
    if (comparison && comparison->refine_feedback_leaf_again == request.face) {
      Require(cap >= 0 && level < cap, "Follow-up leaf requires an initial split below the cap");
      follow_up = &request;
      follow_up_initial_level = level;
    }
    trace << request.face << ',' << request.site.u << ',' << request.site.v << ',' << request.size
          << ',' << chosen->getId() << ',' << level << ',' << cap << ','
          << (capped ? "capped" : "actionable") << '\n';
  }
  trace.close();
  Require(bool(trace), "Cannot retain geometric request evidence");

  const auto before = tree->GetLeafCount();
  for (auto* leaf : leaves)
    if (requested.count(leaf->getId()))
      leaf->subdivideToLevel(leaf->getLevel() + 1);
  Require(tree->GetLeafCount() == before + 3 * requested.size(),
          "Native tree did not apply every distinct actionable request");
  if (!requested.empty())
    Require(tree->refineAccordingToNeighbors() ==
                Par2DJMesh::AFT::QUAD_REFINE_ACCORDING_TO_NEIGHBORS_DONE,
            "Geometric feedback could not balance the native tree");
  if (follow_up) {
    auto* leaf = containing_leaf(tree->getLeaves(), follow_up->site);
    Require(leaf && leaf->getLevel() == follow_up_initial_level + 1 && leaf->getLevel() < cap,
            "Follow-up leaf has no available level after the initial split");
    const auto id = leaf->getId();
    const auto level = leaf->getLevel();
    const auto before_follow_up = tree->GetLeafCount();
    leaf->subdivideToLevel(level + 1);
    Require(tree->GetLeafCount() == before_follow_up + 3,
            "Native tree did not split the follow-up leaf once");
    Require(tree->refineAccordingToNeighbors() ==
                Par2DJMesh::AFT::QUAD_REFINE_ACCORDING_TO_NEIGHBORS_DONE,
            "Native tree could not balance the follow-up leaf split");
    std::ofstream proof(directory / "follow_up_leaf.csv", std::ios::binary);
    proof.imbue(std::locale::classic());
    proof << "face,leaf_id,level_before,level_after,leaves_before,leaves_after_balance\n"
          << follow_up->face << ',' << id << ',' << level << ',' << level + 1 << ','
          << before_follow_up << ',' << tree->GetLeafCount() << '\n';
    proof.close();
    Require(bool(proof), "Cannot retain follow-up leaf evidence");
  }
  const auto refined = tree->GetLeafCount();
  const bool group_parent = comparison && !comparison->group_feedback_parents.empty();
  std::vector<GeometricRequest> protected_sizes;
  if (group_parent) {
    const auto& parents = comparison->group_feedback_parents;
    auto captured = effective_source;
    CaptureRealSourceTree(*tree, captured);
    const auto contains = [](const std::array<double, 4>& box, UvVertex site) {
      return box[0] <= site.u && site.u <= box[2] && box[1] <= site.v && site.v <= box[3];
    };
    for (const auto& parent_box : parents) {
      const bool measured = comparison->measured_contour_parent == parent_box;
      for (const auto& request : requests) {
        const bool in_parent = contains(parent_box, request.site);
        Require(measured || !in_parent, "Grouping would remove a refinement request");
        const bool in_neighbor =
            std::any_of(captured.cells.begin(), captured.cells.end(), [&](const auto& cell) {
              return !cell.subdivided && ShareTreeSide(cell.box, parent_box) &&
                     contains(cell.box, request.site);
            });
        Require(measured || !in_neighbor,
                "Grouping would alter a neighbor with a refinement request");
        if (measured && (in_parent || in_neighbor))
          protected_sizes.push_back(request);
      }
    }
    Require(!comparison->measured_contour_parent || !protected_sizes.empty(),
            "Measured contour parent affects no protected size request");
    const auto grouped = GroupTemplateBlocks(captured, parents);
    CheckGroupedBalance(grouped);
    tree = ReplayRealSourceTree(patch, grouped);
    const bool single = parents.size() == 1;
    std::ofstream evidence(directory / (single ? "grouped_parent.json" : "grouped_parents.json"),
                           std::ios::binary);
    evidence.imbue(std::locale::classic());
    evidence << std::setprecision(17) << (single ? "{\"parent\":" : "{\"parents\":[");
    for (std::size_t i = 0; i < parents.size(); ++i) {
      const auto& box = parents[i];
      if (i)
        evidence << ',';
      evidence << '[' << box[0] << ',' << box[1] << ',' << box[2] << ',' << box[3] << ']';
    }
    if (!single)
      evidence << ']';
    evidence << ",\"leaves_after_requests\":" << refined
             << ",\"leaves_after_grouping\":" << tree->GetLeafCount() << "}\n";
    evidence.close();
    Require(bool(evidence), "Cannot retain the native feedback grouping evidence");
  }
  const auto after = tree->GetLeafCount();
  std::ofstream realized(directory / "leaves.csv", std::ios::binary);
  realized.imbue(std::locale::classic());
  realized << "id,level,u0,v0,u1,v1\n" << std::setprecision(17);
  for (auto* leaf : tree->getLeaves()) {
    Require(cap < 0 || leaf->getLevel() <= cap, "Geometric feedback exceeded the original cap");
    realized << leaf->getId() << ',' << leaf->getLevel() << ',' << leaf->getMin()->getX() << ','
             << leaf->getMin()->getY() << ',' << leaf->getMax()->getX() << ','
             << leaf->getMax()->getY() << '\n';
  }
  realized.close();
  Require(bool(realized), "Cannot retain realized feedback leaves");

  std::optional<Candidate> staged;
  std::string outcome = "no_action";
  std::string rejection;
  const auto guarded_path = directory / "smoothing_comparison";
  const bool guarded = comparison && comparison->guarded_smoothing;
  if (guarded)
    Require(std::filesystem::create_directory(guarded_path), "Cannot reserve smoothing comparison");
  if (after > before || split_source || group_parent) {
    try {
      staged = Generate(
          patch, false, [&]() { return std::move(tree); }, &effective_source, false, true, true,
          comparison && comparison->replay_previous_search ? &previous : nullptr,
          guarded ? &guarded_path : nullptr, comparison && comparison->additional_pairs,
          comparison ? comparison->additional_pair_error_limit : std::nullopt,
          comparison ? comparison->ideal_front_limits : std::nullopt);
    } catch (const std::runtime_error& error) {
      rejection = error.what();
    } catch (const std::invalid_argument& error) {
      rejection = error.what();
    }
    outcome = staged ? "staged" : "rejected";
  }
  if (staged) {
    CheckTypedIncidence(*staged->mesh, *staged);
    if (!protected_sizes.empty() &&
        !CheckProtectedPhysicalSizes(*staged, protected_sizes, directory)) {
      staged.reset();
      outcome = "rejected";
      rejection = "Grouped candidate exceeds one or more protected physical size requests";
    }
  }
  if (staged) {
    staged->source_witness = &effective_source;
    staged->generation_step = source.source_step;
    staged->reference_accepted = source.reference_tri_accepted;
    staged->stage_reason = "geometric_feedback_staged";
    Export(*staged, directory / "candidate.obj");
    ExportArticleSteps(*staged, directory / "candidate_front");
    staged.reset();
  }
  RequireOwnerRehearsalUnchanged(patch, witness);
  Require(ReadRehearsalOutput(previous_path) == bytes,
          "Geometric feedback changed its predecessor OBJ");

  std::ofstream result(directory / "result.txt", std::ios::binary);
  result.imbue(std::locale::classic());
  result << outcome << '\n'
         << cap << ' ' << before << ' ' << after << ' ' << requested.size() << '\n'
         << rejection << '\n'
         << source.sites.size() << ' ' << effective_source.sites.size() << '\n';
  result.close();
  Require(bool(result), "Cannot retain geometric feedback outcome");
}

Candidate StageGroupingCandidate(PatchBezier& patch, Candidate previous,
                                 const RealBoundarySource source, const GroupingPlan& plan,
                                 const std::filesystem::path& directory,
                                 const std::filesystem::path& previous_path,
                                 const FeedbackPlan* feedback) {
  struct RestorePatchLink {
    PatchBezier& patch;
    SubMesh* original;
    ~RestorePatchLink() { patch.SetSubMesh(original); }
  } restore{patch, patch.GetSubMesh()};
  previous.mesh->SetPatch(&patch);
  patch.SetSubMesh(previous.mesh.get());
  CheckTypedIncidence(*previous.mesh, previous);
  const auto witness = SnapshotOwnerRehearsal(*previous.mesh);
  const auto bytes = ReadRehearsalOutput(previous_path);
  Require(source.source_step == 3 && source.reference_tri_accepted && source.source_leaves >= 8 &&
              std::is_sorted(source.leaf_order.begin(), source.leaf_order.end()),
          "Two-block trial requires its retained Step 3 native tree");
  const auto grouped = GroupTemplateBlocks(source, plan.boxes);
  CheckGroupedBalance(grouped);
  const auto verify_previous = [&]() {
    RequireOwnerRehearsalUnchanged(patch, witness);
    Require(ReadRehearsalOutput(previous_path) == bytes, "Grouping changed the previous OBJ");
  };
  const auto attempt = [&](bool reject) {
    auto candidate = Generate(
        patch, false, [&]() { return ReplayRealSourceTree(patch, grouped); }, &source, false, true,
        true);
    CheckTypedIncidence(*candidate.mesh, candidate);
    if (reject) {
      candidate.mesh->SetPatch(&patch);
      RestorePatchLink undo{patch, patch.GetSubMesh()};
      patch.SetSubMesh(candidate.mesh.get());
      Require(patch.GetSubMesh() == candidate.mesh.get(),
              "Grouping rejection did not exercise the temporary candidate link");
      throw PublicationFailure("Injected grouping rejection after temporary candidate link");
    }
    candidate.source_witness = &source;
    candidate.generation_step = source.source_step;
    candidate.reference_accepted = source.reference_tri_accepted;
    candidate.stage_reason = "staged_adjacent_group";
    Require(std::filesystem::create_directory(directory), "Cannot reserve staged grouping output");
    Export(candidate, directory / "candidate.obj");
    ExportArticleSteps(candidate, directory / "candidate_front");
    if (feedback)
      StageGeometricFeedback(patch, candidate, grouped, feedback->recovered,
                             directory.parent_path() / "feedback_recovered",
                             directory / "candidate.obj", feedback);
  };
  if (plan.verify_rejection) {
    bool rejected = false;
    try {
      attempt(true);
    } catch (const PublicationFailure&) {
      rejected = true;
    }
    Require(rejected && !std::filesystem::exists(directory),
            "Grouping rejection did not leave the candidate unpublished");
    verify_previous();
    std::cout << "QUAD_GROUPING_REJECTION previous_owner_preserved=1 previous_obj_preserved=1 "
                 "candidate_unpublished=1\n";
  }
  attempt(false);
  verify_previous();
  std::cout << "QUAD_ADJACENT_GROUP staged=1 previous_owner_preserved=1 mixed_adaptive_epochs=0\n";
  return previous;
}

} // namespace

int RunRealBoundaryPatch(const application::RuntimeConfig& config) {
  std::optional<GroupingPlan> grouping_plan;
  if (const char* plan_path = std::getenv("APMESH_QUAD_GROUPING_PLAN")) {
    Require(*plan_path != '\0' &&
                config.quad_experimental_case == "curved_bezier_article_front_area_centroid_v1" &&
                config.input_model == "builtin:curva_bezier" && !config.quad_verify_rollback,
            "A grouping plan requires the CurvaBezier area-centroid trial");
    grouping_plan = ReadGroupingPlan(plan_path);
  }
  std::optional<FeedbackPlan> feedback;
  std::optional<NativeFeedbackPlan> native_feedback;
  if (const char* path = std::getenv("APMESH_QUAD_FEEDBACK_PLAN")) {
    Require(*path != '\0', "Geometric feedback plan path is empty");
    if (grouping_plan) {
      Require(!grouping_plan->verify_rejection,
              "Geometric feedback requires the recovered grouping comparison");
      feedback = ReadFeedbackPlan(path);
    } else {
      Require(!config.quad_verify_rollback &&
                  config.quad_experimental_case == "curved_bezier_article_front_area_centroid_v1",
              "Single-patch feedback requires the standalone area-centroid experiment");
      native_feedback = ReadNativeFeedbackPlan(path);
    }
  }
  bool grouped_candidate_staged = false;
  const auto output = std::filesystem::path(config.output_prefix + ".obj");
  const auto steps = std::filesystem::path(config.output_prefix + ".steps");
  const auto staging = std::filesystem::path(config.output_prefix + ".steps.pending");
  Require(!std::filesystem::exists(output) &&
              !std::filesystem::exists(output.string() + ".pending") &&
              !std::filesystem::exists(steps) && !std::filesystem::exists(staging),
          "Real-boundary output or pending publication already exists");
  Require(output.parent_path().empty() || std::filesystem::is_directory(output.parent_path()),
          "Real-boundary output parent directory does not exist");
  Geometry geometry;
  Models3d models;
  if (config.input_model == "builtin:curva_bezier")
    models.ModelCurvaBezier(&geometry);
  else {
    PatchReader reader;
    reader.ReaderFilePatches(&geometry, config.input_model);
  }
  Require(geometry.GetNumberPatches() == 1, "Real-boundary QUAD requires one source patch");
  auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  Require(patch != nullptr, "Real-boundary QUAD requires a Bezier source");

  // Preserve original curvature, retries and acceptance. The bounded-domain case
  // explicitly repairs the step2 factor override; other cases retain it unchanged.
  Model model(&geometry);
  GeneratorAdaptive generator(application::MakeGenerationContext(config, NUMBER_PROCESS));
  const bool live_pairs =
      config.quad_experimental_case == "curved_bezier_live_pairs_vertex_mean_v1";
  const bool article_area_centroid =
      config.quad_experimental_case == "curved_bezier_article_front_area_centroid_v1";
  const bool article_front =
      config.quad_experimental_case == "curved_bezier_article_front_vertex_mean_v1" ||
      article_area_centroid;
  if (config.quad_experimental_case == "curved_bezier_bounded_domain_vertex_mean_v1" ||
      live_pairs || article_front)
    generator.EnforceResearchDomainFactorBounds();
  Timer timer(config.num_processes, config.num_threads, 12);
  timer.InitTimerParallel(0, 0, 10);
  struct Capture {
    RealBoundarySource source;
    PatchAttemptIdentity attempt;
    bool locally_selected = false;
    bool domain_selected = false;
  };
  std::vector<Capture> captures;
  struct Stage {
    int step;
    OuterAttemptIdentity outer;
    bool accepted;
    std::string reason;
    Candidate reference;
  };
  std::vector<Stage> stages;
  std::ostringstream curve_trace;
  curve_trace.imbue(std::locale::classic());
  curve_trace << std::setprecision(17)
              << "step,epoch,retry,curve,stage,parameter_count,parameters\n";
  std::optional<RealBoundarySource> pending;
  unsigned active_domain_generation = 0;
  CaptureHooks hooks;
  hooks.domain_begin_sink = [&](int, OuterAttemptIdentity, unsigned side, unsigned generation) {
    Require(side == 0, "Domain generation belongs to a foreign patch");
    active_domain_generation = generation;
  };
  hooks.domain_selection_sink = [&](int step, OuterAttemptIdentity outer, unsigned side,
                                    unsigned generation) {
    Require(side == 0, "Selected domain belongs to a foreign patch");
    for (auto& capture : captures)
      if (capture.source.source_step == step && SameOuterAttempt(capture.attempt.outer, outer))
        capture.domain_selected = capture.source.domain_generation == generation;
  };
  hooks.curve_stage_sink = [&](int step, OuterAttemptIdentity outer, unsigned side,
                               const char* stage, CurveAdaptive& curve) {
    const auto& parameters = static_cast<CurveAdaptiveParametric&>(curve).parameters_;
    curve_trace << step << ',' << outer.epoch << ',' << outer.global_retry << ',' << side << ','
                << stage << ',' << parameters.size() << ',';
    bool first = true;
    for (double parameter : parameters) {
      if (!first)
        curve_trace << '|';
      curve_trace << parameter;
      first = false;
    }
    curve_trace << '\n';
  };
  hooks.mesh_stage_sink = [&](int step, OuterAttemptIdentity outer, bool accepted,
                              const MeshAdaptive& mesh, const std::string& reason) {
    Require(mesh.GetNumberSubMeshesAdaptive() == 1, "Stage lost its single source patch");
    const auto* source = mesh.GetSubMeshAdaptiveByPosition(0);
    Require(source != nullptr, "Stage lost its physical TRI owner");
    stages.push_back({step, outer, accepted, reason, SnapshotTriStage(*source, *patch)});
  };
  hooks.provider = [&](Quadtree& tree) {
    Require(!pending, "Original source capture was not consumed");
    pending = CaptureRealBoundary(*patch, tree);
    LeafPolygonMesh value;
    value.source_leaves = pending->source_leaves;
    return value;
  };
  hooks.sink = [&](AttemptUvCapture value) {
    Require(pending.has_value() && value.attempt.patch_index == 0,
            "Original source capture lost its patch identity");
    pending->source_step = value.attempt.adaptive_step;
    pending->domain_generation = active_domain_generation;
    captures.push_back({std::move(*pending), value.attempt, false, false});
    pending.reset();
  };
  hooks.local_selection_sink = [&](LocalSelectionEvent event) {
    for (auto& capture : captures)
      if (capture.source.domain_generation == active_domain_generation &&
          SamePatchScope(capture.attempt, event.attempt) &&
          capture.attempt.local_attempt == event.attempt.local_attempt)
        capture.locally_selected = event.kind == LocalSelectionKind::SelectedForAdapterReturn;
  };
  generator.SetResearchUvCapture(std::move(hooks), 15112026);
  generator.Generator(model, &timer);
  const auto* outcomes = generator.GetResearchGlobalOutcomeLog();
  Require(outcomes && !outcomes->truncated(), "Original generator outcome stream is incomplete");
  const RealBoundarySource* selected = nullptr;
  for (std::size_t i = 0; i < outcomes->size(); ++i) {
    const auto& event = outcomes->data()[i];
    if (event.kind != GlobalOutcomeKind::AcceptedStepCommitted &&
        event.kind != GlobalOutcomeKind::RejectedStepRestored)
      continue;
    for (auto& capture : captures)
      if (capture.locally_selected && capture.domain_selected &&
          SameOuterAttempt(capture.attempt.outer, event.outer) &&
          capture.attempt.adaptive_step == event.adaptive_step) {
        capture.source.reference_tri_accepted =
            event.kind == GlobalOutcomeKind::AcceptedStepCommitted;
        if (capture.source.reference_tri_accepted)
          selected = &capture.source;
      }
  }
  Require(selected != nullptr,
          "Original workflow produced no accepted source-attempt outcome; no rejected fallback");
  // Preserve a uniform partition when that is the original algorithm's result.
  std::cout << "QUAD_ORIGINAL_SOURCE step=" << selected->source_step
            << " boundary=" << selected->sites.size() << " leaves=" << selected->source_leaves
            << " nonuniform_sides=" << selected->nonuniform_sides << '\n';
  Require(patch->GetSubMesh() && patch->GetSubMesh()->GetNumberElements() > 0,
          "Original source workflow retained no nonempty patch owner");
  const auto previous = SnapshotOwnerRehearsal(*patch->GetSubMesh());
  Require(std::filesystem::create_directory(staging), "Cannot reserve generation archive");
  if (native_feedback) {
    const Capture* captured = nullptr;
    Stage* tri = nullptr;
    for (auto& stage : stages) {
      if (stage.step != native_feedback->step || !stage.accepted)
        continue;
      for (const auto& capture : captures) {
        if (capture.locally_selected && capture.domain_selected &&
            capture.source.reference_tri_accepted && capture.source.source_step == stage.step &&
            SameOuterAttempt(capture.attempt.outer, stage.outer)) {
          Require(captured == nullptr, "Single-patch feedback source is ambiguous");
          captured = &capture;
          tri = &stage;
        }
      }
    }
    Require(captured != nullptr, "No accepted original TRI attempt matches the requested step");
    const auto& source = captured->source;
    const auto comparison = staging / "source_smoothing";
    Require(std::filesystem::create_directory(comparison),
            "Cannot reserve predecessor smoothing archive");
    auto predecessor = Generate(
        *patch, false, [&]() { return ReplayRealSourceTree(*patch, source); }, &source, false, true,
        true, nullptr, &comparison);
    CheckTypedIncidence(*predecessor.mesh, predecessor);
    const auto set_lineage = [&](Candidate& mesh, const char* reason) {
      mesh.source_witness = &source;
      mesh.generation_step = tri->step;
      mesh.reference_accepted = tri->accepted;
      mesh.stage_reason = reason;
    };
    set_lineage(tri->reference, "single_patch_feedback_tri_control");
    set_lineage(predecessor, "single_patch_feedback_source");
    Export(tri->reference, staging / "tri.obj");
    const auto mesh_path = staging / "source.obj";
    Export(predecessor, mesh_path);
    const auto binding_path = staging / "source_tree.txt";
    {
      std::ofstream out(binding_path, std::ios::binary);
      out << NativeFeedbackSourceBinding(source, tri->outer);
      out.close();
      Require(bool(out), "Cannot complete single-patch source binding");
    }
    if (native_feedback->reference) {
      for (const auto* file : {"tri.obj", "source.obj", "source_tree.txt"})
        Require(ReadRehearsalOutput(staging / file) ==
                    ReadRehearsalOutput(*native_feedback->reference / file),
                "Single-patch feedback did not reproduce its original source binding");
      const auto& requests = native_feedback->feedback;
      StageGeometricFeedback(*patch, predecessor, source, requests.recovered, staging / "feedback",
                             mesh_path, &requests);
    }
    RequireOwnerRehearsalUnchanged(*patch, previous);
    std::filesystem::rename(staging, steps);
    return 0;
  }
  std::ofstream manifest(staging / "manifest.csv", std::ios::binary);
  std::ofstream pair_trace(staging / "boundary_pair_candidates.csv", std::ios::binary);
  std::ofstream pair_stages(staging / "boundary_pair_stages.csv", std::ios::binary);
  std::ofstream live_trace, live_stages;
  if (live_pairs) {
    live_trace.open(staging / "live_pair_candidates.csv", std::ios::binary);
    live_stages.open(staging / "live_pair_stages.csv", std::ios::binary);
    Require(bool(live_trace) && bool(live_stages), "Cannot create live pair history");
    live_trace << "step,epoch,retry,domain_generation,reference_tri_accepted,first_source_face,"
                  "second_source_face,front_order,quad_a,quad_b,quad_c,quad_d,status,S_xyz,edge_"
                  "ratio,final_face\n";
    live_stages << "step,epoch,retry,domain_generation,reference_tri_accepted,seed_quads,"
                   "aft_source_triangles,selected_pairs,retained_triangles,scope\n";
    live_trace << std::setprecision(17);
  }
  Require(bool(pair_trace) && bool(pair_stages), "Cannot create boundary pair inventory");
  pair_trace << "step,epoch,retry,domain_generation,reference_tri_accepted,first_face,second_face,"
                "shared_a,shared_b,quad_a,quad_b,quad_c,quad_d,selection_status\n";
  pair_stages << "step,epoch,retry,domain_generation,reference_tri_accepted,seed_quad_faces,"
                 "observed_aft_triangles,topology_candidates,selected_pairs,scope\n";
  manifest << "step,epoch,retry,domain_generation,reference_tri_accepted,reason,tri_obj,quad_tri_"
              "obj,nodes,quads,"
              "triangles,boundary\n";
  Candidate candidate;
  bool have_accepted = false;
  for (auto& stage : stages) {
    const RealBoundarySource* source = nullptr;
    for (const auto& capture : captures)
      if (capture.locally_selected && capture.domain_selected &&
          capture.source.source_step == stage.step &&
          SameOuterAttempt(capture.attempt.outer, stage.outer)) {
        Require(source == nullptr, "Stage matched multiple locally selected sources");
        source = &capture.source;
      }
    Require(stage.step == 0 || source != nullptr,
            "Physical step has no matching curve/tree source");
    const auto stem = "step_" + std::to_string(stage.step) + "_retry_" +
                      std::to_string(stage.outer.global_retry) +
                      (stage.accepted ? "_accepted" : "_rejected");
    stage.reference.source_witness = source;
    stage.reference.generation_step = stage.step;
    stage.reference.reference_accepted = stage.accepted;
    stage.reference.stage_reason = stage.reason;
    Export(stage.reference, staging / (stem + "_tri.obj"));
    auto layout = SnapshotTriStage(*stage.reference.mesh, *patch);
    if (source) {
      auto tree = ReplayRealSourceTree(*patch, *source);
      bool has_interior = false;
      for (auto* leaf : tree->getLeaves())
        has_interior = has_interior || !leaf->inBoundary();
      if (has_interior)
        layout = Generate(
            *patch, false, [&]() { return ReplayRealSourceTree(*patch, *source); }, source,
            live_pairs, article_front, article_area_centroid);
    }
    layout.source_witness = source;
    layout.generation_step = stage.step;
    layout.reference_accepted = stage.accepted;
    layout.stage_reason = stage.reason;
    Export(layout, staging / (stem + "_quad_tri.obj"));
    if (article_front && !layout.article_commits.empty())
      ExportArticleSteps(layout, staging / (stem + "_article_front"));
    if (grouping_plan && source && stage.step == 3 && stage.accepted &&
        stage.outer.global_retry == 0) {
      const auto previous_obj = staging / (stem + "_quad_tri.obj");
      if (feedback && !feedback->replay_previous_search && feedback->curve_intervals.empty())
        StageGeometricFeedback(*patch, layout, *source, feedback->predecessor,
                               staging / "feedback_predecessor", previous_obj);
      layout = StageGroupingCandidate(*patch, std::move(layout), *source, *grouping_plan,
                                      staging / "adjacent_trial", previous_obj,
                                      feedback ? &*feedback : nullptr);
      grouped_candidate_staged = true;
    }
    if (live_pairs)
      Export(layout, staging / (stem + "_aft_source.obj"), true);
    // Completed-output diagnostics only. No candidate replaces any mesh element.
    std::vector<std::array<std::size_t, 3>> exterior;
    if (layout.quads > 0 && !article_front) {
      const auto& scaffold = layout.source_faces.empty() ? layout.faces : layout.source_faces;
      for (std::size_t i = layout.seed_quads; i < scaffold.size(); ++i) {
        const auto& face = scaffold[i];
        Require(face.size() == 3, "Boundary pair inventory received a non-TRI exterior face");
        exterior.push_back({face[0], face[1], face[2]});
      }
    }
    const auto pairs = CollectBoundaryPairCandidates(layout.uv.size(), exterior);
    const auto prefix = std::to_string(stage.step) + ',' + std::to_string(stage.outer.epoch) + ',' +
                        std::to_string(stage.outer.global_retry) + ',' +
                        std::to_string(source ? source->domain_generation : 0) + ',' +
                        std::to_string(stage.accepted) + ',';
    pair_stages << prefix << layout.seed_quads << ',' << exterior.size() << ',' << pairs.size()
                << ",0,"
                << (layout.quads > 0
                        ? (article_front ? "not_applicable_prospective_polygon_commits"
                           : live_pairs  ? "source_scaffold_inventory_live_selection_separate"
                                         : "topology_only_policy_pending")
                        : "not_applicable_without_quad_seed")
                << '\n';
    for (const auto& pair : pairs) {
      pair_trace << prefix << layout.seed_quads + pair.first_triangle + 1 << ','
                 << layout.seed_quads + pair.second_triangle + 1 << ',' << pair.shared_edge[0] + 1
                 << ',' << pair.shared_edge[1] + 1;
      for (auto id : pair.boundary_cycle)
        pair_trace << ',' << id + 1;
      pair_trace << ",not_evaluated\n";
    }
    if (live_pairs) {
      live_stages << prefix << layout.seed_quads << ',' << exterior.size() << ','
                  << layout.aft_pair_origins.size() << ',' << layout.faces.size() - layout.quads
                  << ','
                  << (layout.source_faces.empty() ? "not_applicable_without_quad_seed"
                                                  : "incremental_triangle_commit_pairing")
                  << '\n';
      for (const auto& event : layout.live_pair_events) {
        const auto& pair = event.candidate;
        live_trace << prefix << layout.seed_quads + pair.first_triangle + 1 << ','
                   << layout.seed_quads + pair.second_triangle + 1 << ',' << event.front_order;
        for (auto id : pair.boundary_cycle)
          live_trace << ',' << id + 1;
        live_trace << ',' << event.status << ',';
        if (event.measured)
          live_trace << event.score;
        live_trace << ',';
        if (event.measured)
          live_trace << event.edge_ratio;
        std::size_t final_face = 0;
        if (event.status == "selected")
          for (std::size_t i = 0; i < layout.aft_pair_origins.size(); ++i)
            if (layout.aft_pair_origins[i].first_triangle == pair.first_triangle &&
                layout.aft_pair_origins[i].second_triangle == pair.second_triangle)
              final_face = layout.seed_quads + i + 1;
        live_trace << ',' << final_face << '\n';
      }
    }
    manifest << stage.step << ',' << stage.outer.epoch << ',' << stage.outer.global_retry << ','
             << (source ? source->domain_generation : 0) << ',' << stage.accepted << ','
             << stage.reason << ',' << stem << "_tri.obj," << stem << "_quad_tri.obj,"
             << layout.mesh->GetNumberNos() << ',' << layout.quads << ','
             << layout.faces.size() - layout.quads << ',' << (source ? source->sites.size() : 4)
             << '\n';
    if (source == selected && stage.accepted) {
      candidate = std::move(layout);
      have_accepted = true;
    }
  }
  Require(have_accepted, "Last accepted source has no exported physical step");
  manifest.close();
  Require(bool(manifest), "Cannot complete generation manifest");
  pair_trace.close();
  pair_stages.close();
  Require(bool(pair_trace) && bool(pair_stages), "Cannot complete boundary pair inventory");
  if (live_pairs) {
    live_trace.close();
    live_stages.close();
    Require(bool(live_trace) && bool(live_stages), "Cannot complete live pair history");
  }
  std::ofstream trace(staging / "curve_stages.csv", std::ios::binary);
  trace << curve_trace.str();
  trace.close();
  Require(bool(trace), "Cannot complete curve-stage trace");
  Require(!grouping_plan || grouped_candidate_staged,
          "Grouping trial could not reproduce the admitted Step 3 source");
  std::filesystem::rename(staging, steps);
  RequireOwnerRehearsalUnchanged(*patch, previous);
  CheckTypedIncidence(*candidate.mesh, candidate);
  Export(candidate, config.output_prefix + ".obj");
  candidate.mesh->SetPatch(patch);
  patch->SetSubMesh(candidate.mesh.get());
  std::unique_ptr<SubMesh> accepted;
  accepted.swap(candidate.mesh);
  std::cout << "QUAD_REAL_BOUNDARY source=original_generator_curve_attempt"
            << " reference_tri_accepted=" << selected->reference_tri_accepted
            << " source_step=" << selected->source_step << " boundary=" << selected->sites.size()
            << " native_leaves=" << selected->source_leaves
            << " nonuniform_sides=" << selected->nonuniform_sides
            << " reversed_sides=" << selected->reversed_sides
            << " nodes=" << accepted->GetNumberNos() << " quads=" << candidate.quads
            << " triangles=" << candidate.faces.size() - candidate.quads
            << " original_intervals_preserved=1 native_tree_replayed=1"
            << " published=1 mixed_adaptive_epochs=0\n";
  if (config.quad_verify_rollback) {
    const auto witness = SnapshotOwnerRehearsal(*accepted);
    const auto file = std::filesystem::path(config.output_prefix + ".obj");
    const auto bytes = ReadRehearsalOutput(file);
    bool rejected = false;
    try {
      if (live_pairs || article_front) {
        auto failed = Generate(
            *patch, true, [&]() { return ReplayRealSourceTree(*patch, *selected); }, selected,
            live_pairs, article_front, article_area_centroid);
        (void)failed;
      } else {
        auto failed = CloneTypedHistory(*accepted, candidate, *patch, 0);
        (void)failed;
      }
    } catch (const PublicationFailure&) {
      rejected = true;
    }
    Require(rejected, "Real-boundary publication fault did not fire");
    RequireOwnerRehearsalUnchanged(*patch, witness);
    Require(ReadRehearsalOutput(file) == bytes, "Real-boundary rollback changed published output");
    std::cout << "QUAD_REAL_BOUNDARY_ROLLBACK previous_nonempty=1 preserved=1\n";
    return 1;
  }
  return 0;
}

int RunControlledPatch(const application::RuntimeConfig& config) {
  Geometry geometry;
  Models3d models;
  if (config.input_model == "builtin:curva_bezier")
    models.ModelCurvaBezier(&geometry);
  else {
    PatchReader reader;
    reader.ReaderFilePatches(&geometry, config.input_model);
  }
  Require(geometry.GetNumberPatches() == 1, "Controlled QUAD accepts exactly one source patch");
  auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  Require(patch != nullptr, "Controlled source must be Bezier");
  auto candidate = Generate(*patch, false);
  ProbeTypedHistory(*candidate.mesh, candidate, *patch);
  ProbeMixedCurvature(*candidate.mesh, candidate);
  ProbePhysicalQuadQuality(*candidate.mesh, candidate, *patch);
  const auto mixed_residual = ProbeMixedSurfaceResidual(candidate, *patch);
  ProbeNativeTreeAlternatives(candidate, mixed_residual);
  ProbeConnectedAftBand(candidate, mixed_residual);
  ProbePhysicalConnectedBand(candidate, *patch, mixed_residual, config.output_prefix);
  Export(candidate, config.output_prefix + ".obj");
  candidate.mesh->SetPatch(patch);
  patch->SetSubMesh(candidate.mesh.get());
  std::unique_ptr<SubMesh> accepted;
  accepted.swap(candidate.mesh);
  std::cout << "QUAD_CONTROLLED_PATCH quads=" << candidate.quads
            << " triangles=" << candidate.faces.size() - candidate.quads
            << " nodes=" << accepted->GetNumberNos()
            << " boundary=16 UV_disk=1 overlap=0 min_alignment=" << candidate.min_alignment
            << " min_facet_quality=" << candidate.min_quality << " ids_unique=1 published=1\n";
  ProbePhysicalOwnerTransactionRehearsal(*patch, *accepted, candidate, mixed_residual,
                                         config.output_prefix);
  if (config.quad_verify_rollback) {
    auto* old = accepted.get();
    auto* node = old->GetNoh(0);
    auto* element = old->GetElement(0);
    std::vector<std::vector<ElementAdaptive*>> observers;
    for (unsigned i = 0; i < old->GetNumberNos(); ++i) {
      const auto& values = old->GetNoh(i)->GetElements();
      observers.emplace_back(values.begin(), values.end());
    }
    try {
      auto rejected = Generate(*patch, true);
      (void)rejected;
    } catch (const PublicationFailure& error) {
      Require(accepted.get() == old && patch->GetSubMesh() == old && old->GetNoh(0) == node &&
                  old->GetElement(0) == element,
              "Rollback damaged the accepted physical owner");
      for (unsigned i = 0; i < old->GetNumberNos(); ++i) {
        const auto& values = old->GetNoh(i)->GetElements();
        Require(std::vector<ElementAdaptive*>(values.begin(), values.end()) == observers[i],
                "Rollback changed accepted node observers");
      }
      std::cout << "QUAD_ROLLBACK preserved=1 previous_nonempty=1 reason=" << error.what() << '\n';
      return 1;
    }
    throw std::runtime_error("Expected publication failure did not occur");
  }
  return 0;
}
} // namespace apmesh::quad
