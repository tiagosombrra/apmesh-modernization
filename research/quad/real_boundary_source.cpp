#include "real_boundary_source.h"
#include "crab_mesh/aft/boundary.h"
#include "crab_mesh/aft/edge.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_bezier.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>

namespace apmesh::quad {
namespace {
using namespace Par2DJMesh::AFT;
void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}
using Key = std::pair<double, double>;
std::array<double, 3> Xyz(const PointAdaptive& point) {
  return {point.GetX(), point.GetY(), point.GetZ()};
}
bool Near(const std::array<double, 3>& a, const std::array<double, 3>& b) {
  for (unsigned i = 0; i < 3; ++i)
    if (!std::isfinite(a[i]) || !std::isfinite(b[i]) || std::abs(a[i] - b[i]) > 1e-10)
      return false;
  return true;
}
unsigned Side(UvVertex a, UvVertex b) {
  if (a.v == 0 && b.v == 0 && a.u < b.u)
    return 0;
  if (a.u == 1 && b.u == 1 && a.v < b.v)
    return 1;
  if (a.v == 1 && b.v == 1 && a.u > b.u)
    return 2;
  if (a.u == 0 && b.u == 0 && a.v > b.v)
    return 3;
  throw std::runtime_error("Original boundary has an invalid oriented source interval");
}
UvVertex Uv(unsigned side, double t) {
  return side == 0   ? UvVertex{t, 0}
         : side == 1 ? UvVertex{1, t}
         : side == 2 ? UvVertex{t, 1}
                     : UvVertex{0, t};
}
std::array<double, 4> Box(QuadtreeCell& cell) {
  return {cell.getMin()->getX(), cell.getMin()->getY(), cell.getMax()->getX(),
          cell.getMax()->getY()};
}
std::unique_ptr<Boundary> SourceBoundary(PatchBezier& patch,
                                         const std::vector<RealBoundarySite>& sites) {
  auto boundary = std::make_unique<Boundary>();
  for (const auto& site : sites)
    boundary->addVertex(site.uv.u, site.uv.v,
                        static_cast<CurveAdaptiveParametric*>(patch.GetCurve(site.side)),
                        patch.IsCurveReversed(site.side));
  const auto last_side = sites.back().side;
  Require(boundary->close(static_cast<CurveAdaptiveParametric*>(patch.GetCurve(last_side)),
                          patch.IsCurveReversed(last_side)),
          "Real source boundary did not close");
  return boundary;
}
std::size_t CaptureCell(QuadtreeCell& cell, std::vector<RealSourceCell>& cells) {
  const auto index = cells.size();
  cells.push_back({Box(cell), static_cast<unsigned long>(cell.getLevel()), {}, cell.subdivided()});
  if (cell.subdivided())
    for (unsigned i = 0; i < 4; ++i) {
      Require(cell.getChild(i) != nullptr, "Original source tree has a missing child");
      const auto child = CaptureCell(*cell.getChild(i), cells);
      cells[index].children[i] = child;
    }
  return index;
}
void ReplayCell(QuadtreeCell& cell, const RealBoundarySource& source, std::size_t index,
                std::set<std::size_t>& visited) {
  Require(index < source.cells.size() && visited.insert(index).second,
          "Source tree replay has a missing or repeated cell");
  const auto& saved = source.cells[index];
  Require(Box(cell) == saved.box && static_cast<unsigned long>(cell.getLevel()) == saved.level,
          "Native replay changed original source tree bounds or level");
  if (saved.subdivided) {
    cell.subdivideToLevel(saved.level + 1);
    for (unsigned i = 0; i < 4; ++i)
      ReplayCell(*cell.getChild(i), source, saved.children[i], visited);
  }
}
} // namespace

