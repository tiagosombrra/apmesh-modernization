# Local tooling tests are distinct from application and scientific validation.
include(CTest)
if(BUILD_TESTING)
  find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
  add_test(NAME tooling.controls
    COMMAND "${Python3_EXECUTABLE}" -m unittest discover
      -s "${CMAKE_SOURCE_DIR}/tests/tooling" -p "test_*.py" -v)
  add_test(NAME reference.archived_eistute_artifact
    COMMAND "${Python3_EXECUTABLE}" scripts/verify_reference.py)
  set_tests_properties(tooling.controls reference.archived_eistute_artifact
    PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" TIMEOUT 60)
  set_tests_properties(tooling.controls PROPERTIES LABELS "tooling")
  set_tests_properties(reference.archived_eistute_artifact PROPERTIES LABELS "archived-artifact")
endif()
