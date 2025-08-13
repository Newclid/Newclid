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

#include "ar/linear_combination.hpp"
#include "numbers/util.hpp"
#include "typedef.hpp"

namespace Yuclid {
  class Posreal;

  /**
   * @brief The `RootRat` class represents the `n`th root of a rational number.
   *
   * It stores a rational number and an integer exponent.
   * Operations are defined so that addition means multiplication of underlying numbers
   * and multiplication by a rational number means exponentiation.
   */
  class RootRat {
  private:
    LinearCombination<size_t> m_data;

  public:
    /**
     * @brief Constructor for RootRat from a rational number.
     * Represents the rational number itself (i.e., 1st root).
     * @param r The rational number.
     */
    explicit RootRat(const NNRat& r);

    RootRat(const NNRat& r, Int exp);

    /**
     * @brief Default constructor: `√[1](1)`
     */
    RootRat();

    /**
     * @brief Get the underlying unsigned rational number, or 0
     *
     * If the object represents a rational number, then return it.
     * Otherwise, return zero.
     */
    [[nodiscard]] NNRat as_nnrat() const;

    [[nodiscard]] const LinearCombination<size_t>& data() const { return m_data; }

    [[nodiscard]] Posreal evaluate() const;

    // --- Arithmetic Operators (Member Functions) ---

    /**
     * @brief Compound assignment operator for "addition" (multiplication of underlying numbers).
     * Corresponds to: `this = this * other` (in terms of actual values).
     * @param other The `RootRat` to "add".
     * @return Reference to this `RootRat` after operation.
     */
    RootRat& operator+=(const RootRat& other);

    /**
     * @brief Compound assignment operator for "subtraction" (division of underlying numbers).
     * Corresponds to: `this = this / other` (in terms of actual values).
     * @param other The `RootRat` to "subtract".
     * @return Reference to this `RootRat` after operation.
     * @throws std::runtime_error if division by zero occurs.
     */
    RootRat& operator-=(const RootRat& other);

    /**
     * @brief Compound assignment operator for "multiplication" (exponentiation of underlying number).
     * Corresponds to: this = this ^ r_val (in terms of actual values).
     * @param r_val The rational exponent.
     * @return Reference to this RootRat after operation.
     */
    RootRat& operator*=(const Rat& r_val);

    /**
     * @brief Unary minus operator (corresponds to reciprocal of underlying number).
     * Corresponds to: 1 / this (in terms of actual values).
     * @return A new RootRat representing the reciprocal.
     */
    RootRat operator-() const;

    // --- Comparison Operators ---

    /**
     * @brief Equality operator.
     * @param other The other RootRat object to compare with.
     * @return True if the numbers are equal.
     */
    bool operator==(const RootRat& other) const;

    /**
     * @brief Three-way comparison operator (C++20).
     *
     * Compares by the lex order of prime numbers' exponents.
     */
    std::strong_ordering operator<=>(const RootRat& other) const;

    // --- Friend Declarations for Non-Member Operators ---
    friend std::ostream& operator<<(std::ostream& os, const RootRat& rr);
  };

  RootRat operator+(RootRat x, const RootRat& y);
  RootRat operator-(RootRat x, const RootRat& y);
  RootRat operator*(RootRat x, const Rat& r_val);
  RootRat operator*(const Rat& r_val, RootRat x);

  template<>
  bool approx_eq(const Posreal& a, const RootRat& b);

  inline size_t hash_value(const RootRat& arg) {
    return hash_range(arg.data().begin(), arg.data().end());
  }
}