RealBoundarySource CaptureRealBoundary(PatchBezier& patch, Quadtree& tree) {
  Require(tree.getRoot() && tree.getBoundary(), "Original source tree is incomplete");
  RealBoundarySource result;
  std::map<Key, RealBoundarySite> source_nodes;
  for (unsigned side = 0; side < 4; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    Require(curve != nullptr, "Missing original parametric curve");
    const std::vector<double> parameters(curve->parameters_.begin(), curve->parameters_.end());
    Require(parameters.size() == curve->GetNumBerPoints() && parameters.size() >= 2 &&
                parameters.front() == 0 && parameters.back() == 1,
            "Original curve partition is incomplete");
    const bool reversed = patch.IsCurveReversed(side);
    result.reversed_curves[side] = reversed;
    result.reversed_sides += reversed;
    bool nonuniform = false;
    for (std::size_t i = 0; i < parameters.size(); ++i) {
      const double t = parameters[i];
      Require(std::isfinite(t) && (i == 0 || t > parameters[i - 1]),
              "Original curve parameters are not strictly ordered");
      const auto* node = dynamic_cast<NodeAdaptive*>(curve->GetPoint(static_cast<unsigned>(i)));
      const auto uv = Uv(side, reversed ? 1 - t : t);
      Require(node && Near(Xyz(*node), Xyz(curve->FindPointByParameter(t))) &&
                  Near(Xyz(*node), Xyz(patch.Parameterize(uv.u, uv.v))),
              "Original curve sample disagrees with curve or patch geometry");
      RealBoundarySite site;
      site.uv = uv;
      site.xyz = Xyz(*node);
      site.source_id = node->GetId();
      site.side = side;
      site.parameter = t;
      result.original_curves[side].push_back({t, site.xyz, site.source_id});
      // Corner identity is checked across its two incident original curves.
      const auto inserted = source_nodes.emplace(Key{uv.u, uv.v}, site);
      Require(inserted.second || (inserted.first->second.source_id == site.source_id &&
                                  inserted.first->second.xyz == site.xyz),
              "Original source curves disagree at a shared endpoint");
      if (i > 1 && std::abs((t - parameters[i - 1]) - (parameters[1] - parameters[0])) > 1e-12)
        nonuniform = true;
    }
    result.nonuniform_sides += nonuniform;
  }
  const auto vertices_list = tree.getBoundary()->getBoundary();
  const std::vector<Vertex*> vertices(vertices_list.begin(), vertices_list.end());
  const auto edges_list = tree.getBoundary()->getEdges();
  const std::vector<Edge*> edges(edges_list.begin(), edges_list.end());
  Require(vertices.size() == source_nodes.size() && edges.size() == vertices.size(),
          "Native boundary omitted or duplicated original curve samples");
  for (std::size_t i = 0; i < vertices.size(); ++i) {
    const UvVertex uv{vertices[i]->getX(), vertices[i]->getY()};
    const auto found = source_nodes.find({uv.u, uv.v});
    Require(found != source_nodes.end(), "Native boundary has a foreign source parameter");
    auto site = found->second;
    auto* next = vertices[(i + 1) % vertices.size()];
    site.side = Side(uv, {next->getX(), next->getY()});
    const double local = site.side % 2 == 0 ? uv.u : uv.v;
    site.parameter = patch.IsCurveReversed(site.side) ? 1 - local : local;
    Require(edges[i]->getV1() == vertices[i] && edges[i]->getV2() == next,
            "Native source edge ordering differs from source contour");
    site.edge_mid = {edges[i]->getMid()->getX(), edges[i]->getMid()->getY()};
    // Quadtree::generate uses normalized arc lengths for subdivision, then
    // resets every boundary edge to -1 before the refined-tree observer.
    site.refined_length = edges[i]->getLen();
    result.sites.push_back(site);
  }
  auto parametric_boundary = SourceBoundary(patch, result.sites);
  std::size_t edge_index = 0;
  for (auto* edge : parametric_boundary->getEdges()) {
    auto& site = result.sites.at(edge_index++);
    Require(std::array<double, 2>{edge->getMid()->getX(), edge->getMid()->getY()} == site.edge_mid,
            "Original parametric midpoint changed before tree replay");
    site.normalized_length = edge->getLen();
  }
  result.tree_factor = tree.getFactor();
  result.tree_cap = tree.getMaxLevelCap();
  result.face_quality = tree.FaceQualityThreshold();
  result.low_quality_h = tree.LowQualityHFactor();
  result.template_quality = tree.TemplatePoorScoreThreshold();
  result.source_leaves = tree.GetLeafCount();
  CaptureCell(*tree.getRoot(), result.cells);
  ValidateRealBoundary(patch, result);
  return result;
}

