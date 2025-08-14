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
#define BOOST_TEST_MODULE angle_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the headers for the classes being tested and their dependencies
#include "type/angle.hpp"
#include "type/point.hpp"
#include "problem.hpp"
#include "type/slope_angle.hpp" // For direct SlopeAngle comparisons in tests
#include "numbers/add_circle.hpp" // For Yuclid::AddCircle

// Include standard library headers used in tests
#include <string>
#include <vector>
#include <sstream>   // For std::stringstream in ostream tests
#include <cmath>     // For std::fabs for floating-point comparisons
#include <stdexcept> // For std::runtime_error (for exception testing)

using namespace std;
using namespace Yuclid; // Specific namespace for our classes
using namespace std::string_literals;

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
BOOST_FIXTURE_TEST_SUITE(angle_suite, ProblemClearFixture)

/**
 * @brief Test case for successful angle construction with distinct points.
 */
BOOST_AUTO_TEST_CASE(angle_constructor_success) {
  problem::add_point("A", 0.0, 0.0);
  problem::add_point("B", 1.0, 0.0); // Vertex
  problem::add_point("C", 2.0, 1.0);

  Point pA(0), pB(1), pC(2);
  BOOST_CHECK_NO_THROW(angle ang(pA, pB, pC));
}

/**
 * @brief Test case for constructor throwing when vertex is too close to left point.
 */
BOOST_AUTO_TEST_CASE(angle_constructor_throws_vertex_close_to_left) {
  problem::add_point("A_close", 10.00000001L, 20.00000002L);
  problem::add_point("B_vertex", 10.00000008L, 20.00000009L); // Close to A
  problem::add_point("C_far", 30.0, 40.0);

  Point pA(0), pB(1), pC(2);
  BOOST_CHECK_THROW(angle ang(pA, pB, pC), runtime_error);
}

/**
 * @brief Test case for constructor throwing when vertex is too close to right point.
 */
BOOST_AUTO_TEST_CASE(angle_constructor_throws_vertex_close_to_right) {
  problem::add_point("A_far", 0.0, 0.0);
  problem::add_point("B_vertex", 10.00000008L, 20.00000009L); // Close to C
  problem::add_point("C_close", 10.00000001L, 20.00000002L);

  Point pA(0), pB(1), pC(2);
  BOOST_CHECK_THROW(angle ang(pA, pB, pC), runtime_error);
}

/**
 * @brief Test case for accessing the constituent points of the angle.
 */
BOOST_AUTO_TEST_CASE(angle_point_accessors) {
  problem::add_point("Left", 0.0, 0.0);
  problem::add_point("Vertex", 1.0, 1.0);
  problem::add_point("Right", 2.0, 0.0);

  Point pL(0), pV(1), pR(2);
  angle ang(pL, pV, pR);

  BOOST_CHECK_EQUAL(ang.left().get(), pL.get());
  BOOST_CHECK_EQUAL(ang.vertex().get(), pV.get());
  BOOST_CHECK_EQUAL(ang.right().get(), pR.get());
}

/**
 * @brief Test case for `left_side()` and `right_side()` methods.
 * Verifies that they return correct `SlopeAngle` objects.
 */
BOOST_AUTO_TEST_CASE(angle_side_slope_angles) {
  problem::add_point("L", 0.0, 1.0);
  problem::add_point("V", 0.0, 0.0); // Vertex
  problem::add_point("R", 1.0, 0.0);

  Point pL(0), pV(1), pR(2);
  angle ang(pL, pV, pR);

  // Left side: segment V-L (0,0) to (0,1). Vertical line pointing up. atan2(1,0) = pi/2
  SlopeAngle expected_left_side(pV, pL);
  // Right side: segment V-R (0,0) to (1,0). Horizontal line pointing right. atan2(0,1) = 0
  SlopeAngle expected_right_side(pV, pR);

  BOOST_CHECK(ang.left_side() == expected_left_side);
  BOOST_CHECK(ang.right_side() == expected_right_side);

  // Verify their normalized double values as well
  // Expected left side angle: pi/2 / pi = 0.5
  BOOST_CHECK_CLOSE(static_cast<AddCircle<double>>(ang.left_side()).number(), 0.5L, 0.0001);
  // Expected right side angle: 0 / pi = 0.0
  BOOST_CHECK_CLOSE(static_cast<AddCircle<double>>(ang.right_side()).number(), 0.0L, 0.0001);
}

/**
 * @brief Test cases for implicit conversion to `AddCircle<double>` (angle calculation).
 * Tests various angle configurations.
 */
