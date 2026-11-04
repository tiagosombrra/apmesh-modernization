#ifndef APMESH_DATA_PATCH_FIND_UV_STATISTICS_H
#define APMESH_DATA_PATCH_FIND_UV_STATISTICS_H

#include <atomic>

extern std::atomic<unsigned long long> FINDUV_TOTAL_CALLS;
extern std::atomic<unsigned long long> FINDUV_IMAX_EXITS;

namespace apmesh::diagnostics {
struct FindUvStatistics {
  unsigned long long calls = 0;
  unsigned long long imax_exits = 0;
};

namespace detail {
// One same-thread observer; its scope borrows a live execution-owned value.
inline FindUvStatistics*& ActiveFindUvStatistics() noexcept {
  static thread_local FindUvStatistics* statistics = nullptr;
  return statistics;
}
} // namespace detail

// Nested scopes charge only their current owner and restore the preceding observer.
class FindUvStatisticsScope {
public:
  explicit FindUvStatisticsScope(FindUvStatistics& statistics) noexcept
      : previous_(detail::ActiveFindUvStatistics()) {
    detail::ActiveFindUvStatistics() = &statistics;
  }
  ~FindUvStatisticsScope() { detail::ActiveFindUvStatistics() = previous_; }
  FindUvStatisticsScope(const FindUvStatisticsScope&) = delete;
  FindUvStatisticsScope& operator=(const FindUvStatisticsScope&) = delete;
  FindUvStatisticsScope(FindUvStatisticsScope&&) = delete;
  FindUvStatisticsScope& operator=(FindUvStatisticsScope&&) = delete;

private:
  FindUvStatistics* previous_;
};

inline void RecordFindUvCall() noexcept {
  FINDUV_TOTAL_CALLS.fetch_add(1ULL, std::memory_order_relaxed);
  if (auto* statistics = detail::ActiveFindUvStatistics()) {
    ++statistics->calls;
  }
}

inline unsigned long long RecordFindUvImaxExit() noexcept {
  const unsigned long long hit =
      1ULL + FINDUV_IMAX_EXITS.fetch_add(1ULL, std::memory_order_relaxed);
  if (auto* statistics = detail::ActiveFindUvStatistics()) {
    ++statistics->imax_exits;
  }
  // Retain the process-wide ordinal used by the historical diagnostic throttle.
  return hit;
}
} // namespace apmesh::diagnostics

#endif
