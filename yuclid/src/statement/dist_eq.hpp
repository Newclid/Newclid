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
#include "statement/statement.hpp"
#include "ar/equation.hpp"
#include "typedef.hpp"

namespace Yuclid {
  class SquaredDistEq;

  /** Says |AB|=r */
  class DistEq : public Statement {
  public:
    DistEq(const Dist &d, const NNRat &r);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const Dist &dist() const { return m_dist; }
    [[nodiscard]] SquaredDist get_squared_dist() const { return SquaredDist(m_dist); }
    [[nodiscard]] SinOrDist get_sin_or_dist() const { return SinOrDist(m_dist); }
    auto operator<=>(const DistEq &other) const = default;

    [[nodiscard]] SquaredDistEq as_squared_dist_eq() const;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<DistEq>(*this);
    }

    [[nodiscard]] boost::json::object to_json() const override;
    std::ostream &print(std::ostream &out) const override;

    ~DistEq() override = default;
  
  protected:
    [[nodiscard]] std::optional<Equation<Dist>> as_equation_dist() const override;
    [[nodiscard]] std::optional<Equation<SquaredDist>> as_equation_squared_dist() const override;
    [[nodiscard]] std::optional<Equation<SinOrDist>> as_equation_sin_or_dist() const override;
  private:
    Dist m_dist;
    NNRat m_rhs;
  };

} // namespace Yuclid
