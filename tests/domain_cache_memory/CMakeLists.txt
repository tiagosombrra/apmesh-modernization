cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_domain_cache_memory LANGUAGES CXX)
endif()
get_filename_component(default_cache_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_CACHE_SOURCE_ROOT "${default_cache_root}" CACHE PATH "Production tree for UV cache qualification")
option(AP_MESH_CACHE_ASAN "Instrument the isolated MSVC UV cache probe" OFF)
set(cache_sources
  crab_mesh/aft/shape.cpp crab_mesh/aft/vertex.cpp crab_mesh/aft/edge.cpp
  crab_mesh/aft/face.cpp crab_mesh/aft/boundary.cpp crab_mesh/aft/quadtree_cell.cpp
  crab_mesh/aft/quadtree.cpp crab_mesh/aft/advancing_front.cpp
  data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
  data/point_adaptive.cpp data/vector_adaptive.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM cache_sources PREPEND "${AP_MESH_CACHE_SOURCE_ROOT}/src/")
add_executable(domain_cache_probe probe.cpp ${cache_sources})
target_compile_features(domain_cache_probe PRIVATE cxx_std_17)
target_include_directories(domain_cache_probe PRIVATE "${AP_MESH_CACHE_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(domain_cache_probe PRIVATE /utf-8 /W4 /EHsc)
  target_compile_definitions(domain_cache_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CACHE_ASAN)
    target_compile_options(domain_cache_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(domain_cache_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(domain_cache_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
