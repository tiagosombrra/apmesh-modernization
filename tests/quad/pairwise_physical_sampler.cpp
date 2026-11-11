#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"

#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

// All geometry evaluation remains serial: PatchBezier mutates its basis scratch.
// Only per-patch samples are exported; no global node welding or mesh publication.
struct Uv {
  double u;
  double v;
};

struct Physical {
  std::array<double, 3> xyz;
  std::array<double, 3> du;
  std::array<double, 3> dv;
  double jacobian;
};

void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

double ParseDouble(const std::string& field) {
  std::size_t used = 0;
  const double value = std::stod(field, &used);
  Require(used == field.size() && std::isfinite(value),
          "Nonfinite or invalid source UV coordinate");
  return value;
}

std::vector<Uv> ReadUvCsv(const std::string& filename) {
  std::ifstream in(filename, std::ios::binary);
  Require(static_cast<bool>(in), "Cannot open native-origin UV CSV");
  in.imbue(std::locale::classic());
  std::string line;
  Require(static_cast<bool>(std::getline(in, line)) && line == "id,u,v",
          "Native-origin UV CSV header changed");
  std::vector<Uv> uv;
  std::set<std::pair<double, double>> unique;
  while (std::getline(in, line)) {
    std::istringstream row(line);
    row.imbue(std::locale::classic());
    std::string id, u, v, extra;
    Require(static_cast<bool>(std::getline(row, id, ',')) &&
                static_cast<bool>(std::getline(row, u, ',')) &&
                static_cast<bool>(std::getline(row, v, ',')) &&
                !std::getline(row, extra, ','),
            "Malformed native-origin UV CSV row");
    Require(id == std::to_string(uv.size()),
            "Source UV identity was reordered or duplicated");
    const double x = ParseDouble(u), y = ParseDouble(v);
    Require(x >= 0.0 && x <= 1.0 && y >= 0.0 && y <= 1.0,
            "UV point outside the native parametric chart");
    Require(unique.emplace(x, y).second,
            "Source UV includes duplicated coordinate identity");
    uv.push_back({x, y});
  }
  Require(!in.bad() && uv.size() == 69U,
          "Native hybrid source must contain exactly 69 UV vertices");
  return uv;
}

std::array<double, 3> Values(const PointAdaptive& p) {
  return {p.GetX(), p.GetY(), p.GetZ()};
}

std::array<double, 3> Values(const VectorAdaptive& v) {
  return {v.GetX(), v.GetY(), v.GetZ()};
}

Physical Evaluate(PatchBezier& patch, Uv uv) {
  const auto position = patch.Parameterize(uv.u, uv.v);
  const auto qu = patch.Qu(uv.u, uv.v);
  const auto qv = patch.Qv(uv.u, uv.v);
  Physical sample{Values(position), Values(qu), Values(qv), 0.0};
  for (const auto& vector : {sample.xyz, sample.du, sample.dv})
    for (double value : vector)
      Require(std::isfinite(value), "Nonfinite production PatchBezier sample");
  const auto& a = sample.du;
  const auto& b = sample.dv;
  const std::array<double, 3> normal{
      a[1] * b[2] - a[2] * b[1],
      a[2] * b[0] - a[0] * b[2],
      a[0] * b[1] - a[1] * b[0]};
  sample.jacobian = std::hypot(std::hypot(normal[0], normal[1]), normal[2]);
  // This chart-specific +Z golden is NOT a CAD-wide physical normal rule.
  Require(std::isfinite(sample.jacobian) && sample.jacobian > 1e-12 &&
              normal[2] > 1e-12,
          "Collapsed or reversed fixture Jacobian");
  return sample;
}

void CheckPairwiseLoader(Geometry& geometry, bool reparameterized) {
  Require(geometry.GetNumberPatches() == 2U &&
              geometry.GetNumberCurves() == 7U,
          "Fixture requires exactly two patches and one shared curve");
  auto* first = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  auto* second = dynamic_cast<PatchBezier*>(geometry.GetPatch(1));
  Require(first != nullptr && second != nullptr &&
              first->GetNumBerCurves() == 4U &&
              second->GetNumBerCurves() == 4U,
          "Production fixture is not a two-patch Bezier model");
  const unsigned second_edge = reparameterized ? 1U : 3U;
  Require(first->GetCurve(1U) == second->GetCurve(second_edge) &&
              !first->IsCurveReversed(1U) &&
              second->IsCurveReversed(second_edge) == reparameterized,
          "Shared physical seam identity/direction differs from the fixture");
}

void Export(const std::string& output, Geometry& geometry,
            const std::vector<Uv>& source) {
  std::ofstream out(output, std::ios::binary | std::ios::trunc);
  Require(static_cast<bool>(out), "Cannot open physical sample CSV");
  out.imbue(std::locale::classic());
  out << std::setprecision(17)
      << "patch,id,u,v,x,y,z,qu_x,qu_y,qu_z,qv_x,qv_y,qv_z,jacobian_norm\n";
  for (unsigned patch_id = 0; patch_id < 2U; ++patch_id) {
    auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(patch_id));
    Require(patch != nullptr, "Model patch type changed during sample export");
    for (std::size_t id = 0; id < source.size(); ++id) {
      const Uv uv = source[id];
      const Physical p = Evaluate(*patch, uv);
      out << patch_id << ',' << id << ',' << uv.u << ',' << uv.v;
      for (double x : p.xyz) out << ',' << x;
      for (double x : p.du) out << ',' << x;
      for (double x : p.dv) out << ',' << x;
      out << ',' << p.jacobian << '\n';
    }
  }
  out.close();
  Require(static_cast<bool>(out), "Could not complete physical sample CSV");
}

}  // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 5,
            "Usage: quad_m4_pairwise_physical_sampler MODEL_BP UV_CSV "
            "OUTPUT_CSV aligned|reparameterized");
    const std::string mode(argv[4]);
    Require(mode == "aligned" || mode == "reparameterized",
            "Unsupported or unapproved physical fixture mode");
    const auto uv = ReadUvCsv(argv[2]);
    Geometry geometry;
    PatchReader reader;
    Require(reader.ReaderFilePatches(&geometry, argv[1]) == &geometry,
            "Production PatchReader ownership or result mismatch");
    CheckPairwiseLoader(geometry, mode == "reparameterized");
    Export(argv[3], geometry, uv);
    std::cout << "m4_native_pairwise_physical=ok source_uv=69 "
                 "patches=2 samples=138 real_PatchReader=1 "
                 "real_PatchBezier=1 NOT_model_wide_mesh "
                 "NOT_1993_historical NOT_production_QUAD\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "m4_native_pairwise_physical=failed: "
              << error.what() << '\n';
    return 1;
  }
}
