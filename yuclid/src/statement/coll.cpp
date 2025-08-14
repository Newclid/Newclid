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
#include "eqratio.hpp"
#include "numbers/util.hpp"
#include "statement/statement.hpp"
#include "statement/obtuse_angle.hpp"
#include "type/point.hpp"
#include "typedef.hpp"
#include <algorithm> // For std::sort
#include <array>
#include <cstdlib>
#include <memory>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  Collinear::Collinear(Point a, Point b, Point c) : m_a(a), m_b(b), m_c(c) {} // Updated constructor and member initializers

  Collinear::Collinear(const vector<statement_arg> &args) :
    m_a(get<Point>(args.at(0))),
    m_b(get<Point>(args.at(1))),
    m_c(get<Point>(args.at(2)))
  { }

  string Collinear::name() const { return "coll"; }

  vector<Point> Collinear::points() const {
    return {m_a, m_b, m_c};
  }

  unique_ptr<Statement> Collinear::normalize() const {
    array<Point, 3> pts = {m_a, m_b, m_c};
    ranges::sort(pts);
    return make_unique<Collinear>(pts[0], pts[1], pts[2]);
  }

  bool Collinear::check_nondegen() const {
    return !m_a.is_close(m_b) && !m_b.is_close(m_c) && !m_a.is_close(m_c);
  }

  bool Collinear::check_equations() const {
    double const lhs = ((m_b.x() - m_a.x()) * (m_c.y() - m_a.y()));
    double const rhs = ((m_b.y() - m_a.y()) * (m_c.x() - m_a.x()));

    return approx_eq(lhs, rhs);
  }

  array<Collinear, 3> Collinear::cyclic_permutations() const {
    return {*this, {m_b, m_c, m_a}, {m_c, m_a, m_b}};
  }

  array<Collinear, 6> Collinear::permutations() const {
    return {
      *this, {m_b, m_c, m_a}, {m_c, m_a, m_b},
      {m_a, m_c, m_b}, {m_c, m_b, m_a}, {m_b, m_a, m_c}
    };
  }

  bool Collinear::is_between() const {
    return ObtuseAngle(Angle(m_a, m_b, m_c)).check_nondegen();
  }

  vector<statement_arg> Collinear::args() const {
    return {m_a, m_b, m_c}; // Using new member names
  }

  EqualRatios Collinear::eqratio_ab_bc(const Collinear &other) const {
    return
      { Dist(m_a, m_b), Dist(m_b, m_c),
        Dist(other.m_a, other.m_b), Dist(other.m_b, other.m_c) };
  }

  EqualRatios Collinear::eqratio_ab_ac(const Collinear &other) const {
    return
      { Dist(m_a, m_b), Dist(m_a, m_c),
        Dist(other.m_a, other.m_b), Dist(other.m_a, other.m_c) };
  }

  std::ostream &Collinear::print(std::ostream &out) const {
    return out << m_a << " ∈ " << m_b << m_c;
  }

  std::ostream &Collinear::print_newclid(std::ostream &out) const {
    return out << "coll " << m_a << " " << m_b << " " << m_c;
  }

} // namespace Yuclid
