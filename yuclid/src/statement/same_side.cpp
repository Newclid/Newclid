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
#include "statement/coll.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "typedef.hpp"
#include <format>
#include <memory>
#include <ostream>
#include <string>
#include <vector>
#include "statement/same_side.hpp"

using namespace std;

namespace Yuclid {

  SameSignDot::SameSignDot(const Point &a, const Point &b, const Point &c,
                       const Point &d, const Point &e, const Point &f) :
    m_a(a), m_b(b), m_c(c), m_d(d), m_e(e), m_f(f)
  { }

  SameSignDot::SameSignDot(const Collinear &left, const Collinear &right) :
    SameSignDot(left.a(), left.b(), left.c(), right.a(), right.b(), right.c())
  { }

  std::string SameSignDot::name() const {
    return "sameside";
  }

  std::vector<Point> SameSignDot::points() const {
    return {m_a, m_b, m_c, m_d, m_e, m_f};
  }

  std::unique_ptr<Statement> SameSignDot::normalize() const {
    return clone();
  }

  bool SameSignDot::check_nondegen() const {
    return
      !m_a.is_close(m_b) && !m_b.is_close(m_c) && !m_a.is_close(m_c) &&
      !m_d.is_close(m_e) && !m_e.is_close(m_f) && !m_d.is_close(m_f) &&
      (((m_b.x() - m_a.x()) * (m_c.x() - m_a.x()) + (m_b.y() - m_a.y()) * (m_c.y() - m_a.y()) > 0) ==
       ((m_e.x() - m_d.x()) * (m_f.x() - m_d.x()) + (m_e.y() - m_d.y()) * (m_f.y() - m_d.y()) > 0));
  }

  bool SameSignDot::check_equations() const {
    return true;
  }

  bool SameSignDot::numerical_only() const {
    return true;
  }

  std::vector<statement_arg> SameSignDot::args() const {
    return {m_a, m_b, m_c, m_d, m_e, m_f};
  }

  std::unique_ptr<Statement> SameSignDot::clone() const {
    return make_unique<SameSignDot>(*this);
  }

  std::ostream &SameSignDot::print(std::ostream &out) const {
    return out << format("{} on the same side of [{},{}] as {} of [{}, {}]",
                         m_a.name(), m_b.name(), m_c.name(), m_d.name(), m_e.name(), m_f.name());
  }

} // namespace Yuclid
