#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <memory>
#include <stdexcept>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "crab_mesh/aft/advancing_front.h"

#if defined(min) || defined(max)
#error Windows headers must not export min/max macros into the UV interfaces.
#endif

double TOLERANCE_AFT = 1e-8;
double TOLERANCE = 1e-8;
double DELTA = 1e-8;
double EPSYLON = 1e-8;
std::string USE_TEMPLATE = "y";
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0.0;
double AFT_LOCAL_POSTPROCESS_BLEND = 0.5;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0.0;
double QUADTREE_LOW_QUALITY_H_FACTOR = 1.0;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0.0;

namespace {
bool registration_contracts_ok = true;

void registration_check(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Registration contract failed: %s\n", message);
    registration_contracts_ok = false;
  }
}

void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}

void square(Boundary& boundary) {
  for (int side = 0; side < 4; ++side) {
    for (int step = 0; step < 4; ++step) {
      const double t = step / 4.0;
      const double x = side == 0 ? t : (side == 1 ? 1.0 : (side == 2 ? 1.0 - t : 0.0));
      const double y = side == 1 ? t : (side == 2 ? 1.0 : (side == 3 ? 1.0 - t : 0.0));
      boundary.addVertex(x, y, nullptr);
    }
  }
  require(boundary.close(nullptr), "square boundary closes");
  // A null-curve fixture supplies the normalized size normally set by curve integration.
  for (auto* edge : boundary.getEdges())
    edge->setLen(edge->length());
}

struct InjectedFailure {};

class FailedFront : public AdvancingFront {
public:
  explicit FailedFront(int failure) : AdvancingFront(0.85, 1e-8, 0), failure_(failure) {}
  MethodStatus makeGeometryBasedMesh() override {
    require(!getQuadtree()->getMesh().empty(), "failure injected after actual template generation");
    std::printf("templates_before_failure=%zu\n", getQuadtree()->getMesh().size());
    if (failure_ == 1)
      throw InjectedFailure{};
    return failure_ == 2 ? ADVF_GEOMETRY_EDGE_REJECTED_TWICE : ADVF_EMPTY;
  }
  MethodStatus makeTopologyBasedMesh() override {
    require(failure_ == 2, "topology fallback only in selected control");
    return ADVF_TOPOLOGY_EDGE_REJECTED_TWICE;
  }

private:
  int failure_;
};

void failed(int failure) {
  bool caught = false;
  try {
    FailedFront front(failure);
    square(*front.getBoundary());
    require(!front.execute({}), "injected failure returns false");
  } catch (const InjectedFailure&) {
    caught = true;
  }
  require(caught == (failure == 1), "exception unwind reaches caller");
}

void normal(bool check_transfer) {
  AdvancingFront front(0.85, 1e-8, 0);
  square(*front.getBoundary());
  require(front.execute({}), "real UV generation succeeds");
  require(!front.getMesh().empty() && !front.getInnerVertices().empty(),
          "nonempty generated output");
  require(front.GetRunStats().quadtree_template_count > 0, "positive template coverage");
  std::printf("generated_faces=%zu templates=%llu\n", front.getMesh().size(),
              front.GetRunStats().quadtree_template_count);
  const auto& counts = front.getQuadtree()->GetTemplateStats().template_count;
  std::printf("template_type_counts=%llu,%llu,%llu,%llu,%llu,%llu\n", counts[0], counts[1],
              counts[2], counts[3], counts[4], counts[5]);
  if (check_transfer) {
    require(front.getQuadtree()->getMesh().empty() && front.getQuadtree()->getEdges().empty() &&
                front.getQuadtree()->getVertices().empty(),
            "template owners transfer to front once");
  }
}

class CountedVertex : public Vertex {
public:
  CountedVertex(double x, double y, int& destroyed) : Vertex(x, y), destroyed_(destroyed) {}
  ~CountedVertex() override { ++destroyed_; }

private:
  int& destroyed_;
};

double analytic_curve_position(double parameter) {
  return 0.3 * parameter + 0.6 * parameter * parameter + 0.1 * parameter * parameter * parameter;
}

double analytic_curve_inverse(double position) {
  double low = 0, high = 1;
  for (int step = 0; step < 80; ++step) {
    const double middle = (low + high) / 2;
    if (analytic_curve_position(middle) < position)
      low = middle;
    else
      high = middle;
  }
  return (low + high) / 2;
}

void prepare_parametric_curve(CurveAdaptiveParametric& curve) {
  // Initialize the production polynomial evaluator directly, without a replacement generator.
  Matrix4x1 coefficients;
  coefficients << 0.1, 0.6, 0.3, 0.0;
  curve.SetMatGeoGx(coefficients);
  curve.CalculateLengthCurve();
  require(std::abs(curve.GetLength() - 1.0) < 1e-12, "analytic physical curve length");
}

void curve_evaluation_contracts() {
  CurveAdaptiveParametric curve;
  prepare_parametric_curve(curve);
  int sample = 0;
  for (double parameter : {0.0, 0.125, 0.5, 0.875, 1.0}) {
    const auto point = curve.FindPointByParameter(parameter);
    const auto gradient = curve.CalculateGradientByParameter(parameter);
    require(std::abs(point.GetX() - analytic_curve_position(parameter)) < 1e-12 &&
                point.GetY() == 0 && point.GetZ() == 0,
            "production curve position agrees with independent polynomial");
    const double expected_gradient = 0.3 + 1.2 * parameter + 0.3 * parameter * parameter;
    require(std::abs(gradient.GetX() - expected_gradient) < 1e-12 && gradient.GetY() == 0 &&
                gradient.GetZ() == 0,
            "production curve gradient agrees with independent derivative");
    std::printf("curve_success=sample:%d x:%a gradient:%a\n", sample++, point.GetX(),
                gradient.GetX());
  }
  const double expected_arc = analytic_curve_position(0.875) - analytic_curve_position(0.125);
  const double length = curve.CalculateParametricLength(0.125, 0.875);
  require(std::abs(length - expected_arc) < 1e-12, "physical arc agrees with analytic integral");
  require(std::abs(curve.CalculateParametricLength(0.875, 0.125) + expected_arc) < 1e-12,
          "reversed direct integration preserves its signed interval");
  const double midpoint = curve.CalculateMidparameterByParamters(0.125, 0.875);
  const double expected_midpoint =
      analytic_curve_inverse((analytic_curve_position(0.125) + analytic_curve_position(0.875)) / 2);
  // The legacy physical residual stops at TOLERANCE; dx/dt is at least 0.3.
  require(std::abs(midpoint - expected_midpoint) < TOLERANCE / 0.3,
          "physical midpoint agrees with independent inverse within the solver residual bound");
  std::printf("curve_integral=%a midpoint:%a\n", length, midpoint);
}

