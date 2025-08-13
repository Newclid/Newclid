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
#define BOOST_TEST_MODULE problem_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the headers for the classes being tested
#include "problem.hpp"
#include "type/point.hpp"         // For point object usage
#include "theorem.hpp"       // To ensure inheritance works as expected

// Include standard library headers used in tests
#include <string>
#include <vector>
#include <map>
#include <stdexcept> // For std::out_of_range
#include <locale>    // For std::locale (if needed for string conversion in more complex cases)


// Use the Yuclid namespace to avoid verbose prefixes
using namespace Yuclid;
// Use the std namespace for common standard library elements, as requested for GNU style
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
        // Call the public static reset method
        problem::reset();
    }

    /**
     * @brief Destructor for the fixture.
     * Clears the thread-local problem instance after a test has completed.
     * This ensures a clean state for the next test if tests run sequentially
     * in the same thread.
     */
    ~ProblemClearFixture() {
        // Call the public static reset method
        problem::reset();
    }
};

// Define a test suite and apply the ProblemClearFixture to it.
// All test cases within this suite will automatically use the fixture.
BOOST_FIXTURE_TEST_SUITE(problem_suite, ProblemClearFixture)

/**
 * @brief Test case for the initial state of the problem instance.
 * Ensures that a newly accessed problem instance is empty.
 */
BOOST_AUTO_TEST_CASE(problem_initial_state) {
    const problem& p = problem::get_instance();
    BOOST_CHECK_EQUAL(p.num_points(), 0); // Should have 0 points
    BOOST_CHECK(p.get_name_to_point_map().empty()); // The map should be empty
}

/**
 * @brief Test case for successful addition of a point using `add_point`.
 * Verifies that the point count, name, coordinates, and map are updated correctly.
 */
BOOST_AUTO_TEST_CASE(add_point_success) {
    // Add a point and check if it returns true (indicating success)
    BOOST_CHECK(problem::add_point("Point1", static_cast<double>(10.0L), static_cast<double>(20.0L)));

    const problem& p = problem::get_instance();
    BOOST_CHECK_EQUAL(p.num_points(), 1); // Verify total points count
    
    Point pt0(0); // Create a point object for index 0

    BOOST_CHECK_EQUAL(p.get_name(pt0), "Point1"); // Verify name by point object
    BOOST_CHECK_EQUAL(p.get_x(pt0), static_cast<double>(10.0L));      // Verify x-coordinate by point object
    BOOST_CHECK_EQUAL(p.get_y(pt0), static_cast<double>(20.0L));      // Verify y-coordinate by point object

    // Verify presence and data in the name-to-point map
    BOOST_CHECK(p.get_name_to_point_map().count("Point1") == 1); // Check if name exists in map
    BOOST_CHECK_EQUAL(p.get_name_to_point_map().at("Point1").get(), 0); // Verify stored point object's index
}

/**
 * @brief Test case for `add_point` when a duplicate name is provided.
 * Ensures the state remains unchanged and the function returns false.
 */
BOOST_AUTO_TEST_CASE(add_point_duplicate_name) {
    problem::add_point("PointA", static_cast<double>(1.0L), static_cast<double>(2.0L)); // Add initial point

    // Attempt to add a point with the same name, but different coordinates
    // This should fail and return false, leaving the original point unchanged.
    BOOST_CHECK(!problem::add_point("PointA", static_cast<double>(3.0L), static_cast<double>(4.0L))); // Should return false

    const problem& p = problem::get_instance();
    BOOST_CHECK_EQUAL(p.num_points(), 1); // Still only one point
    
    Point pt0(0); // Point object for index 0

    BOOST_CHECK_EQUAL(p.get_name(pt0), "PointA"); // Name should be unchanged
    BOOST_CHECK_EQUAL(p.get_x(pt0), static_cast<double>(1.0L));      // Coordinates should be unchanged
    BOOST_CHECK_EQUAL(p.get_y(pt0), static_cast<double>(2.0L));
}

/**
 * @brief Test case for adding multiple distinct points.
 * Verifies that all points are added correctly and accessible by their respective indexes.
 */
BOOST_AUTO_TEST_CASE(add_multiple_points) {
    BOOST_CHECK(problem::add_point("Alpha", static_cast<double>(0.0L), static_cast<double>(0.0L)));
    BOOST_CHECK(problem::add_point("Beta", static_cast<double>(1.1L), static_cast<double>(2.2L)));
    BOOST_CHECK(problem::add_point("Gamma", static_cast<double>(3.3L), static_cast<double>(4.4L)));

    const problem& p = problem::get_instance();
    BOOST_CHECK_EQUAL(p.num_points(), 3); // Check total count

    // Verify data for the first point (index 0)
    Point pt0(0);
    BOOST_CHECK_EQUAL(p.get_name(pt0), "Alpha");
    BOOST_CHECK_EQUAL(p.get_x(pt0), static_cast<double>(0.0L));
    BOOST_CHECK_EQUAL(p.get_y(pt0), static_cast<double>(0.0L));

    // Verify data for the second point (index 1)
    Point pt1(1);
    BOOST_CHECK_EQUAL(p.get_name(pt1), "Beta");
    BOOST_CHECK_EQUAL(p.get_x(pt1), static_cast<double>(1.1L));
    BOOST_CHECK_EQUAL(p.get_y(pt1), static_cast<double>(2.2L));

    // Verify data for the third point (index 2)
    Point pt2(2);
    BOOST_CHECK_EQUAL(p.get_name(pt2), "Gamma");
    BOOST_CHECK_EQUAL(p.get_x(pt2), static_cast<double>(3.3L));
    BOOST_CHECK_EQUAL(p.get_y(pt2), static_cast<double>(4.4L));

    BOOST_CHECK_EQUAL(p.get_name_to_point_map().size(), 3); // Check map size
}

