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
#include "para.hpp"
#include "ar/equation.hpp"
#include "numbers/add_circle.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "type/slope_angle.hpp"
#include "typedef.hpp"
#include <memory>
#include <optional>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  Parallel::Parallel(SlopeAngle s1, SlopeAngle s2) : m_left(s1), m_right(s2) {}

  string Parallel::name() const { return "para"; }

  vector<Point> Parallel::points() const {
    return {
      m_left.left(), m_left.right(),
      m_right.left(), m_right.right()
    };
  }

  unique_ptr<Statement> Parallel::normalize() const {
    // If SlopeAngle objects self-normalize, we just compare the members directly.
    if (m_left > m_right) {
      return make_unique<Parallel>(m_right, m_left);
    }
    return make_unique<Parallel>(m_left, m_right);
  }

  bool Parallel::check_nondegen() const {
    return m_left.check_nondegen() && m_right.check_nondegen();
  }

  bool Parallel::check_equations() const {
    return approx_eq(AddCircle<double>(m_left), AddCircle<double>(m_right));
  }

  optional<Equation<SlopeAngle>> Parallel::as_equation_slope_angle() const {
    return Equation<SlopeAngle>::sub_eq_const(m_left, m_right);
  }

  vector<statement_arg> Parallel::args() const {
    return {m_left, m_right};
  }

  ostream &Parallel::print(ostream &out) const {
    return out << m_left.left() << m_left.right() << " ∥ " << m_right.left() << m_right.right();
  }

} // namespace Yuclid
