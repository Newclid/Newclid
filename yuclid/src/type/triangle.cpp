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
#include "triangle.hpp"
#include "dist.hpp"
#include "angle.hpp"
#include "statement/coll.hpp"
#include "type/point.hpp"
#include "problem.hpp"
#include <algorithm>
#include <array>
#include <cstddef>
#include <ostream>
#include <stdexcept>

using namespace std;

namespace Yuclid {
  Triangle::Triangle(Point a, Point b, Point c) noexcept : m_a(a), m_b(b), m_c(c) {}

  Angle Triangle::angle_a() const { return {m_c, m_a, m_b}; }
  Angle Triangle::angle_b() const { return {m_a, m_b, m_c}; }
  Angle Triangle::angle_c() const { return {m_b, m_c, m_a}; }

  Dist Triangle::dist_ab() const { return {m_a, m_b}; }
  Dist Triangle::dist_ac() const { return {m_a, m_c}; }
  Dist Triangle::dist_bc() const { return {m_b, m_c}; }

  Point Triangle::operator[](size_t ind) const {
    switch (ind % 3) {
    case 0 : return m_a;
    case 1 : return m_b;
    case 2 : return m_c;
    default: throw logic_error("The remainder mod 3 can't be anything else");
    }
  }

  double Triangle::area() const {
    return ((m_c.y() - m_a.y()) * (m_b.x() - m_a.x()) -
            (m_c.x() - m_a.x()) * (m_b.y() - m_a.y())) / 2;
  }

  array<Triangle, 3> Triangle::cyclic_rotations() const {
    return {*this, {m_b, m_c, m_a}, {m_c, m_a, m_b}};
  }

  array<Triangle, 6> Triangle::permutations() const {
    return {
      *this, {m_b, m_c, m_a}, {m_c, m_a, m_b},
      {m_a, m_c, m_b}, {m_c, m_b, m_a}, {m_b, m_a, m_c}
    };
  }

  array<Angle, 3> Triangle::angles() const {
    return {angle_a(), angle_b(), angle_c()};
  }

  array<Dist, 3> Triangle::dists() const {
    return {Dist{m_a, m_b}, {m_b, m_c}, {m_a, m_c}};
  }

  Triangle Triangle::sorted() const {
    array<Point, 3> pts {m_a, m_b, m_c};
    ranges::sort(pts);
    return {pts[0], pts[1], pts[2]};
  }

  bool Triangle::check_nondegen() const {
    return !Collinear(m_a, m_b, m_c).check_equations();
  }

  std::ostream &operator<<(std::ostream &out, const Triangle &t) {
    out << "▵" << t.a() << " " << t.b() << " " << t.c();
    return out;
  }
}
