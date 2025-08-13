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
#include "similar_triangles.hpp"
#include "equal_angles.hpp"
#include "eqratio.hpp"
#include "statement/statement.hpp"
#include "statement/same_clock.hpp"
#include "type/point.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"
#include <algorithm>
#include <array>
#include <memory>
#include <ostream>
#include <stdexcept> // For std::invalid_argument
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  SimilarTriangles::SimilarTriangles(const Triangle &t1, const Triangle &t2, bool same_clockwise)
    : m_left(t1), m_right(t2), m_same_clockwise(same_clockwise) {}

  SimilarTriangles::SimilarTriangles(const vector<statement_arg>& args) :
    m_left(get<Triangle>(args.at(0))),
    m_right(get<Triangle>(args.at(1))),
    m_same_clockwise(get<bool>(args.at(2)))
  {
    if (args.size() != 3) {
      throw invalid_argument("similar_triangles constructor expects 3 arguments (2 triangles, 1 bool).");
    }
  }

  string SimilarTriangles::name() const {
    return m_same_clockwise ? "simtri" : "simtrir";
  }

  vector<Point> SimilarTriangles::points() const {
    return {
      m_left.a(), m_left.b(), m_left.c(),
      m_right.a(), m_right.b(), m_right.c()
    };
  }

  SameClock SimilarTriangles::to_same_clock() const {
    if (m_same_clockwise) {
      return {m_left, m_right};
    }
    return {m_left, {m_right.a(), m_right.c(), m_right.b()}};
  }

  array<SimilarTriangles, 12> SimilarTriangles::permutations() const {
    const auto left = m_left.permutations();
    const auto right = m_right.permutations();
    return {
      SimilarTriangles(left[0], right[0], m_same_clockwise),
      SimilarTriangles(left[1], right[1], m_same_clockwise),
      SimilarTriangles(left[2], right[2], m_same_clockwise),
      SimilarTriangles(left[3], right[3], m_same_clockwise),
      SimilarTriangles(left[4], right[4], m_same_clockwise),
      SimilarTriangles(left[5], right[5], m_same_clockwise), // NOLINT
      SimilarTriangles(right[0], left[0], m_same_clockwise),
      SimilarTriangles(right[1], left[1], m_same_clockwise),
      SimilarTriangles(right[2], left[2], m_same_clockwise),
      SimilarTriangles(right[3], left[3], m_same_clockwise),
      SimilarTriangles(right[4], left[4], m_same_clockwise),
      SimilarTriangles(right[5], left[5], m_same_clockwise) // NOLINT
    };
  }

  array<SimilarTriangles, 3> SimilarTriangles::cyclic_rotations() const {
    const auto left = m_left.cyclic_rotations();
    const auto right = m_right.cyclic_rotations();
    return {
      SimilarTriangles(left[0], right[0], m_same_clockwise),
      SimilarTriangles(left[1], right[1], m_same_clockwise),
      SimilarTriangles(left[2], right[2], m_same_clockwise)
    };
  }

  unique_ptr<Statement> SimilarTriangles::normalize() const {
    return make_unique<SimilarTriangles>(ranges::min(permutations()));
  }

  EqualRatios SimilarTriangles::eqratio_abbc() const {
    return {{m_left.a(), m_left.b()}, {m_left.b(), m_left.c()},
            {m_right.a(), m_right.b()}, {m_right.b(), m_right.c()}};
  }

  EqualRatios SimilarTriangles::eqratio_abac() const {
    return {{m_left.a(), m_left.b()}, {m_left.a(), m_left.c()},
            {m_right.a(), m_right.b()}, {m_right.a(), m_right.c()}};
  }

  EqualRatios SimilarTriangles::eqratio_bcac() const {
    return {{m_left.b(), m_left.c()}, {m_left.a(), m_left.c()},
            {m_right.b(), m_right.c()}, {m_right.a(), m_right.c()}};
  }

  EqualAngles SimilarTriangles::equal_angles_abc() const {
    return {m_left.angle_b(), m_same_clockwise ? m_right.angle_b() : -m_right.angle_b()};
  }

  EqualAngles SimilarTriangles::equal_angles_bca() const {
    return {m_left.angle_c(), m_same_clockwise ? m_right.angle_c() : -m_right.angle_c()};
  }

  EqualAngles SimilarTriangles::equal_angles_acb() const {
    return {-m_left.angle_c(), m_same_clockwise ? -m_right.angle_c() : m_right.angle_c()};
  }

  EqualAngles SimilarTriangles::equal_angles_cab() const {
    return {m_left.angle_a(), m_same_clockwise ? m_right.angle_a() : -m_right.angle_a()};
  }

  bool SimilarTriangles::check_nondegen() const {
    return
      m_left.check_nondegen() &&
      m_right.check_nondegen() &&
      (m_same_clockwise == ((m_left.area() > 0) == (m_right.area() > 0)));
  }

  bool SimilarTriangles::check_equations() const {
    return eqratio_abac().check_equations() && eqratio_bcac().check_equations();
  }

  vector<statement_arg> SimilarTriangles::args() const {
    return {m_left, m_right, m_same_clockwise};
  }

  unique_ptr<Statement> SimilarTriangles::clone() const {
    return make_unique<SimilarTriangles>(*this); // Implementation of clone()
  }

  ostream &SimilarTriangles::print(ostream &out) const {
    return out << m_left << " ∼" << (m_same_clockwise ? " " : "r ") << m_right;
  }


} // namespace Yuclid
