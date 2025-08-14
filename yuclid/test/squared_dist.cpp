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
#define BOOST_TEST_MODULE squared_dist_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the headers for the classes being tested and their dependencies
#include "type/squared_dist.hpp"
#include "type/point.hpp"
#include "problem.hpp"

// Include standard library headers used in tests
#include <string>
#include <vector>
#include <sstream>   // For std::stringstream in ostream tests
#include <cmath>     // For std::sqrt, std::fabs for floating-point comparisons

// Use the Yuclid namespace to avoid verbose prefixes
using namespace Yuclid;
// Use the std namespace for common standard library elements
using namespace std;


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
BOOST_FIXTURE_TEST_SUITE(squared_dist_suite, ProblemClearFixture)

/**
 * @brief Test case for constructor and endpoint access with points in order.
 */
BOOST_AUTO_TEST_CASE(constructor_ordered_points) {
    // Add points to the problem
    problem::add_point("P0", 0.0, 0.0); // point(0)
    problem::add_point("P1", 1.0, 1.0); // point(1)

    Point p0(0);
    Point p1(1);

    SquaredDist sd(p0, p1);

    BOOST_CHECK_EQUAL(sd.left().get(), p0.get());
    BOOST_CHECK_EQUAL(sd.right().get(), p1.get());
}

/**
 * @brief Test case for constructor and endpoint access with points out of order.
 * Verifies that the constructor correctly reorders them.
 */
BOOST_AUTO_TEST_CASE(constructor_unordered_points) {
    // Add points to the problem
    problem::add_point("P0", 0.0, 0.0); // point(0)
    problem::add_point("P1", 1.0, 1.0); // point(1)

    Point p0(0);
    Point p1(1);

    SquaredDist sd(p1, p0); // Pass in reverse order

    // m_left should still be p0, m_right should be p1 due to canonical ordering
    BOOST_CHECK_EQUAL(sd.left().get(), p0.get());
    BOOST_CHECK_EQUAL(sd.right().get(), p1.get());
}

/**
 * @brief Test case for constructor with identical points.
 */
BOOST_AUTO_TEST_CASE(constructor_identical_points) {
    // Add points to the problem
    problem::add_point("P0", 0.0, 0.0); // point(0)

    Point p0(0);

    SquaredDist sd(p0, p0);

    BOOST_CHECK_EQUAL(sd.left().get(), p0.get());
    BOOST_CHECK_EQUAL(sd.right().get(), p0.get());
}

/**
 * @brief Test case for implicit conversion to double (squared length calculation).
 * Test with simple integer coordinates.
 */
BOOST_AUTO_TEST_CASE(squared_dist_calculation_simple) {
    problem::add_point("A", static_cast<double>(0.0L), static_cast<double>(0.0L)); // point(0)
    problem::add_point("B", static_cast<double>(3.0L), static_cast<double>(4.0L)); // point(1)

    Point pA(0);
    Point pB(1);

    SquaredDist sd(pA, pB);
    double expected_squared_length = (3.0L - 0.0L) * (3.0L - 0.0L) + (4.0L - 0.0L) * (4.0L - 0.0L); // 9 + 16 = 25
    BOOST_CHECK_CLOSE(static_cast<double>(sd), expected_squared_length, 0.0001); // Use BOOST_CHECK_CLOSE for floating points
}

/**
 * @brief Test case for squared length calculation with negative coordinates.
 */
BOOST_AUTO_TEST_CASE(squared_dist_calculation_negative_coords) {
    problem::add_point("C", static_cast<double>(-1.0L), static_cast<double>(-2.0L)); // point(0)
    problem::add_point("D", static_cast<double>(2.0L), static_cast<double>(2.0L));   // point(1)

    Point pC(0);
    Point pD(1);

    SquaredDist sd(pC, pD);
    double expected_squared_length = (2.0L - (-1.0L)) * (2.0L - (-1.0L)) + (2.0L - (-2.0L)) * (2.0L - (-2.0L));
    // (3)^2 + (4)^2 = 9 + 16 = 25
    BOOST_CHECK_CLOSE(static_cast<double>(sd), expected_squared_length, 0.0001);
}

/**
 * @brief Test case for squared length calculation when points are identical (length 0).
 */
BOOST_AUTO_TEST_CASE(squared_dist_calculation_identical_points) {
    problem::add_point("E", static_cast<double>(5.0L), static_cast<double>(5.0L)); // point(0)

    Point pE(0);

    SquaredDist sd(pE, pE);
    BOOST_CHECK_CLOSE(static_cast<double>(sd), static_cast<double>(0.0L), 0.0001);
}

/**
 * @brief Test case for comparison operators (defaulted).
 * Comparisons are based on m_left, then m_right.
 */
BOOST_AUTO_TEST_CASE(squared_dist_comparison) {
    problem::add_point("P0", 0.0, 0.0); // point(0)
    problem::add_point("P1", 1.0, 1.0); // point(1)
    problem::add_point("P2", 2.0, 2.0); // point(2)
    problem::add_point("P3", 3.0, 3.0); // point(3)

    Point p0(0), p1(1), p2(2);

    SquaredDist sd1(p0, p1); // left: P0, right: P1
    SquaredDist sd2(p0, p2); // left: P0, right: P2
    SquaredDist sd3(p1, p2); // left: P1, right: P2
    SquaredDist sd4(p1, p0); // left: P0, right: P1 (reordered)
    SquaredDist sd5(p0, p1); // left: P0, right: P1

    // Equality
    BOOST_CHECK(sd1 == sd5);
    BOOST_CHECK(sd1 == sd4); // Should be equal due to reordering in constructor

    // Less than/Greater than (based on point ordering)
    BOOST_CHECK(sd1 < sd2); // (P0, P1) < (P0, P2) because P1 < P2
    BOOST_CHECK(sd1 < sd3); // (P0, P1) < (P1, P2) because P0 < P1

    BOOST_CHECK(sd2 > sd1);
    BOOST_CHECK(sd3 > sd1);

    // Less than or equal to / Greater than or equal to
    BOOST_CHECK(sd1 <= sd5);
    BOOST_CHECK(sd1 <= sd2);
    BOOST_CHECK(sd2 >= sd1);
}

// End of the test suite
BOOST_AUTO_TEST_SUITE_END()
