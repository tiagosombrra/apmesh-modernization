#ifndef APMESH_RESEARCH_QUAD_GLOBAL_OUTCOME_H
#define APMESH_RESEARCH_QUAD_GLOBAL_OUTCOME_H

#include "adapter_capture.h"

#include <array>
#include <cstddef>

namespace apmesh::quad {

// Evaluation events are not commits; transition events follow actual changes.
enum class GlobalOutcomeKind {
  ElementBudgetRejectedCandidate,
  GrowthRejectedCandidate,
  AcceptedStepCommitted,
  RejectedStepRestored
};

struct GlobalOutcomeEvent {
  OuterAttemptIdentity outer{};
  int adaptive_step = -1;
  GlobalOutcomeKind kind = GlobalOutcomeKind::ElementBudgetRejectedCandidate;
};

// Record a chronological, bounded prefix without allocation or callbacks.
// Incomplete evidence is explicitly represented by truncated().
template <std::size_t Capacity>
class BoundedGlobalOutcomeLog {
public:
  static constexpr std::size_t capacity() noexcept { return Capacity; }
  void Record(GlobalOutcomeEvent event) noexcept {
    if (size_ < Capacity) {
      entries_[size_++] = event;
    } else {
      truncated_ = true;
    }
  }
  const GlobalOutcomeEvent* data() const noexcept { return entries_.data(); }
  std::size_t size() const noexcept { return size_; }
  bool truncated() const noexcept { return truncated_; }
  void Reset() noexcept {
    size_ = 0;
    truncated_ = false;
  }
private:
  std::array<GlobalOutcomeEvent, Capacity> entries_{};
  std::size_t size_ = 0;
  bool truncated_ = false;
};

using GlobalOutcomeLog = BoundedGlobalOutcomeLog<128>;

} // namespace apmesh::quad
#endif // APMESH_RESEARCH_QUAD_GLOBAL_OUTCOME_H
