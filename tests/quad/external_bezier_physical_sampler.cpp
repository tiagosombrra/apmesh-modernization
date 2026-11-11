#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"

#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

// This read-only research probe evaluates every real Bezier patch independently.
// Curve identity is observed, never used to weld physical mesh nodes.
struct Uv { double u; double v; };
struct Sample {
  std::array<double, 3> xyz;
  std::array<double, 3> du;
  std::array<double, 3> dv;
  double normal_magnitude;
};
struct Boundary {
  unsigned patch;
  unsigned side;
  unsigned curve;
  bool reverse;
};

void Require(bool ok, const char* reason) {
  if (!ok) throw std::runtime_error(reason);
}

double Number(const std::string& field) {
  std::size_t consumed = 0;
  const double value = std::stod(field, &consumed);
  Require(consumed == field.size() && std::isfinite(value),
          "Invalid/nonfinite native source UV value");
  return value;
}

std::vector<Uv> ReadNativeUv(const std::string& filename) {
  std::ifstream input(filename, std::ios::binary);
  Require(static_cast<bool>(input), "Cannot open native C++ UV source CSV");
  input.imbue(std::locale::classic());
  std::string line;
  Require(static_cast<bool>(std::getline(input, line)) &&
              line == "id,u,v",
          "Native UV source CSV header changed");
  std::vector<Uv> points;
  std::set<std::pair<double, double>> seen;
  while (std::getline(input, line)) {
    std::istringstream row(line);
    std::string id, us, vs, extra;
    Require(static_cast<bool>(std::getline(row, id, ',')) &&
                static_cast<bool>(std::getline(row, us, ',')) &&
                static_cast<bool>(std::getline(row, vs, ',')) &&
                !std::getline(row, extra, ','),
            "Malformed source UV CSV row");
    Require(id == std::to_string(points.size()),
            "Native source vertex ID is missing or reordered");
    const double u = Number(us), v = Number(vs);
    Require(u >= 0.0 && u <= 1.0 && v >= 0.0 && v <= 1.0 &&
                seen.emplace(u, v).second,
            "Source UV identity is outside chart or duplicated");
    points.push_back({u, v});
  }
  Require(!input.bad() && points.size() == 69U,
          "Expected 69 native C++/M5 UV vertices");
  return points;
}

std::array<double, 3> Coordinates(const PointAdaptive& point) {
  return {point.GetX(), point.GetY(), point.GetZ()};
}

std::array<double, 3> Coordinates(const VectorAdaptive& value) {
  return {value.GetX(), value.GetY(), value.GetZ()};
}

Sample Evaluate(PatchBezier& patch, Uv uv) {
  // PatchBezier reuses mutable Bernstein matrices; never evaluate concurrently.
  const auto point = patch.Parameterize(uv.u, uv.v);
  const auto qu = patch.Qu(uv.u, uv.v);
  const auto qv = patch.Qv(uv.u, uv.v);
  Sample result{Coordinates(point), Coordinates(qu), Coordinates(qv), 0.0};
  for (const auto& vec : {result.xyz, result.du, result.dv})
    for (double x : vec)
      Require(std::isfinite(x), "Nonfinite physical Bezier evaluation");
  const auto& a = result.du;
  const auto& b = result.dv;
  const double nx = a[1]*b[2] - a[2]*b[1];
  const double ny = a[2]*b[0] - a[0]*b[2];
  const double nz = a[0]*b[1] - a[1]*b[0];
  result.normal_magnitude = std::hypot(std::hypot(nx, ny), nz);
  Require(std::isfinite(result.normal_magnitude),
          "Nonfinite physical tangent cross magnitude");
  // Do not reject on world-space normal sign, or assume global regularity.
  return result;
}