class ParametricFixture {
public:
  ParametricFixture(std::array<int, 2>& destroyed, int variant)
      : destroyed_(destroyed), side_(variant == 10 ? 4 : variant / 2),
        reversed_(variant != 10 && variant % 2 != 0), bound_(variant != 10),
        first_(std::make_unique<CountedVertex>(sides_[side_][0], sides_[side_][1], destroyed[0])),
        last_(std::make_unique<CountedVertex>(sides_[side_][2], sides_[side_][3], destroyed[1])),
        edge_(first_.get(), last_.get(), 301 + variant), original_midpoint_(edge_.getMid()),
        original_x_(original_midpoint_->getX()), original_y_(original_midpoint_->getY()),
        id_(301 + variant) {
    prepare_parametric_curve(curve_);
    edge_.setCurva(bound_ ? &curve_ : nullptr, reversed_);
    edge_.setLen(0.375);
    edge_.setFree(false);
    first_->addAdjacentEdge(&edge_);
    last_->addAdjacentEdge(&edge_);
  }
  ~ParametricFixture() { edge_.DetachVertices(); }
  ParametricFixture(const ParametricFixture&) = delete;
  ParametricFixture& operator=(const ParametricFixture&) = delete;

  void replace() { edge_.makeParamMid(); }

  void check_common() {
    require(destroyed_[0] == 0 && destroyed_[1] == 0 && edge_.getV1() == first_.get() &&
                edge_.getV2() == last_.get() && edge_.getId() == id_ && !edge_.isFree(),
            "parametric replacement preserves caller ownership and edge identity/scalars");
    require(first_->getX() == sides_[side_][0] && first_->getY() == sides_[side_][1] &&
                last_->getX() == sides_[side_][2] && last_->getY() == sides_[side_][3],
            "parametric replacement preserves endpoint geometry");
    for (auto* vertex : {first_.get(), last_.get()}) {
      const auto adjacent = vertex->getAdjacentEdges();
      require(adjacent.size() == 1 && adjacent.count(&edge_) == 1,
              "parametric replacement preserves caller adjacency");
    }
    const auto coefficients = curve_.GetMatGeoGx();
    require(coefficients(0) == 0.1 && coefficients(1) == 0.6 && coefficients(2) == 0.3 &&
                coefficients(3) == 0.0 && std::abs(curve_.GetLength() - 1.0) < 1e-12,
            "curve coefficients and total length remain unchanged; evaluation scratch is mutable");
  }

  void check_unchanged() {
    check_common();
    require(edge_.getMid() == original_midpoint_ && edge_.getLen() == 0.375,
            "failed parametric replacement preserves midpoint identity and normalized length");
    require(original_midpoint_->getX() == original_x_ && original_midpoint_->getY() == original_y_,
            "failed parametric replacement preserves cached geometry");
  }

  void check_success(int variant) {
    check_common();
    if (!bound_) {
      check_unchanged();
    } else if (side_ == 4) {
      require(std::abs(edge_.getMid()->getX() - 0.5) < 1e-15 &&
                  std::abs(edge_.getMid()->getY() - 0.45) < 1e-15 && edge_.getLen() == -1,
              "interior fallback preserves geometric midpoint and length sentinel");
    } else {
      const double first = sides_[side_][side_ % 2 == 0 ? 0 : 1];
      const double last = sides_[side_][side_ % 2 == 0 ? 2 : 3];
      const double physical_first = reversed_ ? 1 - first : first;
      const double physical_last = reversed_ ? 1 - last : last;
      double expected = analytic_curve_inverse(
          (analytic_curve_position(physical_first) + analytic_curve_position(physical_last)) / 2);
      if (reversed_)
        expected = 1 - expected;
      const double actual = side_ % 2 == 0 ? edge_.getMid()->getX() : edge_.getMid()->getY();
      require(std::abs(actual - expected) < TOLERANCE / 0.3,
              "parametric midpoint preserves physical incidence direction");
      const double fixed = side_ % 2 == 0 ? edge_.getMid()->getY() : edge_.getMid()->getX();
      require(fixed == (side_ == 0 || side_ == 3 ? 0 : 1), "midpoint remains on its patch side");
      require(std::abs(edge_.getLen() - std::abs(analytic_curve_position(physical_last) -
                                                 analytic_curve_position(physical_first))) < 1e-12,
              "normalized physical arc agrees with independent integral");
    }
    std::printf("parametric_success=variant:%d x:%a y:%a len:%a null:%d\n", variant,
                edge_.getMid()->getX(), edge_.getMid()->getY(), edge_.getLen(), bound_ ? 0 : 1);
  }

private:
  inline static constexpr std::array<std::array<double, 4>, 5> sides_{
      {{0, 0, 0.5, 0}, {1, 0, 1, 0.5}, {1, 1, 0.5, 1}, {0, 1, 0, 0.5}, {0.2, 0.2, 0.8, 0.7}}};
  std::array<int, 2>& destroyed_;
  int side_;
  bool reversed_, bound_;
  CurveAdaptiveParametric curve_;
  std::unique_ptr<CountedVertex> first_, last_;
  Edge edge_;
  Vertex* original_midpoint_;
  double original_x_, original_y_;
  long id_;
};

void parametric_contracts() {
  curve_evaluation_contracts();
  for (int variant = 0; variant < 11; ++variant) {
    std::array<int, 2> destroyed{};
    {
      ParametricFixture fixture(destroyed, variant);
      fixture.replace();
      fixture.check_success(variant);
    }
    require(destroyed[0] == 1 && destroyed[1] == 1,
            "parametric caller teardown occurs exactly once");
  }
}

class AngleFixture {
public:
  AngleFixture(std::array<int, 4>& destroyed, bool adjacency)
      : destroyed_(destroyed), a_(std::make_unique<CountedVertex>(0, 0, destroyed[0])),
        b_(std::make_unique<CountedVertex>(3, 0, destroyed[1])),
        c_(std::make_unique<CountedVertex>(3, 4, destroyed[2])),
        d_(std::make_unique<CountedVertex>(0, 4, destroyed[3])), edge_(a_.get(), b_.get(), 107),
        midpoint_(edge_.getMid()), adjacency_(adjacency) {
    edge_.setLen(0.25);
    edge_.setFree(false);
    if (adjacency_)
      for (auto* vertex : vertices())
        vertex->addAdjacentEdge(&edge_);
  }
  ~AngleFixture() { edge_.DetachVertices(); }
  AngleFixture(const AngleFixture&) = delete;
  AngleFixture& operator=(const AngleFixture&) = delete;

