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
#define BOOST_TEST_MODULE equation_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

#if 0

// Include the class under test and its dependencies
#include "ar/equation.hpp"
#include "ar/linear_combination.hpp"
#include "numbers/add_circle.hpp"
#include "numbers/additive.hpp"
#include "typedef.hpp"
#include "problem.hpp"
#include "type/angle.hpp"
#include "type/dist.hpp"
#include "type/sin_or_dist.hpp"
#include "type/point.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"

// Standard library includes
#include <string>
#include <vector>
#include <sstream>
#include <map>
#include <stdexcept>
#include <cmath>

using namespace std;
using namespace Yuclid;

/**
 * @brief A fixture to ensure the global problem instance is cleared before and after each test.
 */
struct ProblemClearFixture {
  ProblemClearFixture() {
    problem::reset();
    problem::add_point("A", 0.0, 0.0);
    problem::add_point("B", 1.0, 0.0);
    problem::add_point("C", 0.0, 1.0);
    problem::add_point("D", 1.0, 1.0);
    problem::add_point("E", 2.0, 0.0);
  }
  ~ProblemClearFixture() {
    problem::reset();
  }
};

// Define a test suite and apply the ProblemClearFixture to it.
BOOST_FIXTURE_TEST_SUITE(equation_suite, ProblemClearFixture)

// Helper function to get a point by name (for test setup)
point get_point(const string& name) {
  return problem::get_instance().get_name_to_point_map().at(name);
}

// --- Tests for dist (coefficient_type = rat, RHSType = rat) ---
BOOST_AUTO_TEST_CASE(eq_dist_constructor) {
  dist ab(get_point("A"), get_point("B"));
  LinearCombination<dist> lhs(ab, rat(1));
  equation<dist> eq(lhs, rat(5));
  BOOST_CHECK_EQUAL(eq.lhs()[ab], rat(1));
  BOOST_CHECK_EQUAL(eq.rhs(), rat(5));
}

BOOST_AUTO_TEST_CASE(eq_dist_definition_operator) {
  dist ab(get_point("A"), get_point("B"));
  LinearCombination<dist> lc(ab, rat(2));
  equation<dist> eq = (lc == rat(10)); // Uses the global operator==
  BOOST_CHECK_EQUAL(eq.lhs()[ab], rat(2));
  BOOST_CHECK_EQUAL(eq.rhs(), rat(10));
}

BOOST_AUTO_TEST_CASE(eq_dist_compound_addition) {
  dist ab(get_point("A"), get_point("B"));
  dist ac(get_point("A"), get_point("C"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(1)) == rat(5));
  equation<dist> eq2 = (LinearCombination<dist>(ac, rat(2)) == rat(3));
  eq1 += eq2; // (1*ab + 2*ac) = (5 + 3) = 8
  BOOST_CHECK_EQUAL(eq1.lhs()[ab], rat(1));
  BOOST_CHECK_EQUAL(eq1.lhs()[ac], rat(2));
  BOOST_CHECK_EQUAL(eq1.rhs(), rat(8));
}

BOOST_AUTO_TEST_CASE(eq_dist_compound_subtraction) {
  dist ab(get_point("A"), get_point("B"));
  dist ac(get_point("A"), get_point("C"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(5)) == rat(10));
  equation<dist> eq2 = (LinearCombination<dist>(ac, rat(2)) == rat(3));
  eq1 -= eq2; // (5*ab - 2*ac) = (10 - 3) = 7
  BOOST_CHECK_EQUAL(eq1.lhs()[ab], rat(5));
  BOOST_CHECK_EQUAL(eq1.lhs()[ac], rat(-2));
  BOOST_CHECK_EQUAL(eq1.rhs(), rat(7));
}

BOOST_AUTO_TEST_CASE(eq_dist_compound_multiplication) {
  dist ab(get_point("A"), get_point("B"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(2)) == rat(5));
  eq1 *= rat(3); // (6*ab) = 15
  BOOST_CHECK_EQUAL(eq1.lhs()[ab], rat(6));
  BOOST_CHECK_EQUAL(eq1.rhs(), rat(15));
}

BOOST_AUTO_TEST_CASE(eq_dist_unary_minus) {
  dist ab(get_point("A"), get_point("B"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(2)) == rat(5));
  equation<dist> eq_neg = -eq1; // (-2*ab) = -5
  BOOST_CHECK_EQUAL(eq_neg.lhs()[ab], rat(-2));
  BOOST_CHECK_EQUAL(eq_neg.rhs(), rat(-5));
}

