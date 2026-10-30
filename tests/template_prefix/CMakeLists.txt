cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_template_prefix LANGUAGES CXX)
endif()
find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
get_filename_component(prefix_default_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_PREFIX_ROOT "${prefix_default_root}" CACHE PATH "Native source tree")
set(prefix_generated "${CMAKE_CURRENT_BINARY_DIR}/observed")
add_custom_command(OUTPUT "${prefix_generated}/quadtree.cpp" "${prefix_generated}/quadtree_cell.cpp"
  COMMAND "${Python3_EXECUTABLE}" "${AP_MESH_PREFIX_ROOT}/tools/prepare_template_prefix.py"
    --root "${AP_MESH_PREFIX_ROOT}" --output "${prefix_generated}"
  DEPENDS "${AP_MESH_PREFIX_ROOT}/tools/prepare_template_prefix.py"
    "${AP_MESH_PREFIX_ROOT}/src/crab_mesh/aft/quadtree.cpp"
    "${AP_MESH_PREFIX_ROOT}/src/crab_mesh/aft/quadtree_cell.cpp" VERBATIM)
set(prefix_units crab_mesh/aft/shape.cpp crab_mesh/aft/vertex.cpp crab_mesh/aft/edge.cpp
  crab_mesh/aft/face.cpp crab_mesh/aft/boundary.cpp crab_mesh/aft/advancing_front.cpp
  data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
  data/curve/curve_adaptive_parametric_bezier.cpp data/point_adaptive.cpp data/vector_adaptive.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM prefix_units PREPEND "${AP_MESH_PREFIX_ROOT}/src/")
add_library(template_prefix_native STATIC ${prefix_units})
function(configure_prefix target)
  set_target_properties(${target} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS OFF)
  target_include_directories(${target} PRIVATE "${AP_MESH_PREFIX_ROOT}/include"
    "${AP_MESH_PREFIX_ROOT}/src/crab_mesh/aft" "${CMAKE_CURRENT_SOURCE_DIR}")
  if(MSVC)
    target_compile_options(${target} PRIVATE /utf-8 /W4 /EHsc)
  elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(${target} PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endfunction()
configure_prefix(template_prefix_native)
add_executable(template_prefix_probe probe.cpp "${prefix_generated}/quadtree.cpp" "${prefix_generated}/quadtree_cell.cpp")
add_executable(template_prefix_unobserved probe.cpp "${AP_MESH_PREFIX_ROOT}/src/crab_mesh/aft/quadtree.cpp" "${AP_MESH_PREFIX_ROOT}/src/crab_mesh/aft/quadtree_cell.cpp")
foreach(target template_prefix_probe template_prefix_unobserved)
  configure_prefix(${target})
  target_link_libraries(${target} PRIVATE template_prefix_native)
endforeach()
if(NOT CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  add_test(NAME application.analytic_template_prefix
    COMMAND "${Python3_EXECUTABLE}" "${AP_MESH_PREFIX_ROOT}/tests/template_prefix_case.py"
      --exe "$<TARGET_FILE:template_prefix_probe>" --unobserved "$<TARGET_FILE:template_prefix_unobserved>"
      --output "${CMAKE_BINARY_DIR}/analytic-template-prefix-controls" --repeatable-output)
  set_tests_properties(application.analytic_template_prefix PROPERTIES
    LABELS "application;prefix;required-gate" TIMEOUT 60)
endif()
