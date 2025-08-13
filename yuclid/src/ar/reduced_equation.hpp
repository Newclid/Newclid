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

#include "equation.hpp"        // For Yuclid::Equation
#include "linear_system.hpp"   // For LinearSystem::linear_combination_type and its thread-local instance
#include "typedef.hpp" // For double, rat (indirectly)

#include <optional>            // For std::optional if coefficient logic makes it conditional (though decided against)
#include <ranges>
#include <string>              // For error messages
#include <stdexcept>           // For std::runtime_error
#include <type_traits>         // For std::enable_if, std::is_same_v

namespace Yuclid {

  /**
   * @brief Represents an equation undergoing reduction in a linear system.
   *
   * This class holds an original equation,
   * a linear combination of equation indices representing operations performed, and a remainder equation.
   * It maintains the invariant: `original_equation() = linear_combination().rhs() + remainder()`.
   *
   * For angles, this equality may fail for the RHS,
   * because multiplication of an angle by a rational number is not well-defined.
   *
   * The `reduce()` method performs Gaussian elimination steps to simplify the
   * `m_remainder` and updates `m_linear_combination` to maintain the invariant.
   *
   * @tparam VarT The type of the geometric variable in the equation.
   */
  template <typename VarT>
  class ReducedEquation final {
  public:
    using EquationType = Equation<VarT>;
    using LinearCombinationType = typename LinearSystem<VarT>::LinearCombinationType;
    using VariableType = VarT;

  private:
    const EquationType m_original_eq;           /**< The original equation being reduced. */
    const LinearSystem<VarT> *m_system;
    // m_coefficient is now in the base class conditionally and is private there.
    LinearCombinationType m_linear_combination; /**< The linear combination of previous equations from the system. */
    EquationType m_remainder;                    /**< The remainder of the original equation after reduction. */

  public:
    /**
     * @brief Explicitly constructs a `ReducedEquation` from an original equation.
     *
     * Initializes the base class (which handles `m_coefficient`), `m_linear_combination_of_indices` to an empty
     * linear combination (representing 0 = 0), and `m_remainder` to a copy of `original_eq`.
     * This establishes the initial invariant.
     *
     * @param original_eq The equation to start reducing.
     * @param sys The linear system we use to reduce this equation.
     */
    explicit ReducedEquation(const EquationType& original_eq,
                              const LinearSystem<VarT> *sys);

    /**
     * @brief Gets a const reference to the original equation.
     * @return The original equation.
     */
    [[nodiscard]] const EquationType& original_equation() const { return m_original_eq; }

    /**
     * @brief Get the linear system that we use to reduce the equation.
     */
    [[nodiscard]] const LinearSystem<VarT> *linear_system() const { return m_system; }

    /**
     * @brief Gets a const reference to the linear combination of indices representing
     * the operations performed.
     * @return The linear combination of indices.
     */
    [[nodiscard]] const LinearCombinationType& linear_combination() const {
      return m_linear_combination;
    }

    /**
     * @brief Gets a const reference to the current remainder equation.
     * @return The remainder equation.
     */
    [[nodiscard]] const EquationType& remainder() const { return m_remainder; }

    /**
     * @brief Reduces the `m_remainder` by eliminating its leading terms using
     * equations from the global `LinearSystem`'s echelon form.
     *
     * This method iteratively applies reduction steps, modifying `m_remainder`
     * and `m_linear_combination_of_indices` to maintain the invariant.
     * The process continues until the `m_remainder`'s LHS is empty or
     * no pivot is found for its leading term.
     */
    void reduce();

    /**
     * @brief Check if the reduced equation is solved.
     */
    [[nodiscard]] bool is_solved() const;

    [[nodiscard]] auto statement_dependencies() const {
      return m_linear_combination.lhs()
        | std::views::transform([this](const auto &term) {
          return m_system->pair_at(term.first).second;
        });
    }

    // Defaulted comparison operator for ReducedEquation (compares all members)
    auto operator<=>(const ReducedEquation& other) const = default;
  };

  // Macro for explicit instantiation declarations/definitions
#define YUCLID_INSTANTIATE_REDUCED_EQUATION(r, prefix, VarT)    \
  prefix template class ReducedEquation<VarT>;

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_REDUCED_EQUATION, extern,    \
                        YUCLID_EQN_VARIABLE_TYPES)

} // namespace Yuclid
