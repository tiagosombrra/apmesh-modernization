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

// Value-owned identity/output options and an optional adaptive-policy snapshot.
struct GenerationContext {
  std::string input_model;
  std::string output_prefix;
  std::string write_mode;
  std::string process_suffix;
  // Absence preserves live legacy policy reads for identity-only callers.
  std::optional<AdaptivePolicyConfig> adaptive_policy = std::nullopt;
};
} // namespace apmesh::application

#endif
