#include <algorithm>
#include "adapter/domain_generation_error.h"
#include <atomic>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/definitions.h"
#include "data/model.h"
#include "data/patch/patch_bezier.h"
#include "data/patch/patch_hermite.h"
#include "data/vector_adaptive.h"
#include "data/vertex_adaptive.h"
#include "generator/generator_adaptive.h"
#include "input_output/models_3d.h"
#include "input_output/input_validation.h"
#include "input_output/patch_reader.h"
#include "timer/timer.h"
#include "application/runtime_config.h"
#include "application/run_application.h"

using apmesh::application::ApplyRuntimeConfig;
using apmesh::application::LoadRuntimeConfig;

#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>

#include "crab_mesh/aft/boundary.h"
#include "data/curve/curve_orientation.h"
#include "serial_portability_checks.h"

namespace {
void RequireOrientation(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

double AnalyticPosition(double parameter) {
  // Cubic Bezier controls [0, 0.1, 0.4, 1] on a monotone straight physical curve.
  return 0.3 * parameter + 0.6 * parameter * parameter + 0.1 * parameter * parameter * parameter;
}

double AnalyticInverse(double position) {
  double low = 0.0, high = 1.0;
  for (int iteration = 0; iteration < 80; ++iteration) {
    const double middle = (low + high) / 2.0;
    if (AnalyticPosition(middle) < position)
      low = middle;
    else
      high = middle;
  }
  return (low + high) / 2.0;
}

void CheckConstructors() {
  std::array<PointAdaptive, 16> points;
  for (unsigned int i = 0; i < 4; ++i)
    for (unsigned int j = 0; j < 4; ++j)
      points[4 * i + j] = PointAdaptive(i / 3.0, j / 3.0, i * j / 30.0);
  for (unsigned int mask = 0; mask < 16; ++mask) {
    const auto forward = [mask](unsigned int slot) { return (mask & (1U << slot)) == 0; };
    PatchBezier patch(points[0], points[1], points[2], points[3], points[4], points[5], points[6],
                      points[7], points[8], points[9], points[10], points[11], points[12],
                      points[13], points[14], points[15], forward(0), forward(1), forward(2),
                      forward(3));
    // This legacy constructor creates curves but does not own their lifetimes.
    std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4> curves;
    for (unsigned int slot = 0; slot < curves.size(); ++slot)
      curves[slot].reset(static_cast<CurveAdaptiveParametricBezier*>(patch.GetCurve(slot)));
    PatchBezier reconstructed(curves[0].get(), curves[1].get(), curves[2].get(), curves[3].get(),
                              points[5], points[9], points[6], points[10], forward(0), forward(1),
                              forward(2), forward(3));
    PatchBezier copied(&reconstructed);
    for (unsigned int slot = 0; slot < curves.size(); ++slot) {
      RequireOrientation(patch.IsCurveReversed(slot) == !forward(slot) &&
                             reconstructed.IsCurveReversed(slot) == !forward(slot) &&
                             copied.IsCurveReversed(slot) == !forward(slot),
                         "Patch constructors lost an incidence direction");
      for (double t : {0.0, 0.125, 0.5, 0.875, 1.0}) {
        const double u = slot == 0 || slot == 2 ? t : (slot == 1 ? 1.0 : 0.0);
        const double v = slot == 1 || slot == 3 ? t : (slot == 2 ? 1.0 : 0.0);
        const auto expected = PointAdaptive(u, v, 0.3 * u * v);
        const auto actual = reconstructed.Parameterize(u, v);
        const auto stored = curves[slot]->FindPointByParameter(forward(slot) ? t : 1.0 - t);
        for (const auto& point : {actual, stored})
          RequireOrientation(std::abs(point.GetX() - expected.GetX()) < 1e-12 &&
                                 std::abs(point.GetY() - expected.GetY()) < 1e-12 &&
                                 std::abs(point.GetZ() - expected.GetZ()) < 1e-12,
                             "Patch direction changed its input surface or boundary");
      }
    }
  }
}

void CheckEdges() {
  CurveAdaptiveParametricBezier curve(PointAdaptive(0, 0, 0), PointAdaptive(0.1, 0, 0),
                                      PointAdaptive(0.4, 0, 0), PointAdaptive(1, 0, 0));
  const std::array<std::array<double, 4>, 4> sides = {
      {{0, 0, 0.5, 0}, {1, 0, 1, 0.5}, {1, 1, 0.5, 1}, {0, 1, 0, 0.5}}};
  for (unsigned int slot = 0; slot < sides.size(); ++slot) {
    for (bool reverse : {false, true}) {
      const auto& side = sides[slot];
      Par2DJMesh::Basics::Edge edge(new Par2DJMesh::Basics::Vertex(side[0], side[1]),
                                    new Par2DJMesh::Basics::Vertex(side[2], side[3]));
      edge.setCurva(&curve, reverse);
      edge.makeParamMid();
      const double first = side[slot % 2 == 0 ? 0 : 1];
      const double last = side[slot % 2 == 0 ? 2 : 3];
      const double a = reverse ? 1 - first : first;
      const double b = reverse ? 1 - last : last;
      double expected_mid = AnalyticInverse((AnalyticPosition(a) + AnalyticPosition(b)) / 2.0);
      if (reverse)
        expected_mid = 1 - expected_mid;
      const double actual_mid = slot % 2 == 0 ? edge.getMid()->getX() : edge.getMid()->getY();
      RequireOrientation(std::abs(actual_mid - expected_mid) < 1e-9,
                         "Physical arc midpoint does not respect incidence direction");
      RequireOrientation(
          std::abs(edge.getLen() - std::abs(AnalyticPosition(b) - AnalyticPosition(a))) < 1e-12,
          "Physical arc length uses the wrong parameter interval");
    }
  }

  // At a patch corner the completed edge still belongs to the preceding side.
  CurveAdaptiveParametricBezier different(PointAdaptive(0, 0, 0), PointAdaptive(0, 0, 0),
                                          PointAdaptive(0, 0, 0), PointAdaptive(1, 0, 0));
  Par2DJMesh::AFT::Boundary boundary;
  boundary.addVertex(0.0, 0.0, &curve);
  boundary.addVertex(0.5, 0.0, &curve);
  boundary.addVertex(1.0, 0.0, &different);
  const auto edges = boundary.getEdges();
  RequireOrientation(edges.size() == 2, "Boundary control did not create two edges");
  RequireOrientation(std::abs(edges.back()->getLen() - 0.6875) < 1e-12,
                     "Corner edge used the next side's physical curve");
}
} // namespace

int main(int argc, char** argv) {
  try {
    if (argc == 2 && std::string(argv[1]) == "--serial-portability")
      return apmesh::test::RunSerialPortabilityChecks();
    if (argc != 1)
      throw std::runtime_error("Unexpected probe arguments");
    // Isolated test context: the production tolerance remains unchanged.
    TOLERANCE = 1e-10;
    CheckConstructors();
    CheckEdges();
    for (double t : {0.0, 0.125, 0.5, 0.875, 1.0}) {
      const double reversed = apmesh::geometry::OrientedParameter(t, true);
      RequireOrientation(apmesh::geometry::OrientedParameter(reversed, true) == t,
                         "Parameter reversal is not an involution");
    }
    std::cout << "Sixteen constructor directions, eight physical edge orientations and the corner "
                 "control passed\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
