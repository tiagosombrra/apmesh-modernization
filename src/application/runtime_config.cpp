#include "application/runtime_config.h"
#include "input_output/input_validation.h"

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <unordered_map>
#include <utility>

namespace apmesh::application {
namespace {
std::string Trim(const std::string& value) {
  size_t start = 0;
  while (start < value.size() && std::isspace(static_cast<unsigned char>(value[start])) != 0) {
    ++start;
  }
  size_t end = value.size();
  while (end > start && std::isspace(static_cast<unsigned char>(value[end - 1])) != 0) {
    --end;
  }
  return value.substr(start, end - start);
}

std::unordered_map<std::string, std::string> ReadConfigFile(const std::string& path) {
  std::ifstream file(path.c_str());
  std::unordered_map<std::string, std::string> values;
  if (!file.is_open()) {
    throw std::runtime_error("Cannot open configuration: " + path);
  }
  std::string line;
  while (std::getline(file, line)) {
    const std::string trimmed = Trim(line);
    if (trimmed.empty() || trimmed[0] == '#') {
      continue;
    }
    const size_t equal_pos = trimmed.find('=');
    if (equal_pos == std::string::npos) {
      throw std::runtime_error("Expected KEY=VALUE in configuration: " + trimmed);
    }
    const std::string key = Trim(trimmed.substr(0, equal_pos));
    const std::string value = Trim(trimmed.substr(equal_pos + 1));
    apmesh::io::ValidateConfigValue(key, value);
    if (!values.emplace(key, value).second) {
      throw std::runtime_error("Duplicate configuration key: " + key);
    }
  }
  if (file.bad()) {
    throw std::runtime_error("Cannot read configuration: " + path);
  }
  return values;
}

std::string GetConfigValue(const std::unordered_map<std::string, std::string>& values,
                           const std::string& key, const std::string& fallback = "") {
  const auto it = values.find(key);
  return (it != values.end()) ? it->second : fallback;
}

} // namespace

RuntimeConfig LoadRuntimeConfig(const std::string& path) {
  const auto values = ReadConfigFile(path);
  RuntimeConfig config;
  config.num_processes = std::max(1, atoi(GetConfigValue(values, "NUM_PROCESSES", "1").c_str()));
  config.num_threads = std::max(1, atoi(GetConfigValue(values, "NUM_THREADS", "1").c_str()));
  config.input_model = GetConfigValue(values, "INPUT_MODEL");
  config.write_mode = GetConfigValue(values, "WRITE_MODE", "h");
  config.output_prefix = GetConfigValue(values, "OUTPUT_PREFIX");
  config.use_template = GetConfigValue(values, "USE_TEMPLATE", "y");
  config.adaptive_mode = GetConfigValue(values, "ADAPTIVE_MODE", "adaptive_stable");
  config.adaptive_intensity = atof(GetConfigValue(values, "ADAPTIVE_INTENSITY", "0.45").c_str());
  config.adaptive_quality_priority =
      atof(GetConfigValue(values, "ADAPTIVE_QUALITY_PRIORITY", "0.75").c_str());
  const std::string max_iterations = GetConfigValue(
      values, "ADAPTIVE_MAX_ITERATIONS", GetConfigValue(values, "ADAPTIVE_MAX_STEPS", "6"));
  config.adaptive_max_iterations = std::max(2, atoi(max_iterations.c_str()));
  config.adaptive_target_growth =
      atof(GetConfigValue(values, "ADAPTIVE_TARGET_GROWTH", "1.6").c_str());
  config.epsylon = atof(GetConfigValue(values, "EPSYLON", "0.0000001").c_str());
  config.min_improvement = atof(GetConfigValue(values, "MIN_IMPROVEMENT", "0.01").c_str());
  config.patience = std::max(1, atoi(GetConfigValue(values, "PATIENCE", "2").c_str()));
  config.tol_local = atof(GetConfigValue(values, "TOL_LOCAL", "0.0000001").c_str());
  config.smoothing_laplacian_number =
      atof(GetConfigValue(values, "SMOOTHING_LAPLACIAN_NUMBER", "7").c_str());
  config.smoothing_laplacian_factor =
      atof(GetConfigValue(values, "SMOOTHING_LAPLACIAN_FACTOR", "0.5").c_str());
  config.adaptation_relaxation =
      atof(GetConfigValue(values, "ADAPTATION_RELAXATION", "1.0").c_str());
  config.adaptation_max_delta =
      atof(GetConfigValue(values, "ADAPTATION_MAX_DELTA", "0.10").c_str());
  config.adaptive_retry_count =
      std::max(0, atoi(GetConfigValue(values, "ADAPTIVE_RETRY_COUNT", "0").c_str()));
  config.adaptive_retry_shrink =
      atof(GetConfigValue(values, "ADAPTIVE_RETRY_SHRINK", "1.0").c_str());
  config.patch_factor_min = atof(GetConfigValue(values, "PATCH_FACTOR_MIN", "0.80").c_str());
  config.patch_factor_max = atof(GetConfigValue(values, "PATCH_FACTOR_MAX", "1.12").c_str());
  config.patch_refinement_strength =
      atof(GetConfigValue(values, "PATCH_REFINEMENT_STRENGTH", "0.22").c_str());
  config.patch_coarsening_strength =
      atof(GetConfigValue(values, "PATCH_COARSENING_STRENGTH", "0.10").c_str());
  config.curve_adaptation_policy =
      atoi(GetConfigValue(values, "CURVE_ADAPTATION_POLICY", "0").c_str());
  config.curve_adaptation_blend =
      atof(GetConfigValue(values, "CURVE_ADAPTATION_BLEND", "0.75").c_str());
  config.curve_factor_sensitivity =
      atof(GetConfigValue(values, "CURVE_FACTOR_SENSITIVITY", "1.0").c_str());
  config.curve_point_budget_mode =
      atoi(GetConfigValue(values, "CURVE_POINT_BUDGET_MODE", "0").c_str());
  config.curve_point_growth_step1 =
      atof(GetConfigValue(values, "CURVE_POINT_GROWTH_STEP1", "2.5").c_str());
  config.curve_point_growth_stepn =
      atof(GetConfigValue(values, "CURVE_POINT_GROWTH_STEPN", "1.4").c_str());
  config.curve_point_budget_blend =
      atof(GetConfigValue(values, "CURVE_POINT_BUDGET_BLEND", "0.7").c_str());
  config.curve_point_min =
      std::max(2, atoi(GetConfigValue(values, "CURVE_POINT_MIN", "2").c_str()));
  config.curve_point_max = std::max(config.curve_point_min,
                                    atoi(GetConfigValue(values, "CURVE_POINT_MAX", "128").c_str()));
  config.quadtree_face_quality_threshold =
      atof(GetConfigValue(values, "QUADTREE_FACE_QUALITY_THRESHOLD", "0.0").c_str());
  config.quadtree_low_quality_h_factor =
      atof(GetConfigValue(values, "QUADTREE_LOW_QUALITY_H_FACTOR", "1.0").c_str());
  config.aft_local_postprocess_passes =
      std::max(0, atoi(GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_PASSES", "0").c_str()));
  config.aft_local_postprocess_quality_threshold =
      atof(GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD", "0.35").c_str());
  config.aft_local_postprocess_blend =
      atof(GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_BLEND", "0.35").c_str());
  config.step2_eligible_refinement_damp =
      atof(GetConfigValue(values, "STEP2_ELIGIBLE_REFINEMENT_DAMP", "0.65").c_str());
  config.patch_quadtree_depth_step1 = std::max(
      0, std::min(32, atoi(GetConfigValue(values, "PATCH_QUADTREE_DEPTH_STEP1", "5").c_str())));
  config.patch_quadtree_depth_stepn = std::max(
      0, std::min(32, atoi(GetConfigValue(values, "PATCH_QUADTREE_DEPTH_STEPN", "4").c_str())));
  config.patch_quadtree_min_h_scale =
      atof(GetConfigValue(values, "PATCH_QUADTREE_MIN_H_SCALE", "1.0").c_str());
  config.adapter_resolve_negative_quadtree_depth =
      atoi(GetConfigValue(values, "ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH", "1").c_str()) != 0 ? 1
                                                                                                : 0;
  config.enable_shared_curve_sync =
      atoi(GetConfigValue(values, "ENABLE_SHARED_CURVE_SYNC", "1").c_str()) != 0 ? 1 : 0;
  config.enable_hybrid_reconstruction =
      atoi(GetConfigValue(values, "ENABLE_HYBRID_RECONSTRUCTION", "1").c_str()) != 0 ? 1 : 0;
  config.write_runtime_summary =
      atoi(GetConfigValue(values, "WRITE_RUNTIME_SUMMARY", "1").c_str()) != 0 ? 1 : 0;

  if (config.input_model.empty() || config.output_prefix.empty()) {
    throw std::runtime_error("INPUT_MODEL and OUTPUT_PREFIX are required");
  }

  config.adaptive_intensity = std::max(0.0, std::min(1.0, config.adaptive_intensity));
  config.adaptive_quality_priority = std::max(0.0, std::min(1.0, config.adaptive_quality_priority));
  config.adaptive_target_growth = std::max(1.0, config.adaptive_target_growth);
  config.adaptation_relaxation = std::max(0.0, std::min(1.0, config.adaptation_relaxation));
  config.adaptation_max_delta = std::max(0.0, config.adaptation_max_delta);
  config.adaptive_retry_shrink = std::max(0.05, std::min(1.0, config.adaptive_retry_shrink));
  config.patch_factor_min = std::max(0.1, config.patch_factor_min);
  config.patch_factor_max = std::max(config.patch_factor_min, config.patch_factor_max);
  config.patch_refinement_strength = std::max(0.0, std::min(1.0, config.patch_refinement_strength));
  config.patch_coarsening_strength = std::max(0.0, std::min(1.0, config.patch_coarsening_strength));
  config.curve_adaptation_blend = std::max(0.0, std::min(1.0, config.curve_adaptation_blend));
  config.curve_factor_sensitivity = std::max(0.0, config.curve_factor_sensitivity);
  config.curve_point_growth_step1 = std::max(1.0, config.curve_point_growth_step1);
  config.curve_point_growth_stepn = std::max(1.0, config.curve_point_growth_stepn);
  config.curve_point_budget_blend = std::max(0.0, std::min(1.0, config.curve_point_budget_blend));
  config.quadtree_face_quality_threshold =
      std::max(0.0, std::min(1.0, config.quadtree_face_quality_threshold));
  config.quadtree_low_quality_h_factor =
      std::max(0.1, std::min(1.5, config.quadtree_low_quality_h_factor));
  config.aft_local_postprocess_quality_threshold =
      std::max(0.0, std::min(1.0, config.aft_local_postprocess_quality_threshold));
  config.aft_local_postprocess_blend =
      std::max(0.0, std::min(1.0, config.aft_local_postprocess_blend));
  config.patch_quadtree_min_h_scale =
      std::max(0.5, std::min(1.5, config.patch_quadtree_min_h_scale));
  config.step2_eligible_refinement_damp =
      std::max(0.0, std::min(1.0, config.step2_eligible_refinement_damp));
  return config;
}

void ApplyRuntimeConfig(const RuntimeConfig& config) {
  INPUT_MODEL = config.input_model;
  WRITE_MESH = config.write_mode;
  NAME_MODEL = config.output_prefix;
  USE_TEMPLATE = config.use_template;
  EPSYLON = config.epsylon;
  MIN_IMPROVEMENT = config.min_improvement;
  PATIENCE = config.patience;
  TOL_LOCAL = config.tol_local;
  SMOOTHING_LAPLACIAN_NUMBER = std::max(5.0, std::min(7.0, config.smoothing_laplacian_number));
  SMOOTHING_LAPLACIAN_FACTOR = config.smoothing_laplacian_factor;
  ADAPTATION_RELAXATION = config.adaptation_relaxation;
  ADAPTATION_MAX_DELTA = config.adaptation_max_delta;
  ADAPTIVE_MODE = config.adaptive_mode;
  ADAPTIVE_INTENSITY = config.adaptive_intensity;
  ADAPTIVE_QUALITY_PRIORITY = config.adaptive_quality_priority;
  ADAPTIVE_MAX_STEPS = config.adaptive_max_iterations;
  ADAPTIVE_TARGET_GROWTH = config.adaptive_target_growth;
  ADAPTIVE_RETRY_COUNT = config.adaptive_retry_count;
  ADAPTIVE_RETRY_SHRINK = config.adaptive_retry_shrink;
  PATCH_FACTOR_MIN = config.patch_factor_min;
  PATCH_FACTOR_MAX = config.patch_factor_max;
  PATCH_REFINEMENT_STRENGTH = config.patch_refinement_strength;
  PATCH_COARSENING_STRENGTH = config.patch_coarsening_strength;
  CURVE_ADAPTATION_POLICY = config.curve_adaptation_policy;
  CURVE_ADAPTATION_BLEND = config.curve_adaptation_blend;
  CURVE_FACTOR_SENSITIVITY = config.curve_factor_sensitivity;
  CURVE_POINT_BUDGET_MODE = config.curve_point_budget_mode;
  CURVE_POINT_GROWTH_STEP1 = config.curve_point_growth_step1;
  CURVE_POINT_GROWTH_STEPN = config.curve_point_growth_stepn;
  CURVE_POINT_BUDGET_BLEND = config.curve_point_budget_blend;
  CURVE_POINT_MIN = config.curve_point_min;
  CURVE_POINT_MAX = config.curve_point_max;
  QUADTREE_FACE_QUALITY_THRESHOLD = config.quadtree_face_quality_threshold;
  QUADTREE_LOW_QUALITY_H_FACTOR = config.quadtree_low_quality_h_factor;
  AFT_LOCAL_POSTPROCESS_PASSES = config.aft_local_postprocess_passes;
  AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = config.aft_local_postprocess_quality_threshold;
  AFT_LOCAL_POSTPROCESS_BLEND = config.aft_local_postprocess_blend;
  STEP2_ELIGIBLE_REFINEMENT_DAMP = config.step2_eligible_refinement_damp;
  PATCH_QUADTREE_DEPTH_STEP1 = config.patch_quadtree_depth_step1;
  PATCH_QUADTREE_DEPTH_STEPN = config.patch_quadtree_depth_stepn;
  PATCH_QUADTREE_MIN_H_SCALE = config.patch_quadtree_min_h_scale;
  ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH = config.adapter_resolve_negative_quadtree_depth;
  ENABLE_SHARED_CURVE_SYNC = config.enable_shared_curve_sync;
  ENABLE_HYBRID_RECONSTRUCTION = config.enable_hybrid_reconstruction;
  WRITE_RUNTIME_SUMMARY = config.write_runtime_summary;
  if (ENABLE_HYBRID_RECONSTRUCTION == 0) {
    USE_TEMPLATE = "n";
  }
}
GenerationContext MakeGenerationContext(const RuntimeConfig& config, std::string process_suffix) {
  return {config.input_model,
          config.output_prefix,
          config.write_mode,
          std::move(process_suffix),
          AdaptivePolicyConfig{config.adaptive_mode, config.adaptive_max_iterations, STEPS,
                               config.adaptive_intensity, config.adaptive_quality_priority,
                               config.adaptive_target_growth},
          StopRetryConfig{config.epsylon, config.min_improvement, config.patience, config.tol_local,
                          config.adaptive_retry_count, config.adaptive_retry_shrink,
                          MAX_RETRY_ELEMENT_GROWTH_FACTOR, MAX_RETRY_ELEMENT_GROWTH_ABS,
                          ERROR_FLOOR, MIN_ERROR_DROP_ABS, MIN_ERROR_DROP_PER_ELEMENT},
          AdaptationConfig{config.adaptation_relaxation, config.adaptation_max_delta,
                           config.patch_factor_min, config.patch_factor_max},
          ElementBudgetConfig{STEP_ELEMENT_BUDGET_MODE,
                              STEP_ELEMENT_BUDGET_ABS,
                              STEP_ELEMENT_BUDGET_GROWTH_FACTOR,
                              STEP_ELEMENT_BUDGET_SOFT_RATIO,
                              STEP_ELEMENT_BUDGET_RETRY_SHRINK_TOPK,
                              STEP_ELEMENT_BUDGET_RETRY_H_SCALE,
                              STEP_ELEMENT_BUDGET_RETRY_FACTOR_RANGE_SCALE,
                              STEP_ELEMENT_BUDGET_PRESSURE_MODE,
                              STEP_ELEMENT_BUDGET_PRESSURE_START,
                              STEP_ELEMENT_BUDGET_PRESSURE_H_SCALE,
                              STEP_ELEMENT_BUDGET_PRESSURE_FACTOR_SHRINK,
                              PATCH_LOCAL_ELEMENT_BUDGET_MODE,
                              PATCH_LOCAL_ELEMENT_BUDGET_BASE,
                              PATCH_LOCAL_ELEMENT_BUDGET_SCALE_BY_RANK,
                              PATCH_LOCAL_ELEMENT_BUDGET_SCALE_BY_EFFICIENCY,
                              PATCH_LOCAL_BUDGET_H_SCALE,
                              PATCH_LOCAL_BUDGET_HARD_CAP,
                              STEP_TARGET_ELEMENT_GROWTH_MODE,
                              STEP2_TARGET_ELEMENT_GROWTH,
                              STEP3PLUS_TARGET_ELEMENT_GROWTH,
                              STEP_TARGET_GROWTH_H_SCALE,
                              BUDGET_DRIVEN_ADAPTATION,
                              STEP_ELEMENT_TARGET_MODE,
                              STEP1_TARGET_ELEMENT_GROWTH,
                              STEP_ELEMENT_TARGET_MIN,
                              STEP_ELEMENT_TARGET_MAX,
                              PATCH_BUDGET_ALLOCATION_MODE,
                              PATCH_BUDGET_ERROR_WEIGHT,
                              PATCH_BUDGET_EFFICIENCY_WEIGHT,
                              PATCH_BUDGET_QUALITY_WEIGHT,
                              PATCH_BUDGET_MIN_SHARE,
                              PATCH_BUDGET_TOPK_ONLY_MODE},
          CurveControlsConfig{config.curve_adaptation_policy, config.curve_adaptation_blend,
                              config.curve_factor_sensitivity, STEP2_CURVE_SENSITIVITY_SCALE,
                              CURVE_EFFICIENCY_WEIGHT, config.curve_point_budget_mode,
                              config.curve_point_growth_step1, config.curve_point_growth_stepn,
                              config.curve_point_budget_blend, config.curve_point_min,
                              config.curve_point_max, CURVE_CONSISTENCY_MODE,
                              CURVE_CONSISTENCY_MAX_POINT_RATIO_STEP2,
                              CURVE_CONSISTENCY_PRIORITY_BONUS, CURVE_CONSISTENCY_GROUP_BLEND,
                              DISCRETIZATION_CURVE_FACTOR, DISCRETIZATION_CURVE_FACTOR_INTERNAL}};
}
} // namespace apmesh::application
