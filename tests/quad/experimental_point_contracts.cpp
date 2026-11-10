#include "experimental_point_rule.h"
#include "uv_mesh.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
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

void Require(bool condition, const char* message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

void Near(UvVertex actual, double x, double y, const char* name) {
  Require(std::abs(actual.u - x) < 1.0e-12 && std::abs(actual.v - y) < 1.0e-12, name);
}

void Reject(const std::function<void()>& operation) {
  try {
    operation();
  } catch (const std::invalid_argument&) {
    return;
  }
  throw std::runtime_error("Invalid experimental point fixture was accepted");
}

using Rule = ExperimentalPointRule;

UvVertex Apply(UvVertex value, bool reflection, int turns) {
  if (reflection) {
    value.u = 1.0 - value.u;
  }
  for (int i = 0; i < turns; ++i) {
    const double x = 1.0 - value.v;
    value.v = value.u;
    value.u = x;
  }
  return value;
}

std::vector<UvVertex> Points(const std::string& labels) {
  const std::map<char, UvVertex> values{
      {'A', {0, 0}}, {'B', {1, 0}}, {'C', {1, 1}}, {'D', {0, 1}},
      {'S', {0.5, 0}}, {'E', {1, 0.5}}, {'N', {0.5, 1}},
      {'W', {0, 0.5}}, {'O', {0.5, 0.5}}};
  std::vector<UvVertex> result;
  for (const char label : labels) {
    result.push_back(values.at(label));
  }
  return result;
}

PolygonMesh Pattern(const std::vector<std::string>& cycles, Rule rule,
                    bool reflection, int turns) {
  PolygonMesh result;
  std::map<char, apmesh::quad::VertexId> ids;
  for (const auto& labels : cycles) {
    std::vector<apmesh::quad::VertexId> polygon;
    std::vector<UvVertex> corners;
    for (const char label : labels) {
      const auto transformed = Apply(Points(std::string(1, label)).front(), reflection, turns);
      corners.push_back(transformed);
      const auto found = ids.find(label);
      if (found == ids.end()) {
        ids.emplace(label, result.vertices.size());
        result.vertices.push_back(transformed);
      }
      polygon.push_back(ids.at(label));
    }
    if (reflection) {
      std::reverse(corners.begin(), corners.end());
      std::reverse(polygon.begin(), polygon.end());
    }
    result.interior_points.push_back(ExperimentalInteriorPoint(corners, rule));
    result.polygons.push_back(std::move(polygon));
  }
  return result;
}

} // namespace

