#ifndef APMESH_QUAD_RESEARCH_MIXED_SURFACE_RESIDUAL_H
#define APMESH_QUAD_RESEARCH_MIXED_SURFACE_RESIDUAL_H

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <functional>
#include <limits>
#include <stdexcept>
#include <vector>

namespace apmesh::quad::research {

// Research indicator only; no refinement, publication or epoch acceptance here.
using ResidualUv = std::array<double, 2>;
using ResidualPoint3 = std::array<double, 3>;
using ResidualFace = std::vector<std::size_t>;
using ResidualSurface = std::function<ResidualPoint3(const ResidualUv&)>;

struct MixedSurfaceResidual {
  std::size_t quadrilaterals = 0;
  std::size_t triangles = 0;
  std::size_t samples = 0;
  std::size_t worst_quad_face = 0;
  std::size_t worst_triangle_face = 0;
  ResidualUv worst_quad_sample_uv{0.0, 0.0};
  ResidualUv worst_triangle_sample_uv{0.0, 0.0};
  double maximum = 0.0;
  double rms = 0.0;
  double quad_maximum = 0.0;
  double triangle_maximum = 0.0;
  std::vector<double> face_maximum;
};

namespace detail {

template <typename Sample> void ForEachQuadResidualSample(Sample&& sample) {
  constexpr std::array<std::array<double, 2>, 5> positions{
      {{{0.5, 0.5}}, {{0.25, 0.25}}, {{0.75, 0.25}}, {{0.75, 0.75}}, {{0.25, 0.75}}}};
  for (const auto& position : positions) {
    const double s = position[0], t = position[1];
    sample(std::array<double, 4>{{(1 - s) * (1 - t), s * (1 - t), s * t, (1 - s) * t}});
  }
}

template <typename Uvs, typename Points, typename Face>
double SurfaceResidualSquare(const Uvs& uv, const Points& xyz, const Face& face,
                             const std::array<double, 4>& weights, const ResidualSurface& source,
                             ResidualUv& site) {
  site = {0.0, 0.0};
  ResidualPoint3 interpolated{0.0, 0.0, 0.0};
  for (std::size_t corner = 0; corner < face.size(); ++corner) {
    for (std::size_t axis = 0; axis < 2; ++axis)
      site[axis] += weights[corner] * uv[face[corner]][axis];
    for (std::size_t axis = 0; axis < 3; ++axis)
      interpolated[axis] += weights[corner] * xyz[face[corner]][axis];
  }
  const auto exact = source(site);
  double square = 0.0;
  for (std::size_t axis = 0; axis < 3; ++axis) {
    if (!std::isfinite(exact[axis]))
      throw std::invalid_argument("Nonfinite source surface oracle");
    const double delta = exact[axis] - interpolated[axis];
    square += delta * delta;
  }
  if (!std::isfinite(square))
    throw std::invalid_argument("Overflow in mixed surface residual");
  return square;
}

} // namespace detail

inline double MeasureQuadSurfaceMaximum(const std::array<ResidualUv, 4>& uv,
                                        const std::array<ResidualPoint3, 4>& xyz,
                                        const ResidualSurface& source) {
  constexpr std::array<std::size_t, 4> face{{0, 1, 2, 3}};
  double maximum = 0.0;
  detail::ForEachQuadResidualSample([&](const std::array<double, 4>& weights) {
    ResidualUv site;
    const double square = detail::SurfaceResidualSquare(uv, xyz, face, weights, source, site);
    maximum = std::max(maximum, std::sqrt(square));
  });
  return maximum;
}

inline MixedSurfaceResidual MeasureMixedSurfaceResidual(const std::vector<ResidualUv>& uv,
                                                        const std::vector<ResidualPoint3>& xyz,
                                                        const std::vector<ResidualFace>& faces,
                                                        const ResidualSurface& source) {
  auto require = [](bool ok, const char* message) {
    if (!ok)
      throw std::invalid_argument(message);
  };
  require(source && !faces.empty() && !uv.empty() && uv.size() == xyz.size(),
          "Incomplete mixed surface residual input");
  for (std::size_t i = 0; i < uv.size(); ++i) {
    require(std::isfinite(uv[i][0]) && std::isfinite(uv[i][1]) && uv[i][0] >= 0.0 &&
                uv[i][0] <= 1.0 && uv[i][1] >= 0.0 && uv[i][1] <= 1.0,
            "Invalid mixed residual UV coordinate");
    for (const double value : xyz[i])
      require(std::isfinite(value), "Nonfinite mixed residual physical coordinate");
  }
  constexpr std::array<std::array<double, 3>, 4> tri_weights{{{{1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0}},
                                                              {{0.6, 0.2, 0.2}},
                                                              {{0.2, 0.6, 0.2}},
                                                              {{0.2, 0.2, 0.6}}}};
  MixedSurfaceResidual result;
  result.face_maximum.reserve(faces.size());
  double sum_square = 0.0;
  bool seen_quad = false;
  bool seen_triangle = false;
  for (std::size_t index = 0; index < faces.size(); ++index) {
    const auto& face = faces[index];
    require(face.size() == 3 || face.size() == 4, "Unsupported mixed residual face arity");
    for (std::size_t k = 0; k < face.size(); ++k) {
      require(face[k] < uv.size(), "Out-of-range mixed residual face index");
      for (std::size_t j = 0; j < k; ++j)
        require(face[k] != face[j], "Duplicate mixed residual face vertex");
    }
    double face_maximum = 0.0;
    ResidualUv face_max_uv{0.0, 0.0};
    bool sampled_face = false;
    const auto sample = [&](const std::array<double, 4>& weights) {
      ResidualUv p;
      const double square = detail::SurfaceResidualSquare(uv, xyz, face, weights, source, p);
      const double error = std::sqrt(square);
      if (!sampled_face || error > face_maximum) {
        face_maximum = error;
        face_max_uv = p;
      }
      sampled_face = true;
      result.maximum = std::max(result.maximum, error);
      sum_square += square;
      require(std::isfinite(sum_square), "Overflow in total mixed residual error");
      ++result.samples;
    };
    if (face.size() == 4) {
      // Actual bilinear QUAD: four physical corners, five parametric samples.
      detail::ForEachQuadResidualSample(sample);
      if (!seen_quad || face_maximum > result.quad_maximum) {
        result.worst_quad_face = index;
        result.worst_quad_sample_uv = face_max_uv;
      }
      result.quad_maximum = std::max(result.quad_maximum, face_maximum);
      ++result.quadrilaterals;
      seen_quad = true;
    } else {
      // Genuine triangle: four barycentric probes, no implicit QUAD split.
      for (const auto& w : tri_weights)
        sample({{w[0], w[1], w[2], 0.0}});
      if (!seen_triangle || face_maximum > result.triangle_maximum) {
        result.worst_triangle_face = index;
        result.worst_triangle_sample_uv = face_max_uv;
      }
      result.triangle_maximum = std::max(result.triangle_maximum, face_maximum);
      ++result.triangles;
      seen_triangle = true;
    }
    result.face_maximum.push_back(face_maximum);
  }
  require(seen_quad && result.triangles > 0 && result.samples > 0,
          "Mixed residual requires nonempty physical QUAD and TRI populations");
  result.rms = std::sqrt(sum_square / static_cast<double>(result.samples));
  require(std::isfinite(result.rms) && std::isfinite(result.maximum),
          "Nonfinite mixed surface residual");
  return result;
}

} // namespace apmesh::quad::research
#endif // APMESH_QUAD_RESEARCH_MIXED_SURFACE_RESIDUAL_H
