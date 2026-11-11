#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"

#include <array>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>

namespace {

// This is a bounded read-only admission test of the production .bp loader.
// It does not create mesh elements, weld nodes, or alter the TRI algorithm.
constexpr double kBend = 0.18;
constexpr double kTolerance = 1e-10;
using Xyz = std::array<double, 3>;

enum class Variant {
  Aligned,
  Reparameterized,
  DisplacedControl,
  ReversedNormal,
  TripleIncidence
};

void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

bool Close(double actual, double expected) {
  return std::isfinite(actual) && std::isfinite(expected) &&
         std::abs(actual - expected) <= kTolerance;
}

Xyz Values(const PointAdaptive& p) {
  return {p.GetX(), p.GetY(), p.GetZ()};
}

Xyz Values(const VectorAdaptive& v) {
  return {v.GetX(), v.GetY(), v.GetZ()};
}

void Compare(Xyz got, Xyz expected, const char* message) {
  for (std::size_t i = 0; i < 3; ++i)
    Require(Close(got[i], expected[i]), message);
}

Xyz Cross(Xyz a, Xyz b) {
  return {a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]};
}

double Dot(Xyz a, Xyz b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

bool ReversesBoth(Variant variant) {
  return variant == Variant::Reparameterized;
}

bool ReversesV(Variant variant) {
  return ReversesBoth(variant) || variant == Variant::ReversedNormal;
}

Xyz Control(unsigned patch, unsigned i, unsigned j, Variant variant) {
  const double u = static_cast<double>(i) / 3.0;
  const double v = static_cast<double>(j) / 3.0;
  const double x = patch == 0U ? u : (ReversesBoth(variant) ? 2.0 - u : 1.0 + u);
  double y = patch == 0U ? v : (ReversesV(variant) ? 1.0 - v : v);
  if (patch == 1U && variant == Variant::DisplacedControl && i == 0U && j == 1U)
    y += 0.02;
  // [0, k/3, k/3, 0] are the exact cubic Bernstein controls of k*y*(1-y).
  const double z = (j == 1U || j == 2U) ? kBend / 3.0 : 0.0;
  return {x, y, z};
}

void WriteFixture(const std::filesystem::path& path, Variant variant) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  Require(static_cast<bool>(output), "Cannot write research BP fixture");
  output << std::setprecision(17);
  const unsigned count = variant == Variant::TripleIncidence ? 3U : 2U;
  // The production validator requires every indexed vertex to precede its patch.
  for (unsigned patch = 0; patch < count; ++patch) {
    for (unsigned j = 0; j < 4U; ++j) {
      for (unsigned i = 0; i < 4U; ++i) {
        const Xyz p = Control(patch, i, j, variant);
        output << "v " << p[0] << ' ' << p[1] << ' ' << p[2] << '\n';
      }
    }
  }
  for (unsigned patch = 0; patch < count; ++patch) {
    output << "p";
    for (unsigned local = 0; local < 16U; ++local)
      output << ' ' << patch * 16U + local;
    output << '\n';
  }
  output.close();
  Require(static_cast<bool>(output), "Cannot complete research BP fixture");
}

struct Incidence {
  unsigned singles = 0;
  unsigned pairs = 0;
  unsigned high_valence = 0;
  unsigned maximum_valence = 0;
};

Incidence Inventory(Geometry& geometry) {
  std::unordered_map<CurveAdaptive*, unsigned> ownership;
  for (unsigned id = 0; id < geometry.GetNumberPatches(); ++id) {
    auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(id));
    Require(patch != nullptr && patch->GetNumBerCurves() == 4U,
            "Production loader did not return four-curve Bezier patches");
    for (unsigned edge = 0; edge < 4U; ++edge) {
      CurveAdaptive* curve = patch->GetCurve(edge);
      Require(curve != nullptr, "A production patch has no boundary curve");
      ++ownership[curve];
    }
  }
  Incidence result;
  for (const auto& item : ownership) {
    const unsigned degree = item.second;
    if (degree == 1U)
      ++result.singles;
    else if (degree == 2U)
      ++result.pairs;
    else
      ++result.high_valence;
    if (degree > result.maximum_valence)
      result.maximum_valence = degree;
  }
  Require(ownership.size() == geometry.GetNumberCurves(),
          "Geometry curve registry differs from observed patch incidences");
  return result;
}

