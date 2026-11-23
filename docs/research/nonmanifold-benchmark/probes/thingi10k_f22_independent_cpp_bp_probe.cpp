// Independent C++17 BP index and boundary contract probe; not the APMesh generator.
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using Point = std::array<double,3>;
using Control = std::array<std::size_t,16>;
using Curve = std::array<Point,4>;
using Edge = std::pair<Point,Point>;

int main(int argc, char** argv) {
  try {
    if (argc != 2) throw std::runtime_error("Usage: f22_cpp_probe candidate.bp");
    std::ifstream file(argv[1]);
    if (!file) throw std::runtime_error("Cannot open input BP");
    std::vector<Point> vertices;
    std::vector<Control> patches;
    std::string line;
    std::size_t lineno=0;
    while (std::getline(file,line)) {
      ++lineno;
      std::istringstream in(line);
      std::string rec;
      if (!(in>>rec)) continue;
      if (rec=="v") {
        Point p{};
        if (!(in>>p[0]>>p[1]>>p[2]) || !std::isfinite(p[0]) ||
            !std::isfinite(p[1]) || !std::isfinite(p[2]))
          throw std::runtime_error("Malformed vertex");
        std::string trailing;
        if (in>>trailing) throw std::runtime_error("Unexpected vertex tail");
        vertices.push_back(p);
      } else if (rec=="p") {
        Control c{};
        for (auto& v:c) {
          long long index=-1;
          if (!(in>>index) || index<0 || static_cast<std::size_t>(index)>=vertices.size())
            throw std::runtime_error("Invalid patch index");
          v=static_cast<std::size_t>(index);
        }
        std::string trailing;
        if (in>>trailing) throw std::runtime_error("Unexpected patch tail");
        patches.push_back(c);
      } else {
        throw std::runtime_error("Unsupported record");
      }
      if (vertices.size()>1000000 || patches.size()>100000)
        throw std::runtime_error("BP exceeds research limits");
    }
    if (!file.eof() || vertices.empty() || patches.empty())
      throw std::runtime_error("Incomplete BP read");
    static constexpr int side[4][4]={ {0,1,2,3}, {3,7,11,15},
                                       {15,14,13,12}, {12,8,4,0} };
    std::map<Edge,std::vector<Curve>> usage;
    for (const auto& p:patches) {
      for (const auto& s:side) {
        Curve cc{vertices[p[s[0]]], vertices[p[s[1]]],
                 vertices[p[s[2]]], vertices[p[s[3]]]};
        Edge k=std::minmax(cc[0],cc[3]);
        usage[k].push_back(cc);
      }
    }
    for (const auto& [edge,uses]:usage) {
      if (uses.size()!=2) throw std::runtime_error("Unpaired or nonmanifold edge");
      for (std::size_t j=0;j<4;++j)
        if (uses[0][j]!=uses[1][3-j])
          throw std::runtime_error("Boundary control discontinuity");
    }
    std::cout << "{\"schema\":\"apmesh-f22-independent-cpp-bp-v1\",\"vertices\":"
              << vertices.size() << ",\"patches\":" << patches.size()
              << ",\"paired_edges\":" << usage.size()
              << ",\"original_apmesh_loader_executed\":false}" << std::endl;
    return 0;
  } catch (const std::exception& e) {
    std::cerr << "F22 C++ independent probe BLOCKED: " << e.what() << std::endl;
    return 2;
  }
}
