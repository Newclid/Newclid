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
#define BOOST_TEST_MODULE util_test

// Include necessary Boost.Test headers
#include <boost/test/unit_test.hpp>
#include <boost/test/data/test_case.hpp>
#include <boost/test/data/monomorphic/collection.hpp>

// Include the utility functions header
#include "numbers/util.hpp"

// Include standard library headers for comparisons and data generation
#include <numeric>   // For std::gcd and std::abs
#include <vector>
#include <string>
#include <sstream>
#include <array>     // For std::array

// Use the Yuclid namespace
using namespace Yuclid;
// Use the std namespace for common standard library elements
using namespace std;

// Test case for gcd_abcd
BOOST_DATA_TEST_CASE(
                     gcd_abcd_property_check,
                     boost::unit_test::data::make({
                         // {x, y} pairs to test
                         make_tuple(10L, 15L),
                         make_tuple(15L, 10L),
                         make_tuple(7L, 5L),
                         make_tuple(5L, 7L),
                         make_tuple(0L, 5L),
                         make_tuple(5L, 0L),
                         make_tuple(0L, 0L), 
                         make_tuple(-10L, 15L),
                         make_tuple(10L, -15L),
                         make_tuple(-10L, -15L),
                         make_tuple(6L, 9L),
                         make_tuple(18L, 12L),
                         make_tuple(1L, 1L),
                         make_tuple(-1L, 1L),
                         make_tuple(1L, -1L),
                         make_tuple(-1L, -1L),
                         make_tuple(100L, 75L),
                         make_tuple(75L, 100L),
                         make_tuple(24L, 36L),
                         make_tuple(36L, 24L)
                       }),
                     x, y)
{
  std::array<integer, 4> result = gcd_abcd(x, y);
  integer a = result[0];
  integer b = result[1];
  integer c = result[2];
  integer d = result[3];
    
  integer expected_gcd = std::gcd(std::abs(x), std::abs(y));

  // Verify a * x + b * y = gcd(x, y)
  BOOST_TEST_CONTEXT("Testing a*x + b*y = gcd(x,y) for x=" << x << ", y=" << y) {
    BOOST_CHECK_EQUAL(a * x + b * y, expected_gcd);
  }

  // Verify c * x + d * y = 0
  BOOST_TEST_CONTEXT("Testing c*x + d*y = 0 for x=" << x << ", y=" << y) {
    BOOST_CHECK_EQUAL(c * x + d * y, 0L);
  }

  // Verify gcd(c, d) = 1
  BOOST_TEST_CONTEXT("Testing gcd(c,d) = 1 for x=" << x << ", y=" << y) {
    // For (0,0), gcd_abcd returns {0,0,0,1}. std::gcd(0,1) is 1.
    BOOST_CHECK_EQUAL(std::gcd(std::abs(c), std::abs(d)), 1L);
  }
}