BOOST_AUTO_TEST_CASE(eq_dist_binary_plus) {
  dist ab(get_point("A"), get_point("B"));
  dist ac(get_point("A"), get_point("C"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(1)) == rat(5));
  equation<dist> eq2 = (LinearCombination<dist>(ac, rat(2)) == rat(3));
  equation<dist> sum_eq = eq1 + eq2; // (1*ab + 2*ac) = 8
  BOOST_CHECK_EQUAL(sum_eq.lhs()[ab], rat(1));
  BOOST_CHECK_EQUAL(sum_eq.lhs()[ac], rat(2));
  BOOST_CHECK_EQUAL(sum_eq.rhs(), rat(8));
}

BOOST_AUTO_TEST_CASE(eq_dist_binary_minus) {
  dist ab(get_point("A"), get_point("B"));
  dist ac(get_point("A"), get_point("C"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(5)) == rat(10));
  equation<dist> eq2 = (LinearCombination<dist>(ac, rat(2)) == rat(3));
  equation<dist> diff_eq = eq1 - eq2; // (5*ab - 2*ac) = 7
  BOOST_CHECK_EQUAL(diff_eq.lhs()[ab], rat(5));
  BOOST_CHECK_EQUAL(diff_eq.lhs()[ac], rat(-2));
  BOOST_CHECK_EQUAL(diff_eq.rhs(), rat(7));
}

BOOST_AUTO_TEST_CASE(eq_dist_binary_multiply) {
  dist ab(get_point("A"), get_point("B"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(2)) == rat(5));
  equation<dist> prod_eq = eq1 * rat(3); // (6*ab) = 15
  BOOST_CHECK_EQUAL(prod_eq.lhs()[ab], rat(6));
  BOOST_CHECK_EQUAL(prod_eq.rhs(), rat(15));
  equation<dist> prod_eq_rev = rat(4) * eq1; // (8*ab) = 20
  BOOST_CHECK_EQUAL(prod_eq_rev.lhs()[ab], rat(8));
  BOOST_CHECK_EQUAL(prod_eq_rev.rhs(), rat(20));
}

BOOST_AUTO_TEST_CASE(eq_dist_ostream_operator) {
  dist ab(get_point("A"), get_point("B"));
  dist ac(get_point("A"), get_point("C"));
  LinearCombination<dist> lc(ab, rat(2));
  lc += LinearCombination<dist>(ac, rat(-3));
  equation<dist> eq = (lc == rat(5, 7));
  stringstream ss;
  ss << eq;
  BOOST_CHECK_EQUAL(ss.str(), "2/1|A-B| - 3/1|A-C| = 5/7");
}

// --- Tests for SinOrDist (coefficient_type = integer, RHSType = additive<rat>) ---
BOOST_AUTO_TEST_CASE(eq_sin_or_dist_constructor) {
  SinOrDist ab(get_point("A"), get_point("B"));
  LinearCombination<SinOrDist> lhs(ab, 1L);
  additive<rat> rhs_val = additive<rat>(rat(5));
  equation<SinOrDist> eq(lhs, rhs_val);
  BOOST_CHECK_EQUAL(eq.lhs()[ab], 1L);
  BOOST_CHECK_EQUAL(eq.rhs().number(), rat(5));
}

BOOST_AUTO_TEST_CASE(eq_sin_or_dist_definition_operator) {
  SinOrDist ab(get_point("A"), get_point("B"));
  LinearCombination<SinOrDist> lc(ab, 2L);
  equation<SinOrDist> eq = (lc == additive<rat>(rat(10))); // Uses the global operator==
  BOOST_CHECK_EQUAL(eq.lhs()[ab], 2L);
  BOOST_CHECK_EQUAL(eq.rhs().number(), rat(10));
}

BOOST_AUTO_TEST_CASE(eq_sin_or_dist_compound_addition) {
  SinOrDist ab(get_point("A"), get_point("B"));
  SinOrDist ac(get_point("A"), get_point("C"));
  equation<SinOrDist> eq1 = (LinearCombination<SinOrDist>(ab, 1L) == additive<rat>(rat(5)));
  equation<SinOrDist> eq2 = (LinearCombination<SinOrDist>(ac, 2L) == additive<rat>(rat(3)));
  eq1 += eq2; // (1*ab + 2*ac) = (5 * 3) = 15
  BOOST_CHECK_EQUAL(eq1.lhs()[ab], 1L);
  BOOST_CHECK_EQUAL(eq1.lhs()[ac], 2L);
  BOOST_CHECK_EQUAL(eq1.rhs().number(), rat(15));
}

