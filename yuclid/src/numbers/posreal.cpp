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
#include <ostream>
#include <stdexcept>
#include "numbers/posreal.hpp"
#include "numbers/util.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {
  Posreal::Posreal() : m_data(1) { }

  Posreal::Posreal(double x) : m_data(x) {
    if (x <= 0) {
      throw runtime_error("`Posreal` type is for positive numbers only");
    }
  }

  Posreal &Posreal::operator+=(const Posreal &rhs) {
    m_data *= rhs.m_data;
    return *this;
  }

  Posreal &Posreal::operator-=(const Posreal &rhs) {
    m_data /= rhs.m_data;
    return *this;
  }

  Posreal &Posreal::operator*=(const Rat &coeff) {
    m_data = pow(m_data, rat2double(coeff));
    return *this;
  }

  Posreal Posreal::operator-() const {
    return Posreal(1 / m_data);
  }

  Posreal operator+(Posreal lhs, const Posreal &rhs) {
    return lhs += rhs;
  }

  Posreal operator-(Posreal lhs, const Posreal &rhs) {
    return lhs -= rhs;
  }

  Posreal operator*(Posreal lhs, const Rat &coeff) {
    return lhs *= coeff;
  }

  Posreal operator*(const Rat &coeff, Posreal lhs) {
    return lhs * coeff;
  }

  std::ostream &operator<<(std::ostream &out, const Posreal &x) {
    return out << x.number();
  }

  template<>
  bool approx_eq(const Posreal& lhs, const Posreal& rhs) {
    return approx_eq(lhs.number(), rhs.number());
  }

}