  double angle(int branch) {
    switch (branch) {
    case 0:
      return edge_.angle(a_.get(), c_.get());
    case 1:
      return edge_.angle(c_.get(), a_.get());
    case 2:
      return edge_.angle(b_.get(), d_.get());
    case 3:
      return edge_.angle(d_.get(), b_.get());
    default:
      return edge_.angle(c_.get(), d_.get());
    }
  }

  void check() {
    require(std::all_of(destroyed_.begin(), destroyed_.end(), [](int count) { return count == 0; }),
            "angle helper preserves every caller-owned endpoint");
    require(edge_.getV1() == a_.get() && edge_.getV2() == b_.get() && edge_.getMid() == midpoint_ &&
                midpoint_->getX() == 1.5 && midpoint_->getY() == 0 && edge_.getLen() == 0.25 &&
                edge_.getId() == 107 && !edge_.isFree() && edge_.length() == 3,
            "angle helper preserves receiver identity, geometry and scalar state");
    const std::array<double, 4> x{0, 3, 3, 0}, y{0, 0, 4, 4};
    const auto points = vertices();
    for (std::size_t index = 0; index < points.size(); ++index) {
      require(points[index]->getX() == x[index] && points[index]->getY() == y[index],
              "angle helper preserves caller geometry");
      const auto adjacent = points[index]->getAdjacentEdges();
      require(adjacent.size() == (adjacency_ ? 1U : 0U) &&
                  (!adjacency_ || adjacent.count(&edge_) == 1),
              "angle helper preserves caller adjacency identity");
    }
  }

private:
  std::array<Vertex*, 4> vertices() { return {a_.get(), b_.get(), c_.get(), d_.get()}; }
  std::array<int, 4>& destroyed_;
  std::unique_ptr<CountedVertex> a_, b_, c_, d_;
  Edge edge_;
  Vertex* midpoint_;
  bool adjacency_;
};

void check_angle(double actual, int branch) {
  // The adjacent fixtures form a 3-4-5 right triangle at either receiver endpoint.
  const double expected = branch == 4 ? -1.0 : std::atan2(4.0, 3.0);
  require(std::abs(actual - expected) < 1e-12,
          "angle helper agrees with independent triangle geometry");
}

void check_angle_destruction(const std::array<int, 4>& destroyed) {
  require(std::all_of(destroyed.begin(), destroyed.end(), [](int count) { return count == 1; }),
          "caller destroys each angle-fixture endpoint exactly once");
}

void angle_contracts() {
  for (int adjacency = 0; adjacency < 2; ++adjacency)
    for (int branch = 0; branch < 5; ++branch) {
      std::array<int, 4> destroyed{};
      {
        AngleFixture fixture(destroyed, adjacency != 0);
        const double value = fixture.angle(branch);
        check_angle(value, branch);
        fixture.check();
        std::printf("angle_success=branch:%d adjacency:%d value:%a preserved:4\n", branch,
                    adjacency, value);
      }
      check_angle_destruction(destroyed);
    }
}

std::unique_ptr<AdvancingFront> partial(int& destroyed) {
  auto front = std::make_unique<AdvancingFront>();
  front->getBoundary()->addVertex(0, 0, nullptr);
  front->getBoundary()->addVertex(1, 0, nullptr);
  auto* a = new CountedVertex(0.2, 0.2, destroyed);
  auto* b = new CountedVertex(0.8, 0.2, destroyed);
  auto* c = new CountedVertex(0.2, 0.8, destroyed);
  front->addVertices({a, b, c});
  auto* edge = new Edge(a, b);
  a->addAdjacentEdge(edge);
  b->addAdjacentEdge(edge);
  front->addEdges({edge});
  front->addMesh({new Face(a, b, c)});
  return front;
}

void pending_tree() {
  auto boundary = std::make_unique<Boundary>();
  square(*boundary);
  Quadtree tree(boundary.release());
  require(tree.execute({}), "standalone quadtree builds");
  require(tree.makeTemplateBasedMesh() == QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "standalone templates build");
  require(!tree.getMesh().empty(), "standalone output awaiting transfer");
}

class TransferFront : public AdvancingFront {
public:
  using AdvancingFront::fillMesh;
};

void prepare_transfer(TransferFront& front) {
  square(*front.getBoundary());
  require(front.getQuadtree()->execute({}), "transfer source quadtree builds");
  require(front.getQuadtree()->makeTemplateBasedMesh() == QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "transfer source templates build");
  require(!front.getQuadtree()->getMesh().empty(), "positive transfer source coverage");
}

void transfer_order() {
  TransferFront front;
  prepare_transfer(front);
  auto expected_vertices = front.getQuadtree()->getVertices();
  auto expected_edges = front.getQuadtree()->getEdges();
  auto expected_faces = front.getQuadtree()->getMesh();
  auto* a = new Vertex(0.2, 0.2);
  auto* b = new Vertex(0.8, 0.2);
  auto* c = new Vertex(0.2, 0.8);
  auto* edge = new Edge(a, b);
  auto* face = new Face(a, b, c);
  front.addVertices({a, b, c});
  front.addEdges({edge});
  front.addMesh({face});
  expected_vertices.insert(expected_vertices.begin(), {a, b, c});
  expected_edges.push_front(edge);
  expected_faces.push_front(face);
  front.fillMesh();
  require(front.getInnerVertices() == expected_vertices &&
              front.getInnerEdges() == expected_edges && front.getMesh() == expected_faces,
          "owner handoff preserves every address and append order");
  require(front.getQuadtree()->getVertices().empty() && front.getQuadtree()->getEdges().empty() &&
              front.getQuadtree()->getMesh().empty(),
          "source owners consumed");
  front.fillMesh();
  require(front.getInnerVertices() == expected_vertices &&
              front.getInnerEdges() == expected_edges && front.getMesh() == expected_faces,
          "repeated empty handoff does not duplicate owners");
}

