#include "article_mixed_front.h"
#include <iostream>
#include <stdexcept>

using namespace apmesh::quad;
void Require(bool ok, const char* reason) {
  if (!ok)
    throw std::runtime_error(reason);
}
int main() {
  const std::vector<ArticleMixedFront::Box> cells{{0, 0, 1, 1}};
  const std::vector<UvVertex> square{{0, 0}, {1, 0}, {1, 1}, {0, 1}};
  const auto quad = ArticleMixedFront({}, square, cells).Run();
  Require(quad.faces.size() == 1 && quad.faces[0].size() == 4 && quad.commits.size() == 1,
          "Square must close as one prospective QUAD commit");
  Require(quad.commits[0].before.size() == 4 && quad.commits[0].selected_side >= 0,
          "QUAD selection must precede the four-edge front update");
  std::size_t measured = 0;
  const auto prefer_triangle = [&](const auto& vertices, const auto& polygon, const auto& best) {
    Require(vertices.size() == square.size() && polygon.size() == 4 &&
                best == quad.commits.front().best,
            "Shape callback needs the selected QUAD and initial TRI");
    ++measured;
    return true;
  };
  const auto shape_trial =
      ArticleMixedFront({}, square, cells, false, {}, {}, {}, prefer_triangle).Run();
  Require(measured == 1 && shape_trial.faces.size() == 2 && shape_trial.commits.size() == 2 &&
              shape_trial.commits[0].selected_side == -1 &&
              shape_trial.commits[0].quad_replaced_by_initial_triangle &&
              !shape_trial.commits[1].quad_replaced_by_initial_triangle,
          "Shape fallback must contract the initial TRI and preserve its QUAD witness");
  Require(std::equal(shape_trial.faces[0].begin(), shape_trial.faces[0].end(),
                     quad.commits[0].best.begin(), quad.commits[0].best.end()) &&
              std::equal(quad.faces[0].begin(), quad.faces[0].end(),
                         shape_trial.commits[0].quad_replaced_by_initial_triangle->begin(),
                         shape_trial.commits[0].quad_replaced_by_initial_triangle->end()),
          "Shape fallback changed the referenced front or the selected sites");
  const auto keep_quad = [](const auto&, const auto&, const auto&) { return false; };
  const auto kept = ArticleMixedFront({}, square, cells, false, {}, {}, {}, keep_quad).Run();
  Require(kept.faces == quad.faces && !kept.commits[0].quad_replaced_by_initial_triangle,
          "Failed shape fallback predicate must preserve the QUAD");
  const std::vector<UvVertex> triangle{{0, 0}, {1, 0}, {0, 1}};
  const auto tri = ArticleMixedFront({}, triangle, cells).Run();
  Require(tri.faces.size() == 1 && tri.faces[0].size() == 3 && tri.commits[0].selected_side == -1,
          "No neighbor must retain a TRI");
  const std::vector<UvVertex> poor{{0, 0}, {1, 0}, {0.1, 0.1}, {0, 1}};
  const auto fallback = ArticleMixedFront({}, poor, cells).Run();
  Require(fallback.faces.size() == 2 && fallback.faces[0].size() == 3,
          "Concave or poor union must retain TRI");
  UvMesh seed{{{0.25, 0.25}, {0.75, 0.25}, {0.75, 0.75}, {0.25, 0.75}}, {{{0, 1, 2, 3}}}};
  const auto island = ArticleMixedFront(seed, square, cells).Run();
  Require(island.seed_quads == 1 && island.faces.size() > 1 && island.commits.size() > 1,
          "Hole contour must contract onto the native interior");
  bool aborted = false;
  try {
    (void)ArticleMixedFront(seed, square, cells).Run(1);
  } catch (const std::runtime_error&) {
    aborted = true;
  }
  Require(aborted && seed.vertices.size() == 4 && seed.quads.size() == 1,
          "Precommit failure must preserve caller-owned input");
  const auto retry = ArticleMixedFront(seed, square, cells).Run();
  Require(retry.faces == island.faces, "Fresh retry must preserve deterministic choices");
  std::cout << "ARTICLE_FRONT_CONTRACTS square_quad=1 retained_tri=1 rejected_union=1 island=1 "
               "precommit_abort=1 deterministic_retry=1 shape_fallback=1 shape_kept_quad=1\n";
}
