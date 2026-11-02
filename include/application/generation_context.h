#ifndef APMESH_APPLICATION_GENERATION_CONTEXT_H
#define APMESH_APPLICATION_GENERATION_CONTEXT_H

#include <cmath>
#include <optional>
#include <string>

namespace apmesh::application {
// Raw policy inputs. Derived values retain their existing formulas and clamping.
struct AdaptivePolicyConfig {
  std::string mode = "adaptive_stable";
  int adaptive_max_steps = 6;
  int legacy_max_steps = 3;
  double intensity = 0.45;
  double quality_priority = 0.75;
  double target_growth = 1.6;
};

// Raw generator stopping/retry criteria; effective retries are instance state.
struct StopRetryConfig {
  double global_error_target = 0.0000001;
  double minimum_improvement = 0.01;
  int patience = 2;
  double local_error_target = 0.0000001;
  int retry_count = 0;
  double retry_shrink = 1.0;
  double growth_factor_limit = 0.0;
  double growth_absolute_limit = 0.0;
  double error_floor = 0.0;
  double minimum_error_drop = 0.0;
  double minimum_error_drop_per_element = 0.0;
};

// Raw adaptation settings. Stable overrides and per-attempt values are instance state.
struct AdaptationConfig {
  double relaxation = 1.0;
  double max_delta = 0.20;
  double factor_min = 0.80;
  double factor_max = 1.12;
};

// Raw element-count budget controls; stable mode overrides are instance state.
struct ElementBudgetConfig {
  int step_mode = 0;
  double absolute_limit = 12000.0;
  double growth_factor = 3.0;
  double soft_ratio = 1.05;
  double retry_topk_shrink = 0.65;
  double retry_h_scale = 1.08;
  double retry_factor_range_scale = 0.75;
  int pressure_mode = 0;
  double pressure_start = 0.70;
  double pressure_h_scale = 1.06;
  double pressure_factor_shrink = 0.85;
  int patch_local_mode = 1;
  double patch_local_base = 1800.0;
  double patch_local_rank_scale = 0.75;
  double patch_local_efficiency_scale = 1.25;
  double patch_local_h_scale = 1.10;
  double patch_local_hard_cap = 2600.0;
  int target_growth_mode = 1;
  double step2_growth = 1.8;
  double step3plus_growth = 1.5;
  double target_h_scale = 1.10;
  int budget_driven = 0;
  int target_mode = 0;
  double step1_growth = 8.0;
  double target_min = 0.0;
  double target_max = 0.0;
  int patch_allocation_mode = 0;
  double patch_error_weight = 1.0;
  double patch_efficiency_weight = 0.5;
  double patch_quality_weight = 0.3;
  double patch_min_share = 0.01;
  int patch_topk_only_mode = 0;
};

// Raw curve controls. The discretization pair is stored independently.
struct CurveControlsConfig {
  int adaptation_policy = 0;
  double adaptation_blend = 0.75;
  double factor_sensitivity = 1.0;
  double step2_sensitivity_scale = 0.8;
  double efficiency_weight = 0.5;
  int point_budget_mode = 0;
  double point_growth_step1 = 2.5;
  double point_growth_stepn = 2.4;
  double point_budget_blend = 0.7;
  int point_min = 2;
  int point_max = 128;
  int consistency_mode = 0;
  double consistency_max_point_ratio_step2 = 1.5;
  int consistency_priority_bonus = 1;
  double consistency_group_blend = 0.65;
  double discretization_factor = 1.414213562;
  double internal_discretization_factor = std::sqrt(1.414213562);
};

// Quadtree limits, saturation and quality settings; effective stable state is separate.
struct QuadtreeControlsConfig {
  int saturation_mode = 0;
  double saturation_elements_threshold = 500.0;
  double saturation_efficiency_threshold = 0.001;
  double saturation_h_scale = 1.1;
  int hard_saturation_mode = 0;
  int hard_saturation_steps = 1;
  double hard_saturation_factor_min = 1.02;
  int skip_low_quality_on_saturated = 1;
  int postprocess_damp_on_saturated = 1;
  int cap_mode = 0;
  int depth_step1 = 5;
  int depth_stepn = 4;
  double min_h_scale = 1.0;
  double neighbor_relax = 1.0;
  int template_limit_mode = 0;
  int resolve_negative_depth = 1;
  double face_quality_threshold = 0.0;
  double low_quality_h_factor = 1.0;
  double template_poor_score_threshold = 0.0;
};

// Raw patch generation/refinement controls; stable adjustments are instance state.
struct PatchGenerationConfig {
  int adaptation_mode = 0;
  double refinement_strength = 0.22;
  double coarsening_strength = 0.10;
  double error_exponent = 1.35;
  double quality_weight = 0.35;
  double quality_target = 0.78;
  double quality_min_target = 0.45;
  double top_error_fraction = 1.0;
  double efficiency_weight = 0.0;
  double efficiency_target = 0.003;
  double history_blend = 0.5;
  double step2_refinement_scale = 0.75;
  double inefficient_cap = 0.98;
  int stepwise_mode = 0;
  double refinement_attenuation = 0.8;
  double top_error_fraction_scale = 0.7;
  double factor_range_shrink = 0.8;
  int hard_spatial_filter_mode = 0;
  int top_patch_count_min = 2;
  int top_patch_count_max = 6;
  double noneligible_factor_min = 1.0;
  int noneligible_force_coarsen = 1;
  double smoothing_neighbor_weight = 0.02;
  double eligible_refinement_damp = 0.65;
  double eligible_refinement_damp_on_retry = 0.50;
  double eligible_elements_threshold = 600.0;
  double eligible_h_scale = 1.12;
  int micro_refinement_mode = 0;
  double micro_relaxation_scale = 0.75;
  double micro_max_delta_scale = 0.70;
  double micro_patch_refinement_scale = 0.60;
  double micro_factor_range_scale = 0.70;
  int control_mode = 1;
  double budget_pressure_start = 0.70;
  double micro_h_scale = 1.10;
  double constrained_h_scale = 1.18;
  int top_rank_only_mode = 1;
};

// Value-owned identity/output options and optional execution configuration.
struct GenerationContext {
  std::string input_model;
  std::string output_prefix;
  std::string write_mode;
  std::string process_suffix;
  // Absence preserves live legacy policy reads for identity-only callers.
  std::optional<AdaptivePolicyConfig> adaptive_policy = std::nullopt;
  std::optional<StopRetryConfig> stop_retry = std::nullopt;
  std::optional<AdaptationConfig> adaptation = std::nullopt;
  std::optional<ElementBudgetConfig> element_budget = std::nullopt;
  std::optional<CurveControlsConfig> curves = std::nullopt;
  std::optional<QuadtreeControlsConfig> quadtree = std::nullopt;
  std::optional<PatchGenerationConfig> patch_generation = std::nullopt;
};
} // namespace apmesh::application

#endif
