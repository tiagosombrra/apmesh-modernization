#ifndef APMESH_QUAD_RESEARCH_MIXED_EPOCH_ADMISSION_H
#define APMESH_QUAD_RESEARCH_MIXED_EPOCH_ADMISSION_H

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace apmesh::quad::research {

// Metadata-only preflight. This never publishes a SubMesh or certifies adaptation.
struct MixedEpochReceipt {
  std::uint64_t epoch = 0;
  std::string model_sha256;
  std::string boundary_sha256;
  std::string parent_mesh_sha256;
  std::string mesh_sha256;
  std::string topology_sha256;
  std::string policy_id;
  std::size_t physical_nodes = 0;
  std::size_t quadrilaterals = 0;
  std::size_t triangles = 0;
  std::size_t source_boundary_edges = 0;
  std::size_t real_tree_edits = 0;
  double normalized_error = 0.0;
  double min_signed_corner_jacobian = 0.0;
  double min_physical_area = 0.0;
  bool independent_oracle_pass = false;
  bool actual_native_aft_pass = false;
};

inline bool IsSha256(const std::string& value) {
  if (value.size() != 64)
    return false;
  for (const char c : value)
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')))
      return false;
  return true;
}

class MixedEpochPreflight final {
 public:
  // The initial receipt is an input baseline, not an adaptive epoch.
  explicit MixedEpochPreflight(MixedEpochReceipt initial) {
    ValidateReceipt(initial);
    if (initial.epoch != 0 || !initial.parent_mesh_sha256.empty() ||
        initial.real_tree_edits != 0)
      throw std::invalid_argument("Initial mixed receipt must be epoch zero");
    history_.push_back(std::move(initial));
  }

  const MixedEpochReceipt& Latest() const noexcept { return history_.back(); }
  std::size_t RecordedStates() const noexcept { return history_.size(); }

  // This is a gate for provenance and demonstrable change, not a numerical
  // research policy. A caller must independently establish scientific validity.
  void AdmitCandidate(const MixedEpochReceipt& candidate, bool inject_precommit_failure = false) {
    ValidateReceipt(candidate);
    const auto& previous = history_.back();
    if (candidate.epoch != previous.epoch + 1)
      throw std::invalid_argument("Noncontiguous mixed epoch index");
    if (candidate.model_sha256 != previous.model_sha256 ||
        candidate.boundary_sha256 != previous.boundary_sha256 ||
        candidate.source_boundary_edges != previous.source_boundary_edges)
      throw std::invalid_argument("Source model or sampled boundary changed");
    if (candidate.policy_id != previous.policy_id)
      throw std::invalid_argument("Mixed epoch policy changed without a new experiment");
    if (candidate.parent_mesh_sha256 != previous.mesh_sha256)
      throw std::invalid_argument("Candidate does not identify previous mixed owner");
    if (candidate.mesh_sha256 == previous.mesh_sha256 ||
        candidate.topology_sha256 == previous.topology_sha256)
      throw std::invalid_argument("Cloned or unchanged candidate is not a new epoch");
    if (candidate.real_tree_edits == 0)
      throw std::invalid_argument("No actual quadtree edit was recorded");
    if (candidate.normalized_error >= previous.normalized_error)
      throw std::invalid_argument("Experimental monotone-error witness did not improve");
    if (inject_precommit_failure)
      throw std::runtime_error("Injected precommit epoch metadata failure");
    // A copyable receipt offers the strong exception guarantee of vector push.
    // No physical observer pointers or output files are changed by this gate.
    history_.push_back(candidate);
  }

 private:
  static void ValidateReceipt(const MixedEpochReceipt& receipt) {
    if (!IsSha256(receipt.model_sha256) || !IsSha256(receipt.boundary_sha256) ||
        !IsSha256(receipt.mesh_sha256) || !IsSha256(receipt.topology_sha256) ||
        (!receipt.parent_mesh_sha256.empty() && !IsSha256(receipt.parent_mesh_sha256)))
      throw std::invalid_argument("Invalid mixed epoch SHA-256 identity");
    if (receipt.policy_id.empty() || receipt.physical_nodes == 0 ||
        receipt.triangles == 0 || receipt.quadrilaterals == 0 ||
        receipt.source_boundary_edges == 0 || !receipt.independent_oracle_pass ||
        !receipt.actual_native_aft_pass)
      throw std::invalid_argument("Incomplete typed mixed epoch evidence");
    if (!std::isfinite(receipt.normalized_error) || receipt.normalized_error < 0.0 ||
        !std::isfinite(receipt.min_signed_corner_jacobian) ||
        !(receipt.min_signed_corner_jacobian > 0.0) ||
        !std::isfinite(receipt.min_physical_area) || !(receipt.min_physical_area > 0.0))
      throw std::invalid_argument("Invalid typed mixed physical metric");
  }

  std::vector<MixedEpochReceipt> history_;
};

}  // namespace apmesh::quad::research
#endif  // APMESH_QUAD_RESEARCH_MIXED_EPOCH_ADMISSION_H
