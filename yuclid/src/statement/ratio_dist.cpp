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
#include <boost/json/object.hpp>
#include <boost/json/value_from.hpp>
#include <memory>
#include <ostream>
#include <ranges>
#include <string>
#include <utility>
#include <vector>
#include <optional>
#include "ar/linear_combination.hpp"
#include "numbers/util.hpp"
#include "statement.hpp"
#include "ar/equation.hpp"
#include "typedef.hpp"
#include "statement/ratio_dist.hpp"
#include "statement/ratio_squared_dist.hpp"

using namespace std;

namespace Yuclid {

  RatioDistEquals::RatioDistEquals(const Dist &d1, const Dist &d2, const NNRat &r) :
    m_left(d1), m_right(d2), m_ratio(r)
  { }

  string RatioDistEquals::name() const {
    return "rconst";
  }

  vector<Point> RatioDistEquals::points() const {
    return {
      m_left.left(), m_left.right(), m_right.left(), m_right.right()
    };
  }

  RatioDistEquals RatioDistEquals::swap() const {
    return {m_right, m_left, NNRat(1) / m_ratio};
  }

  unique_ptr<Statement> RatioDistEquals::normalize() const {
    /* Disabled, because Newclid doesn't do that
    if (m_ratio == 1) {
      if (m_left < m_right) {
        return make_unique<DistEqDist>(m_left, m_right);
      } else {
        return make_unique<DistEqDist>(m_right, m_left);
      }
    }
    */
    if (m_left < m_right) {
      return make_unique<RatioDistEquals>(*this);
    }
    return make_unique<RatioDistEquals>(swap());
  }
  
  bool RatioDistEquals::check_nondegen() const {
    return
      m_left.check_nondegen() &&
      m_right.check_nondegen();
  }

  bool RatioDistEquals::check_equations() const {
    return approx_eq(double(m_left), nnrat2double(m_ratio) * double(m_right));
  }

  optional<Equation<Dist>> RatioDistEquals::as_equation_dist() const {
    return LinearCombination<Dist>(m_left) -
      LinearCombination<Dist>(m_right, nnrat2rat(m_ratio)) == Rat(0);
  }

  optional<Equation<SquaredDist>> RatioDistEquals::as_equation_squared_dist() const {
    return as_ratio_squared_dist().value().as_equation<SquaredDist>();
  }

  optional<Equation<SinOrDist>> RatioDistEquals::as_equation_sin_or_dist() const {
    return as_ratio_squared_dist().value().as_equation<SinOrDist>();
  }

  vector<statement_arg> RatioDistEquals::args() const {
    return {
      statement_arg(in_place_type<Dist>, m_left),
      statement_arg(in_place_type<Dist>, m_right),
      statement_arg(in_place_type<NNRat>, m_ratio)
    };
  }

  optional<RatioSquaredDist> RatioDistEquals::as_ratio_squared_dist() const {
    return RatioSquaredDist(SquaredDist(m_left), SquaredDist(m_right), m_ratio * m_ratio);
  }

  ostream &RatioDistEquals::print(ostream &out) const {
    return out << m_left << ":" << m_right << " = " << m_ratio;
  }

  boost::json::object RatioDistEquals::to_json() const {
    std::vector<string> args =
      points() | views::transform(&Point::name) | ranges::to<vector>();
    args.push_back(nnrat2string(m_ratio));
    return {
      {"name", name()},
      {"points", boost::json::value_from(args)}
    };
  }

} // namespace Yuclid
