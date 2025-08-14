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
#include "squared_dist.hpp"
#include "dist.hpp"
#include "type/point.hpp"
#include <algorithm> // For std::min and std::max
#include <cstddef>
#include <iostream>  // For std::ostream
#include <boost/container_hash/hash.hpp>
#include <stdexcept>

using namespace std;

namespace Yuclid {

  /**
   * @brief Constructs a `SquaredDist` object from two points.
   *
   * Ensures canonical ordering: `m_left` will always store the point
   * that is less than or equal to `m_right` based on their internal indexes.
   *
   * @param p1 The first point.
   * @param p2 The second point.
   */
  SquaredDist::SquaredDist(Point p1, Point p2)
    : m_left(min(p1, p2)), // Assign the smaller-indexed point to m_left
      m_right(max(p1, p2)) // Assign the larger-indexed point to m_right
  {
    if (m_left == m_right) [[unlikely]] {
      throw runtime_error("Tried to construct a `SquaredDist` with equal arguments");
    }
  }

  /**
   * @brief Implicit conversion operator to `Yuclid::double`.
   *
   * Calculates the squared Euclidean distance between the `m_left` and `m_right`
   * points using their `x()` and `y()` coordinates obtained from the global problem data.
   * Formula: $(x_2 - x_1)^2 + (y_2 - y_1)^2$
   *
   * @return The squared length of the segment as a `double`.
   */
  SquaredDist::operator double() const {
    // Calculate the differences
    double const dx = m_right.x() - m_left.x();
    double const dy = m_right.y() - m_left.y();

    // Calculate and return the squared Euclidean distance
    return (dx * dx) + (dy * dy);
  }

  SquaredDist::operator Dist() const {
    return {m_left, m_right};
  }

  size_t hash_value(const SquaredDist& arg) {
    size_t seed = 0;
    boost::hash_combine(seed, arg.left());
    boost::hash_combine(seed, arg.right());
    return seed;
  }

  /**
   * @brief Overloads the output stream operator for `SquaredDist` objects.
   *
   * Prints the squared distance in the format `|A-B|^2`, where A and B are the
   * names of the `m_left` and `m_right` points, respectively.
   *
   * @param os The output stream.
   * @param sd The `SquaredDist` object to print.
   * @return The output stream.
   */
  ostream &operator<<(ostream &os, const SquaredDist &sd) {
    os << "|" << sd.left().name() << "-" << sd.right().name() << "|^2";
    return os;
  }

} // namespace Yuclid
