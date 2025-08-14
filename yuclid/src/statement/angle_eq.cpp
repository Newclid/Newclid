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
#include <boost/json/object.hpp>
#include <memory>
#include <ostream>
#include <string>
#include <vector>
#include <optional>
#include "statement/angle_eq.hpp"
#include "numbers/add_circle.hpp"
#include "statement/line_angle_eq.hpp"
#include "ar/equation.hpp"
#include "statement/statement.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {
  AngleEq::AngleEq(const Angle &a, const AddCircle<Rat> &r) :
    m_angle(a), m_rhs(r)
  { }

  AngleEq::AngleEq(const Angle &a, const Rat &r): m_angle(a), m_rhs(r)
  { }
    
  std::string AngleEq::name() const {
    return "aconst";
  }

  std::vector<Point> AngleEq::points() const {
    return {m_angle.left(), m_angle.vertex(), m_angle.right()};
  }

  std::unique_ptr<Statement> AngleEq::normalize() const {
    if (m_angle.left() < m_angle.right()) {
      return clone();
    }
    return make_unique<AngleEq>(-m_angle, -m_rhs);
  }

  bool AngleEq::check_nondegen() const {
    return m_angle.check_nondegen();
  }

  bool AngleEq::check_equations() const {
    return approx_eq(AddCircle<double>(m_angle), m_rhs);
  }

  std::vector<statement_arg> AngleEq::args() const {
    return {m_angle, m_rhs};
  }

  std::optional<Equation<SlopeAngle>> AngleEq::as_equation_slope_angle() const {
    return Equation<SlopeAngle>::sub_eq_const(m_angle.right_side(), m_angle.left_side(), m_rhs);
  }

  LineAngleEq AngleEq::to_line_angle_eq() const {
    return {m_angle.left_side(), m_angle.right_side(), m_rhs};
  }

  boost::json::object AngleEq::to_json() const {
    return to_line_angle_eq().to_json();
  }


  std::ostream &AngleEq::print(std::ostream &out) const {
    return out << m_angle << " = " << m_rhs.number() << "π";
  }

} // namespace Yuclid
