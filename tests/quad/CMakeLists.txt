cmake_minimum_required(VERSION 3.20)
project(apmesh_quad_prototype LANGUAGES CXX)

enable_testing()
add_library(apmesh_quad_uv STATIC ../../research/quad/uv_mesh.cpp)
target_include_directories(apmesh_quad_uv PUBLIC ../../research/quad)
target_compile_features(apmesh_quad_uv PUBLIC cxx_std_17)
add_executable(quad_uv_contracts uv_contracts.cpp)
target_link_libraries(quad_uv_contracts PRIVATE apmesh_quad_uv)
# Explicit research-only alternative point rules; not linked to ap_mesh or CLI.
add_library(apmesh_quad_experimental_point STATIC
  ../../research/quad/experimental_point_rule.cpp)
target_link_libraries(apmesh_quad_experimental_point PUBLIC apmesh_quad_uv)
add_executable(quad_experimental_point_contracts experimental_point_contracts.cpp)
target_link_libraries(quad_experimental_point_contracts PRIVATE
  apmesh_quad_experimental_point)
# Export real C++ UV research meshes for independent visual inspection.
add_executable(quad_visual_export visual_export.cpp)
target_link_libraries(quad_visual_export PRIVATE apmesh_quad_experimental_point)
add_executable(quad_mesh_mode_contracts mesh_mode_contracts.cpp)
target_include_directories(quad_mesh_mode_contracts PRIVATE ../../include)
target_compile_features(quad_mesh_mode_contracts PRIVATE cxx_std_17)
add_executable(quad_uv_demo ../../research/quad/demo.cpp)
target_link_libraries(quad_uv_demo PRIVATE apmesh_quad_uv)

foreach(target IN ITEMS apmesh_quad_uv quad_uv_contracts quad_mesh_mode_contracts quad_uv_demo
  apmesh_quad_experimental_point quad_experimental_point_contracts quad_visual_export)
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
add_test(NAME quad.m1.experimental_point_witnesses COMMAND quad_experimental_point_contracts)
set_tests_properties(quad.m1.experimental_point_witnesses PROPERTIES
  TIMEOUT 30 LABELS "research-quad;numeric-proposal")
add_test(NAME quad.m1.visual_obj_export
  COMMAND quad_visual_export "${CMAKE_CURRENT_BINARY_DIR}/visual_uv_objs")
set_tests_properties(quad.m1.visual_obj_export PROPERTIES
  TIMEOUT 30 LABELS "research-quad;visual-validation")
# Independent exact-rational schematic audit of the Figure 7 transcription.
# This is a documentary contract, not a numerical centroid or physical QUAD gate.
find_package(Python3 COMPONENTS Interpreter REQUIRED)
add_test(NAME quad.m1.figure7.oracle
  COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_SOURCE_DIR}/test_m1_figure7_oracle.py"
    --fixture "${CMAKE_CURRENT_SOURCE_DIR}/../../docs/research/quad/evidence/M1_FIGURE7_TRANSCRIPTION_20261108.json")
set_tests_properties(quad.m1.figure7.oracle PROPERTIES TIMEOUT 120 LABELS "research-quad;historical-review")
# Research-only comparison: the historical area-centroid formula is not yet approved.
add_test(NAME quad.m1.point_rule_quality
  COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_CURRENT_SOURCE_DIR}/test_m1_point_rule_quality.py"
    --fixture "${CMAKE_CURRENT_SOURCE_DIR}/../../docs/research/quad/evidence/M1_FIGURE7_TRANSCRIPTION_20261108.json")
