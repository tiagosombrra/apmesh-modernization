#include "mixed_feedback_graph.h"

#include <iostream>

int main() {
  using apmesh::quad::BuildMixedFeedbackGraph;
  using apmesh::quad::FeedbackEdge;
  try {
    std::size_t nodes = 0, faces = 0, intervals = 0;
    if (!(std::cin >> nodes >> faces >> intervals) || !nodes || !faces || !intervals ||
        nodes > 1000000 || faces > 1000000 || intervals > 1000000)
      throw std::invalid_argument("Invalid mixed feedback probe counts");
    std::vector<std::vector<std::size_t>> connectivity(faces);
    for (auto& face : connectivity) {
      std::size_t corners = 0;
      if (!(std::cin >> corners) || (corners != 3 && corners != 4))
        throw std::invalid_argument("Invalid feedback probe face arity");
      face.resize(corners);
      for (auto& vertex : face)
        if (!(std::cin >> vertex))
          throw std::invalid_argument("Missing feedback probe face index");
    }
    std::vector<FeedbackEdge> contour(intervals);
    for (auto& edge : contour)
      if (!(std::cin >> edge.first >> edge.second))
        throw std::invalid_argument("Missing feedback probe contour interval");
    std::size_t extra = 0;
    if (std::cin >> extra || !std::cin.eof())
      throw std::invalid_argument("Trailing feedback probe input");

    const auto graph = BuildMixedFeedbackGraph(nodes, connectivity, contour);
    for (auto face : graph.interval_faces)
      std::cout << face << ' ';
    std::cout << '\n';
    for (const auto& neighbors : graph.neighbors) {
      for (auto node : neighbors)
        std::cout << node << ' ';
      std::cout << '\n';
    }
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