BOOST_AUTO_TEST_CASE(eq_sin_or_dist_compound_multiplication) {
  SinOrDist ab(get_point("A"), get_point("B"));
  equation<SinOrDist> eq1 = (LinearCombination<SinOrDist>(ab, 2L) == additive<rat>(rat(5)));
  eq1 *= 3L; // (6*ab) = 125
  BOOST_CHECK_EQUAL(eq1.lhs()[ab], 6L);
  BOOST_CHECK_EQUAL(eq1.rhs().number(), rat(125));
}

BOOST_AUTO_TEST_CASE(eq_sin_or_dist_unary_minus) {
  SinOrDist ab(get_point("A"), get_point("B"));
  equation<SinOrDist> eq1 = (LinearCombination<SinOrDist>(ab, 2L) == additive<rat>(rat(5)));
  equation<SinOrDist> eq_neg = -eq1; // (-2*ab) = 1/5
  BOOST_CHECK_EQUAL(eq_neg.lhs()[ab], -2L);
  BOOST_CHECK_EQUAL(eq_neg.rhs().number(), rat(1)/5);
}

BOOST_AUTO_TEST_CASE(eq_sin_or_dist_ostream_operator) {
  SinOrDist ab(get_point("A"), get_point("B"));
  SinOrDist ac(get_point("A"), get_point("C"));
  LinearCombination<SinOrDist> lc(ab, 2L);
  lc += LinearCombination<SinOrDist>(ac, -3L);
  equation<SinOrDist> eq = (lc == additive<rat>(rat(5, 7)));
  stringstream ss;
  ss << eq;
  BOOST_CHECK_EQUAL(ss.str(), "|A-B|^2^2 / |A-C|^2^3 = 5/7");
}

// --- Tests for SlopeAngle (coefficient_type = integer, RHSType = AddCircle<rat>) ---
BOOST_AUTO_TEST_CASE(eq_slope_angle_constructor) {
  SlopeAngle ab(get_point("A"), get_point("B"));
  LinearCombination<SlopeAngle> lhs(ab, 1L);
  AddCircle<rat> rhs_val = AddCircle<rat>(rat(1, 4)); // 45 degrees
  equation<SlopeAngle> eq(lhs, rhs_val);
  BOOST_CHECK_EQUAL(eq.lhs()[ab], 1L);
  BOOST_CHECK_EQUAL(eq.rhs().number(), rat(1, 4));
}

BOOST_AUTO_TEST_CASE(eq_slope_angle_definition_operator) {
  SlopeAngle ab(get_point("A"), get_point("B"));
  LinearCombination<SlopeAngle> lc(ab, 2L);
  equation<SlopeAngle> eq = (lc == AddCircle<rat>(rat(1, 2))); // 90 degrees
  BOOST_CHECK_EQUAL(eq.lhs()[ab], 2L);
  BOOST_CHECK_EQUAL(eq.rhs().number(), rat(1, 2));
}

BOOST_AUTO_TEST_CASE(eq_slope_angle_compound_addition) {
  SlopeAngle ab(get_point("A"), get_point("B")); // angle 0
  SlopeAngle ac(get_point("A"), get_point("C")); // angle 0.5 (pi/2 / pi)
  equation<SlopeAngle> eq1 = (LinearCombination<SlopeAngle>(ab, 1L) == AddCircle<rat>(rat(0)));
  equation<SlopeAngle> eq2 = (LinearCombination<SlopeAngle>(ac, 1L) == AddCircle<rat>(rat(1, 2)));
  eq1 += eq2; // (1*ab + 1*ac) = (0 + 0.5) = 0.5
  BOOST_CHECK_EQUAL(eq1.lhs()[ab], 1L);
  BOOST_CHECK_EQUAL(eq1.lhs()[ac], 1L);
  BOOST_CHECK_EQUAL(eq1.rhs().number(), rat(1, 2));
}

BOOST_AUTO_TEST_CASE(eq_slope_angle_ostream_operator) {
  SlopeAngle ab(get_point("A"), get_point("B"));
  SlopeAngle ac(get_point("A"), get_point("C"));
  LinearCombination<SlopeAngle> lc(ab, 2L);
  lc += LinearCombination<SlopeAngle>(ac, -3L);
  equation<SlopeAngle> eq = (lc == AddCircle<rat>(rat(1, 4)));
  stringstream ss;
  ss << eq;
  BOOST_CHECK_EQUAL(ss.str(), "2∠(A-B) - 3∠(A-C) = AddCircle(1/4)");
}


BOOST_AUTO_TEST_SUITE_END()
#endif
