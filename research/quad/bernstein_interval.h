#ifndef APMESH_RESEARCH_QUAD_BERNSTEIN_INTERVAL_H
#define APMESH_RESEARCH_QUAD_BERNSTEIN_INTERVAL_H

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <limits>
#include <stdexcept>

namespace apmesh::quad::interval {

// Research-only outward-rounded arithmetic on finite IEEE-754 doubles.
// This is conditional on strict, correctly rounded basic operations without
// fast-math. It is not a guarantee about transcendental or GPU operations.
struct Bound {
  double lo = 0.0;
  double hi = 0.0;
};

inline double Down(double value) {
  if (!std::isfinite(value))
    throw std::invalid_argument("Bernstein interval arithmetic overflow");
  return std::nextafter(value, -std::numeric_limits<double>::infinity());
}

inline double Up(double value) {
  if (!std::isfinite(value))
    throw std::invalid_argument("Bernstein interval arithmetic overflow");
  return std::nextafter(value, std::numeric_limits<double>::infinity());
}

inline Bound Exact(double value) {
  if (!std::isfinite(value))
    throw std::invalid_argument("Nonfinite Bernstein input");
  return {value, value};
}

inline Bound Add(Bound a, Bound b) {
  return {Down(a.lo + b.lo), Up(a.hi + b.hi)};
}

inline Bound Negate(Bound x) { return {-x.hi, -x.lo}; }
inline Bound Sub(Bound a, Bound b) { return Add(a, Negate(b)); }

inline Bound Mul(Bound a, Bound b) {
  const std::array<double, 4> values{
      a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi};
  for (double value : values)
    if (!std::isfinite(value))
      throw std::invalid_argument("Nonfinite Bernstein product");
  const auto mm = std::minmax_element(values.begin(), values.end());
  return {Down(*mm.first), Up(*mm.second)};
}

inline Bound Div(Bound a, Bound b) {
  if (!(b.lo > 0.0 || b.hi < 0.0))
    throw std::invalid_argument("Bernstein interval denominator contains zero");
  const std::array<double, 4> values{
      a.lo / b.lo, a.lo / b.hi, a.hi / b.lo, a.hi / b.hi};
  for (double value : values)
    if (!std::isfinite(value))
      throw std::invalid_argument("Nonfinite Bernstein quotient");
  const auto mm = std::minmax_element(values.begin(), values.end());
  return {Down(*mm.first), Up(*mm.second)};
}

inline unsigned Binomial(unsigned degree, unsigned k) {
  if (k > degree || degree > 8U)
    throw std::invalid_argument("Unsupported Bernstein polynomial degree");
  k = std::min(k, degree - k);
  unsigned result = 1U;
  for (unsigned i = 1U; i <= k; ++i)
    result = result * (degree + 1U - i) / i;
  return result;
}

template <std::size_t A, std::size_t B>
std::array<Bound, A + B - 1U> Product(
    const std::array<Bound, A>& left,
    const std::array<Bound, B>& right) {
  static_assert(A > 0U && B > 0U && A + B <= 10U);
  std::array<Bound, A + B - 1U> result{};
  for (std::size_t k = 0; k < result.size(); ++k) {
    Bound coefficient = Exact(0.0);
    for (std::size_t i = 0; i < A; ++i) {
      if (k < i || k - i >= B) continue;
      const std::size_t j = k - i;
      const auto numerator = Binomial(static_cast<unsigned>(A - 1U),
                                      static_cast<unsigned>(i)) *
                             Binomial(static_cast<unsigned>(B - 1U),
                                      static_cast<unsigned>(j));
      const auto denominator = Binomial(
          static_cast<unsigned>(A + B - 2U), static_cast<unsigned>(k));
      coefficient = Add(coefficient,
          Mul(Mul(left[i], right[j]),
              Div(Exact(static_cast<double>(numerator)),
                  Exact(static_cast<double>(denominator)))));
    }
    result[k] = coefficient;
  }
  return result;
}

struct Vector3 {
  std::array<Bound, 3> xyz{};
};

inline Vector3 Difference(Vector3 a, Vector3 b) {
  Vector3 result;
  for (std::size_t d = 0; d < 3U; ++d)
    result.xyz[d] = Sub(a.xyz[d], b.xyz[d]);
  return result;
}

inline Vector3 Scale(Vector3 a, Bound scalar) {
  Vector3 result;
  for (std::size_t d = 0; d < 3U; ++d)
    result.xyz[d] = Mul(a.xyz[d], scalar);
  return result;
}

template <std::size_t N>
std::array<Bound, N> Component(
    const std::array<Vector3, N>& values, std::size_t axis) {
  std::array<Bound, N> result{};
  for (std::size_t i = 0; i < N; ++i)
    result[i] = values[i].xyz[axis];
  return result;
}

// T is the quadratic source-curve derivative. Each R is the cubic
// displacement between a shared patch edge and a fixed inward parametric
// offset. T dot (R_a cross R_b) is a degree-eight scalar polynomial.
// Projection of R onto the tangent-normal plane does not change its sign.
inline std::array<Bound, 9> OrientationPolynomial(
    const std::array<Vector3, 3>& tangent,
    const std::array<Vector3, 4>& first,
    const std::array<Vector3, 4>& second) {
  std::array<Bound, 9> output{};
  for (std::size_t axis = 0; axis < 3U; ++axis) {
    const std::size_t a = (axis + 1U) % 3U;
    const std::size_t b = (axis + 2U) % 3U;
    const auto p = Product(Component(first, a), Component(second, b));
    const auto q = Product(Component(first, b), Component(second, a));
    std::array<Bound, 7> cross{};
    for (std::size_t k = 0; k < 7U; ++k)
      cross[k] = Sub(p[k], q[k]);
    const auto contribution = Product(Component(tangent, axis), cross);
    for (std::size_t k = 0; k < 9U; ++k)
      output[k] = Add(output[k], contribution[k]);
  }
  return output;
}

// de Casteljau: every intermediate operation is outward enclosed.
template <std::size_t N>
struct SplitResult {
  std::array<Bound, N> left{};
  std::array<Bound, N> right{};
};

template <std::size_t N>
SplitResult<N> Split(const std::array<Bound, N>& source, Bound t) {
  if (t.lo < 0.0 || t.hi > 1.0)
    throw std::invalid_argument("Bernstein subdivision parameter outside unit interval");
  auto row = source;
  SplitResult<N> result;
  result.left[0] = row[0];
  result.right[N - 1U] = row[N - 1U];
  const Bound complementary = Sub(Exact(1.0), t);
  for (std::size_t level = 1U; level < N; ++level) {
    for (std::size_t i = 0; i < N - level; ++i)
      row[i] = Add(Mul(complementary, row[i]),
                   Mul(t, row[i + 1U]));
    result.left[level] = row[0];
    result.right[N - 1U - level] = row[N - 1U - level];
  }
  return result;
}

// Clipping a polynomial to an original source interval is not sampling.
template <std::size_t N>
std::array<Bound, N> Restrict(
    const std::array<Bound, N>& source, double a, double b) {
  if (!std::isfinite(a) || !std::isfinite(b) ||
      a < 0.0 || b > 1.0 || !(a < b))
    throw std::invalid_argument("Invalid original Bernstein source interval");
  auto restricted = source;
  if (a > 0.0) restricted = Split(restricted, Exact(a)).right;
  if (b < 1.0) {
    const Bound relative = Div(Sub(Exact(b), Exact(a)),
                               Sub(Exact(1.0), Exact(a)));
    restricted = Split(restricted, relative).left;
  }
  return restricted;
}

struct SignResult {
  std::size_t positive_leaves = 0;
  std::size_t negative_leaves = 0;
  std::size_t unresolved_leaves = 0;
  double smallest_positive_lower = std::numeric_limits<double>::infinity();
  bool strictly_positive = false;
};

// No sample-based acceptance or arbitrary epsilon. A positive Bernstein
// convex-hull lower bound admits the WHOLE closed interval; at budget
// exhaustion the answer is explicitly inconclusive, never a fabricated pass.
template <std::size_t N>
void CheckPositive(const std::array<Bound, N>& coefficients,
                   unsigned depth, SignResult& result) {
  double min_lower = std::numeric_limits<double>::infinity();
  double max_upper = -std::numeric_limits<double>::infinity();
  for (const auto& coefficient : coefficients) {
    min_lower = std::min(min_lower, coefficient.lo);
    max_upper = std::max(max_upper, coefficient.hi);
  }
  if (min_lower > 0.0) {
    ++result.positive_leaves;
    result.smallest_positive_lower =
        std::min(result.smallest_positive_lower, min_lower);
    return;
  }
  if (max_upper < 0.0) {
    ++result.negative_leaves;
    return;
  }
  if (depth == 0U) {
    ++result.unresolved_leaves;
    return;
  }
  const auto halves = Split(coefficients, Exact(0.5));
  CheckPositive(halves.left, depth - 1U, result);
  CheckPositive(halves.right, depth - 1U, result);
}

template <std::size_t N>
SignResult CertifyPositive(const std::array<Bound, N>& polynomial,
                           double a, double b, unsigned max_depth = 10U) {
  if (max_depth > 16U)
    throw std::invalid_argument("Bernstein recursion budget exceeded");
  SignResult result;
  CheckPositive(Restrict(polynomial, a, b), max_depth, result);
  result.strictly_positive =
      result.positive_leaves > 0U &&
      result.negative_leaves == 0U &&
      result.unresolved_leaves == 0U;
  return result;
}

}  // namespace apmesh::quad::interval

#endif  // APMESH_RESEARCH_QUAD_BERNSTEIN_INTERVAL_H
