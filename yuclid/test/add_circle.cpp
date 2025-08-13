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
#define BOOST_TEST_MODULE add_circle_tests
#include <boost/test/unit_test.hpp>
#include <sstream>            // For std::ostringstream in stream tests
#include <cmath>              // For std::fabs if any direct double comparisons are needed

// Include the header for the AddCircle type
#include "numbers/add_circle.hpp"

// Use namespace std for convenience
using namespace std;
// Use Yuclid namespace for types
using namespace Yuclid;

// Define a tolerance for double comparisons
const double DOUBLE_EPSILON = 1E-10; // A stricter epsilon for raw double comparisons in tests


BOOST_AUTO_TEST_SUITE(add_circle_double_suite)

BOOST_AUTO_TEST_CASE(test_double_constructors_and_number_reduction) {
    // Basic construction and reduction
    AddCircle<double> const a1(0.5);
    BOOST_CHECK_EQUAL(a1.number(), 0.5);

    AddCircle<double> const a2(1.5); // Should reduce to 0.5
    BOOST_CHECK_EQUAL(a2.number(), 0.5);

    AddCircle<double> const a3(-0.5); // Should reduce to 0.5
    BOOST_CHECK_EQUAL(a3.number(), 0.5);

    AddCircle<double> const a4(0.999999999);
    BOOST_CHECK_EQUAL(a4.number(), 0.999999999);

    AddCircle<double> const a5(std::nextafter(1.0, 0.0)); // Value slightly less than 1.0
    BOOST_TEST(a5.number() < 1.0);
    BOOST_TEST(a5.number() > (1.0 - DOUBLE_EPSILON)); // Should be close to 1.0
}

BOOST_AUTO_TEST_CASE(test_double_copy_move_constructors) {
    AddCircle<double> const original(0.75);
    AddCircle<double> const copied(original);
    BOOST_CHECK_EQUAL(copied.number(), 0.75);

    AddCircle<double> const moved(original);
    BOOST_CHECK_EQUAL(moved.number(), 0.75);
    // original is in a valid but unspecified state. For primitives, often 0.
}

BOOST_AUTO_TEST_CASE(test_double_copy_move_assignment) {
    AddCircle<double> a(0.1);
    AddCircle<double> const b(0.2);
    AddCircle<double> const c(0.3);

    a = b; // Copy assignment
    BOOST_CHECK_EQUAL(a.number(), 0.2);

    a = c; // Move assignment
    BOOST_CHECK_EQUAL(a.number(), 0.3);
}

BOOST_AUTO_TEST_CASE(test_double_operator_plus_equals) {
    AddCircle<double> a(0.5);
    AddCircle<double> b(0.3);
    a += b; // 0.5 + 0.3 = 0.8
    BOOST_CHECK_EQUAL(a.number(), 0.8);

    a = AddCircle<double>(0.7);
    b = AddCircle<double>(0.4);
    a += b; // 0.7 + 0.4 = 1.1 -> 0.1
    BOOST_TEST(fabs(a.number() - 0.1) < DOUBLE_EPSILON);
}

BOOST_AUTO_TEST_CASE(test_double_operator_minus_equals) {
    AddCircle<double> a(0.5);
    AddCircle<double> b(0.2);
    a -= b; // 0.5 - 0.2 = 0.3
    BOOST_CHECK_EQUAL(a.number(), 0.3);

    a = AddCircle<double>(0.1);
    b = AddCircle<double>(0.3);
    a -= b; // 0.1 - 0.3 = -0.2 -> 0.8
    BOOST_TEST(fabs(a.number() - 0.8) < DOUBLE_EPSILON);
}

BOOST_AUTO_TEST_CASE(test_double_operator_mult_equals) {
    AddCircle<double> a(0.2);
    a *= 3; // 0.2 * 3 = 0.6
    BOOST_CHECK_CLOSE(a.number(), 0.6, 1E-10);

    a = AddCircle<double>(0.3);
    a *= 5; // 0.3 * 5 = 1.5 -> 0.5
    BOOST_CHECK_CLOSE(a.number(), 0.5, 1E-10);

    a = AddCircle<double>(0.7);
    a *= -2; // 0.7 * -2 = -1.4 -> -0.4 -> 0.6
    BOOST_CHECK_CLOSE(a.number(), 0.6, 1E-10);

    a = AddCircle<double>(0.5);
    a *= 0; // 0.5 * 0 = 0.0
    BOOST_CHECK_EQUAL(a.number(), 0.0);
}

