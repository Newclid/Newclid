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
#define BOOST_TEST_MODULE int_sqrt_tests
#include "typedef.hpp"
#include <boost/test/unit_test.hpp> // NOLINT
#include <optional>
#include <cmath>

// Include the header for the AddCircle type
#include "numbers/util.hpp"

// Use namespace std for convenience
using namespace std;
// Use Yuclid namespace for types
using namespace Yuclid;


BOOST_AUTO_TEST_SUITE(integer_sqrt_tests)

BOOST_AUTO_TEST_CASE(perfect_squares) {
  // Test case 1: 0
  std::optional<Nat> result0 = integer_sqrt(0);
  BOOST_TEST(result0.has_value());
  BOOST_TEST(result0.value() == 0);

  // Test case 2: 1
  std::optional<Nat> result1 = integer_sqrt(1);
  BOOST_TEST(result1.has_value());
  BOOST_TEST(result1.value() == 1);

  // Test case 3: 4
  std::optional<Nat> result4 = integer_sqrt(4);
  BOOST_TEST(result4.has_value());
  BOOST_TEST(result4.value() == 2);

  // Test case 4: 81
  std::optional<Nat> result81 = integer_sqrt(81);
  BOOST_TEST(result81.has_value());
  BOOST_TEST(result81.value() == 9);

  // Test case 5: Large perfect square (e.g., 1000 * 1000)
  std::optional<Nat> result_large = integer_sqrt(1000000L);
  BOOST_TEST(result_large.has_value());
  BOOST_TEST(result_large.value() == 1000L);

  // Test case 6: Another large perfect square
  std::optional<Nat> result_another_large =
    integer_sqrt(Nat(987654321L) * Nat(987654321L));
  BOOST_TEST(result_another_large.has_value());
  BOOST_TEST(result_another_large.value() == 987654321L);
}

BOOST_AUTO_TEST_CASE(non_perfect_squares) {
  // Test case 1: 2
  std::optional<Nat> const result2 = integer_sqrt(2);
  BOOST_TEST(!result2.has_value());

  // Test case 2: 3
  std::optional<Nat> const result3 = integer_sqrt(3);
  BOOST_TEST(!result3.has_value());

  // Test case 3: 5
  std::optional<Nat> const result5 = integer_sqrt(5);
  BOOST_TEST(!result5.has_value());

  // Test case 4: A number just below a perfect square (e.g., 99)
  std::optional<Nat> const result99 = integer_sqrt(99);
  BOOST_TEST(!result99.has_value());

  // Test case 5: A number just above a perfect square (e.g., 101)
  std::optional<Nat> const result101 = integer_sqrt(101);
  BOOST_TEST(!result101.has_value());

  // Test case 6: Large non-perfect square
  std::optional<Nat> const result_large_non_perfect =
    integer_sqrt(static_cast<Nat>(987654322L) * static_cast<Nat>(987654321L) + 1);
  BOOST_TEST(!result_large_non_perfect.has_value());
}

BOOST_AUTO_TEST_SUITE_END()
