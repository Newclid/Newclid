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
#include "same_clock.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"
#include <memory>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  SameClock::SameClock(const Triangle &l, const Triangle &r) :
    m_left(l), m_right(r)
  {}

  string SameClock::name() const { return "sameclock"; }

  vector<Point> SameClock::points() const {
    return {
      m_left.a(), m_left.b(), m_left.c(),
      m_right.a(), m_right.b(), m_right.c()
    };
  }

  unique_ptr<Statement> SameClock::normalize() const {
    return make_unique<SameClock>(*this);
  }

  bool SameClock::check_nondegen() const {
    return
      m_left.check_nondegen() &&
      m_right.check_nondegen() &&
      ((m_left.area() > 0) == (m_right.area() > 0));
  }

  vector<statement_arg> SameClock::args() const {
    return {m_left, m_right};
  }

  std::ostream &SameClock::print(std::ostream &out) const {
    return out << m_left << " oriented the same way as " << m_right;
  }

  std::ostream &SameClock::print_newclid(std::ostream &out) const {
    return out << "sameclock " << m_left.a() << " " << m_left.b() << " " << m_left.c()
               << " " << m_right.a() << " " << m_right.b() << " " << m_right.c();
  }

} // namespace Yuclid
