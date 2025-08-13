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
#include <memory>
#include <ostream>
#include <string>
#include <vector>
#include "statement/orthocenter.hpp"
#include "statement/perp.hpp"
#include "statement/statement.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {

  IsOrthocenter::IsOrthocenter(const Triangle &t, const Point &p) :
    m_triangle(t), m_orthocenter(p)
  { }

  // TODO: is_orthocenter(const std::vector<statement_arg> &args);

  std::string IsOrthocenter::name() const {
    return "is_orthocenter";
  }

  std::unique_ptr<Statement> IsOrthocenter::normalize() const {
    return make_unique<IsOrthocenter>(m_triangle.sorted(), m_orthocenter);
  }

  bool IsOrthocenter::check_nondegen() const {
    return
      m_triangle.check_nondegen() &&
      perp_a().check_nondegen() &&
      perp_b().check_nondegen() &&
      perp_c().check_nondegen();
  }

  bool IsOrthocenter::check_equations() const {
    return perp_a().check_equations() && perp_b().check_equations();
  }

  std::vector<statement_arg> IsOrthocenter::args() const {
    return {m_triangle, m_orthocenter};
  }

  Perpendicular IsOrthocenter::perp_a() const {
    return {SlopeAngle(m_triangle.a(), m_orthocenter),
                SlopeAngle(m_triangle.b(), m_triangle.c())};
  }

  Perpendicular IsOrthocenter::perp_b() const {
    return {SlopeAngle(m_triangle.b(), m_orthocenter),
                SlopeAngle(m_triangle.a(), m_triangle.c())};
  }

  Perpendicular IsOrthocenter::perp_c() const {
    return {SlopeAngle(m_triangle.c(), m_orthocenter),
                SlopeAngle(m_triangle.a(), m_triangle.b())};
  }

  std::vector<Point> IsOrthocenter::points() const {
    return {
      m_triangle.a(), m_triangle.b(), m_triangle.c(), m_orthocenter
    };
  }

  std::ostream &IsOrthocenter::print(std::ostream &out) const {
    return out << m_orthocenter << " is the orthocenter of " << m_triangle;
  }

} // namespace Yuclid