void midpoint_alias() {
  int destroyed = 0;
  {
    AdvancingFront front;
    auto* a = new CountedVertex(0, 0, destroyed);
    auto* b = new CountedVertex(1, 0, destroyed);
    auto* c = new CountedVertex(0, 1, destroyed);
    front.addVertices({a, b, c});
    front.addMesh({new Face(a, b, c, a, 1)});
  }
  require(destroyed == 3, "borrowed midpoint alias is not destroyed by face detachment");
}

void face_alias_cache() {
  int destroyed = 0;
  auto a = std::make_unique<CountedVertex>(0, 0, destroyed);
  auto b = std::make_unique<CountedVertex>(3, 0, destroyed);
  auto c = std::make_unique<CountedVertex>(0, 3, destroyed);
  {
    Face face(a.get(), b.get(), c.get(), a.get(), 17);
    face.setVertices(a.get(), b.get(), c.get());
    require(destroyed == 0 && face.getMid() != a.get(),
            "cache replacement preserves the borrowed endpoint alias");
    require(face.getMid()->getX() == 1 && face.getMid()->getY() == 1,
            "replacement midpoint retains the centroid formula");
    face.DetachVertices();
  }
  require(destroyed == 0, "endpoints remain caller-owned after explicit detachment");
}

void primitive_contracts() {
  Vertex a(0, 0), b(3, 4), c(0, 3), d(6, 0);
  Edge edge(&a, &b, 19);
  edge.setLen(0.25);
  require(edge.length() == 5 && edge.getMid()->getX() == 1.5 && edge.getMid()->getY() == 2,
          "edge construction geometry");
  edge.setVertices(&a, &d);
  require(edge.getV1() == &a && edge.getV2() == &d && edge.length() == 6 &&
              edge.getMid()->getX() == 3 && edge.getMid()->getY() == 0 && edge.getLen() == 0.25 &&
              edge.getId() == 19,
          "edge replacement geometry, scalar state and identity");
  edge.setVertices(nullptr, nullptr);
  require(edge.length() == 0 && edge.getMid()->getX() == 0 && edge.getMid()->getY() == 0,
          "null endpoint replacement retains default cache geometry");
  Face face(&a, &b, &c, 23);
  face.h = 0.5;
  face.setVertices(&a, &d, &c);
  require(face.getMid()->getX() == 2 && face.getMid()->getY() == 1 && face.surface() == 9 &&
              face.h == 0.5 && face.getId() == 23,
          "face replacement geometry, scalar state and identity");
  face.DetachVertices();
  face_alias_cache();
}

void unowned_cell_query(bool use_face) {
  Vertex minimum(0, 0), maximum(1, 1);
  QuadtreeCell cell(1, nullptr, &minimum, &maximum);
  Edge edge(new Vertex(0, 0), new Vertex(1, 0));
  edge.setLen(1);
  Face face(new Vertex(0, 0), new Vertex(1, 0), new Vertex(0, 1));
  face.h = 1;
  bool caught = false;
  try {
    if (use_face)
      cell.shouldSubdivide(&face);
    else
      cell.shouldSubdivide(&edge);
  } catch (const std::logic_error&) {
    caught = true;
  }
  require(caught, "unowned cell subdivision query reports its missing context");
}

void registration_contracts() {
  Boundary boundary;
  auto* first = boundary.addVertex(0, 0, nullptr);
  auto* second = boundary.addVertex(1, 0, nullptr);
  auto* third = boundary.addVertex(0, 1, nullptr);
  require(boundary.close(nullptr), "registration contour closes");
  require(first->getId() == 1 && second->getId() == 2 && third->getId() == 3 &&
              boundary.getLastVertexId() == 3 && boundary.getLastEdgeId() == 3,
          "successful boundary IDs and ordering");
  for (auto* vertex : boundary.getBoundary())
    require(vertex->getAdjacentEdges().size() == 2, "closed contour incidence");
  AdvancingFront front(0.85, 1e-8, 0);
  square(*front.getBoundary());
  require(front.execute({}), "registration fixture generates actual templates/front");
  // Compare successful geometry, IDs and owner order without unstable addresses.
  for (auto* vertex : front.getInnerVertices())
    std::printf("registration_vertex=%ld,%a,%a\n", vertex->getId(), vertex->getX(), vertex->getY());
  for (auto* edge : front.getInnerEdges())
    std::printf("registration_edge=%ld,%ld,%ld,%a\n", edge->getId(), edge->getV1()->getId(),
                edge->getV2()->getId(), edge->getLen());
  for (auto* face : front.getMesh())
    std::printf("registration_face=%ld,%ld,%ld,%ld\n", face->getId(), face->getV1()->getId(),
                face->getV2()->getId(), face->getV3()->getId());
}

struct TreeFixture {
  Vertex a{0.2, 0.2}, b{0.3, 0.2}, c{0.2, 0.3};
  Face face{&a, &b, &c};
  FaceList oldmesh;
  std::unique_ptr<Quadtree> tree;

  explicit TreeFixture(int stage) {
    auto boundary = std::make_unique<Boundary>();
    if (stage < 2) {
      boundary->addVertex(0, 0, nullptr);
    } else {
      square(*boundary);
    }
    tree = std::make_unique<Quadtree>(boundary.get());
    boundary.release();
    if (stage == 1) {
      auto min = std::make_unique<Vertex>(0, 0);
      auto max = std::make_unique<Vertex>(1, 1);
      auto root =
          std::make_unique<QuadtreeCell>(tree->getCellId(), tree.get(), min.get(), max.get());
      tree->setRoot(root.get());
      root.release();
      min.release();
      max.release();
    }
    face.h = 0.125;
    if (stage == 3)
      oldmesh.push_back(&face);
    if (stage == 4) {
      require(tree->generate({}) == QUAD_INITIAL_TREE_DONE, "neighbor fixture generates");
      // Refine a real leaf through the public API to create a level gap of two.
      auto* leaf = tree->getLeaves().front();
      leaf->subdivideToLevel(leaf->getLevel() + 2);
    }
  }
  ~TreeFixture() { face.DetachVertices(); }
};

void tree_operation(TreeFixture& fixture, int stage) {
  if (stage == 1)
    fixture.tree->getRoot()->subdivideToLevel(1);
  else if (stage == 4)
    require(fixture.tree->refineAccordingToNeighbors() == QUAD_REFINE_ACCORDING_TO_NEIGHBORS_DONE,
            "neighbor refinement completes");
  else
    require(fixture.tree->generate(fixture.oldmesh) == QUAD_INITIAL_TREE_DONE,
            "tree generation completes");
}

