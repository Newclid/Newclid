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
#include <format>
#include <memory>
#include <ostream>
#include <string>
#include <vector>
#include <optional>
#include "numbers/add_circle.hpp"
#include "statement.hpp"
#include "statement/equal_line_angles.hpp"
#include "type/slope_angle.hpp"
#include "ar/equation.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {

  EqualLineAngles::EqualLineAngles(SlopeAngle left_left,
                                   SlopeAngle left_right,
                                   SlopeAngle right_left,
                                   SlopeAngle right_right) :
    m_left_left(left_left), m_left_right(left_right),
    m_right_left(right_left), m_right_right(right_right)
  { }

  string EqualLineAngles::name() const {
    return "eqangle";
  }

  vector<Point> EqualLineAngles::points() const {
    return {
      m_left_left.left(), m_left_left.right(),
      m_left_right.left(), m_left_right.right(),
      m_right_left.left(), m_right_left.right(),
      m_right_right.left(), m_right_right.right()
    };
  }

  //TODO: actually normalize; in some cases, return equality of 3-pts angles.
  unique_ptr<Statement> EqualLineAngles::normalize() const {
    return this->clone();
  }

  bool EqualLineAngles::check_nondegen() const {
    return
      m_left_left.check_nondegen() &&
      m_left_right.check_nondegen() &&
      m_right_left.check_nondegen() &&
      m_right_right.check_nondegen();
  }

  bool EqualLineAngles::check_equations() const {
    return approx_eq
      (AddCircle<double>(m_left_right) - AddCircle<double>(m_left_left),
       AddCircle<double>(m_right_right) - AddCircle<double>(m_right_left));
  }

  vector<statement_arg> EqualLineAngles::args() const {
    return {m_left_left, m_left_right, m_right_left, m_right_right};
  }

  bool EqualLineAngles::is_refl() const {
    return m_left_left == m_right_left && m_left_right == m_right_right;
  }

  optional<Equation<SlopeAngle>> EqualLineAngles::as_equation_slope_angle() const {
    return Equation<SlopeAngle>::sub_eq_sub
      (m_left_right, m_left_left, m_right_right, m_right_left);
  }

  ostream &EqualLineAngles::print(ostream &out) const {
    return out << format("∠({}{}, {}{}) = ∠({}{}, {}{})",
                         m_left_left.left().name(), m_left_left.right().name(),
                         m_left_right.left().name(), m_left_right.right().name(),
                         m_right_left.left().name(), m_right_left.right().name(),
                         m_right_right.left().name(), m_right_right.right().name());
  }

} // namespace Yuclid    
