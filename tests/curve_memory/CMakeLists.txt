cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_curve_collections LANGUAGES CXX)
endif()
get_filename_component(default_curve_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_CURVE_SOURCE_ROOT "${default_curve_root}" CACHE PATH "Production tree for curve collection qualification")
option(AP_MESH_CURVE_ASAN "Instrument the narrow MSVC curve collection probe" OFF)
set(curve_sources
  data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
  data/point_adaptive.cpp data/vector_adaptive.cpp data/patch/patch.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM curve_sources PREPEND "${AP_MESH_CURVE_SOURCE_ROOT}/src/")
add_executable(curve_collection_probe probe.cpp ${curve_sources})
add_executable(curve_copy_probe copy_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp")
foreach(curve_probe IN ITEMS curve_collection_probe curve_copy_probe)
  target_compile_features(${curve_probe} PRIVATE cxx_std_17)
  target_include_directories(${curve_probe} PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
  if(MSVC)
    target_compile_options(${curve_probe} PRIVATE /utf-8 /W4 /EHsc)
    if(AP_MESH_CURVE_ASAN)
      target_compile_options(${curve_probe} PRIVATE /fsanitize=address /Zi)
      target_link_options(${curve_probe} PRIVATE /INCREMENTAL:NO)
    endif()
  elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(${curve_probe} PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endforeach()
