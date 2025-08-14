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
#include "ar/linear_combination.hpp"
#include "cong.hpp"
#include "statement/ratio_squared_dist.hpp"
#include "numbers/root_rat.hpp"
#include "numbers/util.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/statement.hpp"
#include "type/dist.hpp"
#include "type/point.hpp"
#include "type/sin_or_dist.hpp"
#include "type/squared_dist.hpp"
#include "typedef.hpp"
#include <boost/json/object.hpp>
#include <boost/json/value_from.hpp>
#include <memory>
#include <optional>
#include <ostream>
#include <string>
#include <utility>
#include <vector>

using namespace std; // Added as requested

namespace Yuclid {

  RatioSquaredDist::RatioSquaredDist(SquaredDist d1,
                                         SquaredDist d2,
                                         const NNRat &r) :
    m_left(std::move(d1)), m_right(std::move(d2)), m_ratio(r)
  {}

  string RatioSquaredDist::name() const { return "ratio_squared_dist"; }

  vector<Point> RatioSquaredDist::points() const {
    return {
      m_left.left(), m_left.right(),
      m_right.left(), m_right.right()
    };
  }

  unique_ptr<Statement> RatioSquaredDist::normalize() const {
    optional<NNRat> r = rat_sqrt(m_ratio);
    if (r.has_value()) {
      return RatioDistEquals(Dist(m_left), Dist(m_right), r.value()).normalize();
    }
    if (m_left > m_right) {
      return make_unique<RatioSquaredDist>(m_right, m_left, NNRat(1) / m_ratio);
    }
    return make_unique<RatioSquaredDist>(*this);
  }

  unique_ptr<Statement> RatioSquaredDist::normalize2() const {
    if (m_ratio == 1) {
      return make_unique<DistEqDist>(Dist(m_left), Dist(m_right));
    }
    return normalize();
  }

  bool RatioSquaredDist::check_nondegen() const {
    return m_left.check_nondegen() && m_right.check_nondegen();
  }

  bool RatioSquaredDist::check_equations() const {
    return approx_eq(double(SquaredDist(m_left)),
                     double(SquaredDist(m_right)) * nnrat2double(m_ratio));
  }

  optional<Equation<SinOrDist>> RatioSquaredDist::as_equation_sin_or_dist() const {
    return LinearCombination<SinOrDist>(SinOrDist(m_left)) -
      LinearCombination<SinOrDist>(SinOrDist(m_right)) == RootRat(m_ratio);
  }

  optional<Equation<SquaredDist>> RatioSquaredDist::as_equation_squared_dist() const {
    return LinearCombination<SquaredDist>(m_left) -
      LinearCombination<SquaredDist>(m_right, nnrat2rat(m_ratio)) == 0;
  }

  optional<RatioSquaredDist> RatioSquaredDist::as_ratio_squared_dist() const {
    return *this;
  }

  vector<statement_arg> RatioSquaredDist::args() const { // Removed std::vector
    return {
      statement_arg(in_place_type<SquaredDist>, m_left),
      statement_arg(in_place_type<SquaredDist>, m_right),
      statement_arg(in_place_type<NNRat>, m_ratio)
    };
  }

  boost::json::object RatioSquaredDist::to_json() const {
    vector<string> args =
      {m_left.left().name(), m_left.right().name(),
       m_right.left().name(), m_right.right().name(),
       nnrat2string(m_ratio)};
    return {
      {"name", "r2const"},
      {"points", boost::json::value_from(args)}
    };
  }

  ostream &RatioSquaredDist::print(ostream &out) const {
    return out << SquaredDist(m_left) << " = " << m_ratio << SquaredDist(m_right);
  }

} // namespace Yuclid
