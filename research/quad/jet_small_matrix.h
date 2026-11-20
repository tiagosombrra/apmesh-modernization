#ifndef APMESH_QUAD_JET_SMALL_MATRIX_H
#define APMESH_QUAD_JET_SMALL_MATRIX_H

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace apmesh::quad::research::jet {
using Point = std::array<double, 3>;
using Row = std::array<double, 6>;
inline double Dot(const Point& a, const Point& b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
inline Point Subtract(const Point& a, const Point& b) {
  return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
}
inline Point Cross(const Point& a, const Point& b) {
  return {a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]};
}
inline Point Scale(Point a, double s) {
  for (auto& x : a)
    x *= s;
  return a;
}
inline bool Finite(const Point& a) {
  return std::all_of(a.begin(), a.end(), [](double x) { return std::isfinite(x); });
}
inline double Norm(const Point& a) { return std::hypot(a[0], a[1], a[2]); }

struct Eigen3 {
  Point values{};
  std::array<Point, 3> vectors{}; // Columns, in ascending eigenvalue order.
  bool converged = false;
};

// Symmetric Jacobi eigensystem; no external matrix library or mesh dependency.
inline Eigen3 SymmetricEigen3(std::array<Point, 3> matrix) {
  auto vectors = std::array<Point, 3>{{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}};
  for (const auto& row : matrix)
    if (!Finite(row))
      throw std::invalid_argument("Nonfinite PCA covariance");
  bool converged = false;
  for (std::size_t sweep = 0; sweep < 64; ++sweep) {
    double largest = 0, magnitude = 0;
    std::size_t p = 0, q = 1;
    for (std::size_t i = 0; i < 3; ++i) {
      magnitude = std::max(magnitude, std::abs(matrix[i][i]));
      for (std::size_t j = i + 1; j < 3; ++j)
        if (std::abs(matrix[i][j]) > largest) {
          largest = std::abs(matrix[i][j]);
          p = i;
          q = j;
        }
    }
    if (largest <= std::numeric_limits<double>::epsilon() * magnitude) {
      converged = true;
      break;
    }
    const double tau = (matrix[q][q] - matrix[p][p]) / (2 * matrix[p][q]);
    const double t = std::copysign(1.0 / (std::abs(tau) + std::hypot(1.0, tau)), tau);
    const double c = 1 / std::hypot(1.0, t), s = t * c;
    const double app = matrix[p][p], aqq = matrix[q][q], apq = matrix[p][q];
    matrix[p][p] = c * c * app - 2 * c * s * apq + s * s * aqq;
    matrix[q][q] = s * s * app + 2 * c * s * apq + c * c * aqq;
    matrix[p][q] = matrix[q][p] = 0;
    for (std::size_t k = 0; k < 3; ++k) {
      if (k != p && k != q) {
        const double a = matrix[k][p], b = matrix[k][q];
        matrix[k][p] = matrix[p][k] = c * a - s * b;
        matrix[k][q] = matrix[q][k] = s * a + c * b;
      }
      const double a = vectors[p][k], b = vectors[q][k];
      vectors[p][k] = c * a - s * b;
      vectors[q][k] = s * a + c * b;
    }
  }
  std::array<std::size_t, 3> order{0, 1, 2};
  std::stable_sort(order.begin(), order.end(),
                   [&](auto a, auto b) { return matrix[a][a] < matrix[b][b]; });
  Eigen3 result;
  result.converged = converged;
  for (std::size_t k = 0; k < 3; ++k) {
    result.values[k] = matrix[order[k]][order[k]];
    result.vectors[k] = vectors[order[k]];
  }
  return result;
}

struct LeastSquares6 {
  Row coefficients{}, singular{};
  std::array<Row, 6> right{};
  std::vector<Row> orthogonal_columns;
  std::size_t rank = 0;
  double threshold = 0, residual = 0;
  double condition = std::numeric_limits<double>::infinity();
  bool converged = false;
};

// One-sided Jacobi SVD acts on the rectangular design itself, not normal equations.
inline LeastSquares6 SolveLeastSquares6(const std::vector<Row>& input,
                                        const std::vector<double>& values) {
  if (input.empty() || input.size() != values.size())
    throw std::invalid_argument("Invalid jet least-squares dimensions");
  for (const auto& row : input)
    for (double x : row)
      if (!std::isfinite(x))
        throw std::invalid_argument("Nonfinite jet design");
  for (double x : values)
    if (!std::isfinite(x))
      throw std::invalid_argument("Nonfinite jet response");
  auto columns = input;
  std::array<Row, 6> right{};
  for (std::size_t i = 0; i < 6; ++i)
    right[i][i] = 1;
  const double epsilon = std::numeric_limits<double>::epsilon();
  bool converged = false;
  for (std::size_t sweep = 0; sweep < 128; ++sweep) {
    bool rotated = false;
    for (std::size_t p = 0; p < 6; ++p)
      for (std::size_t q = p + 1; q < 6; ++q) {
        double a = 0, b = 0, ab = 0;
        for (const auto& row : columns) {
          a += row[p] * row[p];
          b += row[q] * row[q];
          ab += row[p] * row[q];
        }
        if (!std::isfinite(a) || !std::isfinite(b) || !std::isfinite(ab))
          throw std::invalid_argument("Jet SVD overflow");
        if (a == 0 || b == 0)
          continue;
        if (std::abs(ab) <= epsilon * static_cast<double>(std::max<std::size_t>(input.size(), 6)) *
                                std::sqrt(a) * std::sqrt(b))
          continue;
        const double tau = (b - a) / (2 * ab);
        const double t = std::copysign(1.0 / (std::abs(tau) + std::hypot(1.0, tau)), tau);
        const double c = 1 / std::hypot(1.0, t), s = t * c;
        for (auto& row : columns) {
          const double x = row[p], y = row[q];
          row[p] = c * x - s * y;
          row[q] = s * x + c * y;
        }
        for (auto& row : right) {
          const double x = row[p], y = row[q];
          row[p] = c * x - s * y;
          row[q] = s * x + c * y;
        }
        rotated = true;
      }
    if (!rotated) {
      converged = true;
      break;
    }
  }
  Row singular{};
  for (const auto& row : columns)
    for (std::size_t j = 0; j < 6; ++j)
      singular[j] = std::hypot(singular[j], row[j]);
  std::array<std::size_t, 6> order{0, 1, 2, 3, 4, 5};
  std::stable_sort(order.begin(), order.end(),
                   [&](auto a, auto b) { return singular[a] > singular[b]; });
  LeastSquares6 result;
  result.converged = converged;
  result.orthogonal_columns.resize(input.size());
  for (std::size_t j = 0; j < 6; ++j) {
    result.singular[j] = singular[order[j]];
    for (std::size_t i = 0; i < 6; ++i)
      result.right[i][j] = right[i][order[j]];
    for (std::size_t i = 0; i < input.size(); ++i)
      result.orthogonal_columns[i][j] = columns[i][order[j]];
  }
  result.threshold =
      static_cast<double>(std::max<std::size_t>(input.size(), 6)) * epsilon * result.singular[0];
  for (std::size_t j = 0; j < 6; ++j) {
    if (!(result.singular[j] > result.threshold))
      continue;
    ++result.rank;
    double projection = 0;
    for (std::size_t i = 0; i < input.size(); ++i)
      projection += result.orthogonal_columns[i][j] * values[i];
    projection /= result.singular[j] * result.singular[j];
    for (std::size_t i = 0; i < 6; ++i)
      result.coefficients[i] += result.right[i][j] * projection;
  }
  if (result.rank == 6)
    result.condition = result.singular[0] / result.singular[5];
  for (std::size_t i = 0; i < input.size(); ++i) {
    double fit = 0;
    for (std::size_t j = 0; j < 6; ++j)
      fit += input[i][j] * result.coefficients[j];
    result.residual = std::hypot(result.residual, fit - values[i]);
  }
  return result;
}
} // namespace apmesh::quad::research::jet
#endif
