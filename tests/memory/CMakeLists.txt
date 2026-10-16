cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_node_lifetime LANGUAGES CXX)
endif()
get_filename_component(mesh_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
option(AP_MESH_NODE_ASAN "Instrument the narrow MSVC node lifetime probe" OFF)
add_executable(node_lifetime_probe probe.cpp
  "${mesh_root}/src/data/mesh/sub_mesh.cpp"
  "${mesh_root}/src/data/node_adaptive.cpp"
  "${mesh_root}/src/data/point_adaptive.cpp"
  "${mesh_root}/src/data/element_adaptive.cpp"
  "${mesh_root}/src/data/triangle_adaptive.cpp"
  "${mesh_root}/src/data/vector_adaptive.cpp")
target_compile_features(node_lifetime_probe PRIVATE cxx_std_17)
target_include_directories(node_lifetime_probe PRIVATE "${mesh_root}/include")
if(MSVC)
  target_compile_options(node_lifetime_probe PRIVATE /utf-8 /W4)
  if(AP_MESH_NODE_ASAN)
    target_compile_options(node_lifetime_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(node_lifetime_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(node_lifetime_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()
