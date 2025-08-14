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
#include "numbers/util.hpp"
#include "typedef.hpp"
#include "add_circle.hpp"

#include <boost/preprocessor/seq/for_each.hpp>
#include <cmath>
#include <ostream>

// Use GNU style for indentation
using namespace std;

namespace Yuclid {

  template<>
  bool approx_eq(const AddCircle<double> &lhs, const AddCircle<double> &rhs) {
    return
      approx_eq(lhs.number(), rhs.number()) ||
      approx_eq(lhs.number() + 1, rhs.number()) ||
      approx_eq(lhs.number(), rhs.number() + 1);
  }

  template<>
  bool approx_eq(const AddCircle<double> &lhs, const AddCircle<Rat> &rhs) {
    return
      approx_eq(lhs.number(), Rat(rhs.number())) ||
      approx_eq(lhs.number() + 1, Rat(rhs.number())) ||
      approx_eq(lhs.number(), Rat(rhs.number() + 1));
  }

  // --- mod1_reduce helper function definition ---
  template <typename T>
  static T mod1_reduce(const T &val) {
    if constexpr (is_same_v<T, double>) {
      double result = fmod(val, 1.0);
      if (result < 0.0) {
        result += 1.0;
      }
      return result;
    } else {
      Rat result = Rat(val.numerator() % val.denominator(), val.denominator());
      if (result < Rat(0)) {
        result += Rat(1);
      }
      return result;
    }
  }

  // --- AddCircle class template definitions ---

  // Constructors
  template<typename t>
  AddCircle<t>::AddCircle() : m_data(t()) {}

  template <typename t>
  AddCircle<t>::AddCircle(const NumberType &r)
    : m_data(mod1_reduce(r)) {}

  template <typename t>
  AddCircle<t>::AddCircle(NumberType &&r)
    : m_data(mod1_reduce(std::move(r))) {}

  // Getter
  template <typename t>
  const typename AddCircle<t>::NumberType &AddCircle<t>::number() const {
    return m_data;
  }

  // Compound assignment operators
  template <typename t>
  AddCircle<t> &AddCircle<t>::operator+=(const AddCircle<t> &rhs) {
    m_data = mod1_reduce(t(m_data + rhs.m_data));
    return *this;
  }

  template <typename t>
  AddCircle<t> &AddCircle<t>::operator-=(const AddCircle<t> &rhs) {
    m_data = mod1_reduce(t(m_data - rhs.m_data));
    return *this;
  }

  template <typename t>
  AddCircle<t> &AddCircle<t>::operator*=(Rat coeff) {
    if constexpr (is_same_v<t, double>) {
      m_data = mod1_reduce(m_data * rat2double(coeff));
    } else {
      m_data = mod1_reduce(m_data * coeff);
    }
    return *this;
  }

  template <typename t>
  AddCircle<t> AddCircle<t>::operator-() const {
    return AddCircle<t>(-m_data);
  }

  // --- Non-member binary operators ---
  template <typename t>
  AddCircle<t> operator+(AddCircle<t> lhs, const AddCircle<t> &rhs) {
    lhs += rhs;
    return lhs;
  }

  template <typename t>
  AddCircle<t> operator-(AddCircle<t> lhs, const AddCircle<t> &rhs) {
    lhs -= rhs;
    return lhs;
  }

  template <typename t>
  AddCircle<t> operator*(AddCircle<t> lhs, Rat coeff) {
    lhs *= coeff;
    return lhs;
  }

  template <typename t>
  AddCircle<t> operator*(Rat coeff, AddCircle<t> rhs) {
    return rhs * coeff;
  }

  // Stream insertion operator
  template <typename t>
  ostream &operator<<(ostream &out, const AddCircle<t> &obj) {
    return out << "AddCircle(" << obj.number() << ")";
  }

  BOOST_PP_SEQ_FOR_EACH(INSTANTIATE_ADD_CIRCLE, /* empty */, BASE_FIELDS)

} // namespace Yuclid
