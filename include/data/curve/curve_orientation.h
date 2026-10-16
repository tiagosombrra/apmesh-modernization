#ifndef AP_MESH_CURVE_ORIENTATION_H
#define AP_MESH_CURVE_ORIENTATION_H

#include <utility>

namespace apmesh {
namespace geometry {

// Reversal is an involution between a patch-side parameter and its shared curve.
inline double OrientedParameter(double parameter, bool reversed) noexcept {
  return reversed ? 1.0 - parameter : parameter;
}

// Arc-length routines expect increasing limits in the stored curve direction.
inline std::pair<double, double> OrientedInterval(double first, double last,
                                                  bool reversed) noexcept {
  return reversed ? std::make_pair(1.0 - last, 1.0 - first) : std::make_pair(first, last);
}

} // namespace geometry
} // namespace apmesh

#endif
