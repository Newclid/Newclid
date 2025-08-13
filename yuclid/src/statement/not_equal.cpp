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
#include "statement/not_equal.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "typedef.hpp"
#include <memory>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  NotEqual::NotEqual(Point left, Point right) : m_left(left), m_right(right) {}

  string NotEqual::name() const { return "diff"; }

  vector<Point> NotEqual::points() const {
    return {m_left, m_right};
  }

  unique_ptr<Statement> NotEqual::normalize() const {
    if (m_left < m_right) {
      return clone();
    }
    return make_unique<NotEqual>(m_right, m_left);
  }

  bool NotEqual::check_nondegen() const {
    return !m_left.is_close(m_right);
  }

  vector<statement_arg> NotEqual::args() const {
    return {m_left, m_right};
  }

  std::ostream &NotEqual::print(std::ostream &out) const {
    return out << m_left << " ≠ " << m_right;
  }

  std::ostream &NotEqual::print_newclid(std::ostream &out) const {
    return out << "diff " << m_left << " " << m_right;
  }

} // namespace Yuclid
