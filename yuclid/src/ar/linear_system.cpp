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
// This is the implementation file for the LinearSystem template class.
// It is typically included at the end of the corresponding header file (.hpp)
// so that the full template definition is available when compiled.

#include <boost/preprocessor/seq/for_each.hpp>
#include <cassert>
#include <cstddef>
#include <stdexcept> // For std::out_of_range, std::runtime_error
#include <string>    // For std::to_string, string concatenation
#include <set>       // For std::set operations
#include <map>       // For std::map operations
#include "ar/linear_system.hpp"
#include "ar/linear_combination.hpp"
#include "solver/statement_proof.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "type/dist.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "type/variable_types.hpp"
#include "typedef.hpp"

#include <utility>

using namespace std; // As per instruction, using namespace std at the top

namespace Yuclid {

  template <typename VarT>
  void LinearSystem<VarT>::reduce_next(LinearCombinationType &e) {
    while (true) {
      const auto &it_begin = e.rhs().lhs().begin();
      // An iterator pointing at the 2nd term in the LHS of the equation.
      const auto &it_next = std::next(it_begin);

      VarT head_var = it_begin->first;

      if (it_next == e.rhs().lhs().end()) {
        // Only the pivot term left.
        m_found_variables.insert(head_var);
        break;
      }

      auto [next_var, next_coeff] = *it_next;

      const auto &echelon_it = m_echelon_form.find(next_var);
      // No more reductions to the next term.
      // Register in the cache and return.
      if (echelon_it == m_echelon_form.end()) {
        m_pivot_by_next[next_var].insert(head_var);
        break;
      }

      e -= next_coeff * echelon_it->second;
    }
  }

  template <typename VarT>
  void LinearSystem<VarT>::add_reduced_equation(StatementProof *pf) {
    auto eq = pf->reduced_equation<VarT>();
    // Skip null ptrs
    if (!eq) {
      return;
    }

    if (eq->is_solved()) {
      return;
    }

    if (eq->remainder().lhs().empty()) [[unlikely]] {
      throw runtime_error("Proved contradiction in AR");
    }

    IndexType const n(m_equations.size(), this);

    m_equations.push_back(make_pair(eq->original_equation(), pf));

    LinearCombinationType lc(LinearCombination<IndexType>(n),
                               eq->original_equation());
    // It should be a bit faster to add this way
    lc = -eq->linear_combination() + lc;
    // In debug builds, double check the invariant.
    assert(lc.rhs() == eq->remainder());
    assert(!lc.rhs().lhs().empty());

    auto [v, c] = *(lc.rhs().lhs().begin());
    assert(!m_echelon_form.contains(v));
    lc *= Rat(1) / c;
    reduce_next(lc);
    if (!m_echelon_form.insert(make_pair(v, lc)).second) {
      throw std::runtime_error("Trying to inssert a non-reduced equation");
    }

    // Partial back substitution
    auto it = m_pivot_by_next.find(v);
    if (it != m_pivot_by_next.end()) {
      for (const auto &pivot : it->second) {
        auto it_pivot = m_echelon_form.find(pivot);
        assert(it_pivot != m_echelon_form.end());
        reduce_next(it_pivot->second);
      }
      m_pivot_by_next.erase(it);
    }

  }

  template <typename VarT>
  const pair<typename LinearSystem<VarT>::EquationType, StatementProof *> &
  LinearSystem<VarT>::pair_at(IndexType i) const {
    size_t const idx = i.get();
    if (idx >= m_equations.size()) [[unlikely]] {
      throw out_of_range("Equation index " + to_string(idx) + " out of bounds for linear system of size " + to_string(m_equations.size()));
    }
    return m_equations[idx];
  }

  template <typename VarT>
  const typename LinearSystem<VarT>::EquationType& LinearSystem<VarT>::at(IndexType i) const {
    return pair_at(i).first;
  }

