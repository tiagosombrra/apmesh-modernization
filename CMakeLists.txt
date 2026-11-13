cmake_minimum_required(VERSION 3.15 FATAL_ERROR)

# Project definition
project(ap_mesh VERSION 1.0 LANGUAGES CXX)

# -----------------------------
# Options
# -----------------------------
option(AP_MESH_USE_MPI "Build with MPI support (requires configuring with an MPI compiler wrapper)." OFF)
option(AP_MESH_USE_OPENMP "Enable OpenMP parallelism when available." ON)
option(AP_MESH_ENABLE_LTO "Enable Link Time Optimization (IPO/LTO) in Release builds when supported." ON)
option(AP_MESH_ENABLE_WARNINGS "Enable extra compiler warnings." ON)
option(AP_MESH_DISABLE_STRICT_ALIASING "Compile with -fno-strict-aliasing (useful if code violates strict aliasing)." ON)
option(AP_MESH_STATIC_MINGW_RUNTIME "Link the MinGW runtime statically for a portable Windows executable." ON)

# Default build type for single-config generators
if(NOT CMAKE_CONFIGURATION_TYPES AND NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
endif()

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# -----------------------------
# Target
# -----------------------------
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
set(INC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

file(GLOB_RECURSE AP_MESH_SOURCES CONFIGURE_DEPENDS "${SRC_DIR}/*.cpp")

set(AP_MESH_ENGINE_SOURCES ${AP_MESH_SOURCES})
list(REMOVE_ITEM AP_MESH_ENGINE_SOURCES "${SRC_DIR}/main.cpp")
add_library(ap_mesh_engine STATIC ${AP_MESH_ENGINE_SOURCES})
add_library(APMesh::Engine ALIAS ap_mesh_engine)
target_compile_features(ap_mesh_engine PUBLIC cxx_std_17)
target_include_directories(ap_mesh_engine PUBLIC "${INC_DIR}")
add_executable(ap_mesh "${SRC_DIR}/main.cpp")
target_link_libraries(ap_mesh PRIVATE ap_mesh_engine)

# English comment: keep the standard on the target (modern CMake)
target_compile_features(ap_mesh PRIVATE cxx_std_17)

target_include_directories(ap_mesh PRIVATE "${INC_DIR}")

# Avoid dependence on whichever MinGW runtime DLLs happen to appear first in
# the reviewer's PATH. Windows system/UCRT dependencies remain dynamic.
if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(
    ap_mesh
    PRIVATE
      -static
      -static-libgcc
      -static-libstdc++
  )
endif()

set(AP_MESH_WORKDIR "${CMAKE_CURRENT_SOURCE_DIR}")

# Historical target names are aliases of the current Book article configuration.
# They do not select separate balanced, conservative or strict scientific profiles.
foreach(book_alias IN ITEMS balanced conservative strict)
  add_custom_target(run_book_v5_fix_${book_alias}
    COMMAND $<TARGET_FILE:ap_mesh>
            --config "${CMAKE_CURRENT_SOURCE_DIR}/configs/book/article.conf"
    DEPENDS ap_mesh "${CMAKE_CURRENT_SOURCE_DIR}/configs/book/article.conf"
    WORKING_DIRECTORY "${AP_MESH_WORKDIR}"
    USES_TERMINAL
    VERBATIM
    COMMENT "Run current Book article configuration (legacy ${book_alias} alias)"
  )
endforeach()

# -----------------------------
# Warnings / flags
# -----------------------------
foreach(ap_mesh_target IN ITEMS ap_mesh ap_mesh_engine)
  if(MSVC)
    target_compile_options(${ap_mesh_target} PRIVATE /EHsc /we4530)
  endif()
  if(AP_MESH_ENABLE_WARNINGS)
    if(MSVC)
      target_compile_options(${ap_mesh_target} PRIVATE /W4 /permissive- /FS)
    else()
      target_compile_options(${ap_mesh_target} PRIVATE -Wall -Wextra -Wpedantic -Wshadow -Wconversion)
      # English comment: keep this only if needed; it may hide real issues.
      target_compile_options(${ap_mesh_target} PRIVATE -Wno-cast-function-type)
    endif()
  endif()

  # Build-type specific optimizations
  if(MSVC)
    target_compile_options(${ap_mesh_target} PRIVATE $<$<CONFIG:Release>:/O2>)
  else()
    target_compile_options(${ap_mesh_target} PRIVATE $<$<CONFIG:Release>:-O3>)
  endif()

  if(AP_MESH_DISABLE_STRICT_ALIASING AND NOT MSVC)
    target_compile_options(${ap_mesh_target} PRIVATE -fno-strict-aliasing)
  endif()
endforeach()

# -----------------------------
# OpenMP
# -----------------------------
if(AP_MESH_USE_OPENMP)
  find_package(OpenMP QUIET)
  if(OpenMP_CXX_FOUND)
    target_link_libraries(ap_mesh PRIVATE OpenMP::OpenMP_CXX)
    target_link_libraries(ap_mesh_engine PUBLIC OpenMP::OpenMP_CXX)
    target_compile_definitions(ap_mesh PRIVATE AP_MESH_HAS_OPENMP=1)
    target_compile_definitions(ap_mesh_engine PRIVATE AP_MESH_HAS_OPENMP=1)
  else()
    message(WARNING "OpenMP requested but not found. Building without OpenMP.")
  endif()
endif()

# -----------------------------
# MPI
# -----------------------------
if(AP_MESH_USE_MPI)
  # English comment: to build with MPI, configure with mpicxx/mpicc wrappers.
  # Example:
  #   cmake -S . -B build-mpi -DAP_MESH_USE_MPI=ON -DCMAKE_CXX_COMPILER=mpicxx -DCMAKE_C_COMPILER=mpicc
  find_package(MPI REQUIRED)
  target_link_libraries(ap_mesh PRIVATE MPI::MPI_CXX)
  target_link_libraries(ap_mesh_engine PUBLIC MPI::MPI_CXX)
  target_compile_definitions(ap_mesh PRIVATE AP_MESH_HAS_MPI=1)
  target_compile_definitions(ap_mesh_engine PRIVATE AP_MESH_HAS_MPI=1)
endif()

# -----------------------------
# LTO (IPO)
# -----------------------------
if(AP_MESH_ENABLE_LTO AND (CMAKE_BUILD_TYPE STREQUAL "Release" OR CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo"))
  include(CheckIPOSupported)
  check_ipo_supported(RESULT ipo_supported OUTPUT ipo_error)
  if(ipo_supported)
    set_property(TARGET ap_mesh PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
    set_property(TARGET ap_mesh_engine PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
  else()
    message(WARNING "IPO/LTO requested but not supported: ${ipo_error}")
  endif()
endif()

# -----------------------------
# Diagnostics
# -----------------------------
message(STATUS "System: ${CMAKE_SYSTEM_NAME}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "MPI: ${AP_MESH_USE_MPI}")
message(STATUS "OpenMP: ${AP_MESH_USE_OPENMP}")
message(STATUS "LTO: ${AP_MESH_ENABLE_LTO}")
message(STATUS "Static MinGW runtime: ${AP_MESH_STATIC_MINGW_RUNTIME}")

# Register local quality controls separately from scientific regression.
include(cmake/Quality.cmake)

if(BUILD_TESTING AND TARGET curvature_sample_probe)
  add_test(NAME application.curvature_sample_contracts COMMAND curvature_sample_probe contracts)
endif()

if(BUILD_TESTING AND TARGET bezier_construction_probe)
  add_test(NAME application.bezier_construction_contracts COMMAND bezier_construction_probe contracts)
  set_tests_properties(application.bezier_construction_contracts PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 300)
endif()

if(BUILD_TESTING AND TARGET serial_reader_probe)
  add_test(NAME application.serial_reader_contracts COMMAND serial_reader_probe contracts "${CMAKE_SOURCE_DIR}/tests/curve_memory/serial_reader.bp")
  set_tests_properties(application.serial_reader_contracts PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 30)
  add_test(NAME tooling.serial_reader_preservation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/audit_serial_reader.py"
            --candidate-root "${CMAKE_SOURCE_DIR}")
  set_tests_properties(tooling.serial_reader_preservation PROPERTIES LABELS "tooling;required-gate" TIMEOUT 30)
endif()

if(BUILD_TESTING AND TARGET bezier_observer_probe)
  add_test(NAME application.bezier_observer_contracts COMMAND bezier_observer_probe contracts)
  set_tests_properties(application.bezier_observer_contracts PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 30)
  add_test(NAME tooling.bezier_observer_preservation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/audit_bezier_observers.py"
      --candidate-root "${CMAKE_SOURCE_DIR}")
  set_tests_properties(tooling.bezier_observer_preservation PROPERTIES LABELS "tooling;required-gate" TIMEOUT 30)
endif()

# M3-5: exercise the actual serial Adapter with research hooks in a test process.
# These sources are never linked into the production application or the CLI.
if(BUILD_TESTING AND NOT AP_MESH_USE_MPI AND NOT AP_MESH_USE_OPENMP)
  add_executable(quad_adapter_integration_probe
    tests/quad/adapter_integration_probe.cpp
    research/quad/quadtree_quad.cpp
    research/quad/uv_mesh.cpp
    research/quad/interior_template_dispatch.cpp
    research/quad/front_interface_audit.cpp
    research/quad/owned_aft_front.cpp
    research/quad/source_tree_replay.cpp)
  target_include_directories(quad_adapter_integration_probe PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/research/quad")
  target_link_libraries(quad_adapter_integration_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_adapter_integration_probe PRIVATE cxx_std_17)
  add_test(NAME quad.adapter.real_patch_capture COMMAND quad_adapter_integration_probe)
  set_tests_properties(quad.adapter.real_patch_capture PROPERTIES
    LABELS "research-quad;application;required-gate" TIMEOUT 75)
  # Run the pre-refinement observer-abort in its own native process to expose
  # source lifetime and previous-SubMesh restoration independently.
  add_test(NAME quad.adapter.real_boundary_abort
    COMMAND quad_adapter_integration_probe --boundary-abort)
  set_tests_properties(quad.adapter.real_boundary_abort PROPERTIES
    LABELS "research-quad;application;ownership;required-gate" TIMEOUT 75)

  # R2b2: native source-aligned QUAD/AFT UV directly lifted through actual
  # PatchReader/PatchBezier. This target never enters the production CLI.
  add_executable(quad_r2b2_bezier_aft_probe
    tests/quad/r2b2_bezier_aft_probe.cpp
    research/quad/uv_mesh.cpp
    research/quad/quadtree_quad.cpp
    research/quad/interior_template_dispatch.cpp
    research/quad/front_interface_audit.cpp
    research/quad/owned_aft_front.cpp)
  target_include_directories(quad_r2b2_bezier_aft_probe PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/research/quad"
    "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad")
  target_link_libraries(quad_r2b2_bezier_aft_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_r2b2_bezier_aft_probe PRIVATE cxx_std_17)
  add_test(NAME quad.r2b2.real_bezier_aft
    COMMAND quad_r2b2_bezier_aft_probe
      "${CMAKE_CURRENT_SOURCE_DIR}/input_models/eistute2.fixed.bp"
      "${CMAKE_CURRENT_SOURCE_DIR}/input_models/book_v7a.bp")
  set_tests_properties(quad.r2b2.real_bezier_aft PROPERTIES
    LABELS "research-quad;physical-source;application;required-gate"
    TIMEOUT 120)

  # M4 preliminary: test actual serial PatchBezier evaluation against independent
  # XYZ and derivative goldens; no production QUAD publication is enabled.
  add_executable(quad_patch_bezier_physical_probe
    tests/quad/patch_bezier_physical_probe.cpp)
  target_link_libraries(quad_patch_bezier_physical_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_patch_bezier_physical_probe PRIVATE cxx_std_17)
  add_test(NAME quad.patch_bezier.physical_api
    COMMAND quad_patch_bezier_physical_probe)
  set_tests_properties(quad.patch_bezier.physical_api PROPERTIES
    LABELS "research-quad;physical-api;application;required-gate" TIMEOUT 30)

  # M4 research: use the actual C++ Quadtree, not a synthetic UV substitute.
  # The physical output remains detached from the production TRI pipeline.
  add_executable(quad_m4_native_tree_export
    tests/quad/tree_visual_export.cpp
    research/quad/quadtree_quad.cpp
    research/quad/uv_mesh.cpp
    research/quad/experimental_point_rule.cpp)
  target_include_directories(quad_m4_native_tree_export PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/research/quad"
    "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad")
  target_link_libraries(quad_m4_native_tree_export PRIVATE ap_mesh_engine)
  target_compile_features(quad_m4_native_tree_export PRIVATE cxx_std_17)

  add_executable(quad_m4_physical_model_lift
    tests/quad/physical_model_hybrid_lift.cpp)
  target_link_libraries(quad_m4_physical_model_lift PRIVATE ap_mesh_engine)
  target_compile_features(quad_m4_physical_model_lift PRIVATE cxx_std_17)
  add_test(NAME quad.m4.real_builtin_model_hybrid
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_m4_real_model_hybrid.py"
      --tree-exe "$<TARGET_FILE:quad_m4_native_tree_export>"
      --lift-exe "$<TARGET_FILE:quad_m4_physical_model_lift>"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/m4_real_model")
  set_tests_properties(quad.m4.real_builtin_model_hybrid PROPERTIES
    LABELS "research-quad;physical-model;application;required-gate"
    TIMEOUT 180)

  # M4 ownership proof: borrow four physical nodes per research QUAD while
  # a SubMesh exclusively owns all 69 nodes and 78 mixed mesh elements.
  # Reuse the independently qualified native Quadtree/M5/M4 model pipeline.
  add_executable(quad_four_node_ownership_probe
    tests/quad/physical_quad_ownership_probe.cpp
    research/quad/physical_quadrilateral_adaptive.cpp)
  target_include_directories(quad_four_node_ownership_probe PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/research/quad")
  target_link_libraries(quad_four_node_ownership_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_four_node_ownership_probe PRIVATE cxx_std_17)
  add_test(NAME quad.m4.four_node_ownership
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_m4_quad_ownership.py"
      --tree-exe "$<TARGET_FILE:quad_m4_native_tree_export>"
      --lift-exe "$<TARGET_FILE:quad_m4_physical_model_lift>"
      --ownership-exe "$<TARGET_FILE:quad_four_node_ownership_probe>"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/m4_quad_ownership")
  set_tests_properties(quad.m4.four_node_ownership PROPERTIES
    LABELS "research-quad;physical-model;ownership;application;required-gate"
    TIMEOUT 180)

  # R2c-2 preflight: detached, unjoined owner roots with fault-injected
  # 4- and 28-chart QUAD/TRI lifetime and strong publication rollback.
  # This does NOT attach physical source Patch observers or authorize welding.
  add_executable(quad_disjoint_owner_stage_probe
    tests/quad/disjoint_owner_stage_probe.cpp
    research/quad/physical_quadrilateral_adaptive.cpp)
  target_include_directories(quad_disjoint_owner_stage_probe PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/research/quad")
  target_link_libraries(quad_disjoint_owner_stage_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_disjoint_owner_stage_probe PRIVATE cxx_std_17)
  add_test(NAME quad.r2c2.disjoint_owner_stage
    COMMAND "$<TARGET_FILE:quad_disjoint_owner_stage_probe>"
      "${CMAKE_CURRENT_SOURCE_DIR}/input_models/eistute2.fixed.bp"
      "${CMAKE_CURRENT_SOURCE_DIR}/input_models/book_v7a.bp")
  set_tests_properties(quad.r2c2.disjoint_owner_stage PROPERTIES
    LABELS "research-quad;ownership;detached;required-gate" TIMEOUT 90)

  # Research-only pairwise boundary admission using the production .bp loader.
  # This fixture never publishes QUAD elements or changes the default TRI path.
  add_executable(quad_m4_pairwise_boundary_probe
    tests/quad/patch_reader_pairwise_probe.cpp)
  target_link_libraries(quad_m4_pairwise_boundary_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_m4_pairwise_boundary_probe PRIVATE cxx_std_17)
  add_test(NAME quad.m4.pairwise_bezier_boundary
    COMMAND "$<TARGET_FILE:quad_m4_pairwise_boundary_probe>"
      "${CMAKE_CURRENT_BINARY_DIR}/m4_pairwise_bezier")
  set_tests_properties(quad.m4.pairwise_bezier_boundary PROPERTIES
    LABELS "research-quad;physical-model;boundary;required-gate"
    TIMEOUT 120)

  # Lift real native C++ QUAD/M5 TRI UV on two controlled physical Bezier sheets.
  # Only independent per-patch OBJ witnesses; no global node publication.
  add_executable(quad_m4_pairwise_physical_sampler
    tests/quad/pairwise_physical_sampler.cpp)
  target_link_libraries(quad_m4_pairwise_physical_sampler PRIVATE ap_mesh_engine)
  target_compile_features(quad_m4_pairwise_physical_sampler PRIVATE cxx_std_17)
  add_test(NAME quad.m4.pairwise_native_physical_candidates
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_m4_pairwise_physical_candidates.py"
      --tree-exe "$<TARGET_FILE:quad_m4_native_tree_export>"
      --fixture-exe "$<TARGET_FILE:quad_m4_pairwise_boundary_probe>"
      --sampler-exe "$<TARGET_FILE:quad_m4_pairwise_physical_sampler>"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/m4_pairwise_physical")
  set_tests_properties(quad.m4.pairwise_native_physical_candidates PROPERTIES
    LABELS "research-quad;physical-model;boundary;hybrid;required-gate"
    TIMEOUT 240)

  # Read-only external Bezier physical witnesses on real indexed BP control nets.
  # No cross-patch global nodes, normal-Z shortcut, or production QUAD mode.
  add_executable(quad_m4_external_bezier_sampler
    tests/quad/external_bezier_physical_sampler.cpp)
  target_link_libraries(quad_m4_external_bezier_sampler PRIVATE ap_mesh_engine)
  target_compile_features(quad_m4_external_bezier_sampler PRIVATE cxx_std_17)
  add_test(NAME quad.m4.external_bezier_physical_diagnostics
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_m4_external_bezier_physical.py"
      --root "${CMAKE_CURRENT_SOURCE_DIR}"
      --tree-exe "$<TARGET_FILE:quad_m4_native_tree_export>"
      --sampler-exe "$<TARGET_FILE:quad_m4_external_bezier_sampler>"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/m4_external_bezier")
  set_tests_properties(quad.m4.external_bezier_physical_diagnostics PROPERTIES
    LABELS "research-quad;physical-model;external-bp;boundary;required-gate"
    TIMEOUT 300)

  # Build conservative, real BP per-patch curve incidence hypergraphs.
  # Depends on the preceding C++ PatchReader physical evidence CTest.
  add_test(NAME quad.m4.sheet_incidence_graph
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_m4_sheet_incidence_graph.py"
      --root "${CMAKE_CURRENT_SOURCE_DIR}"
      --physical-directory "${CMAKE_CURRENT_BINARY_DIR}/m4_external_bezier"
      --directory "${CMAKE_CURRENT_BINARY_DIR}/m4_sheet_incidence")
  set_tests_properties(quad.m4.sheet_incidence_graph PROPERTIES
    DEPENDS quad.m4.external_bezier_physical_diagnostics
    LABELS "research-quad;physical-model;external-bp;sheet-incidence;required-gate"
    TIMEOUT 180)

  # M3-6c: execute the real GeneratorAdaptive with research hooks enabled.
  add_executable(quad_generator_outcome_probe
    tests/quad/generator_outcome_probe.cpp
    research/quad/source_tree_replay.cpp
    research/quad/uv_mesh.cpp
    research/quad/quadtree_quad.cpp
    research/quad/interior_template_dispatch.cpp
    research/quad/front_interface_audit.cpp
    research/quad/owned_aft_front.cpp)
  target_include_directories(quad_generator_outcome_probe PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/research/quad")
  target_link_libraries(quad_generator_outcome_probe PRIVATE ap_mesh_engine)
  target_compile_features(quad_generator_outcome_probe PRIVATE cxx_std_17)
  add_test(NAME quad.generator.real_global_outcomes
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_generator_outcomes.py"
      --exe "$<TARGET_FILE:quad_generator_outcome_probe>"
      --root "${CMAKE_CURRENT_SOURCE_DIR}" --model eistute)
  set_tests_properties(quad.generator.real_global_outcomes PROPERTIES
    LABELS "research-quad;application;required-gate" TIMEOUT 350)
  # Cross-model real GeneratorAdaptive outcome verification (same frozen settings).
  add_test(NAME quad.generator.real_global_outcomes.book
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/quad/test_generator_outcomes.py"
      --exe "$<TARGET_FILE:quad_generator_outcome_probe>"
      --root "${CMAKE_CURRENT_SOURCE_DIR}" --model book)
  set_tests_properties(quad.generator.real_global_outcomes.book PROPERTIES
    LABELS "research-quad;application;required-gate" TIMEOUT 350)
endif()
