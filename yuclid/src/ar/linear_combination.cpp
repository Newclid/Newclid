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
#include <boost/preprocessor/seq/for_each.hpp>
#include <ostream>
#include <cmath>     // For std::fabs (used by output operator)
#include <functional> // For std::plus, std::minus
#include <ranges>    // For std::ranges, std::views
#include <vector>
#include "linear_combination.hpp"
#include "ar/equation_traits.hpp"
#include "ar/equation.hpp" // NOLINT
#include "numbers/posreal.hpp" // NOLINT
#include "type/variable_types.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {

  // Constructor for a single term with coefficient
  template <typename VarT>
  LinearCombination<VarT>::LinearCombination(const VariableType& var, const Rat& coeff) {
    if (coeff != static_cast<Rat>(0)) {
      m_terms.push_back({var, coeff});
    }
  }

  template <typename VarT>
  LinearCombination<VarT>::LinearCombination(const VariableType& var)
    : LinearCombination(var, static_cast<Rat>(1)) {
  }

  template <typename VarT>
  Int LinearCombination<VarT>::common_denominator() const {
    Int res(1);
    for (const auto &[k, v] : m_terms) {
      res = boost::integer::lcm(res, v.denominator());
    }
    return res;
  }

  // Helper to merge two sorted term ranges using a binary operation
  template <typename VarT>
  template <typename left_operation, typename right_operation,
            typename binary_operation>
  [[nodiscard]] LinearCombination<VarT>
  LinearCombination<VarT>::merge_terms(const LinearCombination<VarT>& right,
                                         left_operation op_left,
                                         right_operation op_right,
                                         binary_operation binop) const {
    LinearCombination<VarT> merged_result;

    auto it1 = begin();
    auto end1 = end();
    auto it2 = right.begin();
    auto end2 = right.end();

    while (it1 != end1 || it2 != end2) {
      if (it1 != end1 && it2 != end2) {
        if (it1->first < it2->first) {
          merged_result.m_terms.emplace_back(it1->first,
                                             op_left(it1->second));
          ++it1;
        } else if (it2->first < it1->first) {
          merged_result.m_terms.emplace_back(it2->first,
                                             op_right(it2->second));
          ++it2;
        } else { // Variables are equal, apply operation
          Rat const combined_coeff = binop(it1->second, it2->second);
          if (combined_coeff != static_cast<Rat>(0)) {
            merged_result.m_terms.emplace_back(it1->first, combined_coeff);
          }
          ++it1;
          ++it2;
        }
      } else if (it1 != end1) {
        merged_result.m_terms.emplace_back(it1->first,
                                           op_left(it1->second));
        ++it1;
      } else { // it2 != end2
        merged_result.m_terms.emplace_back(it2->first,
                                           op_right(it2->second));
        ++it2;
      }
    }
    return merged_result;
  }

  // Compound addition
  template <typename VarT>
  LinearCombination<VarT>& LinearCombination<VarT>::operator+=(const LinearCombination<VarT>& other) {
    *this = *this + other; // Reroute to binary operator+
    return *this;
  }

  // Binary addition
  template <typename VarT>
  LinearCombination<VarT> LinearCombination<VarT>::operator+(const LinearCombination<VarT>& rhs) const {
    return merge_terms(rhs, std::identity{}, std::identity{}, std::plus<Rat>());
  }

  // Compound subtraction
  template <typename VarT>
  LinearCombination<VarT>& LinearCombination<VarT>::operator-=(const LinearCombination<VarT>& other) {
    *this = *this - other; // Reroute to binary operator-
    return *this;
  }

  // Binary subtraction
  template <typename VarT>
  LinearCombination<VarT> LinearCombination<VarT>::operator-(const LinearCombination<VarT>& rhs) const {
    return merge_terms(rhs, std::identity(), std::negate(), std::minus<Rat>());
  }

  // Multiplication by coefficient (compound assignment)
  template <typename VarT>
  LinearCombination<VarT>& LinearCombination<VarT>::operator*=(const Rat& multiplier) {
    if (multiplier == static_cast<Rat>(0)) {
      m_terms.clear(); // If multiplier is zero, the entire combination becomes zero
      return *this;
    }

    // Iterate through current terms and multiply their coefficients
    for (auto& pair : m_terms) {
      pair.second *= multiplier;
    }
    return *this;
  }

  // Unary minus
  template <typename VarT>
  LinearCombination<VarT> LinearCombination<VarT>::operator-() const {
    LinearCombination result;
    result.m_terms.reserve(m_terms.size()); // Pre-allocate
    for (const auto& [k, v] : m_terms) {
      result.m_terms.push_back({k, -v}); // Negate each coefficient and add to new vector
    }
    return result;
  }

  // Check if empty
  template <typename VarT>
  bool LinearCombination<VarT>::empty() const {
    return m_terms.empty();
  }

  // Evaluate method
  template <typename VarT>
  typename LinearCombination<VarT>::EvaluationType LinearCombination<VarT>::evaluate() const {
    EvaluationType sum_val = EvaluationType();
    for (const auto& pair : m_terms) {
      sum_val += EquationTraits<VarT>::eval_term(pair.second, pair.first);
    }
    return sum_val;
  }

  template <typename VarT>
  const typename LinearCombination<VarT>::TermsVectorType& LinearCombination<VarT>::terms() const {
    return m_terms;
  }

  template <typename VarT>
  typename LinearCombination<VarT>::TermsVectorType::const_iterator LinearCombination<VarT>::begin() const {
    return m_terms.begin();
  }

  template <typename VarT>
  typename LinearCombination<VarT>::TermsVectorType::const_iterator LinearCombination<VarT>::end() const {
    return m_terms.end();
  }

  // Binary multiplication by coefficient (lc * coeff)
  template <typename VarT>
  LinearCombination<VarT> LinearCombination<VarT>::operator*(const Rat& multiplier) const {
    if (multiplier == Rat(0)) {
      return LinearCombination<VarT>();
    }
    LinearCombination<VarT> result;
    result.m_terms =
      m_terms
      | views::transform([&multiplier](const auto& term) {
        return make_pair(term.first, term.second * multiplier);
      })
      | ranges::to<vector>();
    return result;
  }

  // Binary multiplication by coefficient (coeff * lc)
  template <typename VarT>
  LinearCombination<VarT> operator*(const Rat& multiplier, const LinearCombination<VarT>& lc) {
    return lc * multiplier; // Delegate to the other binary operator*
  }


  // Output stream operator
  template <typename VarT>
  std::ostream& operator<<(std::ostream& os, const LinearCombination<VarT>& lc) {
    if (lc.empty()) {
      os << "0";
      return os;
    }

    // Use if constexpr to differentiate output based on is_multiplicative trait
    if constexpr (EquationTraits<VarT>::is_multiplicative) {
      // Multiplicative formatting (for SinOrDist)
      bool first_term_printed = false; // Track if any term has been printed to handle leading '1 / '

      // First pass: print terms with positive coefficients
      for (const auto& [var, coeff] : lc.terms()) {
        if (coeff > static_cast<Rat>(0)) {
          if (first_term_printed) {
            os << " * ";
          }
          if (abs(coeff) == static_cast<Rat>(1)) {
            os << var;
          } else {
            os << var << "^" << abs(coeff);
          }
          first_term_printed = true;
        }
      }

      // Second pass: print terms with negative coefficients (as division)
      for (const auto& [var, coeff] : lc.terms()) {
        if (coeff < static_cast<Rat>(0)) {
          if (!first_term_printed) { // If no positive terms, start with "1 / "
            os << "1"; // Implicit numerator of 1
            first_term_printed = true; // Now something has been printed
          }
          os << " / "; // Always print "/" before negative coefficient terms

          if (abs(coeff) == static_cast<Rat>(1)) {
            os << var;
          } else {
            os << var << "^" << abs(coeff);
          }
        }
      }

      // If nothing was printed (e.g. only zero coefficients, though cleaned up), fall back to "1" for empty multiplicative
      // If it was meant to be 0, it would have been caught by lc.empty() at the beginning.
      // If it was just 1 (like A^0), it should print 1.
      if (!first_term_printed) { // This implies lc was empty, which is already handled, or all coeffs were zero
        os << "1"; // Default for empty product expression
      }

    } else {
      // Additive formatting (for dist, SquaredDist, SlopeAngle, angle)
      bool first_term = true;
      for (const auto& [var, coeff] : lc.terms()) {

        // Handle sign and spacing for terms
        if (!first_term) {
          if (coeff > static_cast<Rat>(0)) {
            os << " + ";
          } else { // coeff < 0
            os << " - ";
          }
        } else if (coeff < static_cast<Rat>(0)) {
          os << "-"; // Print initial minus for the first negative term
        }

        // Print absolute value of coefficient if not 1 or -1
        if (abs(coeff) != static_cast<Rat>(1)) { // Use abs helper
          os << abs(coeff); // Use abs helper
        } else if (first_term && coeff == static_cast<Rat>(-1)) {
          // Already printed '-', so don't print '1'
        }

        // Print variable, unless coefficient is 1 or -1 and we handled it (e.g. "X" vs "1X")
        if (!(abs(coeff) == static_cast<Rat>(1) && // Use abs helper
              (first_term || coeff == static_cast<Rat>(1)))) {
          os << var;
        } else if (abs(coeff) == static_cast<Rat>(1)) { // Use abs helper
          // For +/-1 coefficients, just print the variable if it's not the case already handled above.
          os << var;
        }
        first_term = false;
      }
    }
    return os;
  }

  // Computes a linear combination of two linear combinations: a * lc1 + b * lc2.
  template <typename VarT>
  LinearCombination<VarT>
  LinearCombination<VarT>::linear_combine(const Rat& coeff_this,
                                            const Rat& coeff_other,
                                            const LinearCombination<VarT>& other) {
    if (coeff_this == 0) {
      return coeff_other * other;
    }
    if (coeff_other == 0) {
      return coeff_this * *this;
    }
    return merge_terms(other,
                       [&coeff_this](const Rat& val) { return coeff_this * val; },
                       [&coeff_other](const Rat& val) { return coeff_other * val; },
                       [&coeff_this, &coeff_other](const Rat& lhs, const Rat& rhs) {
                         return coeff_this * lhs + coeff_other * rhs;
                       });
  }

} // namespace Yuclid

BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_LINEAR_COMBINATION, /* empty */,
                      YUCLID_LINEAR_COMBINATION_TYPES)
