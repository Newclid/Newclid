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
// -*- C++ -*-
// This is the implementation file for the equation template class.
// It is typically included at the end of the corresponding header file (.hpp)
// so that the full template definition is available when compiled.

#include <boost/preprocessor/seq/for_each.hpp>
#include <ostream>
#include <utility>
#include "equation.hpp"
#include "ar/eqn_index.hpp"
#include "ar/equation_traits.hpp"
#include "ar/linear_combination.hpp"
#include "numbers/posreal.hpp"
#include "type/angle.hpp"
#include "type/slope_angle.hpp"
#include "type/variable_types.hpp"
#include "typedef.hpp"

using namespace std; // As per instruction, using namespace std at the top

namespace Yuclid {

  // Constructor
  template <typename VarT>
  Equation<VarT>::Equation(LinearCombinationType lhs, RHSType rhs)
    : m_lhs(std::move(lhs)), m_rhs(std::move(rhs)) {
  }

  // Compound addition
  template <typename VarT>
  Equation<VarT>& Equation<VarT>::operator+=(const Equation& other) {
    m_lhs += other.m_lhs;
    m_rhs += other.m_rhs;
    return *this;
  }

  // Compound subtraction
  template <typename VarT>
  Equation<VarT>& Equation<VarT>::operator-=(const Equation& other) {
    m_lhs -= other.m_lhs;
    m_rhs -= other.m_rhs;
    return *this;
  }

  // Compound multiplication
  template <typename VarT>
  Equation<VarT>& Equation<VarT>::operator*=(const Rat& multiplier) {
    m_lhs *= multiplier;
    m_rhs *= multiplier;
    return *this;
  }

  // Unary minus
  template <typename VarT>
  Equation<VarT> Equation<VarT>::operator-() const {
    Equation result = *this; // Start with a copy
    result.m_lhs = -result.m_lhs; // Negate LHS
    result.m_rhs = -result.m_rhs;
    return result;
  }

  template<typename VarT>
  Equation<VarT> operator==(const LinearCombination<VarT>& lhs,
                             const typename EquationTraits<VarT>::RHSType& rhs) {
    return Equation<VarT>(lhs, rhs);
  }

  template <typename VarT>
  Equation<VarT> Equation<VarT>::sub_eq_sub(const VarT &a, const VarT &b, const VarT &c, const VarT &d) {
    RHSType const rhs;
    return LinearCombination<VarT>(a) - LinearCombination<VarT>(b) - LinearCombination<VarT>(c) + LinearCombination<VarT>(d) == rhs;
  }

  template <typename VarT>
  Equation<VarT> Equation<VarT>::sub_eq_const(const VarT &a, const VarT &b, const typename Equation<VarT>::RHSType &rhs) {
    return LinearCombination<VarT>(a) - LinearCombination<VarT>(b) == rhs;
  }

  // Binary addition
  template <typename VarT>
  Equation<VarT> Equation<VarT>::operator+(const Equation<VarT>& other) const {
    Equation<VarT> result = *this; // Start with a copy of lhs_eq
    result += other; // Use compound assignment
    return result;
  }

  // Binary subtraction
  template <typename VarT>
  Equation<VarT> Equation<VarT>::operator-(const Equation<VarT>& other) const {
    Equation<VarT> result = *this;
    result -= other; // Use compound assignment
    return result;
  }

  // Binary multiplication (equation * coefficient)
  template <typename VarT>
  Equation<VarT> Equation<VarT>::operator*(const Rat& multiplier) const {
    Equation<VarT> result = *this; // Start with a copy
    result *= multiplier; // Use compound assignment
    return result;
  }

  // Binary multiplication (coefficient * equation)
  template <typename VarT>
  Equation<VarT> operator*(const Rat& multiplier, const Equation<VarT>& eq) {
    return eq * multiplier; // Delegate to the other binary operator*
  }

  template <typename VarT>
  bool Equation<VarT>::is_empty() const {
    return m_lhs.empty() && m_rhs == RHSType();
  }

  template<typename VarT>
  pair<Rat, Equation<VarT>> Equation<VarT>::normalize() const {
    if (m_lhs.empty()) {
      return {1, *this};
    }
    if constexpr (is_same_v<typename EquationTraits<VarT>::RHSType,
                  AddCircle<Rat>>) {
      if (m_lhs.begin()->second > 0) {
        return {1, *this};
      }
      return {-1, -*this};
    } else {
      Rat const coeff = 1 / m_lhs.begin()->second;
      return {coeff, *this * coeff};
    }
  }

  // Output stream operator
  template <typename VarT>
  std::ostream& operator<<(std::ostream& os, const Equation<VarT>& eq) {
    os << eq.m_lhs << " = " << eq.m_rhs;
    return os;
  }

  Equation<SlopeAngle> angle_equation_to_slope_angle_equation(const Equation<Angle>& eq_angle) {
    // Accumulate terms for the new linear_combination<SlopeAngle>
    LinearCombination<SlopeAngle> new_lhs; 

    // Iterate over each term (angle_variable, coefficient) in the input equation's LHS
    for (const auto& [var, coeff] : eq_angle.lhs().terms()) {
      new_lhs += LinearCombination<SlopeAngle>(var.right_side(), coeff);
      new_lhs += LinearCombination<SlopeAngle>(var.left_side(), -coeff);
    }

    // Construct and return the new equation<SlopeAngle>
    return {new_lhs, eq_angle.rhs()};
  }


} // namespace Yuclid

BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQUATION, /* empty */, YUCLID_EQUATION_TYPES)
