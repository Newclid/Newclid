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
#include "ar/reduced_equation.hpp"
#include "statement/statement.hpp"

namespace Yuclid {
  class DDARSolver;
  class Theorem;

  enum class StatementProofState : uint8_t {
    NOT_PROVED, //< The statement isn't proved yet.
    PROVED_BY_REFL, //< The statement is true by reflexivity
    PROVED_BY_ASSUMPTION, //< The statement is an assumption of the problem
    PROVED_NUMERICALLY, //< The statement is a numerical check that was verified
    PROVED_AR_DIST, //< The statement is proved by additive length chasing
    PROVED_AR_SQUARE_DIST, //< The statement is proved by chasing squares of lengths
    PROVED_AR_RATIO, //< The statement is proved by ratio chasing.
    PROVED_AR_ANGLE, //< The statement is proved by angle chasing.
    PROVED_BY_THEOREM //< The statement is proved by applying a theorem.
  };

  /**
   * @brief A (partial progress towards a) proof of a statement.
   */
  class StatementProof {
  public:
    /**
     * @brief Create an empty proof attempt for a statement.
     *
     * The statement is assumed to be already normalized.
     */
    StatementProof(DDARSolver *solver, std::unique_ptr<Statement> &&p);

    /**
     * @brief Mark this statement as proved by assumption.
     */
    void prove_by_assumption();

    /**
     * @brief Query if the statement is proved.
     */
    bool is_proved() const { return m_state != StatementProofState::NOT_PROVED; }

    /** Get the state of the proof. */
    StatementProofState state() const { return m_state; }

    /** Try to make progress on the proof.
     *
     * Tries to make progress in each AR table
     * and see if at least one of them succeeds.
     *
     * For proving statements by deduction rules (a.k.a. theorems),
     * we iterate over the enqueued theorems, not statements.
     */
    void make_progress();

    /**
     * @brief Try to auto prove the statement.
     *
     * Try to prove the statement by reflexivity or numerical checks.
     */
    void initial_progress();

    /** @brief Get the statement we're trying to prove here.
     */
    const std::unique_ptr<Statement> &statement() const;

    /**
     * @brief Return immediate dependencies of the proof.
     *
     * If the statement isn't proved, yields nothing.
     *
     * If it is proved by AR, generates the list of statements
     * that generated the equations with nonzero coefficients
     * in the linear combination.
     *
     * If the statement is proved by a theorem,
     * yields the hypotheses of the theorem.
     *
     * The list is not deduplicated.
     */
    std::vector<StatementProof *> immediate_dependencies() const;

    const std::set<Point> &get_point_dependencies() const {
      return m_point_dependencies;
    }

    /**
     * @brief Mark this statement as proved by theorem no `ind`.
     *
     * Should only be used in `DDARSolver::establish_statement()`.
     */
    void set_theorem(size_t ind);

    std::optional<size_t> theorem() const { return m_theorem; }

    bool needed_for_goal() const { return m_needed_for_goal; }

    void set_needed_for_goal() const;

    void register_as_conclusion(size_t i) { m_theorems_that_imply.push_back(i); }

    const std::vector<size_t> &theorems_that_imply() const { return m_theorems_that_imply; }

    const DDARSolver *get_solver() const { return m_solver; }

    template <typename VarT>
    const ReducedEquation<VarT> *reduced_equation() const;

    template <typename VarT>
    const Rat& equation_coeff() const;

    /**
     * @brief Test if a given proven statement needs aux constructions.
     *
     * Currently, it errs on the side of false negatives by a lot.
     * Namely, it checks if the proof depends on a point greater than
     * all the points needed to state the goal.
     */
    bool needs_aux() const;

    template <typename VarT>
    boost::json::value ar_as_json() const;

  private:
    void set_proved(StatementProofState state);
    /** The parent solver. */
    DDARSolver *m_solver;
    /** @brief The statement we're proving.
     */
    std::unique_ptr<Statement> m_statement;
    std::optional<size_t> m_theorem;
    std::vector<size_t> m_theorems_that_imply;
    std::pair<Rat, ReducedEquation<Dist>*> m_dist_eqn;
    std::pair<Rat, ReducedEquation<SquaredDist>*> m_squared_dist_eqn;
    std::pair<Rat, ReducedEquation<SinOrDist>*> m_sin_or_dist_eqn;
    std::pair<Rat, ReducedEquation<SlopeAngle>*> m_slope_angle_eqn;
    std::set<Point> m_point_dependencies;
    mutable bool m_needed_for_goal{false};
    StatementProofState m_state{StatementProofState::NOT_PROVED};
  };
  
  std::ostream &operator<<(std::ostream &out, const StatementProof &pf);

  std::ostream &operator<<(std::ostream &out, const StatementProofState &s);

  void tag_invoke(boost::json::value_from_tag /*unused*/,
                  boost::json::value& jv,
                  const StatementProof &p);

#define INSTANTIATE_GET_REDUCED_EQUATION(r, prefix, VarT)       \
  prefix template const ReducedEquation<VarT> *                 \
  StatementProof::reduced_equation<VarT>() const;               \
  prefix template const Rat&                                    \
  StatementProof::equation_coeff<VarT>() const;                 \
  prefix template boost::json::value                            \
  StatementProof::ar_as_json<VarT>() const;

  BOOST_PP_SEQ_FOR_EACH(INSTANTIATE_GET_REDUCED_EQUATION, extern, YUCLID_EQN_VARIABLE_TYPES)
}
