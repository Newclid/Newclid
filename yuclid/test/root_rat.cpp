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
#define BOOST_TEST_MODULE root_rat_tests // Define the test module name
#include "typedef.hpp"
#include <sstream>
#include <boost/test/unit_test.hpp>    // Include Boost.Test header

#include "numbers/root_rat.hpp"

using namespace std;
using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(root_rat_test_suite)

// Test cases for the constructor
BOOST_AUTO_TEST_CASE(test_constructor) {
  BOOST_CHECK_EQUAL(RootRat(NNRat(8), 1), RootRat(NNRat(8)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(8), Int(3)),
                    RootRat(NNRat(2)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(16), Int(4)),
                    RootRat(NNRat(2)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(64, 81), Int(2)),
                    RootRat(NNRat(8, 9)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(256, 625), Int(4)),
                    RootRat(NNRat(4, 5)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(27, 8), Int(3)),
                    RootRat(NNRat(3, 2)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(256), Int(8)),
                    RootRat(NNRat(2)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(64), Int(6)),
                    RootRat(NNRat(2), 1));

  BOOST_CHECK_EQUAL(RootRat(NNRat(1, 16), Int(4)),
                    RootRat(NNRat(1, 2)));

  BOOST_CHECK_EQUAL(RootRat(NNRat(8), Int(-3)),
                    RootRat(NNRat(1, 2), 1));
}

BOOST_AUTO_TEST_CASE(test_print) {
  RootRat const a(NNRat(4), Int(2)); // a = 2
  RootRat const b(NNRat(9), Int(2)); // b = 3
  RootRat const d(NNRat(16), Int(2)); // d = 4

  ostringstream out;
  out << a;
  BOOST_CHECK_EQUAL(out.str(), "2/1");
}

// Test cases for arithmetic operations
BOOST_AUTO_TEST_CASE(test_arithmetic_operations) {
  RootRat const a(NNRat(4), Int(2)); // a = 2
  RootRat const b(NNRat(9), Int(2)); // b = 3
  RootRat const d(NNRat(16), Int(2)); // d = 4

  BOOST_CHECK_EQUAL(a, RootRat(NNRat(2)));
  BOOST_CHECK_EQUAL(b, RootRat(NNRat(3)));
  BOOST_CHECK_EQUAL(d, RootRat(NNRat(4)));

  // a + b (multiplication): 2 * 3 = 6
  RootRat const res_add = a + b;
  BOOST_CHECK_EQUAL(res_add, RootRat(NNRat(6)));

  // d - b (division): 4 / 3 = 4/3
  RootRat const res_sub = d - b;
  BOOST_CHECK_EQUAL(res_sub, RootRat(NNRat(4, 3)));

  // -a (reciprocal): 1 / 2 = 1/2
  RootRat const res_neg = -a;
  BOOST_CHECK_EQUAL(res_neg, RootRat(NNRat(1, 2)));

  // a * NNRat(2) (exponentiation): 2^2 = 4
  RootRat const res_mul_rat = a * Rat(2);
  BOOST_CHECK_EQUAL(res_mul_rat, RootRat(NNRat(4)));

  // NNRat(1,2) * d (exponentiation): 4^(1/2) = 2
  RootRat const res_rat_mul = Rat(1, 2) * d;
  BOOST_CHECK_EQUAL(res_rat_mul, RootRat(NNRat(2)));

  // Mixed operations: (2^(1/2)) * (4^(1/3)) = 128^(1/6)
  RootRat const r_sqrt_2(NNRat(2), Int(2));
  RootRat const r_cbrt_4(NNRat(4), Int(3));
  RootRat const mixed_add = r_sqrt_2 + r_cbrt_4;
  BOOST_CHECK_EQUAL(mixed_add, RootRat(128, 6));
}

// Test cases for compound assignments
BOOST_AUTO_TEST_CASE(test_compound_assignments) {
  RootRat x(NNRat(2)); // x = 2
  RootRat const y(NNRat(3)); // y = 3

  x += y; // x = x * y = 2 * 3 = 6
  BOOST_CHECK_EQUAL(x, RootRat(NNRat(6)));

  x -= y; // x = x / y = 6 / 3 = 2
  BOOST_CHECK_EQUAL(x, RootRat(NNRat(2)));

  x *= Rat(3); // x = x ^ 3 = 2^3 = 8
  BOOST_CHECK_EQUAL(x, RootRat(NNRat(8)));
}

BOOST_AUTO_TEST_SUITE_END()
