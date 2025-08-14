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

#include <boost/preprocessor.hpp>

#include "type/variable_types.hpp"
#include "typedef.hpp"    // For Yuclid::rat

// Forward declarations for types that might be used as VarT in EqnIndex
namespace Yuclid {
  template <typename VarT> class EqnIndex;
  template <typename VarT> class Equation;
  template <typename t> class AddCircle;
  class Posreal;

  /**
   * @brief Base template for EquationTraits.
   *
   * This primary template defines the `VariableType` alias.
   * Specializations will define `EvaluationType`,
   * `RHSType`, and `is_multiplicative` based on the geometric variable.
   *
   * @tparam VarT The geometric variable type (e.g., `Dist`, `SinOrDist`).
   */
  template <typename VarT>
  struct EquationTraits {
    using VariableType = VarT; /**< The type of the variable itself, inherited by specializations. */
  };

  /**
   * @brief Specialization of `EquationTraits` for `dist` variables.
   */
  template <>
  struct EquationTraits<Dist> {
    using EvaluationType = double;        /**< Evaluates to a double number (`double`). */
    using RHSType = Rat;                /**< RHS is also a rational number (`rat`). */
    static constexpr bool is_multiplicative = false; /**< This type uses additive formatting. */
    static EvaluationType eval_term(const Rat &c, const Dist &v);
  };

  /**
   * @brief Specialization of `EquationTraits` for `SquaredDist` variables.
   */
  template <>
  struct EquationTraits<SquaredDist> {
    using EvaluationType = double;        /**< Evaluates to a double number (`double`). */
    using RHSType = Rat;                /**< RHS is also a rational number (`rat`). */
    static constexpr bool is_multiplicative = false; /**< This type uses additive formatting. */
    static EvaluationType eval_term(const Rat &c, const SquaredDist &v);
  };

  /**
   * @brief Specialization of `EquationTraits` for `SinOrDist` variables.
   */
  template <>
  struct EquationTraits<SinOrDist> {
    using EvaluationType = Posreal;  /**< Evaluates to `Posreal`. */
    using RHSType = RootRat;          /**< RHS is `RootRat`. */
    static constexpr bool is_multiplicative = true; /**< This type uses multiplicative formatting. */
    static EvaluationType eval_term(const Rat &c, const SinOrDist &v);
  };

  /**
   * @brief Specialization of `EquationTraits` for `SlopeAngle` variables.
   */
  template <>
  struct EquationTraits<SlopeAngle> {
    using EvaluationType = AddCircle<double>;/**< Evaluates to `AddCircle<double>`. */
    using RHSType = AddCircle<Rat>;        /**< RHS is `AddCircle<rat>`. */
    static constexpr bool is_multiplicative = false; /**< This type uses additive formatting. */
    static EvaluationType eval_term(const Rat &c, const SlopeAngle &v);
  };

  /**
   * @brief Specialization of `EquationTraits` for `angle` variables.
   */
  template <>
  struct EquationTraits<Angle> {
    using EvaluationType = AddCircle<double>;/**< Evaluates to `AddCircle<double>`. */
    using RHSType = AddCircle<Rat>;        /**< RHS is `AddCircle<rat>`. */
    static constexpr bool is_multiplicative = false; /**< This type uses additive formatting. */
    static EvaluationType eval_term(const Rat &c, const Angle &v);
  };

  /**
   * @brief Specialization of `EquationTraits` for `EqnIndex<VarT>` variables.
   *
   * This allows linear combinations of equation indices, effectively representing
   * linear combinations of equations themselves.
   *
   * @tparam VarT The original geometric variable type (e.g., `dist`) that the indexed equation holds.
   */
  template <typename VarT>
  struct EquationTraits<EqnIndex<VarT>> {
    static constexpr bool is_multiplicative = EquationTraits<VarT>::is_multiplicative; /**< Multiplicative property inherited from the underlying variable type. */
    using EvaluationType = Equation<VarT>; /**< Evaluates to an `equation<VarT>`. */
    using RHSType = Equation<VarT>;        /**< RHS is also an `equation<VarT>`. */
    static EvaluationType eval_term(const Rat &c, const EqnIndex<VarT> &v);
  };

  template <>
  struct EquationTraits<size_t> {
    using EvaluationType = Posreal;  /**< Evaluates to `Posreal`. */
    static constexpr bool is_multiplicative = true; /**< This type uses multiplicative formatting. */
    static EvaluationType eval_term(const Rat& c, const size_t& v);
  };

#define YUCLID_EQN_INDEX_TYPES                                          \
  (EqnIndex<Dist>)(EqnIndex<SquaredDist>)(EqnIndex<SinOrDist>)(EqnIndex<SlopeAngle>)

#define YUCLID_INSTANTIATE_EQUATION_TRAITS(r, prefix, VarT)            \
  prefix template typename EquationTraits<VarT>::EvaluationType        \
  EquationTraits<VarT>::eval_term(const Rat &c, const VarT &v);

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQUATION_TRAITS, extern, YUCLID_EQN_INDEX_TYPES)

} // namespace Yuclid
