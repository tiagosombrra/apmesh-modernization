cmake_minimum_required(VERSION 3.21)
project(model_root_audit LANGUAGES CXX)
if(NOT MSVC)
  message(FATAL_ERROR "This original audit requires MSVC ASan and static Debug CRT")
endif()
option(MODEL_AUDIT_ASAN "Instrument the original model audit with ASan" OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MODEL_AUDIT_ASAN)
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
else()
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDebug")
endif()
get_filename_component(root "${CMAKE_CURRENT_LIST_DIR}/../../../.." ABSOLUTE)
set(sources data/model.cpp data/mesh/mesh_adaptive.cpp data/mesh/sub_mesh.cpp
  data/node_adaptive.cpp data/element_adaptive.cpp data/triangle_adaptive.cpp
  data/point_adaptive.cpp data/vector_adaptive.cpp data/patch/patch.cpp
  data/geometry.cpp data/curve/curve_adaptive.cpp
  data/curve/curve_adaptive_parametric.cpp data/curve/curve_adaptive_parametric_bezier.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM sources PREPEND "${root}/src/")
add_executable(model_root_probe probe.cpp ${sources})
target_include_directories(model_root_probe PRIVATE "${root}/include")
target_compile_definitions(model_root_probe PRIVATE _USE_MATH_DEFINES _ITERATOR_DEBUG_LEVEL=0)
target_compile_options(model_root_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
if(MODEL_AUDIT_ASAN)
  target_compile_options(model_root_probe PRIVATE /fsanitize=address /Zi)
  target_link_options(model_root_probe PRIVATE /INCREMENTAL:NO)
endif()
