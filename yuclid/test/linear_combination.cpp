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
// linear_combination_test.cpp
// Unit tests for the linear_combination template class using Boost.Test.

#define BOOST_TEST_MODULE linear_combination_test
#include <boost/test/unit_test.hpp>
#include "numbers/rational.hpp"
#include <boost/safe_numerics/safe_integer.hpp> // For boost::safe_numerics::safe_base
#include <cstddef>
#include <sstream> // For testing output operator

#include "ar/linear_combination.hpp"
#include "typedef.hpp"

// Define the specific linear_combination type for testing with size_t
using namespace Yuclid;

// Define a helper for creating rational numbers for tests
const Rat R0 = static_cast<Rat>(0);
const Rat R1 = static_cast<Rat>(1);
const Rat R_neg1 = static_cast<Rat>(-1);
const Rat R2 = static_cast<Rat>(2);
const Rat R_half = Rat(1, 2);
const Rat R_neg_half = Rat(-1, 2);
const Rat R_three_halves = Rat(3, 2);

BOOST_AUTO_TEST_SUITE(linear_combination_suite)

BOOST_AUTO_TEST_CASE(test_default_constructor) {
    LinearCombination<size_t> const lc;
    BOOST_CHECK(lc.empty());
    BOOST_CHECK_EQUAL(lc.terms().size(), 0);
    std::stringstream ss;
    ss << lc;
    BOOST_CHECK_EQUAL(ss.str(), "0");
}

BOOST_AUTO_TEST_CASE(test_single_term_constructor) {
    LinearCombination<size_t> const lc(10, R2); // 2 * X10
    BOOST_CHECK(!lc.empty());
    BOOST_CHECK_EQUAL(lc.terms().size(), 1);
    BOOST_CHECK_EQUAL(lc.terms().at(0).first, 10);
    BOOST_CHECK_EQUAL(lc.terms().at(0).second, R2);

    LinearCombination<size_t> const lc_one(5); // 1 * X5
    BOOST_CHECK(!lc_one.empty());
    BOOST_CHECK_EQUAL(lc_one.terms().size(), 1);
    BOOST_CHECK_EQUAL(lc_one.terms().at(0).first, 5);
    BOOST_CHECK_EQUAL(lc_one.terms().at(0).second, R1);

    LinearCombination<size_t> const lc_zero(100, R0); // 0 * X100
    BOOST_CHECK(lc_zero.empty());
    BOOST_CHECK_EQUAL(lc_zero.terms().size(), 0);
}

BOOST_AUTO_TEST_CASE(test_addition_operator_plus_equals) {
    LinearCombination<size_t> lc1(1, R1); // X1
    LinearCombination<size_t> const lc2(2, R2); // 2*X2
    LinearCombination<size_t> const lc3(1, R_half); // 0.5*X1

    lc1 += lc2; // X1 + 2*X2
    BOOST_CHECK_EQUAL(lc1.terms().size(), 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).second, R1);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).second, R2);

    lc1 += lc3; // (X1 + 2*X2) + 0.5*X1 = 1.5*X1 + 2*X2
    BOOST_CHECK_EQUAL(lc1.terms().size(), 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).second, R_three_halves);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).second, R2);

    LinearCombination<size_t> const lc4(1, R_neg_half); // -0.5*X1
    lc1 += lc4; // (1.5*X1 + 2*X2) + (-0.5*X1) = X1 + 2*X2
    BOOST_CHECK_EQUAL(lc1.terms().size(), 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).second, R1);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).second, R2);

    LinearCombination<size_t> lc5(1, R_neg1); // -X1
    LinearCombination<size_t> const lc6(1, R1); // X1
    lc5 += lc6; // -X1 + X1 = 0
    BOOST_CHECK(lc5.empty());
}

BOOST_AUTO_TEST_CASE(test_subtraction_operator_minus_equals) {
    LinearCombination<size_t> lc1(1, R2); // 2*X1
    LinearCombination<size_t> const lc2(2, R1); // X2
    LinearCombination<size_t> const lc3(1, R_half); // 0.5*X1

    lc1 -= lc2; // 2*X1 - X2
    BOOST_CHECK_EQUAL(lc1.terms().size(), 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).second, R2);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).second, R_neg1);

    lc1 -= lc3; // (2*X1 - X2) - 0.5*X1 = 1.5*X1 - X2
    BOOST_CHECK_EQUAL(lc1.terms().size(), 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).second, R_three_halves);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(1).second, R_neg1);

    LinearCombination<size_t> const lc4(1, R_three_halves); // 1.5*X1
    lc1 -= lc4; // (1.5*X1 - X2) - 1.5*X1 = -X2
    BOOST_CHECK_EQUAL(lc1.terms().size(), 1);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).first, 2);
    BOOST_CHECK_EQUAL(lc1.terms().at(0).second, R_neg1);

    LinearCombination<size_t> lc5(1, R1); // X1
    LinearCombination<size_t> const lc6(1, R1); // X1
    lc5 -= lc6; // X1 - X1 = 0
    BOOST_CHECK(lc5.empty());
}

