#include "quadratic_jet_curvature.h"

#include <iostream>
#include <string>

namespace {
using namespace apmesh::quad::research::jet;
std::size_t checks = 0;
void Check(bool ok, const char* why) {
  ++checks;
  if (!ok)
    throw std::runtime_error(why);
}
bool Close(double a, double b, double tolerance = 1e-10) { return std::abs(a - b) <= tolerance; }
void Matrices() {
  std::vector<Row> a(6);
  std::vector<double> b(6);
  for (std::size_t i = 0; i < 6; ++i) {
    a[i][i] = static_cast<double>(i + 1);
    b[i] = a[i][i] * static_cast<double>(i + 2);
  }
  auto solved = SolveLeastSquares6(a, b);
  Check(solved.converged && solved.rank == 6, "Diagonal SVD rank");
  Check(Close(solved.condition, 6), "Known diagonal condition");
  for (std::size_t i = 0; i < 6; ++i) {
    Check(Close(solved.coefficients[i], static_cast<double>(i + 2)), "Known diagonal solution");
    Check(Close(solved.singular[i], static_cast<double>(6 - i)), "Known singular values");
  }
  const Row beta{0.3, 0.2, -0.1, 0.25, 0.08, -0.15};
  a.clear();
  b.clear();
  double expected_residual = 0;
  for (double x : {-1.0, 0.0, 1.0})
    for (double y : {-1.0, 0.0, 1.0}) {
      Row row{1, x, y, x * x, x * y, y * y};
      double value = 0;
      for (std::size_t j = 0; j < 6; ++j)
        value += row[j] * beta[j];
      const double noise = 0.02 * (x * x - 2.0 / 3.0) * y; // Orthogonal to all six design columns.
      a.push_back(row);
      b.push_back(value + noise);
      expected_residual = std::hypot(expected_residual, noise);
    }
  solved = SolveLeastSquares6(a, b);
  Check(solved.converged && solved.rank == 6, "Rectangular SVD rank");
  Check(Close(solved.residual, expected_residual), "Independent orthogonal-noise residual");
  for (std::size_t j = 0; j < 6; ++j)
    Check(Close(solved.coefficients[j], beta[j]), "Known rectangular minimizer");
  for (std::size_t i = 0; i < a.size(); ++i)
    for (std::size_t j = 0; j < 6; ++j) {
      double rebuilt = 0;
      for (std::size_t k = 0; k < 6; ++k)
        rebuilt += a[i][k] * solved.right[k][j];
      Check(Close(rebuilt, solved.orthogonal_columns[i][j]), "SVD A*V reconstruction");
    }
  for (std::size_t j = 0; j < 6; ++j)
    for (std::size_t k = 0; k < 6; ++k) {
      double vdot = 0, udot = 0;
      for (std::size_t i = 0; i < 6; ++i)
        vdot += solved.right[i][j] * solved.right[i][k];
      for (std::size_t i = 0; i < a.size(); ++i)
        udot += solved.orthogonal_columns[i][j] * solved.orthogonal_columns[i][k] /
                (solved.singular[j] * solved.singular[k]);
      Check(Close(vdot, j == k ? 1 : 0) && Close(udot, j == k ? 1 : 0), "SVD orthogonality");
    }
  for (auto& row : a)
    row[5] = row[3];
  solved = SolveLeastSquares6(a, b);
  Check(solved.converged && solved.rank == 5, "Rank-deficient SVD is explicit");
  const auto e = SymmetricEigen3({{{3, 0, 0}, {0, 1, 0}, {0, 0, 2}}});
  Check(e.converged && Close(e.values[0], 1) && Close(e.values[2], 3), "Known PCA spectrum");
  const auto repeated = SymmetricEigen3({{{2, 0, 0}, {0, 2, 0}, {0, 0, 2}}});
  Check(repeated.converged && Close(repeated.values[0], 2) && Close(repeated.values[2], 2),
        "Repeated covariance spectrum");
  a.assign(6, Row{});
  b.assign(6, 0);
  for (std::size_t i = 0; i < 6; ++i)
    a[i][i] = 1;
  solved = SolveLeastSquares6(a, b);
  Check(solved.converged && solved.rank == 6 && Close(solved.condition, 1),
        "Repeated singular spectrum");
  a[5][5] = 1e-12;
  solved = SolveLeastSquares6(a, b);
  Check(solved.converged && solved.rank == 6 && Close(solved.singular[5], 1e-12, 1e-25),
        "Near-degenerate full rank is not an accuracy claim");
  a[5][5] = 1e-16;
  solved = SolveLeastSquares6(a, b);
  Check(solved.converged && solved.rank == 5 && solved.singular[5] < solved.threshold,
        "Explicit machine-epsilon rank boundary");
  bool refused = false;
  try {
    a[0][0] = std::numeric_limits<double>::quiet_NaN();
    (void)SolveLeastSquares6(a, b);
  } catch (const std::invalid_argument&) {
    refused = true;
  }
  Check(refused, "Nonfinite numerical input refused");
}
void Graphs() {
  const Point x{1, 0, 0}, y{0, 1, 0}, z{0, 0, 1};
  for (const Row beta :
       {Row{}, Row{0, 0, 0, 0.5, 0, 0.5}, Row{0, 0, 0, 0.5, 0, -0.5}, Row{0, 0, 0, 0.5, 0, 0}}) {
    const auto value = GraphCurvatures(beta, 1, x, y, z, z, 1e-14);
    const auto scaled = GraphCurvatures(beta, 7, x, y, z, z, 1e-14);
    const auto reverse = GraphCurvatures(beta, 1, x, y, z, Scale(z, -1), 1e-14);
    Check(Close(scaled.gaussian, value.gaussian / 49) && Close(scaled.mean, value.mean / 7),
          "Correct curvature units");
    Check(Close(reverse.gaussian, value.gaussian) && Close(reverse.mean, -value.mean),
          "Fitted normal reversal");
  }
  const auto cylinder = GraphCurvatures({0, 0, 0, 0.5, 0, 0}, 1, x, y, z, z, 1e-14);
  Check(Close(cylinder.gaussian, 0) && Close(cylinder.mean, 0.5), "Cylinder needs mean channel");
  const auto slope = GraphCurvatures({0, 1, 0, 0.5, 0, 0.5}, 1, x, y, z, z, 1e-14);
  Check(Close(slope.gaussian, 0.25) && Close(slope.mean, 3 / (4 * std::sqrt(2.0))),
        "Nonzero fitted first derivatives");
}
void Charts() {
  const std::vector<std::vector<std::size_t>> faces{
      {0, 1, 4, 3}, {1, 2, 5, 4}, {3, 4, 7, 6}, {4, 5, 8, 7}};
  const auto graph = BuildNeighborhood(9, faces);
  std::vector<Point> plane, paraboloid, sphere, cylinder;
  for (double y : {-0.1, 0.0, 0.1})
    for (double x : {-0.1, 0.0, 0.1}) {
      plane.push_back({x, y, 0});
      paraboloid.push_back({x, y, (x * x + y * y) / 2});
    }
  for (std::size_t i = 0; i < plane.size(); ++i) {
    const auto flat = EstimateNode(plane, graph, i, {0, 0, 1});
    Check(flat.value && Close(flat.value->gaussian, 0) && Close(flat.value->mean, 0),
          "Full planar chart including boundary");
    Check(flat.ring == (i == 4 ? 1U : 2U),
          "Complete bounded expansion including rank-deficient edge stencil");
    const auto p = paraboloid[i];
    const double d = 1 + p[0] * p[0] + p[1] * p[1];
    const Point normal{-p[0], -p[1], 1};
    // A fixed symmetric sample set keeps PCA horizontal. A one-sided stencil
    // need not: the adopted contract explicitly makes no exact-quadric claim.
    const std::vector<std::size_t> symmetric{0, 1, 2, 3, 4, 5, 6, 7, 8};
    const auto curved = FitSamples(paraboloid, i, symmetric, normal);
    Check(curved.value && Close(curved.value->gaussian, 1 / (d * d)) &&
              Close(curved.value->mean, (d + 1) / (2 * d * std::sqrt(d))),
          "Fixed symmetric paraboloid support");
    const auto reversed = FitSamples(paraboloid, i, symmetric, Scale(normal, -1));
    Check(reversed.value && Close(reversed.value->mean, -curved.value->mean) &&
              Close(reversed.value->gaussian, curved.value->gaussian),
          "Pipeline normal reversal");
  }
  // These six one-sided samples also lie on z=x^2/2-0.05*y. Full numerical
  // rank is not proof that they distinguish that cylinder from the paraboloid.
  const auto edge = EstimateNode(paraboloid, graph, 1, {0, 0.1, 1});
  Check(edge.value && edge.ring == 1 && edge.fit.rank == 6,
        "Retained one-sided full-rank counterexample");
  for (auto id : edge.support) {
    const auto p = paraboloid[id];
    Check(Close(p[2], p[0] * p[0] / 2 - 0.05 * p[1]), "Independent ambiguous-surface construction");
  }
  Check(Close(edge.value->gaussian, 0) && Close(edge.value->mean, 0.5 / std::sqrt(1.0025)),
        "One-sided fit recovers the alternative cylinder");
  Check(std::abs(edge.value->gaussian - 1 / (1.01 * 1.01)) > 0.9,
        "Full-rank result must not be called accurate for the paraboloid");
  for (double y : {-0.001, 0.0, 0.001})
    for (double x : {-0.001, 0.0, 0.001}) {
      sphere.push_back({x, y, std::sqrt(4 - x * x - y * y)});
      cylinder.push_back({x, y, std::sqrt(4 - x * x)});
    }
  const auto ball = EstimateNode(sphere, graph, 4, {0, 0, 1});
  // Taylor truncation O(h^2/R^3) plus subtraction roundoff is below1e-6 here.
  Check(ball.value && Close(ball.value->gaussian, 0.25, 1e-6) &&
            Close(ball.value->mean, -0.5, 1e-6),
        "Sphere independent reference budget");
  const auto tube = EstimateNode(cylinder, graph, 4, {0, 0, 1});
  Check(tube.value && Close(tube.value->gaussian, 0, 1e-9) && Close(tube.value->mean, -0.25, 1e-6),
        "Cylinder full pipeline");
  auto rotated = faces;
  for (auto& face : rotated)
    std::rotate(face.begin(), face.begin() + 1, face.end());
  const auto other = EstimateNode(paraboloid, BuildNeighborhood(9, rotated), 4, {0, 0, 1});
  const auto first = EstimateNode(paraboloid, graph, 4, {0, 0, 1});
  Check(other.value && first.value && other.support == first.support &&
            other.value->gaussian == first.value->gaussian &&
            other.value->mean == first.value->mean,
        "QUAD cycle invariance");
  const double c = std::cos(0.37), s = std::sin(0.37);
  std::vector<Point> moved;
  for (const auto& p : paraboloid)
    moved.push_back({7 * p[0] + 2, 7 * (c * p[1] - s * p[2]) - 3, 7 * (s * p[1] + c * p[2]) + 4});
  const auto transformed = EstimateNode(moved, graph, 4, {0, -s, c});
  Check(transformed.value && Close(transformed.value->gaussian, first.value->gaussian / 49) &&
            Close(transformed.value->mean, first.value->mean / 7),
        "Rigid motion and geometric scale");
  std::vector<Point> coarse(5);
  std::vector<std::size_t> ids{0, 1, 2, 3, 4};
  for (std::size_t i = 0; i < 5; ++i)
    coarse[i] = {static_cast<double>(i), 0, 0};
  Check(FitSamples(coarse, 0, ids, {0, 0, 1}).status == Status::InsufficientSamples,
        "Coarse source stays unavailable");
  coarse.push_back({5, 0, 0});
  ids.push_back(5);
  Check(FitSamples(coarse, 0, ids, {0, 0, 1}).status == Status::AmbiguousFrame,
        "Collinear PCA unavailable");
  coarse[5] = coarse[0];
  Check(FitSamples(coarse, 0, ids, {0, 0, 1}).status == Status::DuplicateSamples,
        "Duplicate positions not merged");
  bool refused = false;
  try {
    auto invalid = faces;
    invalid.push_back(faces[0]);
    (void)BuildNeighborhood(9, invalid);
  } catch (const std::invalid_argument&) {
    refused = true;
  }
  Check(refused, "Malformed chart refused");
}
void CompleteTwoRing() {
  const std::vector<std::vector<std::size_t>> faces{
      {0, 1, 4, 3}, {1, 2, 5, 4}, {3, 4, 7, 6}, {4, 5, 8, 7}};
  const auto graph = BuildNeighborhood(9, faces);
  std::vector<Point> positions;
  for (double y : {-0.1, 0.0, 0.1})
    for (double x : {-0.1, 0.0, 0.1})
      positions.push_back({x, y, (x * x + y * y) / 2});
  for (std::size_t i = 0; i < positions.size(); ++i) {
    const auto p = positions[i];
    const double d = 1 + p[0] * p[0] + p[1] * p[1];
    const auto fitted = EstimateNodeCompleteTwoRing(positions, graph, i, {-p[0], -p[1], 1});
    Check(fitted.ring == 2 && fitted.support.size() == 9,
          "Complete two-ring policy includes the full stencil even when one-ring rank is six");
    Check(fitted.value && Close(fitted.value->gaussian, 1 / (d * d)) &&
              Close(fitted.value->mean, (d + 1) / (2 * d * std::sqrt(d))),
          "Additional samples distinguish the retained boundary counterexample");
  }
  const auto first = EstimateNode(positions, graph, 4, {0, 0, 1});
  const auto second = EstimateNodeCompleteTwoRing(positions, graph, 4, {0, 0, 1});
  Check(first.value && second.value && first.support == second.support &&
            first.value->gaussian == second.value->gaussian &&
            first.value->mean == second.value->mean,
        "Identical support keeps exact numerical results");
  std::vector<Point> quartic;
  std::vector<std::vector<std::size_t>> cells;
  for (std::size_t r = 0; r < 5; ++r)
    for (std::size_t c = 0; c < 5; ++c) {
      const double x = (static_cast<double>(c) - 2) * 0.1;
      const double y = (static_cast<double>(r) - 2) * 0.1;
      quartic.push_back({x, y, x * x * x * x});
      if (r < 4 && c < 4) {
        const auto a = r * 5 + c;
        cells.push_back({a, a + 1, a + 6, a + 5});
      }
    }
  const auto regular = BuildNeighborhood(25, cells);
  const auto narrow = EstimateNode(quartic, regular, 12, {0, 0, 1});
  const auto wide = EstimateNodeCompleteTwoRing(quartic, regular, 12, {0, 0, 1});
  Check(narrow.support.size() == 9 && wide.support.size() == 25,
        "Complete two-ring expands an already full-rank interior stencil");
  // At the query z=x^4 has analytical K=H=0. Larger support increases local bias.
  Check(narrow.value && wide.value && Close(narrow.value->mean, 0.01) &&
            Close(wide.value->mean, 31.0 / 700) &&
            std::abs(wide.value->mean) > std::abs(narrow.value->mean) + 0.03,
        "Retain oversmoothing counterexample instead of requiring universal improvement");
}
} // namespace
int main() {
  try {
    Matrices();
    Graphs();
    Charts();
    CompleteTwoRing();
    std::cout << "JET_CONTRACTS checks=" << checks << " passed=1\n";
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
