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
#define BOOST_TEST_MODULE reduced_equation_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the class under test and its dependencies
#include "ar/equation.hpp"
#include "ar/linear_combination.hpp"
#include "ar/reduced_equation.hpp"
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
#include <set> // For checking found variables
#include <stdexcept>
#include <cmath>

using namespace std;
using namespace Yuclid;

/**
 * @brief A fixture to ensure the global problem instance is cleared before and after each test.
 * Also clears the LinearSystem instances for all variable types.
 */
struct FullClearFixture {
  FullClearFixture() {
    problem::reset();
    // Reset all LinearSystem instances as well
    LinearSystem<dist>::reset();
    LinearSystem<SquaredDist>::reset();
    LinearSystem<SinOrDist>::reset();
    LinearSystem<SlopeAngle>::reset();

    // Add some common points for testing various variable types
    problem::add_point("A", 0.0, 0.0);
    problem::add_point("B", 1.0, 0.0);
    problem::add_point("C", 0.0, 1.0);
    problem::add_point("D", 1.0, 1.0);
    problem::add_point("E", 2.0, 0.0);
    problem::add_point("X", 10.0, 10.0); // For SinOrDist/SlopeAngle/angle tests
    problem::add_point("Y", 11.0, 11.0); // For SinOrDist/SlopeAngle/angle tests
    problem::add_point("Z", 12.0, 10.0); // For angle tests
    problem::add_point("W", 10.0, 9.0); // For angle tests
  }
  ~FullClearFixture() {
    problem::reset();
    // Reset all LinearSystem instances again after tests
    LinearSystem<dist>::reset();
    LinearSystem<SquaredDist>::reset();
    LinearSystem<SinOrDist>::reset();
    LinearSystem<SlopeAngle>::reset();
  }
};

// Define a test suite and apply the FullClearFixture to it.
BOOST_FIXTURE_TEST_SUITE(reduced_equation_suite, FullClearFixture)

// Helper to check if an equation represents 0 = 0
template <typename VariableT>
bool is_zero_equation(const equation<VariableT>& eq) {
  typename equation<VariableT>::RHSType zero_rhs_val;
  return eq.lhs().empty() && eq.rhs() == zero_rhs_val;
}

// --- Common Setup for Reduction Tests ---
// Helper to set up a simple linear system in echelon form
  template <typename VariableT>
  void setup_simple_linear_system(
                                  const VariableT& v1, const typename LinearSystem<VariableT>::RHSType& rhs1,
                                  const VariableT& v2, const typename LinearSystem<VariableT>::RHSType& rhs2)
  {
    LinearSystem<VariableT>::reset(); // Ensure a clean system

    // Add equation for v1: v1 = rhs1 (or 1*v1 = rhs1)
    LinearCombination<VariableT> lc1_lhs(v1, static_cast<typename LinearSystem<VariableT>::coefficient_type>(1));
    equation<VariableT> eq1 = (lc1_lhs == rhs1);
    BOOST_CHECK(LinearSystem<VariableT>::add_equation(eq1));

    // Add equation for v2: v2 = rhs2 (or 1*v2 = rhs2)
    LinearCombination<VariableT> lc2_lhs(v2, static_cast<typename LinearSystem<VariableT>::coefficient_type>(1));
    equation<VariableT> eq2 = (lc2_lhs == rhs2);
    BOOST_CHECK(LinearSystem<VariableT>::add_equation(eq2));
  }

// --- Test Cases for ReducedEquation constructor and accessors ---
BOOST_AUTO_TEST_CASE(reduced_equation_constructor_dist) {
  Dist ab(point("A"), point("B"));
  equation<Dist> original_eq = (LinearCombination<Dist>(ab, rat(2)) == rat(10));
  ReducedEquation<Dist> re(original_eq);

  BOOST_CHECK_EQUAL(re.original_equation().lhs()[ab], rat(2));
  BOOST_CHECK_EQUAL(re.original_equation().rhs(), rat(10));
  BOOST_CHECK_EQUAL(re.coefficient(), rat(1));
  BOOST_CHECK(is_zero_equation(re.linear_combination_of_indices())); // Should be 0=0
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ab], rat(2)); // Remainder is initially original
  BOOST_CHECK_EQUAL(re.remainder().rhs(), rat(10));
}

