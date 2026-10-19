# Local tooling tests are distinct from application and scientific validation.
include(CTest)
if(BUILD_TESTING)
  find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
  add_subdirectory(tests/memory)
  add_subdirectory(tests/mesh_memory)
  add_test(NAME application.triangle_observer_contracts COMMAND triangle_observer_probe contracts)
  set_tests_properties(application.triangle_observer_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.submesh_lifetime_contracts COMMAND submesh_lifetime_probe contracts)
  set_tests_properties(application.submesh_lifetime_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.triangle_construction_contracts COMMAND triangle_construction_probe contracts)
  set_tests_properties(application.triangle_construction_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.element_adoption_contracts COMMAND element_adoption_probe contracts)
  set_tests_properties(application.element_adoption_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.mesh_adoption_contracts COMMAND mesh_adoption_probe contracts)
  set_tests_properties(application.mesh_adoption_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_subdirectory(tests/uv_memory)
  add_subdirectory(tests/curve_memory)
  add_test(NAME application.curve_collection_contracts COMMAND curve_collection_probe contracts)
  add_test(NAME application.curve_copy_contracts COMMAND curve_copy_probe contracts)
  add_test(NAME application.geometry_adoption_contracts COMMAND geometry_adoption_probe contracts)
  add_test(NAME application.curve_synchronization_contracts COMMAND curve_synchronization_probe contracts)
  add_test(NAME application.curve_snapshot_contracts COMMAND curve_snapshot_probe contracts)
  add_test(NAME application.curve_rebuild_contracts COMMAND curve_rebuild_probe contracts)
  add_test(NAME application.curve_samples_contracts COMMAND curve_samples_probe contracts)
  add_test(NAME application.curve_sample_graph_contracts COMMAND curve_sample_graph_probe contracts)
  add_test(NAME application.curve_sample_lifetime_contracts COMMAND curve_sample_lifetime_probe contracts)
  add_test(NAME application.initial_mesh_contracts COMMAND initial_mesh_probe contracts)
  set_tests_properties(application.initial_mesh_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_sample_lifetime_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_sample_graph_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.curve_publication_contracts COMMAND curve_publication_probe contracts)
  set_tests_properties(application.curve_publication_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_samples_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_rebuild_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_snapshot_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_synchronization_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.geometry_adoption_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_copy_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  set_tests_properties(application.curve_collection_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.uv_lifetime COMMAND uv_lifetime_probe contracts)
  set_tests_properties(application.uv_lifetime
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 60)
  add_test(NAME application.uv_primitive_contracts COMMAND uv_lifetime_probe primitive-contracts)
  set_tests_properties(application.uv_primitive_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.uv_registration_contracts COMMAND uv_lifetime_probe registration-contracts)
  set_tests_properties(application.uv_registration_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.uv_unowned_cell COMMAND uv_lifetime_probe unowned-cell-contracts)
  set_tests_properties(application.uv_unowned_cell
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.uv_tree_contracts COMMAND uv_lifetime_probe tree-contracts)
  set_tests_properties(application.uv_tree_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.uv_angle_contracts COMMAND uv_lifetime_probe angle-contracts)
  set_tests_properties(application.uv_angle_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.uv_parametric_contracts COMMAND uv_lifetime_probe parametric-contracts)
  set_tests_properties(application.uv_parametric_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.node_lifetime COMMAND node_lifetime_probe contracts)
  set_tests_properties(application.node_lifetime
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME tooling.controls
    COMMAND "${Python3_EXECUTABLE}" -m unittest discover
      -s "${CMAKE_SOURCE_DIR}/tests/tooling" -p "test_*.py" -v)
  add_test(NAME reference.archived_eistute_artifact
    COMMAND "${Python3_EXECUTABLE}" scripts/verify_reference.py)
  add_test(NAME application.invalid_inputs
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/cli_failures.py"
      --exe "$<TARGET_FILE:ap_mesh>" --workspace "${CMAKE_BINARY_DIR}/input-controls")
  add_test(NAME application.boundary_orientation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/boundary_orientation_case.py"
      --exe "$<TARGET_FILE:ap_mesh>" --workspace "${CMAKE_BINARY_DIR}/orientation-controls")
  set_tests_properties(application.boundary_orientation
    PROPERTIES LABELS "application;boundary-incidence;required-gate" TIMEOUT 300)
  add_test(NAME application.metric_schema
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/metric_schema_case.py"
      --exe "$<TARGET_FILE:ap_mesh>" --workspace "${CMAKE_BINARY_DIR}/metric-schema-controls")
  set_tests_properties(application.metric_schema
    PROPERTIES LABELS "application;metric-schema;required-gate" TIMEOUT 90)
  set(orientation_probe_sources ${AP_MESH_SOURCES})
  list(REMOVE_ITEM orientation_probe_sources "${CMAKE_SOURCE_DIR}/src/main.cpp")
  add_executable(curve_orientation_probe
    "${CMAKE_SOURCE_DIR}/tests/curve_orientation_probe.cpp" ${orientation_probe_sources})
  target_compile_features(curve_orientation_probe PRIVATE cxx_std_17)
  target_include_directories(curve_orientation_probe PRIVATE "${CMAKE_SOURCE_DIR}/include")
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(curve_orientation_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
  if(AP_MESH_DISABLE_STRICT_ALIASING AND NOT MSVC)
    target_compile_options(curve_orientation_probe PRIVATE -fno-strict-aliasing)
  endif()
  add_test(NAME application.curve_orientation_arclength COMMAND curve_orientation_probe)
  set_tests_properties(application.curve_orientation_arclength
    PROPERTIES LABELS "application;boundary-incidence;required-gate" TIMEOUT 30)
  add_test(NAME tooling.tidy_header_scope
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/tidy_scope_case.py")
  set_tests_properties(tooling.tidy_header_scope
    PROPERTIES LABELS "tooling;required-gate" TIMEOUT 60)
  add_executable(input_validation_probe "${CMAKE_SOURCE_DIR}/tests/input_validation_probe.cpp")
  target_compile_features(input_validation_probe PRIVATE cxx_std_17)
  target_include_directories(input_validation_probe PRIVATE "${CMAKE_SOURCE_DIR}/include")
  add_executable(smoothing_adjacency_probe "${CMAKE_SOURCE_DIR}/tests/smoothing_adjacency_probe.cpp")
  target_compile_features(smoothing_adjacency_probe PRIVATE cxx_std_17)
  target_include_directories(smoothing_adjacency_probe PRIVATE "${CMAKE_SOURCE_DIR}/include")
  add_test(NAME application.smoothing_adjacency_order COMMAND smoothing_adjacency_probe)
  set_tests_properties(application.smoothing_adjacency_order
    PROPERTIES LABELS "application;numerical-control" TIMEOUT 30)
  add_test(NAME application.valid_input_grammar
    COMMAND input_validation_probe
      "${CMAKE_SOURCE_DIR}/input_models/eistute2.fixed.bp"
      "${CMAKE_SOURCE_DIR}/input_models/book_v7a.bp"
      "${CMAKE_SOURCE_DIR}/input_models/ribbed_bracket_nm_decor.bp")
  set_tests_properties(tooling.controls reference.archived_eistute_artifact
    PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" TIMEOUT 60)
  set_tests_properties(tooling.controls PROPERTIES LABELS "tooling")
  set_tests_properties(reference.archived_eistute_artifact PROPERTIES LABELS "archived-artifact")
  set_tests_properties(application.invalid_inputs PROPERTIES LABELS "application;negative-input" TIMEOUT 60)
  set_tests_properties(application.valid_input_grammar PROPERTIES LABELS "application;positive-input" TIMEOUT 30)
endif()
