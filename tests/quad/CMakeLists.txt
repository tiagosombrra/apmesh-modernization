cmake_minimum_required(VERSION 3.20)
project(apmesh_quad_prototype LANGUAGES CXX)

enable_testing()
add_library(apmesh_quad_uv STATIC ../../research/quad/uv_mesh.cpp)
target_include_directories(apmesh_quad_uv PUBLIC ../../research/quad)
target_compile_features(apmesh_quad_uv PUBLIC cxx_std_17)
add_executable(quad_uv_contracts uv_contracts.cpp)
target_link_libraries(quad_uv_contracts PRIVATE apmesh_quad_uv)
add_executable(quad_mesh_mode_contracts mesh_mode_contracts.cpp)
target_include_directories(quad_mesh_mode_contracts PRIVATE ../../include)
target_compile_features(quad_mesh_mode_contracts PRIVATE cxx_std_17)
add_executable(quad_uv_demo ../../research/quad/demo.cpp)
target_link_libraries(quad_uv_demo PRIVATE apmesh_quad_uv)

foreach(target IN ITEMS apmesh_quad_uv quad_uv_contracts quad_mesh_mode_contracts quad_uv_demo)
  if(MSVC)
    target_compile_options(${target} PRIVATE /W4 /WX /EHsc /utf-8)
  else()
    target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror)
  endif()
endforeach()

add_test(NAME quad.mesh_mode.contracts COMMAND quad_mesh_mode_contracts)
set_tests_properties(quad.mesh_mode.contracts PROPERTIES TIMEOUT 20 LABELS "research-quad")
add_test(NAME quad.uv.contracts COMMAND quad_uv_contracts)
set_tests_properties(quad.uv.contracts PROPERTIES TIMEOUT 30 LABELS "research-quad")

option(AP_MESH_QUAD_WITH_TREE "Build the read-only bridge to the existing serial quadtree" OFF)
if(AP_MESH_QUAD_WITH_TREE)
  # Same bounded production component as tests/uv_memory, with actual runtime defaults.
  set(tree_sources
    crab_mesh/aft/shape.cpp crab_mesh/aft/vertex.cpp crab_mesh/aft/edge.cpp
    crab_mesh/aft/face.cpp crab_mesh/aft/boundary.cpp crab_mesh/aft/quadtree_cell.cpp
    crab_mesh/aft/quadtree.cpp crab_mesh/aft/advancing_front.cpp
    data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
    data/point_adaptive.cpp data/vector_adaptive.cpp
    crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp
    application/runtime_state.cpp)
  list(TRANSFORM tree_sources PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/../../src/")
  add_library(apmesh_quad_legacy_tree STATIC ${tree_sources})
  target_include_directories(apmesh_quad_legacy_tree PUBLIC ../../include)
  target_compile_features(apmesh_quad_legacy_tree PUBLIC cxx_std_17)
  add_library(apmesh_quad_tree STATIC ../../research/quad/quadtree_quad.cpp)
  target_link_libraries(apmesh_quad_tree PUBLIC apmesh_quad_uv apmesh_quad_legacy_tree)
  add_executable(quad_leaf_contracts leaf_contracts.cpp)
  target_link_libraries(quad_leaf_contracts PRIVATE apmesh_quad_tree)
  add_executable(quad_refined_observer_contracts refined_observer_contracts.cpp)
  target_include_directories(quad_refined_observer_contracts PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
  target_link_libraries(quad_refined_observer_contracts PRIVATE apmesh_quad_tree)
  add_executable(quad_tree_demo ../../research/quad/tree_demo.cpp)
  target_include_directories(quad_tree_demo PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
  target_link_libraries(quad_tree_demo PRIVATE apmesh_quad_tree)
  foreach(target IN ITEMS apmesh_quad_legacy_tree apmesh_quad_tree quad_leaf_contracts quad_refined_observer_contracts quad_tree_demo)
    # Keep diagnostics visible across the existing legacy-header integration.
    if(MSVC)
      target_compile_options(${target} PRIVATE /W4 /EHsc /utf-8)
    else()
      target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    endif()
  endforeach()
  add_test(NAME quad.leaf.contracts COMMAND quad_leaf_contracts)
  set_tests_properties(quad.leaf.contracts PROPERTIES TIMEOUT 60 LABELS "research-quad")
  add_test(NAME quad.refined_observer.contracts COMMAND quad_refined_observer_contracts)
  set_tests_properties(quad.refined_observer.contracts PROPERTIES TIMEOUT 30 LABELS "research-quad")
endif()
