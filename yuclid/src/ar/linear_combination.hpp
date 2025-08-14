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

#include "ar/eqn_index.hpp"
#include "equation_traits.hpp"
#include "type/angle.hpp"
#include "type/dist.hpp"
#include "type/sin_or_dist.hpp"
#include "type/squared_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/variable_types.hpp"

#include <vector>              // For std::vector
#include <utility>             // For std::pair
#include <ostream>             // For std::ostream
#include <boost/preprocessor.hpp>

namespace Yuclid {

  template <typename VarT> class Equation; // Forward-declaration for `equation()`

  /**
   * @brief Represents a linear combination of geometric variables.
   *
   * This template class holds a collection of terms, where each term
   * consists of a geometric variable and its associated coefficient.
   * Coefficients of zero are not stored; terms are automatically
   * removed if their coefficient becomes zero after an operation.
   *
   * Storage is managed using a std::vector of pairs, sorted by the variable.
   *
   * @tparam VarT The type of the geometric variable (e.g., `dist`, `SinOrDist`).
   */
  template <typename VarT>
  class LinearCombination final {
  public:
    using VariableType = VarT;                                   /**< Alias for the variable type. */
    using EvaluationType = typename EquationTraits<VarT>::EvaluationType;   /**< Alias for the evaluation result type. */
    using TermsVectorType = std::vector<std::pair<VariableType, Rat>>; /**< Alias for the internal vector type. */

  private:
    // The internal storage mapping variables to their coefficients.
    // Stored as a sorted vector of pairs (variable, coefficient).
    TermsVectorType m_terms;

    template <typename left_operation, typename right_operation,
              typename binary_operation>
    [[nodiscard]]
    LinearCombination<VarT> merge_terms(const LinearCombination<VarT>& right,
                                          left_operation op_left,
                                          right_operation op_right,
                                          binary_operation binop) const;

  public:
    /**
     * @brief Default constructor. Creates an empty linear combination.
     */
    LinearCombination() = default;

    /**
     * @brief Constructs a linear combination with a single initial term.
     * If the coefficient is zero, the combination remains empty.
     * @param var The initial variable.
     * @param coeff The coefficient for the initial variable.
     */
    LinearCombination(const VariableType& var, const Rat& coeff);

    /**
     * @brief Explicitly constructs a linear combination with a single term.
     * The variable's coefficient is set to 1. This serves as the explicit
     * "cast from VariableType to linear_combination".
     * @param var The variable to convert into a single-term linear combination.
     */
    explicit LinearCombination(const VariableType& var);

    /**
     * @brief Find the least common denominator of all coefficients.
     *
     * @return The least common multiple of the denominators of all coefficients.
     */
    [[nodiscard]] Int common_denominator() const;

    /**
     * @brief Adds another linear combination to this one (compound assignment).
     * @param other The linear combination to add.
     * @return A reference to this linear combination after addition.
     */
    LinearCombination& operator+=(const LinearCombination& other);
    LinearCombination operator+(const LinearCombination& rhs) const;

    /**
     * @brief Subtracts another linear combination from this one (compound assignment).
     * @param other The linear combination to subtract.
     * @return A reference to this linear combination after subtraction.
     */
    LinearCombination& operator-=(const LinearCombination& other);
    LinearCombination operator-(const LinearCombination& rhs) const;

    /**
     * @brief Multiplies this linear combination by a coefficient (compound assignment).
     * If the multiplier is zero, the combination becomes empty.
     * @param multiplier The coefficient to multiply by.
     * @return A reference to this linear combination after multiplication.
     */
    LinearCombination& operator*=(const Rat& multiplier);
    LinearCombination operator*(const Rat& multiplier) const;

    /**
     * @brief Unary minus operator. Creates a new linear combination with all coefficients negated.
     * @return A new linear combination with negated coefficients.
     */
    LinearCombination operator-() const;

    /**
     * @brief Checks if the linear combination is empty (contains no terms).
     * @return True if empty, false otherwise.
     */
    [[nodiscard]] bool empty() const;

    /**
     * @brief Evaluates the linear combination numerically.
     *
     * The evaluation is performed by summing (coefficient * variable_value).
     *
     * @return The numerical evaluation of the linear combination.
     */
    [[nodiscard]] EvaluationType evaluate() const;

    /**
     * @brief Gets a const reference to the underlying vector of terms.
     * @return A const reference to `m_terms`.
     */
    [[nodiscard]] const TermsVectorType& terms() const;

    /**
     * @brief Returns a const iterator to the beginning of the terms vector.
     * @return A const iterator.
     */
    [[nodiscard]] typename TermsVectorType::const_iterator begin() const;

    /**
     * @brief Returns a const iterator to the end of the terms vector.
     * @return A const iterator.
     */
    [[nodiscard]] typename TermsVectorType::const_iterator end() const;

    LinearCombination<VarT> linear_combine(const Rat& coeff_this,
                                             const Rat& coeff_other,
                                             const LinearCombination<VarT>& other);

    auto operator<=>(const LinearCombination& other) const = default;
  };

  /**
   * @brief Multiplies a linear combination by a coefficient (coeff * lc).
   * @param multiplier The coefficient.
   * @param lc The linear combination.
   * @return A new linear combination representing the product.
   */
  template <typename VarT>
  LinearCombination<VarT> operator*(const Rat& multiplier,
                                      const LinearCombination<VarT>& lc);

  /**
   * @brief Inserts a string representation of the linear combination into an output stream.
   * @param os The output stream.
   * @param lc The linear combination to print.
   * @return A reference to the output stream.
   */
  template <typename VarT>
  std::ostream& operator<<(std::ostream& os, const LinearCombination<VarT>& lc);

} // namespace Yuclid

#define YUCLID_INSTANTIATE_LINEAR_COMBINATION(r, prefix, VarT)          \
  prefix template class Yuclid::LinearCombination<VarT>;                \
  prefix template Yuclid::LinearCombination<VarT>                       \
  Yuclid::operator*(const Yuclid::Rat& multiplier,                      \
                    const Yuclid::LinearCombination<VarT>& lc);         \
  prefix template std::ostream&                                         \
  Yuclid::operator<<(std::ostream& os,                                  \
                     const Yuclid::LinearCombination<VarT>& lc);

BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_LINEAR_COMBINATION, extern,
                      YUCLID_LINEAR_COMBINATION_TYPES)
