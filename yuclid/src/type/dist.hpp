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
#include "point.hpp"
#include "typedef.hpp"
#include <cstddef>

namespace Yuclid {
  class SquaredDist;
  class SinOrDist;

  /**
   * @brief Represents the Euclidean distance (non-squared) between two points.
   *
   * This class stores two const `point` members, `m_left` and `m_right`,
   * ensuring canonical ordering (`m_left <= m_right`) upon construction.
   * It provides read-only access to its endpoints
   * and can be explicitly converted to `double`,
   * which calculates the Euclidean distance between the two points.
   */
  class Dist final {
  private:
    Point m_left;  /**< The "left" endpoint of the segment (canonically ordered). */
    Point m_right; /**< The "right" endpoint of the segment (canonically ordered). */

  public:
    /**
     * @brief Constructs a `dist` object from two points.
     *
     * Ensures canonical ordering: `m_left` will always store the point
     * that is less than or equal to `m_right` based on their internal indexes.
     *
     * @param p1 The first point.
     * @param p2 The second point.
     */
    Dist(Point p1, Point p2);

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
     * Calculates the Euclidean distance between the `m_left` and `m_right`
     * points using their `x()` and `y()` coordinates obtained from the global problem data.
     * Formula: $\sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$
     *
     * @return The Euclidean distance of the segment as a `double`.
     */
    explicit operator double() const;

    /**
     * @brief Explicit conversion operator to `squared_dist`.
     *
     * Creates a `squared_dist` object from this `dist` object.
     *
     * @return A `squared_dist` object representing the squared distance.
     */
    explicit operator SquaredDist() const;

    /**
     * @brief Explicit conversion operator to `SinOrDist`.
     *
     * Creates a `SinOrDist` object from this `Dist` object.
     *
     * @return A `SinOrDist` object representing the distance in the ratio AR table.
     */
    explicit operator SinOrDist() const;

    /**
     * @brief Compares two `dist` objects.
     *
     * This provides default comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`)
     * based on the lexical comparison of `m_left` and then `m_right` members.
     */
    auto operator<=>(const Dist &other) const = default;

    [[nodiscard]] std::array<Point, 2> points() const {
      return {m_left, m_right};
    }

    [[nodiscard]] bool check_nondegen() const {
      return !m_left.is_close(m_right);
    }
  };

  size_t hash_value(const Dist& arg);

  /**
   * @brief Overloads the output stream operator for `dist` objects.
   *
   * Prints the distance in the format `|A-B|`, where A and B are the
   * names of the `m_left` and `m_right` points, respectively.
   *
   * @param os The output stream.
   * @param d The `dist` object to print.
   * @return The output stream.
   */
  std::ostream &operator<<(std::ostream &os, const Dist &d);

} // namespace Yuclid
