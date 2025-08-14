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
#pragma once
#include <iostream>
#include "numbers/util.hpp"
#include "typedef.hpp"

namespace Yuclid {
  /**
   * @brief Positive doubles with addition mapped to multiplication.
   */
  class Posreal final {
  private:
    double m_data;
  public:
    Posreal();
    explicit Posreal(double x);
    /** Returns the underlying number. */
    [[nodiscard]] const double &number() const { return m_data; }

    Posreal &operator+=(const Posreal &rhs);
    Posreal &operator-=(const Posreal &rhs);
    Posreal &operator*=(const Rat &coeff);
    Posreal operator-() const;
    auto operator<=>(const Posreal &other) const = default;
  };

  Posreal operator+(Posreal lhs, const Posreal &rhs);
  Posreal operator-(Posreal lhs, const Posreal &rhs);
  Posreal operator*(Posreal lhs, const Rat &coeff);
  Posreal operator*(const Rat &coeff, Posreal lhs);

  std::ostream &operator<<(std::ostream &out, const Posreal &x);

  template<>
  bool approx_eq(const Posreal& lhs, const Posreal& rhs);
}
