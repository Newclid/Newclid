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
#include "statement/statement.hpp"
#include <compare>     // For operator<=>
#include <stdexcept>   // For std::invalid_argument
#include <vector>      // For std::vector (statement_arg)

namespace Yuclid {
  class Collinear;
  class DistEqDist;

  class Midpoint : public Statement {
  public:
    Midpoint(Point left, Point middle, Point right);
    explicit Midpoint(const std::vector<statement_arg>& args);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override;

    [[nodiscard]] const Point &left() const { return m_left; }
    [[nodiscard]] const Point &middle() const { return m_middle; }
    [[nodiscard]] const Point &right() const { return m_right; }

    [[nodiscard]] Collinear to_coll() const;
    [[nodiscard]] DistEqDist to_cong() const;

    [[nodiscard]] boost::json::object to_json() const override;
    std::ostream &print(std::ostream &out) const override;

    [[nodiscard]] std::vector<Point> points() const override;

    // Defaulted three-way comparison operator
    auto operator<=>(const Midpoint &other) const = default;
  private:
    /** Left endpoint. */
    Point m_left;
    /** Midpoint. */
    Point m_middle;
    /** Right endpoint. */
    Point m_right;
  };

} // namespace Yuclid
