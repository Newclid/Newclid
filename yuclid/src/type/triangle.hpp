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
#include <array>
#include "point.hpp"

namespace Yuclid {
  class Angle;
  class Dist;

  /**
   * @brief A triangle with vertices `a()`, `b()`, `c()`.
   *
   * This class holds three `Point`s available via `a()`, `b()`, and `c()`.
   */
  class Triangle final {
  private:
    Point m_a, m_b, m_c;
  public:
    Triangle() = delete;
    /**
     * @brief Construct a triangle with given vertices.
     */
    Triangle(Point a, Point b, Point c) noexcept;

    /**
     * @brief Oriented area of a triangle.
     *
     * Compute the oriented area of the triangle
     * as half of the cross product of two of its sides.
     *
     * @return the oriented area of the triangle.
     */
    [[nodiscard]] double area() const;

    /**
     * @brief Vertex `a`
     *
     * Get vertex `a` of the triangle.
     */
    [[nodiscard]] const Point &a() const { return m_a; }
    /**
     * @brief Vertex `b`.
     *
     * Get vertex `b` of the triangle.
     */
    [[nodiscard]] const Point &b() const { return m_b; }
    /**
     * @brief Vertex `c`.
     *
     * Get vertex `c` of the triangle.
     */
    [[nodiscard]] const Point &c() const { return m_c; }
    /**
     * @brief Vertices of the triangle.
     *
     * Get all vertices of the triangle as an `std::array`.
     */
    [[nodiscard]] std::array<Point, 3> points() const {
      return {m_a, m_b, m_c};
    }

    /**
     * @brief Angle `∠CAB` of the triangle.
     *
     * @return an `Angle` object that corresponds to `∠CAB`.
     */
    [[nodiscard]] Angle angle_a() const;
    /**
     * @brief Angle `∠ABC` of the triangle.
     *
     * @return an `Angle` object that corresponds to `∠ABC`.
     */
    [[nodiscard]] Angle angle_b() const;
    /**
     * @brief Angle `∠BCA` of the triangle.
     *
     * @return an `Angle` object that corresponds to `∠BCA`.
     */
    [[nodiscard]] Angle angle_c() const;

    /**
     * @brief Side `AB` of the triangle.
     *
     * @return a `Dist` object that corresponds to `|AB|`.
     */
    [[nodiscard]] Dist dist_ab() const;
    /**
     * @brief Side `AC` of the triangle.
     *
     * @return a `Dist` object that corresponds to `|AC|`.
     */
    [[nodiscard]] Dist dist_ac() const;
    /**
     * @brief Side `BC` of the triangle.
     *
     * @return a `Dist` object that corresponds to `|BC|`.
     */
    [[nodiscard]] Dist dist_bc() const;

    /**
     * @brief Get `ind`th vertex of the triangle.
     *
     * For indexes outside of `[0, 3)`, take `ind % 3` first.
     */
    Point operator[](size_t ind) const;
    /**
     * @brief All cyclic rotations of a triangle.
     *
     * @return an array with triangles `ABC`, `BCA`, and `CAB`.
     */
    [[nodiscard]] std::array<Triangle, 3> cyclic_rotations() const;
    /**
     * @brief All permutations of the vertices of a triangle.
     *
     * @return an array with all triangles with vertices `A`, `B`, `C`
     * in some order.
     */
    [[nodiscard]] std::array<Triangle, 6> permutations() const;
    /**
     * @brief Sides of the triangle as `Dist`s
     *
     * @return an array with sides `AB`, `BC, `AC` as `Dist` objects.
     */
    [[nodiscard]] std::array<Dist, 3> dists() const;
    /**
     * @brief Angles of a triangle.
     *
     * @return an array with angles `∠ABC`, `∠BCA`, `∠CAB`
     * as `Angle` objects.
     */
    [[nodiscard]] std::array<Angle, 3> angles() const;
    /**
     * @brief Sort vertices of the triangle.
     *
     * @return a new triangle with vertices sorted by their indexes.
     */
    [[nodiscard]] Triangle sorted() const;

    /**
     * @brief Default 3-way comparison operator for `Triangle`s.
     *
     * This operator provides 3-way comparison `<=>`
     * for objects of type `Triangle`.
     */
    auto operator<=>(const Triangle &other) const = default;

    /**
     * @brief Check that the triangle is nondegenerate.
     *
     * @retval false if the vertices are collinear;
     * @retval true otherwise.
     */
    [[nodiscard]] bool check_nondegen() const;
  };

  /**
   * @brief Print a triangle to `std::ostream`.
   *
   * Prints the triangle in the format `▵ABC`,
   * where `A`, `B`, `C` are the names of the vertices.
   */
  std::ostream &operator<<(std::ostream &out, const Triangle &t);
}