BOOST_AUTO_TEST_CASE(test_multiplication_operator_times_equals) {
    LinearCombination<size_t> lc(1, R2); // 2*X1
    lc += LinearCombination<size_t>(2, R_half);

    lc *= R2; // (2*X1 + 0.5*X2) * 2 = 4*X1 + X2
    BOOST_CHECK_EQUAL(lc.terms().size(), 2);
    BOOST_CHECK_EQUAL(lc.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(lc.terms().at(0).second, static_cast<Rat>(4));
    BOOST_CHECK_EQUAL(lc.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(lc.terms().at(1).second, R1);

    lc *= R0; // (4*X1 + X2) * 0 = 0
    BOOST_CHECK(lc.empty());
}

BOOST_AUTO_TEST_CASE(test_unary_minus) {
    LinearCombination<size_t> lc(1, R2); // 2*X1
    lc += LinearCombination<size_t>(2, R_half);

    LinearCombination<size_t> const neg_lc = -lc; // -2*X1 - 0.5*X2
    BOOST_CHECK_EQUAL(neg_lc.terms().size(), 2);
    BOOST_CHECK_EQUAL(neg_lc.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(neg_lc.terms().at(0).second, static_cast<Rat>(-2));
    BOOST_CHECK_EQUAL(neg_lc.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(neg_lc.terms().at(1).second, R_neg_half);

    LinearCombination<size_t> const lc_zero;
    LinearCombination<size_t> const neg_lc_zero = -lc_zero;
    BOOST_CHECK(neg_lc_zero.empty());
}

BOOST_AUTO_TEST_CASE(test_binary_addition) {
    LinearCombination<size_t> const lc1(1, R1); // X1
    LinearCombination<size_t> const lc2(2, R2); // 2*X2
    LinearCombination<size_t> const lc3(1, R_half); // 0.5*X1

    LinearCombination<size_t> const sum1 = lc1 + lc2; // X1 + 2*X2
    BOOST_CHECK_EQUAL(sum1.terms().size(), 2);
    BOOST_CHECK_EQUAL(sum1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(sum1.terms().at(0).second, R1);
    BOOST_CHECK_EQUAL(sum1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(sum1.terms().at(1).second, R2);

    LinearCombination<size_t> const sum2 = sum1 + lc3; // (X1 + 2*X2) + 0.5*X1 = 1.5*X1 + 2*X2
    BOOST_CHECK_EQUAL(sum2.terms().size(), 2);
    BOOST_CHECK_EQUAL(sum2.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(sum2.terms().at(0).second, R_three_halves);
    BOOST_CHECK_EQUAL(sum2.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(sum2.terms().at(1).second, R2);

    LinearCombination<size_t> const lc4(1, R_neg1); // -X1
    LinearCombination<size_t> const lc5(1, R1); // X1
    LinearCombination<size_t> const sum_zero = lc4 + lc5; // -X1 + X1 = 0
    BOOST_CHECK(sum_zero.empty());
}

BOOST_AUTO_TEST_CASE(test_binary_subtraction) {
    LinearCombination<size_t> const lc1(1, R2); // 2*X1
    LinearCombination<size_t> const lc2(2, R1); // X2
    LinearCombination<size_t> const lc3(1, R_half); // 0.5*X1

    LinearCombination<size_t> const diff1 = lc1 - lc2; // 2*X1 - X2
    BOOST_CHECK_EQUAL(diff1.terms().size(), 2);
    BOOST_CHECK_EQUAL(diff1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(diff1.terms().at(0).second, R2);
    BOOST_CHECK_EQUAL(diff1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(diff1.terms().at(1).second, R_neg1);

    LinearCombination<size_t> const diff2 = diff1 - lc3; // (2*X1 - X2) - 0.5*X1 = 1.5*X1 - X2
    BOOST_CHECK_EQUAL(diff2.terms().size(), 2);
    BOOST_CHECK_EQUAL(diff2.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(diff2.terms().at(0).second, R_three_halves);
    BOOST_CHECK_EQUAL(diff2.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(diff2.terms().at(1).second, R_neg1);

    LinearCombination<size_t> const lc4(1, R1); // X1
    LinearCombination<size_t> const lc5(1, R1); // X1
    LinearCombination<size_t> const diff_zero = lc4 - lc5; // X1 - X1 = 0
    BOOST_CHECK(diff_zero.empty());
}

BOOST_AUTO_TEST_CASE(test_binary_multiplication_lc_times_coeff) {
    LinearCombination<size_t> lc(1, R2); // 2*X1
    lc += LinearCombination<size_t>(2, R_half);

    LinearCombination<size_t> const prod = lc * R2; // (2*X1 + 0.5*X2) * 2 = 4*X1 + X2
    BOOST_CHECK_EQUAL(prod.terms().size(), 2);
    BOOST_CHECK_EQUAL(prod.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(prod.terms().at(0).second, static_cast<Rat>(4));
    BOOST_CHECK_EQUAL(prod.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(prod.terms().at(1).second, R1);

    LinearCombination<size_t> const prod_zero = lc * R0; // (2*X1 + 0.5*X2) * 0 = 0
    BOOST_CHECK(prod_zero.empty());
}

BOOST_AUTO_TEST_CASE(test_binary_multiplication_coeff_times_lc) {
    LinearCombination<size_t> lc(1, R2); // 2*X1
    lc += LinearCombination<size_t>(2, R_half);

    LinearCombination<size_t> const prod = R2 * lc; // 2 * (2*X1 + 0.5*X2) = 4*X1 + X2
    BOOST_CHECK_EQUAL(prod.terms().size(), 2);
    BOOST_CHECK_EQUAL(prod.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(prod.terms().at(0).second, static_cast<Rat>(4));
    BOOST_CHECK_EQUAL(prod.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(prod.terms().at(1).second, R1);

    LinearCombination<size_t> const prod_zero = R0 * lc; // 0 * (2*X1 + 0.5*X2) = 0
    BOOST_CHECK(prod_zero.empty());
}

BOOST_AUTO_TEST_CASE(test_equality_operator) {
    LinearCombination<size_t> lc1(1, R1);
    lc1 += LinearCombination<size_t>(2, R2); // X1 + 2*X2

    LinearCombination<size_t> lc2(2, R2);
    lc2 += LinearCombination<size_t>(1, R1); // X1 + 2*X2

    LinearCombination<size_t> const lc3(1, R2); // 2*X1

    BOOST_CHECK_EQUAL(lc1, lc2);
    BOOST_CHECK(lc1 != lc3);
    BOOST_CHECK(LinearCombination<size_t>() == LinearCombination<size_t>()); // Empty LCs are equal
    BOOST_CHECK_EQUAL(LinearCombination<size_t>(1, R0), LinearCombination<size_t>(2, R0));
    // Note: The single-term constructor with R0 results in an empty LC, so these are equal
    BOOST_CHECK(LinearCombination<size_t>(1, R0) == LinearCombination<size_t>());
}

BOOST_AUTO_TEST_CASE(test_common_denominator) {
    LinearCombination<size_t> lc1(1, Rat(1, 2));
    lc1 += LinearCombination<size_t>(2, Rat(1, 3)); // 0.5*X1 + 0.333*X2
    BOOST_CHECK_EQUAL(lc1.common_denominator(), static_cast<Int>(6));

    LinearCombination<size_t> lc2(1, Rat(3, 4));
    lc2 += LinearCombination<size_t>(2, Rat(5, 6)); // 0.75*X1 + 0.833*X2
    BOOST_CHECK_EQUAL(lc2.common_denominator(), static_cast<Int>(12));

    LinearCombination<size_t> const lc3(1, static_cast<Rat>(7)); // 7*X1
    BOOST_CHECK_EQUAL(lc3.common_denominator(), static_cast<Int>(1));

    LinearCombination<size_t> const lc_empty;
    BOOST_CHECK_EQUAL(lc_empty.common_denominator(), static_cast<Int>(1));
}

BOOST_AUTO_TEST_CASE(test_linear_combine) {
    LinearCombination<size_t> lc1(1, R1); // X1
    LinearCombination<size_t> const lc2(2, R1); // X2
    LinearCombination<size_t> const lc3(1, R2); // 2*X1
    LinearCombination<size_t> const lc4(3, R_half); // 0.5*X3

    // 2*lc1 + 3*lc2 = 2*X1 + 3*X2
    LinearCombination<size_t> const combined1 = lc1.linear_combine(R2, Rat(3), lc2);
    BOOST_CHECK_EQUAL(combined1.terms().size(), 2);
    BOOST_CHECK_EQUAL(combined1.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(combined1.terms().at(0).second, static_cast<Rat>(2));
    BOOST_CHECK_EQUAL(combined1.terms().at(1).first, 2);
    BOOST_CHECK_EQUAL(combined1.terms().at(1).second, static_cast<Rat>(3));

    // 1*lc1 + (-1)*lc3 = X1 - 2*X1 = -X1
    LinearCombination<size_t> const combined2 = lc1.linear_combine(R1, R_neg1, lc3);
    BOOST_CHECK_EQUAL(combined2.terms().size(), 1);
    BOOST_CHECK_EQUAL(combined2.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(combined2.terms().at(0).second, R_neg1);

    // 0*lc1 + 1*lc4 = 0.5*X3
    LinearCombination<size_t> const combined3 = lc1.linear_combine(R0, R1, lc4);
    BOOST_CHECK_EQUAL(combined3.terms().size(), 1);
    BOOST_CHECK_EQUAL(combined3.terms().at(0).first, 3);
    BOOST_CHECK_EQUAL(combined3.terms().at(0).second, R_half);

    // 2*lc1 + 0*lc2 = 2*X1
    LinearCombination<size_t> const combined4 = lc1.linear_combine(R2, R0, lc2);
    BOOST_CHECK_EQUAL(combined4.terms().size(), 1);
    BOOST_CHECK_EQUAL(combined4.terms().at(0).first, 1);
    BOOST_CHECK_EQUAL(combined4.terms().at(0).second, R2);
}

BOOST_AUTO_TEST_SUITE_END()
