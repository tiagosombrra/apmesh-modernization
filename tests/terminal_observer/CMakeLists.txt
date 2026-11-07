cmake_minimum_required(VERSION 3.20)
project(apmesh_terminal_observer LANGUAGES CXX)
find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
get_filename_component(terminal_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(terminal_generated "${CMAKE_CURRENT_BINARY_DIR}/generated")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${terminal_root}/tools/prepare_terminal_observer.py"
  --root "${terminal_root}" --output "${terminal_generated}"
  RESULT_VARIABLE terminal_preparation)
if(NOT terminal_preparation EQUAL 0)
  message(FATAL_ERROR "Terminal observer preparation failed")
endif()

file(GLOB_RECURSE terminal_sources CONFIGURE_DEPENDS "${terminal_root}/src/*.cpp")
list(REMOVE_ITEM terminal_sources "${terminal_root}/src/main.cpp" "${terminal_root}/src/adapter/adapter.cpp")
add_executable(terminal_observer_probe probe.cpp allocation_observer.cpp
  "${terminal_generated}/adapter.cpp" ${terminal_sources})
target_compile_features(terminal_observer_probe PRIVATE cxx_std_17)
target_include_directories(terminal_observer_probe PRIVATE "${terminal_generated}"
  "${CMAKE_CURRENT_SOURCE_DIR}" "${terminal_root}/include" "${terminal_root}/src/adapter")

option(AP_MESH_TERMINAL_ALLOCATOR_WRAP "Observe allocation before the Linux sanitizer's allocation functions" OFF)
if(AP_MESH_TERMINAL_ALLOCATOR_WRAP)
  if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux" OR
     NOT CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64" OR
     NOT CMAKE_SIZEOF_VOID_P EQUAL 8 OR
     NOT CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    message(FATAL_ERROR "Terminal allocator wrapping requires Linux x86_64 Clang with the Itanium C++ ABI")
  endif()
  target_sources(terminal_observer_probe PRIVATE leak_control.cpp)
  set_property(SOURCE probe.cpp allocation_observer.cpp leak_control.cpp APPEND PROPERTY
    COMPILE_DEFINITIONS AP_MESH_TERMINAL_ALLOCATOR_WRAP=1)
  foreach(terminal_allocation_symbol IN ITEMS _Znwm _Znam _ZdlPv _ZdaPv _ZdlPvm _ZdaPvm)
    target_link_options(terminal_observer_probe PRIVATE "LINKER:--wrap=${terminal_allocation_symbol}")
  endforeach()
endif()
if(MSVC)
  target_compile_options(terminal_observer_probe PRIVATE /W4 /permissive- /FS /EHsc /we4530)
endif()
if(MINGW)
  target_compile_options(terminal_observer_probe PRIVATE -fno-strict-aliasing)
  target_link_options(terminal_observer_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()

option(AP_MESH_TERMINAL_CRT_LIFETIME "Observe the fixed terminal callers through checked-CRT static teardown" OFF)
if(AP_MESH_TERMINAL_CRT_LIFETIME)
  if(NOT MSVC)
    message(FATAL_ERROR "The terminal CRT lifetime observer requires MSVC checked Debug")
  endif()
  add_executable(terminal_crt_lifetime_probe crt_lifetime_probe.cpp allocation_observer.cpp
    "${terminal_root}/tests/serial_crt/lifetime_exit_observer.cpp"
    "${terminal_generated}/adapter.cpp" ${terminal_sources})
  target_compile_features(terminal_crt_lifetime_probe PRIVATE cxx_std_17)
  target_include_directories(terminal_crt_lifetime_probe PRIVATE "${terminal_generated}"
    "${CMAKE_CURRENT_SOURCE_DIR}" "${terminal_root}/include" "${terminal_root}/src/adapter")
  target_compile_options(terminal_crt_lifetime_probe PRIVATE /W4 /permissive- /FS /EHsc /we4530)
endif()
