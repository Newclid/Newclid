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
#include <optional>
#include "statement.hpp"
#include "ar/equation.hpp"
#include "typedef.hpp"

namespace Yuclid {

  /**
   * @brief The statement saying `|AB|^2:|CD|^2=r`.
   *
   * Alpha Geometry & Newclid do not support irrational numbers in `rconst`.
   * However, they can be very useful, e.g., to express facts like `\sin(π / 3) = √3 / 2`.
   * So, we introduce a version of `rconst` that allows square roots in the RHS.
   */
  class RatioSquaredDist : public Statement {
  public:
    RatioSquaredDist(SquaredDist d1, SquaredDist d2, const NNRat &r);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;

    /**
     * @brief Normalize a `ratio_squared_dist` statement.
     *
     * 1. If the RHS is one, then normalizes to `cong`. (DISABLED FOR NOW)
     * 2. Otherwise, if the RHS is a square, then normalizes to `ratio_dist`.
     * 3. Otherwise, stays as a `ratio_squared_dist`.
     * 4. In all cases, ensures that the first (squared) distance
     *    comes before the second (squared) distance in the lexicographical order.
     */
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;

    [[nodiscard]] std::unique_ptr<Statement> normalize2() const;

    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const SquaredDist& left_squared_dist() const { return m_left; }
    [[nodiscard]] const SquaredDist& right_squared_dist() const { return m_right; }
    [[nodiscard]] NNRat ratio() const { return m_ratio; }
    auto operator<=>(const RatioSquaredDist &other) const = default;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<RatioSquaredDist>(*this);
    }

    [[nodiscard]] std::optional<RatioSquaredDist> as_ratio_squared_dist() const override;
    std::ostream &print(std::ostream &out) const override;

    [[nodiscard]] boost::json::object to_json() const override;

    ~RatioSquaredDist() override = default;
  
  protected:
    [[nodiscard]] std::optional<Equation<SquaredDist>> as_equation_squared_dist() const override;
    [[nodiscard]] std::optional<Equation<SinOrDist>> as_equation_sin_or_dist() const override;
  private:
    SquaredDist m_left;
    SquaredDist m_right;
    NNRat m_ratio;
  };

} // namespace Yuclid
