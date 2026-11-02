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
};
} // namespace apmesh::application

#endif
