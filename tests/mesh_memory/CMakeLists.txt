cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_mesh_adoption LANGUAGES CXX)
endif()
get_filename_component(default_mesh_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_ADOPTION_SOURCE_ROOT "${default_mesh_root}" CACHE PATH "Actual mesh source snapshot")
option(AP_MESH_MESH_ASAN "Instrument the isolated mesh adoption target" OFF)
add_executable(mesh_adoption_probe probe.cpp
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/mesh/mesh_adaptive.cpp"
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/point_adaptive.cpp"
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_ADOPTION_SOURCE_ROOT}/src/data/vector_adaptive.cpp")
target_compile_features(mesh_adoption_probe PRIVATE cxx_std_17)
target_include_directories(mesh_adoption_probe PRIVATE "${AP_MESH_ADOPTION_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(mesh_adoption_probe PRIVATE /utf-8 /W4 /EHsc /permissive-)
  target_compile_definitions(mesh_adoption_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_MESH_ASAN)
    target_compile_options(mesh_adoption_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(mesh_adoption_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(mesh_adoption_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
