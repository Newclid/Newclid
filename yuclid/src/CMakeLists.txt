add_subdirectory(numbers)

add_library(yuclid
  STATIC
  ar/eqn_index.cpp
  ar/equation.cpp
  ar/equation_traits.cpp
  ar/linear_combination.cpp
  ar/linear_system.cpp
  ar/reduced_equation.cpp
  config_options.cpp
  matcher.cpp
  numbers/add_circle.cpp
  numbers/posreal.cpp
  numbers/root_rat.cpp
  numbers/util.cpp
  parser/simple.cpp
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
  Boost::system
  Boost::headers
)

add_executable(yuclid_exe main.cpp)
set_property(TARGET yuclid_exe PROPERTY OUTPUT_NAME yuclid)
target_link_libraries(yuclid_exe PRIVATE
  yuclid
)

if (DEFINED SKBUILD_SCRIPTS_DIR)
  install(TARGETS yuclid_exe DESTINATION "${SKBUILD_SCRIPTS_DIR}")
else()
  install(TARGETS yuclid_exe DESTINATION "${CMAKE_INSTALL_BINDIR}")
endif()
