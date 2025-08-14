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
#define BOOST_TEST_MODULE additive_tests
#include <boost/test/unit_test.hpp>
#include "numbers/rational.hpp"
#include <cmath>              // For std::pow (used by additive<double>)
#include <sstream>            // For ostringstream in stream insertion test

// Include your additive type header
#include "numbers/additive.hpp"

// Using namespace std for convenience as per your request
using namespace std;
using namespace Yuclid;

// --- Test Suites ---

BOOST_AUTO_TEST_SUITE(additive_double_suite)

BOOST_AUTO_TEST_CASE(test_double_constructors_and_number) {
    additive<double> a1(1.0);
    BOOST_TEST(a1.number() == 1.0);

    additive<double> a2(2.5);
    BOOST_TEST(a2.number() == 2.5);

    additive<double> a3 = a1; // Copy constructor
    BOOST_TEST(a3.number() == 1.0);

    additive<double> a4 = std::move(a2); // Move constructor
    BOOST_TEST(a4.number() == 2.5);
}

BOOST_AUTO_TEST_CASE(test_double_additive_operations) {
    additive<double> a(2.0);
    additive<double> b(3.0);

    // operator+= (multiplication on underlying type)
    a += b;
    BOOST_TEST(a.number() == 6.0);

    // operator+ (multiplication on underlying type)
    additive<double> c = a + b;
    BOOST_TEST(c.number() == 18.0);

    // operator-= (division on underlying type)
    a = additive<double>(10.0);
    b = additive<double>(2.0);
    a -= b;
    BOOST_TEST(a.number() == 5.0);

    // operator- (division on underlying type)
    c = a - b;
    BOOST_TEST(c.number() == 2.5);
}

BOOST_AUTO_TEST_CASE(test_double_multiplicative_operations) {
    additive<double> val(2.0);

    // operator*= (power on underlying type) - positive exponent
    val *= 3;
    BOOST_TEST(val.number() == 8.0);

    // operator* (power on underlying type) - positive exponent
    additive<double> res = val * 2;
    BOOST_TEST(res.number() == 64.0);

    // operator*= (power on underlying type) - zero exponent
    val = additive<double>(5.0);
    val *= 0;
    BOOST_TEST(val.number() == 1.0);

    // operator*= (power on underlying type) - negative exponent
    val = additive<double>(2.0);
    val *= -2;
    BOOST_TEST(val.number() == 0.25);

    // operator* (power on underlying type) - negative exponent
    res = additive<double>(3.0) * -1;
    BOOST_TEST(res.number() == (1.0 / 3.0));
}

BOOST_AUTO_TEST_CASE(test_double_comparisons) {
    additive<double> a(10.0);
    additive<double> b(10.0);
    additive<double> c(20.0);

    BOOST_TEST(a == b);
    BOOST_TEST(a != c);
    BOOST_TEST(a < c);
    BOOST_TEST(c > a);
    BOOST_TEST(a <= b);
    BOOST_TEST(a <= c);
    BOOST_TEST(c >= a);
    BOOST_TEST(b >= a);
}

BOOST_AUTO_TEST_CASE(test_double_stream_insertion) {
    additive<double> a(123.456);
    ostringstream oss;
    oss << a;
    BOOST_TEST(oss.str() == "123.456");
}

BOOST_AUTO_TEST_CASE(test_double_default_constructor) {
  BOOST_TEST(additive<double>() == additive<double>(1.0));
}

BOOST_AUTO_TEST_SUITE_END() // additive_double_suite


BOOST_AUTO_TEST_SUITE(additive_rational_suite)


BOOST_AUTO_TEST_CASE(test_rational_constructors_and_number) {
    additive<rat> a1(rat(1, 2));
    BOOST_TEST(a1.number() == rat(1, 2));

    additive<rat> a2(rat(3, 4));
    BOOST_TEST(a2.number() == rat(3, 4));

    additive<rat> a3 = a1; // Copy constructor
    BOOST_TEST(a3.number() == rat(1, 2));

    additive<rat> a4 = std::move(a2); // Move constructor
    BOOST_TEST(a4.number() == rat(3, 4));
}

BOOST_AUTO_TEST_CASE(test_rational_additive_operations) {
    additive<rat> a(rat(1, 2));
    additive<rat> b(rat(2, 3));

    // operator+= (multiplication on underlying type)
    a += b;
    BOOST_TEST(a.number() == rat(1, 3));

    // operator+ (multiplication on underlying type)
    additive<rat> c = a + b;
    BOOST_TEST(c.number() == rat(2, 9));

    // operator-= (division on underlying type)
    a = additive<rat>(rat(1, 2));
    b = additive<rat>(rat(2, 3));
    a -= b;
    BOOST_TEST(a.number() == rat(3, 4));

    // operator- (division on underlying type)
    c = a - b;
    BOOST_TEST(c.number() == rat(9, 8));
}

BOOST_AUTO_TEST_CASE(test_rational_multiplicative_operations) {
    additive<rat> val(rat(2, 1)); // Value 2

    // operator*= (power on underlying type) - positive exponent
    val *= 3;
    BOOST_TEST(val.number() == rat(8, 1));

    // operator* (power on underlying type) - positive exponent
    additive<rat> res = val * 2;
    BOOST_TEST(res.number() == rat(64, 1));

    // operator*= (power on underlying type) - zero exponent
    val = additive<rat>(rat(5, 7));
    val *= 0;
    BOOST_TEST(val.number() == rat(1, 1));

    // operator*= (power on underlying type) - negative exponent
    val = additive<rat>(rat(2, 3));
    val *= -2;
    BOOST_TEST(val.number() == rat(9, 4));

    // operator* (power on underlying type) - negative exponent
    res = additive<rat>(rat(1, 3)) * -1;
    BOOST_TEST(res.number() == rat(3, 1));
}

BOOST_AUTO_TEST_CASE(test_rational_comparisons) {
    additive<rat> a(rat(1, 2));
    rat r(2, 4);
    r.canonicalize();
    additive<rat> b(r); // Same value as a, but reduced form is (1,2)
    additive<rat> c(rat(3, 4));

    BOOST_TEST(a == b);
    BOOST_TEST(a != c);
    BOOST_TEST(a < c);
    BOOST_TEST(c > a);
    BOOST_TEST(a <= b);
    BOOST_TEST(a <= c);
    BOOST_TEST(c >= a);
    BOOST_TEST(b >= a);
}

BOOST_AUTO_TEST_CASE(test_rational_stream_insertion) {
    additive<rat> a(rat(7, 3));
    ostringstream oss;
    oss << a;
    BOOST_TEST(oss.str() == "7/3");
}

BOOST_AUTO_TEST_CASE(test_rational_default_constructor) {
  BOOST_TEST(additive<rat>() == additive<rat>(rat(1)));
}

BOOST_AUTO_TEST_SUITE_END() // additive_rational_suite
