include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG "v2.10.0"
)
FetchContent_MakeAvailable(pybind11)

message(STATUS "Third-party: adding pybind11")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${pybind11_SOURCE_DIR}/contrib")