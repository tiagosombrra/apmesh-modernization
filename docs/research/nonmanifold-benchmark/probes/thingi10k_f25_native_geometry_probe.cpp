// Exercise the ORIGINAL linked APMesh BP reader and Geometry curve observers.
// This probe does not create a triangle/quad mesh or modify the production engine.
#include "data/curve/curve_adaptive.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/geometry.h"
#include "data/patch/patch_coons.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <map>
#include <sstream>
#include <vector>
#include <cstddef>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <sys/resource.h>

namespace {
using Clock = std::chrono::steady_clock;

std::size_t Count(const char* text) {
  const std::string raw(text);
  if (raw.empty() || raw[0] == '-' || raw[0] == '+')
    throw std::invalid_argument("A count must be a nonnegative integer");
  std::size_t consumed = 0;
  const unsigned long long parsed = std::stoull(raw, &consumed, 10);
  if (consumed != raw.size() || parsed > std::numeric_limits<std::size_t>::max())
    throw std::invalid_argument("Invalid expected count");
  return static_cast<std::size_t>(parsed);
}

void Require(bool success, const char* message) {
  if (!success)
    throw std::runtime_error(message);
}

struct Summary {
  std::size_t patches = 0;
  std::size_t curves = 0;
  std::size_t boundary_curves = 0;
  std::size_t shared_curves = 0;
  std::size_t nonmanifold_curves = 0;
  std::size_t observed_sides = 0;
  std::size_t matched_control_sides = 0;
  std::size_t reversed_control_sides = 0;
};

using Point3 = std::array<double, 3>;
using ControlSide = std::array<double, 12>;
using PatchNet = std::array<Point3, 16>;

std::vector<PatchNet> ReadIndependentBp(const char* filename) {
  std::ifstream stream(filename);
  Require(stream.good(), "Cannot independently open original-model BP");
  std::vector<Point3> points;
  std::vector<PatchNet> patches;
  std::string line;
  while (std::getline(stream, line)) {
    std::istringstream row(line);
    std::string kind;
    row >> kind;
    Require(kind == "v" || kind == "p", "Original BP contains unexpected row type");
    if (kind == "v") {
      Point3 point{};
      for (auto& value : point)
        Require(static_cast<bool>(row >> value) && std::isfinite(value),
                "Malformed control point in independent BP reader");
      points.push_back(point);
      Require(points.size() <= 100000, "Original BP control limit exceeded");
    } else {
      PatchNet patch{};
      for (auto& point : patch) {
        unsigned long long index = 0;
        Require(static_cast<bool>(row >> index) && index < points.size(),
                "Malformed patch index in independent BP reader");
        point = points[static_cast<std::size_t>(index)];
      }
      patches.push_back(patch);
      Require(patches.size() <= 10000, "Original BP patch limit exceeded");
    }
    std::string tail;
    Require(!(row >> tail), "Unexpected extra BP columns");
  }
  Require(stream.eof() && !patches.empty(), "Incomplete original BP rows");
  return patches;
}

ControlSide Controls(const PatchNet& patch, unsigned int side) {
  // Same bottom/right/top/left orientation used by original ReaderFilePatches.
  constexpr unsigned int indexes[4][4] = {
      {0, 1, 2, 3}, {3, 7, 11, 15}, {12, 13, 14, 15}, {0, 4, 8, 12}};
  Require(side < 4, "Invalid patch side index");
  ControlSide flat{};
  for (unsigned int i = 0; i < 4; ++i) {
    for (unsigned int axis = 0; axis < 3; ++axis)
      flat[i * 3 + axis] = patch[indexes[side][i]][axis];
  }
  return flat;
}

ControlSide Reverse(const ControlSide& controls) {
  ControlSide result{};
  for (unsigned int point = 0; point < 4; ++point)
    for (unsigned int axis = 0; axis < 3; ++axis)
      result[3 * point + axis] = controls[3 * (3 - point) + axis];
  return result;
}

ControlSide Stored(const CurveAdaptiveParametricBezier& curve) {
  const std::array<PointAdaptive, 4> points = {
      curve.GetPoint0(), curve.GetPoint1(), curve.GetPoint2(), curve.GetPoint3()};
  ControlSide flat{};
  for (unsigned int i = 0; i < 4; ++i) {
    flat[3 * i] = points[i].GetX();
    flat[3 * i + 1] = points[i].GetY();
    flat[3 * i + 2] = points[i].GetZ();
  }
  return flat;
}

Summary VerifyOriginalGeometry(Geometry& geometry, const std::vector<PatchNet>& source) {
  Summary summary;
  summary.patches = geometry.GetNumberPatches();
  summary.curves = geometry.GetNumberCurves();
  Require(summary.patches > 0 && summary.curves > 0, "No native geometry was created");
  Require(source.size() == summary.patches, "Native model has unexpected source patch count");
  std::map<ControlSide, CurveAdaptive*> source_to_native_curve;

  std::unordered_map<CurveAdaptive*, std::unordered_set<Patch*>> incident;
  incident.reserve(summary.curves);
  for (std::size_t patch_id = 0; patch_id < summary.patches; ++patch_id) {
    Patch* patch = geometry.GetPatch(static_cast<unsigned int>(patch_id));
    auto* coons = dynamic_cast<PatchCoons*>(patch);
    auto* original_bezier = dynamic_cast<PatchBezier*>(patch);
    Require(coons != nullptr && original_bezier != nullptr,
            "Original reader constructed a non-Bezier patch");
    Require(coons->GetNumBerCurves() == 4, "Patch does not contain four curves");
    for (unsigned int side = 0; side < 4; ++side) {
      CurveAdaptive* curve = coons->GetCurve(side);
      Require(curve != nullptr, "Null curve in produced patch");
      auto* original_curve = dynamic_cast<CurveAdaptiveParametricBezier*>(curve);
      Require(original_curve != nullptr, "Original patch contains a non-Bezier curve");
      const ControlSide wanted = Controls(source[patch_id], side);
      const ControlSide actual = Stored(*original_curve);
      const bool forward = (actual == wanted);
      const bool reversed = (actual == Reverse(wanted));
      Require(forward != reversed,
              "Original native curve controls do not match one unambiguous BP side");
      Require(original_bezier->IsCurveReversed(side) == reversed,
              "Native patch orientation flag contradicts its stored curve controls");
      const ControlSide key = std::min(wanted, Reverse(wanted));
      const auto [source_it, source_inserted] = source_to_native_curve.emplace(key, curve);
      Require(source_inserted || source_it->second == curve,
              "One original input boundary was split into distinct runtime curves");
      ++summary.matched_control_sides;
      if (reversed)
        ++summary.reversed_control_sides;
      const bool fresh = incident[curve].insert(patch).second;
      Require(fresh, "A patch references the same curve more than once");
      ++summary.observed_sides;
    }
  }
  Require(incident.size() == summary.curves, "Geometry stores orphan or untracked curves");
  Require(source_to_native_curve.size() == summary.curves,
          "Distinct input curves were improperly merged in native Geometry");
  Require(summary.observed_sides == summary.patches * 4,
          "Patch-side incidence total does not equal 4 * patches");

  std::size_t observer_incidence_total = 0;
  for (std::size_t curve_id = 0; curve_id < summary.curves; ++curve_id) {
    CurveAdaptive* curve = geometry.GetCurve(static_cast<unsigned int>(curve_id));
    Require(curve != nullptr, "Null curve stored in Geometry");
    auto it = incident.find(curve);
    Require(it != incident.end(), "Geometry curve does not appear in patch sides");
    const std::size_t uses = it->second.size();
    observer_incidence_total += uses;
    const auto observer_count = curve->GetNumBerPatches();
    Require(observer_count == uses, "Curve observer count differs from actual patch use");
    std::unordered_set<Patch*> observed;
    for (unsigned int k = 0; k < observer_count; ++k) {
      Patch* patch = curve->GetPatch(k);
      Require(it->second.count(patch) != 0, "Foreign/stale patch in curve observer list");
      Require(observed.insert(patch).second, "Duplicated patch observer");
    }
    if (uses == 1)
      ++summary.boundary_curves;
    else if (uses == 2)
      ++summary.shared_curves;
    else
      ++summary.nonmanifold_curves;
  }
  Require(summary.boundary_curves + summary.shared_curves +
              summary.nonmanifold_curves == summary.curves,
          "Curve class counts are inconsistent");
  Require(observer_incidence_total == summary.observed_sides,
          "Native curve observers disagree with patch-side incidence count");
  return summary;
}
}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 6)
      throw std::invalid_argument(
          "Usage: native_geometry_probe model.bp patches curves boundary shared");
    const std::size_t expected_patches = Count(argv[2]);
    const std::size_t expected_curves = Count(argv[3]);
    const std::size_t expected_boundary = Count(argv[4]);
    const std::size_t expected_shared = Count(argv[5]);
    Require(expected_patches > 0 && expected_curves > 0,
            "Expected geometry counts must be positive");
    Require(expected_boundary + expected_shared == expected_curves,
            "Expected boundary/shared counts do not partition the curves");
    Require(expected_boundary + 2 * expected_shared == 4 * expected_patches,
            "Expected curve incidences do not equal 4 * patches");
    const auto start = Clock::now();
    const std::vector<PatchNet> original_controls = ReadIndependentBp(argv[1]);
    const auto parsed = Clock::now();
    Geometry geometry;
    PatchReader reader;
    const auto native_start = Clock::now();
    reader.ReaderFilePatches(&geometry, argv[1]);
    const auto loaded = Clock::now();
    const Summary actual = VerifyOriginalGeometry(geometry, original_controls);
    const auto verified = Clock::now();
    Require(actual.patches == expected_patches, "Unexpected native patch count");
    Require(actual.curves == expected_curves, "Unexpected native curve count");
    Require(actual.boundary_curves == expected_boundary, "Unexpected boundary count");
    Require(actual.shared_curves == expected_shared, "Unexpected shared-curve count");
    Require(actual.nonmanifold_curves == 0, "Unintended native non-manifold curves");
    const auto parse_ms = std::chrono::duration<double, std::milli>(parsed - start).count();
    const auto load_ms = std::chrono::duration<double, std::milli>(loaded - native_start).count();
    const auto verify_ms = std::chrono::duration<double, std::milli>(verified - loaded).count();
    struct rusage usage{};
    Require(getrusage(RUSAGE_SELF, &usage) == 0, "Cannot read native resource usage");
    Require(usage.ru_maxrss > 0, "Native peak RSS observation missing");
    std::cout << "{\"schema\":\"apmesh-s40-f25-native-geometry-v1\","
              << "\"result\":\"PASS\","
              << "\"patches\":" << actual.patches << ","
              << "\"curves\":" << actual.curves << ","
              << "\"boundary\":" << actual.boundary_curves << ","
              << "\"shared\":" << actual.shared_curves << ","
              << "\"nonmanifold\":" << actual.nonmanifold_curves << ","
              << "\"sides\":" << actual.observed_sides << ","
              << "\"matched_control_sides\":" << actual.matched_control_sides << ","
              << "\"reversed_control_sides\":" << actual.reversed_control_sides << ","
              << "\"parse_ms\":" << parse_ms << ","
              << "\"load_ms\":" << load_ms << ","
              << "\"verify_ms\":" << verify_ms << ","
              << "\"peak_rss_kib\":" << usage.ru_maxrss << "}\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "F25 native Geometry gate failed: " << error.what() << "\n";
    return 2;
  }
}
