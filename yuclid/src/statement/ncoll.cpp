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
#include "coll.hpp"
#include "ncoll.hpp"
#include "statement/statement.hpp"
#include "theorem.hpp"
#include "type/point.hpp"
#include "typedef.hpp"
#include <algorithm> // For std::sort
#include <memory>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  NonCollinear::NonCollinear(Point a, Point b, Point c) : m_a(a), m_b(b), m_c(c) {}

  string NonCollinear::name() const { return "ncoll"; }

  vector<Point> NonCollinear::points() const {
    return {m_a, m_b, m_c};
  }

  unique_ptr<Statement> NonCollinear::normalize() const {
    vector<Point> pts = {m_a, m_b, m_c}; // Using new member names
    ranges::sort(pts);
    return make_unique<NonCollinear>(pts[0], pts[1], pts[2]);
  }

  bool NonCollinear::check_nondegen() const {
    return !m_a.is_close(m_b) && !m_b.is_close(m_c) && !m_a.is_close(m_c) &&
      !Collinear(m_a, m_b, m_c).check_equations();
  }

  vector<statement_arg> NonCollinear::args() const {
    return {m_a, m_b, m_c}; // Using new member names
  }

  std::ostream &NonCollinear::print(std::ostream &out) const {
    return out << m_a << " ∉ " << m_b << m_c;
  }

  std::ostream &NonCollinear::print_newclid(std::ostream &out) const {
    return out << "ncoll " << m_a << " " << m_b << " " << m_c;
  }

} // namespace Yuclid
