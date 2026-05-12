add_subdirectory(numbers)
include(GNUInstallDirs)

add_library(yuclid
  STATIC
  ar/eqn_index.cpp
  ar/equation.cpp
  ar/equation_traits.cpp
  ar/linear_combination.cpp
  ar/linear_system.cpp
  ar/reduced_equation.cpp
  config_options.cpp
  matchers/matcher.cpp
  matchers/generic_rule_matcher.cpp
  numbers/add_circle.cpp
  numbers/posreal.cpp
  numbers/root_rat.cpp
  numbers/util.cpp
  parser/problem_parser.cpp
  parser/rule_parser.cpp
  rules/theorem_builder.cpp
  problem.cpp
  solver/ddar_solver.cpp
  solver/statement_proof.cpp
  solver/theorem_application.cpp
  statement/angle_eq.cpp
  statement/circumcenter.cpp
  statement/coll.cpp
  statement/cong.cpp
  statement/congruent_triangles.cpp
  statement/cyclic.cpp
  statement/diff_side.cpp
  statement/dist_eq.cpp
  statement/eqn_statement.cpp
  statement/eqratio.cpp
  statement/equal_angles.cpp
  statement/equal_line_angles.cpp
  statement/line_angle_eq.cpp
  statement/midpoint.cpp
  statement/ncoll.cpp
  statement/npara.cpp
  statement/nperp.cpp
  statement/not_equal.cpp
  statement/obtuse_angle.cpp
  statement/orthocenter.cpp
  statement/para.cpp
  statement/parallelogram.cpp
  statement/perp.cpp
  statement/ratio_dist.cpp
  statement/ratio_squared_dist.cpp
  statement/same_clock.cpp
  statement/same_side.cpp
  statement/similar_triangles.cpp
  statement/squared_dist_eq.cpp
  statement/statement.cpp
  statement/thales.cpp
  statement/statement_builder.cpp
  theorem.cpp
  type/angle.cpp
  type/dist.cpp
  type/point.cpp
  type/sin_or_dist.cpp
  type/slope_angle.cpp
  type/squared_dist.cpp
  type/triangle.cpp
)

target_include_directories(yuclid PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")

target_link_libraries(yuclid
  PUBLIC
  Boost::log
  Boost::log_setup
  Boost::json
  Boost::program_options
  Boost::headers
)

add_executable(yuclid_exe main.cpp)
set_property(TARGET yuclid_exe PROPERTY OUTPUT_NAME yuclid)
target_link_libraries(yuclid_exe PRIVATE
  yuclid
)

if (DEFINED SKBUILD_SCRIPTS_DIR)
  set(YUCLID_RUNTIME_DEST "${SKBUILD_SCRIPTS_DIR}")
else()
  set(YUCLID_RUNTIME_DEST "${CMAKE_INSTALL_BINDIR}")
endif()

# Install yuclid.exe and any Boost DLLs it depends on into the same directory.
# On Windows, DLLs must live next to the exe or the exe crashes at startup
# with a missing DLL error (exit code 0xC0000135).
# $<TARGET_RUNTIME_DLLS:...> resolves automatically from Boost target metadata.
# OPTIONAL silently skips this when Boost is static (no DLLs to copy).
if(WIN32)
  install(TARGETS yuclid_exe
    RUNTIME DESTINATION "${YUCLID_RUNTIME_DEST}"
  )
  install(FILES $<TARGET_RUNTIME_DLLS:yuclid_exe>
    DESTINATION "${YUCLID_RUNTIME_DEST}"
    OPTIONAL
  )
else()
  install(TARGETS yuclid_exe
    RUNTIME DESTINATION "${YUCLID_RUNTIME_DEST}"
  )
endif()
