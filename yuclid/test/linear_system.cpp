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
#define BOOST_TEST_MODULE linear_system_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the classes under test and their dependencies
#include "ar/equation.hpp"
#include "ar/linear_combination.hpp"
#include "ar/linear_system.hpp"
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
BOOST_FIXTURE_TEST_SUITE(linear_system_suite, FullClearFixture)

// --- Tests for EqnIndex ---
BOOST_AUTO_TEST_CASE(eqn_index_creation_and_get) {
  EqnIndex<dist> idx(5);
  BOOST_CHECK_EQUAL(idx.get(), 5);
}

BOOST_AUTO_TEST_CASE(eqn_index_comparison) {
  EqnIndex<dist> idx1(5);
  EqnIndex<dist> idx2(10);
  EqnIndex<dist> idx3(5);

  BOOST_CHECK(idx1 < idx2);
  BOOST_CHECK(idx2 > idx1);
  BOOST_CHECK(idx1 == idx3);
  BOOST_CHECK(idx1 <= idx3);
  BOOST_CHECK(idx1 >= idx3);
  BOOST_CHECK(idx1 != idx2);
}

BOOST_AUTO_TEST_CASE(eqn_index_ostream_operator) {
  // Add an equation for the index to refer to
  dist ab(point("A"), point("B"));
  equation<dist> eq_for_idx = (LinearCombination<dist>(ab, rat(1)) == rat(5));
  // add_equation now returns bool, so we add it and then derive the index
  BOOST_CHECK(LinearSystem<dist>::add_equation(eq_for_idx));
  auto added_idx = EqnIndex<dist>(LinearSystem<dist>::get().size() - 1);

  stringstream ss;
  ss << added_idx;
  BOOST_CHECK_EQUAL(ss.str(), "Eq[0]: |A-B| = 5/1");
}


// --- Tests for LinearSystem ---

BOOST_AUTO_TEST_CASE(linear_system_initial_state) {
  const auto& sys = LinearSystem<dist>::get();
  BOOST_CHECK_EQUAL(sys.size(), 0);
}

BOOST_AUTO_TEST_CASE(linear_system_add_equation_success) {
  dist ab(point("A"), point("B"));
  dist ac(point("A"), point("C"));
  equation<dist> eq1 = (LinearCombination<dist>(ab, rat(1)) == rat(5));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::add_equation(eq1), true); // Check bool return
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1);

  equation<dist> eq2 = (LinearCombination<dist>(ab, rat(2)) + LinearCombination<dist>(ac, rat(2)) == rat(10));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::add_equation(eq2), true); // Check bool return
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 2);
}

BOOST_AUTO_TEST_CASE(linear_system_add_equation_redundant) {
  dist ab(point("A"), point("B"));
  equation<dist> eq_base = (LinearCombination<dist>(ab, rat(1)) == rat(5));
  BOOST_CHECK(LinearSystem<dist>::add_equation(eq_base));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1);

  // Add a redundant equation (e.g., 2*eq_base)
  equation<dist> eq_redundant = (LinearCombination<dist>(ab, rat(2)) == rat(10));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::add_equation(eq_redundant), false); // Should return false
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1); // Size should not increase
}

BOOST_AUTO_TEST_CASE(linear_system_add_equation_contradiction) {
  dist ab(point("A"), point("B"));
  equation<dist> eq_base = (LinearCombination<dist>(ab, rat(1)) == rat(5));
  BOOST_CHECK(LinearSystem<dist>::add_equation(eq_base));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1);

  // Add a contradictory equation (e.g., (1*ab = 6) which reduces to 0 = 1)
  equation<dist> eq_contradictory = (LinearCombination<dist>(ab, rat(1)) == rat(6));
  BOOST_CHECK_THROW(LinearSystem<dist>::add_equation(eq_contradictory), runtime_error); // Should throw
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1); // Size should not increase
}


BOOST_AUTO_TEST_CASE(linear_system_at_access) {
  dist ab(point("A"), point("B"));
  equation<dist> eq_orig = (LinearCombination<dist>(ab, rat(10)) == rat(100));
  BOOST_CHECK(LinearSystem<dist>::add_equation(eq_orig)); // Check bool return
  auto idx = EqnIndex<dist>(LinearSystem<dist>::get().size() - 1); // Get index

  const auto& retrieved_eq = LinearSystem<dist>::get().at(idx);
  BOOST_CHECK_EQUAL(retrieved_eq.lhs()[ab], rat(10));
  BOOST_CHECK_EQUAL(retrieved_eq.rhs(), rat(100));
}

BOOST_AUTO_TEST_CASE(linear_system_at_out_of_range) {
  const auto& sys = LinearSystem<dist>::get();
  BOOST_CHECK_THROW(sys.at(EqnIndex<dist>(0)), out_of_range); // Index 0 when size is 0

  BOOST_CHECK(LinearSystem<dist>::add_equation((LinearCombination<dist>(dist(point("A"), point("B")), rat(1)) == rat(1))));
  BOOST_CHECK_THROW(sys.at(EqnIndex<dist>(1)), out_of_range); // Index 1 when size is 1
}

BOOST_AUTO_TEST_CASE(linear_system_reset) {
  dist ab(point("A"), point("B"));
  BOOST_CHECK(LinearSystem<dist>::add_equation((LinearCombination<dist>(ab, rat(1)) == rat(1))));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1);

  LinearSystem<dist>::reset();
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 0);
}

BOOST_AUTO_TEST_CASE(linear_system_thread_local_separation) {
  // Add to dist system
  dist ab(point("A"), point("B"));
  BOOST_CHECK(LinearSystem<dist>::add_equation((LinearCombination<dist>(ab, rat(1)) == rat(1))));
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1);

  // Add to SinOrDist system
  SinOrDist ac(point("A"), point("C"));
  BOOST_CHECK(LinearSystem<SinOrDist>::add_equation((LinearCombination<SinOrDist>(ac, 1L) == additive<rat>(rat(1)))));
  BOOST_CHECK_EQUAL(LinearSystem<SinOrDist>::get().size(), 1);

  // Verify dist system is still 1 and SinOrDist system is still 1
  BOOST_CHECK_EQUAL(LinearSystem<dist>::get().size(), 1);
  BOOST_CHECK_EQUAL(LinearSystem<SinOrDist>::get().size(), 1);
}

// TODO: Add tests for new_found_variables generator when its logic is finalized.

BOOST_AUTO_TEST_SUITE_END()
