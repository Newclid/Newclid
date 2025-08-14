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
#define BOOST_TEST_MODULE LHS
#include <boost/test/unit_test.hpp>
#include "ar/lhs.hpp"

using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(Arithmetic)

BOOST_AUTO_TEST_CASE(index_access) {
  ar::lhs<int, rat> x(2, 4);
  BOOST_TEST(x[2] == 4);
  BOOST_TEST(x[1] == 0);
}

BOOST_AUTO_TEST_CASE(addition) {
  ar::lhs<int, rat> x(2, 4), y(2, -2), z(3, 3);
  BOOST_TEST((x + y)[2] == 2, "basic addition");
  BOOST_TEST((x + z)[2] == 4, "basic addition");
  BOOST_TEST((x + z)[3] == 3, "basic addition");
  BOOST_TEST((x + y + y)[2] == 0, "cancelling a term");
  BOOST_TEST((x + y + y).coeffs().size() == 0, "cancelled terms are erased");
  BOOST_TEST(!(x + z + y + y).coeffs().contains(2), "cancelled terms are erased");
}

BOOST_AUTO_TEST_SUITE_END()