BOOST_DATA_TEST_CASE(
                     angle_conversion_to_add_circle_double,
                     boost::unit_test::data::make({
                         // Points: (L, V, R) -> Angle LVR. Slope of VL then VR. (Angle of VR - Angle of VL)
                         // Expected result is normalized to [0,1) where 1.0 = pi radians.

                         // 1. Straight line, angle 0
                         make_tuple("Straight0Deg"s, 0.0L, 0.0L, 1.0L, 0.0L, 2.0L, 0.0L, 0.0L), // L=(0,0), V=(1,0), R=(2,0)
                         // VL slope: 0, VR slope: 0. Result: 0 - 0 = 0
                         // 2. 90 degree angle (L is above V, R is to the right of V)
                         make_tuple("90Deg"s, 0.0L, 1.0L, 0.0L, 0.0L, 1.0L, 0.0L, 0.5L),     // L=(0,1), V=(0,0), R=(1,0)
                         // VL slope: pi/2 -> 0.5. VR slope: 0. Result: 0 - 0.5 = -0.5. Normalized: 0.5
                         // 3. 180 degree angle (L left of V, R right of V)
                         make_tuple("180Deg"s, -1.0L, 0.0L, 0.0L, 0.0L, 1.0L, 0.0L, 0.0L),    // L=(-1,0), V=(0,0), R=(1,0)
                         // VL slope: pi -> 0.0. VR slope: 0. Result: 0 - 0 = 0
                         // (Note: Angle between lines - straight line is 0)
                         // 4. 45 degree angle (L horizontal, R up-right)
                         make_tuple("45Deg"s, 1.0L, 0.0L, 0.0L, 0.0L, 1.0L, 1.0L, 0.25L),    // L=(1,0), V=(0,0), R=(1,1)
                         // VL slope: pi -> 0.0. VR slope: pi/4 -> 0.25. Result: 0.25 - 0.0 = 0.25
                         // 5. Reflex angle > 180 (L top-left, V origin, R bottom-left)
                         make_tuple("ReflexAngle"s, -1.0L, 1.0L, 0.0L, 0.0L, -1.0L, -1.0L, 0.5L) // L=(-1,1), V=(0,0), R=(-1,-1)
                         // VL slope: 3pi/4 -> 0.75. VR slope: -3pi/4 -> 0.25 (normalized).
                         // Result: 0.25 - 0.75 = -0.5. Normalized: 0.5
                       }),
                     test_name, lx, ly, vx, vy, rx, ry, expected_normalized_angle)
{
  // Add points to the problem for each test case
  problem::add_point(test_name + "_L", lx, ly); // L point
  problem::add_point(test_name + "_V", vx, vy); // V point
  problem::add_point(test_name + "_R", rx, ry); // R point

  Point pL(problem::get_instance().get_name_to_point_map().at(test_name + "_L").get());
  Point pV(problem::get_instance().get_name_to_point_map().at(test_name + "_V").get());
  Point pR(problem::get_instance().get_name_to_point_map().at(test_name + "_R").get());

  angle ang(pL, pV, pR);
  AddCircle<double> result_angle = AddCircle<double>(ang); // Explicit conversion

  BOOST_CHECK_CLOSE(result_angle.number(), expected_normalized_angle, 0.0001);
}

/**
 * @brief Test case for comparison operators (defaulted).
 * Comparisons are based on m_left_pt, then m_vertex_pt, then m_right_pt.
 */
BOOST_AUTO_TEST_CASE(angle_comparison) {
  problem::add_point("A", 0.0, 0.0);
  problem::add_point("B", 1.0, 0.0);
  problem::add_point("C", 2.0, 0.0);
  problem::add_point("D", 0.0, 1.0); // For creating different angles

  Point pA(0), pB(1), pC(2), pD(3);

  // Angles: ∠(A-B-C), ∠(A-B-D), ∠(D-B-C), ∠(A-B-C_copy)
  angle ang1(pA, pB, pC); // ∠(A-B-C)
  angle ang2(pA, pB, pD); // ∠(A-B-D) - different right point
  angle ang3(pD, pB, pC); // ∠(D-B-C) - different left point
  angle ang4(pA, pB, pC); // Copy of ang1

  BOOST_CHECK(ang1 == ang4); // Equality
  BOOST_CHECK(ang1 < ang2);  // (A,B,C) < (A,B,D) because C.get() < D.get() (0 < 3) (or their canonical point order)
  BOOST_CHECK(ang1 < ang3);  // (A,B,C) < (D,B,C) because A.get() < D.get() (0 < 3)

  BOOST_CHECK(ang2 > ang1);
  BOOST_CHECK(ang3 > ang1);
  BOOST_CHECK(ang1 <= ang4);
  BOOST_CHECK(ang2 >= ang1);
}

/**
 * @brief Test case for output stream operator for `angle`.
 */
BOOST_AUTO_TEST_CASE(angle_ostream_operator) {
  problem::add_point("PtA", 0.0, 0.0);
  problem::add_point("PtB", 1.0, 0.0);
  problem::add_point("PtC", 2.0, 1.0);

  Point pA(0), pB(1), pC(2);
  angle ang(pA, pB, pC);
  stringstream ss;
  ss << ang;
  BOOST_CHECK_EQUAL(ss.str(), "∠(PtA-PtB-PtC)");
}

// End of the test suite
BOOST_AUTO_TEST_SUITE_END()
