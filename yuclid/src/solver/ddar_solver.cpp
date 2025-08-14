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
#include "solver/ddar_solver.hpp"
#include "ar/equation.hpp"
#include "ar/linear_system.hpp"
#include "solver/theorem_application.hpp"
#include "solver/statement_proof.hpp"
#include "problem.hpp"
#include "ar/reduced_equation.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "statement/squared_dist_eq.hpp"
#include "numbers/util.hpp"
#include "config_options.hpp"
#include "matcher.hpp"
#include "type/dist.hpp"
#include "type/sin_or_dist.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"
#include "type/variable_types.hpp"
#include "typedef.hpp"

#include <boost/json/array.hpp>
#include <boost/json/serialize.hpp>
#include <boost/json/value.hpp>
#include <boost/json/value_from.hpp>
#include <boost/log/trivial.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <cassert>
#include <cstddef>
#include <format>
#include <map>
#include <memory>
#include <optional>
#include <ostream>
#include <sstream>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <vector>

using namespace std;

namespace Yuclid {

  DDARSolver::DDARSolver(const Problem *problem, const Config::Solver *config) :
    m_problem(problem), m_config(config) {
    BOOST_LOG_TRIVIAL(info) << "Adding `by assumption` theorems";
    // Add problem's hypotheses.
    for (const auto &hyp : problem->hypotheses()) {
      insert_statement(hyp->normalize())->prove_by_assumption();
    }

    BOOST_LOG_TRIVIAL(info) << "Matching theorems";
    // Enqueue all numerically matching theorems.
    TheoremMatcher matcher(m_problem, m_config);
    for (const auto &thm : matcher.theorems()) {
      insert_theorem(thm.clone());
    }

    if (!problem->goals().empty()) {
      BOOST_LOG_TRIVIAL(info) << "Adding problem's goals";
      for (const auto &p : problem->goals()) {
        m_goals.push_back(insert_statement(p));
      }
    }
  }

  bool DDARSolver::run_level(const Point &max_pt) {
    // Store the number of established statements before this level.
    size_t num_statements = m_established_statements.size();
    BOOST_LOG_TRIVIAL(info) << format("Running level {}, starting with {} statements",
                                      m_level, num_statements);
    // Try to make progress on each theorem.
    size_t const n = m_theorem_applications.size();
    for (size_t i = 0; i < n; ++ i) {
      if (m_theorem_applications[i].get_max_point() <= max_pt) {
        advance_theorem(i);
      }
    }

    process_squared_dist_eq();
    process_ratio_squared_dist();

    if (!m_problem->goals().empty()) {
      bool b = true;
      for (auto *g : m_goals) {
        // Only count towards `res` if the goal isn't already proved.
        if (!g->is_proved()) {
          g->make_progress();
          if (!g->is_proved()) {
            b = false;
          }
        }
      }
      m_solved = b;
    }

    BOOST_LOG_TRIVIAL(info) << format("Proved {} new facts, {} total",
                                      m_established_statements.size() - num_statements,
                                      m_established_statements.size());
    ++ m_level;
    return num_statements < m_established_statements.size();
  }

  ostream &DDARSolver::print_proof(ostream &out) {
    boost::json::array goals;
    for (auto *goal : m_goals) {
      goal->set_needed_for_goal();
    }

    for (const auto *proof : m_established_statements) {
      if (m_goals.empty() || proof->needed_for_goal()) {
        out << *proof << '\n';
      }
    }

    return out;
  }

  ostream &DDARSolver::print_json(ostream &out) {
    boost::json::array goals;
    for (auto *goal : m_goals) {
      goal->set_needed_for_goal();
    }
    boost::json::array all_deductions;
    boost::json::array deductions_for_goal;
    for (const auto *proof : m_established_statements) {
      boost::json::value const val = boost::json::value_from(*proof);
      all_deductions.push_back(val);
      if (proof->needed_for_goal()) {
        deductions_for_goal.push_back(val);
      }
    }
    boost::json::value const val = {
      {"status", m_solved ? "solved" : "saturated"},
      {"goals", goals},
      {"deductions_for_goal", deductions_for_goal},
      {"all_deductions", all_deductions}
    };
    out << boost::json::serialize(val);
    return out;
  }


