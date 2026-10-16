# Local tooling tests are distinct from application and scientific validation.
include(CTest)
if(BUILD_TESTING)
  find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
  add_test(NAME tooling.controls
    COMMAND "${Python3_EXECUTABLE}" -m unittest discover
      -s "${CMAKE_SOURCE_DIR}/tests/tooling" -p "test_*.py" -v)
  add_test(NAME reference.archived_eistute_artifact
    COMMAND "${Python3_EXECUTABLE}" scripts/verify_reference.py)
  add_test(NAME application.invalid_inputs
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/cli_failures.py"
      --exe "$<TARGET_FILE:ap_mesh>" --workspace "${CMAKE_BINARY_DIR}/input-controls")
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
