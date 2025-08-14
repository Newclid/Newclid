/**
   Copyright 2025 Concordance Inc. dba Harmonic

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
// Define the test module name for Boost.Test
#define BOOST_TEST_MODULE slope_angle_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/array.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the headers for the classes being tested and their dependencies
#include "type/slope_angle.hpp"
#include "type/point.hpp"
#include "problem.hpp"
#include "numbers/add_circle.hpp" // For Yuclid::AddCircle

// Include standard library headers used in tests
#include <string>
#include <vector>
#include <sstream>   // For std::stringstream in ostream tests
#include <cmath>     // For std::atan2, std::fabs
#include <stdexcept> // For std::runtime_error (for exception testing)
#include <numbers>   // For std::numbers::pi_v (C++20 and later)

using namespace std;
using namespace Yuclid; // Specific namespace for our classes

/**
 * @brief A fixture to ensure the global problem instance is cleared before and after each test.
 *
 * This is crucial for testing thread-local singletons like `problem`, as it ensures
 * that each test case starts with a clean and isolated problem state.
 */
struct ProblemClearFixture {
  /**
   * @brief Constructor for the fixture.
   * Clears the thread-local problem instance before a test runs.
   */
  ProblemClearFixture() {
    problem::reset();
  }

  /**
   * @brief Destructor for the fixture.
   * Clears the thread-local problem instance after a test has completed.
   * This ensures a clean state for the next test if tests run sequentially
   * in the same thread.
   */
  ~ProblemClearFixture() {
    problem::reset();
  }
};

// Define a test suite and apply the ProblemClearFixture to it.
// All test cases within this suite will automatically use the fixture.
BOOST_FIXTURE_TEST_SUITE(slope_angle_suite, ProblemClearFixture)

/**
 * @brief Test case for constructor and endpoint access with points in order.
 */
BOOST_AUTO_TEST_CASE(constructor_ordered_points) {
  // Add points to the problem
  problem::add_point("P0", 0.0, 0.0); // point(0)
  problem::add_point("P1", 1.0, 1.0); // point(1)

  Point p0(0);
  Point p1(1);

  // This should not throw as points are not too close
  BOOST_CHECK_NO_THROW(SlopeAngle sa(p0, p1));
}

/**
 * @brief Test case for constructor and endpoint access with points out of order.
 * Verifies that the constructor correctly reorders them.
 */
BOOST_AUTO_TEST_CASE(constructor_unordered_points) {
  // Add points to the problem
  problem::add_point("C", 0.0, 0.0); // point(0)
  problem::add_point("D", 1.0, 1.0); // point(1)

  Point p0(0);
  Point p1(1);

  // This should not throw
  BOOST_CHECK_NO_THROW(SlopeAngle sa(p1, p0));
  SlopeAngle sa(p1, p0); // Create after no-throw check to use for further checks

  // m_left should still be p0, m_right should be p1 due to canonical ordering
  BOOST_CHECK_EQUAL(sa.left().get(), p0.get());
  BOOST_CHECK_EQUAL(sa.right().get(), p1.get());
}

/**
 * @brief Test case for constructor with identical points.
 * This should now throw an exception.
 */
BOOST_AUTO_TEST_CASE(constructor_identical_points_throws) {
  // Add points to the problem
  problem::add_point("E", 0.0, 0.0); // point(0)

  Point p0(0);

  // Should throw because identical points are too close
  BOOST_CHECK_THROW(SlopeAngle sa(p0, p0), runtime_error);
}

/**
 * @brief Test case for constructor with points that are numerically very close.
 * This should now throw an exception.
 */
BOOST_AUTO_TEST_CASE(constructor_close_points_throws) {
  // Add two points that are very close (within 1E-7)
  // The exact value 1E-7L is used in point::is_close
  problem::add_point("Close1", static_cast<double>(10.00000001L), static_cast<double>(20.00000002L)); // point(0)
  problem::add_point("Close2", static_cast<double>(10.00000008L), static_cast<double>(20.00000009L)); // point(1)

  Point pClose1(0);
  Point pClose2(1);

  // Both x and y differences are less than or equal to 1E-7.
  // fabs(10.00000001 - 10.00000008) = 0.00000007 <= 1E-7
  // fabs(20.00000002 - 20.00000009) = 0.00000007 <= 1E-7
  BOOST_CHECK_THROW(SlopeAngle sa(pClose1, pClose2), runtime_error);
}

/**
 * @brief Test case for constructor with points that are far enough apart.
 * This should NOT throw an exception.
 */
BOOST_AUTO_TEST_CASE(constructor_far_points_no_throw) {
  // Add two points where at least one coordinate differs significantly
  // The exact value 1E-7L is used in point::is_close
  problem::add_point("Far1", static_cast<double>(1.0L), static_cast<double>(2.0L)); // point(0)
  problem::add_point("Far2", static_cast<double>(1.0L), static_cast<double>(2.0000001L)); // point(1)

  Point pFar1(0);
  Point pFar2(1);

  // x difference is 0.0 <= 1E-7
  // y difference is 0.0000001 > 1E-7
  // So, it should NOT throw
  BOOST_CHECK_NO_THROW(SlopeAngle sa(pFar1, pFar2));
}