void trace_tree(QuadtreeCell* cell) {
  std::printf("tree_cell=%ld,%lu,%a,%a,%a,%a\n", cell->getId(), cell->getLevel(),
              cell->getMin()->getX(), cell->getMin()->getY(), cell->getMax()->getX(),
              cell->getMax()->getY());
  for (int direction = 0; direction < 4; ++direction)
    for (auto* neighbor : cell->getNeighbors(direction))
      std::printf("tree_neighbor=%ld,%d,%ld\n", cell->getId(), direction, neighbor->getId());
  for (auto* edge : cell->getEdges())
    std::printf("tree_edge=%ld,%ld\n", cell->getId(), edge->getId());
  if (cell->subdivided())
    for (int position = 0; position < 4; ++position) {
      require(cell->getChild(position)->getParent() == cell, "child borrows actual parent");
      trace_tree(cell->getChild(position));
    }
}

void tree_contracts() {
  for (int stage = 0; stage < 5; ++stage) {
    TreeFixture fixture(stage);
    const int before = fixture.tree->getNumCells();
    tree_operation(fixture, stage);
    if (stage == 1)
      require(fixture.tree->getNumCells() == 5 && fixture.tree->getLeaves().size() == 4,
              "one subdivision produces four registered children");
    if (stage == 3)
      require(fixture.face.getV1() == &fixture.a && fixture.face.h == 0.125,
              "old mesh remains borrowed without parameter mutation");
    if (stage == 4)
      require(fixture.tree->getNumCells() > before, "neighbor refinement really subdivides");
    std::printf("tree_stage=%d\n", stage);
    trace_tree(fixture.tree->getRoot());
    for (auto* leaf : fixture.tree->getLeaves()) {
      require(!leaf->subdivided(), "registered leaves have no children");
      std::printf("tree_leaf=%ld\n", leaf->getId());
    }
  }
}

#if defined(_MSC_VER) && defined(_DEBUG)
int denied_allocations = 0;
int allocation_attempts = 0;
int fail_after = -1;
bool forbid_allocations = true;
int allocation_hook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC || kind == _HOOK_REALLOC) {
    ++allocation_attempts;
    if (forbid_allocations || fail_after-- == 0) {
      ++denied_allocations;
      return FALSE;
    }
  }
  return TRUE;
}

void allocation_free_teardown() {
  int destroyed = 0;
  auto front = partial(destroyed);
  std::set_terminate([] {
    std::fprintf(stderr, "teardown allocation caused termination\n");
    std::_Exit(73);
  });
  const auto previous = _CrtSetAllocHook(allocation_hook);
  front.reset();
  _CrtSetAllocHook(previous);
  require(destroyed == 3 && denied_allocations == 0, "teardown performs no allocation");
  std::puts("teardown_allocation_attempts=0");
}

void allocation_hook_control() {
  bool caught = false;
  const auto previous = _CrtSetAllocHook(allocation_hook);
  try {
    auto unexpected = std::make_unique<Vertex>(1, 2);
  } catch (const std::bad_alloc&) {
    caught = true;
  }
  _CrtSetAllocHook(previous);
  require(caught && denied_allocations > 0, "deliberate allocation denial is observed");
  std::puts("allocation_hook_control=detected");
}

