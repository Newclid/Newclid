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
#include "ar/linear_combination.hpp"
#include "statement/statement.hpp"
#include "type/point.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"
#include "statement/coll.hpp"
#include "statement/cong.hpp"
#include "statement/para.hpp"
#include "statement/parallelogram.hpp"
#include "statement/eqn_statement.hpp"
#include <algorithm>
#include <array>
#include <memory>
#include <ostream>
#include <string>
#include <vector>

using namespace std;

namespace Yuclid {

  Parallelogram::Parallelogram(const Point &a, const Point &b, const Point &c, const Point &d) :
    m_a(a), m_b(b), m_c(c), m_d(d)
  { }

  Parallelogram::Parallelogram(const std::vector<statement_arg> &args) :
    m_a(get<Point>(args.at(0))), m_b(get<Point>(args.at(1))),
    m_c(get<Point>(args.at(2))), m_d(get<Point>(args.at(3)))
  { }
  
  std::string Parallelogram::name() const {
    return "parallelogram";
  }

  std::array<Parallelogram, 8> Parallelogram::permutations() const {
    return {
      *this,
      {m_b, m_c, m_d, m_a},
      {m_c, m_d, m_a, m_b},
      {m_d, m_a, m_b, m_c},
      {m_a, m_d, m_c, m_b},
      {m_d, m_c, m_b, m_a},
      {m_c, m_b, m_a, m_d},
      {m_b, m_a, m_d, m_c}
    };
  }

  std::unique_ptr<Statement> Parallelogram::normalize() const {
    return make_unique<Parallelogram>(ranges::min(permutations()));
  }

  bool Parallelogram::check_nondegen() const {
    return
      Dist(m_a, m_b).check_nondegen() &&
      Dist(m_b, m_c).check_nondegen() &&
      Dist(m_c, m_d).check_nondegen() &&
      Dist(m_d, m_a).check_nondegen() &&
      !Collinear(m_a, m_b, m_c).check_equations();
  }

  bool Parallelogram::check_equations() const {
    return
      para_ab_cd().check_equations() &&
      para_ad_bc().check_equations();
  }

  std::vector<statement_arg> Parallelogram::args() const {
    return {m_a, m_b, m_c, m_d};
  }

  Parallel Parallelogram::para_ab_cd() const {
    return {SlopeAngle(m_a, m_b), SlopeAngle(m_c, m_d)};
  }

  Parallel Parallelogram::para_ad_bc() const {
    return {SlopeAngle(m_a, m_d), SlopeAngle(m_b, m_c)};
  }

  DistEqDist Parallelogram::cong_ab_cd() const {
    return {Dist(m_a, m_b), Dist(m_c, m_d)};
  }

  DistEqDist Parallelogram::cong_ad_bc() const {
    return {Dist(m_a, m_d), Dist(m_b, m_c)};
  }

  EqnStatement<SquaredDist> Parallelogram::parallelogram_law_eqn() const {
    return
      EqnStatement
      (LinearCombination(SquaredDist(m_a, m_b), 2) +
       LinearCombination(SquaredDist(m_b, m_c), 2) -
       LinearCombination(SquaredDist(m_a, m_c)) -
       LinearCombination(SquaredDist(m_b, m_d)) == Rat(0));
  }

  std::vector<Point> Parallelogram::points() const {
    return {m_a, m_b, m_c, m_d};
  }

  ostream &Parallelogram::print(ostream &out) const {
    return out << m_a << m_b << m_c << m_d << "is a parallelogram";
  }

} // namespace Yuclid
