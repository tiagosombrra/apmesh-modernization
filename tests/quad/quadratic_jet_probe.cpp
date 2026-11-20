#include "quadratic_jet_curvature.h"

#include <iomanip>
#include <iostream>

int main(int argc, char** argv) {
  using namespace apmesh::quad::research::jet;
  try {
    const bool complete_two_ring = argc == 2 && std::string_view(argv[1]) == "--complete-two-ring";
    if (argc != 1 && !complete_two_ring)
      throw std::invalid_argument("Unknown jet probe neighborhood policy");
    std::size_t n = 0, m = 0;
    if (!(std::cin >> n >> m) || n == 0 || m == 0 || n > 1000000 || m > 1000000)
      throw std::invalid_argument("Invalid jet probe dimensions");
    std::vector<Point> positions(n), normals(n);
    for (std::size_t i = 0; i < n; ++i) {
      for (auto& x : positions[i])
        if (!(std::cin >> x))
          throw std::invalid_argument("Invalid jet probe position");
      for (auto& x : normals[i])
        if (!(std::cin >> x))
          throw std::invalid_argument("Invalid jet probe normal");
    }
    std::vector<std::vector<std::size_t>> faces(m);
    for (auto& f : faces) {
      std::size_t arity = 0;
      if (!(std::cin >> arity) || (arity != 3 && arity != 4))
        throw std::invalid_argument("Invalid jet probe arity");
      f.resize(arity);
      for (auto& id : f)
        if (!(std::cin >> id))
          throw std::invalid_argument("Invalid jet probe face");
    }
    std::string trailing;
    if (std::cin >> trailing)
      throw std::invalid_argument("Trailing jet probe data");
    const auto graph = BuildNeighborhood(n, faces);
    std::cout << std::setprecision(17);
    std::cout << "node,status,ring,boundary,support,scale,rank,converged,sigma_max,sigma_min,rank_"
                 "guard,condition,residual,eig0,eig1,eig2,cov_guard,t1x,t1y,t1z,t2x,t2y,t2z,nx,ny,"
                 "nz,c0,c1,c2,c3,c4,c5,offset,alignment,fit_nx,fit_ny,fit_nz,K,H\n";
    for (std::size_t i = 0; i < n; ++i) {
      const auto r = complete_two_ring
                         ? EstimateNodeCompleteTwoRing(positions, graph, i, normals[i])
                         : EstimateNode(positions, graph, i, normals[i]);
      const bool fitted = !r.fit.orthogonal_columns.empty();
      auto number = [&](double value, bool computed = true) {
        std::cout << ',';
        if (computed && std::isfinite(value))
          std::cout << value;
      };
      std::cout << i << ',' << StatusName(r.status) << ',' << r.ring << ',' << graph.boundary[i]
                << ',';
      for (std::size_t k = 0; k < r.support.size(); ++k) {
        if (k)
          std::cout << '|';
        std::cout << r.support[k];
      }
      number(r.scale);
      number(static_cast<double>(r.fit.rank), fitted);
      number(r.fit.converged ? 1 : 0, fitted);
      number(r.fit.singular[0], fitted);
      number(r.fit.singular[5], fitted);
      number(r.fit.threshold, fitted);
      number(r.fit.condition, fitted);
      number(r.fit.residual, fitted);
      for (double x : r.covariance.values)
        number(x, r.covariance.converged);
      number(r.covariance_guard, r.covariance.converged);
      for (const auto& v : {r.tangent1, r.tangent2, r.rough_normal})
        for (double x : v)
          number(x, fitted);
      for (double x : r.fit.coefficients)
        number(x, fitted);
      number(r.offset, r.value.has_value());
      number(r.orientation, r.value.has_value());
      for (std::size_t k = 0; k < 3; ++k)
        number(r.value ? r.value->normal[k] : 0, r.value.has_value());
      number(r.value ? r.value->gaussian : 0, r.value.has_value());
      number(r.value ? r.value->mean : 0, r.value.has_value());
      std::cout << '\n';
    }
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
