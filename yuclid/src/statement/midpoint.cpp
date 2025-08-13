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
#include "midpoint.hpp"
#include "cong.hpp"
#include "statement/coll.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "typedef.hpp"
#include <boost/json/object.hpp>
#include <boost/json/value_from.hpp>
#include <memory>
#include <ostream>
#include <cmath>     // For numerical comparisons (e.g., in check_equations)
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  // Constructor taking three point objects
  Midpoint::Midpoint(Point left, Point middle, Point right) :
    m_left(left), m_middle(middle), m_right(right)
  {}

  // Explicit constructor from vector<statement_arg>
  Midpoint::Midpoint(const vector<statement_arg>& args) :
    m_left(get<Point>(args.at(0))),
    m_middle(get<Point>(args.at(1))),
    m_right(get<Point>(args.at(2)))
  {}

  string Midpoint::name() const { return "midpoint"; }

  unique_ptr<Statement> Midpoint::normalize() const {
    if (m_left < m_right) {
      return clone();
    }
    return make_unique<Midpoint>(m_right, m_middle, m_left);
  }

  bool Midpoint::check_nondegen() const {
    return to_coll().check_nondegen() && !m_left.is_close(m_right);
  }

  Collinear Midpoint::to_coll() const {
    return {m_left, m_middle, m_right};
  }

  DistEqDist Midpoint::to_cong() const {
    return {Dist(m_left, m_middle), Dist(m_middle, m_right)};
  }

  bool Midpoint::check_equations() const {
    return to_coll().check_equations() && to_cong().check_equations();
  }

  boost::json::object Midpoint::to_json() const {
    vector<Point> pts = {m_middle, m_left, m_right};
    return {
      { "name", "midp" },
      { "points", boost::json::value_from(pts) }
    };
  }

  ostream& Midpoint::print(ostream &out) const {
    return out << middle() << " is the midpoint of " << left() << right();
  }

  vector<Point> Midpoint::points() const {
    return {m_left, m_middle, m_right};
  }

  vector<statement_arg> Midpoint::args() const {
    // The arguments list for 'midpoint' is the same as for 'between', so delegate to parent.
    return to_coll().args();
  }

  unique_ptr<Statement> Midpoint::clone() const {
    return make_unique<Midpoint>(m_left, m_middle, m_right);
  }

} // namespace Yuclid
