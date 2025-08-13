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
#include "typedef.hpp" // Assuming point is defined here

namespace Yuclid {
  class EqualRatios;

  /**
   * @brief Statement saying that three points are collinear.
   */
  class Collinear : public Statement {
  public:
    Collinear(Point a, Point b, Point c);
    Collinear(const std::vector<statement_arg> &args);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    [[nodiscard]] std::array<Collinear, 3> cyclic_permutations() const;
    [[nodiscard]] std::array<Collinear, 6> permutations() const;

    /**
     * Test if `b` is between `a` and `c`.
     */
    [[nodiscard]] bool is_between() const;

    // Public read-only access methods
    [[nodiscard]] const Point& a() const { return m_a; }
    [[nodiscard]] const Point& b() const { return m_b; }
    [[nodiscard]] const Point& c() const { return m_c; }
    auto operator<=>(const Collinear &other) const = default;

    [[nodiscard]] EqualRatios eqratio_ab_bc(const Collinear &other) const;
    [[nodiscard]] EqualRatios eqratio_ab_ac(const Collinear &other) const;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<Collinear>(*this);
    }

    ~Collinear() override = default;

    std::ostream &print(std::ostream &out) const override;

    std::ostream &print_newclid(std::ostream &out) const override;

  protected:
    Point m_a;
    Point m_b;
    Point m_c;
  };

} // namespace Yuclid
