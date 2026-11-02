#ifndef APMESH_APPLICATION_GENERATION_CONTEXT_H
#define APMESH_APPLICATION_GENERATION_CONTEXT_H

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
};
} // namespace apmesh::application

#endif