void transfer_allocation_failure() {
  forbid_allocations = false;
  allocation_attempts = 0;
  {
    TransferFront front;
    prepare_transfer(front);
    const auto previous = _CrtSetAllocHook(allocation_hook);
    front.fillMesh();
    _CrtSetAllocHook(previous);
  }
  const int total = allocation_attempts;
  require(total > 2, "positive measured allocation coverage in observer preparation");
  for (const int index : {0, total / 2, total - 1}) {
    TransferFront front;
    prepare_transfer(front);
    const auto original_vertices = front.getQuadtree()->getVertices();
    const auto original_edges = front.getQuadtree()->getEdges();
    const auto original_faces = front.getQuadtree()->getMesh();
    allocation_attempts = denied_allocations = 0;
    fail_after = index;
    bool caught = false;
    const auto previous = _CrtSetAllocHook(allocation_hook);
    try {
      front.fillMesh();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
    _CrtSetAllocHook(previous);
    require(caught && denied_allocations == 1,
            "injected transfer allocation failure reaches caller");
    require(front.getInnerVertices().empty() && front.getInnerEdges().empty() &&
                front.getMesh().empty(),
            "failed observer preparation transfers no owners");
    require(front.getQuadtree()->getVertices() == original_vertices &&
                front.getQuadtree()->getEdges() == original_edges &&
                front.getQuadtree()->getMesh() == original_faces,
            "source owners remain complete after allocation failure");
  }
  std::printf("transfer_allocation_failures=3 measured_allocations=%d\n", total);
}

class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    allocation_attempts = denied_allocations = 0;
    forbid_allocations = false;
    fail_after = ordinal;
    previous_ = _CrtSetAllocHook(allocation_hook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};

template <class Action> int measure_allocations(Action action) {
  AllocationScope hook(-1);
  action();
  return allocation_attempts;
}

template <class Action> bool inject_allocation_failure(int ordinal, Action action) {
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      action();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  return caught && denied_allocations == 1;
}

void parametric_allocation_failures(int variant) {
  int total = 0;
  std::array<int, 2> calibrated_destroyed{};
  {
    ParametricFixture fixture(calibrated_destroyed, variant);
    total = measure_allocations([&] { fixture.replace(); });
    fixture.check_success(variant);
  }
  require(calibrated_destroyed[0] == 1 && calibrated_destroyed[1] == 1,
          "calibrated parametric teardown occurs exactly once");
  require(total > 0, "parametric sweep has positive measured allocation coverage");
  std::printf("parametric_measured=%d:%d\n", variant, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    std::array<int, 2> destroyed{};
    {
      ParametricFixture fixture(destroyed, variant);
      std::printf("parametric_inject=%d:%d\n", variant, ordinal);
      require(inject_allocation_failure(ordinal, [&] { fixture.replace(); }),
              "every measured parametric allocation denial propagates exactly once");
      fixture.check_unchanged();
      fixture.replace();
      fixture.check_success(variant);
    }
    require(destroyed[0] == 1 && destroyed[1] == 1,
            "caller endpoints survive every failed replacement");
  }
  std::printf("parametric_failure_sites=%d:%d/%d unchanged=1 retry=1\n", variant, total, total);
}

void curve_allocation_observation() {
  CurveAdaptiveParametric curve;
  prepare_parametric_curve(curve);
  PointAdaptive point;
  VectorAdaptive gradient;
  const int point_count = measure_allocations([&] {
    point = curve.FindPointByParameter(0.5);
    gradient = curve.CalculateGradientByParameter(0.5);
  });
  double arc = 0, midpoint = 0;
  const int arc_count =
      measure_allocations([&] { arc = curve.CalculateParametricLength(0.125, 0.875); });
  const int midpoint_count =
      measure_allocations([&] { midpoint = curve.CalculateMidparameterByParamters(0.125, 0.875); });
  require(std::abs(point.GetX() - analytic_curve_position(0.5)) < 1e-12 &&
              std::abs(gradient.GetX() - 0.975) < 1e-12 && arc > 0 && midpoint > 0.125 &&
              midpoint < 0.875,
          "allocation observations execute positive analytic curve operations");
  std::printf("curve_allocation_observation=point-gradient:%d\n", point_count);
  std::printf("curve_allocation_observation=arc:%d\n", arc_count);
  std::printf("curve_allocation_observation=midpoint:%d\n", midpoint_count);
  std::puts("curve_allocation_failure_coverage=unmeasured");
}

void angle_allocation_failures(int variant) {
  const int branch = variant % 5;
  const bool adjacency = variant >= 5;
  int total = 0;
  std::array<int, 4> calibrated_destroyed{};
  {
    AngleFixture fixture(calibrated_destroyed, adjacency);
    double result = 0;
    total = measure_allocations([&] { result = fixture.angle(branch); });
    check_angle(result, branch);
    fixture.check();
  }
  check_angle_destruction(calibrated_destroyed);
  require(total > 0, "angle sweep has positive measured allocation coverage");
  std::printf("angle_measured=%d:%d\n", variant, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    std::array<int, 4> destroyed{};
    {
      AngleFixture fixture(destroyed, adjacency);
      std::printf("angle_inject=%d:%d\n", variant, ordinal);
      require(inject_allocation_failure(ordinal, [&] { fixture.angle(branch); }),
              "every angle allocation denial propagates exactly once");
      fixture.check();
      check_angle(fixture.angle(branch), branch);
      fixture.check();
    }
    check_angle_destruction(destroyed);
  }
  std::printf("angle_failure_sites=%d:%d/%d unchanged=1 retry=1\n", variant, total, total);
}

template <class Action> void construction_failures(const char* name, Action action) {
  const int total = measure_allocations(action);
  require(total > 0, "construction control has positive measured allocation coverage");
  for (int ordinal = 0; ordinal < total; ++ordinal)
    require(inject_allocation_failure(ordinal, action),
            "every construction failure reaches caller");
  std::printf("allocation_failure_sites=%s:%d/%d\n", name, total, total);
}

void edge_construction_failures() {
  int destroyed = 0;
  auto a = std::make_unique<CountedVertex>(0, 0, destroyed);
  auto b = std::make_unique<CountedVertex>(3, 4, destroyed);
  construction_failures("edge", [&] {
    Edge edge(a.get(), b.get());
    edge.DetachVertices();
  });
  require(destroyed == 0, "failed edge construction never adopts caller endpoints");
}

void face_construction_failures() {
  int destroyed = 0;
  auto a = std::make_unique<CountedVertex>(0, 0, destroyed);
  auto b = std::make_unique<CountedVertex>(3, 0, destroyed);
  auto c = std::make_unique<CountedVertex>(0, 3, destroyed);
  construction_failures("face", [&] {
    Face face(a.get(), b.get(), c.get(), 1);
    face.DetachVertices();
  });
  construction_failures("face-explicit", [&] {
    Face face(a.get(), b.get(), c.get(), a.get(), 1);
    face.DetachVertices();
  });
  require(destroyed == 0, "failed face construction never adopts caller endpoints/midpoint");
}

void cache_replacement_failures(bool is_edge) {
  Vertex a(0, 0), b(3, 4), c(0, 3), d(6, 0);
  int total = 0;
  if (is_edge) {
    Edge edge(&a, &b);
    total = measure_allocations([&] { edge.setVertices(&c, &d); });
    edge.DetachVertices();
  } else {
    Face face(&a, &b, &c);
    total = measure_allocations([&] { face.setVertices(&b, &c, &d); });
    face.DetachVertices();
  }
  require(total > 0, "cache control has positive measured allocation coverage");
  bool unchanged = true;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    if (is_edge) {
      Edge edge(&a, &b, 19);
      edge.setLen(0.25);
      auto* midpoint = edge.getMid();
      const bool caught = inject_allocation_failure(ordinal, [&] { edge.setVertices(&c, &d); });
      unchanged = unchanged && caught && edge.getV1() == &a && edge.getV2() == &b &&
                  edge.getMid() == midpoint && edge.length() == 5 && edge.getLen() == 0.25 &&
                  midpoint->getX() == 1.5 && midpoint->getY() == 2 && edge.getId() == 19;
      edge.DetachVertices();
    } else {
      Face face(&a, &b, &c, 23);
      face.h = 0.5;
      auto* midpoint = face.getMid();
      const bool caught = inject_allocation_failure(ordinal, [&] { face.setVertices(&b, &c, &d); });
      unchanged = unchanged && caught && face.getV1() == &a && face.getV2() == &b &&
                  face.getV3() == &c && face.getMid() == midpoint && midpoint->getX() == 1 &&
                  midpoint->getY() == 7.0 / 3.0 && face.h == 0.5 && face.getId() == 23;
      face.DetachVertices();
    }
  }
  std::printf("allocation_failure_sites=%s-cache:%d/%d unchanged=%d\n", is_edge ? "edge" : "face",
              total, total, unchanged ? 1 : 0);
  require(unchanged,
          "failed replacement preserves endpoints, cache identity/geometry and scalar state");
}

void tree_allocation_failures(int stage) {
  int total = 0;
  {
    TreeFixture fixture(stage);
    const int before = fixture.tree->getNumCells();
    total = measure_allocations([&] { tree_operation(fixture, stage); });
    if (stage == 4)
      require(fixture.tree->getNumCells() > before, "measured neighbor refinement subdivides");
  }
  require(total > 0, "tree sweep has positive measured allocation coverage");
  std::printf("tree_measured=%d:%d\n", stage, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    TreeFixture fixture(stage);
    std::printf("tree_inject=%d:%d\n", stage, ordinal);
    require(inject_allocation_failure(ordinal, [&] { tree_operation(fixture, stage); }),
            "every tree allocation denial reaches caller");
    // Only destruction is permitted after failed generation/subdivision.
  }
  std::printf("tree_failure_sites=%d:%d/%d\n", stage, total, total);
}