void ValidateRealBoundary(PatchBezier& patch, const RealBoundarySource& source) {
  Require(source.sites.size() >= 4 && !source.cells.empty(), "Missing original source boundary");
  std::map<Key, OriginalCurveSample> original;
  for (unsigned side = 0; side < 4; ++side) {
    const auto& samples = source.original_curves[side];
    Require(source.reversed_curves[side] == patch.IsCurveReversed(side),
            "Original source curve traversal changed");
    Require(samples.size() >= 2 && samples.front().parameter == 0 && samples.back().parameter == 1,
            "Original curve witness has missing endpoints");
    for (std::size_t i = 0; i < samples.size(); ++i) {
      const auto& sample = samples[i];
      Require(std::isfinite(sample.parameter) &&
                  (i == 0 || sample.parameter > samples[i - 1].parameter),
              "Original curve witness lost parameter ordering");
      const auto uv =
          Uv(side, patch.IsCurveReversed(side) ? 1 - sample.parameter : sample.parameter);
      const auto entry = original.emplace(Key{uv.u, uv.v}, sample);
      Require(entry.second || (entry.first->second.source_id == sample.source_id &&
                               entry.first->second.xyz == sample.xyz),
              "Original curve witnesses disagree at a shared endpoint");
    }
  }
  Require(source.sites.size() == original.size(),
          "Boundary omitted or inserted an original curve sample");
  std::set<Key> coordinates;
  std::set<unsigned long> identities;
  std::array<unsigned, 4> intervals{};
  for (std::size_t i = 0; i < source.sites.size(); ++i) {
    const auto& site = source.sites[i];
    const auto& next = source.sites[(i + 1) % source.sites.size()];
    const auto found = original.find({site.uv.u, site.uv.v});
    Require(found != original.end() && found->second.source_id == site.source_id &&
                found->second.xyz == site.xyz,
            "Boundary sample differs from the actual original curve partition");
    Require(site.side < 4 && Side(site.uv, next.uv) == site.side &&
                coordinates.insert({site.uv.u, site.uv.v}).second &&
                identities.insert(site.source_id).second,
            "Duplicate, foreign or inconsistently oriented source boundary site");
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(site.side));
    const double local = site.side % 2 == 0 ? site.uv.u : site.uv.v;
    Require(curve && site.parameter == (patch.IsCurveReversed(site.side) ? 1 - local : local) &&
                Near(site.xyz, Xyz(curve->FindPointByParameter(site.parameter))) &&
                Near(site.xyz, Xyz(patch.Parameterize(site.uv.u, site.uv.v))),
            "Source boundary parameter geometry is invalid");
    if (!std::isfinite(site.normalized_length) || site.normalized_length <= 0 ||
        site.refined_length != -1) {
      std::ostringstream message;
      message << "Original source edge metric is invalid: side=" << site.side
              << " parameter=" << site.parameter << " length=" << site.normalized_length;
      throw std::runtime_error(message.str());
    }
    ++intervals[site.side];
  }
  Require(std::all_of(intervals.begin(), intervals.end(), [](unsigned n) { return n > 0; }),
          "Original source boundary lost a side");
}

std::unique_ptr<Quadtree> ReplayRealSourceTree(PatchBezier& patch,
                                               const RealBoundarySource& source) {
  ValidateRealBoundary(patch, source);
  auto boundary = SourceBoundary(patch, source.sites);
  const auto edges = boundary->getEdges();
  std::size_t i = 0;
  for (auto* edge : edges) {
    const auto& site = source.sites.at(i++);
    Require(edge->getLen() == site.normalized_length &&
                std::array<double, 2>{edge->getMid()->getX(), edge->getMid()->getY()} ==
                    site.edge_mid,
            "Native boundary replay changed original parametric midpoint or normalized length");
    edge->setLen(site.refined_length);
  }
  auto tree = std::make_unique<Quadtree>(nullptr, source.tree_factor);
  tree->setBoundary(boundary.release());
  tree->setMaxLevelCap(source.tree_cap);
  tree->SetQualityControls({source.face_quality, source.low_quality_h, source.template_quality});
  const auto& box = source.cells.front().box;
  auto low = std::make_unique<Vertex>(box[0], box[1]);
  auto high = std::make_unique<Vertex>(box[2], box[3]);
  auto root = std::make_unique<QuadtreeCell>(tree->getCellId(), tree.get(), low.get(), high.get(),
                                             nullptr, source.cells.front().level);
  tree->setRoot(root.get());
  root.release();
  low.release();
  high.release();
  std::set<std::size_t> visited;
  ReplayCell(*tree->getRoot(), source, 0, visited);
  Require(visited.size() == source.cells.size() && tree->GetLeafCount() == source.source_leaves,
          "Native replay changed the original refined source tree");
  return tree;
}
} // namespace apmesh::quad