BOOST_AUTO_TEST_CASE(reduced_equation_constructor_sin_or_dist) {
  SinOrDist xy(point("X"), point("Y"));
  equation<SinOrDist> original_eq = (LinearCombination<SinOrDist>(xy, 5L) == additive<Rat>(rat(25)));
  ReducedEquation<SinOrDist> re(original_eq);

  BOOST_CHECK_EQUAL(re.original_equation().lhs()[xy], 5L);
  BOOST_CHECK_EQUAL(re.original_equation().rhs().number(), rat(25));
  BOOST_CHECK_EQUAL(re.coefficient(), 1L);
  BOOST_CHECK(is_zero_equation(re.linear_combination_of_indices()));
  BOOST_CHECK_EQUAL(re.remainder().lhs()[xy], 5L);
  BOOST_CHECK_EQUAL(re.remainder().rhs().number(), rat(25));
}

// --- Test Cases for reduced_equation::reduce() for dist (rat coefficients) ---
BOOST_AUTO_TEST_CASE(reduced_equation_reduce_dist_basic) {
  Dist ab(point("A"), point("B"));
  Dist ac(point("A"), point("C"));
  Dist ad(point("A"), point("D"));

  // Set up system: 1*ac = rat(10), 1*ad = rat(20)
  // IMPORTANT: The reduce() method only removes the *leading* term if a pivot is found.
  // It does NOT perform full Gaussian elimination on all terms.
  // So, if 'ab' is the leading term of the remainder and no pivot exists for 'ab',
  // the reduction stops there, even if 'ac' or 'ad' terms exist and have pivots.
  setup_simple_linear_system(ac, rat(10), ad, rat(20));

  // Equation to reduce: 2*ab + 3*ac - 1*ad = 50
  // Assuming lexicographical order for linear_combination: ab, ac, ad
  equation<Dist> original_eq = (LinearCombination<Dist>(ab, rat(2))
                                + LinearCombination<Dist>(ac, rat(3))
                                + LinearCombination<Dist>(ad, rat(-1)) == rat(50));
  ReducedEquation<Dist> re(original_eq);

  // Original remainder is 2*ab + 3*ac - 1*ad = 50
  // 'ab' is the leading term. No pivot for 'ab' in the system (only for 'ac' and 'ad').
  // So, reduce() should stop immediately without modifying anything.

  re.reduce();

  // Remainder should be unchanged
  BOOST_CHECK_EQUAL(re.remainder().lhs().terms().size(), 3);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ab], rat(2));
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ac], rat(3));
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ad], rat(-1));
  BOOST_CHECK_EQUAL(re.remainder().rhs(), rat(50));

  // linear_combination_of_indices should remain empty (0=0)
  BOOST_CHECK(re.linear_combination_of_indices().lhs().empty());
  BOOST_CHECK(is_zero_equation(re.linear_combination_of_indices()));
  BOOST_CHECK_EQUAL(re.coefficient(), rat(1)); // Coefficient should remain 1 for rational systems
}

BOOST_AUTO_TEST_CASE(reduced_equation_reduce_dist_pivot_found_only_first_term) {
  Dist ab(point("A"), point("B"));
  Dist ac(point("A"), point("C"));
  Dist ad(point("A"), point("D"));

  // Set up system: 1*ab = rat(10), 1*ad = rat(20)
  setup_simple_linear_system(ab, rat(10), ad, rat(20)); // Now 'ab' is a pivot

  // Equation to reduce: 2*ab + 3*ac - 1*ad = 50
  equation<Dist> original_eq = (LinearCombination<Dist>(ab, rat(2))
                                + LinearCombination<Dist>(ac, rat(3))
                                + LinearCombination<Dist>(ad, rat(-1)) == rat(50));
  ReducedEquation<Dist> re(original_eq);

  // Original remainder: 2*ab + 3*ac - 1*ad = 50
  // 'ab' is leading term. Pivot for 'ab' found (Eq[0]: ab = 10).
  // Reduce: R_new = R_old - (2/1)*Eq[0].rhs = (2*ab + 3*ac - 1*ad = 50) - 2*(ab = 10)
  // R_new LHS: (2*ab + 3*ac - 1*ad) - 2*(ab) = 3*ac - 1*ad
  // R_new RHS: 50 - 2*10 = 30
  // Remainder after first step: 3*ac - 1*ad = 30
  // 'ac' is now leading term. No pivot for 'ac' in the system (only for 'ab' and 'ad').
  // So reduction stops here.

  re.reduce();

  // Remainder after reduction
  BOOST_CHECK_EQUAL(re.remainder().lhs().terms().size(), 2);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ac], rat(3));
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ad], rat(-1));
  BOOST_CHECK_EQUAL(re.remainder().rhs(), rat(30));

  // linear_combination_of_indices should be (2*Eq[0])
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().lhs().terms().size(), 1);
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().lhs()[EqnIndex<dist>(0)], rat(2));
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().rhs().rhs(), rat(20)); // LC RHS: 2 * (RHS of Eq[0]) = 2*10 = 20
  BOOST_CHECK_EQUAL(re.coefficient(), rat(1));
}


