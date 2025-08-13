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
#include "equal_angles.hpp"
#include "ar/equation.hpp"
#include "equal_line_angles.hpp"
#include "statement/statement.hpp"
#include "type/angle.hpp"
#include "type/point.hpp"
#include "type/slope_angle.hpp"
#include "typedef.hpp"
#include <algorithm>
#include <array>
#include <boost/json/object.hpp>
#include <memory>
#include <optional>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  EqualAngles::EqualAngles(Angle a1, Angle a2) : m_left(a1), m_right(a2) {}

  string EqualAngles::name() const { return "equal_angles"; }

  vector<Point> EqualAngles::points() const {
    return {
      m_left.left(), m_left.vertex(), m_left.right(),
      m_right.left(), m_right.vertex(), m_right.right()
    };
  }

  array<EqualAngles, 4> EqualAngles::permutations() const {
    return {*this, {m_right, m_left}, {-m_left, -m_right}, {-m_right, -m_left}};
  }

  unique_ptr<Statement> EqualAngles::normalize() const {
    return make_unique<EqualAngles>(ranges::min(permutations()));
  }

  EqualLineAngles EqualAngles::to_equal_line_angles() const {
    return {m_left.left_side(), m_left.right_side(),
            m_right.left_side(), m_right.right_side()};
  }

  bool EqualAngles::check_nondegen() const {
    return to_equal_line_angles().check_nondegen();
  }

  bool EqualAngles::check_equations() const {
    return to_equal_line_angles().check_equations();
  }


  vector<statement_arg> EqualAngles::args() const {
    return {m_left, m_right};
  }

  std::optional<Equation<SlopeAngle>> EqualAngles::as_equation_slope_angle() const {
    return to_equal_line_angles().as_equation<SlopeAngle>();
  }

  bool EqualAngles::is_refl() const {
    return m_left == m_right;
  }

  boost::json::object EqualAngles::to_json() const {
    return to_equal_line_angles().to_json();
  }


  ostream &EqualAngles::print(ostream &out) const {
    return out << m_left << " = " << m_right;
  }

} // namespace Yuclid
