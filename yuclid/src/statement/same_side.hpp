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
#include "typedef.hpp"

namespace Yuclid {
  class Collinear;

  /**
   * @brief Represents that `a` is on the same side (inside, outside) of `[b, c]` as `d` of `[e, f]`
   *
   * This statement does not verify that either triple is collinear.
   */
  class SameSignDot : public Statement {
  public:
    SameSignDot(const Point &a, const Point &b, const Point &c,
              const Point &d, const Point &e, const Point &f);
    SameSignDot(const Collinear &left, const Collinear &right);
    explicit SameSignDot(const std::vector<statement_arg>& args);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    /**
     * @brief Normalize a `same_side` statement.
     *
     * For now, does nothing.
     */
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] bool numerical_only() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;
    [[nodiscard]] std::unique_ptr<Statement> clone() const override;

    [[nodiscard]] const Point &a() const { return m_a; }
    [[nodiscard]] const Point &b() const { return m_b; }
    [[nodiscard]] const Point &c() const { return m_c; }
    [[nodiscard]] const Point &d() const { return m_d; }
    [[nodiscard]] const Point &e() const { return m_e; }
    [[nodiscard]] const Point &f() const { return m_f; }

    std::ostream &print(std::ostream &out) const override;

    auto operator<=>(const SameSignDot &other) const = default;
  private:
    Point m_a, m_b, m_c, m_d, m_e, m_f;
  };

} // namespace Yuclid
