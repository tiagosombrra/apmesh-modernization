# Local tooling tests are distinct from application and scientific validation.
include(CTest)
if(BUILD_TESTING)
  find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
  add_subdirectory(tests/memory)
  add_subdirectory(tests/mesh_memory)
  add_subdirectory(tests/model_memory)
  add_subdirectory(tests/patch_copy_memory)
  add_subdirectory(tests/hermite_observer_memory)
  add_subdirectory(tests/hermite_construction_memory)
  add_test(NAME application.hermite_construction_contracts COMMAND hermite_construction_probe contracts)
  add_test(NAME tooling.hermite_construction_preservation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/audit_hermite_construction.py"
      --candidate-root "${CMAKE_SOURCE_DIR}")
  set_tests_properties(application.hermite_construction_contracts tooling.hermite_construction_preservation
    PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 30)
  add_test(NAME application.hermite_observer_contracts COMMAND hermite_observer_probe contracts)
  add_test(NAME tooling.hermite_observer_preservation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/audit_hermite_observers.py"
      --candidate-root "${CMAKE_SOURCE_DIR}")
  set_tests_properties(application.hermite_observer_contracts tooling.hermite_observer_preservation
    PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 30)
  add_test(NAME application.detached_patch_copy_contracts COMMAND detached_patch_copy_probe contracts)
  add_test(NAME tooling.detached_patch_copy_preservation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/audit_patch_copy.py"
      --candidate-root "${CMAKE_SOURCE_DIR}")
  set_tests_properties(application.detached_patch_copy_contracts tooling.detached_patch_copy_preservation
    PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 30)
  add_test(NAME application.model_ownership_contracts COMMAND model_ownership_probe contracts)
  add_test(NAME tooling.model_ownership_preservation
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/audit_model_ownership.py"
      --candidate-root "${CMAKE_SOURCE_DIR}")
  set_tests_properties(application.model_ownership_contracts tooling.model_ownership_preservation
    PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 30)
  add_test(NAME application.triangle_area_contracts COMMAND triangle_area_probe contracts)
  add_test(NAME application.triangle_area_real_error COMMAND triangle_area_real_probe contracts)
  set_tests_properties(application.triangle_area_contracts application.triangle_area_real_error
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.error_estimate_contracts COMMAND error_estimate_probe contracts)
  set_tests_properties(application.error_estimate_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.triangle_count_contracts COMMAND triangle_count_probe contracts)
  set_tests_properties(application.triangle_count_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  add_test(NAME application.estimate_mesh_contracts COMMAND estimate_mesh_probe contracts)
  set_tests_properties(application.estimate_mesh_contracts
    PROPERTIES LABELS "application;contracts;memory")
  add_test(NAME application.triangle_lifetime_contracts COMMAND triangle_lifetime_probe contracts)
  set_tests_properties(application.triangle_lifetime_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
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
  add_subdirectory(tests/face_quality)
  add_test(NAME application.face_quality_scratch COMMAND face_quality_probe snapshot)
  set_tests_properties(application.face_quality_scratch
    PROPERTIES LABELS "application;portability;required-gate" TIMEOUT 30)
  add_subdirectory(tests/domain_cache_memory)
  add_subdirectory(tests/front_angle_memory)
  add_subdirectory(tests/front_face_memory)
  add_subdirectory(tests/face_adoption_memory)
  add_subdirectory(tests/front_marker_memory)
  add_subdirectory(tests/shortcut_face_memory)
  add_subdirectory(tests/first_edge_memory)
  add_subdirectory(tests/second_edge_memory)
  add_subdirectory(tests/ideal_vertex_memory)
  add_subdirectory(tests/template_prefix)
  add_test(NAME application.domain_uv_cache_contracts COMMAND domain_cache_probe contracts)
  set_tests_properties(application.domain_uv_cache_contracts
    PROPERTIES LABELS "application;memory;required-gate" TIMEOUT 90)
  add_subdirectory(tests/curve_memory)
  add_test(NAME application.charge_input_contracts COMMAND charge_input_probe contracts
    "${PROJECT_SOURCE_DIR}/tests/curve_memory/data/charge_input.bp")
  set_tests_properties(application.charge_input_contracts
    PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 30)
  if(TARGET charge_input_real_probe)
    add_test(NAME application.charge_input_real_numbers COMMAND charge_input_real_probe repeat-3-1
      "${PROJECT_SOURCE_DIR}/tests/curve_memory/data/charge_input.bp")
    set_tests_properties(application.charge_input_real_numbers
      PROPERTIES LABELS "application;numerical;required-gate" TIMEOUT 30)
  endif()
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
  add_executable(curve_orientation_probe
    "${CMAKE_SOURCE_DIR}/tests/curve_orientation_probe.cpp")
  target_link_libraries(curve_orientation_probe PRIVATE ap_mesh_engine)
  target_compile_features(curve_orientation_probe PRIVATE cxx_std_17)
  if(MSVC)
    target_compile_options(curve_orientation_probe PRIVATE /permissive-)
  endif()
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
  add_test(NAME application.serial_cpp17_portability
    COMMAND curve_orientation_probe --serial-portability)
  set_tests_properties(application.serial_cpp17_portability
    PROPERTIES LABELS "application;portability;required-gate" TIMEOUT 30)
  add_executable(attempt_metrics_probe
    "${CMAKE_SOURCE_DIR}/tests/attempt_metrics_probe.cpp")
  target_link_libraries(attempt_metrics_probe PRIVATE ap_mesh_engine)
  if(WIN32)
    target_link_libraries(attempt_metrics_probe PRIVATE Rstrtmgr)
  endif()
  target_compile_features(attempt_metrics_probe PRIVATE cxx_std_17)
  target_include_directories(attempt_metrics_probe PRIVATE "${CMAKE_SOURCE_DIR}/include")
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(attempt_metrics_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
  if(AP_MESH_DISABLE_STRICT_ALIASING AND NOT MSVC)
    target_compile_options(attempt_metrics_probe PRIVATE -fno-strict-aliasing)
  endif()
  add_test(NAME application.attempt_metrics
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/attempt_metrics_case.py"
      --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/attempt-metrics-controls")
  set_tests_properties(application.attempt_metrics
    PROPERTIES LABELS "application;metric-schema;required-gate" TIMEOUT 60)
  add_test(NAME application.generator_diagnostics
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/generator_diagnostics_case.py"
      --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/generator-diagnostics-controls")
  set_tests_properties(application.generator_diagnostics
    PROPERTIES LABELS "application;metric-schema;negative-input;required-gate" TIMEOUT 90)
  if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND NOT AP_MESH_USE_MPI AND NOT AP_MESH_USE_OPENMP)
    set_property(SOURCE "${CMAKE_SOURCE_DIR}/tests/attempt_metrics_probe.cpp" APPEND
      PROPERTY COMPILE_DEFINITIONS AP_MESH_DOMAIN_FAILURE_WRAP=1)
    target_link_options(attempt_metrics_probe PRIVATE
      "-Wl,--wrap=_ZN10Par2DJMesh3AFT14AdvancingFront7executeERKNSt7__cxx114listIPNS_6Basics4FaceESaIS6_EEE"
      "-Wl,--wrap=_ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii"
      "-Wl,--wrap=_ZNK7Adapter23GetPatchStructuralStatsEi"
      "-Wl,--wrap=_ZN12MeshAdaptive31InsertSubMeshAdaptiveByPositionEP7SubMeshi"
      "-Wl,--wrap=_Znwy" "-Wl,--wrap=_ZdlPv" "-Wl,--wrap=_ZdlPvy")
    add_test(NAME application.domain_candidate_contracts
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/domain_candidate_case.py"
        --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/domain-candidate-controls")
    set_tests_properties(application.domain_candidate_contracts
      PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 90)
    add_test(NAME application.candidate_snapshots
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/candidate_snapshot_case.py"
        --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/candidate-snapshot-controls")
    set_tests_properties(application.candidate_snapshots
      PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 90)
    add_test(NAME application.accepted_mesh_root
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/accepted_root_case.py"
        --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/accepted-root-controls")
    set_tests_properties(application.accepted_mesh_root
      PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 90)
    add_test(NAME application.domain_observer_cleanup
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/domain_observer_case.py"
        --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/domain-observer-controls")
    set_tests_properties(application.domain_observer_cleanup
      PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 150)
    add_test(NAME application.typed_domain_failure
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/typed_domain_failure_case.py"
        --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/typed-domain-controls")
    set_tests_properties(application.typed_domain_failure
      PROPERTIES LABELS "application;lifecycle;required-gate" TIMEOUT 300)
    add_test(NAME application.domain_failure_status
      COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/domain_failure_case.py"
        --exe "$<TARGET_FILE:attempt_metrics_probe>" --workspace "${CMAKE_BINARY_DIR}/domain-failure-controls")
    set_tests_properties(application.domain_failure_status
      PROPERTIES LABELS "application;negative-input;required-gate" TIMEOUT 90)
  endif()
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
