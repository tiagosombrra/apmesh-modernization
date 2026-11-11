#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/models_3d.h"

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

// This research executable borrows a Geometry-owned, built-in physical model.
// It never creates or publishes an ElementAdaptive or changes the TRI generator.
namespace {

struct Uv {
  double u;
  double v;
};

struct Face {
  std::vector<std::size_t> ids;
};

struct SourceMesh {
  std::vector<Uv> uv;
  std::vector<Face> quads;
  std::vector<Face> triangles;
};

struct PhysicalSample {
  std::array<double, 3> xyz;
  std::array<double, 3> du;
  std::array<double, 3> dv;
  double normal_magnitude;
};

void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

bool Finite(const std::array<double, 3>& values) {
  for (double value : values) {
    if (!std::isfinite(value))
      return false;
  }
  return true;
}

double TwiceSignedArea(const std::vector<Uv>& points, const Face& face) {
  double sum = 0.0;
  for (std::size_t j = 0; j < face.ids.size(); ++j) {
    const Uv& a = points[face.ids[j]];
    const Uv& b = points[face.ids[(j + 1) % face.ids.size()]];
    sum += a.u * b.v - a.v * b.u;
  }
  return sum;
}

SourceMesh ReadUv(const std::string& path) {
  std::ifstream input(path);
  Require(static_cast<bool>(input), "Could not read native hybrid OBJ");
  input.imbue(std::locale::classic());
  SourceMesh result;
  std::string line;
  std::string group;
  std::size_t group_changes = 0;
  while (std::getline(input, line)) {
    std::istringstream record(line);
    record.imbue(std::locale::classic());
    std::string kind;
    if (!(record >> kind) || kind[0] == '#')
      continue;
    if (kind == "v") {
      Require(group_changes == 0, "OBJ vertex encountered after faces");
      double u = 0.0, v = 0.0, z = 0.0;
      Require(static_cast<bool>(record >> u >> v >> z),
              "Invalid native hybrid vertex");
      std::string extra;
      Require(!(record >> extra), "Native UV vertex has unexpected fields");
      Require(std::isfinite(u) && std::isfinite(v) && std::isfinite(z) &&
                  u >= 0.0 && u <= 1.0 && v >= 0.0 && v <= 1.0 &&
                  z == 0.0,
              "Out-of-domain or nonfinite native UV vertex");
      result.uv.push_back({u, v});
    } else if (kind == "g") {
      Require(static_cast<bool>(record >> group), "Missing OBJ face group");
      ++group_changes;
      Require((group_changes == 1 && group == "QUAD_native_cpp_unmodified") ||
                  (group_changes == 2 &&
                   group == "TRI_exterior_local_Lawson_research"),
              "Unexpected native M5 OBJ provenance/group order");
    } else if (kind == "f") {
      Require(group_changes == 1 || group_changes == 2,
              "Face precedes the native QUAD group");
      Face face;
      std::string value;
      while (record >> value) {
        Require(!value.empty() && value.find_first_not_of("0123456789") ==
                    std::string::npos,
                "Nonintegral OBJ vertex index");
        const auto number = std::stoull(value);
        Require(number > 0 && number <= result.uv.size(),
                "Native hybrid face index out of bounds");
        face.ids.push_back(static_cast<std::size_t>(number - 1));
      }
      const std::size_t expected = group_changes == 1 ? 4 : 3;
      Require(face.ids.size() == expected, "Wrong source face arity");
      Require(std::set<std::size_t>(face.ids.begin(), face.ids.end()).size() ==
                  expected,
              "Repeated source face index");
      Require(TwiceSignedArea(result.uv, face) > 1e-14,
              "Inverted or collapsed parametric source face");
      if (group_changes == 1)
        result.quads.push_back(std::move(face));
      else
        result.triangles.push_back(std::move(face));
    } else {
      throw std::runtime_error("Unsupported native M5 OBJ record");
    }
  }
  Require(static_cast<bool>(input) || input.eof(), "Native M5 OBJ I/O error");
  Require(result.uv.size() == 69 && result.quads.size() == 42 &&
              result.triangles.size() == 36 && group_changes == 2,
          "Native C++ QUAD and M5 TRI research inventory changed");
  std::set<std::pair<double, double>> coordinates;
  for (const Uv& point : result.uv)
    Require(coordinates.emplace(point.u, point.v).second,
            "Duplicate native UV identity");
  return result;
}

PhysicalSample Evaluate(PatchBezier& patch, const Uv& uv) {
  // Production PatchBezier mutates evaluation scratch matrices. Calls here are serial.
  const auto xyz = patch.Parameterize(uv.u, uv.v);
  const auto qu = patch.Qu(uv.u, uv.v);
  const auto qv = patch.Qv(uv.u, uv.v);
  PhysicalSample sample{{
                            xyz.GetX(), xyz.GetY(), xyz.GetZ()
                          },
                        {qu.GetX(), qu.GetY(), qu.GetZ()},
                        {qv.GetX(), qv.GetY(), qv.GetZ()},
                        0.0};
  Require(Finite(sample.xyz) && Finite(sample.du) && Finite(sample.dv),
          "Nonfinite built-in Bezier evaluation");
  const std::array<double, 3> normal{
      sample.du[1] * sample.dv[2] - sample.du[2] * sample.dv[1],
      sample.du[2] * sample.dv[0] - sample.du[0] * sample.dv[2],
      sample.du[0] * sample.dv[1] - sample.du[1] * sample.dv[0]};
  sample.normal_magnitude = std::hypot(std::hypot(normal[0], normal[1]), normal[2]);
  Require(std::isfinite(sample.normal_magnitude) &&
              sample.normal_magnitude > 1e-12 && normal[2] > 1e-12,
          "Collapsed or reversed physical model Jacobian");
  return sample;
}

void WriteObj(const std::string& path, const SourceMesh& source,
              const std::vector<PhysicalSample>& mapped) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  Require(static_cast<bool>(output), "Cannot create physical OBJ");
  output.imbue(std::locale::classic());
  output << std::setprecision(17)
         << "# Actual APMesh ModelCurvaBezier; native C++ QUAD + experimental M5 TRI\n"
         << "# Research-only physical lift; NOT 1993 historical or production mesh\n";
  for (const auto& s : mapped)
    output << "v " << s.xyz[0] << ' ' << s.xyz[1] << ' ' << s.xyz[2] << '\n';
  output << "g QUAD_native_cpp_lifted\n";
  for (const auto& face : source.quads) {
    output << 'f';
    for (const auto id : face.ids)
      output << ' ' << id + 1;
    output << '\n';
  }
  output << "g TRI_exterior_Lawson_research_lifted\n";
  for (const auto& face : source.triangles) {
    output << 'f';
    for (const auto id : face.ids)
      output << ' ' << id + 1;
    output << '\n';
  }
  output.close();
  Require(static_cast<bool>(output), "Cannot finish physical OBJ");
}