set_tests_properties(quad.m1.point_rule_quality PROPERTIES
  TIMEOUT 120 LABELS "research-quad;numeric-proposal")

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
  # Select actual Quadtree interior TRI or owned experimental QUAD once per attempt.
  # No application or AFT behavior changes are made by this research target.
  add_library(apmesh_quad_interior_dispatch STATIC
    ../../research/quad/interior_template_dispatch.cpp)
  target_link_libraries(apmesh_quad_interior_dispatch PUBLIC apmesh_quad_tree)
  add_executable(quad_interior_dispatch_contracts interior_template_dispatch_contracts.cpp)
  target_include_directories(quad_interior_dispatch_contracts PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
  target_link_libraries(quad_interior_dispatch_contracts PRIVATE
    apmesh_quad_interior_dispatch apmesh_quad_experimental_point)
  add_executable(quad_leaf_contracts leaf_contracts.cpp)
  target_link_libraries(quad_leaf_contracts PRIVATE apmesh_quad_tree)
  add_executable(quad_refined_observer_contracts refined_observer_contracts.cpp)
  target_include_directories(quad_refined_observer_contracts PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
  target_link_libraries(quad_refined_observer_contracts PRIVATE apmesh_quad_tree)
  add_executable(quad_tree_demo ../../research/quad/tree_demo.cpp)
  target_include_directories(quad_tree_demo PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
  target_link_libraries(quad_tree_demo PRIVATE apmesh_quad_tree)
  add_executable(quad_tree_visual_export tree_visual_export.cpp)
  target_include_directories(quad_tree_visual_export PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
  target_link_libraries(quad_tree_visual_export PRIVATE
    apmesh_quad_tree apmesh_quad_experimental_point)
  foreach(target IN ITEMS apmesh_quad_legacy_tree apmesh_quad_tree apmesh_quad_interior_dispatch
    quad_interior_dispatch_contracts quad_leaf_contracts quad_refined_observer_contracts
    quad_tree_demo quad_tree_visual_export)
    # Keep diagnostics visible across the existing legacy-header integration.
    if(MSVC)
      target_compile_options(${target} PRIVATE /W4 /EHsc /utf-8)
    else()
      target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    endif()
  endforeach()
  add_test(NAME quad.r1.interior_template_dispatch COMMAND quad_interior_dispatch_contracts)
  set_tests_properties(quad.r1.interior_template_dispatch PROPERTIES
    TIMEOUT 60 LABELS "research-quad;real-quadtree;interior-mode;negative-controls")
  add_test(NAME quad.leaf.contracts COMMAND quad_leaf_contracts)
  set_tests_properties(quad.leaf.contracts PROPERTIES TIMEOUT 60 LABELS "research-quad")
  add_test(NAME quad.refined_observer.contracts COMMAND quad_refined_observer_contracts)
  set_tests_properties(quad.refined_observer.contracts PROPERTIES TIMEOUT 30 LABELS "research-quad")
  add_test(NAME quad.m3.real_tree_visual_export
    COMMAND quad_tree_visual_export "${CMAKE_CURRENT_BINARY_DIR}/real_tree_visual")
  set_tests_properties(quad.m3.real_tree_visual_export PROPERTIES
    TIMEOUT 30 LABELS "research-quad;visual-validation")
  add_test(NAME quad.m3.real_tree_visual_verify
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/test_tree_visual_export.py"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/real_tree_visual")
  set_tests_properties(quad.m3.real_tree_visual_verify PROPERTIES
    DEPENDS quad.m3.real_tree_visual_export
    TIMEOUT 30 LABELS "research-quad;visual-validation")
  # Topology-only exterior center-fan experiment on actual C++ Quadtree outputs.
  # Historical Delaunay and contour contraction are explicitly not implemented.
  add_test(NAME quad.m5.experimental_exterior_interface
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/test_m5_exterior_interface.py"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/real_tree_visual")
  set_tests_properties(quad.m5.experimental_exterior_interface PROPERTIES
    DEPENDS quad.m3.real_tree_visual_verify
    TIMEOUT 45 LABELS "research-quad;experimental-boundary")
  # Research-only locally constrained Delaunay comparison over real C++ output.
  # Exact 1993 Delaunay point insertion and contour contraction remain open.
  add_test(NAME quad.m5.local_constrained_delaunay
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/test_m5_constrained_delaunay.py"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/real_tree_visual")
  set_tests_properties(quad.m5.local_constrained_delaunay PROPERTIES
    DEPENDS quad.m5.experimental_exterior_interface
    TIMEOUT 120 LABELS "research-quad;experimental-boundary;local-delaunay")
  # Analytical XYZ embedding of native C++ UV QUAD and experimental M5 TRI only.
  add_test(NAME quad.m6.analytic_surface_lift
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/test_m6_analytic_surface_lift.py"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/real_tree_visual")
  set_tests_properties(quad.m6.analytic_surface_lift PROPERTIES
    DEPENDS quad.m5.local_constrained_delaunay
    TIMEOUT 120 LABELS "research-quad;analytic-xyz;not-physical-model")

endif()
