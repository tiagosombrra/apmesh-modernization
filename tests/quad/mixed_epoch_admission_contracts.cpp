#include "mixed_epoch_admission.h"

#include <iostream>
#include <stdexcept>
#include <string>

using apmesh::quad::research::MixedEpochPreflight;
using apmesh::quad::research::MixedEpochReceipt;

namespace {
void Require(bool condition, const char* message = "Mixed synthetic epoch preflight failed") {
  if (!condition)
    throw std::runtime_error(message);
}
std::string Hash(char character) { return std::string(64, character); }

MixedEpochReceipt InitialSynthetic() {
  MixedEpochReceipt r;
  r.epoch = 0;
  r.model_sha256 = Hash('a');
  r.boundary_sha256 = Hash('b');
  r.mesh_sha256 = Hash('c');
  r.topology_sha256 = Hash('d');
  r.policy_id = "synthetic-preflight-v1";
  r.physical_nodes = 69;
  r.quadrilaterals = 42;
  r.triangles = 36;
  r.source_boundary_edges = 16;
  r.normalized_error = 0.8;
  r.min_signed_corner_jacobian = 0.5;
  r.min_physical_area = 0.002;
  r.independent_oracle_pass = true;
  r.actual_native_aft_pass = true;
  return r;
}

void ExpectRejected(MixedEpochPreflight& ledger, const MixedEpochReceipt& candidate,
                    std::size_t expected_states) {
  const std::string original_mesh = ledger.Latest().mesh_sha256;
  try {
    ledger.AdmitCandidate(candidate);
  } catch (const std::invalid_argument&) {
    Require(ledger.RecordedStates() == expected_states);
    Require(ledger.Latest().mesh_sha256 == original_mesh);
    return;
  }
  throw std::runtime_error("Malformed synthetic epoch was admitted");
}
}  // namespace

int main() {
  const auto baseline = InitialSynthetic();
  MixedEpochPreflight ledger(baseline);
  Require(ledger.RecordedStates() == 1);
  MixedEpochReceipt candidate = baseline;
  candidate.epoch = 1;
  candidate.parent_mesh_sha256 = baseline.mesh_sha256;
  candidate.mesh_sha256 = Hash('e');
  candidate.topology_sha256 = Hash('f');
  candidate.real_tree_edits = 1;
  candidate.normalized_error = 0.7;

  // Negative witnesses must never mutate the previous admission record.
  {
    auto bad = candidate; bad.topology_sha256 = baseline.topology_sha256;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.mesh_sha256 = baseline.mesh_sha256;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.parent_mesh_sha256 = Hash('1');
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.real_tree_edits = 0;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.normalized_error = baseline.normalized_error;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.model_sha256 = Hash('2');
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.independent_oracle_pass = false;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.actual_native_aft_pass = false;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.min_signed_corner_jacobian = 0.0;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.epoch = 3;
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.boundary_sha256 = "bad";
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.source_boundary_edges = 0;
    ExpectRejected(ledger, bad, 1);
  }

  {
    auto bad = candidate; bad.policy_id = "unreviewed-policy-swap";
    ExpectRejected(ledger, bad, 1);
  }
  {
    auto bad = candidate; bad.source_boundary_edges += 1;
    ExpectRejected(ledger, bad, 1);
  }

  // These two records are fabricated to test metadata transitions ONLY.
  ledger.AdmitCandidate(candidate);
  Require(ledger.RecordedStates() == 2);
  MixedEpochReceipt next = candidate;
  next.epoch = 2;
  next.parent_mesh_sha256 = candidate.mesh_sha256;
  next.mesh_sha256 = Hash('3');
  next.topology_sha256 = Hash('4');
  next.real_tree_edits = 2;
  next.normalized_error = 0.6;
  ledger.AdmitCandidate(next);
  Require(ledger.RecordedStates() == 3);
  Require(ledger.Latest().mesh_sha256 == next.mesh_sha256);
  std::cout << "QUAD_EPOCH_PREFLIGHT synthetic_states=3 negative_cases=14 "
               "lineage_verified=1 actual_adaptive_epochs=0\n";
}