  bool DDARSolver::run(size_t max_levels) {
    if (m_problem->goals().empty()) {
      for (Point const max_pt : m_problem->all_points()) {
        for (size_t i = 0; i < max_levels; ++ i) {
          if (!run_level(max_pt)) {
            break;
          }
        }
      }
      m_solved = true;
    } else {
      auto const max_pt = Point(m_problem->num_points() - 1, m_problem);
      for (size_t i = 0; i < max_levels; ++ i) {
        if (!run_level(max_pt)) {
          BOOST_LOG_TRIVIAL(info) << "No new statements, stop trying";
          break;
        }
        if (m_solved) {
          BOOST_LOG_TRIVIAL(info) << "Solved the problem";
          break;
        }
      }
    }
    return m_solved;
  }

  template <typename VarT>
  pair<Rat, ReducedEquation<VarT>*>
  DDARSolver::insert_equation_for(const std::unique_ptr<Statement> &p) {
    if constexpr (is_same_v<VarT, Dist> || is_same_v<VarT, SquaredDist>) {
      if (!m_config->ar_enabled<VarT>()) {
        return {1, nullptr};
      }
    }
    optional<Equation<VarT>> opt_eqn = p->as_equation<VarT>();
    if (!opt_eqn.has_value()) {
      return {1, nullptr};
    }
    eqns_map_type<VarT> *eqns = nullptr;
    LinearSystem<VarT> *sys = nullptr;
    if constexpr (is_same_v<VarT, Dist>) {
      eqns = &m_eqns_dist;
      sys = &m_system_dist;
    } else if constexpr (is_same_v<VarT, SquaredDist>) {
      eqns = &m_eqns_squared_dist;
      sys = &m_system_squared_dist;
    } else if constexpr (is_same_v<VarT, SinOrDist>) {
      eqns = &m_eqns_sin_or_dist;
      sys = &m_system_sin_or_dist;
    } else if constexpr (is_same_v<VarT, SlopeAngle>) {
      eqns = &m_eqns_slope_angle;
      sys = &m_system_slope_angle;
    } else {
      static_assert(false, "Variable type is not supported");
    }
    auto const [coeff, eqn] = opt_eqn.value().normalize();
    auto red_eq = ReducedEquation(eqn, sys);
    return {coeff, &(eqns->insert({eqn, red_eq}).first->second)};
  }

  void DDARSolver::add_established_equations(StatementProof *pf) {
    m_system_dist.add_reduced_equation(pf);
    m_system_squared_dist.add_reduced_equation(pf);
    m_system_sin_or_dist.add_reduced_equation(pf);
    m_system_slope_angle.add_reduced_equation(pf);
  }

  void DDARSolver::advance_theorem(size_t ind) {
    auto &thm = m_theorem_applications.at(ind);
    if (thm.state() != TheoremApplicationState::PENDING) {
      return;
    }
    thm.advance_proof();
    if (thm.state() == TheoremApplicationState::PROVED) {
      for (auto *p : thm.conclusions()) {
        establish_statement(p, ind);
      }
    }
  }

  void DDARSolver::process_ratio_squared_dist() {
    for (const auto& r : m_system_dist.generate_suspected_ratio_squared_dist()) {
      if (m_ratio_squared_dist_found.contains
          (make_pair(r.left_squared_dist(), r.right_squared_dist()))) {
        continue;
      }
      if (!r.check_numerically()) {
        continue;
      }
      auto opt_eq = r.as_equation<Dist>();
      if (!opt_eq.has_value()) {
        continue;
      }
      const auto& eq = opt_eq.value();
      ReducedEquation<Dist> red_eq(eq, &m_system_dist);
      red_eq.reduce();
      if (red_eq.is_solved()) {
        auto *pf = insert_statement(r.normalize2());
        pf->make_progress();
      }
    }

    for (const auto& r : m_system_squared_dist.generate_suspected_ratio_squared_dist()) {
      if (m_ratio_squared_dist_found.contains
          (make_pair(r.left_squared_dist(), r.right_squared_dist()))) {
        continue;
      }
      if (!r.check_numerically()) {
        continue;
      }
      auto opt_eq = r.as_equation<SquaredDist>();
      if (!opt_eq.has_value()) {
        continue;
      }
      const auto& eq = opt_eq.value();
      ReducedEquation<SquaredDist> red_eq(eq, &m_system_squared_dist);
      red_eq.reduce();
      if (red_eq.is_solved()) {
        auto *pf = insert_statement(r.normalize2());
        pf->make_progress();
      }
    }

    for (const auto& r : m_system_sin_or_dist.generate_suspected_ratio_squared_dist()) {
      if (m_ratio_squared_dist_found.contains
          (make_pair(r.left_squared_dist(), r.right_squared_dist()))) {
        continue;
      }
      auto opt_eq = r.as_equation<SinOrDist>();
      if (!opt_eq.has_value()) {
        continue;
      }
      const auto& eq = opt_eq.value();
      ReducedEquation<SinOrDist> red_eq(eq, &m_system_sin_or_dist);
      red_eq.reduce();
      // In this case we check whether `ab^2 / cd^2 = 1` reduces to `1 = r` for some `r`.
      // This means `ab^2 : cd^2 = 1 / r.
      if (red_eq.remainder().lhs().empty()) {
        const NNRat c = red_eq.remainder().rhs().as_nnrat();
        if (c != NNRat(0)) [[likely]] {
          auto *pf = insert_statement
            (RatioSquaredDist(r.left_squared_dist(),
                                r.right_squared_dist(),
                                NNRat(1) / c).normalize2());
          pf->make_progress();
        }
      }
    }
  }

