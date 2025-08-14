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
#include "ar/equation.hpp"
#include "numbers/add_circle.hpp"
#include "numbers/util.hpp"
#include "statement/angle_eq.hpp"
#include "statement/line_angle_eq.hpp"
#include "statement/statement.hpp"
#include "typedef.hpp"
#include <boost/json/object.hpp>
#include <boost/json/value_from.hpp>
#include <memory>
#include <optional>
#include <ostream>
#include <ranges>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  LineAngleEq::LineAngleEq(SlopeAngle l, SlopeAngle r,
                           const AddCircle<Rat> &v) :
    m_left(l), m_right(r), m_rhs(v)
  { }
  
  LineAngleEq::LineAngleEq(SlopeAngle l, SlopeAngle r, const Rat &v) :
    m_left(l), m_right(r), m_rhs(v)
  { }

  std::string LineAngleEq::name() const {
    return "aconst";
  }

  std::vector<Point> LineAngleEq::points() const {
    return {m_left.left(), m_left.right(), m_right.left(), m_right.right()};
  }

  std::unique_ptr<Statement> LineAngleEq::normalize() const {
    /* TODO reenable if Python side starts normalizing this too.
       if (m_left.left() == m_right.left()) {
       return make_unique<AngleEq>
       (angle(m_left.right(), m_left.left(), m_right.right()), m_rhs);
       } else if (m_left.left() == m_right.right()) {
       return make_unique<AngleEq>
       (angle(m_left.right(), m_left.left(), m_right.left()), m_rhs);
       } else if (m_left.right() == m_right.left()) {
       return make_unique<AngleEq>
       (angle(m_left.left(), m_left.right(), m_right.right()), m_rhs);
       } else if (m_left.right() == m_right.right()) {
       return make_unique<AngleEq>
       (angle(m_left.left(), m_left.right(), m_right.left()), m_rhs);
       }
    */
    return clone();
  }

  bool LineAngleEq::check_nondegen() const {
    return m_left.check_nondegen() && m_right.check_nondegen();
  }

  bool LineAngleEq::check_equations() const {
    return approx_eq<AddCircle<double>, AddCircle<Rat>>
      (AddCircle<double>(m_right) - AddCircle<double>(m_left),
       static_cast<AddCircle<Rat>>(m_rhs));
  }

  std::vector<statement_arg> LineAngleEq::args() const {
    return {m_left, m_right, m_rhs};
  }

  std::optional<Equation<SlopeAngle>> LineAngleEq::as_equation_slope_angle() const {
    return Equation<SlopeAngle>::sub_eq_const(m_right, m_left, m_rhs);
  }

  boost::json::object LineAngleEq::to_json() const {
    std::vector<string> args =
      points() | views::transform(&Point::name) | ranges::to<vector>();
    args.push_back(rat2string(m_rhs.number()));
    return {
      {"name", name()},
      {"points", boost::json::value_from(args)}
    };
  }

  std::ostream &LineAngleEq::print(std::ostream &out) const {
    return out << "∠(" << m_left.left() << m_left.right() << ", "
               << m_right.left() << m_right.right() << ")";
  }

} // namespace Yuclid
