#!/usr/bin/env python3
"""Guard the bounded Model ownership delta against its immutable original."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = "cd3dd8c7e269d4384f62109ef28334184c64ce89"
FILES = ["include/data/model.h", "src/data/model.cpp"]


def code(text):
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*#include[^\n]*", "", text, flags=re.M)
    return re.sub(r"\s+", "", text)


def replace_once(text, before, after):
    before, after = code(before), code(after)
    if text.count(before) != 1:
        raise ValueError("Changed Model ownership contract: " + before)
    return text.replace(before, after, 1)


def verify(originals, candidates):
    header = code(candidates[FILES[0]])
    header = replace_once(header, """
      Model(const Model&) = delete;
      Model& operator=(const Model&) = delete;
      Model(Model&& other) noexcept;
      Model& operator=(Model&& other) noexcept;
    """, "")
    header = replace_once(header, "void InsertMeshAdaptive(std::unique_ptr<MeshAdaptive> mesh_adaptive);", "")
    header = replace_once(header, "std::vector<std::unique_ptr<MeshAdaptive>> meshes_;", "std::vector<MeshAdaptive*> meshes_;")
    source = code(candidates[FILES[1]])
    source = replace_once(source, "Model::Model(Geometry* geometry) : geometry_(geometry) {}", "Model::Model(Geometry* geometry) { this->geometry_ = geometry; }")
    source = replace_once(source, "Model::~Model() { while (!meshes_.empty()) meshes_.pop_back(); }", """
      Model::~Model() {
        while (!this->meshes_.empty()) {
          MeshAdaptive* mesh = this->meshes_.back();
          this->meshes_.pop_back();
          delete mesh;
        }
      }
    """)
    source = replace_once(source, """
      Model::Model(Model&& other) noexcept : geometry_(std::exchange(other.geometry_, nullptr)) {
        meshes_.swap(other.meshes_);
      }
      Model& Model::operator=(Model&& other) noexcept {
        if (this == &other) return *this;
        Model incoming(std::move(other));
        std::swap(geometry_, incoming.geometry_);
        meshes_.swap(incoming.meshes_);
        return *this;
      }
    """, "")
    source = replace_once(source, """
      void Model::InsertMeshAdaptive(MeshAdaptive* mesh_adaptive) {
        InsertMeshAdaptive(std::unique_ptr<MeshAdaptive>(mesh_adaptive));
      }
      void Model::InsertMeshAdaptive(std::unique_ptr<MeshAdaptive> mesh_adaptive) {
        meshes_.push_back(std::move(mesh_adaptive));
      }
    """, "void Model::InsertMeshAdaptive(MeshAdaptive* mesh_adaptive) { this->meshes_.push_back(mesh_adaptive); }")
    source = replace_once(source, "this->meshes_[position].get()", "this->meshes_[position]")
    normalized = {FILES[0]: header, FILES[1]: source}
    for name in FILES:
        if normalized[name] != code(originals[name]):
            raise ValueError("Unexpected Model interface, getter, borrowing or order delta: " + name)
    return {name: hashlib.sha256(text.encode()).hexdigest() for name, text in normalized.items()}


def audit(root, original_root=None):
    originals = {name: ((original_root/name).read_text(encoding="utf-8") if original_root else
                       subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=root).decode("utf-8")) for name in FILES}
    candidates = {name: (root/name).read_text(encoding="utf-8") for name in FILES}
    preserved = verify(originals, candidates)
    mutations = [("meshes_.pop_back();", "meshes_.clear();"),
                 ("if (this == &other)", "if (false)"),
                 ("std::exchange(other.geometry_, nullptr)", "other.geometry_"),
                 ("meshes_.push_back(std::move(mesh_adaptive));", "meshes_.insert(meshes_.begin(), std::move(mesh_adaptive));"),
                 ("position < this->meshes_.size()", "position <= this->meshes_.size()"),
                 ("std::unique_ptr<MeshAdaptive>(mesh_adaptive)", "std::unique_ptr<MeshAdaptive>()")]
    for before, after in mutations:
        changed = dict(candidates)
        if candidates[FILES[1]].count(before) != 1:
            raise ValueError("Independent Model mutation was not applied exactly once")
        changed[FILES[1]] = changed[FILES[1]].replace(before, after, 1)
        try:
            verify(originals, changed)
        except ValueError:
            continue
        raise ValueError("Independent Model mutation escaped preservation guard")
    return {"status": "passed", "original_revision": BASE, "rejected_mutations": len(mutations),
            "preserved_tokens_sha256": preserved,
            "source_identities": {label: {name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items()}
                                  for label, files in [("original", originals), ("candidate", candidates)]},
            "scope": "Two actual Model files. Exact exclusive storage, owning/raw handoff, copy prohibition, nonthrowing moves and reverse retirement only. All other getter, borrowing and ordering tokens preserved; runtime fault and live comparison gates are separate."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=Path("."))
    parser.add_argument("--original-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.candidate_root, args.original_root)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(result))
