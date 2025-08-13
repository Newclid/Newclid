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
#include <cmath>
#include <compare>
#include <cstddef>
#include <ostream>
#include <stdexcept>
#include "ar/equation_traits.hpp"
#include "numbers/root_rat.hpp"
#include "numbers/posreal.hpp"
#include "numbers/util.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {

  NNRat RootRat::as_nnrat() const {
    NNRat result(1);
    for (const auto& [base, exp] : m_data.terms()) {
      if (exp.denominator() != 1) {
        return 0;
      }
      result *= zpower(base, exp.numerator());
    }
    return result;
  }

  RootRat::RootRat() = default;

  RootRat::RootRat(const NNRat& number) {
    if (number == NNRat(0)) {
      throw std::runtime_error("The `RootRat` class is for positive numbers only");
    }
    Nat numer = number.numerator();
    Nat denom = number.denominator();
    size_t base = 2;
    while (numer != 1 || denom != 1) {
      Int exp = 0;
      while (numer % base == 0) {
        numer /= base;
        ++ exp;
      }
      while (denom % base == 0) {
        denom /= base;
        -- exp;
      }
      if (exp != 0) {
        m_data += LinearCombination(base, Rat(exp));
      }
      ++ base;
    }
  }

  RootRat::RootRat(const NNRat& r, Int exp) : RootRat(r) {
    m_data *= Rat(1, exp);
  }

  bool RootRat::operator==(const RootRat& other) const = default;
  std::strong_ordering RootRat::operator<=>(const RootRat& other) const = default;

  RootRat& RootRat::operator+=(const RootRat& other) {
    m_data += other.m_data;
    return *this;
  }

  RootRat operator+(RootRat x, const RootRat& y) {
    return x += y;
  }

  RootRat& RootRat::operator-=(const RootRat& other) {
    m_data -= other.m_data;
    return *this;
  }

  RootRat operator-(RootRat x, const RootRat& y) {
    return x -= y;
  }

  RootRat RootRat::operator-() const {
    RootRat res;
    res.m_data = -m_data;
    return res;
  }

  RootRat& RootRat::operator*=(const Rat& r_val) {
    m_data *= r_val;
    return *this;
  }

  RootRat operator*(RootRat x, const Rat& r_val) {
    return x *= r_val;
  }

  RootRat operator*(const Rat& r_val, RootRat x) {
    return x *= r_val;
  }

  std::ostream& operator<<(std::ostream& os, const RootRat& rr) {
    NNRat const r = rr.as_nnrat();
    if (r == NNRat(0)) {
      os << rr.m_data;
    } else {
      os << r;
    }
    return os;
  }
  
  Posreal EquationTraits<size_t>::eval_term(const Rat &c, const size_t& v) {
    return c * Posreal(double(v));
  }

  Posreal RootRat::evaluate() const {
    return m_data.evaluate();
  }

  template<>
  bool approx_eq(const Posreal& a, const RootRat& b) {
    return approx_eq(a, b.evaluate());
  }

}
