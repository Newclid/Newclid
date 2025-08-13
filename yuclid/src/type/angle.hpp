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
#include "slope_angle.hpp"   // For SlopeAngle class
#include "typedef.hpp" // For the double type
#include "numbers/add_circle.hpp" // For the AddCircle template class

#include <boost/container_hash/hash.hpp>

namespace Yuclid {

  /**
   * @brief Represents an angle formed by three points: left, vertex, and right.
   *
   * An `angle` object is defined by three `point`s (A, B, C) where B is the vertex.
   * The constructor validates that the vertex is not too close to either A or C.
   * It provides access to its constituent points and `SlopeAngle`s representing
   * its left and right sides. It can be explicitly converted to an `AddCircle<double>`
   * representing the normalized difference between the right and left slope angles.
   */
  class Angle final {
  private:
    Point m_left_pt;   /**< The left point of the angle (A). */
    Point m_vertex_pt; /**< The vertex point of the angle (B). */
    Point m_right_pt;  /**< The right point of the angle (C). */

  public:
    /**
     * @brief Constructs an `angle` object from three points.
     *
     * Throws `std::runtime_error` if the vertex point `vertex_pt` is equal
     * to either `left_pt` or `right_pt`.
     *
     * @param left_pt The left point (A).
     * @param vertex_pt The vertex point (B).
     * @param right_pt The right point (C).
     * @throws std::runtime_error if the vertex is too close to an endpoint.
     */
    Angle(Point left_pt, Point vertex_pt, Point right_pt);

    Angle() = delete;

    /** @brief Checks if the angle is nondegenerate.
     *
     * Returns `true` if the vertex isn't too close to left/right pts
     * and the points aren't collinear.
     *
     * Note that zero/straight angle is not rejected.
     * If a theorem doesn't work in this case,
     * then it should explicitly assume that the points aren't collinear.
     */
    [[nodiscard]] bool check_nondegen() const;

    /**
     * @brief Gets the left point (A) of the angle.
     * @return A const reference to the left point.
     */
    [[nodiscard]] const Point& left() const { return m_left_pt; }

    /**
     * @brief Gets the vertex point (B) of the angle.
     * @return A const reference to the vertex point.
     */
    [[nodiscard]] const Point& vertex() const { return m_vertex_pt; }

    /**
     * @brief Gets the right point (C) of the angle.
     * @return A const reference to the right point.
     */
    [[nodiscard]] const Point& right() const { return m_right_pt; }

    /**
     * @brief Creates a `SlopeAngle` representing the left side of the angle (segment B-A).
     * @return A `SlopeAngle` object for the segment from vertex to left point.
     */
    [[nodiscard]] SlopeAngle left_side() const;

    /**
     * @brief Creates a `SlopeAngle` representing the right side of the angle (segment B-C).
     * @return A `SlopeAngle` object for the segment from vertex to right point.
     */
    [[nodiscard]] SlopeAngle right_side() const;

    /**
     * @brief Swap left and right points of an angle.
     */
    Angle operator-() const { return {m_right_pt, m_vertex_pt, m_left_pt}; }

    /**
     * @brief Explicit conversion operator to `Yuclid::AddCircle<double>`.
     *
     * Calculates the oriented angle from `left_side` to `right_side` by subtracting
     * the left slope angle from the right slope angle. The result is normalized
     * to the [0, 1) range by the `AddCircle` constructor.
     *
     * @return An `AddCircle<double>` object representing the normalized angle value.
     */
    explicit operator AddCircle<double>() const;

    /**
     * @brief Compute the dot product of the sides of the angle.
     */
    [[nodiscard]] double dot_product() const;

    /**
     * @brief Compares two `angle` objects.
     *
     * This provides default comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`)
     * based on the lexical comparison of `m_left_pt`, then `m_vertex_pt`, then `m_right_pt`.
     */
    auto operator<=>(const Angle &other) const = default;

    [[nodiscard]] std::array<Point, 3> points() const {
      return {m_left_pt, m_vertex_pt, m_right_pt};
    }
  };

  size_t hash_value(const Angle& arg);

  /**
   * @brief Overloads the output stream operator for `angle` objects.
   *
   * Prints the angle in the format `∠(A-B-C)`, where A, B, and C are the
   * names of the `m_left_pt`, `m_vertex_pt`, and `m_right_pt` respectively.
   *
   * @param os The output stream.
   * @param ang The `angle` object to print.
   * @return The output stream.
   */
  std::ostream &operator<<(std::ostream &os, const Angle &ang);

} // namespace Yuclid
