#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/patch/patch_bezier.h"

#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <limits>
#include <stdexcept>

// An actual PatchBezier instance is exercised, but its control grid is a
// deterministic mathematical fixture, not an imported physical CAD model.
namespace {
using Controls = std::array<std::array<PointAdaptive, 4>, 4>;

void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

bool Close(double got, double expected, double tolerance = 5e-11) {
  return std::isfinite(got) && std::abs(got - expected) <= tolerance;
}

double BernsteinBump(unsigned index) {
  return index == 1 || index == 2 ? 1.0 / 3.0 : 0.0;
}

struct OwnedPatchFixture {
  Controls controls{};
  std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4> curves{};
  std::unique_ptr<PatchBezier> patch;

  explicit OwnedPatchFixture(double curvature, bool mirror_u = false,
                             bool collapse = false) {
    for (unsigned i = 0; i < 4; ++i) {
      for (unsigned j = 0; j < 4; ++j) {
        const double u = static_cast<double>(i) / 3.0;
        const double v = static_cast<double>(j) / 3.0;
        controls[i][j] = collapse
            ? PointAdaptive(0.0, 0.0, 0.0)
            : PointAdaptive(mirror_u ? 1.0 - u : u, v,
                            curvature * BernsteinBump(i) * BernsteinBump(j));
      }
    }
    const auto curve = [&](const PointAdaptive& a, const PointAdaptive& b,
                           const PointAdaptive& c, const PointAdaptive& d) {
      return std::make_unique<CurveAdaptiveParametricBezier>(a, b, c, d);
    };
    curves[0] = curve(controls[0][0], controls[1][0], controls[2][0], controls[3][0]);
    curves[1] = curve(controls[3][0], controls[3][1], controls[3][2], controls[3][3]);
    curves[2] = curve(controls[0][3], controls[1][3], controls[2][3], controls[3][3]);
    curves[3] = curve(controls[0][0], controls[0][1], controls[0][2], controls[0][3]);
    // Curves are owned by this fixture and outlive the borrowing PatchBezier.
    // A failed constructor retains ownership and rolls back appended observers.
    patch = std::make_unique<PatchBezier>(
        curves[0].get(), curves[1].get(), curves[2].get(), curves[3].get(),
        controls[1][1], controls[2][1], controls[1][2], controls[2][2]);
  }
};

struct Sample {
  PointAdaptive xyz;
  VectorAdaptive du;
  VectorAdaptive dv;
  double positive_jacobian_z;
};

Sample CheckedSample(PatchBezier& patch, double u, double v) {
  // PatchBezier itself does not validate its UV domain or its Jacobian.
  // Fail closed in this separate research adapter before publishing a point.
  Require(std::isfinite(u) && std::isfinite(v) &&
              u >= 0.0 && u <= 1.0 && v >= 0.0 && v <= 1.0,
          "Invalid UV domain");
  const PointAdaptive p = patch.Parameterize(u, v);
  const VectorAdaptive du = patch.Qu(u, v);
  const VectorAdaptive dv = patch.Qv(u, v);
  const std::array<double, 9> values{
      p.GetX(), p.GetY(), p.GetZ(),
      du.GetX(), du.GetY(), du.GetZ(),
      dv.GetX(), dv.GetY(), dv.GetZ()};
  for (double value : values)
    Require(std::isfinite(value), "Nonfinite PatchBezier evaluation");
  const double jacobian_z = du.GetX() * dv.GetY() - du.GetY() * dv.GetX();
  const double normal_x = du.GetY() * dv.GetZ() - du.GetZ() * dv.GetY();
  const double normal_y = du.GetZ() * dv.GetX() - du.GetX() * dv.GetZ();
  const double normal_norm = std::hypot(std::hypot(normal_x, normal_y), jacobian_z);
  Require(normal_norm > 1e-12 && jacobian_z > 1e-12,
          "Collapsed or reversed PatchBezier oriented Jacobian");
  return {p, du, dv, jacobian_z};
}

bool Rejects(PatchBezier& patch, double u, double v) {
  try {
    static_cast<void>(CheckedSample(patch, u, v));
    return false;
  } catch (const std::runtime_error&) {
    return true;
  }
}

void VerifyIndependentBernsteinGolden(double curvature) {
  OwnedPatchFixture owned(curvature);
  constexpr std::array<double, 9> samples{
      0.0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.625, 0.875, 1.0};
  for (const double u : samples) {
    for (const double v : samples) {
      const Sample result = CheckedSample(*owned.patch, u, v);
      const double fu = u * (1.0 - u);
      const double fv = v * (1.0 - v);
      // This polynomial is independent of PatchBezier matrix evaluation.
      Require(Close(result.xyz.GetX(), u) && Close(result.xyz.GetY(), v) &&
                  Close(result.xyz.GetZ(), curvature * fu * fv),
              "PatchBezier XYZ does not match independent analytic golden");
      Require(Close(result.du.GetX(), 1.0) &&
                  Close(result.du.GetY(), 0.0) &&
                  Close(result.du.GetZ(), curvature * (1.0 - 2.0 * u) * fv),
              "PatchBezier Qu does not match independent derivative");
      Require(Close(result.dv.GetX(), 0.0) &&
                  Close(result.dv.GetY(), 1.0) &&
                  Close(result.dv.GetZ(), curvature * fu * (1.0 - 2.0 * v)),
              "PatchBezier Qv does not match independent derivative");
      Require(Close(result.positive_jacobian_z, 1.0),
              "PatchBezier Jacobian changed the oriented UV area scale");
      if (u == 0.0 || u == 1.0 || v == 0.0 || v == 1.0)
        Require(Close(result.xyz.GetZ(), 0.0),
                "PatchBezier boundary control did not stay on z=0");
    }
  }
  // Invalid coordinates are rejected by the explicit research adapter.
  Require(Rejects(*owned.patch, -0.01, 0.5) &&
              Rejects(*owned.patch, 0.5, 1.01) &&
              Rejects(*owned.patch, std::numeric_limits<double>::quiet_NaN(), 0.5) &&
              Rejects(*owned.patch, 0.5, std::numeric_limits<double>::infinity()),
          "UV invalid-domain controls were not rejected");
}

void VerifyInvalidPatchGeometries() {
  OwnedPatchFixture collapsed(0.0, false, true);
  Require(Rejects(*collapsed.patch, 0.5, 0.5),
          "Collapsed production Bezier patch was not rejected");
  OwnedPatchFixture reflected(0.0, true, false);
  Require(Rejects(*reflected.patch, 0.5, 0.5),
          "Reflected production Bezier patch was not rejected");
}
}  // namespace

int main() {
  try {
    for (const double curvature : {0.0, 1.6, -1.6})
      VerifyIndependentBernsteinGolden(curvature);
    VerifyInvalidPatchGeometries();
    std::cout << "quad.patch_bezier.physical_api=ok 3_curvatures "
                 "243_samples 12_invalid_uv 2_invalid_geometry "
                 "real_PatchBezier_API synthetic_control_grid "
                 "NOT_imported_CAD NOT_production_QUAD\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "quad.patch_bezier.physical_api=failed: "
              << error.what() << '\n';
    return 1;
  }
}
