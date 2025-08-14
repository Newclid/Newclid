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

#include "equation.hpp"
#include "eqn_index.hpp"
#include "typedef.hpp"
#include <vector>
#include <map>
#include <unordered_map>
#include <set>
#include <iostream>
#include <boost/container_hash/hash.hpp>

namespace Yuclid {
  class RatioSquaredDist;
  template <typename VarT> class ReducedEquation;

  /**
   * @brief Manages and solves a system of linear equations for a specific variable type.
   *
   * This template class holds a collection of original `equation` objects and
   * maintains a **row echelon form** of the system using a Gaussian elimination-like process.
   * It tracks **pivot variables** and can **reduce new equations modulo existing ones**.
   *
   * The class also manages a cache of **found variables** that can be solved for,
   * distinguishing between those already reported to the user and newly discovered ones.
   *
   * @tparam VarT The type of the geometric variable in the equations.
   */
  template <typename VarT>
  class LinearSystem final {
  public:
    using EquationType = Equation<VarT>;   /**< Alias for the equation type. */
    using IndexType = EqnIndex<VarT>;     /**< Alias for the equation index type. */
    using VariableType = VarT; /**< Alias for the variable type. */
    // Alias for an equation whose variables are `EqnIndex<VarT>`, used to represent linear combinations of equations.
    using LinearCombinationType = Equation<EqnIndex<VarT>>;

    // Define RHS type based on the VarT, as needed for calculations
    using RHSType = typename EquationTraits<VarT>::RHSType;

    using EchelonFormType =
      std::unordered_map<VariableType, LinearCombinationType,
                         boost::hash<VariableType>>;

  private:
    /** Stores the original equations in the system and the statements that generated them.
     *
     * More precisely, we store iterators to the cache of pending statements
     * in the problem's proof state.
     */
    std::vector<std::pair<EquationType, StatementProof *>> m_equations;

    // Row echelon form of the system: pivot variable maps to the echelon form equation
    // The equation's LHS is a linear combination of original equations, its RHS is also an equation.
    // The LHS of this equation will contain only equation indices.
    EchelonFormType m_echelon_form;

    // Cache of equations in the echelon form whose *second* nonzero term has the key variable.
    // Maps a variable (potential 'next' term) to a set of pivot variables that have this as their 'next' term.
    std::map<VariableType, std::set<VariableType>> m_pivot_by_next;

    // Cache of variables that can be found (i.e., solved for).
    std::set<VariableType> m_found_variables; // Awaiting to be requested

    /**
     * @brief Reduce the "next" term in a linear equation in place.
     *
     * Also add it to the relevant caches.
     *
     * @param e The linear combination equation to reduce.
     */
    void reduce_next(LinearCombinationType &e);

  public:
    /**
     * @brief Default constructor. Initializes an empty linear system.
     */
    LinearSystem() = default;

    /**
     * @brief Adds a reduced equation to the linear system, reducing it modulo existing ones.
     *
     * This method attempts to add a new equation to the system.
     * The equation is supposed to be already reduced.
     *
     * @param pf A proof of a statement that justifies the equation.
     */
    void add_reduced_equation(StatementProof *pf);

    /**
     * @brief Provides read-only access to an equation at a specific index.
     * @param i The `EqnIndex` of the equation to retrieve.
     * @return A const reference to the equation.
     * @throws std::out_of_range if the index is invalid.
     */
    const EquationType& at(IndexType i) const;

    /**
     * @brief Provides read-only access to an equation and the corresponding statement at a specific index.
     * @param i The `EqnIndex` of the equation to retrieve.
     * @return A const reference to the pair of the equation and the statement that proved it.
     * @throws std::out_of_range if the index is invalid.
     */
    const std::pair<EquationType, StatementProof *> &pair_at(IndexType i) const;

    /**
     * @brief Gets the total number of original equations currently stored in the system.
     * @return The number of original equations.
     */
    [[nodiscard]] size_t size() const;

    /**
     * @brief Returns a const reference to the echelon form map.
     * @return A const reference to `m_echelon_form`.
     */
    const EchelonFormType& echelon_form() const {
      return m_echelon_form;
    }

    /**
     * @brief Returns a const reference to the pivot by next cache.
     * @return A const reference to `m_pivot_by_next`.
     */
    const std::map<VariableType, std::set<VariableType>>& get_pivot_by_next() const {
      return m_pivot_by_next;
    }

    /**
     * @brief Returns the newly found variables.
     *
     * @return the newly found variables.
     */
    [[nodiscard]] std::set<VariableType> new_found_variables() const;

    void clear_new_found_variables();

    /**
     * @brief Generate `ratio_squared_dist` statements that may be true.
     *
     * This generator looks on the first two terms only,
     * so the generated statements may be false.
     */
    [[nodiscard]]
    std::vector<RatioSquaredDist> generate_suspected_ratio_squared_dist() const;
  };

  template <typename VarT>
  inline std::ostream& operator<<(std::ostream& out, const LinearSystem<VarT>& sys) {
    for (size_t i = 0; i < sys.size(); ++i) {
      out << sys.at(EqnIndex<VarT>(i, &sys)) << '\n';
    }
    for (const auto& [var, eqn]: sys.echelon_form()) {
      out << var << ": " << eqn.rhs() << '\n';
    }
    return out;
  }

#define YUCLID_INSTANTIATE_LINEAR_SYSTEM(r, prefix, my_type)    \
  prefix template class LinearSystem<my_type>;

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_LINEAR_SYSTEM, extern, YUCLID_EQN_VARIABLE_TYPES)

} // namespace Yuclid
