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

  /** Says ∠(AB, CD)=v */
  class LineAngleEq : public Statement {
  public:
    LineAngleEq(SlopeAngle l, SlopeAngle r, const AddCircle<Rat> &v);
    LineAngleEq(SlopeAngle l, SlopeAngle r, const Rat &v);

    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::vector<Point> points() const override;
    [[nodiscard]] std::unique_ptr<Statement> normalize() const override;
    [[nodiscard]] bool check_nondegen() const override;
    [[nodiscard]] bool check_equations() const override;
    [[nodiscard]] std::vector<statement_arg> args() const override;

    // Public read-only access methods
    [[nodiscard]] const SlopeAngle &left() const { return m_left; }
    [[nodiscard]] const SlopeAngle &right() const { return m_right; }
    auto operator<=>(const LineAngleEq &other) const = default;

    [[nodiscard]] std::unique_ptr<Statement> clone() const override {
      return std::make_unique<LineAngleEq>(*this);
    }

    [[nodiscard]] boost::json::object to_json() const override;
    std::ostream &print(std::ostream &out) const override;

    ~LineAngleEq() override = default;

  protected:
    [[nodiscard]] std::optional<Equation<SlopeAngle>>
    as_equation_slope_angle() const override;
  private:
    SlopeAngle m_left, m_right;
    AddCircle<Rat> m_rhs;
  };

} // namespace Yuclid
