cmake_minimum_required(VERSION 3.20)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  project(apmesh_curve_collections LANGUAGES CXX)
endif()

get_filename_component(default_curve_root "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(AP_MESH_CURVE_SOURCE_ROOT "${default_curve_root}" CACHE PATH "Production tree for curve collection qualification")
option(AP_MESH_CURVE_ASAN "Instrument the narrow MSVC curve collection probe" OFF)
set(curve_sources
  data/curve/curve_adaptive.cpp data/curve/curve_adaptive_parametric.cpp
  data/point_adaptive.cpp data/vector_adaptive.cpp data/patch/patch.cpp
  crab_mesh/numerical/function.cpp crab_mesh/numerical/bisection_equation_root.cpp)
list(TRANSFORM curve_sources PREPEND "${AP_MESH_CURVE_SOURCE_ROOT}/src/")
add_executable(curve_collection_probe probe.cpp ${curve_sources})
add_executable(curve_copy_probe copy_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp")
add_executable(geometry_adoption_probe adoption_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp")
set(AP_MESH_SYNC_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_synchronization.cpp" CACHE FILEPATH "Curve synchronization implementation")
add_executable(curve_synchronization_probe synchronization_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_SYNC_IMPLEMENTATION}")
if(MSVC)
  target_compile_options(curve_synchronization_probe PRIVATE /permissive-)
  # Debug iterator proxies allocate inside noexcept constructors. Keep the CRT
  # heap instrument while matching the serial/ASan container ABI for this target.
  target_compile_definitions(curve_synchronization_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
endif()
foreach(curve_probe IN ITEMS curve_collection_probe curve_copy_probe geometry_adoption_probe curve_synchronization_probe)
  target_compile_features(${curve_probe} PRIVATE cxx_std_17)
  target_include_directories(${curve_probe} PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
  if(MSVC)
    target_compile_options(${curve_probe} PRIVATE /utf-8 /W4 /EHsc)
    if(AP_MESH_CURVE_ASAN)
      target_compile_options(${curve_probe} PRIVATE /fsanitize=address /Zi)
      target_link_options(${curve_probe} PRIVATE /INCREMENTAL:NO)
    endif()
  elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(${curve_probe} PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endforeach()

# Own the reader result and pending charge patch while retaining committed Geometry.
find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
set(charge_backend "${CMAKE_CURRENT_BINARY_DIR}/charge_input_backend")
set(charge_input "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/charge_input_estimate.cpp")
set(control_reader "${AP_MESH_CURVE_SOURCE_ROOT}/src/input_output/control_patch_reader.cpp")
set(charge_outputs "${charge_backend}/lifetime.cpp")
if(NOT EXISTS "${charge_input}")
  set(charge_input "${charge_backend}/caller.cpp")
  set(control_reader "${charge_backend}/reader.cpp")
  list(APPEND charge_outputs "${charge_input}" "${control_reader}")
endif()
add_custom_command(OUTPUT ${charge_outputs}
  BYPRODUCTS "${charge_backend}/extraction.json"
  COMMAND "${Python3_EXECUTABLE}" "${default_curve_root}/tools/extract_charge_input_backend.py"
          --root "${AP_MESH_CURVE_SOURCE_ROOT}" --output "${charge_backend}"
  DEPENDS "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/charge_estimate_process.cpp"
          "${AP_MESH_CURVE_SOURCE_ROOT}/src/input_output/patch_reader.cpp"
          "${default_curve_root}/tools/extract_charge_input_backend.py"
  VERBATIM)
set(charge_sources ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/vertex_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/mesh_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/input_output/write_obj_file.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/timer/timer.cpp"
  "${charge_input}" "${control_reader}")
add_executable(charge_input_probe charge_input_probe.cpp ${charge_sources} "${charge_backend}/lifetime.cpp")
target_compile_features(charge_input_probe PRIVATE cxx_std_17)
target_include_directories(charge_input_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(charge_input_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(charge_input_probe PRIVATE _USE_MATH_DEFINES $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  # The DLL Debug STL's precompiled numeric output aborts on an allocation
  # denial inside its debug machinery. The independent stream control reproduces
  # this without application code. Keep the CRT heap probe and instantiate the
  # matching non-debug-iterator STL in this executable with the static Debug CRT.
  set_property(TARGET charge_input_probe PROPERTY MSVC_RUNTIME_LIBRARY
    "$<IF:$<CONFIG:Debug>,MultiThreadedDebug,MultiThreadedDLL>")
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(charge_input_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(charge_input_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(charge_input_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(charge_input_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()
target_include_directories(curve_synchronization_probe PRIVATE "${default_curve_root}/include")

set(AP_MESH_SNAPSHOT_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_snapshots.cpp" CACHE FILEPATH "Curve sample snapshot implementation")
add_executable(curve_snapshot_probe snapshot_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_SNAPSHOT_IMPLEMENTATION}")
target_compile_features(curve_snapshot_probe PRIVATE cxx_std_17)
target_include_directories(curve_snapshot_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_snapshot_probe PRIVATE /utf-8 /W4 /EHsc /permissive-)
  target_compile_definitions(curve_snapshot_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_snapshot_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_snapshot_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(curve_snapshot_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()

set(AP_MESH_REBUILD_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_rebuild.cpp" CACHE FILEPATH "Curve target rebuild implementation")
add_executable(curve_rebuild_probe rebuild_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_REBUILD_IMPLEMENTATION}")
target_compile_features(curve_rebuild_probe PRIVATE cxx_std_17)
target_include_directories(curve_rebuild_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_rebuild_probe PRIVATE /utf-8 /W4 /EHsc /permissive-)
  target_compile_definitions(curve_rebuild_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_rebuild_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_rebuild_probe PRIVATE /INCREMENTAL:NO)
  endif()
elseif(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
  target_link_options(curve_rebuild_probe PRIVATE -static -static-libgcc -static-libstdc++)
endif()

set(AP_MESH_SAMPLES_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/adapter/curve_samples.cpp" CACHE FILEPATH "Serial adapter sample construction implementation")
add_executable(curve_samples_probe samples_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_SAMPLES_IMPLEMENTATION}")
target_compile_features(curve_samples_probe PRIVATE cxx_std_17)
target_include_directories(curve_samples_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_samples_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(curve_samples_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_samples_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_samples_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(curve_samples_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(curve_samples_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

set(AP_MESH_PUBLICATION_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_publication.cpp" CACHE FILEPATH "Curve publication transaction implementation")
set(AP_MESH_PUBLICATION_HEADER "" CACHE FILEPATH "Original publication block adapter")
add_executable(curve_publication_probe publication_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/adapter/curve_samples.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_rebuild.cpp")
if(AP_MESH_PUBLICATION_HEADER)
  target_compile_definitions(curve_publication_probe PRIVATE AP_MESH_PUBLICATION_HEADER="${AP_MESH_PUBLICATION_HEADER}")
else()
  target_sources(curve_publication_probe PRIVATE "${AP_MESH_PUBLICATION_IMPLEMENTATION}")
endif()
target_compile_features(curve_publication_probe PRIVATE cxx_std_17)
target_include_directories(curve_publication_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_publication_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(curve_publication_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_publication_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_publication_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(curve_publication_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(curve_publication_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

set(AP_MESH_SAMPLE_GRAPH_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_graph.cpp" CACHE FILEPATH "Curve publication transaction implementation")
set(AP_MESH_SAMPLE_GRAPH_HEADER "" CACHE FILEPATH "Original publication block adapter")
add_executable(curve_sample_graph_probe graph_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/adapter/curve_samples.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_rebuild.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_publication.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp")
if(AP_MESH_SAMPLE_GRAPH_HEADER)
  target_compile_definitions(curve_sample_graph_probe PRIVATE AP_MESH_SAMPLE_GRAPH_HEADER="${AP_MESH_SAMPLE_GRAPH_HEADER}")
else()
  target_sources(curve_sample_graph_probe PRIVATE "${AP_MESH_SAMPLE_GRAPH_IMPLEMENTATION}")
endif()
target_compile_features(curve_sample_graph_probe PRIVATE cxx_std_17)
target_include_directories(curve_sample_graph_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_sample_graph_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(curve_sample_graph_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_sample_graph_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_sample_graph_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(curve_sample_graph_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(curve_sample_graph_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

set(AP_MESH_SAMPLE_LIFETIME_HEADER "" CACHE FILEPATH "Pinned final-cleanup block adapter")
add_executable(curve_sample_lifetime_probe lifetime_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/adapter/curve_samples.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_rebuild.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_publication.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_graph.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp")
if(AP_MESH_SAMPLE_LIFETIME_HEADER)
  target_compile_definitions(curve_sample_lifetime_probe PRIVATE AP_MESH_SAMPLE_LIFETIME_HEADER="${AP_MESH_SAMPLE_LIFETIME_HEADER}")
else()
  target_sources(curve_sample_lifetime_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_lifetime.cpp")
endif()
target_compile_features(curve_sample_lifetime_probe PRIVATE cxx_std_17)
target_include_directories(curve_sample_lifetime_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(curve_sample_lifetime_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(curve_sample_lifetime_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curve_sample_lifetime_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curve_sample_lifetime_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(curve_sample_lifetime_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(curve_sample_lifetime_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

set(AP_MESH_INITIAL_MESH_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/initial_mesh.cpp" CACHE FILEPATH "Serial initial mesh implementation")
add_executable(initial_mesh_probe initial_mesh_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/mesh_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_lifetime.cpp"
  "${AP_MESH_INITIAL_MESH_IMPLEMENTATION}")
target_compile_features(initial_mesh_probe PRIVATE cxx_std_17)
target_include_directories(initial_mesh_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(initial_mesh_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(initial_mesh_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(initial_mesh_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(initial_mesh_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(initial_mesh_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(initial_mesh_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

set(AP_MESH_ESTIMATE_MESH_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/initial_mesh_estimate.cpp" CACHE FILEPATH "Estimator initial mesh implementation")
add_executable(estimate_mesh_probe estimate_mesh_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/mesh_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_lifetime.cpp"
  "${AP_MESH_ESTIMATE_MESH_IMPLEMENTATION}")
target_compile_features(estimate_mesh_probe PRIVATE cxx_std_17)
target_include_directories(estimate_mesh_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(estimate_mesh_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(estimate_mesh_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(estimate_mesh_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(estimate_mesh_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(estimate_mesh_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(estimate_mesh_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

set(AP_MESH_TRIANGLE_COUNT_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/triangle_count_estimate.cpp" CACHE FILEPATH "Triangle-count caller implementation")
add_executable(triangle_count_probe triangle_count_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/mesh_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_lifetime.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/initial_mesh_estimate.cpp"
  "${AP_MESH_TRIANGLE_COUNT_IMPLEMENTATION}")
target_compile_features(triangle_count_probe PRIVATE cxx_std_17)
target_include_directories(triangle_count_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(triangle_count_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(triangle_count_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(triangle_count_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(triangle_count_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(triangle_count_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(triangle_count_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
set(error_backend "${CMAKE_CURRENT_BINARY_DIR}/error_estimate_backend.cpp")
add_custom_command(OUTPUT "${error_backend}"
  COMMAND "${Python3_EXECUTABLE}" "${default_curve_root}/tools/extract_error_estimate_backend.py"
          --root "${AP_MESH_CURVE_SOURCE_ROOT}" --output "${error_backend}"
  DEPENDS "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/generator_adaptive.cpp"
          "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/charge_estimate_process.cpp"
          "${default_curve_root}/tools/extract_error_estimate_backend.py"
  VERBATIM)
set(AP_MESH_ERROR_ESTIMATE_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/error_estimate.cpp" CACHE FILEPATH "Error evaluator caller implementation")
add_executable(error_estimate_probe error_estimate_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/node_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/element_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/triangle_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/sub_mesh.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/mesh/mesh_adaptive.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/crab_mesh/performer/ranged_id_manager.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_sample_lifetime.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/initial_mesh_estimate.cpp"
  "${AP_MESH_ERROR_ESTIMATE_IMPLEMENTATION}"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/input_output/write_obj_file.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/curvature/curvature_analytical.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/curvature/curvature_discrete.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/curvature/adjacent.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/timer/timer.cpp"
  "${CMAKE_CURRENT_BINARY_DIR}/error_estimate_backend.cpp")
target_compile_features(error_estimate_probe PRIVATE cxx_std_17)
target_include_directories(error_estimate_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
if(MSVC)
  target_compile_options(error_estimate_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(error_estimate_probe PRIVATE _USE_MATH_DEFINES)
  target_compile_definitions(error_estimate_probe PRIVATE $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(error_estimate_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(error_estimate_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(error_estimate_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(error_estimate_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

# The old pinned count implementation has its own private scope. Current callers
# share the selective scope only after matching factory publication semantics.
if(EXISTS "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/estimate_mesh_scope.cpp")
  target_sources(triangle_count_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/estimate_mesh_scope.cpp")
endif()
set(AP_MESH_TRIANGLE_AREA_IMPLEMENTATION "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/triangle_area_estimate.cpp" CACHE FILEPATH "Triangle area orchestration implementation")
get_target_property(area_sources error_estimate_probe SOURCES)
list(REMOVE_ITEM area_sources error_estimate_probe.cpp "${AP_MESH_ERROR_ESTIMATE_IMPLEMENTATION}")
foreach(area_target IN ITEMS triangle_area_probe triangle_area_real_probe)
  add_executable(${area_target} triangle_area_probe.cpp ${area_sources} "${AP_MESH_TRIANGLE_AREA_IMPLEMENTATION}")
  if(EXISTS "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/estimate_mesh_scope.cpp")
    target_sources(${area_target} PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/estimate_mesh_scope.cpp")
  endif()
  if(area_target STREQUAL "triangle_area_real_probe")
    target_sources(${area_target} PRIVATE "${AP_MESH_ERROR_ESTIMATE_IMPLEMENTATION}")
    target_compile_definitions(${area_target} PRIVATE AP_MESH_AREA_REAL_ERROR=1)
  endif()
  target_compile_features(${area_target} PRIVATE cxx_std_17)
  target_include_directories(${area_target} PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include" "${default_curve_root}/include")
  if(MSVC)
    target_compile_options(${area_target} PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
    target_compile_definitions(${area_target} PRIVATE _USE_MATH_DEFINES $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
    if(AP_MESH_CURVE_ASAN)
      target_compile_options(${area_target} PRIVATE /fsanitize=address /Zi)
      target_link_options(${area_target} PRIVATE /INCREMENTAL:NO)
    endif()
  else()
    target_compile_options(${area_target} PRIVATE -fno-elide-constructors)
    if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
      target_link_options(${area_target} PRIVATE -static -static-libgcc -static-libstdc++)
    endif()
  endif()
endforeach()

if(NOT MSVC)
  get_target_property(charge_real_sources error_estimate_probe SOURCES)
  list(REMOVE_ITEM charge_real_sources error_estimate_probe.cpp "${AP_MESH_ERROR_ESTIMATE_IMPLEMENTATION}" "${error_backend}")
  add_executable(charge_input_real_probe charge_input_probe.cpp ${charge_real_sources}
    "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/charge_estimate_process.cpp"
    "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/triangle_count_estimate.cpp"
    "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/estimate_mesh_scope.cpp"
    "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/vertex_adaptive.cpp" "${control_reader}")
  if(EXISTS "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/charge_input_estimate.cpp")
    target_sources(charge_input_real_probe PRIVATE "${charge_input}")
  endif()
  target_compile_features(charge_input_real_probe PRIVATE cxx_std_17)
  target_compile_definitions(charge_input_real_probe PRIVATE AP_MESH_CHARGE_REAL=1 _USE_MATH_DEFINES)
  target_include_directories(charge_input_real_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
  target_compile_options(charge_input_real_probe PRIVATE -fno-elide-constructors -fno-strict-aliasing)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(charge_input_real_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

# Curvature samples use actual patch/curvature units and an explicit original adapter.
set(sample_backend "${CMAKE_CURRENT_BINARY_DIR}/curvature_sample_backend.cpp")
set(sample_adapter_flags)
if(MSVC)
  list(APPEND sample_adapter_flags --fixed-extent)
endif()
add_custom_command(OUTPUT "${sample_backend}"
  COMMAND "${Python3_EXECUTABLE}" "${default_curve_root}/tools/extract_curvature_sample_backend.py"
          --root "${AP_MESH_CURVE_SOURCE_ROOT}" --output "${sample_backend}" ${sample_adapter_flags}
  DEPENDS "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/charge_estimate_process.cpp"
          "${default_curve_root}/tools/extract_curvature_sample_backend.py"
  VERBATIM)
set(sample_sources ${charge_sources})
list(REMOVE_ITEM sample_sources "${charge_input}" "${control_reader}")
add_executable(curvature_sample_probe curvature_sample_probe.cpp ${sample_sources} "${sample_backend}"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/curvature/curvature_analytical.cpp")
if(EXISTS "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/curvature_sample_estimate.cpp")
  target_sources(curvature_sample_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/curvature_sample_estimate.cpp")
  if(TARGET charge_input_real_probe)
    target_sources(charge_input_real_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/src/estimate/curvature_sample_estimate.cpp")
  endif()
endif()
target_compile_features(curvature_sample_probe PRIVATE cxx_std_17)
target_include_directories(curvature_sample_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(curvature_sample_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(curvature_sample_probe PRIVATE _USE_MATH_DEFINES $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  set_property(TARGET curvature_sample_probe PROPERTY MSVC_RUNTIME_LIBRARY
    "$<IF:$<CONFIG:Debug>,MultiThreadedDebug,MultiThreadedDLL>")
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(curvature_sample_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(curvature_sample_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(curvature_sample_probe PRIVATE -fno-elide-constructors -fno-strict-aliasing)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(curvature_sample_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

# Exercise completed Bezier observer lifetime and dependent Geometry retirement.
add_executable(bezier_observer_probe bezier_observer_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_hermite.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/geometry.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/generator/curve_synchronization.cpp")
target_compile_features(bezier_observer_probe PRIVATE cxx_std_17)
target_include_directories(bezier_observer_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(bezier_observer_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(bezier_observer_probe PRIVATE _USE_MATH_DEFINES $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  set_property(TARGET bezier_observer_probe PROPERTY MSVC_RUNTIME_LIBRARY
    "$<IF:$<CONFIG:Debug>,MultiThreadedDebug,MultiThreadedDLL>")
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(bezier_observer_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(bezier_observer_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(bezier_observer_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(bezier_observer_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()

# Exercise actual Bezier constructors and their curve-publication boundary.
add_executable(bezier_construction_probe bezier_construction_probe.cpp ${curve_sources}
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/curve/curve_adaptive_parametric_bezier.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_coons.cpp"
  "${AP_MESH_CURVE_SOURCE_ROOT}/src/data/patch/patch_bezier.cpp")
target_compile_features(bezier_construction_probe PRIVATE cxx_std_17)
target_include_directories(bezier_construction_probe PRIVATE "${AP_MESH_CURVE_SOURCE_ROOT}/include")
if(MSVC)
  target_compile_options(bezier_construction_probe PRIVATE /utf-8 /W4 /EHsc /permissive- /Zc:nrvo-)
  target_compile_definitions(bezier_construction_probe PRIVATE _USE_MATH_DEFINES $<$<CONFIG:Debug>:_ITERATOR_DEBUG_LEVEL=0>)
  set_property(TARGET bezier_construction_probe PROPERTY MSVC_RUNTIME_LIBRARY
    "$<IF:$<CONFIG:Debug>,MultiThreadedDebug,MultiThreadedDLL>")
  if(AP_MESH_CURVE_ASAN)
    target_compile_options(bezier_construction_probe PRIVATE /fsanitize=address /Zi)
    target_link_options(bezier_construction_probe PRIVATE /INCREMENTAL:NO)
  endif()
else()
  target_compile_options(bezier_construction_probe PRIVATE -fno-elide-constructors)
  if(MINGW AND AP_MESH_STATIC_MINGW_RUNTIME)
    target_link_options(bezier_construction_probe PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
endif()