void WriteSamples(const std::string& path, const SourceMesh& source,
                  const std::vector<PhysicalSample>& mapped) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  Require(static_cast<bool>(output), "Cannot create physical sample CSV");
  output.imbue(std::locale::classic());
  output << std::setprecision(17)
         << "id,u,v,x,y,z,qu_x,qu_y,qu_z,qv_x,qv_y,qv_z,jacobian_norm\n";
  for (std::size_t id = 0; id < mapped.size(); ++id) {
    const auto& p = mapped[id];
    output << id << ',' << source.uv[id].u << ',' << source.uv[id].v;
    for (double value : p.xyz) output << ',' << value;
    for (double value : p.du) output << ',' << value;
    for (double value : p.dv) output << ',' << value;
    output << ',' << p.normal_magnitude << '\n';
  }
  output.close();
  Require(static_cast<bool>(output), "Cannot finish physical sample CSV");
}

}  // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 4,
            "Usage: quad_m4_physical_model_lift SOURCE_UV_OBJ OUTPUT_XYZ_OBJ OUTPUT_CSV");
    const auto input = ReadUv(argv[1]);
    Geometry geometry;
    Models3d model;
    Require(model.ModelCurvaBezier(&geometry) == &geometry &&
                geometry.GetNumberPatches() == 1,
            "Production built-in curved model contract changed");
    PatchBezier* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
    Require(patch != nullptr && patch->GetNumBerCurves() == 4,
            "Expected one Geometry-owned production PatchBezier");
    std::vector<PhysicalSample> mapped;
    mapped.reserve(input.uv.size());
    for (const Uv& point : input.uv)
      mapped.push_back(Evaluate(*patch, point));
    WriteObj(argv[2], input, mapped);
    WriteSamples(argv[3], input, mapped);
    std::cout << "m4_actual_model=ok vertex_ids=69 native_cpp_quad=42 "
                 "research_lawson_tri=36 model=Models3d::ModelCurvaBezier "
                 "NOT_CAD_import NOT_production_hybrid\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "m4_actual_model=failed: " << error.what() << '\n';
    return 1;
  }
}