// Test for additive int systems (integer coefficients)
BOOST_AUTO_TEST_CASE(reduced_equation_reduce_additive_int_basic) {
  SlopeAngle ab(point("A"), point("B")); // 0.0
  SlopeAngle ac(point("A"), point("C")); // 0.5
  SlopeAngle ad(point("A"), point("D")); // 0.25

  // Set up system: 1*ac = 0.5, 1*ad = 0.25
  setup_simple_linear_system(ac, AddCircle<Rat>(Rat(1,2)), ad, AddCircle<rat>(rat(1,4)));

  // Equation to reduce: 2*ab + 3*ac - 1*ad = 0.6
  // 'ab' is leading term. No pivot for 'ab' in the system (only for 'ac' and 'ad').
  // So, reduce() should stop immediately without modifying anything.
  equation<SlopeAngle> original_eq = (LinearCombination<SlopeAngle>(ab, 2L)
                                       + LinearCombination<SlopeAngle>(ac, 3L)
                                       + LinearCombination<SlopeAngle>(ad, -1L) == AddCircle<Rat>(rat(6,10))); // 0.6
  ReducedEquation<SlopeAngle> re(original_eq);

  re.reduce();

  // Remainder should be unchanged
  BOOST_CHECK_EQUAL(re.remainder().lhs().terms().size(), 3);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ab], 2L);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ac], 3L);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ad], -1L);
  BOOST_CHECK_EQUAL(re.remainder().rhs().number(), rat(6,10));
    
  // LC indices should be empty (0=0)
  BOOST_CHECK(is_zero_equation(re.linear_combination_of_indices()));
  BOOST_CHECK_EQUAL(re.coefficient(), 1L);
}

BOOST_AUTO_TEST_CASE(reduced_equation_reduce_additive_int_pivot_found_only_first_term) {
  SlopeAngle ab(point("A"), point("B")); // 0.0
  SlopeAngle ac(point("A"), point("C")); // 0.5
  SlopeAngle ad(point("A"), point("D")); // 0.25

  // Set up system: 1*ab = 0.0, 1*ad = 0.25
  setup_simple_linear_system(ab, AddCircle<Rat>(rat(0,1)), ad, AddCircle<Rat>(rat(1,4))); // 'ab' is now a pivot

  // Equation to reduce: 2*ab + 3*ac - 1*ad = 0.6
  equation<SlopeAngle> original_eq = (LinearCombination<SlopeAngle>(ab, 2L)
                                       + LinearCombination<SlopeAngle>(ac, 3L)
                                       + LinearCombination<SlopeAngle>(ad, -1L) == AddCircle<Rat>(rat(6,10))); // 0.6
  ReducedEquation<SlopeAngle> re(original_eq);

  // Reduce: (2*ab + 3*ac - 1*ad) = 0.6
  // 'ab' is leading. Pivot found (Eq[0]: ab = 0.0).
  // R_new = R_old - (2/1)*Eq[0].rhs = (2*ab + 3*ac - 1*ad = 0.6) - 2*(ab=0.0)
  // R_new LHS: 3*ac - 1*ad
  // R_new RHS: 0.6 - 2*0.0 = 0.6
  // Remainder after first step: 3*ac - 1*ad = 0.6
  // 'ac' is now leading term. No pivot for 'ac' in the system (only for 'ab' and 'ad').
  // So reduction stops here.

  re.reduce();

  // Remainder after reduction
  BOOST_CHECK_EQUAL(re.remainder().lhs().terms().size(), 2);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ac], 3L);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ad], -1L);
  BOOST_CHECK_EQUAL(re.remainder().rhs().number(), rat(6,10));
    
  // LC indices should be (2*Eq[0])
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().lhs().terms().size(), 1);
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().lhs()[EqnIndex<SlopeAngle>(0)], 2L);
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().rhs().rhs().number(), rat(0,1)); // 2 * (RHS of Eq[0]) = 2*0 = 0
  BOOST_CHECK_EQUAL(re.coefficient(), 1L);
}


