#ifndef APMESH_ADAPTER_DOMAIN_UV_CACHE_H
#define APMESH_ADAPTER_DOMAIN_UV_CACHE_H

#include "../crab_mesh/aft/face.h"

#include <memory>
#include <tuple>

namespace apmesh::adaptation {

// Exclusive owner of fresh UV faces, their three distinct copied endpoints and
// their midpoint caches. This is not a physical mesh and never adopts its nodes.
// Declare before the AFT consumer so faces survive that consumer's unwinding.
class DomainUvCache {
public:
  using Face = Par2DJMesh::Basics::Face;
  using Vertex = Par2DJMesh::Basics::Vertex;
  using FaceList = Par2DJMesh::Basics::FaceList;
  using Parameters = std::tuple<double, double>;

  DomainUvCache() = default;
  ~DomainUvCache() noexcept { Clear(); }
  DomainUvCache(const DomainUvCache&) = delete;
  DomainUvCache& operator=(const DomainUvCache&) = delete;
  DomainUvCache(DomainUvCache&&) = delete;
  DomainUvCache& operator=(DomainUvCache&&) = delete;

  static std::unique_ptr<Face> MakeFace(const Parameters& first, const Parameters& second,
                                        const Parameters& third, long id) {
    auto a = std::make_unique<Vertex>(std::get<0>(first), std::get<1>(first));
    auto b = std::make_unique<Vertex>(std::get<0>(second), std::get<1>(second));
    auto c = std::make_unique<Vertex>(std::get<0>(third), std::get<1>(third));
    auto face = std::make_unique<Face>(a.get(), b.get(), c.get(), id);
    a.release();
    b.release();
    c.release();
    return face;
  }

  // The nonnull face and its endpoints must be exclusively owned, as in MakeFace.
  // A failed list append destroys the pending face and preserves the prior list.
  void Append(std::unique_ptr<Face> face) {
    faces_.push_back(face.get());
    face.release();
  }

  // Borrowers may update face fields, but must not change membership or owners.
  FaceList& BorrowFaces() noexcept { return faces_; }
  const FaceList& BorrowFaces() const noexcept { return faces_; }

  void Clear() noexcept {
    while (!faces_.empty()) {
      Face* face = faces_.front();
      faces_.pop_front();
      delete face;
    }
  }

private:
  FaceList faces_;
};

} // namespace apmesh::adaptation

#endif // APMESH_ADAPTER_DOMAIN_UV_CACHE_H
