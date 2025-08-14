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
#include "statement/dist_eq.hpp"
#include "ar/equation.hpp"
#include "ar/linear_combination.hpp"
#include "numbers/util.hpp"
#include "statement/squared_dist_eq.hpp"
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

using namespace std;

namespace Yuclid {

  DistEq::DistEq(const Dist &d, const NNRat &r) :
    m_dist(d), m_rhs(r)
  { }

  std::string DistEq::name() const {
    return "lconst";
  }

  std::vector<Point> DistEq::points() const {
    return {m_dist.left(), m_dist.right()};
  }

  std::unique_ptr<Statement> DistEq::normalize() const {
    return clone();
  }

  bool DistEq::check_nondegen() const {
    return m_dist.check_nondegen();
  }

  bool DistEq::check_equations() const {
    return approx_eq(double(m_dist), m_rhs);
  }

  SquaredDistEq DistEq::as_squared_dist_eq() const {
    return {SquaredDist(m_dist), m_rhs * m_rhs};
  }

  std::optional<Equation<Dist>> DistEq::as_equation_dist() const {
    return LinearCombination<Dist>(m_dist) == nnrat2rat(m_rhs);
  }

  std::optional<Equation<SquaredDist>> DistEq::as_equation_squared_dist() const {
    return as_squared_dist_eq().as_equation<SquaredDist>();
  }

  std::optional<Equation<SinOrDist>> DistEq::as_equation_sin_or_dist() const {
    return as_squared_dist_eq().as_equation<SinOrDist>();
  }
  
  std::vector<statement_arg> DistEq::args() const {
    return {
      statement_arg(in_place_type<Dist>, m_dist),
      statement_arg(in_place_type<NNRat>, m_rhs)
    };
  }

  boost::json::object DistEq::to_json() const {
    std::vector<string> args = {
      m_dist.left().name(),
      m_dist.right().name(),
      nnrat2string(m_rhs)
    };
    return {
      {"name", name()},
      {"points", boost::json::value_from(args)}
    };
  }

  std::ostream &DistEq::print(std::ostream &out) const {
    return out << m_dist << " = " << m_rhs;
  }

} // namespace Yuclid
