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
#include "perp.hpp"
#include "ar/equation.hpp"
#include "numbers/add_circle.hpp"
#include "numbers/util.hpp"
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

  Perpendicular::Perpendicular(SlopeAngle s1, SlopeAngle s2) : m_left(s1), m_right(s2) {}

  string Perpendicular::name() const { return "perp"; }

  vector<Point> Perpendicular::points() const {
    return {
      m_left.left(), m_left.right(),
      m_right.left(), m_right.right()
    };
  }

  unique_ptr<Statement> Perpendicular::normalize() const {
    // If SlopeAngle objects self-normalize, we just compare the members directly.
    if (m_left > m_right) {
      return make_unique<Perpendicular>(m_right, m_left);
    }
    return make_unique<Perpendicular>(m_left, m_right);
  }

  bool Perpendicular::check_nondegen() const {
    return m_left.check_nondegen() && m_right.check_nondegen();
  }

  bool Perpendicular::check_equations() const {
    return approx_eq((m_left.right().x() - m_left.left().x()) * (m_right.right().x() - m_right.left().x()),
                     -(m_left.right().y() - m_left.left().y()) * (m_right.right().y() - m_right.left().y()));
  }

  optional<Equation<SlopeAngle>> Perpendicular::as_equation_slope_angle() const {
    return Equation<SlopeAngle>::sub_eq_const(m_left, m_right, AddCircle(Rat(1, 2)));
  }

  vector<statement_arg> Perpendicular::args() const {
    return {m_left, m_right};
  }

  Perpendicular Perpendicular::swap() const {
    return {m_right, m_left};
  }

  ostream &Perpendicular::print(ostream &out) const {
    return out << m_left.left() << m_left.right() << " ⟂ " << m_right.left() << m_right.right();
  }

} // namespace Yuclid
