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
#include "statement.hpp"
#include "type/triangle.hpp"
#include "typedef.hpp" // Assuming point, triangle are defined here

namespace Yuclid {
  class DistEqDist;

  /**
   * Predicate saying that `center` is the circumcenter of a triangle.
   */
  class Circumcenter : public Statement {
  public:
    Circumcenter(Point center, Triangle tri);
    explicit Circumcenter(const std::vector<statement_arg>& args);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override;

    [[nodiscard]] DistEqDist cong_ab() const;
    [[nodiscard]] DistEqDist cong_bc() const;
    [[nodiscard]] DistEqDist cong_ac() const;

    // Public read-only access methods
    [[nodiscard]] const Point& center() const { return m_center; }
    [[nodiscard]] const Triangle& triangle() const { return m_triangle; }
    [[nodiscard]] const Point &a() const { return m_triangle.a(); }
    [[nodiscard]] const Point &b() const { return m_triangle.b(); }
    [[nodiscard]] const Point &c() const { return m_triangle.c(); }

    std::ostream &print(std::ostream &out) const override;

    // Defaulted three-way comparison operator
    auto operator<=>(const Circumcenter &other) const = default;

  private:
    Point m_center;
    Triangle m_triangle;
  };

} // namespace Yuclid
