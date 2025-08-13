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
#include "ar/reduced_equation.hpp"
#include "solver/statement_proof.hpp"
#include "numbers/util.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "solver/ddar_solver.hpp"
#include "theorem.hpp"
#include "solver/theorem_application.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "type/variable_types.hpp"
#include "typedef.hpp"

#include <algorithm>
#include <boost/json/array.hpp>
#include <boost/json/conversion.hpp>
#include <boost/json/object.hpp>
#include <boost/json/value.hpp>
#include <boost/json/value_from.hpp>
#include <boost/log/trivial.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <cassert>
#include <cstddef>
#include <memory>
#include <optional>
#include <ostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

using namespace std;

namespace Yuclid {

  using enum StatementProofState;

  StatementProof::StatementProof(DDARSolver *solver, std::unique_ptr<Statement> &&p) :
    m_solver(solver),
    m_statement(std::move(p)),
    m_dist_eqn(m_solver->insert_equation_for<Dist>(m_statement)),
    m_squared_dist_eqn(m_solver->insert_equation_for<SquaredDist>(m_statement)),
    m_sin_or_dist_eqn(m_solver->insert_equation_for<SinOrDist>(m_statement)),
    m_slope_angle_eqn(m_solver->insert_equation_for<SlopeAngle>(m_statement))
  {}

  void StatementProof::prove_by_assumption() {
    set_proved(PROVED_BY_ASSUMPTION);
  }

  void StatementProof::initial_progress() {
    if (m_statement->is_refl()) {
      set_proved(PROVED_BY_REFL);
      return;
    }
    if (m_statement->numerical_only()) {
      if (m_statement->check_numerically()) [[likely]] {
        set_proved(PROVED_NUMERICALLY);
        return;
      }
      BOOST_LOG_TRIVIAL(error) << *m_statement;
      for (const auto &p : m_statement->points()) {
        BOOST_LOG_TRIVIAL(error) << p << " " << p.x() << " " << p.y();
      }
      throw runtime_error("Tried to add a numerical only check that doesn't work");
    }
  }

  void StatementProof::make_progress() {
    if (m_state != NOT_PROVED) {
      return;
    }
    if (m_dist_eqn.second != nullptr) {
      m_dist_eqn.second->reduce();
      if (m_dist_eqn.second->is_solved()) {
        set_proved(PROVED_AR_DIST);
        return;
      }
    }
    if (m_squared_dist_eqn.second != nullptr) {
      m_squared_dist_eqn.second->reduce();
      if (m_squared_dist_eqn.second->is_solved()) {
        set_proved(PROVED_AR_SQUARE_DIST);
        return;
      }
    }
    if (m_sin_or_dist_eqn.second != nullptr) {
      m_sin_or_dist_eqn.second->reduce();
      if (m_sin_or_dist_eqn.second->is_solved()) {
        set_proved(PROVED_AR_RATIO);
        return;
      }
    }
    if (m_slope_angle_eqn.second != nullptr) {
      m_slope_angle_eqn.second->reduce();
      if (m_slope_angle_eqn.second->is_solved()) {
        set_proved(PROVED_AR_ANGLE);
        return;
      }
    }
  }

  void StatementProof::set_theorem(size_t ind) {
    m_theorem = ind;
    set_proved(PROVED_BY_THEOREM);
  }


  const std::unique_ptr<Statement> &StatementProof::statement() const {
    return m_statement;
  }

  template <typename VarT>
  const ReducedEquation<VarT> *StatementProof::reduced_equation() const {
    if constexpr (is_same_v<VarT, Dist>) {
      return m_dist_eqn.second;
    } else if constexpr (is_same_v<VarT, SquaredDist>) {
      return m_squared_dist_eqn.second;
    } else if constexpr (is_same_v<VarT, SinOrDist>) {
      return m_sin_or_dist_eqn.second;
    } else if constexpr (is_same_v<VarT, SlopeAngle>) {
      return m_slope_angle_eqn.second;
    } else {
      static_assert("Unsupported variable type");
    }
  }

  template <typename VarT>
  const Rat& StatementProof::equation_coeff() const {
    if constexpr (is_same_v<VarT, Dist>) {
      return m_dist_eqn.first;
    } else if constexpr (is_same_v<VarT, SquaredDist>) {
      return m_squared_dist_eqn.first;
    } else if constexpr (is_same_v<VarT, SinOrDist>) {
      return m_sin_or_dist_eqn.first;
    } else if constexpr (is_same_v<VarT, SlopeAngle>) {
      return m_slope_angle_eqn.first;
    } else {
      static_assert("Unsupported variable type");
    }
  }


