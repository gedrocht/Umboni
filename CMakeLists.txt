cmake_minimum_required(VERSION 3.27)

project(
  umboni_new_england_weather_intelligence_platform
  VERSION 0.1.0
  DESCRIPTION "Fortran weather simulation engine for the Umboni platform."
  LANGUAGES Fortran
)

include(CTest)

set(CMAKE_Fortran_STANDARD 2018)
set(CMAKE_Fortran_STANDARD_REQUIRED ON)
set(CMAKE_Fortran_EXTENSIONS OFF)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

option(ENABLE_STRICT_FORTRAN_WARNINGS "Enable compiler warnings and treat them as errors." ON)
option(ENABLE_FORTRAN_ADDRESS_SANITIZER "Enable address and undefined behavior sanitizers when using GNU Fortran." OFF)
option(ENABLE_FORTRAN_COVERAGE "Enable GNU Fortran coverage instrumentation." OFF)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/FortranCompilerConfiguration.cmake)

add_subdirectory(fortran)

