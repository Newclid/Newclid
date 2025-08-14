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
#include "ar/equation.hpp"
#include "cong.hpp"
#include "ar/linear_combination.hpp"
#include "numbers/util.hpp"
#include "ratio_squared_dist.hpp"
#include "statement/statement.hpp"
#include "type/dist.hpp"
#include "type/point.hpp"
#include "type/sin_or_dist.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"
#include <memory>
#include <optional>
#include <ostream>
#include <string>
#include <utility>
#include <vector>

using namespace std; // Added as requested

namespace Yuclid {

  DistEqDist::DistEqDist(Dist d1, Dist d2) : m_left(d1), m_right(d2) {}

  string DistEqDist::name() const { return "cong"; } // Removed std::string

  vector<Point> DistEqDist::points() const {
    return {m_left.left(), m_left.right(), m_right.left(), m_right.right()};
  }

  unique_ptr<Statement> DistEqDist::normalize() const { // Removed std::unique_ptr
    // If dist objects self-normalize, we just compare the members directly.
    if (m_left > m_right) {
      return make_unique<DistEqDist>(m_right, m_left);
    }
    return make_unique<DistEqDist>(m_left, m_right);
  }

  bool DistEqDist::check_nondegen() const {
    return m_left.check_nondegen() && m_right.check_nondegen();
  }

  bool DistEqDist::check_equations() const {
    return approx_eq(double(m_left), double(m_right));
  }

  optional<Equation<Dist>> DistEqDist::as_equation_dist() const {
    return LinearCombination<Dist>(m_left) - LinearCombination<Dist>(m_right) == 0;
  }

  optional<Equation<SinOrDist>> DistEqDist::as_equation_sin_or_dist() const {
    return LinearCombination<SinOrDist>(SinOrDist(m_left)) - LinearCombination<SinOrDist>(SinOrDist(m_right)) == RootRat();
  }

  optional<Equation<SquaredDist>> DistEqDist::as_equation_squared_dist() const {
    return LinearCombination<SquaredDist>(SquaredDist(m_left)) - LinearCombination<SquaredDist>(SquaredDist(m_right)) == 0;
  }

  optional<RatioSquaredDist> DistEqDist::as_ratio_squared_dist() const {
    return RatioSquaredDist(SquaredDist(m_left), SquaredDist(m_right), 1);
  }

  vector<statement_arg> DistEqDist::args() const {
    return {
      statement_arg(in_place_type<Dist>, m_left),
      statement_arg(in_place_type<Dist>, m_right)
    };
  }

  bool DistEqDist::is_refl() const {
    return m_left == m_right;
  }

  ostream &DistEqDist::print(ostream &out) const {
    return out << m_left << " = " << m_right;
  }

} // namespace Yuclid
