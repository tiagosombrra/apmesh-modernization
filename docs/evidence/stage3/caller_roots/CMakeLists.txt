cmake_minimum_required(VERSION 3.21)
project(serial_reader_root_audit LANGUAGES CXX)
if(NOT MSVC)
  message(FATAL_ERROR "This original-retention reproduction requires the MSVC Debug CRT")
endif()
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDebug")
get_filename_component(root "${CMAKE_CURRENT_LIST_DIR}/../../../.." ABSOLUTE)
set(sources data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
  data/point_adaptive.cpp data/vector_adaptive.cpp data/patch/patch.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp
  data/curve/curve_adaptive_parametric_bezier.cpp data/curve/curve_adaptive_parametric_hermite.cpp
  data/patch/patch_coons.cpp data/patch/patch_bezier.cpp data/patch/patch_hermite.cpp
  data/geometry.cpp data/vertex_adaptive.cpp input_output/patch_reader.cpp
  input_output/control_patch_reader.cpp)
list(TRANSFORM sources PREPEND "${root}/src/")
add_executable(serial_reader_root_probe probe.cpp ${sources})
target_include_directories(serial_reader_root_probe PRIVATE "${root}/include")
target_compile_definitions(serial_reader_root_probe PRIVATE _USE_MATH_DEFINES _ITERATOR_DEBUG_LEVEL=0)
target_compile_options(serial_reader_root_probe PRIVATE /utf-8 /EHsc /permissive- /Zc:nrvo-)
