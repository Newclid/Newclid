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
#include "typedef.hpp" // For the double type
#include "numbers/add_circle.hpp" // For the AddCircle template class

#include <utility>   // For std::min, std::max
#include <cstddef>   // For size_t, used indirectly
#include <stdexcept> // For std::runtime_error

namespace Yuclid {

  /**
   * @brief Represents the slope angle of a line segment.
   *
   * This class calculates the oriented angle of the line segment formed by two points
   * relative to the positive x-axis. The angle is normalized to the [0, 1) range,
   * where 1.0 represents $\pi$ radians (or 180 degrees).
   *
   * The constructor ensures canonical ordering of points (`m_left < m_right`)
   * and throws an exception if the points are too close to prevent division-by-zero
   * or ill-defined angles.
   */
  class SlopeAngle final {
  private:
    Point m_left;  /**< The "left" endpoint of the segment (canonically ordered). */
    Point m_right; /**< The "right" endpoint of the segment (canonically ordered). */

  public:
    /**
     * @brief Constructs a `SlopeAngle` object from two points.
     *
     * Ensures canonical ordering: `m_left` will always store the point
     * that is less than or equal to `m_right` based on their internal indexes.
     * Throws `std::runtime_error` if the two points are equal.
     *
     * @param p1 The first point.
     * @param p2 The second point.
     * @throws std::runtime_error if points are equal.
     */
    SlopeAngle(Point p1, Point p2);

    /** @brief Check if the slope is nondegenerate.
     *
     * @return `true` if the points aren't too close.
     */
    [[nodiscard]] bool check_nondegen() const { return !m_left.is_close(m_right); }

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
     * @brief Explicit conversion operator to `Yuclid::AddCircle<double>`.
     *
     * Calculates the oriented angle of the line segment formed by `m_left` and `m_right`
     * points using `atan2(dy, dx)`, then normalizes it to the [0, 1) range
     * where 1.0 corresponds to $\pi$ radians.
     *
     * @return An `AddCircle<double>` object containing the normalized slope angle.
     */
    explicit operator AddCircle<double>() const;

    /**
     * @brief Compares two `SlopeAngle` objects.
     *
     * This provides default comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`)
     * based on the lexical comparison of `m_left` and then `m_right` members.
     */
    auto operator<=>(const SlopeAngle &other) const = default;

    [[nodiscard]] std::array<Point, 2> points() const {
      return {m_left, m_right};
    }
  };

  size_t hash_value(const SlopeAngle& arg);

  /**
   * @brief Overloads the output stream operator for `SlopeAngle` objects.
   *
   * Prints the slope angle representation in the format `∠(A-B)`,
   * where A and B are the names of the `m_left` and `m_right` points.
   *
   * @param os The output stream.
   * @param sa The `SlopeAngle` object to print.
   * @return The output stream.
   */
  std::ostream &operator<<(std::ostream &os, const SlopeAngle &sa);

} // namespace Yuclid
