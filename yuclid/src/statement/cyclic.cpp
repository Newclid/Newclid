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
#include "cyclic.hpp"
#include "coll.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "typedef.hpp"
#include <algorithm>
#include <memory>
#include <ostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  CyclicQuadrangle::CyclicQuadrangle(Point a, Point b, Point c, Point d)
    : m_a(a), m_b(b), m_c(c), m_d(d) {}

  CyclicQuadrangle::CyclicQuadrangle(const vector<statement_arg>& args) :
    m_a(get<Point>(args.at(0))), m_b(get<Point>(args.at(1))),
    m_c(get<Point>(args.at(2))), m_d(get<Point>(args.at(1)))
  {
    if (args.size() != 4) {
      throw invalid_argument("cyclic constructor expects 4 arguments.");
    }
  }

  string CyclicQuadrangle::name() const { return "cyclic"; }

  vector<Point> CyclicQuadrangle::points() const {
    return {m_a, m_b, m_c, m_d};
  }

  unique_ptr<Statement> CyclicQuadrangle::normalize() const {
    vector<Point> pts = {m_a, m_b, m_c, m_d};
    ranges::sort(pts);
    return make_unique<CyclicQuadrangle>(pts[0], pts[1], pts[2], pts[3]);
  }

  bool CyclicQuadrangle::check_nondegen() const {
    return equal_angles_cad_cbd().check_nondegen() &&
      equal_angles_bad_bcd().check_nondegen() &&
      !Collinear(m_a, m_b, m_c).check_equations();
  }

  bool CyclicQuadrangle::check_equations() const {
    return equal_angles_cad_cbd().check_equations();
  }

  vector<statement_arg> CyclicQuadrangle::args() const {
    return {m_a, m_b, m_c, m_d};
  }

  unique_ptr<Statement> CyclicQuadrangle::clone() const {
    return make_unique<CyclicQuadrangle>(*this);
  }

  // Implementation of statement-specific methods for cyclic
  EqualAngles CyclicQuadrangle::equal_angles_cad_cbd() const {
    return {Angle(m_c, m_a, m_d), Angle(m_c, m_b, m_d)};
  }

  EqualAngles CyclicQuadrangle::equal_angles_bad_bcd() const {
    return {Angle(m_b, m_a, m_d), Angle(m_b, m_c, m_d)};
  }

  EqualAngles CyclicQuadrangle::equal_angles_abd_acd() const {
    return {Angle(m_a, m_b, m_d), Angle(m_a, m_c, m_d)};
  }

  ostream &CyclicQuadrangle::print(ostream &out) const {
    return out << m_a << " ∈ ω(" << m_b << m_c << m_d << ")";
  }

} // namespace Yuclid
