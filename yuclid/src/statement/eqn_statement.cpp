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
#include "eqn_statement.hpp"
#include <algorithm>
#include <boost/preprocessor/seq/for_each.hpp>
#include <cstddef>
#include <memory>
#include <optional>
#include <ostream>
#include <string>
#include <type_traits>
#include <typeinfo> // For typeid (name())
#include <stdexcept> // For std::invalid_argument
#include "ar/equation.hpp"
#include "ar/equation_traits.hpp"
#include "ar/linear_combination.hpp"
#include <variant>
#include <vector>
#include "config_options.hpp"
#include "numbers/posreal.hpp"
#include "statement/statement.hpp"
#include "type/angle.hpp"
#include "type/dist.hpp"
#include "type/point.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {

  template<typename VarT>
  EqnStatement<VarT>::EqnStatement(const vector<statement_arg>& args) {
    if (args.empty()) {
      throw invalid_argument("EqnStatement constructor: arguments list cannot be empty. Expected: coefficients, terms, then RHS.");
    }

    // The last element is the RHS.
    if (!holds_alternative<typename EquationTraits<VarT>::RHSType>(args.back())) {
      throw invalid_argument("EqnStatement constructor: last argument must be of the equation's RHS type.");
    }
    typename EquationTraits<VarT>::RHSType const rhs = get<typename EquationTraits<VarT>::RHSType>(args.back());
    LinearCombination<VarT> lhs;

    // Iterate through args up to the second-to-last element (as last is RHS)
    for (size_t i = 0; i < args.size() - 1; i += 2) {
      if (i + 1 >= args.size() - 1) { // Check if we have both coefficient and term
        throw invalid_argument("EqnStatement constructor: malformed arguments. Expected pairs of (coefficient, term) followed by RHS.");
      }
      if (!holds_alternative<Rat>(args[i])) {
        throw invalid_argument("EqnStatement constructor: argument at index " + to_string(i) + " must be a coefficient.");
      }
      if (!holds_alternative<VarT>(args[i+1])) {
        throw invalid_argument("EqnStatement constructor: argument at index " + to_string(i+1) + " must be of the variable type.");
      }
      Rat const coeff = get<Rat>(args[i]);
      VarT term = get<VarT>(args[i+1]);
      lhs += LinearCombination<VarT>(term, coeff);
    }

    if ((args.size() - 1) % 2 != 0) { // Check if there's an odd number of elements for terms/coeffs
      throw invalid_argument("EqnStatement constructor: malformed arguments. Expected pairs of (coefficient, term) followed by RHS.");
    }

    m_eqn = Equation<VarT>(lhs, rhs);
  }

  template<typename VarT>
  EqnStatement<VarT>::EqnStatement(const Equation<VarT> &data) : m_eqn(data) {}

  template<typename VarT>
  EqnStatement<VarT>::EqnStatement(Equation<VarT> &&data) : m_eqn(std::move(data)) {}

  template<typename VarT>
  string EqnStatement<VarT>::name() const {
    return "equation_" + string(typeid(VarT).name());
  }

  template<typename VarT>
  vector<Point> EqnStatement<VarT>::points() const {
    vector<Point> res;
    res.reserve(3 * m_eqn.lhs().terms().size());
    for (const auto& term_pair : m_eqn.lhs().terms()) {
      for (const auto& point : term_pair.first.points()) {
        res.push_back(point);
      }
    }
    return res;
  }

  template<typename VarT>
  unique_ptr<Statement> EqnStatement<VarT>::normalize() const {
    return make_unique<EqnStatement<VarT>>(m_eqn.normalize().second);
  }

  template<typename VarT>
  bool EqnStatement<VarT>::check_nondegen() const {
    if constexpr (is_same_v<VarT, Dist> || is_same_v<VarT, SquaredDist>) {
      return true;
    } else {
      return ranges::all_of(m_eqn.lhs().terms(), [](const auto &term_pair) {
        return term_pair.first.check_nondegen();
      });
    }
  }

  template<typename VarT>
  bool EqnStatement<VarT>::check_equations() const {
    return m_eqn.check_numerically();
  }

  template<typename VarT>
  optional<Equation<Dist>> EqnStatement<VarT>::as_equation_dist() const {
    if constexpr (std::is_same_v<VarT, Dist>) {
      return m_eqn;
    } else {
      return nullopt;
    }
  }

  template<typename VarT>
  optional<Equation<SquaredDist>> EqnStatement<VarT>::as_equation_squared_dist() const {
    if constexpr (std::is_same_v<VarT, SquaredDist>) {
      return m_eqn;
    } else {
      return nullopt;
    }
  }

  template<typename VarT>
  optional<Equation<SlopeAngle>> EqnStatement<VarT>::as_equation_slope_angle() const {
    if constexpr (std::is_same_v<VarT, Angle>) {
      return angle_equation_to_slope_angle_equation(m_eqn);
    } else {
      return nullopt;
    }
  }

  template<typename VarT>
  optional<Equation<SinOrDist>> EqnStatement<VarT>::as_equation_sin_or_dist() const {
    if constexpr (std::is_same_v<VarT, SinOrDist>) {
      return m_eqn;
    } else {
      return nullopt;
    }
  }

  template<typename VarT>
  vector<statement_arg> EqnStatement<VarT>::args() const {
    vector<statement_arg> result_args;
    for (const auto& pair : m_eqn.lhs().terms()) {
      result_args.push_back(pair.second); // Coefficient
      result_args.push_back(statement_arg(in_place_type<VarT>, pair.first));  // Term
    }
    result_args.push_back(statement_arg(m_eqn.rhs())); // RHS
    return result_args;
  }

  template<typename VarT>
  unique_ptr<Statement> EqnStatement<VarT>::clone() const {
    return make_unique<EqnStatement<VarT>>(*this); // Implementation of clone()
  }


  template<typename VarT>
  ostream &EqnStatement<VarT>::print(ostream &out) const {
    return out << m_eqn;
  }

  BOOST_PP_SEQ_FOR_EACH(YUCLID_INSTANTIATE_EQN_STATEMENT, /* empty */,  \
                        YUCLID_STATEMENT_VARIABLE_TYPES)

} // namespace Yuclid
