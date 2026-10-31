#pragma once

#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/patch/patch_bezier.h"
#include "estimate/charge_estimate_process.h"
#include "parallel/NoCommunicator.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>

namespace apmesh::test {
inline void RequirePortability(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

class RecordingCommunicator : public Parallel::NoCommunicator {
public:
  using Parallel::NoCommunicator::reduceScatter;
  Data::Int numProcesses() const override { return 3; }
  Data::IntVector ranks(Data::Int = -1) const override { return {0, 1, 2}; }
  Data::Int expected_count = 1;
  mutable unsigned calls = 0;

  void reduceScatter(const void* source, void* destination, Data::Int counts[], Type type,
                     Operation operation) const override {
    RequirePortability(operation == SUM, "Reduction operation changed");
    for (Data::Int index = 0; index < numProcesses(); ++index)
      RequirePortability(counts[index] == expected_count, "Reduction count buffer changed");
    RequirePortability(type == INT || type == REAL, "Reduction element type changed");
    const auto count = static_cast<std::size_t>(numProcesses() * expected_count);
    std::memcpy(destination, source,
                count * (type == INT ? sizeof(Data::Int) : sizeof(Data::Real)));
    ++calls;
  }
};

inline double CheckQuadrature(bool tilted, int order) {
  std::array<PointAdaptive, 16> points;
  for (unsigned i = 0; i < 4; ++i)
    for (unsigned j = 0; j < 4; ++j) {
      const double u = i / 3.0, v = j / 3.0;
      points[4 * i + j] = PointAdaptive(2 * u, 3 * v, tilted ? u + 2 * v : 0);
    }
  // The patch must retire before its externally owned curves.
  std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4> curves;
  auto patch = std::make_unique<PatchBezier>(
      points[0], points[1], points[2], points[3], points[4], points[5], points[6], points[7],
      points[8], points[9], points[10], points[11], points[12], points[13], points[14], points[15]);
  for (unsigned slot = 0; slot < curves.size(); ++slot)
    curves[slot].reset(static_cast<CurveAdaptiveParametricBezier*>(patch->GetCurve(slot)));
  ChargeEstimateProcess estimator;
  const double area = estimator.CalculateAreaPatch(patch.get(), order);
  const double expected = tilted ? std::sqrt(61.0) : 6.0;
  RequirePortability(std::isfinite(area) && std::abs(area - expected) < 1e-10 * expected,
                     "Defined quadrature order changed analytic affine-patch area");
  return area;
}

inline int RunSerialPortabilityChecks() {
#if defined(_MSVC_LANG)
  constexpr long language = _MSVC_LANG;
#else
  constexpr long language = __cplusplus;
#endif
#if defined(_ITERATOR_DEBUG_LEVEL)
  constexpr int iterator_level = _ITERATOR_DEBUG_LEVEL;
#else
  constexpr int iterator_level = -1;
#endif
  static_assert(language >= 201703L);
  static_assert(sizeof(double) == sizeof(std::uint64_t));
  const double pi = M_PI;
  std::uint64_t bits = 0;
  std::memcpy(&bits, &pi, sizeof(bits));
  RequirePortability(bits == UINT64_C(0x400921fb54442d18), "Existing pi constant changed");

  std::array<double, 4> areas{};
  unsigned index = 0;
  for (bool tilted : {false, true})
    for (int order : {3, 4})
      areas[index++] = CheckQuadrature(tilted, order);

  RecordingCommunicator communicator;
  const std::array<Data::Int, 6> integers{2, 3, 5, 7, 11, 13};
  const std::array<Data::Real, 6> reals{0.125, -0.5, 1.0, 2.0, 4.0, 8.0};
  for (Data::Int count : {1, 2}) {
    communicator.expected_count = count;
    std::unique_ptr<Data::Int[]> copied_ints(
        communicator.reduceScatter(integers.data(), count, Parallel::Communicator::SUM));
    std::unique_ptr<Data::Real[]> copied_reals(
        communicator.reduceScatter(reals.data(), count, Parallel::Communicator::SUM));
    for (Data::Int position = 0; position < count * communicator.numProcesses(); ++position) {
      const auto offset = static_cast<std::size_t>(position);
      RequirePortability(copied_ints[offset] == integers[offset] &&
                             copied_reals[offset] == reals[offset],
                         "Typed reduction buffer extent or payload changed");
    }
  }
  RequirePortability(communicator.calls == 4, "Required buffer calls were not executed");
  std::cout << std::setprecision(17) << "{\"language\":" << language
            << ",\"iterator_level\":" << iterator_level << ",\"pi_bits\":" << bits
            << ",\"areas\":[";
  for (unsigned i = 0; i < areas.size(); ++i)
    std::cout << (i ? "," : "") << areas[i];
  std::cout << "],\"buffer_calls\":" << communicator.calls << "}\n";
  return 0;
}
} // namespace apmesh::test