/**
 * @brief Test case for accessing data through the `get_name_to_point_map()` map.
 * Verifies that the map provides correct point objects (indexes) for given names,
 * and that these point objects can then be used to retrieve coordinates.
 */
BOOST_AUTO_TEST_CASE(get_name_to_point_map_access) {
    problem::add_point("KeyPoint", static_cast<double>(7.0L), static_cast<double>(8.0L));
    problem::add_point("AnotherPoint", static_cast<double>(9.0L), static_cast<double>(10.0L));

    const problem& p = problem::get_instance();
    const map<string, point>& name_to_point_map = p.get_name_to_point_map();

    // Access point objects using the map
    point key_point = name_to_point_map.at("KeyPoint");
    point another_point = name_to_point_map.at("AnotherPoint");

    // Verify indexes from the point objects
    BOOST_CHECK_EQUAL(key_point.get(), 0);
    BOOST_CHECK_EQUAL(another_point.get(), 1);

    // Use the point objects to retrieve and verify coordinates from the problem
    BOOST_CHECK_EQUAL(p.get_x(key_point), static_cast<double>(7.0L));
    BOOST_CHECK_EQUAL(p.get_y(key_point), static_cast<double>(8.0L));
    BOOST_CHECK_EQUAL(p.get_x(another_point), static_cast<double>(9.0L));
    BOOST_CHECK_EQUAL(p.get_y(another_point), static_cast<double>(10.0L));
}

/**
 * @brief Test case for the `clear()` method.
 * Ensures that `clear()` resets the problem instance to its initial empty state.
 */
BOOST_AUTO_TEST_CASE(clear_method) {
    problem::add_point("Temp1", static_cast<double>(1.0L), static_cast<double>(1.0L));
    problem::add_point("Temp2", static_cast<double>(2.0L), static_cast<double>(2.0L));

    const problem& p_const_before = problem::get_instance();
    BOOST_CHECK_EQUAL(p_const_before.num_points(), 2); // Verify points before clear

    // Call the public static reset method
    problem::reset();

    const problem& p_const_after = problem::get_instance();
    BOOST_CHECK_EQUAL(p_const_after.num_points(), 0); // Verify points after clear
    BOOST_CHECK(p_const_after.get_name_to_point_map().empty()); // Verify map is empty
}

/**
 * @brief Test case to verify inheritance from `theorem`.
 * This test primarily checks for compilation success, demonstrating the `is-a` relationship.
 */
BOOST_AUTO_TEST_CASE(inheritance_from_theorem) {
    problem p_instance; // Create an instance of problem
    theorem& t_ref = p_instance; // Assign to a polymorphic reference of theorem

    // This check is a compile-time verification that `problem` can be treated as `theorem`.
    // No specific runtime check is needed beyond successful compilation if `theorem` is a simple base.
    (void)t_ref; // Suppress unused variable warning for `t_ref`

    BOOST_CHECK(true); // If it compiles and runs, the inheritance is structurally correct.
}

/**
 * @brief Basic test to demonstrate the effect of thread-local storage within a single thread's test suite.
 *
 * Because `ProblemClearFixture` is applied to the suite, each test case effectively
 * runs with its own, cleared thread-local `problem` instance. This test simply
 * verifies that the problem is indeed empty at the start of a test, confirming
 * the fixture's behavior. Full thread-local *isolation* would require explicit
 * multi-threading tests.
 */
BOOST_AUTO_TEST_CASE(thread_local_isolation_basic) {
    // At the start of this test case, the ProblemClearFixture should have
    // already cleared the thread-local problem instance.
    const problem& p = problem::get_instance();
    BOOST_CHECK_EQUAL(p.num_points(), 0); // Problem should be empty initially for this test.

    // Add a point to verify it's added only for this thread's instance.
    problem::add_point("IsolatedPoint", static_cast<double>(100.0L), static_cast<double>(200.0L));
    BOOST_CHECK_EQUAL(p.num_points(), 1); // Now it has one point.
    // This point will be cleared by the fixture after this test completes.
}

// End of the test suite
BOOST_AUTO_TEST_SUITE_END()
