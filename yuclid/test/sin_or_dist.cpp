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
#define BOOST_TEST_MODULE sin_or_dist_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the headers for the classes being tested and their dependencies
#include "type/sin_or_dist.hpp"
#include "type/point.hpp"
#include "problem.hpp"
#include "numbers/additive.hpp" // For Yuclid::additive

// Include standard library headers used in tests
#include <string>
#include <vector>
#include <sstream>   // For std::stringstream in ostream tests
#include <cmath>     // For std::sqrt, std::fabs for floating-point comparisons
#include <stdexcept> // For std::runtime_error (for exception testing)

// Place using namespace std; at the top as requested for new files
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
BOOST_FIXTURE_TEST_SUITE(sin_or_dist_suite, ProblemClearFixture)

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
  BOOST_CHECK_NO_THROW(SinOrDist md(p0, p1));
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
  BOOST_CHECK_NO_THROW(SinOrDist md(p1, p0));
  SinOrDist md(p1, p0); // Create after no-throw check to use for further checks

  // m_left should still be p0, m_right should be p1 due to canonical ordering
  BOOST_CHECK_EQUAL(md.left().get(), p0.get());
  BOOST_CHECK_EQUAL(md.right().get(), p1.get());
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
  BOOST_CHECK_THROW(SinOrDist md(p0, p0), runtime_error);
}

/**
 * @brief Test case for constructor with points that are numerically very close.
 * This should now throw an exception.
 */
BOOST_AUTO_TEST_CASE(constructor_close_points_throws) {
  // Add two points that are very close (within 1E-7)
  problem::add_point("Close1", static_cast<double>(10.00000001L), static_cast<double>(20.00000002L)); // point(0)
  problem::add_point("Close2", static_cast<double>(10.00000008L), static_cast<double>(20.00000009L)); // point(1)

  Point pClose1(0);
  Point pClose2(1);

  // Both x and y differences are less than or equal to 1E-7.
  // fabs(10.00000001 - 10.00000008) = 0.00000007 <= 1E-7
  // fabs(20.00000002 - 20.00000009) = 0.00000007 <= 1E-7
  BOOST_CHECK_THROW(SinOrDist md(pClose1, pClose2), runtime_error);
}

/**
 * @brief Test case for constructor with points that are far enough apart.
 * This should NOT throw an exception.
 */
BOOST_AUTO_TEST_CASE(constructor_far_points_no_throw) {
  // Add two points where at least one coordinate differs significantly
  problem::add_point("Far1", static_cast<double>(1.0L), static_cast<double>(2.0L)); // point(0)
  problem::add_point("Far2", static_cast<double>(1.0L), static_cast<double>(2.0000001L)); // point(1)

  Point pFar1(0);
  Point pFar2(1);

  // x difference is 0.0 <= 1E-7
  // y difference is 0.0000001 > 1E-7
  // So, it should NOT throw
  BOOST_CHECK_NO_THROW(SinOrDist md(pFar1, pFar2));
}


/**
 * @brief Test case for implicit conversion to `additive<double>`.
 * Verifies that `SinOrDist` converts to `additive<double>` containing the squared distance.
 */
BOOST_AUTO_TEST_CASE(sin_or_dist_conversion_to_additive_double) {
  problem::add_point("F", static_cast<double>(0.0L), static_cast<double>(0.0L)); // point(0)
  problem::add_point("G", static_cast<double>(3.0L), static_cast<double>(4.0L)); // point(1)

  Point pF(0);
  Point pG(1);

  SinOrDist md(pF, pG); // This will succeed as points are not too close
  // Expected squared distance is (3-0)^2 + (4-0)^2 = 9 + 16 = 25
  double expected_squared_dist = 25.0L;

  additive<double> additive_val = additive<double>(md); // Explicit conversion
  BOOST_CHECK_CLOSE(additive_val.number(), expected_squared_dist, 0.0001);
}

/**
 * @brief Test case for `SinOrDist` when points are identical (squared distance 0).
 * NOTE: This test will now implicitly test the throwing constructor by NOT being able to
 * construct `SinOrDist` with identical points.
 * The previous test case `sin_or_dist_identical_points_squared_dist_zero` is replaced
 * by `constructor_identical_points_throws`.
 */
// BOOST_AUTO_TEST_CASE(sin_or_dist_identical_points_squared_dist_zero) { ... } // Removed

/**
 * @brief Test case for comparison operators (defaulted).
 * Comparisons are based on m_left, then m_right (lexical).
 */
BOOST_AUTO_TEST_CASE(sin_or_dist_comparison) {
  problem::add_point("M0", 0.0, 0.0); // point(0)
  problem::add_point("M1", 1.0, 1.0); // point(1)
  problem::add_point("M2", 2.0, 2.0); // point(2)
  problem::add_point("M3", 3.0, 3.0); // point(3)

  Point p0(0), p1(1), p2(2), p3(3);

  // Ensure construction succeeds before comparison tests
  SinOrDist md1(p0, p1); // left: P0, right: P1
  SinOrDist md2(p0, p2); // left: P0, right: P2
  SinOrDist md3(p1, p2); // left: P1, right: P2
  SinOrDist md4(p1, p0); // left: P0, right: P1 (reordered)
  SinOrDist md5(p0, p1); // left: P0, right: P1

  // Equality
  BOOST_CHECK(md1 == md5);
  BOOST_CHECK(md1 == md4); // Should be equal due to reordering in constructor

  // Less than/Greater than (based on point ordering)
  BOOST_CHECK(md1 < md2); // (P0, P1) < (P0, P2) because P1 < P2
  BOOST_CHECK(md1 < md3); // (P0, P1) < (P1, P2) because P0 < P1

  BOOST_CHECK(md2 > md1);
  BOOST_CHECK(md3 > md1);

  // Less than or equal to / Greater than or equal to
  BOOST_CHECK(md1 <= md5);
  BOOST_CHECK(md1 <= md2);
  BOOST_CHECK(md2 >= md1);
}

/**
 * @brief Test case for output stream operator for `SinOrDist`.
 */
BOOST_AUTO_TEST_CASE(sin_or_dist_ostream_operator) {
  problem::add_point("Start", 0.0, 0.0);
  problem::add_point("End", 1.0, 1.0);

  Point pStart(0);
  Point pEnd(1);

  SinOrDist md(pStart, pEnd); // This will succeed
  stringstream ss;
  ss << md;
  BOOST_CHECK_EQUAL(ss.str(), "|Start-End|^2");
}

// End of the test suite
BOOST_AUTO_TEST_SUITE_END()
