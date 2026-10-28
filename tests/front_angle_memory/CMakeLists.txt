cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_front_angle_memory LANGUAGES CXX)
endif()
find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
get_filename_component(default_angle_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_ANGLE_ROOT "${default_angle_root}" CACHE PATH "Native source tree")
set(AP_MESH_ANGLE_SOURCE "${AP_MESH_ANGLE_ROOT}/src/crab_mesh/aft/advancing_front.cpp" CACHE FILEPATH "Native front source")
option(AP_MESH_ANGLE_ASAN "Instrument the isolated MSVC angle probe" OFF)
set(angle_backend "${CMAKE_CURRENT_BINARY_DIR}/front_angle_backend.cpp")
add_custom_command(OUTPUT "${angle_backend}"
  COMMAND "${Python3_EXECUTABLE}" "${AP_MESH_ANGLE_ROOT}/tools/prepare_front_angle_probe.py"
    --root "${AP_MESH_ANGLE_ROOT}" --source "${AP_MESH_ANGLE_SOURCE}"
    --output "${angle_backend}" --metadata "${CMAKE_CURRENT_BINARY_DIR}/observer.json"
  DEPENDS "${AP_MESH_ANGLE_SOURCE}" "${AP_MESH_ANGLE_ROOT}/tools/prepare_front_angle_probe.py"
  VERBATIM)
set(angle_sources
  crab_mesh/aft/shape.cpp crab_mesh/aft/vertex.cpp crab_mesh/aft/edge.cpp
  crab_mesh/aft/face.cpp crab_mesh/aft/boundary.cpp crab_mesh/aft/quadtree_cell.cpp
  crab_mesh/aft/quadtree.cpp data/curve/curve_adaptive.cpp
  data/curve/curve_adaptive_parametric.cpp data/point_adaptive.cpp data/vector_adaptive.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM angle_sources PREPEND "${AP_MESH_ANGLE_ROOT}/src/")
add_executable(front_angle_probe probe.cpp uaf_control.cpp "${angle_backend}" ${angle_sources})
target_compile_features(front_angle_probe PRIVATE cxx_std_17)
set_target_properties(front_angle_probe PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS OFF)
target_include_directories(front_angle_probe PRIVATE "${AP_MESH_ANGLE_ROOT}/include"
  "${AP_MESH_ANGLE_ROOT}/src/crab_mesh/aft" "${CMAKE_CURRENT_SOURCE_DIR}")
if(MSVC)
  target_compile_options(front_angle_probe PRIVATE /utf-8 /W4 /EHsc)
  target_compile_definitions(front_angle_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_ANGLE_ASAN)
    target_compile_options(front_angle_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(front_angle_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(front_angle_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
if(NOT CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  add_test(NAME application.front_angle_ownership
    COMMAND "${Python3_EXECUTABLE}" "${AP_MESH_ANGLE_ROOT}/tests/front_angle_case.py"
      --exe "$<TARGET_FILE:front_angle_probe>" --output "${CMAKE_BINARY_DIR}/front-angle-controls" --repeatable-output)
  set_tests_properties(application.front_angle_ownership PROPERTIES
    LABELS "application;memory;required-gate" TIMEOUT 60)
endif()
