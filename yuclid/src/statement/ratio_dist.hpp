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

  /** Says `|AB|:|CD|=r` */
  class RatioDistEquals : public Statement {
  public:
    RatioDistEquals(const Dist &d1, const Dist &d2, const NNRat &r);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;

    /**
     * @brief Normalize a `ratio_dist` statement.
     *
     * If rhs is one, then normalize to `cong(left_dist(), right_dist())`.
     * Otherwise, ensure that `left_dist()` is smaller than `right_dist()`
     * in the lex order of points.
     */
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const Dist& left_dist() const { return m_left; }
    [[nodiscard]] const Dist& right_dist() const { return m_right; }
    [[nodiscard]] const NNRat &ratio() const { return m_ratio; }
    [[nodiscard]] RatioDistEquals swap() const;

    auto operator<=>(const RatioDistEquals &other) const = default;

    [[nodiscard]] boost::json::object to_json() const override;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<RatioDistEquals>(*this);
    }

    [[nodiscard]] std::optional<RatioSquaredDist> as_ratio_squared_dist() const override;
    std::ostream &print(std::ostream &out) const override;

    ~RatioDistEquals() override = default;

  protected:
    [[nodiscard]] std::optional<Equation<Dist>> as_equation_dist() const override;
    [[nodiscard]] std::optional<Equation<SquaredDist>> as_equation_squared_dist() const override;
    [[nodiscard]] std::optional<Equation<SinOrDist>> as_equation_sin_or_dist() const override;

  private:
    Dist m_left;
    Dist m_right;
    NNRat m_ratio;
  };

} // namespace Yuclid