void boundary_registration_failures(int mode) {
  auto prepare = [mode] {
    auto boundary = std::make_unique<Boundary>();
    if (mode > 0) {
      boundary->addVertex(0, 0, nullptr);
      boundary->addVertex(1, 0, nullptr);
    }
    if (mode == 2)
      boundary->addVertex(0, 1, nullptr);
    return boundary;
  };
  auto operation = [mode](Boundary& boundary) {
    if (mode == 2)
      boundary.close(nullptr);
    else
      boundary.addVertex(mode == 0 ? 0 : 0.5, mode == 0 ? 0 : 1, nullptr);
  };
  int total = 0;
  {
    auto boundary = prepare();
    total = measure_allocations([&] { operation(*boundary); });
  }
  require(total > 0, "boundary sweep has positive allocation coverage");
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    auto boundary = prepare();
    const auto vertices = boundary->getBoundary();
    const auto edges = boundary->getEdges();
    const auto vertex_id = boundary->getLastVertexId();
    const auto edge_id = boundary->getLastEdgeId();
    std::vector<EdgeSet> adjacency;
    for (auto* vertex : vertices)
      adjacency.push_back(vertex->getAdjacentEdges());
    require(inject_allocation_failure(ordinal, [&] { operation(*boundary); }),
            "boundary allocation failure reaches caller");
    bool unchanged = vertices == boundary->getBoundary() && edges == boundary->getEdges() &&
                     vertex_id == boundary->getLastVertexId() &&
                     edge_id == boundary->getLastEdgeId();
    std::size_t index = 0;
    for (auto* vertex : vertices)
      unchanged = (adjacency[index++] == vertex->getAdjacentEdges()) && unchanged;
    registration_check(unchanged,
                       "failed boundary registration preserves owners, IDs and adjacency");
    if (unchanged) {
      operation(*boundary);
      registration_check(boundary->getLastVertexId() == vertex_id + (mode == 2 ? 0 : 1) &&
                             boundary->getLastEdgeId() == edge_id + (mode == 0 ? 0 : 1),
                         "retry consumes exactly the successful IDs");
      if (mode == 2)
        registration_check(boundary->getEdges().back()->getV2() == vertices.front(),
                           "failed close preserves the contour start for retry");
    }
  }
  std::printf("registration_failure_sites=boundary-%d:%d/%d unchanged=%d\n", mode, total, total,
              registration_contracts_ok ? 1 : 0);
}

void face_quality_failures() {
  Vertex a(0, 0), b(1, 0), c(0, 1);
  Face face(&a, &b, &c);
  double quality = 0.0;
  const int total = measure_allocations([&] { quality = face.quality(); });
  require(total == 0, "quality uses no temporary heap allocation");
  double denied_quality = 0.0;
  require(!inject_allocation_failure(0, [&] { denied_quality = face.quality(); }) &&
              allocation_attempts == 0 && denied_allocations == 0,
          "quality completes with the next allocation denied");
  registration_check(quality == denied_quality && face.getV1() == &a && face.getV2() == &b &&
                         face.getV3() == &c && a.getX() == 0 && b.getX() == 1 && c.getY() == 1,
                     "nonallocating quality retains value and caller endpoint geometry");
  face.DetachVertices();
  allocation_hook_control();
  std::puts("face_quality_nonallocating calls=2 allocations=0 hook_detected=1 unchanged=1");
}

std::unique_ptr<TransferFront> prepare_registration_stage(int stage) {
  auto front = std::make_unique<TransferFront>();
  square(*front->getBoundary());
  auto* tree = front->getQuadtree();
  tree->setFactor(0.85);
  // Match AdvancingFront's generate/refine sequence; execute adds uniform refinement.
  require(tree->generate({}) == QUAD_INITIAL_TREE_DONE, "registration source quadtree builds");
  require(tree->refineAccordingToNeighbors() == QUAD_REFINE_ACCORDING_TO_NEIGHBORS_DONE,
          "registration source neighbors refine");
  // Match the production template wrapper's boundary ID initialization.
  for (long i = 0; i < front->getBoundary()->getLastVertexId(); ++i)
    tree->vertexId();
  for (long i = 0; i < front->getBoundary()->getLastEdgeId(); ++i)
    tree->edgeId();
  tree->getRoot()->sortNeighbors();
  if (stage > 0)
    tree->getRoot()->makeOuterVertices();
  if (stage > 1)
    tree->getRoot()->makeOuterEdges();
  return front;
}

QuadtreeCell* registration_leaf(Quadtree* tree, int type) {
  for (auto* leaf : tree->getLeaves()) {
    if (leaf->inBoundary())
      continue;
    int total = 0;
    int sizes[4]{};
    for (int side = 0; side < 4; ++side) {
      sizes[side] = static_cast<int>(leaf->getNeighbors(side).size());
      total += sizes[side];
    }
    if ((type == 1 && total == 4) || (type == 4 && total == 6 && sizes[QUAD_B] != sizes[QUAD_T]))
      return leaf;
  }
  require(false, "actual prepared quadtree has requested template type");
  return nullptr;
}

void template_registration_failures(int stage) {
  auto operation = [stage](TransferFront& front, QuadtreeCell* leaf) {
    if (stage == 0)
      front.getQuadtree()->getRoot()->makeOuterVertices();
    else if (stage == 1)
      front.getQuadtree()->getRoot()->makeOuterEdges();
    else
      leaf->makeTemplateBasedMesh();
  };
  int total = 0;
  const int type = stage == 2 ? 1 : 4;
  {
    auto front = prepare_registration_stage(stage);
    auto* leaf = stage > 1 ? registration_leaf(front->getQuadtree(), type) : nullptr;
    total = measure_allocations([&] { operation(*front, leaf); });
    if (stage > 1)
      require(front->getQuadtree()->GetTemplateStats().template_count[type - 1] == 1,
              "exactly one requested real template is measured");
  }
  require(total > 0, "template/outer sweep has positive measured allocation coverage");
  std::printf("registration_measured=template-%d:%d\n", stage, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    auto front = prepare_registration_stage(stage);
    auto* leaf = stage > 1 ? registration_leaf(front->getQuadtree(), type) : nullptr;
    std::printf("registration_inject=template-%d:%d\n", stage, ordinal);
    require(inject_allocation_failure(ordinal, [&] { operation(*front, leaf); }),
            "template allocation failure reaches caller");
    // Failed trees are qualified for destruction, not retry or observer consumption.
  }
  std::printf("registration_failure_sites=template-%d:%d/%d\n", stage, total, total);
}

