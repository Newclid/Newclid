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
// This is the implementation file for the ReducedEquation template class.
// It is typically included at the end of the corresponding header file (.hpp)
// so that the full template definition is available when compiled.

#include <boost/preprocessor/seq/for_each.hpp>
#include <cassert>
#include <cmath>     // For std::abs (for integer coefficients)
#include <boost/log/trivial.hpp>

// Includes for types used in LinearSystem operations
#include "ar/eqn_index.hpp"
#include "linear_system.hpp"
#include "numbers/add_circle.hpp"
#include "type/variable_types.hpp"
#include "typedef.hpp"
#include "reduced_equation.hpp"

using namespace std;

namespace Yuclid {

  // Explicit constructor from original equation
  template <typename VarT>
  ReducedEquation<VarT>::ReducedEquation(const EquationType& original_eq,
                                            const LinearSystem<VarT> *sys)
    : m_original_eq(original_eq),
      m_system(sys),
      m_linear_combination(),
      m_remainder(original_eq)
  { }

  // Reduce method
  template <typename VarT>
  void ReducedEquation<VarT>::reduce() {

    while (!m_remainder.lhs().empty()) {
      auto &[var, coeff] = *(m_remainder.lhs().begin());

      // Check if this variable is a pivot in the echelon form
      auto echelon_it = m_system->echelon_form().find(var);
        
      // If a pivot is found for the leading variable of the remainder, reduce it.
      // Otherwise, no further reduction is possible with current echelon form.
      if (echelon_it != m_system->echelon_form().end()) {
        const LinearCombinationType& pivot_eq_lc = echelon_it->second; // Equation<EqnIndex<VarT>>
        m_linear_combination += coeff * pivot_eq_lc; // LC_new = coeff + factor * pivot_indices
        m_remainder -= coeff * pivot_eq_lc.rhs(); // R_new = R_old - coeff * pivot_equation_content
      } else {
        // No pivot found for the leading variable, cannot reduce further.
        // Break the reduction loop.
        break;
      }
    }
  }

  template <typename VarT>
  bool ReducedEquation<VarT>::is_solved() const {
    if constexpr (is_same_v<typename LinearSystem<VarT>::RHSType, AddCircle<Rat>>) {
      if (!m_remainder.lhs().empty()) {
        return false;
      }
      if (m_remainder.rhs() == AddCircle<Rat>()) {
        return true;
      }
      Rat const c(m_linear_combination.lhs().common_denominator());
      AddCircle<Rat> rhs(c * m_original_eq.rhs());
      for (const auto &[k, v] : m_linear_combination.lhs()) {
        Rat const a = c * v;
        assert (a.denominator() == 1);
        rhs -= a * k.equation().rhs();
      }
      if (rhs != AddCircle<Rat>()) {
        BOOST_LOG_TRIVIAL(warning)
          << "Angle equation reduced to 0 = nonzero, even after multiplication by denominators";
      }
      return rhs == AddCircle<Rat>();
    } else {
      return m_remainder.is_empty();
    }
  }

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_REDUCED_EQUATION, /* empty */, \
                        YUCLID_EQN_VARIABLE_TYPES)

} // namespace Yuclid
