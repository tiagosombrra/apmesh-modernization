cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_uv_lifetime LANGUAGES CXX)
endif()
get_filename_component(default_uv_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_UV_SOURCE_ROOT "${default_uv_root}" CACHE PATH "Production tree for the UV lifetime probe")
option(AP_MESH_UV_ASAN "Instrument the narrow MSVC UV lifetime probe" OFF)
set(uv_sources
  crab_mesh/aft/shape.cpp crab_mesh/aft/vertex.cpp crab_mesh/aft/edge.cpp
  crab_mesh/aft/face.cpp crab_mesh/aft/boundary.cpp crab_mesh/aft/quadtree_cell.cpp
  crab_mesh/aft/quadtree.cpp crab_mesh/aft/advancing_front.cpp
  data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
  data/point_adaptive.cpp data/vector_adaptive.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM uv_sources PREPEND "${AP_MESH_UV_SOURCE_ROOT}/src/")
add_executable(uv_lifetime_probe probe.cpp ${uv_sources})
target_compile_features(uv_lifetime_probe PRIVATE cxx_std_17)
target_include_directories(uv_lifetime_probe PRIVATE "${AP_MESH_UV_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(uv_lifetime_probe PRIVATE /utf-8 /W4 /EHsc)
  if(AP_MESH_UV_ASAN)
    target_compile_options(uv_lifetime_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(uv_lifetime_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(uv_lifetime_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
