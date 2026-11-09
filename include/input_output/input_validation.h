#ifndef APMESH_INPUT_OUTPUT_INPUT_VALIDATION_H
#define APMESH_INPUT_OUTPUT_INPUT_VALIDATION_H

#include <cmath>
#include <fstream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_set>

namespace apmesh::io {

/**
 * @brief Reject unsupported or malformed configuration values before legacy conversion.
 * @param key An exact, case-sensitive configuration key.
 * @param value A trimmed, nonempty value.
 * @throws std::runtime_error For unknown keys, invalid numbers, or invalid CLI modes.
 * @note Existing finite-value clamping policies remain in LoadRuntimeConfig.
 */
inline void ValidateConfigValue(const std::string& key, const std::string& value) {
  static const std::unordered_set<std::string> strings = {
      "INPUT_MODEL",   "OUTPUT_PREFIX", "WRITE_MODE", "USE_TEMPLATE", "MESH_ELEMENT_KIND",
      "ADAPTIVE_MODE", "BUILD_DIR",     "EXECUTABLE"};
  static const std::unordered_set<std::string> integers = {
      "NUM_PROCESSES",
      "NUM_THREADS",
      "ADAPTIVE_MAX_ITERATIONS",
      "ADAPTIVE_MAX_STEPS",
      "ADAPTIVE_RETRY_COUNT",
      "ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH",
      "AFT_LOCAL_POSTPROCESS_PASSES",
      "CURVE_ADAPTATION_POLICY",
      "CURVE_POINT_BUDGET_MODE",
      "CURVE_POINT_MIN",
      "CURVE_POINT_MAX",
      "ENABLE_HYBRID_RECONSTRUCTION",
      "ENABLE_SHARED_CURVE_SYNC",
      "PATCH_QUADTREE_DEPTH_STEP1",
      "PATCH_QUADTREE_DEPTH_STEPN",
      "PATIENCE",
      "WRITE_RUNTIME_SUMMARY"};
  static const std::unordered_set<std::string> numbers = {"ADAPTATION_MAX_DELTA",
                                                          "ADAPTATION_RELAXATION",
                                                          "ADAPTIVE_INTENSITY",
                                                          "ADAPTIVE_QUALITY_PRIORITY",
                                                          "ADAPTIVE_RETRY_SHRINK",
                                                          "ADAPTIVE_TARGET_GROWTH",
                                                          "AFT_LOCAL_POSTPROCESS_BLEND",
                                                          "AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD",
                                                          "CURVE_ADAPTATION_BLEND",
                                                          "CURVE_FACTOR_SENSITIVITY",
                                                          "CURVE_POINT_BUDGET_BLEND",
                                                          "CURVE_POINT_GROWTH_STEP1",
                                                          "CURVE_POINT_GROWTH_STEPN",
                                                          "EPSYLON",
                                                          "MIN_IMPROVEMENT",
                                                          "PATCH_COARSENING_STRENGTH",
                                                          "PATCH_FACTOR_MAX",
                                                          "PATCH_FACTOR_MIN",
                                                          "PATCH_QUADTREE_MIN_H_SCALE",
                                                          "PATCH_REFINEMENT_STRENGTH",
                                                          "QUADTREE_FACE_QUALITY_THRESHOLD",
                                                          "QUADTREE_LOW_QUALITY_H_FACTOR",
                                                          "SMOOTHING_LAPLACIAN_FACTOR",
                                                          "SMOOTHING_LAPLACIAN_NUMBER",
                                                          "STEP2_ELIGIBLE_REFINEMENT_DAMP",
                                                          "TOL_LOCAL"};
  if (value.empty()) {
    throw std::runtime_error("Empty configuration value for " + key);
  }
  if (strings.count(key) != 0U) {
    if ((key == "WRITE_MODE" && value != "m" && value != "q" && value != "h") ||
        (key == "USE_TEMPLATE" && value != "y" && value != "n") ||
        (key == "MESH_ELEMENT_KIND" && value != "tri" && value != "quad_uv")) {
      throw std::runtime_error("Unsupported configuration value for " + key + ": " + value);
    }
    return;
  }
  try {
    std::size_t consumed = 0;
    if (integers.count(key) != 0U) {
      const long long number = std::stoll(value, &consumed);
      if (consumed != value.size() || number < std::numeric_limits<int>::min() ||
          number > std::numeric_limits<int>::max() ||
          ((key == "NUM_PROCESSES" || key == "NUM_THREADS") && number < 1)) {
        throw std::invalid_argument("Invalid integer or process/thread count");
      }
    } else if (numbers.count(key) != 0U) {
      const double number = std::stod(value, &consumed);
      if (consumed != value.size() || !std::isfinite(number)) {
        throw std::invalid_argument("Expected a finite number");
      }
    } else {
      throw std::runtime_error("Unknown configuration key: " + key);
    }
  } catch (const std::invalid_argument&) {
    throw std::runtime_error("Invalid numeric configuration value for " + key + ": " + value);
  } catch (const std::out_of_range&) {
    throw std::runtime_error("Out-of-range configuration value for " + key + ": " + value);
  }
}

/**
 * @brief Check the supported indexed bicubic BP grammar without changing geometry.
 * @param path Input path resolved using the historical working-directory rule.
 * @throws std::runtime_error If reading fails or any record is malformed.
 * @note Coordinates and zero-based control indices retain their original order.
 *       No degeneracy, welding, curvature or tolerance policy is introduced.
 */
inline void ValidateBezierPatchInput(const std::string& path) {
  std::ifstream input(path);
  if (!input.is_open()) {
    throw std::runtime_error("Cannot open model input: " + path);
  }
  std::size_t vertices = 0;
  std::size_t patches = 0;
  std::size_t line_number = 0;
  std::string line;
  while (std::getline(input, line)) {
    ++line_number;
    const auto first = line.find_first_not_of(" \t\r");
    if (first == std::string::npos || line.compare(first, 2, "//") == 0 || line[first] == '#') {
      continue;
    }
    const auto fail = [&](const std::string& reason) {
      throw std::runtime_error("Invalid model " + path + ":" + std::to_string(line_number) + ": " +
                               reason);
    };
    // The historical reader recognizes records only at the start of a line.
    if (first != 0U) {
      fail("v/p records must begin in column 1");
    }
    std::istringstream record(line);
    std::string kind;
    record >> kind;
    if (kind == "v") {
      double x = 0.0;
      double y = 0.0;
      double z = 0.0;
      if (!(record >> x >> y >> z) || !std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z)) {
        fail("a vertex requires exactly three finite coordinates");
      }
      ++vertices;
    } else if (kind == "p") {
      for (int index = 0; index < 16; ++index) {
        long long vertex = 0;
        if (!(record >> vertex) || vertex < 0 ||
            static_cast<unsigned long long>(vertex) >= vertices) {
          fail("a patch requires 16 valid zero-based indices of preceding vertices");
        }
      }
      ++patches;
    } else {
      fail("unsupported record: " + kind);
    }
    record >> std::ws;
    std::string tail;
    std::getline(record, tail);
    if (!tail.empty() && tail[0] != '#' && tail.compare(0, 2, "//") != 0) {
      fail("unexpected trailing data");
    }
  }
  if (input.bad() || (!input.eof() && input.fail())) {
    throw std::runtime_error("Cannot read model input: " + path);
  }
  if (vertices == 0U || patches == 0U) {
    throw std::runtime_error("Model input contains no complete bicubic patch: " + path);
  }
}

} // namespace apmesh::io

#endif
