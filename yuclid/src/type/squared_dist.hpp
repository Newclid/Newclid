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
#pragma once
#include "point.hpp"         // For the point class

#include <utility>   // For std::pair, used indirectly
#include <cstddef>   // For size_t, used indirectly

namespace Yuclid {

  // Forward declaration of the 'Dist' class for explicit conversion
  class Dist;

  /**
   * @brief Represents the squared Euclidean distance between two points.
   *
   * This class stores two const `Point` members, `m_left` and `m_right`,
   * ensuring canonical ordering (`m_left <= m_right`) upon construction.
   * It provides read-only access to its endpoints
   * and can be explicitly converted to `double`,
   * which calculates the squared Euclidean distance between the two points.
   */
  class SquaredDist final {
  private:
    const Point m_left;  /**< The "left" endpoint of the segment (canonically ordered). */
    const Point m_right; /**< The "right" endpoint of the segment (canonically ordered). */

  public:
    /**
     * @brief Constructs a `SquaredDist` object from two points.
     *
     * Ensures canonical ordering: `m_left` will always store the point
     * that is less than or equal to `m_right` based on their internal indexes.
     *
     * @param p1 The first point.
     * @param p2 The second point.
     */
    SquaredDist(Point p1, Point p2);

    /**
     * @brief Gets the left (smaller indexed) endpoint of the segment.
     * @return A const reference to the `m_left` point.
     */
    [[nodiscard]] const Point& left() const { return m_left; }

    /**
     * @brief Gets the right (larger indexed) endpoint of the segment.
     * @return A const reference to the `m_right` point.
     */
    [[nodiscard]] const Point& right() const { return m_right; }

    /**
     * @brief Explicit conversion operator to `double`.
     *
     * Calculates the squared Euclidean distance between the `m_left` and `m_right`
     * points using their `x()` and `y()` coordinates obtained from the global problem data.
     * Formula: $(x_2 - x_1)^2 + (y_2 - y_1)^2$
     *
     * @return The squared length of the segment as a `double`.
     */
    explicit operator double() const;

    /**
     * @brief Explicit conversion operator to `dist`.
     *
     * Creates a `dist` object from this `SquaredDist` object.
     *
     * @return A `dist` object representing the non-squared distance.
     */
    explicit operator Dist() const;

    /**
     * @brief Compares two `SquaredDist` objects.
     *
     * This provides default comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`)
     * based on the lexical comparison of `m_left` and then `m_right` members.
     */
    auto operator<=>(const SquaredDist &other) const = default;

    [[nodiscard]] std::array<Point, 2> points() const {
      return {m_left, m_right};
    }

    [[nodiscard]] bool check_nondegen() const {
      return !m_left.is_close(m_right);
    }
  };

  size_t hash_value(const SquaredDist& arg);

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
  std::ostream &operator<<(std::ostream &os, const SquaredDist &sd);

} // namespace Yuclid
