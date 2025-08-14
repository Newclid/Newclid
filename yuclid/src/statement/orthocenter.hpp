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
#include <memory>
#include <string>
#include <vector>
#include <variant>
#include <optional>
#include "statement.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp"

namespace Yuclid {
  class Perpendicular;

  /**
   * @brief statement saying that a point is the orthocenter of a triangle.
   */
  class IsOrthocenter : public Statement {
  public:
    IsOrthocenter(const Triangle &t, const Point &p);
    IsOrthocenter(const std::vector<statement_arg> &args);

    [[nodiscard]] std::string name() const override;
    /**
     * @brief Ensure that the triangle is sorted.
     */
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    auto operator<=>(const IsOrthocenter &other) const = default;

    [[nodiscard]] Perpendicular perp_a() const;
    [[nodiscard]] Perpendicular perp_b() const;
    [[nodiscard]] Perpendicular perp_c() const;

    [[nodiscard]] const Triangle &triangle() const { return m_triangle; }
    [[nodiscard]] const Point &a() const { return m_triangle.a(); }
    [[nodiscard]] const Point &b() const { return m_triangle.b(); }
    [[nodiscard]] const Point &c() const { return m_triangle.c(); }
    [[nodiscard]] const Point &orthocenter() const { return m_orthocenter; }

    [[nodiscard]] std::vector<Point> points() const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<IsOrthocenter>(*this);
    }

    std::ostream &print(std::ostream &out) const override;

    ~IsOrthocenter() override = default;
  private:
    Triangle m_triangle;
    Point m_orthocenter;
  };

} // namespace Yuclid
