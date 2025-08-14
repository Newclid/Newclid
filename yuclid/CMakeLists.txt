cmake_minimum_required(VERSION 3.28 FATAL_ERROR)
project(Yuclid
  VERSION 0.1
  DESCRIPTION "Fast C++ DD/AR engine"
  LANGUAGES CXX)
enable_testing()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

function(yuclid_check_cxx_feature feature_name source_file description)
  if (NOT DEFINED ${feature_name})
    message(CHECK_START "Performing Test ${description}")

    try_compile(${feature_name}
      SOURCES "${source_file}"
      CXX_STANDARD 23
      LOG_DESCRIPTION "${description}"
      ${ARGN}
    )

    if (${${feature_name}})
      message(CHECK_PASS "Success")
      add_compile_definitions(${feature_name})
    else()
      message(CHECK_FAIL "Fail")
    endif()
  endif()
endfunction()

yuclid_check_cxx_feature(
  HAVE_ZIP_TRANSFORM
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake/zip_transform.cpp"
  "std::views::zip_transform"
)

if(MSVC)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4 /WX")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -Werror")
endif()

if(POLICY CMP0167)
  cmake_policy(SET CMP0167 NEW)
endif()

set(WITH_SAFE_NUMERICS_DEFAULT "ON")
if(WIN32)
  set(WITH_SAFE_NUMERICS_DEFAULT "OFF")
endif()

option(WITH_SAFE_NUMERICS
  "Use boost::safe_numerics for runtime type overflow checks"
  ${WITH_SAFE_NUMERICS_DEFAULT}
)

option(USE_STATIC_LINK "Link statically to external libraries" ON)
option(BUILD_DOC "Build doxygen documentation" ON)

if (USE_STATIC_LINK)
  set(Boost_USE_STATIC_LIBS ON)
  if(MSVC)
    if(CMAKE_BUILD_TYPE MATCHES "Debug")
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MTd")
    else()
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MT")
    endif()
  elseif(NOT APPLE)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")
  endif()
endif()

find_package(Boost 1.83 REQUIRED
  COMPONENTS log log_setup json program_options system unit_test_framework headers)

yuclid_check_cxx_feature(
  HAVE_VARIABLES_MAP_CONTAINS
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake/variables_map_contains.cpp"
  "boost::program_options::variables_map::contains"
  LINK_LIBRARIES Boost::program_options
)

if(WITH_SAFE_NUMERICS)
  add_compile_definitions(WITH_SAFE_NUMERICS)
endif()

add_subdirectory(src)
add_subdirectory(test)

if (BUILD_DOC)
  find_package(Doxygen)
  if (DOXYGEN_FOUND)
    set(DOXYGEN_CALL_GRAPH YES)
    set(DOXYGEN_CALLER_GRAPH YES)
    doxygen_add_docs(
      docs
      src
      ALL
      COMMENT "Generating Doxygen documentation"
    )

    message(STATUS "Doxygen documentation target 'docs' created.")
    message(STATUS "Run 'cmake --build . --target docs' or 'cmake --build .' to generate documentation.")
  else ()
    message(STATUS "Doxygen not found. Documentation will not be generated.")
  endif ()
endif()