// Test for multiplicative int systems (SinOrDist coefficients)
BOOST_AUTO_TEST_CASE(reduced_equation_reduce_sin_or_dist_basic) {
  SinOrDist ab(point("A"), point("B")); // val=1.0
  SinOrDist ac(point("A"), point("C")); // val=1.0
  SinOrDist ad(point("A"), point("D")); // val=sqrt(2)^2=2.0

  // Set up system: 1*ac = additive<rat>(1.0), 1*ad = additive<rat>(2.0)
  // Equation to reduce: ab^2 * ac^3 / ad^1 = additive<rat>(50)
  // 'ab' is leading term. No pivot for 'ab' in the system (only for 'ac' and 'ad').
  // So, reduce() should stop immediately without modifying anything.
  setup_simple_linear_system(ac, additive<Rat>(rat(1)), ad, additive<Rat>(rat(2)));

  // Equation to reduce: 2*ab + 3*ac - 1*ad = additive<rat>(50)
  equation<SinOrDist> original_eq = (LinearCombination<SinOrDist>(ab, 2L)
                                    + LinearCombination<SinOrDist>(ac, 3L)
                                    + LinearCombination<SinOrDist>(ad, -1L) == additive<Rat>(rat(50)));
  ReducedEquation<SinOrDist> re(original_eq);

  re.reduce();

  // Remainder should be unchanged
  BOOST_CHECK_EQUAL(re.remainder().lhs().terms().size(), 3);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ab], 2L);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ac], 3L);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ad], -1L);
  BOOST_CHECK_EQUAL(re.remainder().rhs().number(), rat(50));

  // LC indices should be empty (0=0)
  BOOST_CHECK(is_zero_equation(re.linear_combination_of_indices()));
  BOOST_CHECK_EQUAL(re.coefficient(), 1L);
}

BOOST_AUTO_TEST_CASE(reduced_equation_reduce_sin_or_dist_pivot_found_only_first_term) {
  SinOrDist ab(point("A"), point("B")); // val=1.0
  SinOrDist ac(point("A"), point("C")); // val=1.0
  SinOrDist ad(point("A"), point("D")); // val=sqrt(2)^2=2.0

  // Set up system: 1*ab = additive<rat>(1.0), 1*ad = additive<rat>(2.0)
  setup_simple_linear_system(ab, additive<Rat>(rat(1)), ad, additive<Rat>(rat(2))); // 'ab' is now a pivot

  // Equation to reduce: ab^2 * ac^3 / ad^1 = additive<rat>(50)
  // Represented as 2*ab + 3*ac - 1*ad = additive<rat>(50) in LC
  equation<SinOrDist> original_eq = (LinearCombination<SinOrDist>(ab, 2L)
                                    + LinearCombination<SinOrDist>(ac, 3L)
                                    + LinearCombination<SinOrDist>(ad, -1L) == additive<Rat>(rat(50)));
  ReducedEquation<SinOrDist> re(original_eq);

  // Reduce: ab^2 * ac^3 / ad^1 = 50
  // 'ab' is leading. Pivot found (Eq[0]: ab = 1.0).
  // R_new = (pivot_coeff/D)*R_old - (rem_coeff/D)*P_RHS
  // Here: pivot_coeff = 1 (for Eq[0]), rem_coeff = 2 (for ab in remainder)
  // d_gcd(1,2) = 1.
  // So R_new = (1/1)*R_old - (2/1)*Eq[0].rhs
  // R_new LHS: (2*ab + 3*ac - 1*ad) - 2*ab = 3*ac - 1*ad
  // R_new RHS: 50 - 2*1.0 = 48
  // Remainder after first step: 3*ac - 1*ad = 48
  // 'ac' is now leading term. No pivot for 'ac' in the system (only for 'ab' and 'ad').
  // So reduction stops here.

  re.reduce();

  // Remainder after reduction
  BOOST_CHECK_EQUAL(re.remainder().lhs().terms().size(), 2);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ac], 3L);
  BOOST_CHECK_EQUAL(re.remainder().lhs()[ad], -1L);
  BOOST_CHECK_EQUAL(re.remainder().rhs().number(), rat(50)); // 50 / 1 ^ 2 = 50 TODO write a better test

  // LC indices: (2*Eq[0])
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().lhs().terms().size(), 1);
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().lhs()[EqnIndex<SinOrDist>(0)], 2L);
  BOOST_CHECK_EQUAL(re.linear_combination_of_indices().rhs().rhs().number(), rat(1)); // (RHS of Eq[0]) ^ 2 = 1
  BOOST_CHECK_EQUAL(re.coefficient(), 1L); // Coefficient remains 1
}