  void StatementProof::set_proved(StatementProofState state) {
    if (state == NOT_PROVED) {
      return;
    }
    if (m_state != NOT_PROVED) {
      throw logic_error("Trying to re-prove a statement");
    }

    m_state = state;
    m_solver->push_established_statement(this);

    if (!m_statement->check_numerically()) {
      BOOST_LOG_TRIVIAL(error) << "Established a numerically incorrect statement " << *this;
    }

    optional<RatioSquaredDist> opt_r = m_statement->as_ratio_squared_dist();
    if (opt_r.has_value()) {
      m_solver->insert_ratio_squared_dist_cache
        (minmax(opt_r.value().left_squared_dist(),
                opt_r.value().right_squared_dist()));
    }

    if (m_dist_eqn.second != nullptr) {
      m_dist_eqn.second->reduce();
    }
    if (m_squared_dist_eqn.second != nullptr) {
      m_squared_dist_eqn.second->reduce();
    }
    if (m_sin_or_dist_eqn.second != nullptr) {
      m_sin_or_dist_eqn.second->reduce();
    }
    if (m_slope_angle_eqn.second != nullptr) {
      m_slope_angle_eqn.second->reduce();
    }

    m_solver->add_established_equations(this);

    for (const auto &dep : immediate_dependencies()) {
      for (Point const pt : dep->m_point_dependencies) {
        m_point_dependencies.insert(pt);
      }
    }
    for (Point const pt : m_statement->points()) {
      m_point_dependencies.insert(pt);
    }
  }

  void StatementProof::set_needed_for_goal() const {
    if (m_needed_for_goal) {
      return;
    }
    m_needed_for_goal = true;
    for (const auto &pf : immediate_dependencies()) {
      pf->set_needed_for_goal();
    }
  }

  bool StatementProof::needs_aux() const {
    assert(m_state != NOT_PROVED);
    Point max_pt = ranges::max(m_statement->points());
    return ranges::any_of(m_point_dependencies,
                          [&max_pt](const Point &pt) {
                            return pt > max_pt;
                          });
  }

  std::vector<StatementProof *> StatementProof::immediate_dependencies() const {
    switch (m_state) {
    case PROVED_BY_REFL:
    case PROVED_NUMERICALLY:
    case PROVED_BY_ASSUMPTION:
    case NOT_PROVED:
      return {};
    case PROVED_BY_THEOREM:
      return m_solver->theorem_applications()[m_theorem.value()].hypotheses();
    case PROVED_AR_DIST:
      return m_dist_eqn.second->statement_dependencies() | ranges::to<vector>();
    case PROVED_AR_SQUARE_DIST:
      return m_squared_dist_eqn.second->statement_dependencies() | ranges::to<vector>();
    case PROVED_AR_RATIO:
      return m_sin_or_dist_eqn.second->statement_dependencies() | ranges::to<vector>();
      break;
    case PROVED_AR_ANGLE:
      return m_slope_angle_eqn.second->statement_dependencies() | ranges::to<vector>();
    }
    return {};
  }

  std::ostream &operator<<(std::ostream &out, const StatementProof &pf) {
    bool first_dep = true;
    switch (pf.state()) {
    case PROVED_BY_THEOREM:
      out << pf.get_solver()->theorem_applications()[pf.theorem().value()].theorem();
      break;
    case PROVED_BY_REFL:
    case PROVED_BY_ASSUMPTION:
    case PROVED_NUMERICALLY:
      out << pf.state() << " " << *(pf.statement());
      break;
    case PROVED_AR_DIST:
    case PROVED_AR_SQUARE_DIST:
    case PROVED_AR_ANGLE:
    case PROVED_AR_RATIO:
      out << "From ";
      for (const auto &dep : pf.immediate_dependencies()) {
        if (first_dep) {
          first_dep = false;
        } else {
          out << ", ";
        }
        out << *(dep->statement());
      }
      out << " " << pf.state() << " " << *(pf.statement());
      break;
    case NOT_PROVED:
      out << *(pf.statement()) << ": " << "not proved";
      BOOST_LOG_TRIVIAL(info) << "Would follow from these theorems:";
      for (auto k : pf.theorems_that_imply()) {
        BOOST_LOG_TRIVIAL(info) << pf.get_solver()->theorem_applications()[k].theorem()
                                << " (" << pf.get_solver()->theorem_applications()[k].state() << ")";
      }
    }
    return out;
  }

