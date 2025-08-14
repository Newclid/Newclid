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
#define BOOST_TEST_MODULE dist_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the headers for the classes being tested and their dependencies
#include "type/dist.hpp"
#include "type/squared_dist.hpp" // For explicit cast testing
#include "type/point.hpp"
#include "problem.hpp"

// Include standard library headers used in tests
#include <string>
#include <vector>
#include <sstream>   // For std::stringstream in ostream tests
#include <cmath>     // For std::sqrt, std::fabs for floating-point comparisons

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
BOOST_FIXTURE_TEST_SUITE(dist_suite, ProblemClearFixture)

/**
 * @brief Test case for constructor and endpoint access with points in order.
 */
BOOST_AUTO_TEST_CASE(constructor_ordered_points) {
    // Add points to the problem
    problem::add_point("A", 0.0, 0.0); // point(0)
    problem::add_point("B", 1.0, 1.0); // point(1)

    Point p0(0);
    Point p1(1);

    Dist d(p0, p1);

    BOOST_CHECK_EQUAL(d.left().get(), p0.get());
    BOOST_CHECK_EQUAL(d.right().get(), p1.get());
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

    Dist d(p1, p0); // Pass in reverse order

    // m_left should still be p0, m_right should be p1 due to canonical ordering
    BOOST_CHECK_EQUAL(d.left().get(), p0.get());
    BOOST_CHECK_EQUAL(d.right().get(), p1.get());
}

/**
 * @brief Test case for constructor with identical points.
 */
BOOST_AUTO_TEST_CASE(constructor_identical_points) {
    // Add points to the problem
    problem::add_point("E", 0.0, 0.0); // point(0)

    Point p0(0);

    Dist d(p0, p0);

    BOOST_CHECK_EQUAL(d.left().get(), p0.get());
    BOOST_CHECK_EQUAL(d.right().get(), p0.get());
}

/**
 * @brief Test case for implicit conversion to double (distance calculation).
 * Test with simple integer coordinates resulting in an exact square root.
 */
BOOST_AUTO_TEST_CASE(dist_calculation_simple) {
    problem::add_point("F", static_cast<double>(0.0L), static_cast<double>(0.0L)); // point(0)
    problem::add_point("G", static_cast<double>(3.0L), static_cast<double>(4.0L)); // point(1)

    Point pF(0);
    Point pG(1);

    Dist d(pF, pG);
    double expected_dist = 5.0L; // sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5
    BOOST_CHECK_CLOSE(static_cast<double>(d), expected_dist, 0.0001); // Use BOOST_CHECK_CLOSE for floating points
}

/**
 * @brief Test case for distance calculation with negative coordinates.
 */
BOOST_AUTO_TEST_CASE(dist_calculation_negative_coords) {
    problem::add_point("H", static_cast<double>(-1.0L), static_cast<double>(-2.0L)); // point(0)
    problem::add_point("I", static_cast<double>(2.0L), static_cast<double>(2.0L));   // point(1)

    Point pH(0);
    Point pI(1);

    Dist d(pH, pI);
    double expected_dist = 5.0L; // sqrt((2 - (-1))^2 + (2 - (-2))^2) = sqrt(3^2 + 4^2) = 5
    BOOST_CHECK_CLOSE(static_cast<double>(d), expected_dist, 0.0001);
}

/**
 * @brief Test case for distance calculation when points are identical (distance 0).
 */
BOOST_AUTO_TEST_CASE(dist_calculation_identical_points) {
    problem::add_point("J", static_cast<double>(5.0L), static_cast<double>(5.0L)); // point(0)

    Point pJ(0);

    Dist d(pJ, pJ);
    BOOST_CHECK_CLOSE(static_cast<double>(d), static_cast<double>(0.0L), 0.0001);
}

/**
 * @brief Test case for explicit conversion to `SquaredDist`.
 */
BOOST_AUTO_TEST_CASE(explicit_cast_to_squared_dist) {
    problem::add_point("K", static_cast<double>(0.0L), static_cast<double>(0.0L));
    problem::add_point("L", static_cast<double>(3.0L), static_cast<double>(4.0L));

    Point pK(0);
    Point pL(1);

    Dist d(pK, pL); // Distance is 5.0
    SquaredDist sd = static_cast<SquaredDist>(d); // Explicit cast

    BOOST_CHECK_EQUAL(sd.left().get(), pK.get());
    BOOST_CHECK_EQUAL(sd.right().get(), pL.get());
    // Expected squared distance is 5.0^2 = 25.0
    BOOST_CHECK_CLOSE(static_cast<double>(sd), static_cast<double>(25.0L), 0.0001);
}

/**
 * @brief Test case for comparison operators (defaulted).
 * Comparisons are based on m_left, then m_right.
 */
BOOST_AUTO_TEST_CASE(dist_comparison) {
    problem::add_point("M0", 0.0, 0.0); // point(0)
    problem::add_point("M1", 1.0, 1.0); // point(1)
    problem::add_point("M2", 2.0, 2.0); // point(2)
    problem::add_point("M3", 3.0, 3.0); // point(3)

    Point p0(0), p1(1), p2(2);

    Dist d1(p0, p1); // left: P0, right: P1
    Dist d2(p0, p2); // left: P0, right: P2
    Dist d3(p1, p2); // left: P1, right: P2
    Dist d4(p1, p0); // left: P0, right: P1 (reordered)
    Dist d5(p0, p1); // left: P0, right: P1

    // Equality
    BOOST_CHECK(d1 == d5);
    BOOST_CHECK(d1 == d4); // Should be equal due to reordering in constructor

    // Less than/Greater than (based on point ordering)
    BOOST_CHECK(d1 < d2); // (P0, P1) < (P0, P2) because P1 < P2
    BOOST_CHECK(d1 < d3); // (P0, P1) < (P1, P2) because P0 < P1

    BOOST_CHECK(d2 > d1);
    BOOST_CHECK(d3 > d1);

    // Less than or equal to / Greater than or equal to
    BOOST_CHECK(d1 <= d5);
    BOOST_CHECK(d1 <= d2);
    BOOST_CHECK(d2 >= d1);
}

/**
 * @brief Test case for output stream operator for `dist`.
 */
BOOST_AUTO_TEST_CASE(dist_ostream_operator) {
    problem::add_point("Start", 0.0, 0.0);
    problem::add_point("End", 1.0, 1.0);

    Point pStart(0);
    Point pEnd(1);

    Dist d(pStart, pEnd);
    stringstream ss;
    ss << d;
    BOOST_CHECK_EQUAL(ss.str(), "|Start-End|");
}

// End of the test suite
BOOST_AUTO_TEST_SUITE_END()