/**
 * @brief Test cases for implicit conversion to `AddCircle<double>` (slope angle calculation).
 * Test with various common angles using 1.0 = pi radians mapping.
 */
BOOST_DATA_TEST_CASE(
                     slope_angle_conversion_to_add_circle_double,
                     boost::unit_test::data::make({
                         make_tuple("HorizontalRight", 0.0L, 0.0L, 1.0L, 0.0L, 0.0L),         // 0 degrees (0 / pi = 0)
                         make_tuple("45Deg", 0.0L, 0.0L, 1.0L, 1.0L, 0.25L),                 // 45 degrees (pi/4 / pi = 0.25)
                         make_tuple("VerticalUp", 0.0L, 0.0L, 0.0L, 1.0L, 0.5L),             // 90 degrees (pi/2 / pi = 0.5)
                         make_tuple("135Deg", 0.0L, 0.0L, -1.0L, 1.0L, 0.75L),               // 135 degrees (3pi/4 / pi = 0.75)
                         make_tuple("HorizontalLeft", 0.0L, 0.0L, -1.0L, 0.0L, 0.0L),         // 180 degrees (pi / pi = 1.0, normalized to 0.0 by AddCircle)
                         make_tuple("225Deg", 0.0L, 0.0L, -1.0L, -1.0L, 0.25L),              // 225 degrees (-3pi/4 / pi = -0.75, normalized to 0.25 by AddCircle)
                         make_tuple("VerticalDown", 0.0L, 0.0L, 0.0L, -1.0L, 0.5L),          // 270 degrees (-pi/2 / pi = -0.5, normalized to 0.5 by AddCircle)
                         make_tuple("315Deg", 0.0L, 0.0L, 1.0L, -1.0L, 0.75L)                // 315 degrees (-pi/4 / pi = -0.25, normalized to 0.75 by AddCircle)
                       }),
                     test_name, x1, y1, x2, y2, expected_normalized_angle)
{
  // Add points to the problem for each test case
  problem::add_point(string(test_name) + "_p1", x1, y1); // point(0) relative to this test's context
  problem::add_point(string(test_name) + "_p2", x2, y2); // point(1) relative to this test's context

  Point p_start(0);
  Point p_end(1);

  SlopeAngle sa(p_start, p_end);
  AddCircle<double> result_angle = AddCircle<double>(sa); // Explicit conversion

  // Check the normalized angle value with a small tolerance
  BOOST_CHECK_CLOSE(result_angle.number(), expected_normalized_angle, 0.0001);
}


/**
 * @brief Test case for comparison operators (defaulted).
 * Comparisons are based on m_left, then m_right (lexical).
 */
BOOST_AUTO_TEST_CASE(slope_angle_comparison) {
  problem::add_point("M0", 0.0, 0.0); // point(0)
  problem::add_point("M1", 1.0, 1.0); // point(1)
  problem::add_point("M2", 2.0, 2.0); // point(2)
  problem::add_point("M3", 3.0, 3.0); // point(3)

  Point p0(0), p1(1), p2(2);

  // Ensure construction succeeds before comparison tests
  SlopeAngle sa1(p0, p1); // left: P0, right: P1
  SlopeAngle sa2(p0, p2); // left: P0, right: P2
  SlopeAngle sa3(p1, p2); // left: P1, right: P2
  SlopeAngle sa4(p1, p0); // left: P0, right: P1 (reordered)
  SlopeAngle sa5(p0, p1); // left: P0, right: P1

  // Equality
  BOOST_CHECK(sa1 == sa5);
  BOOST_CHECK(sa1 == sa4); // Should be equal due to reordering in constructor

  // Less than/Greater than (based on point ordering)
  BOOST_CHECK(sa1 < sa2); // (P0, P1) < (P0, P2) because P1 < P2
  BOOST_CHECK(sa1 < sa3); // (P0, P1) < (P1, P2) because P0 < P1

  BOOST_CHECK(sa2 > sa1);
  BOOST_CHECK(sa3 > sa1);

  // Less than or equal to / Greater than or equal to
  BOOST_CHECK(sa1 <= sa5);
  BOOST_CHECK(sa1 <= sa2);
  BOOST_CHECK(sa2 >= sa1);
}

/**
 * @brief Test case for output stream operator for `SlopeAngle`.
 */
BOOST_AUTO_TEST_CASE(slope_angle_ostream_operator) {
  problem::add_point("Start", 0.0, 0.0);
  problem::add_point("End", 1.0, 1.0);

  Point pStart(0);
  Point pEnd(1);

  SlopeAngle sa(pStart, pEnd); // This will succeed
  stringstream ss;
  ss << sa;
  BOOST_CHECK_EQUAL(ss.str(), "∠(Start-End)");
}

// End of the test suite
BOOST_AUTO_TEST_SUITE_END()
