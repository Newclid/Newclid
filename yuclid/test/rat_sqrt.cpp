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
#define BOOST_TEST_MODULE rat_sqrt_tests
#include "typedef.hpp"
#include <optional>
#include <boost/test/unit_test.hpp> // NOLINT
#include <cmath>              // For std::fabs if any direct double comparisons are needed

#include "numbers/util.hpp"

// Use namespace std for convenience
using namespace std;
// Use Yuclid namespace for types
using namespace Yuclid;

BOOST_AUTO_TEST_SUITE(rat_sqrt_tests)

BOOST_AUTO_TEST_CASE(perfect_square_rationals) {
    // Test case 1: 4/9 should return 2/3
    NNRat const r1(4, 9);
    std::optional<NNRat> result1 = rat_sqrt(r1);
    BOOST_TEST(result1.has_value());
    BOOST_CHECK_EQUAL(result1.value(), NNRat(2, 3));

    // Test case 2: 25/1 should return 5/1
    NNRat const r2(25, 1);
    std::optional<NNRat> result2 = rat_sqrt(r2);
    BOOST_TEST(result2.has_value());
    BOOST_CHECK_EQUAL(result2.value(), NNRat(5, 1));

    // Test case 3: 1/16 should return 1/4
    NNRat const r3(1, 16);
    std::optional<NNRat> result3 = rat_sqrt(r3);
    BOOST_TEST(result3.has_value());
    BOOST_CHECK_EQUAL(result3.value(), NNRat(1, 4));

    // Test case 4: Large perfect squares
    NNRat const r4(1000000, 4000000); // 1000000/4000000 simplifies to 1/4
    std::optional<NNRat> result4 = rat_sqrt(r4);
    BOOST_TEST(result4.has_value());
    BOOST_CHECK_EQUAL(result4.value(), NNRat(1, 2)); // sqrt(1/4) = 1/2

    // Test case 5: Rational already simplified, numerator and denominator are perfect squares
    NNRat const r5(36, 49);
    std::optional<NNRat> result5 = rat_sqrt(r5);
    BOOST_TEST(result5.has_value());
    BOOST_CHECK_EQUAL(result5.value(), NNRat(6, 7));
}

BOOST_AUTO_TEST_CASE(non_perfect_square_rationals) {
    // Test case 1: 2/3 should return empty optional
    NNRat const r1(2, 3);
    std::optional<NNRat> const result1 = rat_sqrt(r1);
    BOOST_TEST(!result1.has_value());

    // Test case 2: 5/2 should return empty optional
    NNRat const r2(5, 2);
    std::optional<NNRat> const result2 = rat_sqrt(r2);
    BOOST_TEST(!result2.has_value());

    // Test case 3: 8/9 (numerator not perfect square) should return empty optional
    NNRat const r3(8, 9);
    std::optional<NNRat> const result3 = rat_sqrt(r3);
    BOOST_TEST(!result3.has_value());

    // Test case 4: 4/10 (denominator not perfect square) should return empty optional
    NNRat const r4(4, 10);
    std::optional<NNRat> const result4 = rat_sqrt(r4);
    BOOST_TEST(!result4.has_value());

    // Test case 5: 7/1 should return empty optional
    NNRat const r5(7, 1);
    std::optional<NNRat> const result5 = rat_sqrt(r5);
    BOOST_TEST(!result5.has_value());

    // Test case 6: Numerator and denominator not perfect squares (e.g. 2/5)
    NNRat const r6(2, 5);
    std::optional<NNRat> const result6 = rat_sqrt(r6);
    BOOST_TEST(!result6.has_value());
}

BOOST_AUTO_TEST_CASE(zero_rational) {
    // Test case: 0/1 should return 0/1
    NNRat const r1(0, 1);
    std::optional<NNRat> result1 = rat_sqrt(r1);
    BOOST_TEST(result1.has_value());
    BOOST_CHECK_EQUAL(result1.value(), NNRat(0, 1));
}

BOOST_AUTO_TEST_CASE(one_rational) {
    // Test case: 1/1 should return 1/1
    NNRat const r1(1, 1);
    std::optional<NNRat> result1 = rat_sqrt(r1);
    BOOST_TEST(result1.has_value());
    BOOST_CHECK_EQUAL(result1.value(), NNRat(1, 1));
}

BOOST_AUTO_TEST_SUITE_END()