int main() {
  std::size_t cases = 0;
  try {
    const auto check = [&](const std::function<void()>& operation) {
      operation();
      ++cases;
    };
    const auto mean = Rule::VertexArithmeticMean;
    const auto area = Rule::PolygonAreaCentroid;
    check([&] {
      Near(ExperimentalInteriorPoint(Points("ABOW"), mean), 3.0 / 8, 1.0 / 4,
           "T2 vertex mean differs from independent rational oracle");
      Near(ExperimentalInteriorPoint(Points("ABOW"), area), 7.0 / 18, 2.0 / 9,
           "T2 area centroid differs from independent rational oracle");
      Near(ExperimentalInteriorPoint(Points("WSND"), mean), 1.0 / 4, 5.0 / 8,
           "T5 vertex mean differs from independent rational oracle");
      Near(ExperimentalInteriorPoint(Points("WSND"), area), 5.0 / 18, 11.0 / 18,
           "T5 area centroid differs from independent rational oracle");
    });
    const std::array<std::vector<std::string>, 6> cycles{{
        {"ABCD"}, {"ABOW", "BCO", "WOCD"}, {"ABOW", "WOND", "OBCN"},
        {"ABEW", "WECD"}, {"ASW", "WSND", "SBCN"},
        {"ASOW", "SBEO", "OECN", "WOND"}}};
    const std::array<std::size_t, 6> counts{{4, 11, 12, 8, 11, 16}};
    for (std::size_t pattern = 0; pattern < cycles.size(); ++pattern) {
      for (bool reflection : {false, true}) {
        for (int turns = 0; turns < 4; ++turns) {
          for (Rule rule : {mean, area}) {
            check([&] {
              auto source = Pattern(cycles[pattern], rule, reflection, turns);
              const auto result = apmesh::quad::Subdivide(source);
              Require(result.quads.size() == counts[pattern],
                      "Selected research witness changed Figure 7 quad count");
              apmesh::quad::Validate(result, 1.0L);
              for (const auto& polygon : source.polygons) {
                std::vector<UvVertex> face;
                for (auto id : polygon) {
                  face.push_back(source.vertices[id]);
                }
                const auto chosen = ExperimentalInteriorPoint(face, rule);
                const auto transformed = ExperimentalInteriorPoint(
                    Points(cycles[pattern][&polygon - &source.polygons[0]]), rule);
                const auto expected = Apply(transformed, reflection, turns);
                Near(chosen, expected.u, expected.v, "D4 equivariance failed");
              }
            });
          }
        }
      }
    }
    check([&] {
      auto shifted = Points("ABOW");
      for (auto& point : shifted) {
        point.u = 2.0 * point.u + 17.0;
        point.v = 2.0 * point.v - 11.0;
      }
      for (const Rule rule : {mean, area}) {
        const auto old_point = ExperimentalInteriorPoint(Points("ABOW"), rule);
        const auto new_point = ExperimentalInteriorPoint(shifted, rule);
        Near(new_point, old_point.u * 2.0 + 17.0, old_point.v * 2.0 - 11.0,
             "Affine scale/translation equivariance failed");
      }
    });
    check([&] {
      for (Rule rule : {mean, area}) {
        Reject([&] { ExperimentalInteriorPoint({}, rule); });
        Reject([&] { ExperimentalInteriorPoint(Points("AAW"), rule); });
        Reject([&] { ExperimentalInteriorPoint(Points("ABCD"), rule, 0.0L); });
        Reject([&] { ExperimentalInteriorPoint(Points("ABCD"), rule, -1.0L); });
        Reject([&] { ExperimentalInteriorPoint(Points("ABCD"), rule, 1.0L); });
        Reject([&] { ExperimentalInteriorPoint(Points("ABCD"), rule,
                           std::numeric_limits<long double>::quiet_NaN()); });
        auto clockwise = Points("ABOW");
        std::reverse(clockwise.begin(), clockwise.end());
        Reject([&] { ExperimentalInteriorPoint(clockwise, rule); });
        auto invalid = Points("ABOW");
        invalid[1].u = std::numeric_limits<double>::infinity();
        Reject([&] { ExperimentalInteriorPoint(invalid, rule); });
        invalid = Points("ABOW");
        invalid[1].v = std::numeric_limits<double>::quiet_NaN();
        Reject([&] { ExperimentalInteriorPoint(invalid, rule); });
        Reject([&] { ExperimentalInteriorPoint(Points("ABCD"), static_cast<Rule>(999)); });
        Reject([&] { ExperimentalInteriorPoint(Points("ABCD"),
                       rule, std::numeric_limits<long double>::infinity()); });
      }
    });
    check([&] {
      // The test API must not expose a default rule or select it implicitly.
      const auto square = Points("ABCD");
      Near(ExperimentalInteriorPoint(square, mean), 0.5, 0.5,
           "Square arithmetic mean changed");
      Near(ExperimentalInteriorPoint(square, area), 0.5, 0.5,
           "Square area centroid changed");
      const auto original = Points("ABOW");
      const auto fixed = original;
      (void)ExperimentalInteriorPoint(original, area);
      for (std::size_t i = 0; i < fixed.size(); ++i) {
        Require(original[i].u == fixed[i].u && original[i].v == fixed[i].v,
                "Experimental research selector mutated input");
      }
    });
    std::cout << "experimental_point_witnesses=" << cases << " failed=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL experimental point witness case " << cases
              << ": " << error.what() << '\n';
    return 1;
  }
}
