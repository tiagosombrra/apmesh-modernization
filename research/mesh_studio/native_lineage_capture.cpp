#include "native_lineage_capture.h"

#include "data/curve/curve_adaptive.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/element_adaptive.h"
#include "data/geometry.h"
#include "data/mesh/mesh_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_coons.h"
#include "data/point_adaptive.h"
#include "data/triangle_adaptive.h"

#include <array>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>

namespace apmesh::mesh_studio {
namespace {

constexpr unsigned int kMaxPatches = 1024;
constexpr unsigned int kMaxCurves = 16384;
constexpr unsigned long long kMaxFaces = 120000ULL;
constexpr unsigned long long kMaxNodes = 240000ULL;

void Require(bool pass, const char* reason) {
  if (!pass)
    throw std::runtime_error(reason);
}

std::string SafeOutputStem(const std::string& prefix) {
  const std::string filename = std::filesystem::path(prefix).filename().string();
  std::string stem;
  for (const char ch : filename) {
    if (stem.size() == 48)
      break;
    if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
        (ch >= '0' && ch <= '9') || ch == '-' || ch == '_')
      stem += ch;
    else
      stem += '_';
  }
  return stem.empty() ? "model" : stem;
}

void WriteLineage(const Geometry& source, MeshAdaptive& mesh,
                  int adaptive_step, int retry_index,
                  std::uint64_t session, std::uint64_t outer_epoch,
                  int global_retry, const std::string& output_prefix,
                  std::filesystem::path& pending) {
  const char* root_string = std::getenv("APMESH_RESEARCH_LINEAGE_DIR");
  if (root_string == nullptr || root_string[0] == '\0')
    return;
  Require(adaptive_step > 0 && retry_index >= 0, "invalid_committed_step");
  Require(source.GetNumberPatches() > 0 &&
              source.GetNumberPatches() <= kMaxPatches &&
              source.GetNumberCurves() <= kMaxCurves,
          "source_patch_or_curve_limit");
  Require(mesh.GetNumberSubMeshesAdaptive() == source.GetNumberPatches(),
          "submesh_patch_count_mismatch");
  const bool has_outer = session != 0 || outer_epoch != 0 || global_retry >= 0;
  Require(!has_outer || (session > 0 && outer_epoch > 0 && global_retry >= 0),
          "partial_outer_scope");

  std::unordered_map<const CurveAdaptive*, unsigned int> curve_slots;
  curve_slots.reserve(source.GetNumberCurves());
  for (unsigned int i = 0; i < source.GetNumberCurves(); ++i) {
    const CurveAdaptive* curve = source.GetCurve(i);
    Require(curve != nullptr && curve_slots.emplace(curve, i).second,
            "invalid_source_curve_slot");
  }

  std::ostringstream text;
  text << std::setprecision(17);
  text << "{\"schema\":\"apmesh.meshstudio.r2712.native_lineage_ndjson.v1\","
       << "\"type\":\"accepted_commit\",\"step\":" << adaptive_step
       << ",\"retry\":" << retry_index
       << ",\"session\":" << session
       << ",\"outer_epoch\":" << outer_epoch
       << ",\"global_retry\":" << global_retry
       << ",\"has_typed_outer_scope\":" << (has_outer ? "true" : "false")
       << ",\"source_patch_count\":" << source.GetNumberPatches()
       << ",\"source_curve_count\":" << source.GetNumberCurves()
       << ",\"native_id_semantics\":\"snapshot_local_not_cross_epoch\","
       << "\"face_record_semantics\":\"native_element_id_plus_patch_slot_not_obj_ordinal\","
       << "\"r2717_corner_observer\":\"native_postcommit_source_curve_endpoints_v1\","
       << "\"scientific_lod_admitted\":false}\n";

  unsigned long long total_faces = 0ULL;
  unsigned long long total_nodes = 0ULL;
  for (unsigned int patch_slot = 0; patch_slot < source.GetNumberPatches(); ++patch_slot) {
    const Patch* patch = source.GetPatch(patch_slot);
    SubMesh* sub = mesh.GetSubMeshAdaptiveByPosition(patch_slot);
    Require(patch != nullptr && sub != nullptr && sub->GetPatch() == patch,
            "native_patch_submesh_ownership_mismatch");
    const auto* coons = dynamic_cast<const PatchCoons*>(patch);
    Require(coons != nullptr, "unsupported_native_source_patch");
    const auto node_count = sub->GetNumberNos();
    const auto face_count = sub->GetNumberElements();
    total_nodes += node_count;
    total_faces += face_count;
    Require(total_nodes <= kMaxNodes && total_faces <= kMaxFaces,
            "native_lineage_size_limit");

    text << "{\"type\":\"patch\",\"patch_slot\":" << patch_slot
         << ",\"native_patch_id\":" << patch->GetId()
         << ",\"node_count\":" << node_count
         << ",\"face_count\":" << face_count
         << ",\"source_curves\":[";
    for (unsigned int edge = 0; edge < coons->GetNumBerCurves(); ++edge) {
      const CurveAdaptive* curve = coons->GetCurve(edge);
      auto found = curve_slots.find(curve);
      Require(curve != nullptr && found != curve_slots.end(),
              "curve_not_owned_by_source_geometry");
      if (edge)
        text << ',';
      // Record the original live source curve endpoints without sorting or
      // modifying either the source samples or the accepted native mesh.
      const auto* parametric = dynamic_cast<const CurveAdaptiveParametric*>(curve);
      Require(parametric != nullptr, "r2717_nonparametric_source_curve");
      const unsigned int samples = curve->GetNumBerPoints();
      Require(samples >= 2 && parametric->parameters_.size() == samples,
              "r2717_original_curve_sample_parameter_count_mismatch");
      // GetPoint is a read-only accessor lacking a const overload. It neither
      // changes the source list nor creates/retains a new native point.
      const PointAdaptive* first = const_cast<CurveAdaptive*>(curve)->GetPoint(0);
      const PointAdaptive* last = const_cast<CurveAdaptive*>(curve)->GetPoint(samples - 1);
      Require(first != nullptr && last != nullptr,
              "r2717_missing_original_curve_corner_point");
      const std::array<const PointAdaptive*, 2> endpoints{{first, last}};
      const std::array<double, 2> parameters{{
          parametric->parameters_.front(), parametric->parameters_.back()}};
      text << "{\"edge_slot\":" << edge << ",\"source_curve_slot\":"
           << found->second << ",\"native_curve_id\":" << curve->GetId()
           << ",\"reversed\":" << (coons->IsCurveReversed(edge) ? "true" : "false")
           << ",\"reported_curve_patch_observers\":" << curve->GetNumBerPatches()
           << ",\"r2717_original_curve_endpoints\":[";
      for (unsigned int index = 0; index < 2; ++index) {
        const PointAdaptive* p = endpoints[index];
        Require(std::isfinite(parameters[index]) && std::isfinite(p->GetX()) &&
                    std::isfinite(p->GetY()) && std::isfinite(p->GetZ()),
                "r2717_nonfinite_original_source_curve_sample");
        if (index != 0)
          text << ',';
        text << "{\"stored_index\":" << (index == 0 ? 0 : samples - 1)
             << ",\"stored_parameter\":" << parameters[index]
             << ",\"original_sample_id\":" << p->GetId()
             << ",\"xyz\":[" << p->GetX() << ',' << p->GetY()
             << ',' << p->GetZ() << "]}";
      }
      text << "]}";
    }
    text << "]}\n";

    for (unsigned int element_slot = 0; element_slot < face_count; ++element_slot) {
      ElementAdaptive* base = sub->GetElement(element_slot);
      auto* triangle = dynamic_cast<TriangleAdaptive*>(base);
      Require(triangle != nullptr, "unsupported_native_face_type");
      const std::array<std::tuple<double, double>, 3> uv{{
          triangle->GetParametersN1(), triangle->GetParametersN2(),
          triangle->GetParametersN3()}};
      text << "{\"type\":\"face\",\"patch_slot\":" << patch_slot
           << ",\"native_patch_id\":" << patch->GetId()
           << ",\"element_slot\":" << element_slot
           << ",\"native_element_id\":" << triangle->GetId()
           << ",\"vertices\":[";
      for (unsigned int corner = 0; corner < 3; ++corner) {
        const PointAdaptive node = triangle->GetVertexPoint(corner + 1);
        const double u = std::get<0>(uv[corner]);
        const double v = std::get<1>(uv[corner]);
        Require(std::isfinite(node.GetX()) && std::isfinite(node.GetY()) &&
                    std::isfinite(node.GetZ()) && std::isfinite(u) && std::isfinite(v),
                "nonfinite_native_face_geometry");
        if (corner)
          text << ',';
        text << "{\"native_node_id\":" << node.GetId()
             << ",\"xyz\":[" << node.GetX() << ',' << node.GetY()
             << ',' << node.GetZ() << "],\"uv\":[" << u << ',' << v << "]}";
      }
      text << "]}\n";
    }
  }
  text << "{\"type\":\"complete\",\"patch_records\":"
       << source.GetNumberPatches() << ",\"face_records\":" << total_faces
       << ",\"node_records_counted_per_patch\":" << total_nodes
       << ",\"fully_accepted_source_face_lineage_across_epochs\":false}\n";

  const std::filesystem::path root(root_string);
  Require(!root.empty(), "missing_lineage_output_directory");
  const std::string basename = SafeOutputStem(output_prefix) + "_accepted_step_" +
      std::to_string(adaptive_step) + "_outer_" + std::to_string(outer_epoch) + ".ndjson";
  std::filesystem::create_directories(root);
  const std::filesystem::path destination = root / basename;
  pending = root / (basename + ".pending");
  Require(!std::filesystem::exists(destination) && !std::filesystem::exists(pending),
          "lineage_output_already_exists");
  {
    std::ofstream output(pending, std::ios::binary | std::ios::out);
    Require(output.good(), "cannot_open_pending_lineage");
    const std::string bytes = text.str();
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.flush();
    Require(output.good(), "cannot_write_pending_lineage");
  }
  std::filesystem::rename(pending, destination);
  pending.clear();
  std::cerr << "R2712_NATIVE_LINEAGE_WRITTEN=" << destination.string()
            << " step=" << adaptive_step << " faces=" << total_faces
            << " patches=" << source.GetNumberPatches()
            << " outer_scope=" << (has_outer ? 1 : 0) << '\n';
}

} // namespace

void WriteAcceptedEpochIfEnabled(const Geometry& source, MeshAdaptive& accepted_mesh,
                                 int adaptive_step, int retry_index,
                                 std::uint64_t session, std::uint64_t outer_epoch,
                                 int global_retry,
                                 const std::string& output_prefix) noexcept {
  std::filesystem::path pending;
  try {
    WriteLineage(source, accepted_mesh, adaptive_step, retry_index, session,
                 outer_epoch, global_retry, output_prefix, pending);
  } catch (const std::exception& error) {
    // Observation never changes an accepted/rejected native TRI decision.
    if (!pending.empty()) {
      std::error_code ignored;
      std::filesystem::remove(pending, ignored);
    }
    std::cerr << "R2712_NATIVE_LINEAGE_ERROR=" << error.what() << '\n';
  } catch (...) {
    // C++ observation failures are explicitly unqualified, never silent.
    std::cerr << "R2712_NATIVE_LINEAGE_ERROR=unknown_failure\n";
  }
}

} // namespace apmesh::mesh_studio
