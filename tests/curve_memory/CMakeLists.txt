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
add_executable(geometry_adoption_probe adoption_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp")
set(AP_MESH_SYNC_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_synchronization.cpp" CACHE FILEPATH "Curve synchronization implementation")
add_executable(curve_synchronization_probe synchronization_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_SYNC_IMPLEMENTATION}")
if(MSVC)
  target_compile_options(curve_synchronization_probe PRIVATE /permissive-)
  # Debug iterator proxies allocate inside noexcept constructors. Keep the CRT
  # heap instrument while matching the serial/ASan container ABI for this target.
  target_compile_definitions(curve_synchronization_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
endif()
foreach(curve_probe IN ITEMS curve_collection_probe curve_copy_probe geometry_adoption_probe curve_synchronization_probe)
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
target_include_directories(curve_synchronization_probe PRIVATE "${default_curve_root}/include")

set(AP_MESH_SNAPSHOT_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_snapshots.cpp" CACHE FILEPATH "Curve sample snapshot implementation")
add_executable(curve_snapshot_probe snapshot_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_SNAPSHOT_IMPLEMENTATION}")
target_compile_features(curve_snapshot_probe PRIVATE cxx_std_17)
target_include_directories(curve_snapshot_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_snapshot_probe PRIVATE /utf-8 /W4 /EHsc /permissive-)
  target_compile_definitions(curve_snapshot_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_snapshot_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_snapshot_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(curve_snapshot_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
