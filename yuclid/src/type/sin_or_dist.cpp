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
#include "angle.hpp"
#include "squared_dist.hpp"
#include "sin_or_dist.hpp"
#include "typedef.hpp"
#include "numbers/posreal.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <numbers>
#include <ostream>
#include <ranges>
#include <variant>
#include <vector>

using namespace std;

namespace Yuclid {

  SinOrDist::SinOrDist(const Angle &a) : m_data(min(a, -a)) { }
  SinOrDist::SinOrDist(const SquaredDist &d) : m_data(d) { }

  SinOrDist::operator Posreal() const {
    if (holds_alternative<Angle>(m_data)) {
      // Get the angle as a number in [0, 1)
      AddCircle<double> const a(get<Angle>(m_data));
      double const s = sin(a.number() * numbers::pi_v<double>);
      return Posreal(s * s);
    }
    return Posreal(double(get<SquaredDist>(m_data)));
  }

  vector<Point> SinOrDist::points() const {
    if (holds_alternative<Angle>(m_data)) {
      return angle().points() | ranges::to<vector>();
    }
    return get_squared_dist().points() | ranges::to<vector>();
  }

  bool SinOrDist::check_nondegen() const {
    if (holds_alternative<Angle>(m_data)) {
      return angle().check_nondegen();
    }
    return get_squared_dist().check_nondegen();
  };

  size_t hash_value(const SinOrDist& arg) {
    if (arg.is_sin()) {
      return hash_value(arg.angle());
    }
    return hash_value(arg.get_squared_dist());
  }

  std::ostream &operator<<(std::ostream &os, const SinOrDist &md) {
    if (md.is_sin()) {
      return os << "\\sin² " << md.angle();
    }
    return os << md.get_squared_dist();
  }

} // namespace Yuclid
