#ifndef APMESH_GENERATOR_CURVE_SAMPLE_LIFETIME_H
#define APMESH_GENERATOR_CURVE_SAMPLE_LIFETIME_H

class Geometry;

namespace apmesh::generation {
// Own the collective lifetime of samples currently published in curve lists.
// Geometry outlives this serial scope; sample objects have no competing owner.
// Physical mesh nodes are independent copies. Inner publication/graph guards
// must unwind first and leave every surviving sample reachable in these lists.
// Unpublished allocations and metadata recovery are outside this boundary.
class CurveSampleLifetime {
public:
  explicit CurveSampleLifetime(Geometry& geometry) noexcept : geometry_(geometry) {}
  ~CurveSampleLifetime() noexcept;
  CurveSampleLifetime(const CurveSampleLifetime&) = delete;
  CurveSampleLifetime& operator=(const CurveSampleLifetime&) = delete;

  // Idempotent while the lists stay empty; never allocates, including on failure.
  void Release() noexcept;

private:
  Geometry& geometry_;
};
} // namespace apmesh::generation

#endif // APMESH_GENERATOR_CURVE_SAMPLE_LIFETIME_H
