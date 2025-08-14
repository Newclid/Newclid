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
#include <cstddef>   // For size_t
#include <iostream>  // For std::ostream
#include <ranges>
#include <string>    // For std::string
#include <boost/json.hpp>

#include "typedef.hpp" // For Yuclid::double

namespace Yuclid {
  class Problem;

  /**
   * @brief Represents a point in a problem, storing only its index.
   *
   * For performance reasons, `point` instances only store an index.
   * Actual coordinate and name data are retrieved from a global (thread-local)
   * `problem` instance when needed.
   */
  class Point final {
  private:
    size_t m_data; /**< The index of the point in the global problem data. */
    /** The problem that owns this point. */
    const Problem *m_problem;

  public:
    Point() = delete;

    /**
     * @brief Constructs a `point` from an integer index.
     * @param ind The zero-based index of the point.
     */
    constexpr Point(size_t ind, const Problem *owner) noexcept :
      m_data(ind), m_problem(owner) { };

    /**
     * @brief Gets the raw index stored by the point.
     * @return The integer index of the point.
     */
    [[nodiscard]] constexpr size_t get() const { return m_data; };

    /**
     * @brief Queries the `x` coordinate of the point from the global problem data.
     * @return The x-coordinate as a `double`.
     * @throws std::out_of_range if the point's index is invalid.
     */
    [[nodiscard]] double x() const;

    /**
     * @brief Queries the `y` coordinate of the point from the global problem data.
     * @return The y-coordinate as a `double`.
     * @throws std::out_of_range if the point's index is invalid.
     */
    [[nodiscard]] double y() const;

    /**
     * @brief Queries the name of the point from the global problem data.
     * @return A const reference to the `std::string` name of the point.
     * @throws std::out_of_range if the point's index is invalid.
     */
    [[nodiscard]] const std::string &name() const;

    /**
     * @brief Checks if this point is too close to another point.
     *
     * Two points are considered "too close" if both their x and y coordinates
     * differ by at most a predefined epsilon (1E-7).
     *
     * @param other The other point to compare against.
     * @return True if the points are too close, false otherwise.
     */
    [[nodiscard]] bool is_close(const Point &other) const;

    /**
     * @brief Compares two points by their internal indexes.
     *
     * Provides all comparison operators (`<`, `<=`, `>`, `>=`, `==`, `!=`)
     * based on the underlying `size_t` index.
     */
    auto operator<=>(const Point &other) const = default;

    /**
     * @brief Generates all points that are strictly less than this point's index.
     *
     * This method uses `std::views` to lazily yield `Point` objects
     * with indexes from 0 up to `this->get() - 1`.
     *
     * @return An `std::views` compatible object that yields `Point` objects.
     */
    [[nodiscard]] auto up_to() const {
      return std::views::iota(static_cast<size_t>(0), m_data)
        | std::views::transform([this](size_t ind) {
          return Point(ind, m_problem);
        });
    }
  };

  inline size_t hash_value(const Point& arg) { return arg.get(); }

  /**
   * @brief Overloads the output stream operator for `point` objects.
   *
   * Prints the point's index, name, x-coordinate, and y-coordinate to the stream.
   * Handles cases where the point's index might be invalid by catching `std::out_of_range`.
   *
   * @param os The output stream.
   * @param pt The point object to print.
   * @return The output stream.
   */
  std::ostream &operator<<(std::ostream &out, const Point &pt);

  void tag_invoke(boost::json::value_from_tag /*unused*/,
                  boost::json::value& jval,
                  const Point& pt);

} // namespace Yuclid
