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

add_executable(serial_crt_lifetime_probe lifetime_probe.cpp lifetime_exit_observer.cpp)
target_link_libraries(serial_crt_lifetime_probe PRIVATE APMesh::Engine)
target_compile_options(serial_crt_lifetime_probe PRIVATE /W4 /permissive- /EHsc /we4530)
set_target_properties(serial_crt_lifetime_probe PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# Reuse the original two-call public Execute sequence without editing its body.
add_library(serial_crt_reuse_entry OBJECT reuse_entry.cpp)
target_compile_options(serial_crt_reuse_entry PRIVATE /W4 /permissive- /EHsc /we4530)
target_link_libraries(serial_crt_reuse_entry PRIVATE APMesh::Engine)

add_executable(serial_crt_reuse_probe lifetime_probe.cpp lifetime_exit_observer.cpp
  $<TARGET_OBJECTS:serial_crt_reuse_entry>)
target_compile_definitions(serial_crt_reuse_probe PRIVATE AP_MESH_CRT_REUSE_ENTRY)
target_compile_options(serial_crt_reuse_probe PRIVATE /W4 /permissive- /EHsc /we4530)
target_link_libraries(serial_crt_reuse_probe PRIVATE APMesh::Engine Rstrtmgr)
set_target_properties(serial_crt_reuse_probe PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
