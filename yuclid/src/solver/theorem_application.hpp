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
#include "theorem.hpp"
#include "statement/statement.hpp"

namespace Yuclid {
  class DDARSolver;

  enum class TheoremApplicationState : uint8_t {
    /** The theorem is not proved yet. */
    PENDING,
    /** The theorem is already proved. */
    PROVED,
    /** The theorem was discarded, because all of its conclusions were proved
     * before we proved all the hypotheses.
     */
    DISCARDED,
  };

  class TheoremApplication {
  public:

    /**
     * @brief Initialize a `theorem_application` for a given theorem.
     *
     * Add hypotheses and conclusions to `statements`, if they aren't there yet,
     * and store iterators pointing to these statements.
     */
    TheoremApplication(DDARSolver *solver, Theorem &&theorem, size_t k);

    /**
     * @brief Try to advance theorem's proof.
     *
     * If the theorem is pending,
     * - try to prove all the theorem's asertions using AR;
     * - if all the conclusions are proved, discard this theorem;
     * - otherwise, try to prove all the theorem's hypotheses using AR;
     * - if all hypotheses are proved, then mark the state as proved.
     */
    void advance_proof();

    [[nodiscard]] TheoremApplicationState state() const { return m_state; }

    [[nodiscard]] const std::vector<StatementProof *> &hypotheses() const
    { return m_hypotheses; }

    [[nodiscard]] const std::vector<StatementProof *> &conclusions() const
    { return m_conclusions; }

    [[nodiscard]] const Theorem &theorem() const { return m_theorem; }

    [[nodiscard]] const Point &get_max_point() const { return m_max_point; }

  private:
    /** The theorem we're trying to apply. */
    Theorem m_theorem;
    /** Current state of the proof. */
    TheoremApplicationState m_state{TheoremApplicationState::PENDING};
    /** Iterators pointing to the partial proofs of the hypotheses. */
    std::vector<StatementProof *> m_hypotheses;
    /** Iterators pointing to the partial proofs of the conclusions. */
    std::vector<StatementProof *> m_conclusions;
    /** Maximal point used in the theorem. */
    Point m_max_point;
  };

  std::ostream &operator<<(std::ostream &out, const TheoremApplicationState &st);

}
