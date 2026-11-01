#include "crab_mesh/aft/face.h"

#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>

double TOLERANCE_AFT = 1e-8;
double TOLERANCE = 1e-8;
double DELTA = 1e-8;
double EPSYLON = 1e-8;
std::string USE_TEMPLATE = "y";
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0.0;
double AFT_LOCAL_POSTPROCESS_BLEND = 0.5;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0.0;
double QUADTREE_LOW_QUALITY_H_FACTOR = 1.0;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0.0;

namespace {
bool observe_allocations = false;
bool deny_allocations = false;
std::size_t allocation_attempts = 0;
std::size_t denied_allocations = 0;

void* Allocate(std::size_t size) {
  if (observe_allocations) {
    ++allocation_attempts;
    if (deny_allocations) {
      ++denied_allocations;
      throw std::bad_alloc();
    }
  }
  while (true) {
    if (void* result = std::malloc(size ? size : 1))
      return result;
    const auto handler = std::get_new_handler();
    if (!handler)
      throw std::bad_alloc();
    handler();
  }
}

struct AllocationWindow {
  explicit AllocationWindow(bool deny) {
    allocation_attempts = denied_allocations = 0;
    deny_allocations = deny;
    observe_allocations = true;
  }
  ~AllocationWindow() { observe_allocations = deny_allocations = false; }
};

void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

std::uint64_t Bits(double value) {
  std::uint64_t bits = 0;
  static_assert(sizeof(bits) == sizeof(value));
  std::memcpy(&bits, &value, sizeof(bits));
  return bits;
}

struct DetachFace {
  Face& face;
  ~DetachFace() { face.DetachVertices(); }
};

using Triangle = std::array<double, 6>;
std::uint64_t random_state = UINT64_C(0x9e3779b97f4a7c15);
double Dyadic() {
  random_state ^= random_state << 13;
  random_state ^= random_state >> 7;
  random_state ^= random_state << 17;
  return static_cast<double>(static_cast<int>(random_state % 20001) - 10000) / 64.0;
}

void CheckTriangle(const Triangle& coordinates, unsigned case_id, bool reference, int analytic) {
  constexpr unsigned orders[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2},
                                     {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
  for (unsigned permutation = 0; permutation < 6; ++permutation) {
    const auto* order = orders[permutation];
    Vertex a(coordinates[2 * order[0]], coordinates[2 * order[0] + 1], 11);
    Vertex b(coordinates[2 * order[1]], coordinates[2 * order[1] + 1], 17);
    Vertex c(coordinates[2 * order[2]], coordinates[2 * order[2] + 1], 23);
    Edge sentinel;
    a.addAdjacentEdge(&sentinel);
    b.addAdjacentEdge(&sentinel);
    c.addAdjacentEdge(&sentinel);
    Face face(&a, &b, &c, 31);
    DetachFace detach{face};
    auto* midpoint = face.getMid();
    const auto midpoint_x = Bits(midpoint->getX()), midpoint_y = Bits(midpoint->getY());
    std::unique_ptr<Vertex> incenter(face.incenter()), circumcenter(face.circumcenter());
    double quality = 0.0;
    std::size_t allocations = 0;
    {
      AllocationWindow window(false);
      quality = face.quality();
      allocations = allocation_attempts;
    }
    Require(reference ? allocations > 0 : allocations == 0, "Quality allocation contract changed");
    if (!reference) {
      double denied_quality = 0.0;
      {
        AllocationWindow window(true);
        denied_quality = face.quality();
        Require(allocation_attempts == 0 && denied_allocations == 0,
                "Quality attempted allocation under denial");
      }
      Require(Bits(quality) == Bits(denied_quality), "Denial changed quality bits");
    }
    Require(face.getV1() == &a && face.getV2() == &b && face.getV3() == &c &&
                face.getMid() == midpoint && Bits(midpoint->getX()) == midpoint_x &&
                Bits(midpoint->getY()) == midpoint_y && face.getId() == 31,
            "Quality changed face ownership or cache");
    Require(a.getId() == 11 && b.getId() == 17 && c.getId() == 23 &&
                a.getAdjacentEdges().count(&sentinel) == 1 &&
                b.getAdjacentEdges().count(&sentinel) == 1 &&
                c.getAdjacentEdges().count(&sentinel) == 1,
            "Quality changed caller identity or adjacency");
    if (analytic >= 0) {
      const double expected = analytic == 0 ? 1.0 : 2.0 * (std::sqrt(2.0) - 1.0);
      Require(std::isfinite(quality) && std::abs(quality - expected) <= 1e-13,
              "Quality disagrees with independent analytic triangle");
    }
    std::printf("face_quality case=%u permutation=%u quality=%016llx inx=%016llx iny=%016llx "
                "circx=%016llx circy=%016llx allocations=%zu observers=1\n",
                case_id, permutation, static_cast<unsigned long long>(Bits(quality)),
                static_cast<unsigned long long>(Bits(incenter->getX())),
                static_cast<unsigned long long>(Bits(incenter->getY())),
                static_cast<unsigned long long>(Bits(circumcenter->getX())),
                static_cast<unsigned long long>(Bits(circumcenter->getY())), allocations);
  }
}
} // namespace

void* operator new(std::size_t size) { return Allocate(size); }
void* operator new[](std::size_t size) { return Allocate(size); }
void operator delete(void* pointer) noexcept { std::free(pointer); }
void operator delete[](void* pointer) noexcept { std::free(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { std::free(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { std::free(pointer); }

unsigned char* AllocateQualityControl();

int main(int argc, char** argv) {
  try {
    Require(argc == 2, "Expected snapshot or reference");
    const bool reference = std::strcmp(argv[1], "reference") == 0;
    Require(reference || std::strcmp(argv[1], "snapshot") == 0, "Unknown quality probe mode");
    const double huge = std::numeric_limits<double>::max();
    const double tiny = std::numeric_limits<double>::denorm_min();
    const std::array<Triangle, 13> fixed{{{0, 0, 1, 0, 0.5, std::sqrt(3.0) / 2.0},
                                          {0, 0, 1, 0, 0, 1},
                                          {0, 0, 3, 0, 0.2, 0.1},
                                          {0, 0, 1, 0, 2, 0},
                                          {0, 0, 0, 0, 0, 0},
                                          {-0.0, 0.0, 1, -0.0, 0, 1},
                                          {0, 0, 1, 0, 0.5, std::ldexp(1.0, -40)},
                                          {huge, 0, huge, 1, -huge, 0},
                                          {0, 0, tiny, 0, 0, tiny},
                                          {0, 0, 1e-140, 0, 0, 1e-140},
                                          {0, 0, 1e140, 0, 0, 1e140},
                                          {1e12, -1e12, 1e12 + 1, -1e12, 1e12, -1e12 + 1},
                                          {-3, 7, 2, -1, -6, 4}}};
    unsigned cases = 0;
    for (const auto& triangle : fixed) {
      const int analytic = cases < 2 ? static_cast<int>(cases) : -1;
      CheckTriangle(triangle, cases++, reference, analytic);
    }
    for (unsigned index = 0; index < 128; ++index) {
      Triangle triangle{};
      const int exponent = std::array<int, 5>{-80, -20, 0, 20, 80}[index % 5];
      for (auto& coordinate : triangle)
        coordinate = std::ldexp(Dyadic(), exponent);
      CheckTriangle(triangle, cases++, reference, -1);
    }
    bool denied = false;
    {
      AllocationWindow window(true);
      try {
        std::unique_ptr<unsigned char[]> control(AllocateQualityControl());
      } catch (const std::bad_alloc&) {
        denied = allocation_attempts == 1 && denied_allocations == 1;
      }
    }
    Require(denied, "Independent real allocation was not denied");
    std::printf("face_quality_complete cases=%u permutations=6 hook_denials=1\n", cases);
    return 0;
  } catch (const std::exception& error) {
    std::fprintf(stderr, "%s\n", error.what());
    return 1;
  }
}