void VerifyIndependentAnalytic(PatchBezier& patch, unsigned id, Variant variant) {
  // This independently evaluated analytic graph has positive world-Z normals.
  // General models must instead derive a local, patch-aware normal policy.
  const double dx_du = id == 0U || !ReversesBoth(variant) ? 1.0 : -1.0;
  const double dy_dv = id == 0U || !ReversesV(variant) ? 1.0 : -1.0;
  for (unsigned iu = 0; iu <= 8U; ++iu) {
    for (unsigned iv = 0; iv <= 8U; ++iv) {
      const double u = static_cast<double>(iu) / 8.0;
      const double v = static_cast<double>(iv) / 8.0;
      const double x = id == 0U ? u : (ReversesBoth(variant) ? 2.0 - u : 1.0 + u);
      const double y = id == 0U ? v : (ReversesV(variant) ? 1.0 - v : v);
      const Xyz xyz{x, y, kBend * y * (1.0 - y)};
      const Xyz qu{dx_du, 0.0, 0.0};
      const Xyz qv{0.0, dy_dv, kBend * (1.0 - 2.0 * y) * dy_dv};
      Compare(Values(patch.Parameterize(u, v)), xyz,
              "Production Bezier XYZ differs from independent Bernstein golden");
      const Xyz actual_qu = Values(patch.Qu(u, v));
      const Xyz actual_qv = Values(patch.Qv(u, v));
      Compare(actual_qu, qu, "Production Bezier Qu differs from analytic golden");
      Compare(actual_qv, qv, "Production Bezier Qv differs from analytic golden");
      const Xyz normal = Cross(actual_qu, actual_qv);
      Require(Dot(normal, {0.0, 0.0, 1.0}) > 1e-12,
              "Research two-patch fixture has reversed chart orientation");
    }
  }
}

void AdmitPair(Geometry& geometry, Variant variant) {
  Require(geometry.GetNumberPatches() == 2U, "Not an ordinary pairwise model");
  const Incidence incidence = Inventory(geometry);
  Require(geometry.GetNumberCurves() == 7U &&
              incidence.singles == 6U && incidence.pairs == 1U &&
              incidence.high_valence == 0U && incidence.maximum_valence == 2U,
          "Two-patch seam is absent, ambiguous or nonmanifold");
  auto* left = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  auto* right = dynamic_cast<PatchBezier*>(geometry.GetPatch(1));
  Require(left != nullptr && right != nullptr, "Unexpected patch type");
  const unsigned right_edge = ReversesBoth(variant) ? 1U : 3U;
  Require(left->GetCurve(1) == right->GetCurve(right_edge),
          "Shared seam did not preserve the production curve object");
  Require(!left->IsCurveReversed(1) &&
              right->IsCurveReversed(right_edge) == ReversesBoth(variant),
          "Production curve incidence lost its relative direction");
  // This check only applies to the constructed C1-continuous analytic fixture.
  VerifyIndependentAnalytic(*left, 0U, variant);
  VerifyIndependentAnalytic(*right, 1U, variant);
  for (unsigned i = 0; i <= 16U; ++i) {
    const double t = static_cast<double>(i) / 16.0;
    const double v = ReversesBoth(variant) ? 1.0 - t : t;
    const double u = ReversesBoth(variant) ? 1.0 : 0.0;
    Compare(Values(left->Parameterize(1.0, t)),
            Values(right->Parameterize(u, v)),
            "Physical seam contains an XYZ gap");
    const Xyz tangent_left = Values(left->Qv(1.0, t));
    const Xyz tangent_right = Values(right->Qv(u, v));
    const double direction = ReversesBoth(variant) ? -1.0 : 1.0;
    Compare(tangent_left, {direction * tangent_right[0],
                           direction * tangent_right[1],
                           direction * tangent_right[2]},
            "Physical seam curve tangent is discontinuous");
  }
}

void Run(const std::filesystem::path& directory, Variant variant,
         const char* name, bool should_admit) {
  const auto file = directory / (std::string(name) + ".bp");
  WriteFixture(file, variant);
  Geometry geometry;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&geometry, file.string()) == &geometry,
          "Production PatchReader returned the wrong geometry");
  const Incidence counts = Inventory(geometry);
  if (variant == Variant::TripleIncidence)
    Require(geometry.GetNumberPatches() == 3U && counts.maximum_valence >= 3U,
            "Three-way curve incidence negative control did not load");
  if (variant == Variant::DisplacedControl)
    Require(geometry.GetNumberPatches() == 2U && counts.pairs == 0U,
            "Displaced seam negative control unexpectedly welded");
  bool admitted = true;
  try {
    AdmitPair(geometry, variant);
  } catch (const std::runtime_error&) {
    admitted = false;
  }
  Require(admitted == should_admit, "Research seam admission misclassified a fixture");
}

}  // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 2, "Usage: quad_m4_pairwise_boundary_probe OUTPUT_DIRECTORY");
    const std::filesystem::path directory(argv[1]);
    std::filesystem::create_directories(directory);
    Run(directory, Variant::Aligned, "pair_aligned", true);
    Run(directory, Variant::Reparameterized, "pair_reparameterized", true);
    Run(directory, Variant::DisplacedControl, "displaced_seam", false);
    Run(directory, Variant::ReversedNormal, "reversed_chart_normal", false);
    Run(directory, Variant::TripleIncidence, "triple_incidence", false);
    std::cout << "quad_m4_pairwise_boundary=ok admitted=2 rejected=3 "
                 "source=PatchReader::ReaderFilePatches "
                 "shared_curve_identity=verified reverse_uv=verified "
                 "analytic_samples=324 seam_samples=34 "
                 "NOT_model_wide_mesh NOT_production_quad\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "quad_m4_pairwise_boundary=failed: " << error.what() << '\n';
    return 1;
  }
}