BOOST_AUTO_TEST_CASE(test_double_non_member_operators) {
    AddCircle<double> const a(0.2);
    AddCircle<double> const b(0.3);

    AddCircle<double> const sum = a + b; // 0.2 + 0.3 = 0.5
    BOOST_CHECK_EQUAL(sum.number(), 0.5);

    AddCircle<double> const diff = a - b; // 0.2 - 0.3 = -0.1 -> 0.9
    BOOST_CHECK_EQUAL(diff.number(), 0.9);

    AddCircle<double> const scaled = a * 4; // 0.2 * 4 = 0.8
    BOOST_CHECK_EQUAL(scaled.number(), 0.8);
}

BOOST_AUTO_TEST_CASE(test_double_approx_eq) {
    AddCircle<double> const a(0.1);
    AddCircle<double> const b(0.1 + 1E-8); // Very close
    AddCircle<double> const c(0.1 + 1.1E-2); // Slightly outside tolerance
    AddCircle<double> const d(0.999999999); // Close to 1 (equiv. to 0)
    AddCircle<double> const e(0.000000001); // Close to 0

    BOOST_TEST(approx_eq(a, b));
    BOOST_TEST(!(approx_eq(a, c))); // Should be false due to being outside tolerance

    // Test wrap-around equivalence (0.999... vs 0.000...)
    BOOST_TEST(approx_eq(d, e));
    BOOST_TEST(approx_eq(AddCircle<double>(0.0), AddCircle<double>(std::nextafter(1.0, 0.0)))); // 0 and almost 1
    BOOST_TEST(approx_eq(AddCircle<double>(0.0), AddCircle<double>(1E-8))); // 0 and small positive

    BOOST_TEST(!(approx_eq(AddCircle<double>(0.1), AddCircle<double>(0.9)))); // Not approx. equal (diff=0.2)
}

BOOST_AUTO_TEST_CASE(test_double_comparisons) {
    AddCircle<double> a(0.1);
    AddCircle<double> b(0.1);
    AddCircle<double> c(0.2);

    BOOST_CHECK_EQUAL(a, b);
    BOOST_TEST(a != c);
    BOOST_TEST(a < c);
    BOOST_TEST(c > a);
    BOOST_TEST(a <= b);
    BOOST_TEST(a <= c);
    BOOST_TEST(c >= a);
    BOOST_TEST(b >= a);
}

BOOST_AUTO_TEST_CASE(test_double_stream_insertion) {
    AddCircle<double> const a(0.123456);
    ostringstream oss;
    oss << a;
    BOOST_CHECK_EQUAL(oss.str(), "AddCircle(0.123456)");
}

BOOST_AUTO_TEST_SUITE_END() // add_circle_double_suite


BOOST_AUTO_TEST_SUITE(add_circle_rational_suite)

BOOST_AUTO_TEST_CASE(test_rat_constructors_and_number_reduction) {
    AddCircle<Rat> const a1(Rat(1, 2));
    BOOST_CHECK_EQUAL(a1.number(), Rat(1, 2));

    AddCircle<Rat> const a2(Rat(3, 2)); // Should reduce to 1/2
    BOOST_CHECK_EQUAL(a2.number(), Rat(1, 2));

    AddCircle<Rat> const a3(Rat(-1, 2)); // Should reduce to 1/2
    BOOST_CHECK_EQUAL(a3.number(), Rat(1, 2));

    AddCircle<Rat> const a4(Rat(10, 3)); // Should reduce to 1/3
    BOOST_CHECK_EQUAL(a4.number(), Rat(1, 3));
}

BOOST_AUTO_TEST_CASE(test_rat_copy_move_constructors) {
    AddCircle<Rat> const original(Rat(3, 4));
    AddCircle<Rat> const copied(original);
    BOOST_CHECK_EQUAL(copied.number(), Rat(3, 4));

    AddCircle<Rat> const moved(original);
    BOOST_CHECK_EQUAL(moved.number(), Rat(3, 4));
}

BOOST_AUTO_TEST_CASE(test_rat_copy_move_assignment) {
    AddCircle<Rat> a(Rat(1, 10));
    AddCircle<Rat> const b(Rat(2, 10));
    AddCircle<Rat> const c(Rat(3, 10));

    a = b; // Copy assignment
    BOOST_CHECK_EQUAL(a.number(), Rat(2, 10));

    a = c; // Move assignment
    BOOST_CHECK_EQUAL(a.number(), Rat(3, 10));
}

