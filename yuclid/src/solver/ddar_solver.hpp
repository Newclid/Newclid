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
#include "ar/linear_system.hpp"
#include "type/variable_types.hpp"
#include "typedef.hpp"
#include "config_options.hpp"
#include <boost/preprocessor.hpp>
#include <map>
#include <memory>
#include <set>
#include <vector>

namespace Yuclid {
  class Theorem;
  class StatementProof;
  class TheoremApplication;
  class Statement;
  struct StatementData;
  template <typename VarT> class ReducedEquation;

  /** @brief The main proof state manager class.
   */
  class DDARSolver {
  public:
    /**
     * Go once over all pending theorems & problem's goals and try to prove them.
     *
     * Then query the AR tables for autodetected `ratio_squared_dist`/`aconst` statements and add them.
     *
     * @param max_pt Maximal point that is seen by the algorithm.
     * @return true if proved a new statement;
     * @return false if no new statements were proved.
     */
    bool run_level(const Point &max_pt);

    bool run(size_t max_levels);

    std::ostream &print_proof(std::ostream & /*out*/);
    std::ostream &print_json(std::ostream & /*out*/);

    /** Get the current proof level. */
    size_t get_level() const { return m_level; }

    /**
     * @brief Query if the problem is already solved.
     *
     * This method doesn't iterate over all the goals,
     * just returns the saved value.
     */
    bool get_solved() const { return m_solved; }

    /**
     * Get a theorem using an index.
     */
    const Theorem &theorem_at(size_t i);

    /**
     * @brief Add a statement to the set of pending statements.
     *
     * Normalizes the statement, Computes its `statement::data()`,
     * then generates an empty `StatementProof` for the statement
     * and tries to insert `(p, p_proof)` into the cache of pending statements.
     */
    [[nodiscard]]
    StatementProof *insert_statement(const std::unique_ptr<Statement> &p);

    void insert_ratio_squared_dist_cache(const std::pair<SquaredDist, SquaredDist> &p);

    const std::vector<TheoremApplication> &theorem_applications() const {
      return m_theorem_applications;
    }

    size_t num_theorems() const;

    /**
     * @brief Push an already established statement to the global list of proved facts.
     *
     * To be called by `StatementProof` when it's proved.
     */
    size_t push_established_statement(const StatementProof *pf);

    DDARSolver(const Problem *problem, const Config::Solver *config);

    /**
     * @brief Insert an equation in a table of equations to solve.
     *
     * If equations of this type are disabled in the configuration
     * or if the statement can't be expressed as an equation of this type,
     * then this function does nothing and returns `nullptr`.
     *
     * Otherwise, this function normalizes the equation,
     * then creates an "empty" attempt at solving it,
     * then inserts the pair in the corresponding AR table
     * and returns a pointer to the reduced equation.
     *
     * If an equivalent equation (up to normalization) is already in the table,
     * then this function returns a pointer
     * to the existing `ReducedEquation`.
     *
     * We never erase equations from AR tables,
     * so the pointer stays valid until the parent `DDARSolver` object is destroyed.
     *
     * @todo Also return the coefficient `c` such that `c * eqn.normalize() == eqn`.
     * This will help us produce coefficients for external AR verification.
     *
     * @param[in] p the statement to process;
     * @return a pointer to the `ReducedEquation` for `p->as_equation<VarT>().normalize()`.
     */
    template <typename VarT>
    std::pair<Rat, ReducedEquation<VarT>*>
    insert_equation_for(const std::unique_ptr<Statement> &p);

    /**
     * @brief Add equation for a completed statement proof to the relevant AR table.
     */
    void add_established_equations(StatementProof *pf);

  protected:
    /**
     * @brief Process one theorem.
     *
     * If the theorem is neither proved nor discarded,
     * ask it to update its state.
     *
     * If the new state is "proved",
     * then mark all conclusions as proved by this theorem
     * using `establish_statement` below.
     */
    void advance_theorem(size_t thm_ind);

    /**
     * @brief Add a theorem to the set of pending theorems.
     *
     * Creates a `theorem_application` object for the theorem
     * and adds it to the queue.
     */
    void insert_theorem(Theorem thm);

    /**
     * @brief Note the fact that theorem `thm` is proved and implies `p`.
     *
     * If the statement already proved, returns `false`.
     * If the statement is already provable by AR,
     * mark it as proved by AR and return `true`.
     * Otherwise, mark this statement as proved by this theorem and return `true`.
     *
     * @todo Move completely to the `StatementProof` class.
     * @return true if the statement was just proved (by thm or AR).
     */
    static bool establish_statement(StatementProof *p, size_t thm_index);

    void process_squared_dist_eq();
    void process_ratio_squared_dist();

  private:
    const Problem *m_problem;
    const Config::Solver *m_config;

    /** Current proof level. */
    size_t m_level{0};

    /**
     * @brief Pending and completed theorem proofs.
     *
     * Current, `class Theorem` does not support `operator<`,
     * so we do not deduplicate the theorems.
     * On the one hand, we try not to generate duplicate theorems.
     * On the other hand, this shouldn't be a big issue,
     * since we're deduplicating theorems' hypotheses and conclusions,
     * and making 0 progress on an AR equation
     * is just one lookup in `std::map`.
     */
    std::vector<TheoremApplication> m_theorem_applications;

    /** Pending and completed statement proofs. */
    std::map<StatementData, StatementProof> m_statement_proofs;

    /** The set of statements that are the problem's goals.
     *
     * On every level, we're trying to prove these goals
     * even if they aren't triggered by any theorem.
     */
    std::vector<StatementProof *> m_goals;

    /** Pairs of `squared_dist`s that are found to me proportional. */
    std::set<std::pair<SquaredDist, SquaredDist>> m_ratio_squared_dist_found;

    /** The list of established statements. */
    std::vector<const StatementProof *> m_established_statements;

    /** Is problem solved? */
    bool m_solved{false};

    LinearSystem<Dist> m_system_dist;
    LinearSystem<SquaredDist> m_system_squared_dist;
    LinearSystem<SinOrDist> m_system_sin_or_dist;
    LinearSystem<SlopeAngle> m_system_slope_angle;

    template <typename VarT>
    using eqns_map_type =
      std::unordered_map<Equation<VarT>, ReducedEquation<VarT>,
                         boost::hash<Equation<VarT>>>;

    /** Additive `dist` equations to be reduced. */
    eqns_map_type<Dist> m_eqns_dist;

    /** Additive `squared_dist` equations to be reduced. */
    eqns_map_type<SquaredDist> m_eqns_squared_dist;

    /** Ratio equations to be reduced. */
    eqns_map_type<SinOrDist> m_eqns_sin_or_dist;

    /** Angle equations to be reduced. */
    eqns_map_type<SlopeAngle> m_eqns_slope_angle;
  };

#define INSTANTIATE_INSERT_EQUATION_FOR(r, prefix, VarT)               \
  prefix template std::pair<Rat, ReducedEquation<VarT>*>               \
  DDARSolver::insert_equation_for<VarT>(const std::unique_ptr<Statement> &p);

  BOOST_PP_SEQ_FOR_EACH(INSTANTIATE_INSERT_EQUATION_FOR, extern, YUCLID_EQN_VARIABLE_TYPES)
}