  void DDARSolver::process_squared_dist_eq() {
    auto f = [this](const unique_ptr<Statement> &p) {
      auto *pf = this->insert_statement(p);
      pf->make_progress();
      if (!pf->is_proved()) {
        throw runtime_error("Failed to prove a generated `squared_dist_eq`");
      }
    };
    for (const auto &v : m_system_dist.new_found_variables()) {
      Rat const r = m_system_dist.echelon_form().find(v)->second.rhs().rhs();
      if (r != Rat(0)) [[likely]] {
        f(make_unique<SquaredDistEq>(SquaredDist(v), rat2nnrat(r * r)));
      } else {
        throw runtime_error("Found zero distance");
      }
    }
    m_system_dist.clear_new_found_variables();
    for (const auto &v : m_system_squared_dist.new_found_variables()) {
      Rat const r = m_system_squared_dist.echelon_form().find(v)->second.rhs().rhs();
      if (r != Rat(0)) [[likely]] {
        f(make_unique<SquaredDistEq>(v, rat2nnrat(r)));
      } else {
        ostringstream err;
        err << "Found zero squared distance: " << v << " = 0";
        throw runtime_error(err.str());
      }
    }
    m_system_squared_dist.clear_new_found_variables();
    for (const auto &v : m_system_sin_or_dist.new_found_variables()) {
      // Skip found `\sin² α = r`. We'll match well-known values in theorems.
      if (v.is_sin()) {
        continue;
      }

      const NNRat r =
        m_system_sin_or_dist.echelon_form().find(v)->second.rhs().rhs().as_nnrat();
      if (r != NNRat(0)) [[likely]] {
        f(make_unique<SquaredDistEq>(v.get_squared_dist(), r));
      }
    }
    m_system_sin_or_dist.clear_new_found_variables();
  }

  size_t DDARSolver::push_established_statement(const StatementProof *pf) {
    size_t const res = m_established_statements.size();
    m_established_statements.push_back(pf);
    return res;
  }

  void DDARSolver::insert_theorem(Theorem thm) {
    size_t const size = m_theorem_applications.size();
    m_theorem_applications.emplace_back(this, std::move(thm), size);
  }

  StatementProof *DDARSolver::insert_statement(const std::unique_ptr<Statement> &p) {
    auto val = p->normalize();
    auto key = val->data();
    auto [iter, success] = m_statement_proofs.insert({
        key, StatementProof(this, std::move(val))
      });
    if (success) {
      iter->second.initial_progress();
    }
    return &(iter->second);
  }

  size_t DDARSolver::num_theorems() const {
    return m_theorem_applications.size();
  }

  void DDARSolver::insert_ratio_squared_dist_cache(const pair<SquaredDist, SquaredDist> &p) {
    m_ratio_squared_dist_found.insert(p);
  }

  bool DDARSolver::establish_statement(StatementProof *pf, size_t thm_index) {
    if (pf->is_proved()) {
      return false;
    }
    pf->make_progress();
    if (!pf->is_proved()) {
      pf->set_theorem(thm_index);
    }
    return true;
  }

  BOOST_PP_SEQ_FOR_EACH(INSTANTIATE_INSERT_EQUATION_FOR, /* empty */, YUCLID_EQN_VARIABLE_TYPES)
}
