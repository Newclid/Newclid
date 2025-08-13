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

#include "ar/linear_combination.hpp"
#include "ar/equation_traits.hpp"
#include "numbers/root_rat.hpp"
#include <ostream>

namespace Yuclid {
  template<typename VarT> class EqnIndex;

  /**
   * @brief Represents a linear equation involving geometric variables.
   *
   * This class holds a linear combination for its left-hand side (LHS)
   * and a value of `RHSType` for its right-hand side (RHS).
   * Algebraic operations applied to an `equation` object will affect both
   * its LHS and RHS.
   *
   * @tparam VarT The type of the geometric variable (e.g., `Dist`, `SinOrDist`).
   */
  template <typename VarT>
  class Equation final {
  public:
    using VariableType = VarT;                                   /**< Alias for the variable type. */
    using LinearCombinationType = LinearCombination<VariableType>; /**< Alias for the linear combination type. */
    using RHSType = typename EquationTraits<VariableType>::RHSType; /**< Alias for the RHS type. */

  private:
    LinearCombinationType m_lhs; /**< The left-hand side of the equation. */
    RHSType m_rhs;                /**< The right-hand side of the equation. */

  public:
    /**
     * @brief Default constructor, build the `0 = 0` equation.
     */
    Equation() = default;

    /**
     * @brief Constructs an `equation` from a linear combination and an RHS value.
     * @param lhs The linear combination for the left-hand side.
     * @param rhs The value for the right-hand side.
     */
    Equation(LinearCombinationType lhs, RHSType rhs);

    /**
     * @brief Gets a const reference to the left-hand side linear combination.
     * @return A const reference to the LHS.
     */
    [[nodiscard]] const LinearCombinationType& lhs() const { return m_lhs; }

    /**
     * @brief Gets a const reference to the right-hand side value.
     * @return A const reference to the RHS.
     */
    [[nodiscard]] const RHSType& rhs() const { return m_rhs; }

    /**
     * @brief Compound addition operator. Adds another equation to this one.
     * Both LHS and RHS are added.
     * @param other The equation to add.
     * @return A reference to this equation after addition.
     */
    Equation& operator+=(const Equation& other);
    Equation operator+(const Equation& other) const;

    /**
     * @brief Compound subtraction operator. Subtracts another equation from this one.
     * Both LHS and RHS are subtracted.
     * @param other The equation to subtract.
     * @return A reference to this equation after subtraction.
     */
    Equation& operator-=(const Equation& other);
    Equation operator-(const Equation& other) const;

    /**
     * @brief Compound multiplication operator. Multiplies both sides by a coefficient.
     * @param multiplier The coefficient to multiply by.
     * @return A reference to this equation after multiplication.
     */
    Equation& operator*=(const Rat& multiplier);
    Equation operator*(const Rat& multiplier) const;

    /**
     * @brief Unary minus operator. Negates both sides of the equation.
     * @return A new equation with negated LHS and RHS.
     */
    Equation operator-() const;

    /**
     * @brief Defaulted three-way comparison operator.
     * Compares two `equation` objects based on their `m_lhs` and then `m_rhs` members.
     */
    auto operator<=>(const Equation& other) const = default;

    /**
     * @brief Generates equation `a - b = c - d`.
     */
    static Equation sub_eq_sub(const VarT &a, const VarT &b, const VarT &c, const VarT &d);

    /**
     * @brief Generate equation `a - b = rhs`.
     */
    static Equation sub_eq_const(const VarT &a, const VarT &b, const RHSType &rhs = {});

    [[nodiscard]] bool check_numerically() const {
      return approx_eq(lhs().evaluate(), RHSType(m_rhs));
    }

    [[nodiscard]] bool is_empty() const;

    [[nodiscard]] std::pair<Rat, Equation> normalize() const;

    template <typename VarTt>
    friend std::ostream& operator<<(std::ostream& os, const Equation<VarTt>& eq);
  };

  template<typename VarT>
  bool approx_eq(const Equation<VarT> &left, const Equation<VarT> &right) {
    return left == right;
  }

  template<typename VarT>
  Equation<VarT> operator==(const LinearCombination<VarT>& lhs, const typename EquationTraits<VarT>::RHSType& rhs);

  template <typename VarT>
  Equation<VarT> operator*(const Rat &multiplier, const Equation<VarT>& eq);

  template <typename VarT>
  std::ostream& operator<<(std::ostream& os, const Equation<VarT>& eq);

  /** @brief Convert an equation about `angle`s into an equation about `SlopeAngle`s.
   * For each `c * v i`, add `c * (v i).right_side - c * (v i).left_side`.
   */
  Equation<SlopeAngle> angle_equation_to_slope_angle_equation(const Equation<Angle>& eq_angle);

  template <typename VarT>
  inline size_t hash_value(const Equation<VarT>& arg) {
    size_t seed = hash_range(arg.lhs().begin(), arg.lhs().end());
    boost::hash_combine(seed, arg.rhs());
    return seed;
  }

} // namespace Yuclid

#define YUCLID_INSTANTIATE_EQUATION(r, prefix, VarT)    \
  prefix template                                       \
  class Yuclid::Equation<VarT>;                         \
  prefix template Yuclid::Equation<VarT>                \
  Yuclid::operator==                                    \
  (const Yuclid::LinearCombination<VarT>& lhs,          \
   const typename                                       \
   Yuclid::EquationTraits<VarT>::RHSType& rhs);         \
  prefix template Yuclid::Equation<VarT>                \
  Yuclid::operator*(const Yuclid::Rat &multiplier,      \
                    const Yuclid::Equation<VarT>& eq);  \
  prefix template std::ostream&                         \
  Yuclid::operator<<(std::ostream& os,                  \
                     const Yuclid::Equation<VarT>& eq);

BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQUATION, extern, YUCLID_EQUATION_TYPES)
