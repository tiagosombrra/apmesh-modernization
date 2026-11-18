#include "mixed_uv_smoothing.h"
#include <iostream>
#include <limits>
#include <string>

using namespace apmesh::quad;
namespace {
void Check(bool ok, const char* reason) {
  if (!ok)
    throw std::runtime_error(reason);
}
bool Same(const std::vector<UvVertex>& a, const std::vector<UvVertex>& b) {
  if (a.size() != b.size())
    return false;
  for (std::size_t i = 0; i < a.size(); ++i)
    if (a[i].u != b[i].u || a[i].v != b[i].v)
      return false;
  return true;
}
} // namespace
int main() {
  try {
    const std::vector<UvVertex> uv{{0, 0}, {1, 0}, {1, 1}, {0, 1}, {.3, .4}, {.7, .6}};
    const std::vector<std::vector<VertexId>> faces{
        {0, 1, 5, 4}, {1, 2, 5}, {2, 3, 4, 5}, {3, 0, 4}};
    std::size_t calls = 0;
    // This synthetic callback checks the arithmetic contract, not acceptance
    // of this small mesh after movement. The application supplies real validity.
    const auto trace = SmoothMixedUv(uv, faces, [&](std::size_t pass, const auto& next) {
      Check(pass == ++calls && next.size() == uv.size(), "Wrong simultaneous pass scope");
    });
    Check(calls == 5 && trace.passes.size() == 5 &&
              trace.boundary == std::vector<VertexId>({0, 1, 2, 3}),
          "Wrong pass count or contour identity");
    Check(std::abs(trace.passes[0][4].u - .54) < 1e-14 &&
              std::abs(trace.passes[0][4].v - .52) < 1e-14 &&
              std::abs(trace.passes[0][5].u - .46) < 1e-14 &&
              std::abs(trace.passes[0][5].v - .48) < 1e-14,
          "Distinct incident vertices/opposite corners or Jacobi arithmetic changed");
    Check(std::abs(trace.passes[1][4].u - .492) < 1e-14, "Second pass used sequential updates");
    for (const auto& pass : trace.passes)
      for (const auto id : trace.boundary)
        Check(pass[id].u == uv[id].u && pass[id].v == uv[id].v, "Contour moved");
    bool failed = false;
    try {
      (void)SmoothMixedUv(uv, faces, [](std::size_t pass, const auto&) {
        if (pass == 3)
          throw std::runtime_error("injected pass failure");
      });
    } catch (const std::runtime_error& e) {
      failed = std::string(e.what()) == "injected pass failure";
    }
    Check(failed && Same(uv, {{0, 0}, {1, 0}, {1, 1}, {0, 1}, {.3, .4}, {.7, .6}}),
          "Partial pass failure changed source");
    const auto retry = SmoothMixedUv(uv, faces, [](auto, const auto&) {});
    Check(Same(trace.passes.back(), retry.passes.back()), "Fresh smoothing retry changed result");
    unsigned rejected = 0;
    const auto reject = [&](const auto& points, const auto& polygons) {
      try {
        (void)SmoothMixedUv(points, polygons, [](auto, const auto&) {});
      } catch (const std::invalid_argument&) {
        ++rejected;
        return;
      }
      throw std::runtime_error("Malformed smoothing input accepted");
    };
    reject(uv, std::vector<std::vector<VertexId>>{{0, 0, 4}});
    reject(uv, std::vector<std::vector<VertexId>>{{0, 1, 99}});
    reject(uv, std::vector<std::vector<VertexId>>{{0, 1, 4}, {0, 1, 5}});
    auto bad = uv;
    bad[4].u = std::numeric_limits<double>::quiet_NaN();
    reject(bad, faces);
    bad = uv;
    bad.push_back({.2, .2});
    reject(bad, faces);
    Check(rejected == 5, "Missing malformed controls");
    std::cout << "MIXED_UV_SMOOTHING distinct_neighbors=1 quad_opposite=1 jacobi=1 passes=5 "
                 "contour_fixed=1 failure_preserves_source=1 retry=1 rejected=5\n";
    return 0;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
