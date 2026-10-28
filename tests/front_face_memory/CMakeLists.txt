cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_front_face_memory LANGUAGES CXX)
endif()
find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
get_filename_component(default_face_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_FACE_ROOT "${default_face_root}" CACHE PATH "Native source tree")
set(AP_MESH_FACE_ORIGINAL_SOURCE "" CACHE FILEPATH "Optional pinned original front source")
option(AP_MESH_FACE_ASAN "Instrument the bounded interception probe" OFF)
set(face_sources crab_mesh/aft/shape.cpp crab_mesh/aft/vertex.cpp crab_mesh/aft/edge.cpp
  crab_mesh/aft/face.cpp crab_mesh/aft/boundary.cpp crab_mesh/aft/quadtree_cell.cpp crab_mesh/aft/quadtree.cpp
  data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp data/point_adaptive.cpp data/vector_adaptive.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM face_sources PREPEND "${AP_MESH_FACE_ROOT}/src/")
add_library(front_face_native STATIC ${face_sources})
function(configure_face_target target)
  set_target_properties(${target} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS OFF)
  target_include_directories(${target} PRIVATE "${AP_MESH_FACE_ROOT}/include"
    "${AP_MESH_FACE_ROOT}/src/crab_mesh/aft" "${CMAKE_CURRENT_SOURCE_DIR}")
  if(MSVC)
    target_compile_options(${target} PRIVATE /utf-8 /W4 /EHsc)
    target_compile_definitions(${target} PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
    if(AP_MESH_FACE_ASAN)
      target_compile_options(${target} PRIVATE /fsanitize=address /Zi)
      target_link_options(${target} PRIVATE /INCREMENTAL:NO)
    endif()
  elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(${target} PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endfunction()
configure_face_target(front_face_native)
function(add_face_probe target source)
  set(backend "${CMAKE_CURRENT_BINARY_DIR}/${target}_backend.cpp")
  add_custom_command(OUTPUT "${backend}"
    COMMAND "${Python3_EXECUTABLE}" "${AP_MESH_FACE_ROOT}/tools/prepare_front_face_probe.py"
      --root "${AP_MESH_FACE_ROOT}" --source "${source}" --output "${backend}"
      --metadata "${CMAKE_CURRENT_BINARY_DIR}/${target}_observer.json"
    DEPENDS "${source}" "${AP_MESH_FACE_ROOT}/tools/prepare_front_face_probe.py" VERBATIM)
  add_executable(${target} probe.cpp uaf_control.cpp "${backend}")
  configure_face_target(${target})
  target_link_libraries(${target} PRIVATE front_face_native)
endfunction()
add_face_probe(front_face_probe "${AP_MESH_FACE_ROOT}/src/crab_mesh/aft/advancing_front.cpp")
if(AP_MESH_FACE_ORIGINAL_SOURCE)
  add_face_probe(front_face_original "${AP_MESH_FACE_ORIGINAL_SOURCE}")
endif()
if(NOT CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  add_test(NAME application.front_face_borrowers
    COMMAND "${Python3_EXECUTABLE}" "${AP_MESH_FACE_ROOT}/tests/front_face_case.py"
      --exe "$<TARGET_FILE:front_face_probe>" --output "${CMAKE_BINARY_DIR}/front-face-controls" --repeatable-output)
  set_tests_properties(application.front_face_borrowers PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 60)
endif()