#endif

void scenario(const char* mode) {
  if (std::strcmp(mode, "normal") == 0)
    normal(false);
  else if (std::strcmp(mode, "transfer-contract") == 0)
    normal(true);
  else if (std::strcmp(mode, "failure") == 0)
    failed(0);
  else if (std::strcmp(mode, "exception") == 0)
    failed(1);
  else if (std::strcmp(mode, "topology-failure") == 0)
    failed(2);
  else if (std::strcmp(mode, "pending-tree") == 0)
    pending_tree();
  else if (std::strcmp(mode, "transfer-order") == 0)
    transfer_order();
  else if (std::strcmp(mode, "midpoint-alias") == 0)
    midpoint_alias();
  else if (std::strcmp(mode, "face-alias-cache") == 0)
    face_alias_cache();
  else if (std::strcmp(mode, "primitive-contracts") == 0)
    primitive_contracts();
  else if (std::strcmp(mode, "angle-contracts") == 0)
    angle_contracts();
  else if (std::strcmp(mode, "parametric-contracts") == 0)
    parametric_contracts();
  else if (std::strcmp(mode, "curve-allocation-observation") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    curve_allocation_observation();
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strncmp(mode, "parametric-failure-", 19) == 0 && std::strlen(mode) == 20 &&
             mode[19] >= '0' && mode[19] <= '9') {
#if defined(_MSC_VER) && defined(_DEBUG)
    parametric_allocation_failures(mode[19] - '0');
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strncmp(mode, "angle-failure-", 14) == 0 && std::strlen(mode) == 15 &&
             mode[14] >= '0' && mode[14] <= '9') {
#if defined(_MSC_VER) && defined(_DEBUG)
    angle_allocation_failures(mode[14] - '0');
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "registration-contracts") == 0)
    registration_contracts();
  else if (std::strcmp(mode, "tree-contracts") == 0)
    tree_contracts();
  else if (std::strncmp(mode, "tree-failure-", 13) == 0 && std::strlen(mode) == 14 &&
           mode[13] >= '0' && mode[13] <= '4') {
#if defined(_MSC_VER) && defined(_DEBUG)
    tree_allocation_failures(mode[13] - '0');
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "unowned-edge-query") == 0)
    unowned_cell_query(false);
  else if (std::strcmp(mode, "unowned-face-query") == 0)
    unowned_cell_query(true);
  else if (std::strcmp(mode, "unowned-cell-contracts") == 0) {
    unowned_cell_query(false);
    unowned_cell_query(true);
  } else if (std::strcmp(mode, "partial") == 0) {
    int destroyed = 0;
    partial(destroyed).reset();
    require(destroyed == 3, "shared endpoints destroyed exactly once by front");
  } else if (std::strcmp(mode, "teardown-allocation") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    allocation_free_teardown();
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "allocation-hook-control") == 0 ||
             std::strcmp(mode, "transfer-allocation-failure") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(mode, "allocation-hook-control") == 0)
      allocation_hook_control();
    else
      transfer_allocation_failure();
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "edge-construction-failure") == 0 ||
             std::strcmp(mode, "face-construction-failure") == 0 ||
             std::strcmp(mode, "front-construction-failure") == 0 ||
             std::strcmp(mode, "edge-cache-failure") == 0 ||
             std::strcmp(mode, "face-cache-failure") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(mode, "edge-construction-failure") == 0)
      edge_construction_failures();
    else if (std::strcmp(mode, "face-construction-failure") == 0)
      face_construction_failures();
    else if (std::strcmp(mode, "front-construction-failure") == 0)
      construction_failures("front", [] { AdvancingFront front; });
    else
      cache_replacement_failures(std::strcmp(mode, "edge-cache-failure") == 0);
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "boundary-first-failure") == 0 ||
             std::strcmp(mode, "boundary-append-failure") == 0 ||
             std::strcmp(mode, "boundary-close-failure") == 0 ||
             std::strcmp(mode, "face-quality-failure") == 0 ||
             std::strcmp(mode, "outer-vertex-failure") == 0 ||
             std::strcmp(mode, "outer-edge-failure") == 0 ||
             std::strcmp(mode, "template-one-failure") == 0 ||
             std::strcmp(mode, "template-four-failure") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(mode, "boundary-first-failure") == 0)
      boundary_registration_failures(0);
    else if (std::strcmp(mode, "boundary-append-failure") == 0)
      boundary_registration_failures(1);
    else if (std::strcmp(mode, "boundary-close-failure") == 0)
      boundary_registration_failures(2);
    else if (std::strcmp(mode, "face-quality-failure") == 0)
      face_quality_failures();
    else
      template_registration_failures(
          std::strcmp(mode, "outer-vertex-failure") == 0
              ? 0
              : (std::strcmp(mode, "outer-edge-failure") == 0
                     ? 1
                     : (std::strcmp(mode, "template-one-failure") == 0 ? 2 : 3)));
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* vertex = new Vertex(1, 2);
    delete vertex;
    std::printf("expired-x=%g\n", vertex->getX());
  } else if (std::strcmp(mode, "shared-delete") == 0) {
    auto* shared = new Vertex(0, 0);
    auto* first = new Edge(shared, new Vertex(1, 0));
    auto* second = new Edge(shared, new Vertex(0, 1));
    delete first;
    delete second;
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new Vertex(1, 2)));
  } else
    require(false, "unknown scenario");
}
} // namespace

int main(int argc, char** argv) {
  require(argc == 2, "one scenario required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
#endif
  std::puts("UV lifetime diagnostic");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_ERROR, _CRTDBG_FILE_STDERR);
  _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_ASSERT, _CRTDBG_FILE_STDERR);
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int repetition = 0; repetition < 10; ++repetition) {
      for (const auto* mode :
           {"normal", "partial", "failure", "exception", "topology-failure", "pending-tree"})
        scenario(mode);
    }
    scenario("transfer-contract");
    scenario("transfer-order");
    scenario("midpoint-alias");
  } else
    scenario(argv[1]);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  if (delta.lCounts[_NORMAL_BLOCK] != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    return 1;
  }
#endif
  if (!registration_contracts_ok)
    return 1;
  std::puts("PASS");
}
