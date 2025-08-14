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
#include "eqratio.hpp"
#include <memory>
#include <optional>
#include <ostream>
#include <string>
#include <utility>
#include <algorithm>
#include "ar/equation.hpp"
#include "ar/linear_combination.hpp"
#include <vector>
#include "numbers/util.hpp"
#include "statement/statement.hpp"
#include "type/dist.hpp"
#include "type/point.hpp"
#include "typedef.hpp"

using namespace std;

namespace Yuclid {

  EqualRatios::EqualRatios(Dist num_left, Dist den_left,
                           Dist num_right, Dist den_right)
    : m_num_left(num_left), m_den_left(den_left),
      m_num_right(num_right), m_den_right(den_right) {}

  string EqualRatios::name() const { return "eqratio"; }

  vector<Point> EqualRatios::points() const {
    return {
      m_num_left.left(), m_num_left.right(),
      m_den_left.left(), m_den_left.right(),
      m_num_right.left(), m_num_right.right(),
      m_den_right.left(), m_den_right.right()
    };
  }

  unique_ptr<Statement> EqualRatios::normalize() const {
    /* TODO: re-enable and do the same on the Python side?
    if (num_left() == num_right()) {
      return DistEqDist(den_left(), den_right()).normalize();
    }
    if (den_left() == den_right()) {
      return DistEqDist(num_left(), num_right()).normalize();
    }
    if (num_left() == den_left()) {
      return DistEqDist(num_right(), den_right()).normalize();
    }
    if (num_right() == den_right()) {
      return DistEqDist(num_left(), den_left()).normalize();
    }
    if (num_left() == den_right() && num_right() == den_left()) {
      return DistEqDist(num_left(), num_right()).normalize();
    }
    */
    Dist a = num_left();
    Dist b = den_left();
    Dist c = num_right();
    Dist d = den_right();

    if (min(a, b) > min(c, d)) {
      std::swap(a, c);
      std::swap(b, d);
    }

    if (a > b) {
      swap(a, b);
      swap(c, d);
    }
    // Now `a` is the minimal element. Make sure that `b <= c`;
    if (b > c) {
      swap(b, c);
    }
    return make_unique<EqualRatios>(EqualRatios{a, b, c, d});
  }

  bool EqualRatios::check_nondegen() const {
    return
      !m_num_left.left().is_close(m_num_left.right()) &&
      !m_den_left.left().is_close(m_den_left.right()) &&
      !m_num_right.left().is_close(m_num_right.right()) &&
      !m_den_right.left().is_close(m_den_right.right());
  }

  bool EqualRatios::check_equations() const {
    return approx_eq(double(m_num_left) * double(m_den_right), double(m_num_right) * double(m_den_left));
  }

  optional<Equation<SinOrDist>> EqualRatios::as_equation_sin_or_dist() const {
    return
      LinearCombination<SinOrDist>(SinOrDist(m_num_left)) -
      LinearCombination<SinOrDist>(SinOrDist(m_den_left)) -
      LinearCombination<SinOrDist>(SinOrDist(m_num_right)) +
      LinearCombination<SinOrDist>(SinOrDist(m_den_right)) == RootRat();
  }

  vector<statement_arg> EqualRatios::args() const {
    return {
      statement_arg(in_place_type<Dist>, m_num_left),
      statement_arg(in_place_type<Dist>, m_den_left),
      statement_arg(in_place_type<Dist>, m_num_right),
      statement_arg(in_place_type<Dist>, m_den_right)
    };
  }

  std::ostream &EqualRatios::print(std::ostream &out) const {
    out << m_num_left << ":" << m_den_left << " = " << m_num_right << ":" << m_den_right;
    return out;
  }

} // namespace Yuclid