  std::ostream &operator<<(std::ostream &out, const StatementProofState &s) {
    switch (s) {
    case NOT_PROVED:
      return out << "not proved";
    case PROVED_BY_REFL:
      return out << "by reflexivity";
    case PROVED_BY_ASSUMPTION:
      return out << "by assumption";
    case PROVED_NUMERICALLY:
      return out << "verified numerically";
    case PROVED_AR_DIST:
      return out << "by length chasing";
    case PROVED_AR_SQUARE_DIST:
      return out << "by squared length chasing";
    case PROVED_AR_RATIO:
      return out << "by ratio chasing";
    case PROVED_AR_ANGLE:
      return out << "by angle chasing";
    case PROVED_BY_THEOREM:
      return out << "by theorem";
    }
    return out;
  }

  template <typename VarT>
  boost::json::value StatementProof::ar_as_json() const {
    namespace json = boost::json;
    const string ar_reason = []() {
      if constexpr (is_same_v<VarT, Dist>) {
        return "length chasing";
      }
      if constexpr (is_same_v<VarT, SquaredDist>) {
        return "squared lengths chasing";
      }
      if constexpr (is_same_v<VarT, SinOrDist>) {
        return "ratio chasing";
      }
      if constexpr (is_same_v<VarT, SlopeAngle>) {
        return "angle chasing";
      }
    }();
    json::array hypotheses;
    const Rat& coeff_rhs = equation_coeff<VarT>();
    const ReducedEquation<VarT> *red_eq = reduced_equation<VarT>();
    assert(red_eq != nullptr);
    for (const auto& [ind, coeff] : red_eq->linear_combination().lhs()) {
      const auto [eqn, prf] = red_eq->linear_system()->pair_at(ind);
      json::object obj = prf->statement()->to_json();
      obj.emplace("coeff",
                  rat2string(coeff * prf->template equation_coeff<VarT>()
                             / coeff_rhs));
      json::object lhs_terms;
      const auto dep_eqn =
        prf->statement()->template as_equation<VarT>().value();
      for (const auto& [var, var_coeff] : dep_eqn.lhs()) {
        ostringstream var_name;
        var_name << var;
        lhs_terms.emplace(var_name.str(), rat2string(var_coeff));
      }
      obj.emplace("lhs_terms", lhs_terms);
      hypotheses.push_back(obj);
    }
    json::object obj = statement()->to_json();
    json::object lhs_terms;
    const auto dep_eqn =
      statement()->template as_equation<VarT>().value();
    for (const auto& [var, var_coeff] : dep_eqn.lhs()) {
      ostringstream var_name;
      var_name << var;
      lhs_terms.emplace(var_name.str(), rat2string(var_coeff));
    }
    obj.emplace("lhs_terms", lhs_terms);
    json::array conclusions;
    conclusions.push_back(obj);
    return {
      {"deduction_type", "ar"},
      {"ar_reason", ar_reason},
      {"point_deps", json::value_from(get_point_dependencies())},
      {"assumptions", hypotheses},
      {"assertions", conclusions}
    };
  }

  void tag_invoke(boost::json::value_from_tag /*unused*/, boost::json::value& jv,
                  const StatementProof &p) {
    namespace json = boost::json;
    string name;
    string deduction_type;
    switch(p.state()) {
    case NOT_PROVED:
      name = "not proved";
      deduction_type = "none";
      break;
    case PROVED_BY_REFL:
      name = "by reflexivity";
      deduction_type = "refl";
      break;
    case PROVED_BY_ASSUMPTION:
      name = "By construction";
      deduction_type = "rule";
      break;
    case PROVED_NUMERICALLY:
      name = "Numerical check";
      deduction_type = "num";
      break;
    case PROVED_AR_DIST:
      jv = p.ar_as_json<Dist>();
      return;
    case PROVED_AR_SQUARE_DIST:
      jv = p.ar_as_json<SquaredDist>();
      return;
    case PROVED_AR_RATIO:
      jv = p.ar_as_json<SinOrDist>();
      return;
    case PROVED_AR_ANGLE:
      jv = p.ar_as_json<SlopeAngle>();
      return;
    case PROVED_BY_THEOREM:
      name = p.get_solver()->theorem_applications()[p.theorem().value()].theorem().newclid_rule();
      deduction_type = "rule";
    }
    json::array hypotheses;
    json::array conclusions;
    for (auto *dep : p.immediate_dependencies()) {
      hypotheses.emplace_back(json::value_from(dep->statement()));
    }
    conclusions.emplace_back(json::value_from(p.statement()));
    jv = {
      {"deduction_type", deduction_type},
      {(deduction_type == "ar" ? "ar_reason" : "newclid_rule"), name},
      {"point_deps", json::value_from(p.get_point_dependencies())},
      {"assumptions", hypotheses},
      {"assertions", conclusions}
    };
  }

  BOOST_PP_SEQ_FOR_EACH(INSTANTIATE_GET_REDUCED_EQUATION, /* empty */, YUCLID_EQN_VARIABLE_TYPES)
}