  template <typename VarT>
  vector<RatioSquaredDist> LinearSystem<VarT>::generate_suspected_ratio_squared_dist() const {
    if constexpr (std::is_same_v<VarT, SlopeAngle>) {
      return {};
    } else {
      vector<RatioSquaredDist> res;
      for (const auto& [next_var, pivots_sharing_next] : m_pivot_by_next) {
        // Iterate over pairs of distinct pivots (i, j) within this bucket where i < j
        for (auto it_i = pivots_sharing_next.begin(); it_i != pivots_sharing_next.end(); ++it_i) {
          const VarT& i_var = *it_i;

          // We get no `ratio_squared_dist`s from something like `\sin α = \sin b` or `\sin α = 3|bc|`.
          if constexpr (std::is_same_v<VarT, SinOrDist>) {
            if (i_var.is_sin()) {
              continue;
            }
          }

          // Get the echelon form equation for pivot 'i_var'
          const auto& eq_i_lc = m_echelon_form.at(i_var);
          // Get the coefficient of the 'next_var' in eq_i_lc.rhs().lhs()
          // (i.e., the coefficient 'a' for 'next_var' in the equation where 'i_var' is pivot)
          auto eq_i_coeff = std::next(eq_i_lc.rhs().lhs().begin())->second;

          // If the LHS has only 2 terms, then we can find `i_var`
          // in terms of `next_var`
          if (eq_i_lc.rhs().lhs().terms().size() == 2) {
            if constexpr (is_same_v<VarT, Dist>) {
              if (eq_i_lc.rhs().rhs() == RHSType()) {
                assert(eq_i_coeff < 0);
                res.emplace_back(SquaredDist(i_var), SquaredDist(next_var),
                                 rat2nnrat(eq_i_coeff * eq_i_coeff));
              }
            } else if constexpr (is_same_v<VarT, SquaredDist>) {
              assert(eq_i_coeff < 0);
              if (eq_i_lc.rhs().rhs() == RHSType()) {
                res.emplace_back(SquaredDist(i_var), SquaredDist(next_var),
                                 rat2nnrat(-eq_i_coeff));
              }
            } else {
              static_assert(std::is_same_v<VarT, SinOrDist>,
                            "We should deal with the ratios table in this branch.");
              if (eq_i_coeff == -1) {
                res.emplace_back(SquaredDist(i_var.get_squared_dist()),
                                 SquaredDist(next_var.get_squared_dist()), 1);
              }
            }
          }

          for (auto it_j = std::next(it_i); it_j != pivots_sharing_next.end(); ++it_j) {
            const auto& eq_j_lc = m_echelon_form.at(*it_j);
            auto eq_j_coeff = std::next(eq_j_lc.rhs().lhs().begin())->second;

            if constexpr (std::is_same_v<VarT, Dist>) {
              res.emplace_back(SquaredDist(i_var), SquaredDist(*it_j),
                               rat2nnrat((eq_i_coeff * eq_i_coeff) /
                                         (eq_j_coeff * eq_j_coeff)));
            } else if constexpr (std::is_same_v<VarT, SquaredDist>) {
              Rat const c = eq_i_coeff / eq_j_coeff;
              if (c < 0) {
                continue;
              }
              res.emplace_back(i_var, *it_j, rat2nnrat(eq_i_coeff / eq_j_coeff));
            } else {
              static_assert(std::is_same_v<VarT, SinOrDist>,
                            "We should deal with the ratios table in this branch.");
              // Since the set is sorted, we know for sure `it_j->is_squared_dist()`.
              if (eq_i_coeff == eq_j_coeff) {
                res.emplace_back(SquaredDist(i_var.get_squared_dist()),
                                 SquaredDist(it_j->get_squared_dist()), 1);
              }
            }
          }
        }
      }
      return res;
    }
  }

  template <typename VarT>
  size_t LinearSystem<VarT>::size() const {
    return m_equations.size();
  }

  template <typename VarT>
  std::set<VarT> LinearSystem<VarT>::new_found_variables() const {
    return m_found_variables;
  }

  template <typename VarT>
  void LinearSystem<VarT>::clear_new_found_variables() {
    m_found_variables.clear();
  }

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_LINEAR_SYSTEM, /* empty */, YUCLID_EQN_VARIABLE_TYPES)
} // namespace Yuclid
