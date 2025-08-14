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

#include "numbers/rat.hpp"
#include "numbers/util.hpp"
#include "typedef.hpp"
#include <boost/preprocessor.hpp>
#include <iostream>     // For std::ostream

namespace Yuclid {

  /** @brief Represents a number on the circle R/Z.
   *
   * All operations automatically reduce the underlying number modulo 1,
   * ensuring it stays within the [0, 1) range.
   */
  template <typename t>
  class AddCircle {
  public:
    using NumberType = t;

  private:
    NumberType m_data;

  public:
    // Constructors
    AddCircle();
    explicit AddCircle(const NumberType &r);
    explicit AddCircle(NumberType &&r);

    /** Returns the underlying number in the [0, 1) range. */
    [[nodiscard]] const NumberType &number() const;

    // Compound assignment operators (perform modular arithmetic)
    AddCircle &operator+=(const AddCircle &rhs);
    AddCircle &operator-=(const AddCircle &rhs);
    /**
     * @brief Multiply an angle by a rational number.
     *
     * If the coefficient has a denominator greater than one,
     * then the operation is not well-defined.
     * We're picking one of the values.
     */
    AddCircle &operator*=(Rat coeff);
    AddCircle operator-() const;

    // Three-way comparison operator (C++20)
    auto operator<=>(const AddCircle &other) const = default;

  };

  /** @brief Approximate equality check, considering wrap-around for floating-point types. */
  template<>
  bool approx_eq(const AddCircle<double> &lhs, const AddCircle<double> &rhs);

  /** @brief Approximate equality check, considering wrap-around. */
  template<>
  bool approx_eq(const AddCircle<double> &lhs, const AddCircle<Rat> &rhs);

  // Non-member binary operators
  template <typename t>
  AddCircle<t> operator+(AddCircle<t> lhs, const AddCircle<t> &rhs);
  template <typename t>
  AddCircle<t> operator-(AddCircle<t> lhs, const AddCircle<t> &rhs);
  template <typename t>
  AddCircle<t> operator*(AddCircle<t> lhs, Rat coeff);
  template <typename t>
  AddCircle<t> operator*(Rat coeff, AddCircle<t> rhs);

  // Stream insertion operator
  template <typename t>
  std::ostream &operator<<(std::ostream & out, const AddCircle<t> & obj);

  template <typename t>
  size_t inline hash_value(const AddCircle<t>& arg) {
    return hash_value(arg.number());
  }

#define INSTANTIATE_ADD_CIRCLE(r, prefix, t)                            \
  prefix template class AddCircle<t>;                                   \
  prefix template AddCircle<t> operator+(AddCircle<t> lhs, const AddCircle<t> &rhs); \
  prefix template AddCircle<t> operator-(AddCircle<t> lhs, const AddCircle<t> &rhs); \
  prefix template AddCircle<t> operator*(AddCircle<t> lhs, Rat coeff);  \
  prefix template AddCircle<t> operator*(Rat coeff, AddCircle<t> rhs);  \
  prefix template std::ostream &operator<<(std::ostream &, const AddCircle<t> &);
  
  BOOST_PP_SEQ_FOR_EACH(INSTANTIATE_ADD_CIRCLE, extern, BASE_FIELDS)

} // namespace Yuclid