// --- Tests for angle_equation_to_slope_angle_equation ---
BOOST_AUTO_TEST_CASE(angle_equation_to_slope_angle_equation_basic) {
  Point pA("A"), pB("B"), pC("C");

  // Angle ABC (A-B-C)
  // Slope of BA: atan2(0-0, 0-1) = atan2(0,-1) = pi. Normalised to 0.0
  // Slope of BC: atan2(1-0, 0-1) = atan2(1,-1) = 3pi/4. Normalised to 0.75
  // Angle ABC = Slope(BC) - Slope(BA) = 0.75 - 0.0 = 0.75
  angle abc_var(pA, pB, pC);

  // Equation: 1*∠(A-B-C) = 0.75 (AddCircle<rat>(3,4))
  equation<angle> eq_angle = (LinearCombination<angle>(abc_var, 1L) == AddCircle<rat>(rat(3,4)));

  // Perform conversion
  equation<SlopeAngle> converted_eq = angle_equation_to_slope_angle_equation(eq_angle);

  // Expected LHS: 1*slope(BC) - 1*slope(BA)
  // slope(BC) is SlopeAngle(B,C)
  // slope(BA) is SlopeAngle(B,A)
  SlopeAngle bc_sa(pB, pC);
  SlopeAngle ba_sa(pB, pA);

  // Check LHS terms
  BOOST_CHECK_EQUAL(converted_eq.lhs().terms().size(), 2);
  BOOST_CHECK_EQUAL(converted_eq.lhs()[bc_sa], 1L);
  BOOST_CHECK_EQUAL(converted_eq.lhs()[ba_sa], -1L);

  // Check RHS
  BOOST_CHECK_EQUAL(converted_eq.rhs().number(), rat(3,4));

  // Evaluate the converted equation (should be 0.75 - 0.0 = 0.75)
  BOOST_CHECK_CLOSE(converted_eq.lhs().evaluate().number(), static_cast<double>(3) / 4, 0.0001);
  BOOST_CHECK_EQUAL(converted_eq.rhs().number(), rat(3,4));
}

BOOST_AUTO_TEST_CASE(angle_equation_to_slope_angle_equation_multiple_terms) {
  Point pA("A"), pB("B"), pC("C"), pD("D");

  // Angle ABC: A(0,0)-B(1,0)-C(0,1) = 0.75 (as above)
  // Angle ABD: A(0,0)-B(1,0)-D(1,1)
  // Slope of BA: 0.0
  // Slope of BD: atan2(1-0, 1-1) = atan2(1,0) = pi/2. Normalised to 0.5
  // Angle ABD = Slope(BD) - Slope(BA) = 0.5 - 0.0 = 0.5
  angle abc_var(pA, pB, pC);
  angle abd_var(pA, pB, pD);

  // Equation: 2*∠(A-B-C) - 3*∠(A-B-D) = RHS_combined
  // RHS_combined = 2*(0.75) - 3*(0.5) = 1.5 - 1.5 = 0.0
  equation<angle> eq_angle = (LinearCombination<angle>(abc_var, 2L)
                              + LinearCombination<angle>(abd_var, -3L) == AddCircle<rat>(rat(0)));

  equation<SlopeAngle> converted_eq = angle_equation_to_slope_angle_equation(eq_angle);

  SlopeAngle bc_sa(pB, pC);
  SlopeAngle ba_sa(pB, pA);
  SlopeAngle bd_sa(pB, pD);

  // Expected LHS: 2*slope(BC) - 2*slope(BA) - 3*slope(BD) + 3*slope(BA)
  // Simplified: 2*slope(BC) + 1*slope(BA) - 3*slope(BD)
  BOOST_CHECK_EQUAL(converted_eq.lhs().terms().size(), 3);
  BOOST_CHECK_EQUAL(converted_eq.lhs()[bc_sa], 2L);
  BOOST_CHECK_EQUAL(converted_eq.lhs()[ba_sa], 1L); // -2 + 3 = 1
  BOOST_CHECK_EQUAL(converted_eq.lhs()[bd_sa], -3L);

  // Check RHS
  BOOST_CHECK_EQUAL(converted_eq.rhs().number(), rat(0));

  // Evaluate the converted equation (should be 0.0)
  BOOST_CHECK_CLOSE(converted_eq.lhs().evaluate().number(), 0, 0.0001);
}

BOOST_AUTO_TEST_SUITE_END()