std::vector<Boundary> Inventory(Geometry& geometry) {
  std::map<CurveAdaptive*, unsigned> identities;
  std::vector<Boundary> result;
  for (unsigned patch_id = 0; patch_id < geometry.GetNumberPatches(); ++patch_id) {
    auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(patch_id));
    Require(patch != nullptr && patch->GetNumBerCurves() == 4U,
            "External model did not produce four-sided Bezier charts");
    for (unsigned side = 0; side < 4U; ++side) {
      CurveAdaptive* pointer = patch->GetCurve(side);
      Require(pointer != nullptr, "External model has null boundary curve");
      auto it = identities.find(pointer);
      if (it == identities.end())
        it = identities.emplace(pointer, static_cast<unsigned>(identities.size())).first;
      result.push_back({patch_id, side, it->second,
                        patch->IsCurveReversed(side)});
    }
  }
  Require(identities.size() == geometry.GetNumberCurves(),
          "Production loader curve identity registry mismatch");
  return result;
}

void ExportCurves(const std::string& filename,
                  const std::vector<Boundary>& edges) {
  std::map<unsigned, unsigned> degrees;
  for (const auto& edge : edges) ++degrees[edge.curve];
  std::ofstream out(filename, std::ios::binary | std::ios::trunc);
  Require(static_cast<bool>(out), "Cannot write external curve incidence");
  out << "patch,side,curve_id,reversed,degree\n";
  for (const auto& edge : edges)
    out << edge.patch << ',' << edge.side << ',' << edge.curve << ','
        << (edge.reverse ? 1 : 0) << ',' << degrees.at(edge.curve) << '\n';
  out.close();
  Require(static_cast<bool>(out), "Incomplete external incidence CSV");
}

void ExportSamples(const std::string& filename, Geometry& geometry,
                   const std::vector<Uv>& uv) {
  std::ofstream out(filename, std::ios::binary | std::ios::trunc);
  Require(static_cast<bool>(out), "Cannot write external physical sample CSV");
  out.imbue(std::locale::classic());
  out << std::setprecision(17)
      << "patch,id,u,v,x,y,z,qu_x,qu_y,qu_z,qv_x,qv_y,qv_z,jacobian_norm\n";
  for (unsigned id = 0; id < geometry.GetNumberPatches(); ++id) {
    auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(id));
    Require(patch != nullptr, "Non-Bezier source patch encountered");
    for (std::size_t i = 0; i < uv.size(); ++i) {
      const auto sample = Evaluate(*patch, uv[i]);
      out << id << ',' << i << ',' << uv[i].u << ',' << uv[i].v;
      for (double x : sample.xyz) out << ',' << x;
      for (double x : sample.du) out << ',' << x;
      for (double x : sample.dv) out << ',' << x;
      out << ',' << sample.normal_magnitude << '\n';
    }
  }
  out.close();
  Require(static_cast<bool>(out), "Incomplete external physical sample CSV");
}

} // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 6,
            "Usage: quad_m4_external_bezier_sampler MODEL_BP NATIVE_UV_CSV "
            "SAMPLE_CSV INCIDENCE_CSV EXPECTED_PATCHES");
    const auto uv = ReadNativeUv(argv[2]);
    const unsigned expected = static_cast<unsigned>(std::stoul(argv[5]));
    Require(expected == 4U || expected == 13U || expected == 28U,
            "This bounded experiment supports only three audited model sizes");
    Geometry geometry;
    PatchReader reader;
    Require(reader.ReaderFilePatches(&geometry, argv[1]) == &geometry &&
                geometry.GetNumberPatches() == expected,
            "Unexpected external Bezier patch count");
    const auto edges = Inventory(geometry);
    ExportCurves(argv[4], edges);
    ExportSamples(argv[3], geometry, uv);
    std::cout << "m4_external_bezier_samples=ok patches=" << expected
              << " samples=" << expected * uv.size()
              << " curves=" << geometry.GetNumberCurves()
              << " real_PatchReader=1 real_PatchBezier=1 "
                 "NO_global_node_weld NO_owned_mesh NO_historical_1993\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "m4_external_bezier_samples=failed: " << error.what() << '\n';
    return 1;
  }
}
