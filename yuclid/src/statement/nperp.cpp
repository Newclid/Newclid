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
#include <algorithm>
#include <memory>
#include <ostream>
#include <string>
#include <vector>
#include "statement/statement.hpp"
#include "typedef.hpp" // Assuming point is defined here
#include "nperp.hpp"
#include "perp.hpp"

using namespace std;

namespace Yuclid {

  string NonPerpendicular::name() const { return "nperp"; }

  vector<Point> NonPerpendicular::points() const {
    return {
      m_left.left(), m_left.right(),
      m_right.left(), m_right.right()
    };
  }

  unique_ptr<Statement> NonPerpendicular::normalize() const {
    return make_unique<NonPerpendicular>(min(m_left, m_right), max(m_left, m_right));
  }

  bool NonPerpendicular::check_nondegen() const {
    return
      m_left.check_nondegen() &&
      m_right.check_nondegen() &&
      !Perpendicular(m_left, m_right).check_equations();
  }

  vector<statement_arg> NonPerpendicular::args() const { return {m_left, m_right}; }

  ostream &NonPerpendicular::print(ostream &out) const {
    return out << m_left.left() << m_left.right() << "⟂̸" << m_right.left() << m_right.right();
  }

} // namespace Yuclid
