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
#include "slope_angle.hpp"
#include "point.hpp"         // For point::is_close() and coordinate access
#include "typedef.hpp" // For double type
#include "numbers/add_circle.hpp" // For AddCircle
#include <algorithm> // For std::min, std::max
#include <cmath>     // For std::atan2, std::fabs
#include <cstddef>
#include <string>    // For std::string (used by point::name())
#include <iostream>  // For std::ostream
#include <stdexcept> // For std::runtime_error
#include <numbers>   // For std::numbers::pi_v (C++20 and later)
#include <boost/container_hash/hash.hpp>

using namespace std;

namespace Yuclid { // Consolidate into a single namespace block

  SlopeAngle::SlopeAngle(Point p1, Point p2)
    : m_left(std::min(p1, p2)),
      m_right(std::max(p1, p2))
  {
    if (m_left == m_right) {
      string error_msg = "Error: Cannot create SlopeAngle for points that are eqal: ";
      error_msg += m_left.name() + " and " + m_right.name();
      throw runtime_error(error_msg);
    }
  }

  SlopeAngle::operator AddCircle<double>() const {
    // Retrieve coordinates from the points
    double const x1 = m_left.x();
    double const y1 = m_left.y();
    double const x2 = m_right.x();
    double const y2 = m_right.y();

    // Calculate delta x and delta y
    double const dx = x2 - x1;
    double const dy = y2 - y1;

    // Calculate the angle using atan2. atan2 returns angle in radians in range (-pi, pi].
    double const angle_radians = atan2(dy, dx);

    // Normalize the angle to be in terms of pi (where 1.0 represents pi radians).
    // The AddCircle constructor will then normalize this result to the [0, 1) range.
    double const normalized_by_pi = angle_radians / std::numbers::pi_v<double>;

    return AddCircle<double>(normalized_by_pi);
  }

  size_t hash_value(const SlopeAngle& arg) {
    size_t seed = 0;
    boost::hash_combine(seed, arg.left());
    boost::hash_combine(seed, arg.right());
    return seed;
  }

  std::ostream &operator<<(std::ostream &os, const SlopeAngle &sa) {
    os << "∠(" << sa.left().name() << "-" << sa.right().name() << ")";
    return os;
  }

} // namespace Yuclid
