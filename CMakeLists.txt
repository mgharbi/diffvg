cmake_minimum_required(VERSION 3.15)

project(diffvg VERSION 0.0.1 DESCRIPTION "Differentiable Vector Graphics")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(SRCS atomic.h
    color.h
    cdf.h
    cuda_utils.h
    diffvg.h
    edge_query.h
    filter.h
    matrix.h
    parallel.h
    pcg.h
    ptr.h
    sample_boundary.h
    scene.h
    shape.h
    solve.h
    vector.h
    within_distance.h
    winding_number.h
    atomic.cpp
    color.cpp
    diffvg.cpp
    parallel.cpp
    scene.cpp
    shape.cpp)
add_library(diffvg MODULE ${SRCS})

include(CheckLanguage)
check_language(CUDA)
set(DIFFVG_CUDA OFF)
if(CMAKE_CUDA_COMPILER)
    set(DIFFVG_CUDA ON)
    enable_language(CUDA)
    message(STATUS "CUDA found, build with CUDA support")
    set(CMAKE_CUDA_STANDARD 14)

    # if(NOT WIN32)
        # Hack: for some reason the line above doesn't work on some Linux systems.
        # set(CUDA_NVCC_FLAGS "${CUDA_NVCC_FLAGS} -std=c++11")
        # set(CUDA_NVCC_FLAGS_DEBUG "-g -G")
    # endif()

    target_compile_definitions(diffvg PUBLIC COMPILE_WITH_CUDA)
    set_target_properties(diffvg PROPERTIES CUDA_ARCHITECTURES "60;72")
    set_source_files_properties(
        diffvg.cpp
        scene.cpp
        PROPERTIES LANGUAGE CUDA)
else()
    message(STATUS "CUDA not found, build without CUDA support")
    include(thrust)
    find_package(Thrust REQUIRED CONFIG)
    thrust_create_target(Thrust HOST CPP DEVICE CPP)
    target_link_libraries(diffvg Thrust)
endif()

set (CMAKE_FIND_FRAMEWORK NEVER)
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# if(NOT MSVC)
#     # These compile definitions are not meaningful for MSVC
#     add_compile_options(-Wall -g -O3 -fvisibility=hidden -Wno-unknown-pragmas)
# else()
#     # add_compile_options(/Wall /Zi)
#     # add_link_options(/DEBUG)
# endif()

include(pybind11)
target_link_libraries(diffvg pybind11::pybind11)
# if(WIN32)
#     # See: https://pybind11.readthedocs.io/en/master/compiling.html#advanced-interface-library-target
#     target_link_libraries(diffvg pybind11::module)
#     set_target_properties(diffvg PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
#         SUFFIX "${PYTHON_MODULE_EXTENSION}")
# endif()

if(APPLE)
    # The "-undefined dynamic_lookup" is a hack for systems with
    # multiple Python installed. If we link a particular Python version
    # here, and we import it with a different Python version later.
    # likely a segmentation fault.
    # The solution for Linux Mac OS machines, as mentioned in
    # https://github.com/pybind/pybind11/blob/master/tools/pybind11Tools.cmake
    # is to not link against Python library at all and resolve the symbols
    # at compile time.
    set(DYNAMIC_LOOKUP "-undefined dynamic_lookup")
endif()

target_link_libraries(diffvg ${DYNAMIC_LOOKUP})

set_target_properties(diffvg PROPERTIES SKIP_BUILD_RPATH FALSE)
set_target_properties(diffvg PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)

if(UNIX AND NOT APPLE)
    set_target_properties(diffvg PROPERTIES INSTALL_RPATH "$ORIGIN")
elseif(APPLE)
    set_target_properties(diffvg PROPERTIES INSTALL_RPATH "@loader_path")
endif()

set_property(TARGET diffvg PROPERTY CXX_STANDARD 14)
set_target_properties(diffvg PROPERTIES PREFIX "")

# # Still enable assertion in release mode
# string(REPLACE "/DNDEBUG" "" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
# string(REPLACE "-DNDEBUG" "" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
# string(REPLACE "/DNDEBUG" "" CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")
# string(REPLACE "-DNDEBUG" "" CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")
# string(REPLACE "/DNDEBUG" "" CMAKE_C_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
# string(REPLACE "-DNDEBUG" "" CMAKE_C_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
# string(REPLACE "/DNDEBUG" "" CMAKE_C_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")
# string(REPLACE "-DNDEBUG" "" CMAKE_C_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO}")

if(NOT WIN32)
    find_package(TensorFlow)
    if(TensorFlow_FOUND)
        add_subdirectory(pydiffvg_tensorflow/custom_ops)
    else()
        message(INFO " Building without TensorFlow support (not found)")
    endif()
endif()
