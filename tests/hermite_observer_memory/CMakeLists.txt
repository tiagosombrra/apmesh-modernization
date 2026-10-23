cmake_minimum_required(VERSION 3.21)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_hermite_observer LANGUAGES CXX)
endif()
get_filename_component(default_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_HERMITE_OBSERVER_SOURCE_ROOT "${default_root}" CACHE PATH "Actual patch production snapshot")
option(AP_MESH_HERMITE_OBSERVER_ASAN "Instrument the detached Hermite observer probe" OFF)
set(sources data/geometry.cpp generator/curve_synchronization.cpp data/mesh/sub_mesh.cpp data/node_adaptive.cpp data/element_adaptive.cpp
  data/triangle_adaptive.cpp data/point_adaptive.cpp data/vector_adaptive.cpp
  data/patch/patch.cpp data/patch/patch_coons.cpp data/patch/patch_bezier.cpp
  data/patch/patch_hermite.cpp data/curve/curve_adaptive.cpp
  data/curve/curve_adaptive_parametric.cpp data/curve/curve_adaptive_parametric_bezier.cpp
  data/curve/curve_adaptive_parametric_hermite.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM sources PREPEND "${AP_MESH_HERMITE_OBSERVER_SOURCE_ROOT}/src/")
add_executable(hermite_observer_probe probe.cpp ${sources})
target_include_directories(hermite_observer_probe PRIVATE "${AP_MESH_HERMITE_OBSERVER_SOURCE_ROOT}/include")
set_target_properties(hermite_observer_probe PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON CXX_EXTENSIONS OFF)
if(MSVC)
  target_compile_definitions(hermite_observer_probe PRIVATE _USE_MATH_DEFINES _ITERATOR_DEBUG_LEVEL=0)
  target_compile_options(hermite_observer_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  if(AP_MESH_HERMITE_OBSERVER_ASAN)
    set_property(TARGET hermite_observer_probe PROPERTY MSVC_RUNTIME_LIBRARY MultiThreadedDLL)
    target_compile_options(hermite_observer_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(hermite_observer_probe PRIVATE /INCREMENTAL:NO)
  else()
    set_property(TARGET hermite_observer_probe PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
  endif()
elseif(MINGW)
  target_link_options(hermite_observer_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
