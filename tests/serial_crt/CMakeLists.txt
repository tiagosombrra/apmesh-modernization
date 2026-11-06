cmake_minimum_required(VERSION 3.21)
project(apmesh_serial_crt LANGUAGES CXX)

if(NOT MSVC)
  message(FATAL_ERROR "The complete-entry CRT observer requires MSVC checked Debug")
endif()

get_filename_component(AP_MESH_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(BUILD_TESTING OFF CACHE BOOL "Keep the existing regression separate" FORCE)
set(AP_MESH_USE_MPI OFF CACHE BOOL "Serial observer" FORCE)
set(AP_MESH_USE_OPENMP OFF CACHE BOOL "Serial observer" FORCE)
set(AP_MESH_ENABLE_LTO OFF CACHE BOOL "Checked Debug observer" FORCE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_subdirectory("${AP_MESH_ROOT}" engine EXCLUDE_FROM_ALL)

add_executable(serial_crt_probe probe.cpp)
target_link_libraries(serial_crt_probe PRIVATE APMesh::Engine)
target_compile_options(serial_crt_probe PRIVATE /W4 /permissive- /EHsc /we4530)
set_target_properties(serial_crt_probe PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

add_executable(serial_crt_static_probe static_probe.cpp static_exit_observer.cpp)
target_link_libraries(serial_crt_static_probe PRIVATE APMesh::Engine)
target_compile_options(serial_crt_static_probe PRIVATE /W4 /permissive- /EHsc /we4530)
set_target_properties(serial_crt_static_probe PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
