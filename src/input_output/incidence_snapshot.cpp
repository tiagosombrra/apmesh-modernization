#include "input_output/incidence_snapshot.h"

#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <limits>
#include <locale>
#include <stdexcept>
#include <unordered_map>

#include "data/mesh/mesh_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_bezier.h"
#include "data/triangle_adaptive.h"

namespace apmesh {
namespace io {
namespace {
void WriteNumber(std::ostream& stream, double value) {
  if (!std::isfinite(value)) {
    throw std::runtime_error("Cannot export a non-finite incidence coordinate");
  }
  stream << value;
}

void WritePoint(std::ostream& stream, const PointAdaptive& point) {
  WriteNumber(stream, point.GetX());
  stream << ',';
  WriteNumber(stream, point.GetY());
  stream << ',';
  WriteNumber(stream, point.GetZ());
}
} // namespace

void WriteIncidenceSnapshot(const MeshAdaptive& mesh, const std::string& path, int step) {
  std::ofstream stream(path);
  stream.exceptions(std::ios::failbit | std::ios::badbit);
  stream.imbue(std::locale::classic());
  stream << std::setprecision(std::numeric_limits<double>::max_digits10);
  stream << "{\"schema\":\"apmesh-incidence-v1\",\"step\":" << step << ",\"patches\":[";
  std::unordered_map<const CurveAdaptive*, unsigned int> curve_ids;
  for (unsigned int index = 0; index < mesh.GetNumberSubMeshesAdaptive(); ++index) {
    const SubMesh* submesh = mesh.GetSubMeshAdaptiveByPosition(index);
    if (submesh == nullptr) {
      throw std::runtime_error("Cannot export a missing submesh incidence");
    }
    const auto* patch = dynamic_cast<const PatchBezier*>(submesh->GetPatch());
    if (patch == nullptr || patch->GetNumBerCurves() != 4) {
      throw std::runtime_error("Incidence snapshots require four-sided Bezier patches");
    }
    if (index != 0)
      stream << ',';
    stream << "{\"index\":" << index << ",\"curves\":[";
    for (unsigned int slot = 0; slot < 4; ++slot) {
      const CurveAdaptive* curve = patch->GetCurve(slot);
      if (curve == nullptr)
        throw std::runtime_error("Cannot export a missing curve incidence");
      const auto inserted = curve_ids.emplace(curve, static_cast<unsigned int>(curve_ids.size()));
      if (slot != 0)
        stream << ',';
      stream << inserted.first->second;
    }
    const std::array<PointAdaptive, 16> controls = {
        patch->GetPt00(), patch->GetPt10(), patch->GetPt20(), patch->GetPt30(),
        patch->GetPt01(), patch->GetPt11(), patch->GetPt21(), patch->GetPt31(),
        patch->GetPt02(), patch->GetPt12(), patch->GetPt22(), patch->GetPt32(),
        patch->GetPt03(), patch->GetPt13(), patch->GetPt23(), patch->GetPt33()};
    stream << "],\"control_points\":[";
    for (std::size_t control = 0; control < controls.size(); ++control) {
      if (control != 0)
        stream << ',';
      stream << '[';
      WritePoint(stream, controls[control]);
      stream << ']';
    }
    stream << "],\"nodes\":[";
    for (unsigned int node = 0; node < submesh->GetNumberNos(); ++node) {
      const NodeAdaptive* point = submesh->GetNoh(node);
      if (point == nullptr)
        throw std::runtime_error("Cannot export a missing patch node");
      if (node != 0)
        stream << ',';
      stream << '[' << point->GetId() << ',';
      WritePoint(stream, *point);
      stream << ']';
    }
    stream << "],\"faces\":[";
    for (unsigned int face = 0; face < submesh->GetNumberElements(); ++face) {
      const auto* triangle = dynamic_cast<const TriangleAdaptive*>(submesh->GetElement(face));
      if (triangle == nullptr)
        throw std::runtime_error("Incidence snapshot requires triangles");
      const std::array<std::tuple<double, double>, 3> parameters = {
          triangle->GetParametersN1(), triangle->GetParametersN2(), triangle->GetParametersN3()};
      if (face != 0)
        stream << ',';
      stream << '[' << face;
      for (unsigned int corner = 0; corner < 3; ++corner) {
        const NodeAdaptive point = triangle->GetNoh(corner + 1);
        stream << ",[" << point.GetId() << ',';
        WriteNumber(stream, std::get<0>(parameters[corner]));
        stream << ',';
        WriteNumber(stream, std::get<1>(parameters[corner]));
        stream << ',';
        WritePoint(stream, point);
        stream << ']';
      }
      stream << ']';
    }
    stream << "]}";
  }
  stream << "]}\n";
  stream.close();
}

} // namespace io
} // namespace apmesh