BOOST_AUTO_TEST_CASE(test_rat_operator_plus_equals) {
    AddCircle<Rat> a(Rat(1, 2));
    AddCircle<Rat> b(Rat(1, 3));
    a += b; // 1/2 + 1/3 = 5/6
    BOOST_CHECK_EQUAL(a.number(), Rat(5, 6));

    a = AddCircle<Rat>(Rat(3, 4));
    b = AddCircle<Rat>(Rat(1, 2));
    a += b; // 3/4 + 1/2 = 5/4 -> 1/4
    BOOST_CHECK_EQUAL(a.number(), Rat(1, 4));
}

BOOST_AUTO_TEST_CASE(test_rat_operator_minus_equals) {
    AddCircle<Rat> a(Rat(1, 2));
    AddCircle<Rat> b(Rat(1, 3));
    a -= b; // 1/2 - 1/3 = 1/6
    BOOST_CHECK_EQUAL(a.number(), Rat(1, 6));

    a = AddCircle<Rat>(Rat(1, 4));
    b = AddCircle<Rat>(Rat(1, 2));
    a -= b; // 1/4 - 1/2 = -1/4 -> 3/4
    BOOST_CHECK_EQUAL(a.number(), Rat(3, 4));
}

BOOST_AUTO_TEST_CASE(test_rat_operator_mult_equals) {
    AddCircle<Rat> a(Rat(1, 5));
    a *= 3; // 1/5 * 3 = 3/5
    BOOST_CHECK_EQUAL(a.number(), Rat(3, 5));

    a = AddCircle<Rat>(Rat(2, 3));
    a *= 2; // 2/3 * 2 = 4/3 -> 1/3
    BOOST_CHECK_EQUAL(a.number(), Rat(1, 3));

    a = AddCircle<Rat>(Rat(3, 4));
    a *= -2; // 3/4 * -2 = -6/4 = -3/2 -> -1/2 -> 1/2
    BOOST_CHECK_EQUAL(a.number(), Rat(1, 2));

    a = AddCircle<Rat>(Rat(1, 2));
    a *= 0; // 1/2 * 0 = 0
    BOOST_CHECK_EQUAL(a.number(), Rat(0, 1));
}

BOOST_AUTO_TEST_CASE(test_rat_non_member_operators) {
    AddCircle<Rat> const a(Rat(1, 4));
    AddCircle<Rat> const b(Rat(1, 2));

    AddCircle<Rat> const sum = a + b; // 1/4 + 1/2 = 3/4
    BOOST_CHECK_EQUAL(sum.number(), Rat(3, 4));

    AddCircle<Rat> const diff = a - b; // 1/4 - 1/2 = -1/4 -> 3/4
    BOOST_CHECK_EQUAL(diff.number(), Rat(3, 4));

    AddCircle<Rat> const scaled = a * 5; // 1/4 * 5 = 5/4 -> 1/4
    BOOST_CHECK_EQUAL(scaled.number(), Rat(1, 4));
}

BOOST_AUTO_TEST_CASE(test_rat_comparisons) {
    AddCircle<Rat> a(Rat(1, 2));
    AddCircle<Rat> b(Rat(2, 4)); // Same value as a
    AddCircle<Rat> c(Rat(3, 4));

    BOOST_CHECK_EQUAL(a, b);
    BOOST_TEST(a != c);
    BOOST_TEST(a < c);
    BOOST_TEST(c > a);
    BOOST_TEST(a <= b);
    BOOST_TEST(a <= c);
    BOOST_TEST(c >= a);
    BOOST_TEST(b >= a);
}

BOOST_AUTO_TEST_CASE(test_rat_stream_insertion) {
    AddCircle<Rat> const a(Rat(1, 7));
    ostringstream oss;
    oss << a;
    BOOST_CHECK_EQUAL(oss.str(), "AddCircle(1/7)");
}

BOOST_AUTO_TEST_CASE(test_rat_default_constructor) {
  AddCircle<Rat> const a;
  BOOST_CHECK_EQUAL(a, AddCircle<Rat>(0));
}

BOOST_AUTO_TEST_SUITE_END() // add_circle_rational_suite
