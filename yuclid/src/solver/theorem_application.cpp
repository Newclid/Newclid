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
#include "solver/theorem_application.hpp"
#include "solver/ddar_solver.hpp"
#include "solver/statement_proof.hpp"
#include <cstddef>
#include <ostream>
#include <utility>

namespace Yuclid {
  TheoremApplication::TheoremApplication(DDARSolver *solver, Theorem &&theorem, size_t k) :
    m_theorem(std::move(theorem)),
    m_max_point(m_theorem.max_point())
  {
    for (const auto &p : m_theorem.hypotheses()) {
      m_hypotheses.push_back(solver->insert_statement(p));
    }
    for (const auto &p : m_theorem.conclusions()) {
      m_conclusions.push_back(solver->insert_statement(p));
    }
    for (auto *p : m_conclusions) {
      p->register_as_conclusion(k);
    }
  }

  void TheoremApplication::advance_proof() {
    if (m_state != TheoremApplicationState::PENDING) {
      return;
    }

    bool conclusions_proved = true;

    for (auto *pf : m_conclusions) {
      pf->make_progress();
      conclusions_proved = conclusions_proved && pf->is_proved();
    }

    if (conclusions_proved) {
      m_state = TheoremApplicationState::DISCARDED;
      return;
    }

    bool hypotheses_proved = true;
    for (auto *pf : m_hypotheses) {
      pf->make_progress();
      if (!pf->is_proved()) {
        hypotheses_proved = false;
        break;
      }
    }
    if (hypotheses_proved) {
      m_state = TheoremApplicationState::PROVED;
    }
  }

  std::ostream &operator<<(std::ostream &out, const TheoremApplicationState &st) {
    switch (st) {
    case TheoremApplicationState::DISCARDED:
      return out << "discarded";
    case TheoremApplicationState::PENDING:
      return out << "pending";
    case TheoremApplicationState::PROVED:
      return out << "proved";
    }
    return out;
  }

}
