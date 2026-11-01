#ifndef APMESH_APPLICATION_RUNTIME_CONFIG_H
#define APMESH_APPLICATION_RUNTIME_CONFIG_H

#include "application/runtime_state.h"
#include "application/generation_context.h"

namespace apmesh::application {
struct RuntimeConfig {
  int num_processes = 1;
  int num_threads = 1;
  std::string input_model;
  std::string write_mode = "h";
  std::string output_prefix;
  std::string use_template = "n";
  std::string adaptive_mode = "adaptive_stable";
  double adaptive_intensity = 0.45;
  double adaptive_quality_priority = 0.75;
  int adaptive_max_iterations = 6;
  double adaptive_target_growth = 1.6;
  double epsylon = EPSYLON;
  double min_improvement = MIN_IMPROVEMENT;
  int patience = PATIENCE;
  double tol_local = TOL_LOCAL;
  double smoothing_laplacian_number = SMOOTHING_LAPLACIAN_NUMBER;
  double smoothing_laplacian_factor = SMOOTHING_LAPLACIAN_FACTOR;
  double adaptation_relaxation = ADAPTATION_RELAXATION;
  double adaptation_max_delta = ADAPTATION_MAX_DELTA;
  int adaptive_retry_count = 0;
  double adaptive_retry_shrink = 1.0;
  double patch_factor_min = PATCH_FACTOR_MIN;
  double patch_factor_max = PATCH_FACTOR_MAX;
  double patch_refinement_strength = 0.22;
  double patch_coarsening_strength = PATCH_COARSENING_STRENGTH;
  int curve_adaptation_policy = CURVE_ADAPTATION_POLICY;
  double curve_adaptation_blend = CURVE_ADAPTATION_BLEND;
  double curve_factor_sensitivity = CURVE_FACTOR_SENSITIVITY;
  int curve_point_budget_mode = CURVE_POINT_BUDGET_MODE;
  double curve_point_growth_step1 = CURVE_POINT_GROWTH_STEP1;
  double curve_point_growth_stepn = CURVE_POINT_GROWTH_STEPN;
  double curve_point_budget_blend = CURVE_POINT_BUDGET_BLEND;
  int curve_point_min = CURVE_POINT_MIN;
  int curve_point_max = CURVE_POINT_MAX;
  double quadtree_face_quality_threshold = QUADTREE_FACE_QUALITY_THRESHOLD;
  double quadtree_low_quality_h_factor = QUADTREE_LOW_QUALITY_H_FACTOR;
  int aft_local_postprocess_passes = AFT_LOCAL_POSTPROCESS_PASSES;
  double aft_local_postprocess_quality_threshold = AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD;
  double aft_local_postprocess_blend = AFT_LOCAL_POSTPROCESS_BLEND;
  double step2_eligible_refinement_damp = 0.65;
  int patch_quadtree_depth_step1 = 5;
  int patch_quadtree_depth_stepn = 4;
  double patch_quadtree_min_h_scale = PATCH_QUADTREE_MIN_H_SCALE;
  int adapter_resolve_negative_quadtree_depth = 1;
  int enable_shared_curve_sync = 1;
  int enable_hybrid_reconstruction = 1;
  int write_runtime_summary = 1;
};

RuntimeConfig LoadRuntimeConfig(const std::string& path);
void ApplyRuntimeConfig(const RuntimeConfig& config);
GenerationContext MakeGenerationContext(const RuntimeConfig& config,
                                        std::string process_suffix = {});
} // namespace apmesh::application

#endif
