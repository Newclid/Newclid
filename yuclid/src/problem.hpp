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
#include <ranges>
#include <string>
#include <vector>
#include <cstddef>

#include "statement/statement.hpp"
#include "type/named_point.hpp"
#include "typedef.hpp"

namespace Yuclid {

  /**
   * @brief Manages the global problem data, including point names and coordinates.
   *
   * This class is designed to be stored as a thread-local instance to manage
   * problem-specific data such as point names, coordinates, and their total count.
   * It inherits from `theorem` and provides methods to add points and
   * access the stored data.
   */
  class Problem final {
  private:
    /** Points' names and coordinates. */
    std::vector<NamedPoint> m_points;

    /** Hypotheses of the problem. */
    std::vector<std::unique_ptr<Statement>> m_hypotheses;
    /** Goals of the problem. */
    std::vector<std::unique_ptr<Statement>> m_goals;
    /** Name of the problem. */
    std::string m_name;

  public:

    /**
     * @brief Default constructor. Initializes an empty problem.
     *
     * Sets the initial number of points to zero.
     */
    constexpr Problem() = default;

    /**
     * @brief Adds a point with a given name and coordinates to the problem.
     *
     * If a point with the same name already exists in the current thread's
     * problem instance, throws `std::runtime_error`.
     * Otherwise, the new point's name and coordinates are added to the internal storage,
     * and the function returns the new `Point` object.
     *
     * @param name The wide string name of the point to add.
     * @param x The x-coordinate of the point, using 'double' type.
     * @param y The y-coordinate of the point, using 'double' type.
     * @return The new Point object.
     */
    [[nodiscard]] Point add_point(const std::string &name, double x, double y);

    /**
     * @brief Set problem's name
     */
    void set_name(const std::string &name);

    /**
     * @brief Add a hypothesis to the problem.
     */
    void add_hypothesis(std::unique_ptr<Statement> &&p);

    [[nodiscard]] const std::vector<std::unique_ptr<Statement>>& hypotheses() const;

    void add_goal(std::unique_ptr<Statement> &&p);

    [[nodiscard]] const std::vector<std::unique_ptr<Statement>>& goals() const;

    /**
     * @brief Gets the name of the point.
     *
     * @param pt The point object representing the index.
     * @return The name of the point.
     * @throws std::out_of_range if the point's index is out of bounds.
     */
    [[nodiscard]] const std::string& point_name(Point pt) const;

    /**
     * @brief Gets the x-coordinate of the point.
     *
     * @param pt The point object representing the index.
     * @return The x-coordinate of the point, using 'double' type.
     * @throws std::out_of_range if the point's index is out of bounds.
     */
    [[nodiscard]] double get_x(Point pt) const;

    /**
     * @brief Gets the y-coordinate of the point.
     *
     * @param pt The point object representing the index.
     * @return The y-coordinate of the point, using 'double' type.
     * @throws std::out_of_range if the point's index is out of bounds.
     */
    [[nodiscard]] double get_y(Point pt) const;

    /**
     * @brief Gets the total number of points currently stored in the problem.
     *
     * @return The total number of points.
     */
    [[nodiscard]] size_t num_points() const;

    /**
     * @brief Generates all points currently defined in the problem.
     *
     * This method uses Ranges library to create an `std::views` compatible object
     * that yields all `Point`s in the problem.
     *
     * @return An `std::views` compatible object that yields all `Point`s in the problem.
     */
    [[nodiscard]] auto all_points() const {
      return std::views::iota(static_cast<size_t>(0), num_points())
        | std::views::transform([this](size_t ind) { return Point(ind, this); });
    }

    /**
     * @brief Find a point by its name.
     *
     * @return A point with a given name.
     */
    [[nodiscard]] Point find_point(const std::string &name) const;
  };

} // namespace Yuclid
