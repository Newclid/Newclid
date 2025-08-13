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
#include "statement/squared_dist_eq.hpp"
#include "ar/linear_combination.hpp"
#include "numbers/root_rat.hpp"
#include "numbers/util.hpp"
#include "statement/dist_eq.hpp"
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

  SquaredDistEq::SquaredDistEq(SquaredDist d, const NNRat &r) :
    m_squared_dist(std::move(d)), m_rhs(r)
  {}

  string SquaredDistEq::name() const { return "squared_dist_eq"; }

  vector<Point> SquaredDistEq::points() const {
    return {m_squared_dist.left(), m_squared_dist.right()};
  }

  unique_ptr<Statement> SquaredDistEq::normalize() const {
    auto r = rat_sqrt(m_rhs);
    if (r.has_value()) {
      return make_unique<DistEq>(Dist(m_squared_dist), r.value());
    }
    return clone();
  }

  bool SquaredDistEq::check_nondegen() const {
    return m_squared_dist.check_nondegen();
  }

  bool SquaredDistEq::check_equations() const {
    return approx_eq(double(SquaredDist(m_squared_dist)), nnrat2double(m_rhs));
  }

  optional<Equation<SinOrDist>> SquaredDistEq::as_equation_sin_or_dist() const {
    return LinearCombination<SinOrDist>(SinOrDist(m_squared_dist)) == RootRat(m_rhs);
  }

  optional<Equation<SquaredDist>> SquaredDistEq::as_equation_squared_dist() const {
    return LinearCombination<SquaredDist>(m_squared_dist) == nnrat2rat(m_rhs);
  }

  boost::json::object SquaredDistEq::to_json() const {
    vector<string> args = {
      m_squared_dist.left().name(),
      m_squared_dist.right().name(),
      nnrat2string(m_rhs)
    };
    return {
      {"name", "l2const"},
      {"points", boost::json::value_from(args)}
    };
  }

  ostream &SquaredDistEq::print(std::ostream &out) const {
    return out << m_squared_dist << " = " << m_rhs;
  }

  vector<statement_arg> SquaredDistEq::args() const { // Removed std::vector
    return {
      statement_arg(in_place_type<SquaredDist>, m_squared_dist),
      statement_arg(in_place_type<NNRat>, m_rhs)
    };
  }

} // namespace Yuclid
