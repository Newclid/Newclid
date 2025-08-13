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
#include "angle.hpp"
#include "squared_dist.hpp"
#include "typedef.hpp" // For the double type

#include <cstddef>   // For size_t, used indirectly

namespace Yuclid {
  class Posreal;

  /**
   * @brief Represents a quantity in the ratio AR table.
   *
   * Two types are allowed:
   * - an angle `α` that evaluates to the `\sin² α`;
   * - a squared distance between two points.
   *
   * Objects of this type numerically evaluate to the type `Posreal`,
   * which represents positive double numbers
   * with `(a + b).number() == a.number() * b.number()`.
   */
  class SinOrDist final {
  private:
    const std::variant<Angle, SquaredDist> m_data;

  public:
    /**
     * @brief Constructs a `SinOrDist` object from an angle.
     *
     * The new object evaluates to `\sin² α`.
     */
    explicit SinOrDist(const Angle &a);

    /**
     * @brief Constructs a `SinOrDist` object from a squared distance.
     *
     * The new object evaluates to the same number.
     */
    explicit SinOrDist(const SquaredDist &d);

    /**
     * @brief Explicit conversion operator to `Yuclid::Posreal`.
     *
     * If the object stores an angle `α`, then evaluates `\sin² α`.
     * Otherwise, evaluates the squared distance between the endpoints.
     *
     * The result is then wrapped in a `Posreal` object.
     *
     * @return A `Posreal` object containing the squared length.
     */
    explicit operator Posreal() const;

    /** @brief Test if the object holds a sine of an angle. */
    [[nodiscard]] bool is_sin() const { return std::holds_alternative<Angle>(m_data); }

    /** @brief Test if the object holds a squared distance between two points. */
    [[nodiscard]] bool is_squared_dist() const;

    /**
     * @brief Get the angle stored in the object.
     *
     * @throws std::bad_variant_access if the object holds a squared distance instead.
     */
    [[nodiscard]] const Angle &angle() const {
      return std::get<Angle>(m_data);
    }

    /**
     * @brief Get the squared distance stored in the object.
     *
     * @throws std::bad_variant_access if the object holds an angle instead.
     */
    [[nodiscard]] const SquaredDist &get_squared_dist() const {
      return std::get<SquaredDist>(m_data);
    }

    /**
     * @brief Compares two `SinOrDist` objects.
     *
     * This provides default comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`).
     * All sines are sorted less than squared distances,
     * so that the "sin" part of the corresponding AR table
     * does not poison the "distance" part until it can prove
     * something that does not involve angles.
     *
     * We may decide to reevaluate this decision later.
     */
    auto operator<=>(const SinOrDist &other) const = default;

    /**
     * @brief Yield all points used in the object.
     */
    [[nodiscard]] std::vector<Point> points() const;

    /**
     * @brief Test if the underlying object is valid (nondegenerate).
     */
    [[nodiscard]] bool check_nondegen() const;
  };

  size_t hash_value(const SinOrDist& arg);

  /**
   * @brief Overloads the output stream operator for `SinOrDist` objects.
   *
   * For an angle, prints `\sin² a b c`.
   * For a squared distance, prints `|a b|²`.
   *
   * @param os The output stream.
   * @param md The `SinOrDist` object to print.
   * @return The output stream.
   */
  std::ostream &operator<<(std::ostream &os, const SinOrDist &md);

} // namespace Yuclid
